from __future__ import annotations

from app.config import Settings, get_settings
from app.platforms.base import BasePlatform
from app.platforms.bluesky import BlueskyPlatform
from app.platforms.devto import DevToPlatform
from app.platforms.discord import DiscordPlatform
from app.platforms.mastodon import MastodonPlatform
from app.platforms.telegram import TelegramPlatform
from app.schemas import PlatformResult, PostingResponse


def build_platforms(settings: Settings | None = None) -> list[BasePlatform]:
    cfg = settings or get_settings()
    return [
        DevToPlatform(cfg),
        MastodonPlatform(cfg),
        BlueskyPlatform(cfg),
        TelegramPlatform(cfg),
        DiscordPlatform(cfg),
    ]


async def post_to_all_platforms(
    message: str,
    settings: Settings | None = None,
) -> PostingResponse:
    platforms = build_platforms(settings)
    results: list[PlatformResult] = []

    for platform in platforms:
        result = await platform.post(message)
        results.append(result)

    success = any(item.status == "success" for item in results)
    return PostingResponse(success=success, results=results)
