from __future__ import annotations

import httpx

from app.platforms.base import BasePlatform
from app.schemas import PlatformResult


class MastodonPlatform(BasePlatform):
    name = "Mastodon"

    def has_credentials(self) -> bool:
        return bool(
            self.settings.mastodon_base_url and self.settings.mastodon_access_token
        )

    async def publish(self, message: str) -> PlatformResult:
        base_url = self.settings.mastodon_base_url.rstrip("/")
        headers = {
            "Authorization": f"Bearer {self.settings.mastodon_access_token}",
        }
        form = {"status": message}

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{base_url}/api/v1/statuses",
                data=form,
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()

        return self._success_result(data.get("url"), public_access=True)
