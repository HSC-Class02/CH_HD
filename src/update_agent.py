#!/usr/bin/env python3
"""OpenDART collector for HD Hyundai (267250), with normalized data and ratios."""
from __future__ import annotations
import argparse, csv, io, json, os, re, sys, time, zipfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
import requests
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
import config
API="https://opendart.fss.or.kr/api"
KST=timezone(timedelta(hours=9))
RAW_FIELDS=["year","reprt_code","fs_div","sj_div","account_id","account_nm","account_detail","thstrm_nm","thstrm_amount","thstrm_add_amount","frmtrm_amount","rcept_no"]

class DartError(RuntimeError): pass
def log(msg): print(f"[{datetime.now(KST).isoformat(timespec='seconds')}] {msg}",flush=True)
def get_key():
    key=(os.getenv("DART_API_KEY") or os.getenv("OPENDART_API_KEY") or "").strip()
    if not key or key in {"PASTE_YOUR_40_CHARACTER_OPENDART_KEY_HERE","여기에_OpenDART_40자리_인증키"}:
        raise DartError("DART_API_KEY is missing. Add it in GitHub Settings > Secrets and variables > Actions.")
    return key
def api_json(endpoint,params,key):
    try:
        r=requests.get(f"{API}/{endpoint}.json",params={"crtfc_key":key,**params},timeout=90)
        r.raise_for_status(); data=r.json()
    except Exception as e: raise DartError(f"OpenDART request failed ({endpoint}): {e}") from e
    status=str(data.get("status",""))
    if status=="000": return data
    if status=="013": return {**data,"list":[]}
    messages={"010":"invalid API key","011":"API key unavailable","020":"request limit exceeded","021":"query range exceeded","100":"missing required parameter","101":"invalid required parameter"}
    raise DartError(f"OpenDART {endpoint}: {status} {messages.get(status,data.get('message','unknown error'))}")
def resolve_corp_code(key):
    """Resolve DART's 8-digit corp_code from the KRX stock code, with actionable API errors."""
    try:
        response=requests.get(f"{API}/corpCode.xml",params={"crtfc_key":key},timeout=120)
        response.raise_for_status()
        content=response.content
        if not zipfile.is_zipfile(io.BytesIO(content)):
            detail=""
            try:
                payload=response.json()
                detail=f" OpenDART status={payload.get('status')}; message={payload.get('message')}"
            except Exception:
                excerpt=response.text[:220].replace("\n"," ").replace("\r"," ")
                detail=f" Response excerpt: {excerpt}"
            raise DartError("OpenDART corpCode.xml did not return the expected ZIP. Check DART_API_KEY validity/permissions and API availability."+detail)
        with zipfile.ZipFile(io.BytesIO(content)) as archive:
            member=next((n for n in archive.namelist() if n.lower().endswith("corpcode.xml")),archive.namelist()[0])
            import xml.etree.ElementTree as ET
            root=ET.fromstring(archive.read(member))
    except DartError:
        raise
    except Exception as e:
        raise DartError(f"Could not download/parse OpenDART corporate-code file: {e}") from e
    matches=[]
    for item in root.findall(".//list"):
        stock=(item.findtext("stock_code") or "").strip()
        name=(item.findtext("corp_name") or "").strip()
        if stock==config.STOCK_CODE and ("현대" in name or "HYUNDAI" in name.upper()):
            code=(item.findtext("corp_code") or "").strip()
            if code: matches.append((name,code))
    code=next((c for name,c in matches),None)
    if not code:
        raise DartError(f"Unable to resolve OpenDART corp_code for stock code {config.STOCK_CODE}. Check the listed company name/code.")
    return code
def parse_amount(v):
    if v is None:return None
    s=str(v).strip().replace(",","").replace("₩","").replace("원","")
    if not s or s in {"-","–","—","N/A"}:return None
    neg=s.startswith("(") and s.endswith(")")
    if neg:s=s[1:-1]
    try:
        n=float(s)
        return -n if neg else n
    except ValueError:return None
