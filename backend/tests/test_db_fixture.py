"""Smoke tests for the real-database test harness (Phase 0).

These prove the Postgres-backed fixtures and factories work end-to-end:
schema creation, a direct session round-trip, and an ASGI request served from
the same per-test schema. Later phases build their route/service tests on top of
these fixtures.
"""

from __future__ import annotations

from sqlalchemy import select

from app.models.article import Article
from tests.factories import create_article, create_company, create_user, link_article_company


async def test_db_session_round_trip(db_session):
    article = await create_article(db_session, title="Round trip story")

    result = await db_session.execute(select(Article).where(Article.id == article.id))
    fetched = result.scalar_one()

    assert fetched.id == article.id
    assert fetched.title == "Round trip story"
    # Server/Python defaults applied (JSONB column).
    assert fetched.deep_dive == article.deep_dive


async def test_user_factory_hashes_password(db_session):
    user = await create_user(db_session, password="supersecure")

    assert user.id is not None
    assert user.password_hash.startswith("pbkdf2_sha256$")
    assert user.password_hash != "supersecure"


async def test_api_reads_from_test_db(db_client, db_session):
    company = await create_company(db_session, name="Acme Corp")
    article = await create_article(db_session, title="Deal of the year")
    await link_article_company(db_session, article, company)

    response = await db_client.get(f"/articles/{article.id}")

    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == article.id
    assert payload["title"] == "Deal of the year"
    assert payload["companies"] == ["Acme Corp"]
