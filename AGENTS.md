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
- i18n module: Per-user language via `app/bot/i18n.py` `t(key, lang=...)` helper with fallback chain (requested lang → English → slug from key); locale dicts live in `app/bot/locales/en.py` and `app/bot/locales/ru.py`; language read from DB by `app/bot/lang_utils.py`; default `BOT_LANGUAGE` setting used as fallback
- Emotion names: Stored as `slug` in `emotions` table, translated via `t(f"emotion.{slug}", lang=lang)` — no `name`/`name_en`/`is_active` columns
- Emotion ordering: `sort_order` integer column defines logical grouping (not alphabetical)
- Memory storage for FSM: Uses aiogram's MemoryStorage (not persistent)
- PostgreSQL with asyncpg: Async database operations required
- Webhook mode: Bot operates via webhook (not polling)
- Dual environment: `APP_ENV=development` uses ngrok; `APP_ENV=production` uses nginx + domain
- Production compose: `docker-compose.prod.yml` (no ngrok service)

## Code Style

- Ruff configuration ignores: F541, ANN, D, COM812, FBT001, FBT002, FAST002, BLE001, SLF001, RUF001; E501 ignored for alembic migration files
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
- Emotion display names use `t(f"emotion.{emotion.slug}", lang=lang)` — never access `emotion.name` or `emotion.name_en` (those columns don't exist)
- Language resolution: `app/bot/lang_utils.py` reads user's language directly from DB on every getter call
- Dialog widgets must use `Format("{key}")` with getter-provided translations, NOT `Const(t("key"))` (which is static)
- Admin notifications sent to all ADMIN_IDS on bot start/stop
- Loguru logging configured in `app/config.py` with rotation
- User lookup: `UserDAO.get_by_telegram_id()` in `app/dao/user_dao.py` — not in a separate ActivityDAO

## Adding a New Language

1. Create `app/bot/locales/<lang>.py` with all UI string keys + all `emotion.*` keys
2. Import and register in `app/bot/i18n.py` `_messages` dict
3. Add to `LANG_NAMES` in `i18n.py`
4. Add to language dialog in `app/bot/user/language_dialog.py`
5. No database schema changes needed

## Adding a New Emotion

1. Add `emotion.<slug>` key to all locale files (`en.py`, `ru.py`, etc.)
2. Insert a row into the `emotions` table with `slug` and `sort_order` via migration
3. No code changes needed in dialog files — `t(f"emotion.{slug}", lang=lang)` handles it

## Workflow

- Always present a plan with specific files, key changes, and reasoning BEFORE implementing — wait for user approval before making any changes
- Always update `.md` docs (AGENTS.md, README.md, etc.) before commit

## Gotchas

- Bot requires webhook setup before processing updates
- Empty `__init__.py` files throughout the project
- `_get_ngrok_url()` returns `str | None` — callers must handle `None`
- Middleware stores `user_lang` in handler data dict; `get_user_lang()` in `lang_utils.py` reads from DB (not middleware data)
- `t()` has a 3-level fallback: requested language → English → slug derived from key name
- Emotions table has no `name` column — only `slug`. All display names come from i18n
- `sort_order` on emotions defines display order — not alphabetical, uses logical grouping
