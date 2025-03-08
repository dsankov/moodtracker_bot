from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand, BotCommandScopeDefault
from aiogram_dialog import setup_dialogs
from loguru import logger

from app.bot.user.router import router as user_router
from app.config import settings

bot = Bot(
    token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher(storage=MemoryStorage())


async def set_commands():
    commands = [
        BotCommand(command="start", description="start bot"),
        BotCommand(command="help", description="help"),
    ]
    await bot.set_my_commands(commands, BotCommandScopeDefault())


async def start_bot():
    logger.info("Starting bot")
    await set_commands()
    setup_dialogs(dp)
    dp.include_router(user_router)

    for admin_id in settings.ADMIN_IDS:
        try:
            await bot.send_message(admin_id, f"mood_trackerbot started")
        except:
            pass
    logger.info("Bot started")


async def stop_bot():
    for admin_id in settings.ADMIN_IDS:
        try:
            await bot.send_message(admin_id, f"mood_trackerbot stopped")
        except:
            pass
    logger.info("Bot stopped")
