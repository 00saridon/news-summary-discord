# 업무 자동화

---

## 0. 파이썬 설치 (이미 있다면 1번으로)

> 📌 **권장 버전: Python 3.10 ~ 3.13**
> - 3.10 미만은 pandas 최신 버전이 안 깔립니다.
> - 3.14처럼 갓 출시된 버전은 일부 패키지 wheel이 아직 없어 설치가 실패할 수 있습니다.
> - 옆 사람과 버전이 달라도 됩니다. venv가 각자 격리된 환경을 만들어주기 때문에 서로 영향을 주지 않습니다.

### 설치 여부 확인

터미널을 열고:

- **Windows**: `Win + R` → `cmd` 입력 → 엔터
- **macOS**: `Cmd + Space` → `terminal` 입력 → 엔터

다음 명령을 실행:

```bash
python --version
```

`Python 3.10` 이상이 보이면 설치된 것. macOS는 `python3 --version`도 같이 시도해보세요.
명령을 못 찾는다는 에러(`command not found`, `'python'은(는) 내부 또는 외부 명령... 아닙니다`)가 나오면 아래 설치 단계로.

### Windows 설치

1. https://www.python.org/downloads/windows/ 에서 **최신 안정판 (3.12 이상)** Installer 다운로드
2. 설치 마법사 실행 시 **첫 화면 맨 아래 `Add python.exe to PATH` 체크박스를 반드시 체크** ⚠️
3. `Install Now` 클릭
4. 설치 후 새 cmd 창을 열고 `python --version` 으로 확인

> ❗ **PATH 체크박스를 깜빡한 경우**: 제어판에서 Python을 제거 후 재설치하거나, 아래 "환경변수 직접 추가" 절을 따르세요.

### macOS 설치

가장 쉬운 방법 두 가지 중 택1.

**A. 공식 설치 파일 (가장 단순)**
1. https://www.python.org/downloads/macos/ 에서 `.pkg` 다운로드
2. 더블클릭 후 안내대로 설치
3. 터미널에서 `python3 --version`

**B. Homebrew (추천)**
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install python
python3 --version
```

> macOS는 `python` 대신 **`python3`** 명령을 사용합니다. 이 README의 모든 명령에서 Windows의 `python`을 macOS는 `python3`로 바꿔 실행하세요.

---

## 0-1. 파이썬은 깔았는데 명령어가 안 먹을 때 (PATH 문제)

증상: `python --version`을 쳤는데 "명령을 찾을 수 없습니다", "외부 명령이 아닙니다" 가 뜸.

### Windows — 환경변수에 직접 추가

1. `Win` 키 → **"환경 변수"** 검색 → `시스템 환경 변수 편집` 클릭
2. `환경 변수(N)...` 버튼 클릭
3. 아래쪽 **시스템 변수**에서 `Path` 선택 → `편집(E)...`
4. `새로 만들기(N)`로 두 줄 추가 (경로는 본인 사용자명에 맞게):
   ```
   C:\Users\<본인사용자명>\AppData\Local\Programs\Python\Python312\
   C:\Users\<본인사용자명>\AppData\Local\Programs\Python\Python312\Scripts\
   ```
   > 정확한 경로는 파일 탐색기 주소창에 `%LOCALAPPDATA%\Programs\Python` 을 붙여넣어 확인하세요.
5. 모든 창에서 `확인` → **새 cmd 창**을 열어 `python --version`

### macOS — PATH에 추가

zsh(기본 셸):
```bash
echo 'export PATH="/usr/local/bin:/opt/homebrew/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
python3 --version
```

> Apple Silicon(M1/M2/M3/M4)은 Homebrew 경로가 `/opt/homebrew/bin`, Intel Mac은 `/usr/local/bin`. 둘 다 넣어두면 안전.

---

## 1. 가상환경 만들기

프로젝트 폴더로 이동:

**Windows**
```cmd
cd C:\Users\<본인사용자명>\Desktop\KSA\datas
python -m venv .venv