def norm(s): return re.sub(r"[\s()（）\[\]{}·,./_-]","",(s or "")).lower()
def choose_row(rows,spec):
    ids=set(spec.get("ids",[])); aliases={norm(a) for a in spec.get("aliases",[])}
    order={s:i for i,s in enumerate(spec.get("statements",[]))}
    cand=[]
    for row in rows:
        aid=(row.get("account_id") or "").strip()
        name=norm(row.get("account_nm",""))
        if aid in ids:cand.append(((0,order.get(row.get("sj_div",""),99)),row))
        elif name in aliases:cand.append(((1,order.get(row.get("sj_div",""),99)),row))
    return sorted(cand,key=lambda v:v[0])[0][1] if cand else None
def metric_values(rows,mode="period"):
    out={}
    for k,spec in config.METRICS.items():
        row=choose_row(rows,spec)
        if not row: out[k]=None;continue
        vals=(row.get("thstrm_add_amount"),row.get("thstrm_amount")) if mode=="ytd" and spec.get("flow") else (row.get("thstrm_amount"),row.get("thstrm_add_amount"))
        out[k]=next((n for n in (parse_amount(v) for v in vals) if n is not None),None)
    return out
def raw_line(row,year,code,fs):
    return {"year":year,"reprt_code":code,"fs_div":fs,**{k:row.get(k) for k in RAW_FIELDS if k not in {"year","reprt_code","fs_div"}}}
def fetch_stmt(key,corp,year,report,fs):
    return api_json("fnlttSinglAcntAll",{"corp_code":corp,"bsns_year":str(year),"reprt_code":report,"fs_div":fs},key).get("list",[]) or []
def request_stmt(key,corp,year,report):
    for fs in ("CFS","OFS"):
        rows=fetch_stmt(key,corp,year,report,fs)
        if rows:return rows,fs
    return [],"CFS"
def write_csv(path,rows,fields=None):
    path.parent.mkdir(parents=True,exist_ok=True)
    fields=fields or (list(dict.fromkeys(k for r in rows for k in r)) if rows else [])
    with path.open("w",encoding="utf-8-sig",newline="") as f:
        if fields:
            w=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore");w.writeheader();w.writerows(rows)
def div(n,d,m=1):
    return None if n is None or d is None or d==0 else n/d*m
def enrich(records,kind,annual=[]):
    records.sort(key=lambda r:(r["year"],r.get("quarter") or 0))
    for r in records:
        yr=r["year"]; q=r.get("quarter")
        if kind=="annual":prev=next((x for x in records if x["year"]==yr-1),None)
        elif kind=="half_year":prev=next((x for x in annual if x["year"]==yr-1),None)
        elif q==1:prev=next((x for x in annual if x["year"]==yr-1),None)
        else:prev=next((x for x in records if x["year"]==yr and x.get("quarter")==q-1),None)
        assets,equity=r.get("total_assets"),r.get("total_equity")
        avg_a=(assets+prev["total_assets"])/2 if assets is not None and prev and prev.get("total_assets") is not None else assets
        avg_e=(equity+prev["total_equity"])/2 if equity is not None and prev and prev.get("total_equity") is not None else equity
        r.update({
          "operating_margin_pct":div(r.get("operating_income"),r.get("revenue"),100),
          "net_margin_pct":div(r.get("net_income"),r.get("revenue"),100),
          "roa_pct":div(r.get("net_income"),avg_a,100),
          "roe_pct":div(r.get("net_income"),avg_e,100),
          "current_ratio_pct":div(r.get("current_assets"),r.get("current_liabilities"),100),
          "debt_to_assets_pct":div(r.get("total_liabilities"),assets,100),
          "debt_to_equity_pct":div(r.get("total_liabilities"),equity,100),
          "equity_ratio_pct":div(equity,assets,100),
          "asset_turnover":div(r.get("revenue"),avg_a),
          "interest_coverage":div(r.get("operating_income"),r.get("interest_expense")),
        })
        if kind=="annual":p=next((x for x in records if x["year"]==yr-1),None)
        elif kind=="half_year":p=next((x for x in HALF if x["year"]==yr-1),None)
        else:p=next((x for x in ALL_QUARTERS if x["year"]==yr-1 and x.get("quarter")==q),None)
        r["revenue_yoy_pct"]=div(r["revenue"]-p["revenue"],p.get("revenue"),100) if p and r.get("revenue") is not None and p.get("revenue") not in (None,0) else None
        r["operating_income_yoy_pct"]=div(r["operating_income"]-p["operating_income"],abs(p.get("operating_income")),100) if p and r.get("operating_income") is not None and p.get("operating_income") not in (None,0) else None
    return records
