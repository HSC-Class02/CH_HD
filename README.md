# DART Financial Agent → GitHub Dashboard

DART(OpenDART)에서 특정 기업의 사업보고서를 자동 수집하고, 주요 재무수치와 재무비율을 계산한 뒤 GitHub Pages 대시보드로 공개하는 템플릿입니다.

## 1. 전체 구조

```text
DART API
  ├─ 기업 고유번호 조회
  ├─ 사업보고서 검색
  ├─ 사업보고서 원본 ZIP/XML 저장
  └─ 재무제표 주요계정 조회
          ↓
GitHub Actions (자동 실행)
          ↓
data/financials.csv
data/metrics.json
reports/YYYY/*.zip
          ↓
docs/index.html
          ↓
GitHub Pages Dashboard
```

OpenDART는 공시검색, 공시서류 원본, 주요 재무계정 및 주요 재무지표 API를 제공합니다.

## 2. 중요한 점: "현대그룹"은 기업집단명일 수 있음

OpenDART 재무 API는 기업집단 전체를 한 번에 조회하는 방식이 아니라 **DART에 등록된 개별 법인(corp_code)** 단위로 조회합니다.

따라서 `.env`의 `COMPANY_NAME`에는 실제 DART 법인명을 넣어야 합니다.

예:
```env
COMPANY_NAME=현대엘리베이터
```

또는 분석 대상 법인이 정확히 무엇인지 확인한 후 해당 법인명을 입력하세요.

## 3. API 키 입력

1. OpenDART에서 인증키를 발급합니다.
2. GitHub Repository → Settings → Secrets and variables → Actions
3. `New repository secret`
4. 이름: `DART_API_KEY`
5. 값: 발급받은 40자리 인증키
6. 저장

**API 키를 코드에 직접 넣거나 GitHub에 commit하지 마세요.**

로컬 테스트가 필요하면:
```bash
cp .env.example .env
```
`.env`에 API 키를 넣고 실행합니다. `.gitignore`에 `.env`가 포함되어 있습니다.

## 4. 로컬 실행

Python 3.11 이상 권장.

```bash
pip install -r requirements.txt
python src/update_agent.py
```

생성되는 결과:
- `reports/` : 새로 발견한 사업보고서 원본
- `data/financials.csv` : 주요 재무수치
- `data/metrics.json` : 대시보드용 데이터
- `docs/index.html` : GitHub Pages 대시보드

## 5. 자동 업데이트

`.github/workflows/update.yml`이 매일 실행되도록 되어 있습니다.

GitHub Actions의 `schedule`은 기본적으로 UTC 기준이며, workflow에서 timezone을 지정할 수 있습니다.

현재 템플릿은 한국시간 오전 9시를 목표로 설정했습니다.

수동 실행도 가능합니다:
Repository → Actions → `DART Financial Data Update` → `Run workflow`

## 6. 분석 항목

기본 템플릿에는 다음을 포함합니다.

### 주요 재무수치
- 매출액
- 영업이익
- 당기순이익
- 자산총계
- 부채총계
- 자본총계
- 유동자산
- 유동부채
- 현금및현금성자산
- 차입금/이자부부채(공시 계정명 매핑이 가능한 경우)
- 영업활동현금흐름

### 재무비율
- 영업이익률
- 순이익률
- ROA
- ROE
- 유동비율
- 부채비율
- 자기자본비율
- 부채/자본비율
- 총자산회전율

계정과목 명칭은 기업의 XBRL 공시 구조에 따라 조금씩 달라질 수 있으므로 `src/config.py`의 alias를 수정할 수 있습니다.

## 7. GitHub Pages

Repository Settings → Pages에서:

- Source: `Deploy from a branch`
- Branch: `main`
- Folder: `/docs`

로 설정합니다.

그러면 `docs/index.html`이 대시보드가 됩니다.

## 8. 첨부파일의 재무항목 반영

현재 대화에서 재무수치 항목이 적힌 첨부파일을 확인할 수 없어, 일반적인 재무분석 항목을 기본값으로 넣었습니다.

첨부파일의 정확한 재무항목을 확인할 수 있게 되면 `src/config.py`의 `METRICS`와 계정 alias를 그 항목에 맞춰 1:1로 조정하면 됩니다.

## 9. 데이터 저장 주의

사업보고서 원본을 GitHub에 계속 쌓으면 저장소 용량이 빠르게 증가할 수 있습니다. 학교 프로젝트/프로토타입에서는 적합하지만, 장기 운영에서는 원본 문서를 별도 저장소나 Object Storage에 보관하고 GitHub에는 분석 데이터와 링크만 저장하는 방식을 고려하세요.
