# Research-online

텔레그램에서 받은 요청을 현재 저장소 기준으로 처리하는 Codex 코딩 에이전트 프로젝트입니다.  
봇은 사용자의 메시지를 받아 `codex exec`로 전달하고, 결과를 다시 텔레그램으로 응답합니다.  
리서치 결과 문서는 `research/`에 저장하고, 필요하면 `automation/`으로 자동 커밋/푸시를 붙일 수 있습니다.

## 핵심 구성

- `app.py`
  현재 기준 메인 실행 파일입니다. 상태 파일 저장, 오래된 업데이트 건너뛰기, 타임아웃 설정, `/pwd`, `/reset` 같은 운영 기능이 들어 있습니다.
- `research/`
  조사 결과나 정리 문서를 보관하는 폴더입니다.
- `automation/`
  macOS `launchd` 기반 자동 커밋/푸시 설정입니다. 자세한 내용은 `automation/README.md`를 보면 됩니다.

## 동작 방식

1. 사용자가 텔레그램으로 메시지를 보냅니다.
2. 봇이 허용된 사용자 여부를 확인합니다.
3. 메시지를 프롬프트에 넣어 `codex exec`를 현재 저장소에서 실행합니다.
4. Codex가 이 저장소의 파일을 읽고 필요하면 수정합니다.
5. 결과를 텔레그램으로 다시 전송합니다.

즉, 이 저장소는 단순한 예제가 아니라 "텔레그램 인터페이스 + 로컬 Codex 작업 폴더 + 리서치 문서 저장소" 역할을 같이 합니다.

## 요구 사항

- Python 3.10+
- 로컬에 설치된 `codex` CLI
- 텔레그램 봇 토큰
- 필요 시 Codex/OpenAI 인증이 완료된 로컬 환경

Python 패키지는 `requirements.txt`로 설치하지만, `codex` CLI 자체는 별도로 준비되어 있어야 합니다.

## 빠른 시작

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

`.env`를 채운 뒤 실행합니다.

```bash
python3 app.py
```

## 환경 변수

`.env.example` 기준으로 아래 값을 설정하면 됩니다.

- `TELEGRAM_BOT_TOKEN`
  텔레그램 봇 토큰
- `CODEX_WORKDIR`
  Codex가 작업할 저장소 경로. 보통 이 프로젝트 루트 경로를 넣습니다.
- `ALLOWED_TELEGRAM_USER_ID`
  허용할 텔레그램 사용자 ID. 비워 두면 제한이 없습니다.
- `BOT_USERNAME`
  봇 계정명
- `BOT_URL`
  봇 링크
- `CODEX_TIMEOUT_SECONDS`
  Codex 실행 제한 시간
- `CODEX_FULL_AUTO`
  `codex exec --full-auto` 사용 여부
- `CODEX_SKIP_GIT_REPO_CHECK`
  git 저장소 검사 스킵 여부
- `SKIP_OLD_UPDATES_ON_START`
  실행 시 예전 메시지 무시 여부
- `STATE_FILE`
  마지막 `update_id` 저장 파일 경로

`OPENAI_API_KEY`도 예시 파일에 들어 있지만, 실제 사용 여부는 로컬 Codex/OpenAI 인증 방식에 따라 달라질 수 있습니다.

## 텔레그램 명령

- `/start`
  봇 정보와 작업 폴더를 확인합니다.
- `/status`
  현재 설정값과 상태를 확인합니다.
- `/pwd`
  현재 작업 폴더를 확인합니다.
- `/reset`
  저장된 업데이트 상태를 초기화합니다.

## 디렉터리 구조

```text
.
├── app.py
├── research/
├── automation/
├── .env.example
└── requirements.txt
```

## 운영 메모

- 실제 운영 기준 엔트리포인트는 `app.py`입니다.
- 결과 문서가 쌓이면 `research/` 아래에 주제별 Markdown 파일로 관리하면 됩니다.
- 자동 푸시는 선택 사항입니다. 활성화하려면 `automation/README.md`의 `launchd` 설정을 따르세요.
- 민감한 작업이라면 `ALLOWED_TELEGRAM_USER_ID`를 반드시 설정하는 편이 안전합니다.

## 관련 문서

- `automation/README.md`: 자동 커밋/푸시 설정
- `research/`: 조사 결과 예시 문서
