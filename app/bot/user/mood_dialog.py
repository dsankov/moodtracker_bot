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

from app.bot.i18n import t
from app.dao.database import get_db_session
from app.dao.emotion_dao import EmotionDAO

MAX_EMOTIONS = 3


class MoodSG(StatesGroup):
    select_emotions = State()
    confirm = State()


async def on_emotion_toggled(
    _callback: CallbackQuery,
    _widget,
    dialog_manager: DialogManager,
    item_id: str,
) -> None:
    """Track selection order in dialog_data."""
    ordered: list[str] = dialog_manager.dialog_data.get(
        "ordered_selection", [],
    )
    if item_id in ordered:
        ordered.remove(item_id)
    else:
        ordered.append(item_id)
    dialog_manager.dialog_data["ordered_selection"] = ordered


async def emotions_getter(
    dialog_manager: DialogManager,
    **_kwargs,
) -> dict:
    """Load active emotions and current selection with names."""
    async with get_db_session() as session:
        emotions = await EmotionDAO.get_all_active(session=session)

    ordered: list[str] = dialog_manager.dialog_data.get(
        "ordered_selection", [],
    )

    # Prune stale IDs (e.g. if dialog was reset)
    widget = dialog_manager.find("emotions_ms")
    if widget:
        checked = set(widget.get_checked())
        ordered = [sid for sid in ordered if sid in checked]
        dialog_manager.dialog_data["ordered_selection"] = ordered

    id_to_name = {str(e.id): e.name for e in emotions}
    selected_names = [id_to_name[sid] for sid in ordered if sid in id_to_name]
    selected_count = len(selected_names)

    if selected_count == 0:
        header = t("mood.select_header")
    else:
        choices_text = ", ".join(selected_names)
        header = t(
            "mood.selected_header",
            choices=choices_text,
            count=selected_count,
            max=MAX_EMOTIONS,
        )

    return {
        "emotions": emotions,
        "selected_count": selected_count,
        "max": MAX_EMOTIONS,
        "header": header,
    }


async def confirm_getter(
    dialog_manager: DialogManager,
    **_kwargs,
) -> dict:
    """Show selected emotion names on the confirmation screen (in order)."""
    selected_ids: list[str] = dialog_manager.dialog_data.get(
        "selected_emotion_ids", [],
    )

    async with get_db_session() as session:
        emotions = await EmotionDAO.get_by_ids(
            session=session,
            emotion_ids=selected_ids,
        )

    # Preserve selection order
    id_to_name = {str(e.id): e.name for e in emotions}
    names = ", ".join(
        id_to_name[sid] for sid in selected_ids if sid in id_to_name
    )
    return {"emotions_list": names}


async def on_proceed_clicked(
    callback: CallbackQuery,
    _button: Button,
    dialog_manager: DialogManager,
) -> None:
    """Validate selection and switch to confirm state."""
    ordered: list[str] = dialog_manager.dialog_data.get(
        "ordered_selection", [],
    )

    if len(ordered) != MAX_EMOTIONS:
        await callback.answer(
            text=t(
                "mood.validation_alert",
                current=len(ordered),
                max=MAX_EMOTIONS,
            ),
            show_alert=True,
        )
        return

    dialog_manager.dialog_data["selected_emotion_ids"] = ordered
    await dialog_manager.switch_to(state=MoodSG.confirm)


async def on_save_clicked(
    callback: CallbackQuery,
    _button: Button,
    dialog_manager: DialogManager,
) -> None:
    """Close the dialog with a demo message (no DB save yet)."""
    if callback.message:
        await callback.message.answer(
            text=t("mood.saved_demo"),
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
        Format("{header}"),
        ScrollingGroup(
            Multiselect(
                Format(t("mood.emotion_checked")),
                Format("{item.name}"),
                id="emotions_ms",
                item_id_getter=lambda emotion: str(emotion.id),
                items="emotions",
                on_click=on_emotion_toggled,
            ),
            id="emotions_scroll",
            width=1,
            height=6,
        ),
        Row(
            Button(
                Const(t("mood.btn_proceed")),
                id="proceed_btn",
                on_click=on_proceed_clicked,
            ),
            Button(
                Const(t("btn.cancel")),
                id="cancel_btn",
                on_click=on_cancel_clicked,
            ),
        ),
        state=MoodSG.select_emotions,
        getter=emotions_getter,
    ),
    # Window 2: confirm selection
    Window(
        Format(t("mood.confirm_header")),
        Row(
            Button(
                Const(t("mood.btn_save")),
                id="save_btn",
                on_click=on_save_clicked,
            ),
            Button(
                Const(t("btn.back")),
                id="back_btn",
                on_click=on_back_clicked,
            ),
        ),
        state=MoodSG.confirm,
        getter=confirm_getter,
    ),
)
