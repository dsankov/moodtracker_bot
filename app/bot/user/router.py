from aiogram.dispatcher.router import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    user_data = message.from_user.model_dump()
    await message.answer(text=f"Hello, {user_data['first_name']}!")
    await message.answer(
        text="I am a mood tracker bot. I can help you track your mood and provide insights.",
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        text="""
        Hello!
        /start for restart
        /help for this message
        """,
    )
