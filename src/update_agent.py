from __future__ import annotations

import io
import json
import os
import re
import zipfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import pandas as pd
import requests
from dotenv import load_dotenv

from config import ALIASES, DISPLAY_NAMES

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
REPORTS = ROOT / "reports"
DATA.mkdir(exist_ok=True)
REPORTS.mkdir(exist_ok=True)

load_dotenv(ROOT / ".env")

API_KEY = os.getenv("DART_API_KEY", "").strip()
COMPANY_NAME = os.getenv("COMPANY_NAME", "현대그룹").strip()
START_YEAR = int(os.getenv("START_YEAR", "2020"))
REPORT_LIMIT = int(os.getenv("REPORT_LIMIT", "100"))

BASE = "https://opendart.fss.or.kr/api"

if not API_KEY:
    raise SystemExit("DART_API_KEY가 없습니다. GitHub Actions Secret 또는 .env에 입력하세요.")


def get_json(path: str, params: dict[str, Any]) -> dict[str, Any]:
    p = dict(params)
    p["crtfc_key"] = API_KEY
    r = requests.get(f"{BASE}/{path}", params=p, timeout=60)
    r.raise_for_status()
    data = r.json()
    if data.get("status") != "000":
        raise RuntimeError(f"DART API 오류 {data.get('status')}: {data.get('message')}")
    return data


def get_corp_code(company_name: str) -> str:
    # OpenDART corpCode API는 ZIP/XML이므로 여기서는 다운로드 후 XML을 읽습니다.
    r = requests.get(f"{BASE}/corpCode.xml", params={"crtfc_key": API_KEY}, timeout=60)
    r.raise_for_status()

    with zipfile.ZipFile(io.BytesIO(r.content)) as z:
        xml_name = next(n for n in z.namelist() if n.lower().endswith(".xml"))
        xml = z.read(xml_name).decode("utf-8", errors="ignore")

    pattern = re.compile(
        r"<corp_code>(.*?)</corp_code>.*?"
        r"<corp_name>(.*?)</corp_name>.*?"
        r"<stock_code>(.*?)</stock_code>",
        re.S,
    )
    rows = pattern.findall(xml)

    exact = [x for x in rows if x[1].strip() == company_name]
    if exact:
        return exact[0][0].strip()

    # 정확한 법인명이 아닐 때 유사 후보를 알려줌
    candidates = [x[1].strip() for x in rows if company_name in x[1]]
    msg = f"'{company_name}'에 해당하는 정확한 DART 법인을 찾지 못했습니다."
    if candidates:
        msg += "\n유사 후보:\n- " + "\n- ".join(candidates[:20])
    msg += "\nCOMPANY_NAME을 실제 DART 법인명으로 수정하세요."
    raise RuntimeError(msg)


def get_business_reports(corp_code: str) -> list[dict[str, Any]]:
    today = datetime.now()
    start = f"{max(START_YEAR, today.year - 7)}0101"
    end = today.strftime("%Y%m%d")

    data = get_json(
        "list.json",
        {
            "corp_code": corp_code,
            "bgn_de": start,
            "end_de": end,
            "pblntf_ty": "A",
            "pblntf_detail_ty": "A001",
            "sort": "date",
            "sort_mth": "desc",
            "page_no": "1",
            "page_count": str(min(REPORT_LIMIT, 100)),
        },
    )
    return data.get("list", [])


def download_report(report: dict[str, Any]) -> Path | None:
    rcept_no = report["rcept_no"]
    year = report["rcept_dt"][:4]
    out_dir = REPORTS / year
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{rcept_no}.zip"

    if out.exists():
        return None

    r = requests.get(
        f"{BASE}/document.xml",
        params={"crtfc_key": API_KEY, "rcept_no": rcept_no},
        timeout=120,
    )
    r.raise_for_status()

    # DART가 오류 XML을 반환할 경우 ZIP으로 저장하지 않음
    if not r.content.startswith(b"PK"):
        raise RuntimeError(f"원본보고서 다운로드 실패: {rcept_no}")

    out.write_bytes(r.content)
    return out


