from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import (
    Button,
    Multiselect,
    Row,
    ScrollingGroup,
)
from aiogram_dialog.widgets.text import Const, Format

from app.dao.database import get_db_session
from app.dao.emotion_dao import EmotionDAO

MAX_EMOTIONS = 3


class MoodSG(StatesGroup):
    select_emotions = State()
    confirm = State()


async def emotions_getter(
    dialog_manager: DialogManager,
    **_kwargs,
) -> dict:
    """Load active emotions and current selection count."""
    async with get_db_session() as session:
        emotions = await EmotionDAO.get_all_active(session=session)

    selected_count = 0
    widget = dialog_manager.find("emotions_ms")
    if widget:
        selected_count = len(widget.get_checked())

    return {
        "emotions": emotions,
        "selected_count": selected_count,
        "max": MAX_EMOTIONS,
    }


async def confirm_getter(
    dialog_manager: DialogManager,
    **_kwargs,
) -> dict:
    """Show selected emotion names on the confirmation screen."""
    selected_ids = dialog_manager.dialog_data.get(
        "selected_emotion_ids", [],
    )

    async with get_db_session() as session:
        emotions = await EmotionDAO.get_by_ids(
            session=session,
            emotion_ids=selected_ids,
        )

    names = ", ".join(e.name for e in emotions)
    return {"emotions_list": names}


async def on_proceed_clicked(
    callback: CallbackQuery,
    _button: Button,
    dialog_manager: DialogManager,
) -> None:
    """Validate selection and switch to confirm state."""
    widget = dialog_manager.find("emotions_ms")
    selected = widget.get_checked() if widget else set()

    if len(selected) != MAX_EMOTIONS:
        await callback.answer(
            text=f"Выбрано {len(selected)}/{MAX_EMOTIONS}. "
            f"Нужно ровно {MAX_EMOTIONS} эмоции.",
            show_alert=True,
        )
        return

    dialog_manager.dialog_data["selected_emotion_ids"] = list(selected)
    await dialog_manager.switch_to(state=MoodSG.confirm)


async def on_save_clicked(
    callback: CallbackQuery,
    _button: Button,
    dialog_manager: DialogManager,
) -> None:
    """Close the dialog with a demo message (no DB save yet)."""
    if callback.message:
        await callback.message.answer(
            text="Запись сохранена! (демо-режим)",
        )
    await dialog_manager.done()


async def on_cancel_clicked(
    _callback: CallbackQuery,
    _button: Button,
    dialog_manager: DialogManager,
) -> None:
    """Cancel and close the dialog."""
    await dialog_manager.done()


async def on_back_clicked(
    _callback: CallbackQuery,
    _button: Button,
    dialog_manager: DialogManager,
) -> None:
    """Go back to emotion selection."""
    await dialog_manager.switch_to(state=MoodSG.select_emotions)


mood_dialog = Dialog(
    # Window 1: select emotions
    Window(
        Format(
            "Выберите {max} эмоции "
            "(выбрано: {selected_count}/{max}):",
        ),
        ScrollingGroup(
            Multiselect(
                Format("✅ {item.name}"),
                Format("{item.name}"),
                id="emotions_ms",
                item_id_getter=lambda emotion: str(emotion.id),
                items="emotions",
            ),
            id="emotions_scroll",
            width=1,
            height=6,
        ),
        Row(
            Button(
                Const("Записать"),
                id="proceed_btn",
                on_click=on_proceed_clicked,
            ),
            Button(
                Const("Отмена"),
                id="cancel_btn",
                on_click=on_cancel_clicked,
            ),
        ),
        state=MoodSG.select_emotions,
        getter=emotions_getter,
    ),
    # Window 2: confirm selection
    Window(
        Format("Вы выбрали:\n\n{emotions_list}"),
        Row(
            Button(
                Const("Записать ✅"),
                id="save_btn",
                on_click=on_save_clicked,
            ),
            Button(
                Const("Назад ↩️"),
                id="back_btn",
                on_click=on_back_clicked,
            ),
        ),
        state=MoodSG.confirm,
        getter=confirm_getter,
    ),
)
