from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db_session
from app.models.article import ArticleSentiment, ArticleVertical
from app.models.user import User
from app.schemas.articles import ArticleCardResponse
from app.schemas.feed import FeedResponse
from app.services.feed_service import FeedService

router = APIRouter(prefix="/feed", tags=["feed"])


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
    return await FeedService(session).latest(
        vertical=vertical,
        region=region,
        sentiment=sentiment,
        sort=sort,
        page=page,
        page_size=page_size,
    )


@router.get("/personalized", response_model=FeedResponse)
async def personalized_feed(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> FeedResponse:
    return await FeedService(session).personalized(current_user, page=page, page_size=page_size)


@router.get("/funding-radar", response_model=FeedResponse)
async def funding_radar(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
) -> FeedResponse:
    return await FeedService(session).funding_radar(page=page, page_size=page_size)


@router.get("/hot", response_model=list[ArticleCardResponse])
async def hot_feed(session: AsyncSession = Depends(get_db_session)) -> list[ArticleCardResponse]:
    return await FeedService(session).hot()
