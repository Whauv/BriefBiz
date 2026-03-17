from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, func, text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.article import Article


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True)
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    sector: Mapped[str | None] = mapped_column(String(128))
    hq_country: Mapped[str | None] = mapped_column(String(128))
    funding_stage: Mapped[str | None] = mapped_column(String(64))
    investors: Mapped[list[str]] = mapped_column(
        ARRAY(String(255)),
        default=list,
        server_default=text("'{}'"),
    )
    article_count: Mapped[int] = mapped_column(Integer, default=0, server_default=text("0"))
    last_headline: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=func.now,
    )

    articles: Mapped[list["ArticleCompany"]] = relationship(back_populates="company", cascade="all, delete-orphan")


class ArticleCompany(Base):
    __tablename__ = "article_companies"

    article_id: Mapped[int] = mapped_column(ForeignKey("articles.id", ondelete="CASCADE"), primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), primary_key=True)

    article: Mapped["Article"] = relationship(back_populates="companies")
    company: Mapped["Company"] = relationship(back_populates="articles")
