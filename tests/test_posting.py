from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.config import Settings
from app.main import app
from app.schemas import PostingRequest
from app.services.posting_service import post_to_all_platforms

client = TestClient(app)

VALID_MESSAGE = (
    "Check out our latest business platform and grow online. https://example.com"
)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_posting_dry_run_returns_five_results() -> None:
    response = client.post("/posting", json={"message": VALID_MESSAGE})
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert len(body["results"]) == 5
    platforms = {item["platform"] for item in body["results"]}
    assert platforms == {"Dev.to", "Mastodon", "Bluesky", "Telegram", "Discord"}
    assert all(item["status"] == "success" for item in body["results"])
    assert all(item["posted_url"] for item in body["results"])


def test_message_too_long() -> None:
    long_message = ("x" * 181) + " https://example.com"
    assert len(long_message) > 200
    response = client.post("/posting", json={"message": long_message})
    assert response.status_code == 422


def test_message_without_url() -> None:
    response = client.post(
        "/posting",
        json={"message": "Hello world without a call to action"},
    )
    assert response.status_code == 422


def test_message_with_two_urls() -> None:
    response = client.post(
        "/posting",
        json={
            "message": "See https://one.example.com and https://two.example.com",
        },
    )
    assert response.status_code == 422


def test_message_with_invalid_url() -> None:
    with pytest.raises(ValidationError):
        PostingRequest(message="Broken CTA link here http:///bad")


@pytest.mark.asyncio
async def test_missing_credentials_fails_when_not_dry_run() -> None:
    settings = Settings(
        dry_run=False,
        devto_api_key="",
        mastodon_access_token="",
        bluesky_handle="",
        bluesky_app_password="",
        telegram_bot_token="",
        telegram_chat_id="",
        discord_webhook_url="",
    )

    result = await post_to_all_platforms(VALID_MESSAGE, settings=settings)
    assert result.success is False
    assert len(result.results) == 5
    assert all(item.status == "failed" for item in result.results)
    assert all(item.error == "Missing credentials" for item in result.results)
