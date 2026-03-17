from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from app.schemas.articles import ArticleCardResponse


class CompanyResponse(BaseModel):
    id: int
    name: str
    slug: str
    sector: str | None
    hq_country: str | None
    funding_stage: str | None
    investors: list[str]
    article_count: int
    last_headline: str | None
    created_at: datetime
    articles: list[ArticleCardResponse]


class TrendingCompanyResponse(BaseModel):
    slug: str
    name: str
    article_mentions: int

