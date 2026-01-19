import httpx

from packages.common.config import get_settings


def send_telegram(message: str) -> None:
    settings = get_settings()
    if not settings.telegram_bot_token or not settings.telegram_chat_id:
        return
    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"
    payload = {"chat_id": settings.telegram_chat_id, "text": message}
    with httpx.Client(timeout=10) as client:
        client.post(url, json=payload)
