from __future__ import annotations

from tests.factories import auth_header_for, create_article, create_user


async def test_reaction_rejects_empty_text(db_client, db_session):
    user = await create_user(db_session)
    article = await create_article(db_session)

    response = await db_client.post(
        f"/articles/{article.id}/reaction",
        headers=auth_header_for(user),
        json={"reaction_text": ""},
    )

    assert response.status_code == 422


async def test_reaction_rejects_overlong_text(db_client, db_session):
    user = await create_user(db_session)
    article = await create_article(db_session)

    response = await db_client.post(
        f"/articles/{article.id}/reaction",
        headers=auth_header_for(user),
        json={"reaction_text": "x" * 101},
    )

    assert response.status_code == 422
