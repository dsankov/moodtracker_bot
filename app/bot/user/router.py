from aiogram.dispatcher.router import Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram_dialog import DialogManager

from app.bot.user.greeting_dialog import GreetingSG
from app.bot.user.help_dialog import HelpSG
from app.bot.user.mood_dialog import MoodSG
from app.dao.activity_dao import ActivityDAO
from app.dao.database import get_db_session

router = Router()


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
    current = await state.get_state()

    # If help dialog is on top, close it — mood dialog underneath resumes
    if current == HelpSG.main.state:
        await dialog_manager.done()
        return

    # If mood dialog is already active, don't restart
    if current in (MoodSG.select_emotions.state, MoodSG.confirm.state):
        return

    await dialog_manager.start(state=MoodSG.select_emotions)


@router.message(Command("help"))
async def cmd_help(_message: Message, dialog_manager: DialogManager):
    """Show help as an overlay dialog (any active dialog stays underneath)."""
    await dialog_manager.start(state=HelpSG.main)
