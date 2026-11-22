from __future__ import annotations

from app.services.feed_service import FeedService
from tests.factories import create_article, create_user


async def test_personalized_with_no_preferences_returns_everything(db_session):
    user = await create_user(
        db_session,
        preferences={"sectors": [], "regions": [], "followed_companies": [], "followed_investors": []},
    )
    await create_article(db_session, title="One", region="US")
    await create_article(db_session, title="Two", region="Europe")

    result = await FeedService(db_session).personalized(user)

    assert result.total == 2


async def test_latest_region_filter(db_session):
    await create_article(db_session, title="US story", region="US")
    await create_article(db_session, title="EU story", region="Europe")

    result = await FeedService(db_session).latest(region="US")

    assert result.total == 1
    assert result.items[0].title == "US story"
