from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from app.db.session import get_db_session
from app.main import app
from app.models.user import User
from app.services.auth import decode_access_token


@pytest.mark.asyncio
async def test_auth_register_returns_token(client, execute_result):
    session = AsyncMock()
    session.execute.side_effect = [execute_result(scalar_one_or_none=None)]

    async def refresh_side_effect(user: User):
        user.id = 1
        user.created_at = datetime.now(UTC)
        user.preferences = {"sectors": [], "regions": [], "followed_companies": [], "followed_investors": []}

    session.refresh.side_effect = refresh_side_effect

    async def override_db():
        yield session

    app.dependency_overrides[get_db_session] = override_db

    response = await client.post(
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


@pytest.mark.asyncio
async def test_auth_register_normalizes_email_and_name(client, execute_result):
    session = AsyncMock()
    session.execute.side_effect = [execute_result(scalar_one_or_none=None)]

    async def refresh_side_effect(user: User):
        user.id = 2
        user.created_at = datetime.now(UTC)
        user.preferences = {"sectors": [], "regions": [], "followed_companies": [], "followed_investors": []}

    session.refresh.side_effect = refresh_side_effect

    async def override_db():
        yield session

    app.dependency_overrides[get_db_session] = override_db

    response = await client.post(
        "/auth/register",
        json={"email": " Founder@Example.com ", "password": "supersecure", "name": "  Jane   Founder  "},
    )

    assert response.status_code == 201
    created_user = session.add.call_args.args[0]
    assert created_user.email == "founder@example.com"
    assert created_user.name == "Jane Founder"
