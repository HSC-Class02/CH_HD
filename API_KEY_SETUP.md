# OpenDART API 키 설정

## GitHub Actions에 키 등록하기

1. OpenDART(https://opendart.fss.or.kr/)에 로그인해 인증키를 발급합니다.
2. GitHub 저장소에서 **Settings → Secrets and variables → Actions**로 이동합니다.
3. **New repository secret**을 클릭합니다.
4. Name: **DART_API_KEY**
5. Secret: OpenDART에서 발급받은 인증키를 입력하고 저장합니다.
6. **Actions → HD Hyundai DART Update & Deploy → Run workflow**로 첫 실행을 시작합니다.

Secret 값은 저장소 파일이나 실행 로그로 읽거나 출력하지 않습니다. 키를 Python 코드, README, JSON, CSV에 붙여 넣지 마세요. 이 프로젝트는 DART 법인고유번호를 종목코드 267250로 법인코드 파일에서 자동 조회합니다.

## GitHub Pages 최초 설정

1. 저장소의 **Settings → Pages**를 엽니다.
2. **Build and deployment → Source**에서 **GitHub Actions**를 선택합니다.
3. Actions 실행이 성공한 뒤 https://hsc-class02.github.io/CH_HD/ 에서 대시보드를 확인합니다.

## 로컬 실행 (Windows PowerShell)

\`\`\`powershell
python -m pip install -r requirements.txt
$env:DART_API_KEY = "발급받은 인증키"
python src/update_agent.py --self-test
python src/update_agent.py
\`\`\`

macOS/Linux에서는 export DART_API_KEY="발급받은 인증키"로 환경변수를 설정합니다. API 키가 노출되면 OpenDART에서 키를 폐기하거나 다시 발급하세요.
