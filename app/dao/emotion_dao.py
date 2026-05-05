from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import select

from app.dao.models import Emotion

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class EmotionDAO:
    @staticmethod
    async def get_all(session: AsyncSession) -> list[Emotion]:
        """Get all emotions ordered by sort_order."""
        query = select(Emotion).order_by(Emotion.sort_order)
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
