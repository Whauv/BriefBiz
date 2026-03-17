from __future__ import annotations

from pydantic import BaseModel

from app.schemas.articles import ArticleCardResponse


class SearchCompanyResult(BaseModel):
    id: int
    name: str
    slug: str
    sector: str | None


class SearchResponse(BaseModel):
    articles: list[ArticleCardResponse]
    companies: list[SearchCompanyResult]

