from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from app.db.session import get_db_session
from app.main import app
from app.models.article import Article, ArticleSentiment, ArticleVertical


@pytest.mark.asyncio
async def test_article_detail_returns_deep_dive(client, execute_result):
    article = Article(
        id=7,
        title="M&A heats up",
        url="https://example.com/story",
        url_hash="hash-7",
        source_name="Bloomberg",
        source_quality_score=0.95,
        published_at=datetime.now(UTC),
        raw_content="Deal details",
        summary_60w="Two companies struck a strategic acquisition deal.",
        deep_dive={"what_happened": "A deal happened", "key_players": ["Acme"], "market_impact": "", "whats_next": ""},
        sentiment=ArticleSentiment.NEUTRAL,
        impact_score=0.7,
        vertical=ArticleVertical.GENERAL,
        region="Global",
        image_url=None,
        audio_url=None,
        why_it_matters="Consolidation is accelerating.",
    )

    session = AsyncMock()
    session.execute.side_effect = [
        execute_result(scalar_one_or_none=article),
        execute_result(all_rows=[(7, "Acme")]),
    ]

    async def override_db():
        yield session

    app.dependency_overrides[get_db_session] = override_db
    response = await client.get("/articles/7")

    assert response.status_code == 200
    assert response.json()["deep_dive"]["key_players"] == ["Acme"]
