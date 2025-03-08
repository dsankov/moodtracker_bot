from aiogram import F
from aiogram.filters import CommandStart
from aiogram.dispatcher.router import Router

router = Router()

@router.message(CommandStart())
async def cmd_start(message: F.Message):
    user_data = message.from_user.dict()
    await message.answer(f"Hello, {user_data['first_name']}!")
    await message.answer("I am a mood tracker bot. I can help you track your mood and provide insights.")
    


