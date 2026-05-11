from __future__ import annotations

import contextlib
from dataclasses import dataclass
from typing import TYPE_CHECKING

from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import (
    Button,
    CurrentPage,
    Multiselect,
    NextPage,
    PrevPage,
    Row,
    ScrollingGroup,
)
from aiogram_dialog.widgets.text import Format

from app.bot.i18n import t
from app.bot.lang_utils import get_user_lang
from app.dao.database import get_db_session
from app.dao.emotion_dao import EmotionDAO

if TYPE_CHECKING:
    from aiogram.types import CallbackQuery

MAX_EMOTIONS = 3
SEPARATOR_LINE = "━━" * 24  # fixed-width line to keep dialog bubble constant

# Check mark shown next to selected emotions.
# Alternatives: "✔" (\u2714), "☑" (\u2611), "🗸" (\u2713),
#               "✓" (\u2713), "⬜" (\u2B1C), "🔘" (\u1F518), "✅"
CHECK_MARK = "☑"


@dataclass
class EmotionDisplay:
    """Wrapper that exposes the emotion name in the user's language."""

    id: str
    name: str


class MoodSG(StatesGroup):
    select_emotions = State()
    confirm = State()


async def on_emotion_toggled(
    _callback: CallbackQuery,
    _widget,
    dialog_manager: DialogManager,
    item_id: str,
) -> None:
    """Track selection order in dialog_data and auto-transition on exact match."""
    ordered: list[str] = dialog_manager.dialog_data.get(
        "ordered_selection",
        [],
    )
    if item_id in ordered:
        ordered.remove(item_id)
    else:
        ordered.append(item_id)
    dialog_manager.dialog_data["ordered_selection"] = ordered

    # Auto-transition to confirm when exactly MAX_EMOTIONS selected
    if len(ordered) == MAX_EMOTIONS:
        dialog_manager.dialog_data["selected_emotion_ids"] = ordered
        await dialog_manager.switch_to(state=MoodSG.confirm)


async def emotions_getter(
    dialog_manager: DialogManager,
    **_kwargs,
) -> dict:
    """Load active emotions and current selection with names."""
    lang = await get_user_lang(dialog_manager)

    async with get_db_session() as session:
        emotions = await EmotionDAO.get_all(session=session)

    ordered: list[str] = dialog_manager.dialog_data.get(
        "ordered_selection",
        [],
    )

    # Prune stale IDs (e.g. if dialog was reset)
    widget = dialog_manager.find("emotions_ms")
    if widget:
        checked = set(widget.get_checked())
        ordered = [sid for sid in ordered if sid in checked]
        dialog_manager.dialog_data["ordered_selection"] = ordered

    # Wrap emotions with translated names via i18n
    display_emotions = [
        EmotionDisplay(
            id=str(e.id),
            name=t(f"emotion.{e.slug}", lang=lang),
        )
        for e in emotions
    ]

    id_to_name = {
        str(e.id): de.name for e, de in zip(emotions, display_emotions, strict=True)
    }
    selected_names = [id_to_name[sid] for sid in ordered if sid in id_to_name]
    selected_count = len(selected_names)

    if selected_count == 0:
        header = t("mood.select_header", lang=lang)
    else:
        choices_text = ", ".join(selected_names)
        header = t(
            "mood.selected_header",
            lang=lang,
            choices=choices_text,
            count=selected_count,
            max=MAX_EMOTIONS,
        )

    return {
        "emotions": display_emotions,
        "selected_count": selected_count,
        "max": MAX_EMOTIONS,
        "header": f"{header}\n{SEPARATOR_LINE}",
        "btn_proceed": t("mood.btn_proceed", lang=lang),
        "btn_cancel": t("btn.cancel", lang=lang),
    }


