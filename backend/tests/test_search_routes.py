from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from app.db.session import get_db_session
from app.main import app
from app.models.article import Article, ArticleSentiment, ArticleVertical
from app.models.company import Company


@pytest.mark.asyncio
async def test_search_returns_articles_and_companies(client, execute_result, monkeypatch):
    article = Article(
        id=9,
        title="Fintech unicorn expands",
        url="https://example.com/fintech",
        url_hash="hash-fintech",
        source_name="VentureBeat",
        source_quality_score=0.8,
        published_at=datetime.now(UTC),
        raw_content="Expansion story",
        summary_60w="A fintech unicorn expanded internationally.",
        deep_dive={"what_happened": "", "key_players": [], "market_impact": "", "whats_next": ""},
        sentiment=ArticleSentiment.BULLISH,
        impact_score=0.82,
        vertical=ArticleVertical.GENERAL,
        region="Europe",
        image_url=None,
        audio_url=None,
        why_it_matters="Regional expansion continues.",
    )
    company = Company(
        id=3,
        name="Finco",
        slug="finco",
        sector="FinTech",
        hq_country="UK",
        funding_stage="Series C",
        investors=[],
        article_count=2,
        last_headline="Finco expands",
        created_at=datetime.now(UTC),
    )

    class FakeES:
        async def search(self, **kwargs):
            return {"hits": {"hits": [{"_id": "9"}]}}

    monkeypatch.setattr("app.api.routes.search.get_elasticsearch", lambda: FakeES())

    session = AsyncMock()
    session.execute.side_effect = [
        execute_result(scalars=[article]),
        execute_result(all_rows=[(9, "Finco")]),
        execute_result(scalars=[company]),
    ]

    async def override_db():
        yield session

    app.dependency_overrides[get_db_session] = override_db
    response = await client.get("/search", params={"q": "fintech"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["articles"][0]["id"] == 9
    assert payload["companies"][0]["slug"] == "finco"
