from aiogram.dispatcher.router import Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram_dialog import DialogManager

from app.bot.user.greeting_dialog import GreetingSG
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
    user = message.from_user

    async with get_db_session() as session:
        db_user = await ActivityDAO.get_user_by_telegram_id(
            session=session,
            telegram_id=user.id,
        )

    if db_user:
        await dialog_manager.start(state=GreetingSG.returning)
    else:
        await dialog_manager.start(state=GreetingSG.welcome)


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
