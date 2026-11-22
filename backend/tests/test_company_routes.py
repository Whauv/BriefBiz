from __future__ import annotations

from tests.factories import create_article, create_company, link_article_company


async def test_company_profile_returns_related_articles(db_client, db_session):
    company = await create_company(db_session, name="Acme", slug="acme", investors=["SeedCo"])
    article = await create_article(db_session, title="Acme expands")
    await link_article_company(db_session, article, company)

    response = await db_client.get("/companies/acme")

    assert response.status_code == 200
    payload = response.json()
    assert payload["slug"] == "acme"
    assert payload["investors"] == ["SeedCo"]
    assert payload["articles"][0]["title"] == "Acme expands"


async def test_company_profile_missing_returns_404(db_client):
    response = await db_client.get("/companies/does-not-exist")
    assert response.status_code == 404


async def test_trending_companies_rank_by_recent_mentions(db_client, db_session):
    popular = await create_company(db_session, name="Popular", slug="popular")
    quiet = await create_company(db_session, name="Quiet", slug="quiet")

    for index in range(2):
        article = await create_article(db_session, title=f"Popular story {index}")
        await link_article_company(db_session, article, popular)
    quiet_article = await create_article(db_session, title="Quiet story")
    await link_article_company(db_session, quiet_article, quiet)

    response = await db_client.get("/companies/trending")

    assert response.status_code == 200
    rows = response.json()
    slugs = [row["slug"] for row in rows]
    assert slugs[0] == "popular"
    assert {"popular", "quiet"} <= set(slugs)