```
> "venv라는 Python 모듈을 실행해서 .venv 폴더에 가상환경 만들어"

**macOS**
```bash
cd ~/Desktop/KSA/datas
python3 -m venv .venv
```

> ⚠️ **`.venv/` 폴더는 절대 다른 PC로 복사해서 쓰지 마세요.** 폴더 안에 그 PC의 파이썬 절대경로와 OS별 실행 파일이 박혀 있어서, USB로 복사하면 동작하지 않습니다. 각자 자기 PC에서 위 명령으로 새로 만들고, 공유는 `requirements.txt` 로만 합니다.

### 한 PC에 파이썬이 여러 개 깔려 있을 때

`python` 명령이 어떤 버전을 가리키는지 헷갈릴 수 있습니다. (예: Anaconda 3.11 + 별도 설치 3.13이 같이 있는 경우) Windows는 `py` 런처로 버전을 명시해 venv를 만들 수 있어요:

```cmd
py -0                          :: 설치된 파이썬 목록 확인
py -3.13 -m venv .venv         :: 3.13으로 venv 생성
py -3.11 -m venv .venv         :: 3.11로 venv 생성
```

생성 후 버전 확인:
```cmd
.venv\Scripts\python.exe --version
```

macOS는 `python3.13 -m venv .venv` 처럼 버전을 직접 지정합니다.

> 💡 **이렇게 하면 좋은 이유**: 시스템 `python` 명령이 다른 버전을 가리키더라도, `py -3.13`으로 만든 venv 안에서는 항상 3.13이 동작합니다. venv 활성화 후 `python` 명령은 그 버전을 가리키게 됩니다.

### 활성화

| OS / 셸 | 명령 |
|---|---|
| Windows PowerShell | `.\.venv\Scripts\Activate.ps1` |
| Windows cmd | `.venv\Scripts\activate.bat` |
| Windows Git Bash | `source .venv/Scripts/activate` |
| macOS / Linux | `source .venv/bin/activate` |

활성화되면 프롬프트 앞에 `(.venv)` 표시가 붙습니다. 비활성화는 `deactivate`.

> ❗ **PowerShell에서 "이 시스템에서 스크립트를 실행할 수 없으므로..." 에러**가 나면, PowerShell을 **관리자 권한**으로 열고 한 번만 실행:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

---

## 2. 패키지 설치

가상환경 활성화 상태에서:

```bash
pip install -r requirements.txt
```

> macOS에서 활성화하지 않고 쓰려면 `pip` 대신 `pip3`.

---

## 3. 실행

```bash
python "뉴스요약_문서/telegram_sender.py"
python "엑셀-Gmail자동화/gmail_sender.py"
python "카드지출분석/_analyze.py"
python "뉴스요약/main.py"
python "송파커뮤니티센터-정보/songpa_crawler.py"
```

---

## 카테고리 매핑

| 파일 | 카테고리 | 데이터 소스 |
|---|---|---|
| 뉴스요약_문서/telegram_sender.py | 정보 자동화 (입문) | 요약된 뉴스(.md) 텔레그램 발송 |
| 엑셀-Gmail자동화/gmail_sender.py | 업무 자동화 (기초) | Gmail + Excel + Docx 연동 |
| 카드지출분석/_analyze.py | 데이터 분석 (중급) | 카드 명세서 Excel → Docx 보고서 |
| 뉴스요약/main.py | 정보 자동화 (심화) | 네이버 뉴스(정치/경제) 요약 + 디스코드/카카오 전송 |
| 송파커뮤니티센터-정보/songpa_crawler.py | 정보 자동화 (전문) | 송파소식 크롤링 + 텔레그램 전송 |


## 🦾 바이브코딩 프롬프트 예시

아래 프롬프트를 채팅창에 그대로 붙여넣으면 프로젝트 폴더 내의 파일을 참조하여 자동으로 코드를 생성하고 실행합니다.
필요에 따라 파일명, 카테고리, 전송 채널 등을 바꿔서 요청해보세요.

---

### 1단계 — 요약 문서 텔레그램 전송 (난이도: ★☆☆☆☆)

```
[STEP1]

'뉴스요약_문서' 폴더에 https://news.naver.com/ 뉴스 요약한 md파일 만들어줘.
파일명은 '네이버_뉴스_요약.md'로 해줘.

[STEP2]
저장된 마크다운(.md) 뉴스 요약 파일을 읽어서 내 텔레그램 봇으로 전송해주는 프로그램을 만들어줘.

