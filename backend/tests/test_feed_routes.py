from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from app.db.session import get_db_session
from app.main import app
from app.models.article import Article, ArticleSentiment, ArticleVertical


@pytest.mark.asyncio
async def test_feed_returns_paginated_cards(client, execute_result):
    article = Article(
        id=101,
        title="Startup raises Series A",
        url="https://example.com/a",
        url_hash="hash",
        source_name="TechCrunch",
        source_quality_score=0.85,
        published_at=datetime.now(UTC),
        raw_content="Startup raised capital",
        summary_60w="A startup raised capital in a notable round.",
        deep_dive={"what_happened": "", "key_players": [], "market_impact": "", "whats_next": ""},
        sentiment=ArticleSentiment.BULLISH,
        impact_score=0.91,
        vertical=ArticleVertical.FUNDING,
        region="US",
        image_url=None,
        audio_url=None,
        why_it_matters="Fundraising appetite remains active.",
    )

    session = AsyncMock()
    session.execute.side_effect = [
        execute_result(scalar_one=1),
        execute_result(scalars=[article]),
        execute_result(all_rows=[(101, "Acme")]),
    ]

    async def override_db():
        yield session

    app.dependency_overrides[get_db_session] = override_db

    response = await client.get("/feed")

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 1
    assert payload["items"][0]["title"] == "Startup raises Series A"
    assert payload["items"][0]["companies"] == ["Acme"]
