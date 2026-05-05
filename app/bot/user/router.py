from aiogram.dispatcher.router import Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram_dialog import DialogManager

from app.bot.i18n import t
from app.bot.lang_utils import get_user_lang
from app.bot.user.help_dialog import HelpSG
from app.bot.user.language_dialog import LanguageSG
from app.bot.user.mood_dialog import MoodSG
from app.dao.activity_dao import ActivityDAO
from app.dao.database import get_db_session

router = Router()


async def _close_help_if_active(
    dialog_manager: DialogManager,
    state: FSMContext,
) -> bool:
    """Close help dialog if it's on top of the stack.

    Returns True if help was closed.
    """
    current = await state.get_state()
    if current == HelpSG.main.state:
        await dialog_manager.done()
        return True
    return False


@router.message(CommandStart())
async def cmd_start(message: Message, dialog_manager: DialogManager):
    """Send a greeting message directly (no dialog)."""
    user = message.from_user
    lang = await get_user_lang(dialog_manager)

    async with get_db_session() as session:
        db_user = await ActivityDAO.get_user_by_telegram_id(
            session=session,
            telegram_id=user.id,
        )

    greeting_hello = t("greeting.hello", lang=lang, first_name=user.first_name)

    if db_user:
        first_seen = db_user.first_seen_at.strftime("%Y-%m-%d %H:%M")
        greeting_first_seen = t("greeting.first_seen", lang=lang, first_seen=first_seen)
        await message.answer(text=f"{greeting_hello}\n{greeting_first_seen}")
    else:
        welcome_new = t("greeting.welcome_new", lang=lang)
        welcome_desc = t("greeting.welcome_desc", lang=lang)
        await message.answer(text=f"{greeting_hello}\n{welcome_new}\n{welcome_desc}")


@router.message(Command("mood"))
async def cmd_mood(
    _message: Message,
    dialog_manager: DialogManager,
    state: FSMContext,
):
    """Open or resume the mood tracking dialog."""
    # Close help if active — don't return to it
    await _close_help_if_active(dialog_manager, state)

    current = await state.get_state()

    # If mood dialog is already active, don't restart
    if current in (MoodSG.select_emotions.state, MoodSG.confirm.state):
        return

    await dialog_manager.start(state=MoodSG.select_emotions)


@router.message(Command("help"))
async def cmd_help(_message: Message, dialog_manager: DialogManager):
    """Show help as an overlay dialog (any active dialog stays underneath)."""
    await dialog_manager.start(state=HelpSG.main)


@router.message(Command("language"))
async def cmd_language(
    _message: Message,
    dialog_manager: DialogManager,
    state: FSMContext,
):
    """Show language selection dialog."""
    # Close help if active — don't return to it
    await _close_help_if_active(dialog_manager, state)

    await dialog_manager.start(state=LanguageSG.select)
