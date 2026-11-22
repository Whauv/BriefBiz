from __future__ import annotations

from sqlalchemy import select

from app.models.social import Bookmark, FounderReaction
from tests.factories import (
    auth_header_for,
    create_article,
    create_company,
    create_user,
    link_article_company,
)


async def test_article_detail_returns_deep_dive_and_companies(db_client, db_session):
    company = await create_company(db_session, name="Acme")
    article = await create_article(
        db_session,
        title="M&A heats up",
        deep_dive={"what_happened": "A deal happened", "key_players": ["Acme"], "market_impact": "", "whats_next": ""},
    )
    await link_article_company(db_session, article, company)

    response = await db_client.get(f"/articles/{article.id}")

    assert response.status_code == 200
    payload = response.json()
    assert payload["deep_dive"]["key_players"] == ["Acme"]
    assert payload["companies"] == ["Acme"]
    assert payload["raw_content"] == article.raw_content


async def test_article_detail_missing_returns_404(db_client):
    response = await db_client.get("/articles/999999")
    assert response.status_code == 404


async def test_share_card_returns_metadata(db_client, db_session):
    article = await create_article(db_session, title="Shareable")
    response = await db_client.get(f"/articles/{article.id}/share-card")
    assert response.status_code == 200
    payload = response.json()
    assert payload["article_id"] == article.id
    assert payload["download_url"].endswith(f"/articles/{article.id}/share-card/image")


async def test_create_bookmark_is_idempotent(db_client, db_session):
    user = await create_user(db_session)
    article = await create_article(db_session)
    headers = auth_header_for(user)

    first = await db_client.post(f"/articles/{article.id}/bookmark", headers=headers)
    second = await db_client.post(f"/articles/{article.id}/bookmark", headers=headers)

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["bookmarked"] is True

    rows = (
        await db_session.execute(
            select(Bookmark).where(Bookmark.user_id == user.id, Bookmark.article_id == article.id)
        )
    ).scalars().all()
    assert len(rows) == 1


async def test_delete_bookmark_removes_row(db_client, db_session):
    user = await create_user(db_session)
    article = await create_article(db_session)
    headers = auth_header_for(user)

    await db_client.post(f"/articles/{article.id}/bookmark", headers=headers)
    response = await db_client.delete(f"/articles/{article.id}/bookmark", headers=headers)

    assert response.status_code == 200
    assert response.json()["bookmarked"] is False
    remaining = (await db_session.execute(select(Bookmark).where(Bookmark.user_id == user.id))).scalars().all()
    assert remaining == []


async def test_bookmark_requires_authentication(db_client, db_session):
    article = await create_article(db_session)
    response = await db_client.post(f"/articles/{article.id}/bookmark")
    assert response.status_code == 401


async def test_create_reaction_persists(db_client, db_session):
    user = await create_user(db_session)
    article = await create_article(db_session)

    response = await db_client.post(
        f"/articles/{article.id}/reaction",
        headers=auth_header_for(user),
        json={"reaction_text": "  Big if true  "},
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["reaction_text"] == "Big if true"  # trimmed by the service
    stored = (await db_session.execute(select(FounderReaction).where(FounderReaction.user_id == user.id))).scalar_one()
    assert stored.reaction_text == "Big if true"
