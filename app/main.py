from contextlib import asynccontextmanager

import uvicorn
from aiogram.types import Update
from fastapi import FastAPI, Request
from loguru import logger

from app.bot import bot_factory
from app.config import settings

logger.info("Application started")


# The @asynccontextmanager decorator is used to define an asynchronous context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Lifespan for {app.title} started")
    await bot_factory.start_bot()
    yield
    await bot_factory.stop_bot()
    logger.info(f"Lifespan for {app.title} ended")


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    logger.info(f"Processing root request")
    return {"message": "Hello, FastAPI!"}


# Run Uvicorn only if the script is executed directly
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
