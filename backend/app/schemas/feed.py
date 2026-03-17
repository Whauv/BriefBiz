from __future__ import annotations

from pydantic import BaseModel

from app.schemas.articles import ArticleCardResponse


class FeedResponse(BaseModel):
    page: int
    page_size: int
    total: int
    items: list[ArticleCardResponse]

