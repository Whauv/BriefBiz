from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy import Select, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.article import Article, ArticleSentiment, ArticleVertical
from app.models.company import ArticleCompany, Company
from app.models.user import User
from app.schemas.articles import ArticleCardResponse
from app.schemas.feed import FeedResponse
from app.services.serializers import serialize_article_cards

HOT_FEED_WINDOW = timedelta(hours=24)
HOT_FEED_LIMIT = 20


class FeedService:
    """Builds the various feed queries and paginated responses.

    Query construction and serialization used to live inline in the feed route
    handlers; centralizing it here keeps the routes thin and makes the feed logic
    testable without the ASGI client.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def _paginate(self, query: Select[tuple[Article]], *, page: int, page_size: int) -> FeedResponse:
        total = (
            await self.session.execute(select(func.count()).select_from(query.subquery()))
        ).scalar_one()
        paginated = query.offset((page - 1) * page_size).limit(page_size)
        articles = list((await self.session.execute(paginated)).scalars().unique().all())
        items = await serialize_article_cards(self.session, articles)
        return FeedResponse(page=page, page_size=page_size, total=total, items=items)

    async def latest(
        self,
        *,
        vertical: ArticleVertical | None = None,
        region: str | None = None,
        sentiment: ArticleSentiment | None = None,
        sort: str = "latest",
        page: int = 1,
        page_size: int = 20,
    ) -> FeedResponse:
        query = select(Article)
        if vertical is not None:
            query = query.where(Article.vertical == vertical)
        if region:
            query = query.where(Article.region == region)
        if sentiment is not None:
            query = query.where(Article.sentiment == sentiment)

        if sort == "impact":
            query = query.order_by(desc(Article.impact_score), desc(Article.published_at))
        else:
            query = query.order_by(desc(Article.published_at))
        return await self._paginate(query, page=page, page_size=page_size)

    async def personalized(self, user: User, *, page: int = 1, page_size: int = 20) -> FeedResponse:
        preferences = user.preferences or {}
        regions = preferences.get("regions", [])
        followed_companies = preferences.get("followed_companies", [])

        query = select(Article).distinct()
        filters = []
        if regions:
            filters.append(Article.region.in_(regions))
        if followed_companies:
            query = query.join(ArticleCompany, ArticleCompany.article_id == Article.id).join(
                Company, Company.id == ArticleCompany.company_id
            )
            filters.append(Company.name.in_(followed_companies))
        if filters:
            query = query.where(or_(*filters))
        query = query.order_by(desc(Article.impact_score), desc(Article.published_at))
        return await self._paginate(query, page=page, page_size=page_size)

    async def funding_radar(self, *, page: int = 1, page_size: int = 20) -> FeedResponse:
        query = (
            select(Article)
            .where(Article.vertical == ArticleVertical.FUNDING)
            .order_by(desc(Article.impact_score), desc(Article.published_at))
        )
        return await self._paginate(query, page=page, page_size=page_size)

    async def hot(self) -> list[ArticleCardResponse]:
        cutoff = datetime.now(UTC) - HOT_FEED_WINDOW
        query = (
            select(Article)
            .where(Article.published_at >= cutoff)
            .order_by(desc(Article.impact_score), desc(Article.published_at))
            .limit(HOT_FEED_LIMIT)
        )
        articles = list((await self.session.execute(query)).scalars().unique().all())
        return await serialize_article_cards(self.session, articles)
