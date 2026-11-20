from __future__ import annotations

import httpx

from app.platforms.base import BasePlatform
from app.schemas import PlatformResult


class DevToPlatform(BasePlatform):
    name = "Dev.to"

    def has_credentials(self) -> bool:
        return bool(self.settings.devto_api_key)

    async def publish(self, message: str) -> PlatformResult:
        payload = {
            "article": {
                "title": message[:80] or "Automated post",
                "body_markdown": message,
                "published": True,
            }
        }
        headers = {
            "api-key": self.settings.devto_api_key,
            "Content-Type": "application/json",
            "Accept": "application/vnd.forem.api-v1+json",
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://dev.to/api/articles",
                json=payload,
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()

        return self._success_result(data.get("url"), public_access=True)
