from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class ArticleCardResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    url: str
    source_name: str
    source_quality_score: float
    published_at: datetime
    summary_60w: str | None
    deep_dive: dict[str, Any]
    sentiment: str
    impact_score: float
    vertical: str
    region: str | None
    image_url: str | None
    audio_url: str | None
    why_it_matters: str | None
    topic_cluster: str | None
    sources_disagree: bool
    conflict_context: dict[str, Any]
    companies: list[str]


class ArticleDetailResponse(ArticleCardResponse):
    raw_content: str | None
    created_at: datetime


class ShareCardResponse(BaseModel):
    article_id: int
    title: str
    summary_60w: str | None
    source_name: str
    sentiment: str
    vertical: str
    image_url: str | None
    download_url: str | None = None


class BookmarkResponse(BaseModel):
    article_id: int
    bookmarked: bool


class ReactionRequest(BaseModel):
    reaction_text: str


class ReactionResponse(BaseModel):
    id: int
    article_id: int
    user_id: int
    reaction_text: str
    created_at: datetime
