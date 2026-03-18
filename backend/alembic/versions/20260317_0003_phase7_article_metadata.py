"""phase 7 article metadata

Revision ID: 20260317_0003
Revises: 20260317_0002
Create Date: 2026-03-17 18:20:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260317_0003"
down_revision = "20260317_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("articles", sa.Column("topic_cluster", sa.String(length=120), nullable=True))
    op.add_column(
        "articles",
        sa.Column("sources_disagree", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )
    op.add_column(
        "articles",
        sa.Column(
            "conflict_context",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("""'{"related_article_ids": [], "perspectives": []}'::jsonb"""),
        ),
    )
    op.create_index("ix_articles_topic_cluster", "articles", ["topic_cluster"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_articles_topic_cluster", table_name="articles")
    op.drop_column("articles", "conflict_context")
    op.drop_column("articles", "sources_disagree")
    op.drop_column("articles", "topic_cluster")
