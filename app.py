import os
import subprocess
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
WORKDIR = os.getenv("CODEX_WORKDIR", os.getcwd()).strip()
ALLOWED_USER_ID_RAW = os.getenv("ALLOWED_TELEGRAM_USER_ID", "").strip()
BOT_USERNAME = os.getenv("BOT_USERNAME", "").strip()
BOT_URL = os.getenv("BOT_URL", "").strip()

CODEX_TIMEOUT_SECONDS = int(os.getenv("CODEX_TIMEOUT_SECONDS", "900"))
CODEX_FULL_AUTO = os.getenv("CODEX_FULL_AUTO", "true").strip().lower() in {"1", "true", "yes", "on"}
CODEX_SKIP_GIT_REPO_CHECK = os.getenv("CODEX_SKIP_GIT_REPO_CHECK", "true").strip().lower() in {"1", "true", "yes", "on"}
SKIP_OLD_UPDATES_ON_START = os.getenv("SKIP_OLD_UPDATES_ON_START", "true").strip().lower() in {"1", "true", "yes", "on"}

STATE_FILE = os.getenv("STATE_FILE", ".telegram_state").strip()

ALLOWED_USER_ID = int(ALLOWED_USER_ID_RAW) if ALLOWED_USER_ID_RAW else None

if not BOT_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN이 .env에 없습니다.")

if not os.path.isdir(WORKDIR):
    raise RuntimeError(f"CODEX_WORKDIR가 존재하지 않습니다: {WORKDIR}")

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"
last_update_id = None


def tg_get(method, params=None, timeout=40):
    r = requests.get(f"{BASE_URL}/{method}", params=params or {}, timeout=timeout)
    r.raise_for_status()
    return r.json()


def tg_post(method, payload=None, timeout=40):
    r = requests.post(f"{BASE_URL}/{method}", json=payload or {}, timeout=timeout)
    r.raise_for_status()
    return r.json()


def send_message(chat_id, text):
    text = (text or "응답이 비어 있습니다.").strip()
    chunk_size = 3500

    for i in range(0, len(text), chunk_size):
        tg_post(
            "sendMessage",
            {
                "chat_id": chat_id,
                "text": text[i:i + chunk_size],
            },
        )


def load_last_update_id():
    global last_update_id

    state_path = Path(STATE_FILE)
    if not state_path.exists():
        last_update_id = None
        return

    raw = state_path.read_text(encoding="utf-8").strip()
    last_update_id = int(raw) if raw else None


def save_last_update_id():
    if last_update_id is None:
        return

    Path(STATE_FILE).write_text(str(last_update_id), encoding="utf-8")


def initialize_last_update_id():
    """
    앱을 처음 띄울 때 예전 메시지를 다시 처리하지 않도록,
    현재 쌓여 있는 update 중 마지막 update_id를 기억한다.
    """
    global last_update_id

    response = tg_get("getUpdates", params={"timeout": 1}, timeout=5)
    updates = response.get("result", [])

    if updates:
        last_update_id = updates[-1]["update_id"]
        save_last_update_id()
        print(f"skip old updates until update_id={last_update_id}")
    else:
        print("no old updates to skip")


def build_codex_command(user_text):
    prompt = f"""
너는 텔레그램에서 동작하는 Codex 코딩 에이전트다.
현재 작업 디렉터리의 파일과 코드를 기준으로 사용자의 요청을 처리하라.
필요하면 현재 작업 디렉터리 안에 파일을 생성하거나 수정하라.
답변은 간결하고 실행 가능하게 작성하라.
작업 결과로 파일을 만들거나 수정했다면, 마지막에 어떤 파일을 건드렸는지 짧게 적어라.

사용자 요청:
{user_text}
""".strip()

    cmd = ["codex", "exec"]

    if CODEX_SKIP_GIT_REPO_CHECK:
        cmd.append("--skip-git-repo-check")

    if CODEX_FULL_AUTO:
        cmd.append("--full-auto")

    cmd.append(prompt)
    return cmd


