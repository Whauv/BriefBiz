from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

from app.models.article import ArticleSentiment


class DeepDivePayload(BaseModel):
    what_happened: str
    key_players: list[str] = Field(default_factory=list)
    market_impact: str
    whats_next: str


class SentimentImpactPayload(BaseModel):
    sentiment: ArticleSentiment
    impact_score: float

    @field_validator("impact_score")
    @classmethod
    def clamp_score(cls, value: float) -> float:
        return max(0.0, min(1.0, value))


class ArticleEnrichmentPayload(BaseModel):
    summary_60w: str
    deep_dive: DeepDivePayload
    sentiment_impact: SentimentImpactPayload
    why_it_matters: str

