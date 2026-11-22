from __future__ import annotations

from app.models.article import ArticleVertical
from app.services.article_classifier import ArticleClassifierService


class _FailingOpenAI:
    """Stand-in that always fails, forcing the deterministic fallback paths."""

    async def complete_json(self, **kwargs):
        raise RuntimeError("no LLM configured")

    async def complete_list(self, **kwargs):
        raise RuntimeError("no LLM configured")


async def test_classify_article_falls_back_to_keywords():
    service = ArticleClassifierService(openai=_FailingOpenAI())

    result = await service.classify_article("Startup raises Series A funding round", "They raised a seed round")

    assert result.vertical == ArticleVertical.FUNDING


async def test_classify_article_detects_layoffs_region():
    service = ArticleClassifierService(openai=_FailingOpenAI())

    result = await service.classify_article("Big layoff hits India unit", "job cut announced")

    assert result.vertical == ArticleVertical.LAYOFFS
    assert result.region == "India"


async def test_extract_companies_returns_empty_on_failure():
    service = ArticleClassifierService(openai=_FailingOpenAI())

    result = await service.extract_companies("Some title", "Some content")

    assert result.companies == []