def save_report(key,receipt,year,label):
    url=f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={receipt}"
    directory=ROOT/"reports"/str(year);directory.mkdir(parents=True,exist_ok=True)
    path=directory/f"{label}_{receipt}.zip"
    if path.exists():return {"year":year,"label":label,"rcept_no":receipt,"dart_url":url,"archive":str(path.relative_to(ROOT)),"archive_status":"already_saved"}
    if os.getenv("SAVE_REPORT_ARCHIVES","true").lower() not in {"1","true","yes"}:return {"year":year,"label":label,"rcept_no":receipt,"dart_url":url,"archive":None,"archive_status":"disabled"}
    try:
        r=requests.get(f"{API}/document.xml",params={"crtfc_key":key,"rcept_no":receipt},timeout=120);r.raise_for_status();raw=r.content
        if not raw.startswith(b"PK"):return {"year":year,"label":label,"rcept_no":receipt,"dart_url":url,"archive":None,"archive_status":"DART did not return ZIP"}
        limit=float(os.getenv("MAX_REPORT_ARCHIVE_MB","8"))
        if len(raw)>limit*1024*1024:return {"year":year,"label":label,"rcept_no":receipt,"dart_url":url,"archive":None,"archive_status":f"skipped_over_{limit:g}MB"}
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            bad=z.testzip()
            if bad:raise zipfile.BadZipFile(f"Corrupt member {bad}")
        path.write_bytes(raw)
        return {"year":year,"label":label,"rcept_no":receipt,"dart_url":url,"archive":str(path.relative_to(ROOT)),"archive_status":"saved"}
    except Exception as e:
        log(f"Original report archive skipped ({receipt}): {e}")
        return {"year":year,"label":label,"rcept_no":receipt,"dart_url":url,"archive":None,"archive_status":f"error: {str(e)[:150]}"}
