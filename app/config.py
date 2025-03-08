import os
import sys
from pathlib import Path

from loguru import logger
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    BOT_TOKEN: str
    ADMIN_IDS: list[int]
    INIT_DB: int

    FORMAT_LOG: str = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
    LOG_ROTATION: str = "10 MB"
    DB_URL: str = "sqlite+aiosqlite:///data/db.sqlite3"

    BASE_URL: str = ""

    model_config = SettingsConfigDict(
        env_file=(Path(__file__).resolve().parent / ".." / ".env").resolve(),
    )

    @property
    def hook_url(self) -> str:
        return f"{self.BASE_URL}/webhook"


settings = Settings()

logger.remove()

log_file_path = os.path.join(os.path.dirname(__file__), "log.txt")
logger.add(sys.stdout, format=settings.FORMAT_LOG, level="INFO", colorize=True)
logger.add(
    log_file_path,
    format=settings.FORMAT_LOG,
    level="INFO",
    rotation=settings.LOG_ROTATION,
)
