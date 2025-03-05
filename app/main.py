from app.config import settings
from loguru import logger
from fastapi import FastAPI, Request
from aiogram.types import Update
from contextlib import asynccontextmanager
import uvicorn



logger.info("Application started")

# The @asynccontextmanager decorator is used to define an asynchronous context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Lifespan started")
    yield
    logger.info("Lifespan ended")
    
app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    return {"message": "Hello, FastAPI!"}

# Run Uvicorn only if the script is executed directly
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)