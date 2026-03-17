"""add why it matters to articles

Revision ID: 20260317_0002
Revises: 20260317_0001
Create Date: 2026-03-17 13:05:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "20260317_0002"
down_revision = "20260317_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("articles", sa.Column("why_it_matters", sa.String(length=120), nullable=True))


def downgrade() -> None:
    op.drop_column("articles", "why_it_matters")

