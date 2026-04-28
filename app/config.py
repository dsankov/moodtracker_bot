import sys
from pathlib import Path

import httpx
from loguru import logger
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    BOT_TOKEN: str
    ADMIN_IDS: list[int]
    # INIT_DB: int

    FORMAT_LOG: str = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
    LOG_ROTATION: str = "10 MB"
    DB_URL: str = "sqlite+aiosqlite:///data/db.sqlite3"

    # Environment: "development" (ngrok) or "production" (nginx + domain)
    APP_ENV: str = "development"

    BASE_URL: str = ""
    NGROK_AUTHTOKEN: str = ""
    NGROK_URL: str = ""

    model_config = SettingsConfigDict(
        env_file=(Path(__file__).parent / ".." / ".env").resolve(),
    )

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"

    # Function to get the ngrok URL (development only)
    async def _get_ngrok_url(self) -> str:
        """Get the ngrok URL for the current session."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get("http://ngrok:4040/api/tunnels")
                response.raise_for_status()
                tunnels = response.json()["tunnels"]
                for tunnel in tunnels:
                    if tunnel["proto"] == "https":
                        return tunnel["public_url"]
        except (httpx.RequestError, httpx.ConnectError) as e:
            logger.error(f"Error fetching ngrok URL: {e}")
        return None

    @property
    async def hook_url(self) -> str:
        logger.info(f"{settings.APP_ENV=}, {settings.BASE_URL=}")

        if self.is_production:
            # Production: use BASE_URL directly (nginx handles SSL)
            return f"{self.BASE_URL}/webhook"

        # Development: resolve ngrok tunnel URL
        logger.debug("Fetching ngrok_url")
        ngrok_url = await self._get_ngrok_url()
        if not ngrok_url:
            logger.error("Failed to get ngrok URL")
            error_msg = "Failed to get ngrok URL"
            raise httpx.ConnectError(error_msg)

        return f"{ngrok_url}/webhook"


settings = Settings()

logger.remove()

log_file_path = Path(__file__).resolve().parent / "log.txt"
logger.add(sys.stdout, format=settings.FORMAT_LOG, level="DEBUG", colorize=True)

logger.add(
    log_file_path,
    format=settings.FORMAT_LOG,
    level="DEBUG",
    rotation=settings.LOG_ROTATION,
)
