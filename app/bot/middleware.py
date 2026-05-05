from __future__ import annotations

from aiogram import BaseMiddleware
from loguru import logger

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

                # Store user's language preference for per-user i18n
                data["user_lang"] = db_user.language
            except Exception:
                logger.error("Failed to track user {}", user.id)

        return await handler(event, data)
