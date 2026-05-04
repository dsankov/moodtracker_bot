"""add emotions table

Revision ID: e3f4a5b6c7d8
Revises: bd1dfb4bec88
Create Date: 2026-05-01 20:38:00.000000

"""
import uuid
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.sql import column, table

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e3f4a5b6c7d8"
down_revision: str | Sequence[str] | None = "bd1dfb4bec88"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


SEED_EMOTIONS = [
    "спокойствие",
    "радость",
    "тревога",
    "грусть",
    "злость",
    "усталость",
    "бодрость",
    "вдохновение",
    "скука",
    "нежность",
    "уверенность",
    "растерянность",
    "благодарность",
    "раздражение",
    "воодушевление",
    "апатия",
    "интерес",
    "страх",
    "гордость",
    "одиночество",
]


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "emotions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    emotions_table = table(
        "emotions",
        column("id", sa.Uuid()),
        column("name", sa.String()),
        column("is_active", sa.Boolean()),
    )

    op.bulk_insert(
        emotions_table,
        [
            {"id": uuid.uuid4(), "name": name, "is_active": True}
            for name in SEED_EMOTIONS
        ],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("emotions")
