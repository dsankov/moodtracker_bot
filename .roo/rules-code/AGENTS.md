# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## Project Coding Rules (Non-Obvious Only)

- Always use async/await for database operations - asyncpg requires async patterns
- Bot handlers must be async due to aiogram's async architecture
- Database models inherit from Base in `app/dao/database.py` with automatic timestamps
- Use `contextlib.suppress(Exception)` for error handling in bot operations
- Webhook endpoint in `app/main.py` requires specific Update validation pattern
- Bot factory pattern: All bot initialization must go through `app/bot/bot_factory.py`
- Settings must be loaded from `app.config.settings` - direct env access will fail
- Database engine variable is `engine` in `app.dao.database` — standard naming
- FSM state storage is MemoryStorage - no persistence across restarts
- Admin notifications automatically sent to ADMIN_IDS on start/stop - don't add duplicate notifications
- `APP_ENV` setting controls dev vs prod mode: `development` uses ngrok, `production` uses BASE_URL directly
- Production uses `docker-compose.prod.yml` (no ngrok); development uses `docker-compose.yml` (with ngrok)
- `settings.is_production` property should be used to check environment mode