async def confirm_getter(
    dialog_manager: DialogManager,
    **_kwargs,
) -> dict:
    """Show selected emotion names on the confirmation screen (in order)."""
    lang = await get_user_lang(dialog_manager)
    selected_ids: list[str] = dialog_manager.dialog_data.get(
        "selected_emotion_ids",
        [],
    )

    async with get_db_session() as session:
        emotions = await EmotionDAO.get_by_ids(
            session=session,
            emotion_ids=selected_ids,
        )

    # Preserve selection order with translated names
    id_to_name = {str(e.id): t(f"emotion.{e.slug}", lang=lang) for e in emotions}
    names = ", ".join(id_to_name[sid] for sid in selected_ids if sid in id_to_name)
    confirm_text = t(
        "mood.confirm_header",
        lang=lang,
        emotions_list=names,
    )
    return {
        "emotions_list": names,
        "confirm_header": f"{confirm_text}\n{SEPARATOR_LINE}",
        "btn_save": t("mood.btn_save", lang=lang),
        "btn_back": t("btn.back", lang=lang),
    }


async def on_proceed_clicked(
    callback: CallbackQuery,
    _button: Button,
    dialog_manager: DialogManager,
) -> None:
    """Validate selection and switch to confirm state."""
    lang = await get_user_lang(dialog_manager)
    ordered: list[str] = dialog_manager.dialog_data.get(
        "ordered_selection",
        [],
    )

    if len(ordered) == 0:
        await callback.answer(
            text=t("mood.validation_alert", lang=lang),
            show_alert=True,
        )
        return

    dialog_manager.dialog_data["selected_emotion_ids"] = ordered
    await dialog_manager.switch_to(state=MoodSG.confirm)


async def _delete_cmd_message(
    callback: CallbackQuery,
    start_data: dict | None,
) -> None:
    """Delete the user's original /mood command message."""
    cmd_msg_id: int | None = (
        start_data.get("cmd_msg_id") if isinstance(start_data, dict) else None
    )
    if cmd_msg_id and callback.message:
        with contextlib.suppress(Exception):
            await callback.bot.delete_message(
                chat_id=callback.message.chat.id,
                message_id=cmd_msg_id,
            )


async def on_save_clicked(
    callback: CallbackQuery,
    _button: Button,
    dialog_manager: DialogManager,
) -> None:
    """Close the dialog with a demo message (no DB save yet)."""
    lang = await get_user_lang(dialog_manager)
    start_data = dialog_manager.start_data
    if callback.message:
        await callback.message.answer(
            text=t("mood.saved_demo", lang=lang),
        )
    await dialog_manager.done()
    await _delete_cmd_message(callback, start_data)
    if isinstance(callback.message, Message):
        with contextlib.suppress(Exception):
            await callback.message.delete()


async def on_cancel_clicked(
    callback: CallbackQuery,
    _button: Button,
    dialog_manager: DialogManager,
) -> None:
    """Cancel and close the dialog, removing its message."""
    start_data = dialog_manager.start_data
    await dialog_manager.done()
    await _delete_cmd_message(callback, start_data)
    if isinstance(callback.message, Message):
        with contextlib.suppress(Exception):
            await callback.message.delete()


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
                Format(f"{CHECK_MARK} {{item.name}}"),
                Format("\u3164 {item.name}"),
                id="emotions_ms",
                item_id_getter=lambda emotion: str(emotion.id),
                items="emotions",
                on_click=on_emotion_toggled,
            ),
            id="emotions_scroll",
            width=2,
            height=8,
            hide_pager=True,
        ),
        Row(
            PrevPage(
                scroll="emotions_scroll",
                id="prev_page",
            ),
            CurrentPage(
                scroll="emotions_scroll",
                id="current_page",
                text=Format("[{current_page1}/{pages}]"),
            ),
            NextPage(
                scroll="emotions_scroll",
                id="next_page",
            ),
        ),
        Row(
            Button(
                Format("{btn_proceed}"),
                id="proceed_btn",
                on_click=on_proceed_clicked,
            ),
            Button(
                Format("{btn_cancel}"),
                id="cancel_btn",
                on_click=on_cancel_clicked,
            ),
        ),
        state=MoodSG.select_emotions,
        getter=emotions_getter,
    ),
    # Window 2: confirm selection
    Window(
        Format("{confirm_header}"),
        Row(
            Button(
                Format("{btn_save}"),
                id="save_btn",
                on_click=on_save_clicked,
            ),
            Button(
                Format("{btn_back}"),
                id="back_btn",
                on_click=on_back_clicked,
            ),
        ),
        state=MoodSG.confirm,
        getter=confirm_getter,
    ),
)
