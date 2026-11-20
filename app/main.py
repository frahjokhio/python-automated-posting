from __future__ import annotations

from fastapi import FastAPI

from app.schemas import PostingRequest, PostingResponse
from app.services.posting_service import post_to_all_platforms

app = FastAPI(
    title="Automated Multi-Platform Posting",
    description="Publish a short CTA message across multiple platforms.",
    version="1.0.0",
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/posting", response_model=PostingResponse)
async def posting(payload: PostingRequest) -> PostingResponse:
    return await post_to_all_platforms(payload.message)
