from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import select

from app.dao.models import Emotion

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class EmotionDAO:
    @staticmethod
    async def get_all_active(session: AsyncSession) -> list[Emotion]:
        """Get all active emotions ordered by name."""
        query = (
            select(Emotion)
            .where(Emotion.is_active.is_(True))
            .order_by(Emotion.name)
        )
        result = await session.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_by_ids(
        session: AsyncSession,
        emotion_ids: list[str],
    ) -> list[Emotion]:
        """Get emotions by a list of IDs."""
        query = select(Emotion).where(Emotion.id.in_(emotion_ids))
        result = await session.execute(query)
        return list(result.scalars().all())
