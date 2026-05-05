from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Format

from app.bot.i18n import t
from app.bot.lang_utils import get_user_lang
from app.dao.activity_dao import ActivityDAO
from app.dao.database import get_db_session


class GreetingSG(StatesGroup):
    welcome = State()
    returning = State()


async def welcome_getter(
    dialog_manager: DialogManager,
    **_kwargs,
) -> dict:
    """Getter for the new-user welcome window."""
    lang = await get_user_lang(dialog_manager)
    user = dialog_manager.event.from_user
    return {
        "greeting_hello": t(
            "greeting.hello",
            lang=lang,
            first_name=user.first_name,
        ),
        "greeting_welcome_new": t("greeting.welcome_new", lang=lang),
        "greeting_welcome_desc": t("greeting.welcome_desc", lang=lang),
        "btn_ok": t("btn.ok", lang=lang),
    }


async def returning_getter(
    dialog_manager: DialogManager,
    **_kwargs,
) -> dict:
    """Getter for the returning-user window — fetches DB info."""
    lang = await get_user_lang(dialog_manager)
    user = dialog_manager.event.from_user

    async with get_db_session() as session:
        db_user = await ActivityDAO.get_user_by_telegram_id(
            session=session,
            telegram_id=user.id,
        )

        first_seen = t("greeting.unknown_date", lang=lang)
        last_help = t("greeting.no_help_yet", lang=lang)

        if db_user:
            first_seen = db_user.first_seen_at.strftime("%Y-%m-%d %H:%M")

            last_help_activity = await ActivityDAO.get_last_help_usage(
                session=session,
                user_id=str(db_user.id),
            )
            if last_help_activity:
                last_help = last_help_activity.strftime("%Y-%m-%d %H:%M")

    return {
        "greeting_hello": t(
            "greeting.hello",
            lang=lang,
            first_name=user.first_name,
        ),
        "greeting_first_seen": t(
            "greeting.first_seen",
            lang=lang,
            first_seen=first_seen,
        ),
        "greeting_last_help": t(
            "greeting.last_help",
            lang=lang,
            last_help=last_help,
        ),
        "btn_ok": t("btn.ok", lang=lang),
    }


async def on_ok_clicked(
    _callback: CallbackQuery,
    _button: Button,
    _dialog_manager: DialogManager,
) -> None:
    """Close the dialog when the OK button is pressed."""
    await _dialog_manager.done()


greeting_dialog = Dialog(
    # Window for new users
    Window(
        Format("{greeting_hello}"),
        Format("{greeting_welcome_new}"),
        Format("{greeting_welcome_desc}"),
        Button(Format("{btn_ok}"), id="ok_btn", on_click=on_ok_clicked),
        state=GreetingSG.welcome,
        getter=welcome_getter,
    ),
    # Window for returning users
    Window(
        Format("{greeting_hello}"),
        Format("{greeting_first_seen}"),
        Format("{greeting_last_help}"),
        Button(Format("{btn_ok}"), id="ok_btn", on_click=on_ok_clicked),
        state=GreetingSG.returning,
        getter=returning_getter,
    ),
)
