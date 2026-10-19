from __future__ import annotations

# DART 계정과목명은 회사/연도/XBRL 구조에 따라 조금씩 달라질 수 있습니다.
# 필요한 경우 aliases를 추가하세요.

ALIASES = {
    "revenue": [
        "매출액", "수익(매출액)", "영업수익", "매출",
        "Revenue", "Sales"
    ],
    "operating_profit": [
        "영업이익", "영업이익(손실)", "Operating income",
        "Operating profit"
    ],
    "net_income": [
        "당기순이익", "당기순이익(손실)", "분기순이익",
        "반기순이익", "Profit for the period", "Net income"
    ],
    "assets": ["자산총계", "Assets"],
    "liabilities": ["부채총계", "Liabilities"],
    "equity": ["자본총계", "Equity"],
    "current_assets": ["유동자산", "Current assets"],
    "current_liabilities": ["유동부채", "Current liabilities"],
    "cash": [
        "현금및현금성자산", "현금 및 현금성자산",
        "Cash and cash equivalents"
    ],
    "operating_cash_flow": [
        "영업활동으로 인한 현금흐름", "영업활동현금흐름",
        "영업활동 현금흐름", "Net cash provided by operating activities"
    ],
    "interest_bearing_debt": [
        "단기차입금", "장기차입금", "유동성장기부채",
        "사채", "장기차입부채", "차입금"
    ],
}

# dashboard에 표시할 항목 순서
DISPLAY_NAMES = {
    "revenue": "매출액",
    "operating_profit": "영업이익",
    "net_income": "당기순이익",
    "assets": "자산총계",
    "liabilities": "부채총계",
    "equity": "자본총계",
    "current_assets": "유동자산",
    "current_liabilities": "유동부채",
    "cash": "현금및현금성자산",
    "operating_cash_flow": "영업활동현금흐름",
}

RATIOS = [
    "operating_margin",
    "net_margin",
    "roa",
    "roe",
    "current_ratio",
    "debt_ratio",
    "equity_ratio",
    "debt_to_equity",
    "asset_turnover",
]
