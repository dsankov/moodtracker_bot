import contextlib

from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const, Format

from app.bot.i18n import LANG_NAMES, t
from app.bot.lang_utils import get_user_lang
from app.dao.database import get_db_session
from app.dao.user_dao import UserDAO


class LanguageSG(StatesGroup):
    select = State()


async def language_getter(
    dialog_manager: DialogManager,
    **_kwargs,
) -> dict:
    """Getter for the language selection window."""
    lang = await get_user_lang(dialog_manager)
    return {
        "language_select": t("language.select", lang=lang),
        "language_current": t(
            "language.current",
            lang=lang,
            lang_name=LANG_NAMES.get(lang, lang),
        ),
    }


async def _apply_language(
    callback: CallbackQuery,
    dialog_manager: DialogManager,
    language: str,
) -> None:
    """Persist language choice and close dialog."""
    user = callback.from_user
    start_data = dialog_manager.start_data
    # Check for parent dialog BEFORE done() pops the stack
    has_parent = len(dialog_manager.current_stack().intents) > 1

    async with get_db_session() as session:
        await UserDAO.update_language(
            session=session,
            telegram_id=user.id,
            language=language,
        )
    await dialog_manager.done()

    # Delete the user's original /language command message
    cmd_msg_id: int | None = (
        start_data.get("cmd_msg_id") if isinstance(start_data, dict) else None
    )
    if cmd_msg_id and callback.message:
        with contextlib.suppress(Exception):
            await callback.bot.delete_message(
                chat_id=callback.message.chat.id,
                message_id=cmd_msg_id,
            )

    # Remove the dialog message only when no parent dialog
    # (parent dialog needs the message to re-render on)
    if not has_parent and isinstance(callback.message, Message):
        with contextlib.suppress(Exception):
            await callback.message.delete()


async def on_russian_selected(
    callback: CallbackQuery,
    _button: Button,
    dialog_manager: DialogManager,
) -> None:
    """Set language to Russian."""
    await _apply_language(callback, dialog_manager, language="ru")


async def on_english_selected(
    callback: CallbackQuery,
    _button: Button,
    dialog_manager: DialogManager,
) -> None:
    """Set language to English."""
    await _apply_language(callback, dialog_manager, language="en")


language_dialog = Dialog(
    Window(
        Format("{language_select}"),
        Format("{language_current}"),
        Button(
            Const("Русский"),
            id="lang_ru_btn",
            on_click=on_russian_selected,
        ),
        Button(
            Const("English"),
            id="lang_en_btn",
            on_click=on_english_selected,
        ),
        state=LanguageSG.select,
        getter=language_getter,
    ),
)
