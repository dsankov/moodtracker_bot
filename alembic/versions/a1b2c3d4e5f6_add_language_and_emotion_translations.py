"""add language column to users and name_en to emotions

Revision ID: a1b2c3d4e5f6
Revises: e3f4a5b6c7d8
Create Date: 2026-05-04 14:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: str | Sequence[str] | None = "e3f4a5b6c7d8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# Mapping: Russian name → English translation
EMOTION_TRANSLATIONS = {
    "спокойствие": "calm",
    "радость": "joy",
    "тревога": "anxiety",
    "грусть": "sadness",
    "злость": "anger",
    "усталость": "tiredness",
    "бодрость": "energy",
    "вдохновение": "inspiration",
    "скука": "boredom",
    "нежность": "tenderness",
    "уверенность": "confidence",
    "растерянность": "confusion",
    "благодарность": "gratitude",
    "раздражение": "irritation",
    "воодушевление": "enthusiasm",
    "апатия": "apathy",
    "интерес": "interest",
    "страх": "fear",
    "гордость": "pride",
    "одиночество": "loneliness",
}


def upgrade() -> None:
    """Upgrade schema."""
    # Add language column to users table
    op.add_column(
        "users",
        sa.Column(
            "language",
            sa.String(length=5),
            server_default="en",
            nullable=False,
        ),
    )

    # Add name_en column to emotions table
    op.add_column(
        "emotions",
        sa.Column("name_en", sa.String(length=100), nullable=True),
    )

    # Update existing emotion rows with English translations
    for ru_name, en_name in EMOTION_TRANSLATIONS.items():
        stmt = sa.text(
            "UPDATE emotions SET name_en = :en_name WHERE name = :ru_name"
        ).bindparams(en_name=en_name, ru_name=ru_name)
        op.execute(stmt)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("emotions", "name_en")
    op.drop_column("users", "language")
