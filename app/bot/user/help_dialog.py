from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const


class HelpSG(StatesGroup):
    main = State()


async def on_ok_clicked(
    _callback: CallbackQuery,
    _button: Button,
    dialog_manager: DialogManager,
) -> None:
    """Close help dialog — any underlying dialog resumes automatically."""
    await dialog_manager.done()


help_dialog = Dialog(
    Window(
        Const(
            "Hello!\n"
            "/start for restart\n"
            "/mood to track your mood\n"
            "/help for this message",
        ),
        Button(Const("OK"), id="ok_btn", on_click=on_ok_clicked),
        state=HelpSG.main,
    ),
)
