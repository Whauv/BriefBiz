from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.article import Article
from app.models.social import Bookmark, FounderReaction


class SocialService:
    """Bookmark and founder-reaction writes.

    These were raw ``select``/``add``/``commit`` blocks inside the article route;
    centralizing them keeps the route thin and the write logic reusable/testable.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def _get_article_or_404(self, article_id: int) -> Article:
        result = await self.session.execute(select(Article).where(Article.id == article_id))
        article = result.scalar_one_or_none()
        if article is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
        return article

    async def add_bookmark(self, *, user_id: int, article_id: int) -> None:
        await self._get_article_or_404(article_id)
        existing = await self.session.execute(
            select(Bookmark).where(Bookmark.user_id == user_id, Bookmark.article_id == article_id)
        )
        if existing.scalar_one_or_none() is None:
            self.session.add(Bookmark(user_id=user_id, article_id=article_id))
            await self.session.commit()

    async def remove_bookmark(self, *, user_id: int, article_id: int) -> None:
        await self.session.execute(
            delete(Bookmark).where(Bookmark.user_id == user_id, Bookmark.article_id == article_id)
        )
        await self.session.commit()

    async def add_reaction(self, *, user_id: int, article_id: int, reaction_text: str) -> FounderReaction:
        await self._get_article_or_404(article_id)
        reaction = FounderReaction(
            article_id=article_id,
            user_id=user_id,
            reaction_text=reaction_text.strip(),
        )
        self.session.add(reaction)
        await self.session.commit()
        await self.session.refresh(reaction)
        return reaction