[원하는 기능]
- '네이버_뉴스_요약.md' 파일을 읽어서 텍스트를 추출해줘.
- 마크다운의 특수 기호(###, **)가 텔레그램에서 깨지지 않게 HTML 태그(<b> 등)로 변환해줘.
- 변환된 내용을 텔레그램 sendMessage API를 통해 내 봇으로 발송해줘.

봇 토큰과 챗 ID는 .env 파일에서 불러오게 해줘.
코드는 '뉴스요약_문서' 폴더 안에 저장해줘.
```

---

### 2단계 — 업무 자동화 (Gmail + 엑셀) (난이도: ★★☆☆☆)

```
'엑셀-Gmail자동화' 폴더에 내가 필요한 파일들이 있어. 
'고객리스트.xlsx' 파일에는 고객들의 이메일 주소가 있고, '이메일_템플릿.docx' 워드 파일에는 보낼 메일 양식이 들어있어.
이걸 읽어서 각 고객에게 맞춤형 메일을 보내는 프로그램을 만들어줘.

[원하는 기능]
- 워드 템플릿의 {회사명}, {담당자} 부분을 엑셀에 적힌 실제 정보로 바꿔서 보내줘.
- 메일을 성공적으로 보냈다면, 엑셀의 '발송상태' 칸에 '발송 완료'라고 적고 날짜도 기록해줘.
- 이미 '발송 완료'라고 적힌 사람은 건너뛰고 안 보낸 사람에게만 보내줘.

비밀번호는 보안을 위해 .env 파일에서 불러오게 해줘.
코드는 '엑셀-Gmail자동화' 폴더 안에 저장해줘.
```

---

### 3단계 — 데이터 분석 (카드 지출 내역) (난이도: ★★★☆☆)

```
'카드지출분석' 폴더에 있는 '카드명세서_2026년4월.xlsx' 파일을 분석해서 예쁜 워드 보고서를 만들어주는 프로그램을 만들어줘.

[보고서에 들어갈 내용]
- 이번 달 총 지출 금액과 총 결제 건수 요약
- 식비, 교통, 쇼핑 등 카테고리별로 얼마를 썼고 전체의 몇 %인지 분석한 표
- 가장 돈을 많이 쓴 가맹점 TOP 5 순위표
- 넷플릭스나 유튜브 같은 정기구독 결제 내역만 따로 모은 목록

보고서는 파란색 계열의 깔끔한 디자인으로 만들어주고, 파일명은 '카드지출분석_보고서.docx'로 해줘.
코드는 '카드지출분석' 폴더 안에 저장해줘.
```

---

### 4단계 — 뉴스 요약 및 디스코드 전송 (난이도: ★★★★☆)

```
네이버 뉴스(https://news.naver.com)의 정치(100)와 경제(101) 섹션 뉴스를 수집해서 요약하고, 
그 내용을 디스코드와 카카오톡으로 보내주는 프로그램을 만들어줘.

[원하는 기능]
- 정치 뉴스와 경제 뉴스를 각각 10개씩 수집해줘.
- Google Gemini를 사용해 정치와 경제 이슈를 구분해서 요약해줘.
- 디스코드 웹훅 1번에는 정치 뉴스 요약만, 웹훅 2번에는 경제 뉴스 요약만 보내줘.
- 카카오톡 전송은 Claude Code Play MCP 방식으로 구성해줘.
  Python 스크립트는 전송할 메시지를 kakao_pending.json에 저장하고,
  Claude가 그 파일을 읽어서 KakaotalkChat-MemoChat MCP 도구로 실제 전송해.
  메시지가 200자를 넘으면 자동으로 분할해서 여러 개로 나눠 보내줘.
- 실행 코드는 '뉴스요약' 폴더에, 요약 결과(.md)는 '뉴스요약_문서' 폴더에 저장해줘.

웹훅 URL과 API 키는 .env 파일에서 불러오게 해줘.
```

---

### 4-1단계 — 카카오톡 MCP 전송 자동화 (난이도: ★★★★☆)

```
'뉴스요약/main.py'의 카카오톡 전송 방식을 Claude Code Play MCP 방식으로 자동화해줘.

[구조]
- Python 스크립트(kakao_sender.py)는 실제 전송 대신 메시지를 kakao_pending.json 파일로 저장해.
- 메시지가 200자를 넘으면 190자 단위로 자동 분할해서 배열로 저장해.
- Claude는 python main.py --kakao-only 실행 후 kakao_pending.json을 읽어서
  KakaotalkChat-MemoChat MCP 도구로 각 메시지를 순서대로 전송해.

[이유]
Python에서 Claude Code MCP 도구를 직접 호출할 수 없기 때문에,
파일 기반 중간 저장소를 통해 Python(수집/요약) ↔ Claude MCP(전송) 역할을 분리해.
```

---

### 5단계 — 송파소식 크롤링 (난이도: ★★★★★)

```
playwright mcp를 이용해서 송파소식 정보마당(https://songpa.newstool.co.kr/list_section.php?sid=412&bpage=1)에서
송파커뮤니티센터의 교육 프로그램 정보를 수집해서 내 텔레그램 봇으로 보내주는 프로그램을 만들어줘.

[원하는 기능]
- 목록 페이지에서 '[교육정보]' 제목을 포함한 게시글만 골라내줘.
- 상세 페이지에서 '송파커뮤니티센터'와 '프로그램 수강생 모집'이 들어간 섹션을 찾아줘.
- 해당 프로그램의 안내 텍스트와 이미지(QR코드 포함)를 추출해줘.
- 이미 보낸 게시물은 중복해서 보내지 않게 파일로 기록해서 관리해줘.
- 현재 날짜 기준으로 지난 달 이전의 정보는 제외하고 최신 정보만 보내줘.

봇 토큰과 챗 ID는 .env 파일에서 불러오게 해줘.
코드는 '송파커뮤니티센터-정보' 폴더 안에 저장해줘.
```

---

## 자주 만나는 트러블슈팅

| 증상 | 원인 / 해결 |
|---|---|
| `python: command not found` (Windows) | PATH 미설정 → 위 "환경변수 직접 추가" 참고하거나 Python 재설치 시 `Add to PATH` 체크 |
| `command not found: python` (macOS) | `python3` 로 시도. 그래도 안 되면 Homebrew로 설치 |
| `Activate.ps1 ... 실행할 수 없음` | PowerShell `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` |
| `pip` 도 안 먹음 | `python -m pip ...` 형태로 호출 (macOS는 `python3 -m pip`) |
| 패키지 설치가 매우 느리거나 설치불가능 | 사내망이면 프록시 문제 가능, IT담당자에게 요청 |
| 한글 CSV가 깨져 보임 | 1번 코드는 cp949/utf-8 자동 시도. 그래도 깨지면 엑셀에서 한 번 열어 UTF-8로 다시 저장 |
