from aiogram.fsm.state import State, StatesGroup
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.text import Format

from app.bot.i18n import t
from app.bot.lang_utils import get_user_lang


class HelpSG(StatesGroup):
    main = State()


async def help_getter(
    dialog_manager: DialogManager,
    **_kwargs,
) -> dict:
    """Getter for the help window — provides translated strings."""
    lang = await get_user_lang(dialog_manager)
    return {
        "help_text": t("help.text", lang=lang),
    }


help_dialog = Dialog(
    Window(
        Format("{help_text}"),
        state=HelpSG.main,
        getter=help_getter,
    ),
)
