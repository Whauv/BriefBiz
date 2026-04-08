from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from app.db.session import get_db_session
from app.main import app
from app.models.article import Article, ArticleSentiment, ArticleVertical


@pytest.mark.asyncio
async def test_validation_errors_include_request_id(client):
    response = await client.post(
        "/auth/register",
        headers={"X-Request-ID": "req-123"},
        json={"email": "not-an-email", "password": "short", "name": ""},
    )

    assert response.status_code == 422
    assert response.json()["request_id"] == "req-123"


@pytest.mark.asyncio
async def test_search_preserves_elasticsearch_order(client, execute_result, monkeypatch):
    first = Article(
        id=3,
        title="Third result should be first",
        url="https://example.com/3",
        url_hash="hash-3",
        source_name="Bloomberg",
        source_quality_score=0.95,
        published_at=datetime.now(UTC),
        raw_content="Story 3",
        summary_60w="Third article",
        deep_dive={"what_happened": "", "key_players": [], "market_impact": "", "whats_next": ""},
        sentiment=ArticleSentiment.NEUTRAL,
        impact_score=0.61,
        vertical=ArticleVertical.GENERAL,
        region="Global",
        image_url=None,
        audio_url=None,
        why_it_matters="Ordering matters.",
    )
    second = Article(
        id=9,
        title="Ninth result should be second",
        url="https://example.com/9",
        url_hash="hash-9",
        source_name="TechCrunch",
        source_quality_score=0.85,
        published_at=datetime.now(UTC),
        raw_content="Story 9",
        summary_60w="Ninth article",
        deep_dive={"what_happened": "", "key_players": [], "market_impact": "", "whats_next": ""},
        sentiment=ArticleSentiment.BULLISH,
        impact_score=0.82,
        vertical=ArticleVertical.FUNDING,
        region="US",
        image_url=None,
        audio_url=None,
        why_it_matters="Ranking should remain stable.",
    )

    class FakeES:
        async def search(self, **kwargs):
            return {"hits": {"hits": [{"_id": "3"}, {"_id": "9"}]}}

    monkeypatch.setattr("app.api.routes.search.get_elasticsearch", lambda: FakeES())

    session = AsyncMock()
    session.execute.side_effect = [
        execute_result(scalars=[second, first]),
        execute_result(all_rows=[(3, "Alpha"), (9, "Beta")]),
        execute_result(scalars=[]),
    ]

    async def override_db():
        yield session

    app.dependency_overrides[get_db_session] = override_db

    response = await client.get("/search", params={"q": "rank"})

    assert response.status_code == 200
    payload = response.json()
    assert [article["id"] for article in payload["articles"]] == [3, 9]
