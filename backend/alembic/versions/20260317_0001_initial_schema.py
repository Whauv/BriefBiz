"""initial schema

Revision ID: 20260317_0001
Revises:
Create Date: 2026-03-17 12:00:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260317_0001"
down_revision = None
branch_labels = None
depends_on = None

article_sentiment_enum = postgresql.ENUM(
    "bullish",
    "bearish",
    "risk",
    "neutral",
    name="article_sentiment",
)

article_vertical_enum = postgresql.ENUM(
    "funding",
    "founder_stories",
    "layoffs",
    "regulatory",
    "emerging_markets",
    "general",
    name="article_vertical",
)


def upgrade() -> None:
    article_sentiment_enum.create(op.get_bind(), checkfirst=True)
    article_vertical_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column(
            "preferences",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text(
                """'{"sectors": [], "regions": [], "followed_companies": [], "followed_investors": []}'::jsonb"""
            ),
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "articles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("url_hash", sa.String(length=64), nullable=False),
        sa.Column("source_name", sa.String(length=255), nullable=False),
        sa.Column("source_quality_score", sa.Float(), nullable=False, server_default=sa.text("0.0")),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("raw_content", sa.Text(), nullable=True),
        sa.Column("summary_60w", sa.Text(), nullable=True),
        sa.Column(
            "deep_dive",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text(
                """'{"what_happened": "", "key_players": [], "market_impact": "", "whats_next": ""}'::jsonb"""
            ),
        ),
        sa.Column("sentiment", article_sentiment_enum, nullable=False, server_default="neutral"),
        sa.Column("impact_score", sa.Float(), nullable=False, server_default=sa.text("0.0")),
        sa.Column("vertical", article_vertical_enum, nullable=False, server_default="general"),
        sa.Column("region", sa.String(length=128), nullable=True),
        sa.Column("image_url", sa.Text(), nullable=True),
        sa.Column("audio_url", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("url_hash", name="uq_articles_url_hash"),
    )
    op.create_index("ix_articles_published_at", "articles", ["published_at"], unique=False)
    op.create_index("ix_articles_region", "articles", ["region"], unique=False)
    op.create_index("ix_articles_sentiment", "articles", ["sentiment"], unique=False)
    op.create_index("ix_articles_url_hash", "articles", ["url_hash"], unique=True)
    op.create_index("ix_articles_vertical", "articles", ["vertical"], unique=False)

    op.create_table(
        "companies",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=255), nullable=False),
        sa.Column("sector", sa.String(length=128), nullable=True),
        sa.Column("hq_country", sa.String(length=128), nullable=True),
        sa.Column("funding_stage", sa.String(length=64), nullable=True),
        sa.Column(
            "investors",
            postgresql.ARRAY(sa.String(length=255)),
            nullable=False,
            server_default=sa.text("'{}'"),
        ),
        sa.Column("article_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("last_headline", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("name", name="uq_companies_name"),
        sa.UniqueConstraint("slug", name="uq_companies_slug"),
    )
    op.create_index("ix_companies_slug", "companies", ["slug"], unique=True)

    op.create_table(
        "article_companies",
        sa.Column("article_id", sa.Integer(), nullable=False),
        sa.Column("company_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["article_id"], ["articles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("article_id", "company_id"),
    )

    op.create_table(
        "bookmarks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("article_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["article_id"], ["articles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("user_id", "article_id", name="uq_bookmarks_user_article"),
    )
    op.create_index("ix_bookmarks_user_id", "bookmarks", ["user_id"], unique=False)

    op.create_table(
        "founder_reactions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("article_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("reaction_text", sa.String(length=100), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["article_id"], ["articles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_founder_reactions_article_id", "founder_reactions", ["article_id"], unique=False)

    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("article_id", sa.Integer(), nullable=False),
        sa.Column("type", sa.String(length=64), nullable=False),
        sa.Column("read", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["article_id"], ["articles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_notifications_read", "notifications", ["read"], unique=False)
    op.create_index("ix_notifications_user_id", "notifications", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_notifications_user_id", table_name="notifications")
    op.drop_index("ix_notifications_read", table_name="notifications")
    op.drop_table("notifications")

    op.drop_index("ix_founder_reactions_article_id", table_name="founder_reactions")
    op.drop_table("founder_reactions")

    op.drop_index("ix_bookmarks_user_id", table_name="bookmarks")
    op.drop_table("bookmarks")

    op.drop_table("article_companies")

    op.drop_index("ix_companies_slug", table_name="companies")
    op.drop_table("companies")

    op.drop_index("ix_articles_vertical", table_name="articles")
    op.drop_index("ix_articles_url_hash", table_name="articles")
    op.drop_index("ix_articles_sentiment", table_name="articles")
    op.drop_index("ix_articles_region", table_name="articles")
    op.drop_index("ix_articles_published_at", table_name="articles")
    op.drop_table("articles")

    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")

    article_vertical_enum.drop(op.get_bind(), checkfirst=True)
    article_sentiment_enum.drop(op.get_bind(), checkfirst=True)

