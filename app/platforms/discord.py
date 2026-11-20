from __future__ import annotations

import httpx

from app.platforms.base import BasePlatform
from app.schemas import PlatformResult


class DiscordPlatform(BasePlatform):
    name = "Discord"

    def has_credentials(self) -> bool:
        return bool(self.settings.discord_webhook_url)

    async def publish(self, message: str) -> PlatformResult:
        webhook_url = self.settings.discord_webhook_url
        # Request the created message so we can return an id when available.
        if "?" in webhook_url:
            request_url = f"{webhook_url}&wait=true"
        else:
            request_url = f"{webhook_url}?wait=true"

        payload = {"content": message}

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(request_url, json=payload)
            response.raise_for_status()
            data = response.json() if response.content else {}

        message_id = data.get("id")
        channel_id = data.get("channel_id")
        posted_url = None
        if message_id and channel_id:
            posted_url = f"https://discord.com/channels/@me/{channel_id}/{message_id}"

        # Webhook posts land in a server channel; treat as publicly reachable
        # only when Discord returned message metadata.
        return self._success_result(
            posted_url,
            public_access=bool(posted_url),
        )
