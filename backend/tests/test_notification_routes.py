from __future__ import annotations

from sqlalchemy import select

from app.models.notification import Notification
from tests.factories import auth_header_for, create_article, create_notification, create_user


async def test_list_notifications_orders_unread_first(db_client, db_session):
    user = await create_user(db_session)
    article = await create_article(db_session)
    await create_notification(db_session, user=user, article=article, read=True)
    await create_notification(db_session, user=user, article=article, read=False)

    response = await db_client.get("/notifications", headers=auth_header_for(user))

    assert response.status_code == 200
    rows = response.json()
    assert len(rows) == 2
    assert rows[0]["read"] is False  # unread sorts ahead of read


async def test_list_notifications_requires_auth(db_client):
    response = await db_client.get("/notifications")
    assert response.status_code == 401


async def test_mark_read_all(db_client, db_session):
    user = await create_user(db_session)
    article = await create_article(db_session)
    await create_notification(db_session, user=user, article=article, read=False)
    await create_notification(db_session, user=user, article=article, read=False)

    response = await db_client.post("/notifications/mark-read", headers=auth_header_for(user), json={})

    assert response.status_code == 200
    assert response.json()["updated"] == 2
    unread = (
        await db_session.execute(
            select(Notification).where(Notification.user_id == user.id, Notification.read.is_(False))
        )
    ).scalars().all()
    assert unread == []


async def test_mark_read_specific_ids(db_client, db_session):
    user = await create_user(db_session)
    article = await create_article(db_session)
    target = await create_notification(db_session, user=user, article=article, read=False)
    other = await create_notification(db_session, user=user, article=article, read=False)

    response = await db_client.post(
        "/notifications/mark-read",
        headers=auth_header_for(user),
        json={"notification_ids": [target.id]},
    )

    assert response.status_code == 200
    assert response.json()["updated"] == 1
    await db_session.refresh(other)
    assert other.read is False
