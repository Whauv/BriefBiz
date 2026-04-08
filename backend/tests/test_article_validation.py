from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from app.api.deps import get_current_user
from app.db.session import get_db_session
from app.main import app
from app.models.user import User


@pytest.mark.asyncio
async def test_article_reaction_validation_rejects_long_payload(client):
    session = AsyncMock()
    current_user = User(id=1, email="u@example.com", password_hash="x", name="User", preferences={})

    async def override_db():
        yield session

    async def override_user():
        return current_user

    app.dependency_overrides[get_db_session] = override_db
    app.dependency_overrides[get_current_user] = override_user

    response = await client.post("/articles/1/reaction", json={"reaction_text": "x" * 101})

    assert response.status_code == 422
