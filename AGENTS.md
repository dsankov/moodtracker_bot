# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## Commands

- Run the bot: `python -m app.main`
- Lint code: `ruff check .`
- Format code: `ruff format .`
- Docker dev: `make build`, `make up`, `make down`, `make logs`
- Docker prod: `make prod-build`, `make prod-up`, `make prod-down`, `make prod-logs`
- Deploy to VPS: `make deploy-prod` (git pull + rebuild + restart)

## Architecture

- FastAPI + Aiogram hybrid: Web server handles webhook endpoints, bot processes Telegram updates
- Bot factory pattern: Centralized bot creation in `app/bot/bot_factory.py`
- i18n module: Per-user language via `app/bot/i18n.py` `t(key, lang=...)` helper; language read from DB by `app/bot/lang_utils.py`; default `BOT_LANGUAGE` setting used as fallback
- Memory storage for FSM: Uses aiogram's MemoryStorage (not persistent)
- SQLite with aiosqlite: Async database operations required
- Webhook mode: Bot operates via webhook (not polling)
- Dual environment: `APP_ENV=development` uses ngrok; `APP_ENV=production` uses nginx + domain
- Production compose: `docker-compose.prod.yml` (no ngrok service)

## Code Style

- Ruff configuration ignores: F541 (f-strings without placeholders), ERA001 (commented code), ANN (type annotations), D (docstrings)
- Use `contextlib.suppress(Exception)` for error handling in bot operations
- Pydantic models for configuration with BaseSettings
- Async/await required throughout due to async database and bot operations
- Always use keyword arguments (`param=value`) in function/method calls where named parameters exist — e.g. `bot.send_message(chat_id=admin_id, text=...)`, not `bot.send_message(admin_id, "...")`. Exception: fluent/builder APIs (SQLAlchemy `.where()`, `.limit()`) and positional-only parameters (e.g. `AiogramError(msg)`) remain positional

## Critical Patterns

- Database models inherit from Base in `app/dao/database.py` with automatic timestamps
- Settings loaded from `.env` file relative to `app/config.py` location
- Webhook URL: In production (`APP_ENV=production`), uses `BASE_URL` directly; in development, resolves via ngrok API
- `APP_ENV` controls mode: `development` (ngrok) or `production` (nginx reverse-proxy)
- `BOT_LANGUAGE` controls default UI language: `"en"` (default) or `"ru"` — per-user language stored in `users.language` column
- All user-facing strings must use `t("key", lang=lang)` from `app/bot/i18n.py` with `lang` from `get_user_lang(dialog_manager)` — never hardcode text in dialog files
- Language resolution: `app/bot/lang_utils.py` reads user's language directly from DB on every getter call
- Dialog widgets must use `Format("{key}")` with getter-provided translations, NOT `Const(t("key"))` (which is static)
- Admin notifications sent to all ADMIN_IDS on bot start/stop
- Loguru logging configured in `app/config.py` with rotation

## Workflow

- Always present a plan with specific files, key changes, and reasoning BEFORE implementing — wait for user approval before making any changes
- Always update `.md` docs (AGENTS.md, README.md, etc.) before commit

## Gotchas

- Database engine has typo: `enging` instead of `engine` in `app/dao/database.py`
- Bot requires webhook setup before processing updates
- Empty `__init__.py` files throughout the project
- Pydantic test file (`app/pydantic_test.py`) has syntax error (missing comma in Field definition)