from __future__ import annotations

from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy import desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db_session
from app.models.article import Article, ArticleSentiment, ArticleVertical
from app.models.company import ArticleCompany, Company
from app.schemas.articles import ArticleCardResponse
from app.models.user import User
from app.schemas.feed import FeedResponse
from app.services.serializers import get_article_company_names, serialize_article_card

router = APIRouter(prefix="/feed", tags=["feed"])


async def _build_feed_response(
    session: AsyncSession,
    query,
    *,
    page: int,
    page_size: int,
) -> FeedResponse:
    total = (await session.execute(select(func.count()).select_from(query.subquery()))).scalar_one()
    paginated = query.offset((page - 1) * page_size).limit(page_size)
    articles = list((await session.execute(paginated)).scalars().unique().all())
    company_map = await get_article_company_names(session, [article.id for article in articles])
    return FeedResponse(
        page=page,
        page_size=page_size,
        total=total,
        items=[serialize_article_card(article, company_map.get(article.id, [])) for article in articles],
    )


@router.get("", response_model=FeedResponse)
async def feed(
    vertical: ArticleVertical | None = None,
    region: str | None = None,
    sentiment: ArticleSentiment | None = None,
    sort: str = Query(default="latest", pattern="^(latest|impact)$"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
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
    return await _build_feed_response(session, query, page=page, page_size=page_size)


@router.get("/personalized", response_model=FeedResponse)
async def personalized_feed(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> FeedResponse:
    preferences = current_user.preferences or {}
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
    return await _build_feed_response(session, query, page=page, page_size=page_size)


@router.get("/funding-radar", response_model=FeedResponse)
async def funding_radar(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
) -> FeedResponse:
    query = (
        select(Article)
        .where(Article.vertical == ArticleVertical.FUNDING)
        .order_by(desc(Article.impact_score), desc(Article.published_at))
    )
    return await _build_feed_response(session, query, page=page, page_size=page_size)


@router.get("/hot", response_model=list[ArticleCardResponse])
async def hot_feed(session: AsyncSession = Depends(get_db_session)):
    cutoff = datetime.now(UTC) - timedelta(hours=24)
    query = (
        select(Article)
        .where(Article.published_at >= cutoff)
        .order_by(desc(Article.impact_score), desc(Article.published_at))
        .limit(20)
    )
    articles = list((await session.execute(query)).scalars().unique().all())
    company_map = await get_article_company_names(session, [article.id for article in articles])
    return [serialize_article_card(article, company_map.get(article.id, [])) for article in articles]
