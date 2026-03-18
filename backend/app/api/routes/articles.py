from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db_session
from app.models.article import Article
from app.models.social import Bookmark, FounderReaction
from app.models.user import User
from app.schemas.articles import (
    ArticleDetailResponse,
    BookmarkResponse,
    ReactionRequest,
    ReactionResponse,
    ShareCardResponse,
)
from app.services.share_cards import ShareCardService
from app.services.serializers import get_article_company_names, serialize_article_detail

router = APIRouter(prefix="/articles", tags=["articles"])


async def _get_article_or_404(session: AsyncSession, article_id: int) -> Article:
    result = await session.execute(select(Article).where(Article.id == article_id))
    article = result.scalar_one_or_none()
    if article is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
    return article


@router.get("/{article_id}", response_model=ArticleDetailResponse)
async def get_article(article_id: int, session: AsyncSession = Depends(get_db_session)) -> ArticleDetailResponse:
    article = await _get_article_or_404(session, article_id)
    company_map = await get_article_company_names(session, [article.id])
    return serialize_article_detail(article, company_map.get(article.id, []))


@router.get("/{article_id}/share-card", response_model=ShareCardResponse)
async def share_card(article_id: int, session: AsyncSession = Depends(get_db_session)) -> ShareCardResponse:
    article = await _get_article_or_404(session, article_id)
    return ShareCardResponse(
        article_id=article.id,
        title=article.title,
        summary_60w=article.summary_60w,
        source_name=article.source_name,
        sentiment=article.sentiment.value,
        vertical=article.vertical.value,
        image_url=article.image_url,
        download_url=f"/articles/{article.id}/share-card/image",
    )


@router.get("/{article_id}/share-card/image")
async def share_card_image(article_id: int, session: AsyncSession = Depends(get_db_session)) -> FileResponse:
    article = await _get_article_or_404(session, article_id)
    card_path = ShareCardService().generate_card(article)
    return FileResponse(card_path, media_type="image/png", filename=f"briefbiz-{article.id}.png")


@router.post("/{article_id}/bookmark", response_model=BookmarkResponse)
async def create_bookmark(
    article_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> BookmarkResponse:
    await _get_article_or_404(session, article_id)
    existing = await session.execute(
        select(Bookmark).where(Bookmark.user_id == current_user.id, Bookmark.article_id == article_id)
    )
    bookmark = existing.scalar_one_or_none()
    if bookmark is None:
        session.add(Bookmark(user_id=current_user.id, article_id=article_id))
        await session.commit()
    return BookmarkResponse(article_id=article_id, bookmarked=True)


@router.delete("/{article_id}/bookmark", response_model=BookmarkResponse)
async def delete_bookmark(
    article_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> BookmarkResponse:
    await session.execute(
        delete(Bookmark).where(Bookmark.user_id == current_user.id, Bookmark.article_id == article_id)
    )
    await session.commit()
    return BookmarkResponse(article_id=article_id, bookmarked=False)


@router.post("/{article_id}/reaction", response_model=ReactionResponse, status_code=status.HTTP_201_CREATED)
async def create_reaction(
    article_id: int,
    payload: ReactionRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> ReactionResponse:
    await _get_article_or_404(session, article_id)
    if len(payload.reaction_text) > 100:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Reaction too long")

    reaction = FounderReaction(
        article_id=article_id,
        user_id=current_user.id,
        reaction_text=payload.reaction_text,
    )
    session.add(reaction)
    await session.commit()
    await session.refresh(reaction)
    return ReactionResponse(
        id=reaction.id,
        article_id=reaction.article_id,
        user_id=reaction.user_id,
        reaction_text=reaction.reaction_text,
        created_at=reaction.created_at,
    )
