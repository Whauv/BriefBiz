from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from app.api.deps import get_current_user
from app.db.session import get_db_session
from app.main import app
from app.models.notification import Notification
from app.models.user import User


@pytest.mark.asyncio
async def test_notifications_list_requires_user_and_returns_items(client, execute_result):
    current_user = User(
        id=12,
        email="ops@example.com",
        password_hash="hash",
        name="Ops",
        preferences={"sectors": [], "regions": [], "followed_companies": [], "followed_investors": []},
        created_at=datetime.now(UTC),
    )
    notification = Notification(
        id=4,
        user_id=12,
        article_id=9,
        type="followed_company",
        read=False,
        created_at=datetime.now(UTC),
    )

    session = AsyncMock()
    session.execute.side_effect = [execute_result(scalars=[notification])]

    async def override_db():
        yield session

    async def override_current_user():
        return current_user

    app.dependency_overrides[get_db_session] = override_db
    app.dependency_overrides[get_current_user] = override_current_user
    response = await client.get("/notifications")

    assert response.status_code == 200
    assert response.json()[0]["type"] == "followed_company"
