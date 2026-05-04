from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const, Format, Multi

from app.bot.i18n import t
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
    user = dialog_manager.event.from_user
    return {"first_name": user.first_name}


async def returning_getter(
    dialog_manager: DialogManager,
    **_kwargs,
) -> dict:
    """Getter for the returning-user window — fetches DB info."""
    user = dialog_manager.event.from_user

    async with get_db_session() as session:
        db_user = await ActivityDAO.get_user_by_telegram_id(
            session=session,
            telegram_id=user.id,
        )

        first_seen = t("greeting.unknown_date")
        last_help = t("greeting.no_help_yet")

        if db_user:
            first_seen = db_user.first_seen_at.strftime("%Y-%m-%d %H:%M")

            last_help_activity = await ActivityDAO.get_last_help_usage(
                session=session,
                user_id=str(db_user.id),
            )
            if last_help_activity:
                last_help = last_help_activity.strftime("%Y-%m-%d %H:%M")

    return {
        "first_name": user.first_name,
        "first_seen": first_seen,
        "last_help": last_help,
    }


async def on_ok_clicked(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
) -> None:
    """Close the dialog when the OK button is pressed."""
    await dialog_manager.done()


greeting_dialog = Dialog(
    # Window for new users
    Window(
        Multi(
            Format(t("greeting.hello")),
            Const(t("greeting.welcome_new")),
            Const(t("greeting.welcome_desc")),
            sep="\n",
        ),
        Button(Const(t("btn.ok")), id="ok_btn", on_click=on_ok_clicked),
        state=GreetingSG.welcome,
        getter=welcome_getter,
    ),
    # Window for returning users
    Window(
        Multi(
            Format(t("greeting.hello")),
            Format(t("greeting.first_seen")),
            Format(t("greeting.last_help")),
            sep="\n",
        ),
        Button(Const(t("btn.ok")), id="ok_btn", on_click=on_ok_clicked),
        state=GreetingSG.returning,
        getter=returning_getter,
    ),
)
