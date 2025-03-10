from contextlib import asynccontextmanager

import uvicorn
from aiogram.types import Update
from fastapi import FastAPI, Request
from loguru import logger

from app.bot import bot_factory
from app.config import settings


# The @asynccontextmanager decorator is used to define an asynchronous context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Lifespan for {app.title} started")
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
        raise Exception("Failed to set webhook")

    yield

    await bot_factory.stop_bot()
    logger.info(f"Lifespan for {app.title} ended")


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    logger.info(f"Processing root request")
    return {"message": "Hello, FastAPI!"}


@app.post("/webhook")
async def webhook(request: Request) -> None:
    """Handle incoming webhook requests from Telegram.

    Args:
        request (Request): The incoming request object containing the update data.

    Returns:
        dict: A dictionary indicating the success of the request processing.

    """
    logger.info(f"Processing webhook request")
    update_data = await request.json()
    update = Update.model_validate(update_data, context={"bot": bot_factory.bot})
    await bot_factory.dp._process_update(bot=bot_factory.bot, update=update)
    logger.info(f"Webhook request processed")


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
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_config=uvicorn_log_config,
        use_colors=True,
    )
