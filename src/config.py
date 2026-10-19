"""Configuration and metric mapping for HD Hyundai (267250)."""
COMPANY_NAME = "에이치디현대(주)"
STOCK_CODE = "267250"  # KRX stock code; NOT the 8-digit OpenDART corp_code
START_YEAR = 2015
REPORTS = {
    "11011": {"label": "Annual", "report_name": "사업보고서"},
    "11012": {"label": "Half-year", "report_name": "반기보고서"},
    "11013": {"label": "Quarterly", "quarter": 1, "report_name": "1분기보고서"},
    "11014": {"label": "Quarterly", "quarter": 3, "report_name": "3분기보고서"},
}
METRICS = {
 "revenue":{"label":"매출액","unit":"KRW","statements":["CIS","IS"],"ids":["ifrs-full_Revenue","ifrs_Revenue","dart_OperatingRevenue","ifrs-full_RevenueFromContractsWithCustomers"],"aliases":["매출액","수익(매출액)","영업수익","매출","수익"],"flow":True},
 "operating_income":{"label":"영업이익","unit":"KRW","statements":["CIS","IS"],"ids":["ifrs-full_ProfitLossFromOperatingActivities","dart_OperatingIncomeLoss"],"aliases":["영업이익","영업이익(손실)","영업손익"],"flow":True},
 "net_income":{"label":"당기순이익","unit":"KRW","statements":["CIS","IS"],"ids":["ifrs-full_ProfitLoss","ifrs_ProfitLoss","dart_ProfitLoss"],"aliases":["당기순이익","당기순이익(손실)","분기순이익","반기순이익","연결당기순이익"],"flow":True},
 "total_assets":{"label":"자산총계","unit":"KRW","statements":["BS"],"ids":["ifrs-full_Assets","ifrs_Assets"],"aliases":["자산총계"],"flow":False},
 "total_liabilities":{"label":"부채총계","unit":"KRW","statements":["BS"],"ids":["ifrs-full_Liabilities","ifrs_Liabilities"],"aliases":["부채총계"],"flow":False},
 "total_equity":{"label":"자본총계","unit":"KRW","statements":["BS"],"ids":["ifrs-full_Equity","ifrs_Equity"],"aliases":["자본총계"],"flow":False},
 "current_assets":{"label":"유동자산","unit":"KRW","statements":["BS"],"ids":["ifrs-full_CurrentAssets","ifrs_CurrentAssets"],"aliases":["유동자산"],"flow":False},
 "current_liabilities":{"label":"유동부채","unit":"KRW","statements":["BS"],"ids":["ifrs-full_CurrentLiabilities","ifrs_CurrentLiabilities"],"aliases":["유동부채"],"flow":False},
 "cash_and_equivalents":{"label":"현금및현금성자산","unit":"KRW","statements":["BS"],"ids":["ifrs-full_CashAndCashEquivalents","ifrs_CashAndCashEquivalents"],"aliases":["현금및현금성자산","현금및현금성자산과현금성자산"],"flow":False},
 "operating_cash_flow":{"label":"영업활동현금흐름","unit":"KRW","statements":["CF"],"ids":["ifrs-full_CashFlowsFromUsedInOperatingActivities","ifrs_CashFlowsFromUsedInOperatingActivities"],"aliases":["영업활동현금흐름","영업활동으로인한현금흐름","영업활동순현금흐름"],"flow":True},
 "interest_expense":{"label":"금융비용","unit":"KRW","statements":["CIS","IS"],"ids":["ifrs-full_FinanceCosts","ifrs_FinanceCosts"],"aliases":["금융비용","금융원가","이자비용"],"flow":True},
}
PEERS = [
 {"name":"SK스퀘어","ticker":"402340","dart_name":"에스케이스퀘어 주식회사","rationale":"상장 지주회사·투자 포트폴리오 관리","caveat":"디지털·투자자산 중심이라 사업 구성 차이 유의","url":"https://dart.fss.or.kr/dsab001/main.do?autoSearch=true&textCrpNm=402340"},
 {"name":"SK㈜","ticker":"034730","dart_name":"SK(주)","rationale":"대기업 지주회사·자회사 포트폴리오 보유","caveat":"비상장 자회사 가치 및 지분법 영향에 유의","url":"https://dart.fss.or.kr/dsab001/main.do?autoSearch=true&textCrpNm=034730"},
 {"name":"㈜두산","ticker":"000150","dart_name":"(주)두산","rationale":"산업·기계 사업과 투자회사 성격 병존","caveat":"직접 사업 비중 차이 유의","url":"https://dart.fss.or.kr/dsab001/main.do?autoSearch=true&textCrpNm=000150"},
 {"name":"㈜LS","ticker":"006260","dart_name":"(주)LS","rationale":"산업재 중심 지주회사","caveat":"전력·전선·소재 계열 비중이 높음","url":"https://dart.fss.or.kr/dsab001/main.do?autoSearch=true&textCrpNm=006260"},
 {"name":"GS㈜","ticker":"078930","dart_name":"GS(주)","rationale":"에너지·유통 등 다각화 지주회사","caveat":"업종 포트폴리오 차이 유의","url":"https://dart.fss.or.kr/dsab001/main.do?autoSearch=true&textCrpNm=078930"},
 {"name":"㈜한화","ticker":"000880","dart_name":"(주)한화","rationale":"방산·에너지·소재 등 복합 사업구조","caveat":"직접 영업사업 비중 차이 유의","url":"https://dart.fss.or.kr/dsab001/main.do?autoSearch=true&textCrpNm=000880"},
 {"name":"효성","ticker":"004800","dart_name":"효성","rationale":"산업·소재 중심 복합 기업집단","caveat":"분할 및 계열 구조 변화 시 비교 시점 주의","url":"https://dart.fss.or.kr/dsab001/main.do?autoSearch=true&textCrpNm=004800"},
]
