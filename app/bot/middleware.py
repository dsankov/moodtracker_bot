from __future__ import annotations

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message
from loguru import logger

from app.dao.activity_dao import ActivityDAO, ActivityInfo
from app.dao.database import get_db_session
from app.dao.user_dao import UserDAO


class UserTrackingMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        user = event.from_user
        if not user:
            return await handler(event, data)

        async with get_db_session() as session:
            try:
                db_user = await UserDAO.upsert_user(
                    session=session,
                    telegram_id=user.id,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    username=user.username,
                )

                info = self._extract_activity_info(event)
                await ActivityDAO.log_activity(
                    session=session,
                    user_id=str(db_user.id),
                    info=info,
                )
            except Exception:
                logger.error("Failed to track user {}", user.id)

        return await handler(event, data)

    @staticmethod
    def _extract_activity_info(event) -> ActivityInfo:
        if isinstance(event, Message):
            text = event.text or ""
            if text.startswith("/"):
                command = text.split()[0].lstrip("/").split("@")[0]
                return ActivityInfo(activity_type="command", command=command)
            return ActivityInfo(
                activity_type="message",
                text_preview=text[:255] if text else None,
            )
        if isinstance(event, CallbackQuery):
            return ActivityInfo(activity_type="callback", callback_data=event.data)
        return ActivityInfo(activity_type="unknown")
