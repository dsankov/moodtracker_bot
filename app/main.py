from contextlib import asynccontextmanager

import uvicorn
from aiogram.types import Update
from fastapi import FastAPI, Request
from loguru import logger

from app.bot import bot_factory
from app.config import settings
from icecream import ic
import httpx


# Function to get the ngrok URL
async def get_ngrok_url():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:4040/api/tunnels")
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
    await bot_factory.start_bot()

    # webhook_url = settings.hook_url
    # logger.info(f"Setting webhook to {webhook_url}")
    # await bot_factory.bot.set_webhook(
    #     url=webhook_url,
    #     drop_pending_updates=True,
    #     # allowed_updates=bot_factory.dp.resolve_used_update_types(),
    # )

    ngrok_url = await get_ngrok_url()
    if ngrok_url:
        webhook_url = f"{ngrok_url}/webhook"
        logger.info(f"Setting webhook to {webhook_url}")
        await bot_factory.bot.set_webhook(
            url=webhook_url,
            drop_pending_updates=True,
            # allowed_updates=bot_factory.dp.resolve_used_update_types(),
        )
        logger.success(f"Webhook set to {webhook_url}")
    else:
        logger.error("Failed to set webhook: ngrok URL not found")

    # webhook_info = await bot_factory.bot.get_webhook_info()
    # logger.info(webhook_info.url)
    # logger.info((await bot_factory.bot.get_webhook_info().).url)
    # if await bot_factory.bot.get_webhook_info().url == webhook_url:
    #     logger.success(f"Webhook successfully set to {webhook_url}")
    # else:
    #     logger.error(f"Failed to set webhook to {webhook_url}")

    yield

    await bot_factory.stop_bot()
    logger.info(f"Lifespan for {app.title} ended")


app = FastAPI(lifespan=lifespan)

<<<<<<< Updated upstream

@app.get("/")
async def root():
    logger.info(f"Processing root request")
    return {"message": "Hello, FastAPI!"}


=======
@app.get("/")
async def root() -> dict:
    """Root endpoint."""
    return {"message": "Hello, World!"}


@app.get("/user/{user_id}")
async def get_user(user_id: int, is_admin: bool | None = None) -> None:
    """Get user data by ID."""

    logger.debug(f"Getting user with ID {user_id}")


@app.post("/user/add")
async def add_user(user_data: dict) -> None:
    """Add a new user to the database."""
    logger.debug(f"Adding new user: {user_data}")
    return {"status": "success"}

>>>>>>> Stashed changes
@app.post("/webhook")
async def webhook(request: Request):
    logger.info(f"Processing webhook request")
    try:
        update_data = await request.json()
        update = Update.model_validate(update_data, context={"bot": bot_factory.bot})
    except Exception as e:
        logger.error(f"Failed to validate update data")
        return

    await bot_factory.dp._process_update(bot=bot_factory.bot, update=update)
    logger.info(f"Webhook request processed")
    return {"ok": True}


# Run Uvicorn only if the script is executed directly
if __name__ == "__main__":
    uvicorn_log_config = uvicorn.config.LOGGING_CONFIG
    uvicorn_log_config["formatters"]["default"]["fmt"] = (
        "%(asctime)s | %(levelname)s | %(message)s"
    )
    uvicorn_log_config["formatters"]["default"]["datefmt"] = "%Y-%m-%d %H:%M:%S"
    # uvicorn_log_config["formatters"]["default"]["use_colors"] = True
    # ic(uvicorn_log_config)
    logger.info("Application started")
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_config=uvicorn_log_config,
        use_colors=True,
    )
