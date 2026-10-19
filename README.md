# HD현대 DART Financial Agent

[![🔗 대시보드 바로가기](https://img.shields.io/badge/🔗%20대시보드-바로가기-176B87?style=for-the-badge)](https://hsc-class02.github.io/CH_HD/)

HD현대(에이치디현대㈜, KOSPI 267250)의 OpenDART 재무제표를 수집하고, 주요 재무수치와 재무비율을 산출해 GitHub Pages 대시보드로 보여주는 프로젝트입니다.

## 대시보드

**[🔗 대시보드 바로가기](https://hsc-class02.github.io/CH_HD/)** · [GitHub Actions 실행 내역](https://github.com/HSC-Class02/CH_HD/actions) · [OpenDART](https://opendart.fss.or.kr/)

## API 인증키 등록 및 최초 실행

1. [OpenDART](https://opendart.fss.or.kr/)에서 인증키를 발급합니다.
2. 저장소의 **Settings → Secrets and variables → Actions → New repository secret**으로 이동합니다.
3. Secret 이름을 정확히 **DART_API_KEY**로 입력하고 발급받은 키를 값으로 저장합니다. 키를 소스코드, README, CSV, 로그에 넣지 마세요.
4. **Settings → Pages → Build and deployment → Source**에서 **GitHub Actions**를 선택합니다.
5. **Actions → HD Hyundai DART Update & Deploy → Run workflow**를 실행합니다.
6. 성공 여부를 [Actions 탭](https://github.com/HSC-Class02/CH_HD/actions)에서 확인하고 대시보드를 엽니다.

저장소 파일만으로는 GitHub Secret의 실제 값이나 등록 여부를 읽을 수 없습니다. 첫 실행 전 반드시 등록 상태를 직접 확인하세요.

## 수집 범위 및 계산 방식

- OpenDART 전체 재무제표 API를 사용하며 기본 시작연도는 2015년입니다. 기업의 DART 8자리 고유번호는 종목코드 **267250**로 법인코드 XML을 조회해 자동으로 확인합니다.
- 연결재무제표(CFS)를 우선 사용하고, 해당 보고서의 연결 자료가 없을 때에만 별도재무제표(OFS)를 조회합니다. 각 행의 **fs_div**에서 실제 기준을 확인할 수 있습니다.
- 사업보고서(Annual), 반기보고서(Half-year), 1분기 및 3분기 공시를 수집합니다. 반기 표의 손익·현금흐름은 6개월 누적 값, 분기 표의 Q2는 반기보고서의 당기 3개월 값입니다. Q4는 연간 흐름 값에서 Q1~Q3를 차감할 수 있을 때만 계산합니다.
- 자산·부채·자본 등 재무상태표 항목은 보고기간 말 잔액입니다. ROA/ROE와 총자산회전율은 중간기간에 대해 연환산하지 않습니다. 분류·계정과목이 명확하지 않거나 값이 없는 경우 0으로 꾸미지 않고 공란(null)으로 남깁니다.
- DART 원본 ZIP은 **reports/YYYY/**에 저장을 시도합니다. 다운로드가 불가하거나 크기가 제한을 넘으면 **reports/index.json**에 접수번호 및 DART 원문 링크를 보관합니다.

## 주요 항목

**재무수치:** 매출액, 영업이익, 당기순이익, 자산총계, 부채총계, 자본총계, 유동자산, 유동부채, 현금및현금성자산, 영업활동현금흐름, 금융비용(공시 계정이 매핑되는 경우).

**재무비율:** 영업이익률, 순이익률, ROA, ROE, 유동비율, 부채/자산, 부채/자본, 자기자본비율, 총자산회전율, 이자보상배율, 매출액 YoY, 영업이익 YoY.

## 자동 업데이트

GitHub Actions는 **매월 1일 한국시간 오전 9시**(UTC 00:00)에 데이터를 수집하고 CSV/JSON을 갱신한 뒤 GitHub Pages로 배포하도록 설정됩니다. GitHub 플랫폼 부하에 따라 예약 실행이 지연될 수 있습니다. 수동 실행도 지원합니다.

## 산출물

- **data/financials.csv**: 연간·반기·분기 정규화 재무 데이터와 재무비율
- **data/raw_financial_statements.csv**: API 원 계정 행 및 재무제표 구분
- **data/metrics.json**, **docs/data/metrics.json**: 대시보드 데이터
- **reports/index.json**, **reports/YYYY/*.zip**: 보고서 메타데이터 및 원본 보관 시도 결과
- **docs/index.html**: 그래프, 기간별 테이블, Peer Firms 표

## 국내 Peer Firms

| 기업 | 종목코드 | 비교 근거 | 비교 시 주의점 |
|---|---:|---|---|
| [SK스퀘어](https://dart.fss.or.kr/dsab001/main.do?autoSearch=true&textCrpNm=402340) | 402340 | 상장 지주회사·투자 포트폴리오 관리 | 디지털·투자자산 중심이라 사업 구성 차이 유의 |
| [SK㈜](https://dart.fss.or.kr/dsab001/main.do?autoSearch=true&textCrpNm=034730) | 034730 | 대기업 지주회사·자회사 포트폴리오 보유 | 비상장 자회사 가치 및 지분법 영향에 유의 |
| [(주)두산](https://dart.fss.or.kr/dsab001/main.do?autoSearch=true&textCrpNm=000150) | 000150 | 산업·기계 사업과 투자회사 성격 병존 | 직접 사업 비중 차이 유의 |
| [(주)LS](https://dart.fss.or.kr/dsab001/main.do?autoSearch=true&textCrpNm=006260) | 006260 | 산업재 중심 지주회사 | 전력·전선·소재 계열 비중이 높음 |
| [GS㈜](https://dart.fss.or.kr/dsab001/main.do?autoSearch=true&textCrpNm=078930) | 078930 | 에너지·유통 등 다각화 지주회사 | 업종 포트폴리오 차이 유의 |
| [(주)한화](https://dart.fss.or.kr/dsab001/main.do?autoSearch=true&textCrpNm=000880) | 000880 | 방산·에너지·소재 등 복합 사업구조 | 직접 영업사업 비중 차이 유의 |
| [효성](https://dart.fss.or.kr/dsab001/main.do?autoSearch=true&textCrpNm=004800) | 004800 | 산업·소재 중심 복합 기업집단 | 분할 및 계열 구조 변화 시 비교 시점 주의 |

Peer Firms는 구조적 참고군이며, 완전히 동일한 사업모델의 동종기업 목록은 아닙니다. 투자 권유나 가치평가 결론이 아니며, 최신 공시·연결범위를 별도로 검토해야 합니다.

## 저장소 About 링크 설정

README 맨 위에는 대시보드 배지가 포함되어 있습니다. 저장소 오른쪽 **About**의 Website 링크는 GitHub 설정에서 직접 저장해야 합니다.

1. 저장소 상단 About 옆 톱니바퀴를 클릭합니다.
2. Website에 **https://hsc-class02.github.io/CH_HD/**를 입력합니다.
3. **Save changes**를 클릭합니다.

## 로컬 실행

Python 3.11 이상 권장:

\`\`\`bash
python -m pip install -r requirements.txt
python src/update_agent.py --self-test
\`\`\`

실제 자료 수집 시 **DART_API_KEY** 또는 **OPENDART_API_KEY** 환경변수를 설정합니다. **.env**를 만들 경우 저장소에 커밋하지 마세요.
