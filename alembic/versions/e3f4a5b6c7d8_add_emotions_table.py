"""add emotions table

Revision ID: e3f4a5b6c7d8
Revises: c11d1b10da0e
Create Date: 2026-05-01 20:38:00.000000

"""

import uuid
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.sql import column, table

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e3f4a5b6c7d8"
down_revision: str | Sequence[str] | None = "c11d1b10da0e"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# fmt: off
# (slug, sort_order) — sort_order defines logical grouping:
#   10-110: Fear/Anxiety
#   120-200: Anger/Disgust
#   210-380: Positive/Empowered
#   410-500: Sadness/Shame
#   510-540: Stress/Fatigue
#   610-650: Surprise/Confusion
#   710-870: Gratitude/Contentment
SEED_EMOTIONS: list[tuple[str, int]] = [
    # Group 1: Fear/Anxiety
    ("pressured", 10),
    ("scared", 20),
    ("defensive", 30),
    ("worried", 40),
    ("worthless", 50),
    ("stupid", 60),
    ("disrespected", 70),
    ("excluded", 80),
    ("threatened", 90),
    ("nervous", 100),
    ("misunderstood", 110),
    # Group 2: Anger/Disgust
    ("angry", 120),
    ("let_down", 130),
    ("humiliated", 140),
    ("betrayed", 150),
    ("jealous", 160),
    ("frustrated", 170),
    ("annoyed", 180),
    ("disgust", 190),
    ("contempt", 200),
    # Group 3: Positive/Empowered
    ("curious", 210),
    ("confident", 220),
    ("courageous", 230),
    ("loving", 240),
    ("inspired", 250),
    ("brave", 260),
    ("joy", 270),
    ("smart", 280),
    ("powerful", 290),
    ("wanted", 300),
    ("excited", 310),
    ("romantic", 320),
    ("creative", 330),
    ("thoughtful", 340),
    ("amazed", 350),
    ("generous", 360),
    ("accepting", 370),
    ("relieved", 380),
    # Group 4: Sadness/Shame
    ("lonely", 410),
    ("abandoned", 420),
    ("unimportant", 430),
    ("hopeless", 440),
    ("guilty", 450),
    ("ashamed", 460),
    ("disappointed", 470),
    ("embarrassed", 480),
    ("ugly", 490),
    ("small", 500),
    # Group 5: Stress/Fatigue
    ("bored", 510),
    ("stressed", 520),
    ("tired", 530),
    ("overwhelmed", 540),
    # Group 6: Surprise/Confusion
    ("surprised", 610),
    ("confused", 620),
    ("bullied", 630),
    ("down", 640),
    ("unloved", 650),
    # Group 7: Gratitude/Contentment
    ("proud", 710),
    ("respected", 720),
    ("peaceful", 730),
    ("optimistic", 740),
    ("playful", 750),
    ("thankful", 760),
    ("daring", 770),
    ("appreciated", 780),
    ("satisfied", 790),
    ("honored", 800),
    ("amused", 810),
    ("helpful", 820),
    ("anticipating", 830),
    ("moved", 840),
    ("respectful", 850),
    ("content", 860),
    ("popular", 870),
]
# fmt: on


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "emotions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
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
        sa.UniqueConstraint("slug"),
    )

    emotions_table = table(
        "emotions",
        column("id", sa.Uuid()),
        column("slug", sa.String()),
        column("sort_order", sa.Integer()),
    )

    op.bulk_insert(
        emotions_table,
        [
            {
                "id": uuid.uuid4(),
                "slug": slug,
                "sort_order": sort_order,
            }
            for slug, sort_order in SEED_EMOTIONS
        ],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("emotions")