HALF=[]
ALL_QUARTERS=[]
def update(key):
    now=datetime.now(KST);corp=resolve_corp_code(key)
    log(f"{config.COMPANY_NAME} / stock code {config.STOCK_CODE} / DART corp_code {corp}")
    annual=[];half=[];qb={};raw=[];reports=[];warnings=[]
    for year in range(config.START_YEAR,now.year+1):
        for code in ("11011","11012","11013","11014"):
            try:rows,fs=request_stmt(key,corp,year,code)
            except DartError as e:
                warnings.append(f"{year}/{code}: {e}");log(warnings[-1]);continue
            if not rows:continue
            raw.extend(raw_line(x,year,code,fs) for x in rows)
            receipt=next((str(x.get("rcept_no")) for x in rows if x.get("rcept_no")),None)
            meta={"rcept_no":receipt,"report_code":code,"fs_div":fs}
            if code=="11011":
                annual.append({"period":str(year),"year":year,"period_type":"annual","quarter":None,**meta,**metric_values(rows)})
            elif code=="11012":
                cumulative=metric_values(rows,"ytd")
                # For stock/balance sheet values the reported period-end balance is retained.
                half.append({"period":f"{year} H1","year":year,"period_type":"half_year","quarter":2,**meta,**cumulative})
                q2=metric_values(rows,"period")
                qb.setdefault(year,{})[2]={"period":f"{year} Q2","year":year,"period_type":"quarterly","quarter":2,**meta,**{k:(q2[k] if not s.get("flow") else q2[k]) for k,s in config.METRICS.items()}}
            elif code=="11013":
                qb.setdefault(year,{})[1]={"period":f"{year} Q1","year":year,"period_type":"quarterly","quarter":1,**meta,**metric_values(rows)}
            elif code=="11014":
                qb.setdefault(year,{})[3]={"period":f"{year} Q3","year":year,"period_type":"quarterly","quarter":3,**meta,**metric_values(rows)}
            if receipt:reports.append(save_report(key,receipt,year,config.REPORTS[code]["label"]))
            time.sleep(.12)
    # Ensure Q2 balance sheet values are identical to the half-year balance sheet, while flows use standalone Q2.
    h_by_year={r["year"]:r for r in half}
    for year,quarters in qb.items():
        if 2 in quarters and year in h_by_year:
            for k,spec in config.METRICS.items():
                if not spec["flow"]:quarters[2][k]=h_by_year[year].get(k)
    annual.sort(key=lambda r:r["year"]);half.sort(key=lambda r:r["year"])
    annual=enrich(annual,"annual",annual)
    HALF[:] = half
    half=enrich(half,"half_year",annual)
    # Q4 is derived only when Q1/Q2/Q3 and annual data all exist and every flow value is available.
    a_by_year={r["year"]:r for r in annual}
    for year,quarters in qb.items():
        a=a_by_year.get(year)
        if a and all(q in quarters for q in (1,2,3)):
            q4={"period":f"{year} Q4","year":year,"period_type":"quarterly","quarter":4,"report_code":"11011","rcept_no":a.get("rcept_no"),"fs_div":a.get("fs_div"),"derived_from_annual":True}
            for k,spec in config.METRICS.items():
                if spec["flow"]:
                    parts=[quarters[q].get(k) for q in (1,2,3)]
                    q4[k]=a.get(k)-sum(parts) if a.get(k) is not None and all(v is not None for v in parts) else None
                else:q4[k]=a.get(k)
            quarters[4]=q4
    quarterly=[r for y in sorted(qb) for q,r in sorted(qb[y].items())]
    ALL_QUARTERS[:] = quarterly
    quarterly=enrich(quarterly,"quarterly",annual)
    fields=list(config.METRICS)+["operating_margin_pct","net_margin_pct","roa_pct","roe_pct","current_ratio_pct","debt_to_assets_pct","debt_to_equity_pct","equity_ratio_pct","asset_turnover","interest_coverage","revenue_yoy_pct","operating_income_yoy_pct"]
    normalized=[]
    for group in (annual,half,quarterly):
        normalized.extend({k:r.get(k) for k in ["period","year","period_type","quarter","report_code","rcept_no","fs_div"]+fields} for r in group)
    write_csv(ROOT/"data/financials.csv",normalized)
    write_csv(ROOT/"data/raw_financial_statements.csv",raw,RAW_FIELDS)
    unique={(r.get("year"),r.get("label"),r.get("rcept_no")):r for r in reports}
    report_list=sorted(unique.values(),key=lambda r:(r["year"],r["label"]))
    index={"updated_at":now.isoformat(),"company":config.COMPANY_NAME,"stock_code":config.STOCK_CODE,"corp_code":corp,"reports":report_list}
    (ROOT/"reports/index.json").parent.mkdir(parents=True,exist_ok=True)
    (ROOT/"reports/index.json").write_text(json.dumps(index,ensure_ascii=False,indent=2),encoding="utf-8")
    data={"company":{"name":config.COMPANY_NAME,"english_name":"HD HYUNDAI CO., LTD.","stock_code":config.STOCK_CODE,"corp_code":corp,"market":"KOSPI","currency":"KRW"},
          "updated_at":now.isoformat(),"data_start_year":config.START_YEAR,"units":{"amount":"KRW","table_amount":"억원","ratios":"%"},
          "annual":annual,"half_year":half,"quarterly":quarterly,"peers":config.PEERS,"reports":report_list,"warnings":warnings[-50:],
          "methodology":{"financial_scope":"CFS preferred; OFS used only when CFS returns no data for the filing.","interim_returns":"ROA/ROE and asset turnover are not annualized for interim periods.","q4":"Q4 is derived from audited annual flow values less standalone Q1-Q3 only when all required values exist."}}
    for path in (ROOT/"data/metrics.json",ROOT/"docs/data/metrics.json"):
        path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(data,ensure_ascii=False,indent=2,allow_nan=False),encoding="utf-8")
    log(f"Updated: annual={len(annual)}, half-year={len(half)}, quarterly={len(quarterly)}, raw rows={len(raw)}")
    if not annual and not half and not quarterly:log("WARNING: no report data returned; check OpenDART key and available filings.")
def self_test():
    assert parse_amount("1,234")==1234 and parse_amount("(12)") == -12 and parse_amount("-") is None
    assert div(25,100,100)==25 and div(1,0) is None
    assert norm("매출액 (손실)")=="매출액손실"
    assert "revenue" in config.METRICS and len(config.PEERS)>=5
    print("SELF-TEST PASS")
if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("--self-test",action="store_true");args=parser.parse_args()
    if args.self_test:self_test()
    else:update(get_key())
