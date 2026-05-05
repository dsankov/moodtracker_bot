"""Shared language resolution utility.

Reads the user's language preference directly from the database
to ensure the latest committed value is always used.
"""

from aiogram_dialog import DialogManager

from app.dao.activity_dao import ActivityDAO
from app.dao.database import get_db_session


async def get_user_lang(dialog_manager: DialogManager) -> str:
    """Read user's language preference directly from DB.

    Returns the user's language (e.g. 'en', 'ru'),
    or 'en' as fallback.
    """
    user = dialog_manager.event.from_user
    if not user:
        return "en"
    async with get_db_session() as session:
        db_user = await ActivityDAO.get_user_by_telegram_id(
            session=session,
            telegram_id=user.id,
        )
    if db_user:
        return db_user.language
    return "en"
