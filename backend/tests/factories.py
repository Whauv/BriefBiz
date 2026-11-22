"""Async factory helpers for building persisted test data.

These replace the ~30-line inline ``Article(...)`` / ``User(...)`` construction that
was copy-pasted across the route tests. Each factory creates a row, commits it, and
returns the refreshed instance so tests can use server-generated columns (ids,
timestamps, defaults).

All factories take an :class:`~sqlalchemy.ext.asyncio.AsyncSession` as their first
argument and accept keyword overrides for any column.
"""

from __future__ import annotations

from datetime import UTC, datetime
from itertools import count
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.article import Article, ArticleSentiment, ArticleVertical
from app.models.company import ArticleCompany, Company
from app.models.notification import Notification
from app.models.social import Bookmark, FounderReaction
from app.models.user import User
from app.services.auth import create_access_token, hash_password


def auth_header_for(user: User) -> dict[str, str]:
    """Bearer-token header that authenticates requests as ``user``."""
    return {"Authorization": f"Bearer {create_access_token(str(user.id))}"}

# Monotonic counters keep generated unique fields (url_hash, email, slug) distinct
# within a test run without the caller having to supply them.
_article_seq = count(1)
_user_seq = count(1)
_company_seq = count(1)

DEFAULT_DEEP_DIVE: dict[str, Any] = {
    "what_happened": "",
    "key_players": [],
    "market_impact": "",
    "whats_next": "",
}


async def create_article(session: AsyncSession, **overrides: Any) -> Article:
    seq = next(_article_seq)
    defaults: dict[str, Any] = {
        "title": f"Test article {seq}",
        "url": f"https://example.com/article-{seq}",
        "url_hash": f"hash-{seq}",
        "source_name": "Bloomberg",
        "source_quality_score": 0.9,
        "published_at": datetime.now(UTC),
        "raw_content": "Raw content",
        "summary_60w": "A concise sixty-word summary of the story.",
        "deep_dive": dict(DEFAULT_DEEP_DIVE),
        "sentiment": ArticleSentiment.NEUTRAL,
        "impact_score": 0.5,
        "vertical": ArticleVertical.GENERAL,
        "region": "Global",
        "why_it_matters": "It matters.",
    }
    defaults.update(overrides)
    article = Article(**defaults)
    session.add(article)
    await session.commit()
    await session.refresh(article)
    return article


async def create_user(session: AsyncSession, *, password: str = "supersecure", **overrides: Any) -> User:
    seq = next(_user_seq)
    defaults: dict[str, Any] = {
        "email": f"user{seq}@example.com",
        "name": f"User {seq}",
        "password_hash": hash_password(password),
        "preferences": {
            "sectors": [],
            "regions": [],
            "followed_companies": [],
            "followed_investors": [],
        },
    }
    defaults.update(overrides)
    user = User(**defaults)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def create_company(session: AsyncSession, **overrides: Any) -> Company:
    seq = next(_company_seq)
    defaults: dict[str, Any] = {
        "name": f"Company {seq}",
        "slug": f"company-{seq}",
        "sector": "Software",
        "investors": [],
    }
    defaults.update(overrides)
    company = Company(**defaults)
    session.add(company)
    await session.commit()
    await session.refresh(company)
    return company


async def link_article_company(session: AsyncSession, article: Article, company: Company) -> ArticleCompany:
    link = ArticleCompany(article_id=article.id, company_id=company.id)
    session.add(link)
    await session.commit()
    return link


async def create_bookmark(session: AsyncSession, *, user: User, article: Article) -> Bookmark:
    bookmark = Bookmark(user_id=user.id, article_id=article.id)
    session.add(bookmark)
    await session.commit()
    await session.refresh(bookmark)
    return bookmark


async def create_notification(
    session: AsyncSession,
    *,
    user: User,
    article: Article,
    type: str = "new_article",
    read: bool = False,
) -> Notification:
    notification = Notification(user_id=user.id, article_id=article.id, type=type, read=read)
    session.add(notification)
    await session.commit()
    await session.refresh(notification)
    return notification


async def create_reaction(
    session: AsyncSession,
    *,
    user: User,
    article: Article,
    reaction_text: str = "Big if true",
) -> FounderReaction:
    reaction = FounderReaction(user_id=user.id, article_id=article.id, reaction_text=reaction_text)
    session.add(reaction)
    await session.commit()
    await session.refresh(reaction)
    return reaction
