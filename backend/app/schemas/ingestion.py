from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from app.models.article import ArticleVertical


class SourceArticle(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    title: str
    url: HttpUrl
    source_name: str
    published_at: datetime
    raw_content: str | None = None
    image_url: HttpUrl | None = None


class ArticleClassification(BaseModel):
    vertical: ArticleVertical = ArticleVertical.GENERAL
    region: str = "Global"


class CompanyExtractionResult(BaseModel):
    companies: list[str] = Field(default_factory=list)

