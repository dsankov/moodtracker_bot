from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery
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


async def on_russian_selected(
    callback: CallbackQuery,
    _button: Button,
    dialog_manager: DialogManager,
) -> None:
    """Set language to Russian."""
    user = callback.from_user
    async with get_db_session() as session:
        await UserDAO.update_language(
            session=session,
            telegram_id=user.id,
            language="ru",
        )
    await callback.answer(text=t("language.changed", lang="ru"))
    await dialog_manager.done()


async def on_english_selected(
    callback: CallbackQuery,
    _button: Button,
    dialog_manager: DialogManager,
) -> None:
    """Set language to English."""
    user = callback.from_user
    async with get_db_session() as session:
        await UserDAO.update_language(
            session=session,
            telegram_id=user.id,
            language="en",
        )
    await callback.answer(text=t("language.changed", lang="en"))
    await dialog_manager.done()


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
