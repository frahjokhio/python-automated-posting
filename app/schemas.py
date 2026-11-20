from __future__ import annotations

import re
from typing import Literal
from urllib.parse import urlparse

from pydantic import BaseModel, Field, field_validator

URL_PATTERN = re.compile(
    r"https?://[^\s<>\"']+",
    re.IGNORECASE,
)


class PostingRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=200)

    @field_validator("message")
    @classmethod
    def validate_message(cls, value: str) -> str:
        message = value.strip()
        if not message:
            raise ValueError("Message must not be empty")

        if len(message) > 200:
            raise ValueError("Message must not exceed 200 characters")

        urls = URL_PATTERN.findall(message)
        if len(urls) == 0:
            raise ValueError("Message must include exactly one CTA link")
        if len(urls) > 1:
            raise ValueError("Message must include exactly one CTA link")

        parsed = urlparse(urls[0])
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("CTA link must be a valid URL")

        return message


class PlatformResult(BaseModel):
    platform: str
    status: Literal["success", "failed"]
    posted_url: str | None = None
    public_access: bool = False
    date: str | None = None
    time: str | None = None
    error: str | None = None


class PostingResponse(BaseModel):
    success: bool
    results: list[PlatformResult]
