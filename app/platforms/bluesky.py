from __future__ import annotations

from datetime import datetime, timezone

import httpx

from app.platforms.base import BasePlatform
from app.schemas import PlatformResult

BLUESKY_SERVICE = "https://bsky.social"


class BlueskyPlatform(BasePlatform):
    name = "Bluesky"

    def has_credentials(self) -> bool:
        return bool(
            self.settings.bluesky_handle and self.settings.bluesky_app_password
        )

    async def publish(self, message: str) -> PlatformResult:
        async with httpx.AsyncClient(timeout=30.0) as client:
            session_response = await client.post(
                f"{BLUESKY_SERVICE}/xrpc/com.atproto.server.createSession",
                json={
                    "identifier": self.settings.bluesky_handle,
                    "password": self.settings.bluesky_app_password,
                },
            )
            session_response.raise_for_status()
            session = session_response.json()

            did = session["did"]
            access_jwt = session["accessJwt"]
            handle = session.get("handle", self.settings.bluesky_handle)
            created_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

            record = {
                "$type": "app.bsky.feed.post",
                "text": message,
                "createdAt": created_at,
            }
            create_response = await client.post(
                f"{BLUESKY_SERVICE}/xrpc/com.atproto.repo.createRecord",
                headers={"Authorization": f"Bearer {access_jwt}"},
                json={
                    "repo": did,
                    "collection": "app.bsky.feed.post",
                    "record": record,
                },
            )
            create_response.raise_for_status()
            data = create_response.json()

        uri = data.get("uri", "")
        rkey = uri.rsplit("/", 1)[-1] if uri else ""
        posted_url = (
            f"https://bsky.app/profile/{handle}/post/{rkey}" if rkey else None
        )
        return self._success_result(posted_url, public_access=True)
