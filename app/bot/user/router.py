from aiogram.dispatcher.router import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from app.dao.activity_dao import ActivityDAO
from app.dao.database import get_db_session

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    user = message.from_user
    first_name = user.first_name

    async with get_db_session() as session:
        db_user = await ActivityDAO.get_user_by_telegram_id(
            session=session,
            telegram_id=user.id,
        )

        last_help = None
        if db_user:
            last_help = await ActivityDAO.get_last_help_usage(
                session=session,
                user_id=str(db_user.id),
            )

    if not db_user:
        await message.answer(
            text=f"Hello, {first_name}! 👋\n"
            "Welcome to Mood Tracker Bot!\n"
            "I can help you track your mood and provide insights.",
        )
        return

    first_seen = db_user.first_seen_at.strftime("%Y-%m-%d %H:%M")
    lines = [
        f"Hello, {first_name}! 👋",
        f"We first met: {first_seen}",
    ]

    if last_help:
        help_time = last_help.strftime("%Y-%m-%d %H:%M")
        lines.append(f"Last time you used /help: {help_time}")
    else:
        lines.append("You haven't used /help yet.")

    await message.answer(text="\n".join(lines))


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        text="""
        Hello!
        /start for restart
        /help for this message
        """,
    )
