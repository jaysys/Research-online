import os
import time
import subprocess
import requests
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
WORKDIR = os.getenv("CODEX_WORKDIR", os.getcwd()).strip()
ALLOWED_USER_ID_RAW = os.getenv("ALLOWED_TELEGRAM_USER_ID", "").strip()
BOT_USERNAME = os.getenv("BOT_USERNAME", "").strip()
BOT_URL = os.getenv("BOT_URL", "").strip()

ALLOWED_USER_ID = int(ALLOWED_USER_ID_RAW) if ALLOWED_USER_ID_RAW else None

if not BOT_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN이 .env에 없습니다.")

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
    text = text or "응답이 비어 있습니다."
    chunk_size = 3500
    for i in range(0, len(text), chunk_size):
        tg_post("sendMessage", {
            "chat_id": chat_id,
            "text": text[i:i + chunk_size],
        })


def run_codex(user_text):
    prompt = f"""
너는 텔레그램에서 동작하는 Codex 코딩 에이전트다.
현재 작업 디렉터리의 파일과 코드를 기준으로 사용자의 요청을 처리하라.
필요하면 파일을 생성하라.
답변은 간결하고 실행 가능하게 작성하라.

사용자 요청:
{user_text}
""".strip()

    try:
        result = subprocess.run(
            [
                "codex",
                "exec",
                "--skip-git-repo-check",
                "--full-auto",
                prompt,
            ],
            cwd=WORKDIR,
            capture_output=True,
            text=True,
            timeout=900,
        )
        
    except subprocess.TimeoutExpired:
        return "[Codex 오류]\n작업 시간이 15분을 초과했습니다. 요청을 더 작게 나누거나 timeout을 더 늘리세요."

    if result.returncode != 0:
        err = result.stderr.strip() or result.stdout.strip() or "알 수 없는 오류"
        return f"[Codex 오류]\n{err}"

    return result.stdout.strip() or "응답이 비어 있습니다."


def handle_command(chat_id, text):
    if text == "/start":
        intro = "Codex Telegram Agent 준비 완료."
        if BOT_USERNAME:
            intro += f"\n봇: @{BOT_USERNAME}"
        if BOT_URL:
            intro += f"\n링크: {BOT_URL}"
        intro += f"\n작업 폴더: {WORKDIR}"
        send_message(chat_id, intro)
        return True

    if text == "/status":
        status = [
            "현재 상태",
            f"- workdir: {WORKDIR}",
            f"- allowed_user_id: {ALLOWED_USER_ID if ALLOWED_USER_ID is not None else '미설정'}",
            f"- bot: @{BOT_USERNAME}" if BOT_USERNAME else "- bot: 미설정",
        ]
        send_message(chat_id, "\n".join(status))
        return True

    return False


def main():
    global last_update_id

    print(f"BOT_USERNAME={BOT_USERNAME}")
    print(f"BOT_URL={BOT_URL}")
    print(f"WORKDIR={WORKDIR}")
    print(f"ALLOWED_USER_ID={ALLOWED_USER_ID}")

    while True:
        params = {"timeout": 30}
        if last_update_id is not None:
            params["offset"] = last_update_id + 1

        response = tg_get("getUpdates", params=params, timeout=40)
        updates = response.get("result", [])

        for upd in updates:
            last_update_id = upd["update_id"]

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


if __name__ == "__main__":
    main()