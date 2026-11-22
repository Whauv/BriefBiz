from __future__ import annotations

from app.models.article import ArticleSentiment
from app.services.enrichment import ArticleEnrichmentService, source_quality_score


class _FailingOpenAI:
    async def complete_json(self, **kwargs):
        raise RuntimeError("no LLM configured")

    async def complete_list(self, **kwargs):
        raise RuntimeError("no LLM configured")


async def test_enrich_article_returns_deterministic_fallback():
    service = ArticleEnrichmentService(openai=_FailingOpenAI())

    payload = await service.enrich_article(
        title="Markets wobble",
        content="A long article about market movements and their causes.",
        source_name="Bloomberg",
    )

    assert payload.summary_60w  # non-empty deterministic summary
    assert payload.sentiment_impact.sentiment == ArticleSentiment.NEUTRAL
    assert payload.sentiment_impact.impact_score == 0.5
    assert payload.why_it_matters


def test_source_quality_score_ranks_known_sources():
    assert source_quality_score("Bloomberg Markets") == 0.95
    assert source_quality_score("TechCrunch") == 0.85
    assert source_quality_score("Some Random Blog") == 0.60
