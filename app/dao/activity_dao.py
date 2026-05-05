from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from sqlalchemy import select

from app.dao.models import User, UserActivity

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


@dataclass
class ActivityInfo:
    """Dataclass for activity information to log."""

    activity_type: str
    command: str | None = None
    callback_data: str | None = None
    text_preview: str | None = None


class ActivityDAO:
    @staticmethod
    async def log_activity(
        session: AsyncSession,
        user_id: str,
        info: ActivityInfo,
    ) -> UserActivity:
        activity = UserActivity(
            user_id=user_id,
            activity_type=info.activity_type,
            command=info.command,
            callback_data=info.callback_data,
            text_preview=info.text_preview,
        )
        session.add(activity)
        await session.commit()
        return activity

    @staticmethod
    async def get_user_by_telegram_id(
        session: AsyncSession,
        telegram_id: int,
    ) -> User | None:
        query = select(User).where(User.telegram_id == telegram_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()
