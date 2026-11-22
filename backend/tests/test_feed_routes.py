from __future__ import annotations

from datetime import UTC, datetime, timedelta

from app.models.article import ArticleSentiment, ArticleVertical
from tests.factories import (
    auth_header_for,
    create_article,
    create_company,
    create_user,
    link_article_company,
)


async def test_feed_returns_paginated_cards(db_client, db_session):
    await create_article(db_session, title="Only story", region="US")

    response = await db_client.get("/feed")

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 1
    assert payload["page"] == 1
    assert payload["items"][0]["title"] == "Only story"


async def test_feed_filters_by_vertical(db_client, db_session):
    await create_article(db_session, title="Funding one", vertical=ArticleVertical.FUNDING)
    await create_article(db_session, title="General one", vertical=ArticleVertical.GENERAL)

    response = await db_client.get("/feed", params={"vertical": "funding"})

    payload = response.json()
    assert payload["total"] == 1
    assert payload["items"][0]["title"] == "Funding one"


async def test_feed_sort_by_impact(db_client, db_session):
    await create_article(db_session, title="Low", impact_score=0.1)
    await create_article(db_session, title="High", impact_score=0.9)

    response = await db_client.get("/feed", params={"sort": "impact"})

    titles = [item["title"] for item in response.json()["items"]]
    assert titles[0] == "High"


async def test_feed_pagination_limits_page_size(db_client, db_session):
    for index in range(3):
        await create_article(db_session, title=f"Story {index}")

    response = await db_client.get("/feed", params={"page": 1, "page_size": 2})

    payload = response.json()
    assert payload["total"] == 3
    assert len(payload["items"]) == 2


async def test_personalized_feed_filters_by_preferences(db_client, db_session):
    user = await create_user(
        db_session,
        preferences={
            "sectors": [],
            "regions": ["Europe"],
            "followed_companies": [],
            "followed_investors": [],
        },
    )
    await create_article(db_session, title="EU story", region="Europe")
    await create_article(db_session, title="US story", region="US")

    response = await db_client.get("/feed/personalized", headers=auth_header_for(user))

    payload = response.json()
    titles = [item["title"] for item in payload["items"]]
    assert "EU story" in titles
    assert "US story" not in titles


async def test_personalized_feed_requires_auth(db_client):
    response = await db_client.get("/feed/personalized")
    assert response.status_code == 401


async def test_funding_radar_returns_only_funding(db_client, db_session):
    await create_article(db_session, title="Raise", vertical=ArticleVertical.FUNDING)
    await create_article(db_session, title="Layoff", vertical=ArticleVertical.LAYOFFS)

    response = await db_client.get("/feed/funding-radar")

    titles = [item["title"] for item in response.json()["items"]]
    assert titles == ["Raise"]


async def test_hot_feed_excludes_stale_articles(db_client, db_session):
    await create_article(db_session, title="Fresh", published_at=datetime.now(UTC))
    await create_article(db_session, title="Stale", published_at=datetime.now(UTC) - timedelta(hours=48))

    response = await db_client.get("/feed/hot")

    assert response.status_code == 200
    titles = [item["title"] for item in response.json()]
    assert "Fresh" in titles
    assert "Stale" not in titles


async def test_personalized_feed_matches_followed_company(db_client, db_session):
    user = await create_user(
        db_session,
        preferences={
            "sectors": [],
            "regions": [],
            "followed_companies": ["Acme"],
            "followed_investors": [],
        },
    )
    company = await create_company(db_session, name="Acme")
    tracked = await create_article(db_session, title="Acme raises", sentiment=ArticleSentiment.BULLISH)
    await link_article_company(db_session, tracked, company)
    await create_article(db_session, title="Unrelated")

    response = await db_client.get("/feed/personalized", headers=auth_header_for(user))

    titles = [item["title"] for item in response.json()["items"]]
    assert titles == ["Acme raises"]
