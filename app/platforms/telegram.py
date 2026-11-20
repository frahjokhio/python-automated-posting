from __future__ import annotations

import httpx

from app.platforms.base import BasePlatform
from app.schemas import PlatformResult


class TelegramPlatform(BasePlatform):
    name = "Telegram"

    def has_credentials(self) -> bool:
        return bool(
            self.settings.telegram_bot_token and self.settings.telegram_chat_id
        )

    async def publish(self, message: str) -> PlatformResult:
        token = self.settings.telegram_bot_token
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": self.settings.telegram_chat_id,
            "text": message,
            "disable_web_page_preview": False,
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()

        if not data.get("ok"):
            description = data.get("description", "Telegram API error")
            return self._failed_result(description)

        result = data.get("result", {})
        chat = result.get("chat", {})
        message_id = result.get("message_id")
        username = chat.get("username")

        posted_url = None
        if username and message_id:
            posted_url = f"https://t.me/{username}/{message_id}"

        # Channel/group posts with a username are public; private chats are not.
        public_access = bool(username)
        return self._success_result(posted_url, public_access=public_access)
