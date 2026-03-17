from __future__ import annotations

import asyncio

from pydantic import BaseModel

from app.models.article import ArticleSentiment
from app.schemas.enrichment import (
    ArticleEnrichmentPayload,
    DeepDivePayload,
    SentimentImpactPayload,
)
from app.services.openai_client import OpenAIStructuredService


class SummaryPayload(BaseModel):
    summary_60w: str


class WhyItMattersPayload(BaseModel):
    why_it_matters: str


class ArticleEnrichmentService:
    def __init__(self) -> None:
        self.openai = OpenAIStructuredService()

    async def enrich_article(self, *, title: str, content: str, source_name: str) -> ArticleEnrichmentPayload:
        summary_task = self._generate_summary(title=title, content=content, source_name=source_name)
        deep_dive_task = self._generate_deep_dive(title=title, content=content)
        sentiment_task = self._generate_sentiment_and_impact(title=title, content=content)
        why_task = self._generate_why_it_matters(title=title, content=content)

        try:
            summary, deep_dive, sentiment_impact, why_it_matters = await asyncio.gather(
                summary_task,
                deep_dive_task,
                sentiment_task,
                why_task,
            )
        except Exception:
            return self._fallback_payload(title=title, content=content)

        return ArticleEnrichmentPayload(
            summary_60w=summary.summary_60w,
            deep_dive=deep_dive,
            sentiment_impact=sentiment_impact,
            why_it_matters=why_it_matters.why_it_matters,
        )

    async def _generate_summary(self, *, title: str, content: str, source_name: str) -> SummaryPayload:
        prompt = f"""
Summarize the following news article in exactly 60 words.
Be factual, concise, and include what happened, who is involved, key numbers, and why it matters to the business world.
Do not editorialize.

Source: {source_name}
Title: {title}
Article:
{content}
""".strip()
        return await self.openai.complete_json(prompt=prompt, response_model=SummaryPayload)

    async def _generate_deep_dive(self, *, title: str, content: str) -> DeepDivePayload:
        prompt = f"""
Given this article, return a JSON with four fields:
- what_happened: 50 words
- key_players: list of names or companies
- market_impact: 40 words
- whats_next: 30 words

Title: {title}
Article:
{content}
""".strip()
        return await self.openai.complete_json(prompt=prompt, response_model=DeepDivePayload)

    async def _generate_sentiment_and_impact(self, *, title: str, content: str) -> SentimentImpactPayload:
        prompt = f"""
Classify this business news article as one of: bullish, bearish, risk, neutral.
Also give an impact_score from 0.0 to 1.0 based on how significant this news is for the startup/business ecosystem.
Return JSON: {{ "sentiment": "...", "impact_score": 0.0 }}

Title: {title}
Article:
{content}
""".strip()
        return await self.openai.complete_json(prompt=prompt, response_model=SentimentImpactPayload)

    async def _generate_why_it_matters(self, *, title: str, content: str) -> WhyItMattersPayload:
        prompt = f"""
In one sentence, maximum 20 words, explain the broader strategic implication of this news for startup founders or investors.
Return JSON with the field `why_it_matters`.

Title: {title}
Article:
{content}
""".strip()
        return await self.openai.complete_json(prompt=prompt, response_model=WhyItMattersPayload)

    def _fallback_payload(self, *, title: str, content: str) -> ArticleEnrichmentPayload:
        compact_content = " ".join(content.split())
        summary = _truncate_words(compact_content or title, 60)
        what_happened = _truncate_words(compact_content or title, 50)
        market_impact = _truncate_words(f"This development may affect markets, founders, and investors. {compact_content}", 40)
        whats_next = _truncate_words("Watch for company responses, financing activity, and market reaction in the coming days.", 30)
        why_it_matters = _truncate_words("This signals how quickly business conditions can shift for founders and investors.", 20)

        return ArticleEnrichmentPayload(
            summary_60w=summary,
            deep_dive=DeepDivePayload(
                what_happened=what_happened,
                key_players=[],
                market_impact=market_impact,
                whats_next=whats_next,
            ),
            sentiment_impact=SentimentImpactPayload(
                sentiment=ArticleSentiment.NEUTRAL,
                impact_score=0.5,
            ),
            why_it_matters=why_it_matters,
        )


def source_quality_score(source_name: str) -> float:
    normalized = source_name.casefold()
    if "bloomberg" in normalized:
        return 0.95
    if "forbes" in normalized:
        return 0.88
    if "techcrunch" in normalized:
        return 0.85
    if "venturebeat" in normalized:
        return 0.80
    return 0.60


def _truncate_words(text: str, limit: int) -> str:
    words = text.split()
    if not words:
        return ""
    truncated = words[:limit]
    return " ".join(truncated)
