import contextlib

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand, BotCommandScopeDefault
from aiogram_dialog import setup_dialogs
from loguru import logger

from app.bot.i18n import t
from app.bot.middleware import UserTrackingMiddleware
from app.bot.user.greeting_dialog import greeting_dialog
from app.bot.user.help_dialog import help_dialog
from app.bot.user.mood_dialog import mood_dialog
from app.bot.user.router import router as user_router
from app.config import settings

bot = Bot(
    token=settings.BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)
dp = Dispatcher(storage=MemoryStorage())
dp.message.middleware(UserTrackingMiddleware())
dp.callback_query.middleware(UserTrackingMiddleware())


async def set_commands():
    commands = [
        BotCommand(command="start", description=t("cmd.start")),
        BotCommand(command="mood", description=t("cmd.mood")),
        BotCommand(command="help", description=t("cmd.help")),
    ]
    logger.debug("Setting commands")
    await bot.set_my_commands(commands=commands, scope=BotCommandScopeDefault())


async def start_bot():
    logger.info("Starting bot")
    await set_commands()
    dp.include_router(user_router)
    dp.include_router(greeting_dialog)
    dp.include_router(help_dialog)
    dp.include_router(mood_dialog)
    setup_dialogs(dp)

    for admin_id in settings.ADMIN_IDS:
        with contextlib.suppress(Exception):
            await bot.send_message(chat_id=admin_id, text=t("admin.bot_started"))
    logger.info("Bot started")


async def stop_bot():
    for admin_id in settings.ADMIN_IDS:
        with contextlib.suppress(Exception):
            await bot.send_message(chat_id=admin_id, text=t("admin.bot_stopped"))
    logger.info("Bot stopped")