def run_codex(user_text):
    cmd = build_codex_command(user_text)

    try:
        result = subprocess.run(
            cmd,
            cwd=WORKDIR,
            capture_output=True,
            text=True,
            timeout=CODEX_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        return (
            "[Codex 오류]\n"
            f"작업 시간이 {CODEX_TIMEOUT_SECONDS}초를 초과했습니다.\n"
            "요청을 더 작게 나누거나 timeout 값을 늘려주세요."
        )
    except FileNotFoundError:
        return "[Codex 오류]\n`codex` 명령을 찾을 수 없습니다. Codex CLI 설치 상태를 확인하세요."

    if result.returncode != 0:
        err = result.stderr.strip() or result.stdout.strip() or "알 수 없는 오류"
        return f"[Codex 오류]\n{err}"

    return result.stdout.strip() or "작업은 완료된 것 같지만 출력이 비어 있습니다."


def handle_command(chat_id, text):
    global last_update_id

    if text == "/start":
        lines = ["Codex Telegram Agent 준비 완료."]
        if BOT_USERNAME:
            lines.append(f"봇: @{BOT_USERNAME}")
        if BOT_URL:
            lines.append(f"링크: {BOT_URL}")
        lines.append(f"작업 폴더: {WORKDIR}")
        lines.append(f"허용 사용자 ID: {ALLOWED_USER_ID if ALLOWED_USER_ID is not None else '제한 없음'}")
        send_message(chat_id, "\n".join(lines))
        return True

    if text == "/status":
        lines = [
            "현재 상태",
            f"- workdir: {WORKDIR}",
            f"- allowed_user_id: {ALLOWED_USER_ID if ALLOWED_USER_ID is not None else '미설정'}",
            f"- timeout_seconds: {CODEX_TIMEOUT_SECONDS}",
            f"- full_auto: {CODEX_FULL_AUTO}",
            f"- skip_git_repo_check: {CODEX_SKIP_GIT_REPO_CHECK}",
            f"- last_update_id: {last_update_id}",
            f"- bot: @{BOT_USERNAME}" if BOT_USERNAME else "- bot: 미설정",
        ]
        send_message(chat_id, "\n".join(lines))
        return True

    if text == "/pwd":
        send_message(chat_id, WORKDIR)
        return True

    if text == "/reset":
        last_update_id = None
        if Path(STATE_FILE).exists():
            Path(STATE_FILE).unlink()
        send_message(chat_id, "상태 파일을 초기화했습니다.")
        return True

    return False


def main():
    global last_update_id

    print(f"BOT_USERNAME={BOT_USERNAME}")
    print(f"BOT_URL={BOT_URL}")
    print(f"WORKDIR={WORKDIR}")
    print(f"ALLOWED_USER_ID={ALLOWED_USER_ID}")
    print(f"CODEX_TIMEOUT_SECONDS={CODEX_TIMEOUT_SECONDS}")
    print(f"CODEX_FULL_AUTO={CODEX_FULL_AUTO}")
    print(f"CODEX_SKIP_GIT_REPO_CHECK={CODEX_SKIP_GIT_REPO_CHECK}")
    print(f"STATE_FILE={STATE_FILE}")

    load_last_update_id()

    if last_update_id is None and SKIP_OLD_UPDATES_ON_START:
        initialize_last_update_id()

    while True:
        try:
            params = {"timeout": 30}
            if last_update_id is not None:
                params["offset"] = last_update_id + 1

            response = tg_get("getUpdates", params=params, timeout=40)
            updates = response.get("result", [])

            for upd in updates:
                last_update_id = upd["update_id"]
                save_last_update_id()

                msg = upd.get("message", {})
                chat = msg.get("chat", {})
                user = msg.get("from", {})

                chat_id = chat.get("id")
                user_id = user.get("id")
                text = msg.get("text")

                print(f"chat_id={chat_id}, user_id={user_id}, text={text!r}")

                if not chat_id or not text:
                    continue

                if ALLOWED_USER_ID is not None and user_id != ALLOWED_USER_ID:
                    send_message(chat_id, "접근 권한이 없습니다.")
                    continue

                if handle_command(chat_id, text):
                    continue

                send_message(chat_id, "작업 중...")
                answer = run_codex(text)
                send_message(chat_id, answer)

            time.sleep(1)

        except requests.RequestException as e:
            print(f"[telegram error] {e}")
            time.sleep(3)
        except Exception as e:
            print(f"[unexpected error] {e}")
            time.sleep(3)


if __name__ == "__main__":
    main()
