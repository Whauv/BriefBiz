from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any

from sqlalchemy import DateTime, Enum as SAEnum, Float, Index, String, Text, func, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.company import ArticleCompany
    from app.models.notification import Notification
    from app.models.social import Bookmark, FounderReaction


class ArticleSentiment(str, Enum):
    BULLISH = "bullish"
    BEARISH = "bearish"
    RISK = "risk"
    NEUTRAL = "neutral"


class ArticleVertical(str, Enum):
    FUNDING = "funding"
    FOUNDER_STORIES = "founder_stories"
    LAYOFFS = "layoffs"
    REGULATORY = "regulatory"
    EMERGING_MARKETS = "emerging_markets"
    GENERAL = "general"


class Article(Base):
    __tablename__ = "articles"
    __table_args__ = (
        Index("ix_articles_published_at", "published_at"),
        Index("ix_articles_region", "region"),
        Index("ix_articles_sentiment", "sentiment"),
        Index("ix_articles_vertical", "vertical"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(500))
    url: Mapped[str] = mapped_column(Text())
    url_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    source_name: Mapped[str] = mapped_column(String(255))
    source_quality_score: Mapped[float] = mapped_column(Float, default=0.0, server_default=text("0.0"))
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    raw_content: Mapped[str | None] = mapped_column(Text())
    summary_60w: Mapped[str | None] = mapped_column(Text())
    deep_dive: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        default=lambda: {
            "what_happened": "",
            "key_players": [],
            "market_impact": "",
            "whats_next": "",
        },
        server_default=text(
            """'{"what_happened": "", "key_players": [], "market_impact": "", "whats_next": ""}'::jsonb"""
        ),
    )
    sentiment: Mapped[ArticleSentiment] = mapped_column(
        SAEnum(ArticleSentiment, name="article_sentiment"),
        default=ArticleSentiment.NEUTRAL,
        server_default=ArticleSentiment.NEUTRAL.value,
    )
    impact_score: Mapped[float] = mapped_column(Float, default=0.0, server_default=text("0.0"))
    vertical: Mapped[ArticleVertical] = mapped_column(
        SAEnum(ArticleVertical, name="article_vertical"),
        default=ArticleVertical.GENERAL,
        server_default=ArticleVertical.GENERAL.value,
    )
    region: Mapped[str | None] = mapped_column(String(128))
    image_url: Mapped[str | None] = mapped_column(Text())
    audio_url: Mapped[str | None] = mapped_column(Text())
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=func.now,
    )

    companies: Mapped[list["ArticleCompany"]] = relationship(back_populates="article", cascade="all, delete-orphan")
    bookmarks: Mapped[list["Bookmark"]] = relationship(back_populates="article", cascade="all, delete-orphan")
    founder_reactions: Mapped[list["FounderReaction"]] = relationship(
        back_populates="article",
        cascade="all, delete-orphan",
    )
    notifications: Mapped[list["Notification"]] = relationship(
        back_populates="article",
        cascade="all, delete-orphan",
    )