def find_value(rows: list[dict[str, Any]], aliases: list[str], fs_div: str = "CFS") -> float | None:
    aliases_norm = [a.strip().lower() for a in aliases]

    def score(name: str) -> int:
        n = name.strip().lower()
        for i, a in enumerate(aliases_norm):
            if n == a:
                return 1000 - i
        for i, a in enumerate(aliases_norm):
            if a in n or n in a:
                return 500 - i
        return -1

    candidates = []
    for row in rows:
        if row.get("fs_div") not in (fs_div, None):
            continue
        name = row.get("account_nm", "")
        s = score(name)
        if s >= 0:
            candidates.append((s, row))

    if not candidates:
        return None

    row = sorted(candidates, key=lambda x: x[0], reverse=True)[0][1]
    # 당기금액 우선. 없으면 당기금액이 들어있는 다른 필드를 사용.
    raw = row.get("thstrm_amount") or row.get("thstrm_add_amount")
    if raw in (None, ""):
        return None
    try:
        return float(str(raw).replace(",", "").replace(" ", ""))
    except ValueError:
        return None


def get_financials(corp_code: str) -> pd.DataFrame:
    records: list[dict[str, Any]] = []

    # 사업보고서(연간) 중심으로 2020~현재까지 조회
    for year in range(START_YEAR, datetime.now().year + 1):
        try:
            data = get_json(
                "fnlttSinglAcntAll.json",
                {
                    "corp_code": corp_code,
                    "bsns_year": str(year),
                    "reprt_code": "11011",
                    "fs_div": "CFS",
                },
            )
        except Exception as e:
            # 연결재무제표가 없는 경우 별도재무제표로 재시도
            try:
                data = get_json(
                    "fnlttSinglAcntAll.json",
                    {
                        "corp_code": corp_code,
                        "bsns_year": str(year),
                        "reprt_code": "11011",
                        "fs_div": "OFS",
                    },
                )
            except Exception:
                print(f"[WARN] {year}년 재무제표 조회 실패: {e}")
                continue

        rows = data.get("list", [])
        rec = {"year": year, "corp_code": corp_code}

        for key, aliases in ALIASES.items():
            rec[key] = find_value(rows, aliases)

        rec.update(calc_ratios(rec))
        records.append(rec)

    return pd.DataFrame(records).sort_values("year") if records else pd.DataFrame()


def calc_ratios(r: dict[str, Any]) -> dict[str, Any]:
    def div(a, b):
        if a is None or b in (None, 0):
            return None
        return a / b * 100

    def rawdiv(a, b):
        if a is None or b in (None, 0):
            return None
        return a / b

    return {
        "operating_margin": div(r.get("operating_profit"), r.get("revenue")),
        "net_margin": div(r.get("net_income"), r.get("revenue")),
        "roa": div(r.get("net_income"), r.get("assets")),
        "roe": div(r.get("net_income"), r.get("equity")),
        "current_ratio": div(r.get("current_assets"), r.get("current_liabilities")),
        "debt_ratio": div(r.get("liabilities"), r.get("assets")),
        "equity_ratio": div(r.get("equity"), r.get("assets")),
        "debt_to_equity": div(r.get("liabilities"), r.get("equity")),
        "asset_turnover": rawdiv(r.get("revenue"), r.get("assets")),
    }


def save_outputs(df: pd.DataFrame, reports: list[dict[str, Any]], corp_code: str):
    if df.empty:
        raise RuntimeError("재무 데이터가 없습니다.")

    df.to_csv(DATA / "financials.csv", index=False, encoding="utf-8-sig")

    payload = {
        "generated_at": datetime.now().astimezone().isoformat(),
        "company_name": COMPANY_NAME,
        "corp_code": corp_code,
        "unit": "DART API 원자료 단위(일반적으로 원)",
        "years": [int(x) for x in df["year"].tolist()],
        "financials": df.where(pd.notnull(df), None).to_dict(orient="records"),
        "reports": [
            {
                "report_nm": x.get("report_nm"),
                "rcept_no": x.get("rcept_no"),
                "rcept_dt": x.get("rcept_dt"),
                "corp_name": x.get("corp_name"),
            }
            for x in reports
        ],
        "display_names": DISPLAY_NAMES,
    }

    (DATA / "metrics.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def main():
    corp_code = get_corp_code(COMPANY_NAME)
    print(f"[INFO] {COMPANY_NAME} -> corp_code={corp_code}")

    reports = get_business_reports(corp_code)
    downloaded = 0
    for report in reports:
        try:
            if download_report(report):
                downloaded += 1
        except Exception as e:
            print(f"[WARN] 보고서 {report.get('rcept_no')} 저장 실패: {e}")

    print(f"[INFO] 신규 사업보고서 저장: {downloaded}건")

    df = get_financials(corp_code)
    save_outputs(df, reports, corp_code)
    print(f"[INFO] 재무 데이터 저장: {len(df)}개 연도")


if __name__ == "__main__":
    main()
