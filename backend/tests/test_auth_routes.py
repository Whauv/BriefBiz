from __future__ import annotations

from sqlalchemy import select

from app.models.user import User
from app.services.auth import decode_access_token
from tests.factories import auth_header_for, create_user


async def test_register_returns_token(db_client):
    response = await db_client.post(
        "/auth/register",
        json={"email": "founder@example.com", "password": "supersecure", "name": "Founder"},
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["token_type"] == "bearer"
    assert payload["user"]["email"] == "founder@example.com"
    token_payload = decode_access_token(payload["access_token"])
    assert token_payload["aud"] == "briefbiz-clients"
    assert token_payload["iss"] == "briefbiz-api"


async def test_register_normalizes_email_and_name(db_client, db_session):
    response = await db_client.post(
        "/auth/register",
        json={"email": " Founder@Example.com ", "password": "supersecure", "name": "  Jane   Founder  "},
    )

    assert response.status_code == 201
    user = (await db_session.execute(select(User))).scalar_one()
    assert user.email == "founder@example.com"
    assert user.name == "Jane Founder"


async def test_register_duplicate_email_conflicts(db_client, db_session):
    await create_user(db_session, email="dupe@example.com")
    response = await db_client.post(
        "/auth/register",
        json={"email": "dupe@example.com", "password": "supersecure", "name": "Someone"},
    )
    assert response.status_code == 409


async def test_login_succeeds_with_correct_password(db_client, db_session):
    await create_user(db_session, email="login@example.com", password="supersecure")
    response = await db_client.post(
        "/auth/login",
        json={"email": "login@example.com", "password": "supersecure"},
    )
    assert response.status_code == 200
    assert response.json()["user"]["email"] == "login@example.com"


async def test_login_rejects_wrong_password(db_client, db_session):
    await create_user(db_session, email="login@example.com", password="supersecure")
    response = await db_client.post(
        "/auth/login",
        json={"email": "login@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401


async def test_login_rejects_unknown_user(db_client):
    response = await db_client.post(
        "/auth/login",
        json={"email": "ghost@example.com", "password": "supersecure"},
    )
    assert response.status_code == 401


async def test_me_returns_current_user(db_client, db_session):
    user = await create_user(db_session, email="me@example.com")
    response = await db_client.get("/auth/me", headers=auth_header_for(user))
    assert response.status_code == 200
    assert response.json()["email"] == "me@example.com"


async def test_me_requires_authentication(db_client):
    response = await db_client.get("/auth/me")
    assert response.status_code == 401


async def test_update_preferences_merges_and_normalizes(db_client, db_session):
    user = await create_user(db_session)
    response = await db_client.patch(
        "/auth/preferences",
        headers=auth_header_for(user),
        json={"regions": ["  US  ", "us", "Europe"], "followed_companies": ["Acme"]},
    )

    assert response.status_code == 200
    prefs = response.json()["preferences"]
    # Deduped (case-insensitive) and trimmed by the request schema.
    assert prefs["regions"] == ["US", "Europe"]
    assert prefs["followed_companies"] == ["Acme"]
    # Untouched keys are preserved.
    assert prefs["sectors"] == []
