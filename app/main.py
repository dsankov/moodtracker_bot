import asyncio
from contextlib import asynccontextmanager

import uvicorn
from aiogram.exceptions import AiogramError
from alembic.config import Config
from fastapi import FastAPI, Request
from loguru import logger

from alembic import command
from app.bot import bot_factory
from app.config import settings


# The @asynccontextmanager decorator is used to define an asynchronous context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Lifespan for {app.title} started")
    mode = "PRODUCTION" if settings.is_production else "DEVELOPMENT"
    logger.info(f"Running in {mode} mode (APP_ENV={settings.APP_ENV})")
    if settings.is_production and not settings.BASE_URL:
        logger.error("BASE_URL is required in production mode. Set it in .env")

    # Run database migrations (in a thread since alembic uses asyncio.run internally)
    logger.info("Running database migrations...")
    alembic_cfg = Config(file_="alembic.ini")
    await asyncio.to_thread(command.upgrade, alembic_cfg, "head")
    logger.success("Database migrations complete")

    await bot_factory.start_bot()

    webhook_url = await settings.hook_url
    logger.info(f"Setting webhook to {webhook_url}")
    await bot_factory.bot.set_webhook(
        url=webhook_url,
        drop_pending_updates=True,
        allowed_updates=bot_factory.dp.resolve_used_update_types(),
    )
    logger.success(f"Webhook set to {webhook_url}")

    webhook_info = await bot_factory.bot.get_webhook_info()
    if webhook_info.url == webhook_url:
        logger.success(f"Webhook successfully set to {webhook_url}")
    else:
        logger.error(f"Failed to set webhook to {webhook_url}")
        error_msg = "Failed to set webhook"
        raise AiogramError(error_msg)

    yield

    await bot_factory.stop_bot()
    logger.info(f"Lifespan for {app.title} ended")


app = FastAPI(lifespan=lifespan)


@app.get("/health_check")
async def health_check() -> dict[str, str]:
    """Lightweight liveness probe for deployment health checks."""
    return {"status": "ok"}


@app.post("/webhook")
async def webhook(request: Request) -> None:
    """Handle incoming webhook requests from Telegram.

    Args:
        request (Request): The incoming request object containing the update data.

    """
    logger.info("Processing webhook request")
    update_data = await request.json()
    await bot_factory.dp.feed_raw_update(bot=bot_factory.bot, update=update_data)
    logger.info("Webhook request processed")


# Run Uvicorn only if the script is executed directly
if __name__ == "__main__":
    uvicorn_log_config = uvicorn.config.LOGGING_CONFIG
    uvicorn_log_config["formatters"]["default"]["fmt"] = (
        "%(asctime)s | %(levelname)s | %(message)s"
    )
    uvicorn_log_config["formatters"]["default"]["datefmt"] = "%Y-%m-%d %H:%M:%S"

    logger.info("Starting Uvicorn server")
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_config=uvicorn_log_config,
        use_colors=True,
    )
