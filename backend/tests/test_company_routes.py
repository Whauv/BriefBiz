from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from app.db.session import get_db_session
from app.main import app
from app.models.article import Article, ArticleSentiment, ArticleVertical
from app.models.company import Company


@pytest.mark.asyncio
async def test_company_profile_returns_related_articles(client, execute_result):
    company = Company(
        id=5,
        name="Acme",
        slug="acme",
        sector="SaaS",
        hq_country="US",
        funding_stage="Series B",
        investors=["SeedCo"],
        article_count=1,
        last_headline="Acme expands",
        created_at=datetime.now(UTC),
    )
    article = Article(
        id=11,
        title="Acme expands",
        url="https://example.com/acme",
        url_hash="hash-acme",
        source_name="Forbes",
        source_quality_score=0.88,
        published_at=datetime.now(UTC),
        raw_content="Acme grows",
        summary_60w="Acme announced an expansion.",
        deep_dive={"what_happened": "", "key_players": [], "market_impact": "", "whats_next": ""},
        sentiment=ArticleSentiment.BULLISH,
        impact_score=0.77,
        vertical=ArticleVertical.GENERAL,
        region="US",
        image_url=None,
        audio_url=None,
        why_it_matters="Acme keeps scaling.",
    )

    session = AsyncMock()
    session.execute.side_effect = [
        execute_result(scalar_one_or_none=company),
        execute_result(scalars=[article]),
        execute_result(all_rows=[(11, "Acme")]),
    ]

    async def override_db():
        yield session

    app.dependency_overrides[get_db_session] = override_db
    response = await client.get("/companies/acme")

    assert response.status_code == 200
    payload = response.json()
    assert payload["slug"] == "acme"
    assert payload["articles"][0]["title"] == "Acme expands"
