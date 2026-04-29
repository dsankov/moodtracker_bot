import asyncio
from contextlib import asynccontextmanager

import httpx
import uvicorn
from aiogram.exceptions import AiogramError
from aiogram.types import Update
from fastapi import FastAPI, Header, Request

# from icecream import ic
from loguru import logger

from alembic import command
from alembic.config import Config
from app.bot import bot_factory
from app.config import settings


# Function to get the ngrok URL
async def get_ngrok_url():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://ngrok:4040/api/tunnels")
            response.raise_for_status()
            tunnels = response.json()["tunnels"]
            for tunnel in tunnels:
                if tunnel["proto"] == "https":
                    return tunnel["public_url"]
    except httpx.RequestError as e:
        logger.error(f"Error fetching ngrok URL: {e}")
    return None


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
    alembic_cfg = Config("alembic.ini")
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


@app.get("/")
async def root() -> dict:
    """Root endpoint."""
    return {"message": "Hello, World!"}


@app.post("/user/add")
async def add_user(user_data: str = Header()) -> dict:
    """Add a new user to the database."""
    logger.debug(f"Adding new user: {user_data}")
    return {"user_data": user_data}


# @app.get("/user/{user_id}")
# async def get_user(user_id: int, is_admin: bool | None = None) -> None:
#     """Get user data by ID."""

#     logger.debug(f"Getting user with ID {user_id}")
#     return {"user_id": user_id, "is_admin": is_admin}


@app.post("/webhook")
async def webhook(request: Request) -> None:
    """Handle incoming webhook requests from Telegram.

    Args:
        request (Request): The incoming request object containing the update data.

    """
    logger.info(f"Processing webhook request")
    try:
        update_data = await request.json()
        update = Update.model_validate(update_data, context={"bot": bot_factory.bot})
    except Exception:
        logger.error(f"Failed to validate update data")
        return

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
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_config=uvicorn_log_config,
        use_colors=True,
    )
