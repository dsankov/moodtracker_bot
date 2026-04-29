# Plan: PostgreSQL Migration + User Tracking (with Alembic)

## Overview

Migrate from SQLite to PostgreSQL (Docker Compose) and add user tracking that records first and last bot usage timestamps. Uses Alembic for database schema migrations from the start.

## Architecture

```mermaid
flowchart TD
    subgraph Docker Compose
        A[app container - FastAPI + Aiogram]
        P[postgres container - PostgreSQL 16]
    end
    T[Telegram] -->|webhook| N[nginx :443] -->|reverse proxy| A
    A -->|asyncpg| P

    subgraph User Tracking Flow
        U[Telegram Update] --> M[UserTrackingMiddleware]
        M -->|upsert| DAO[UserDAO]
        DAO -->|SQL INSERT/UPDATE| P
        M -->|continue| H[Handler]
    end

    subgraph Alembic Migrations
        S[app/dao/models.py] -->|Base.metadata| AL[alembic/env.py]
        AL -->|autogenerate| AV[alembic/versions/]
        AV -->|upgrade head| P
    end
```

## Alembic Setup

### Directory Structure

```
alembic/
├── versions/          # Migration files (committed to git)
├── env.py            # Async migration runner
├── script.py.mako    # Migration template
alembic.ini           # Alembic config (at project root)
```

### `alembic/env.py` — Key Configuration

```python
import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from app.config import settings  # reads DATABASE_URL from Settings
from app.dao.database import Base
# Import all models so autogenerate picks them up:
from app.dao.models import User  # noqa: F401

config = context.config
config.set_main_option("sqlalchemy.url", settings.DB_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in 'online' mode with async engine."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

### `alembic.ini` — Key Settings

```ini
[alembic]
script_location = alembic
# sqlalchemy.url is NOT set here — env.py reads it from app.config.settings

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic
```

### Initial Migration

After creating the `User` model, generate the initial migration:

```bash
alembic revision --autogenerate -m "add users table"
```

This inspects `Base.metadata` and produces a migration file in `alembic/versions/`. The migration files **should be committed to git** — they are part of the codebase.

## Files to Create

### 1. `app/dao/models.py` — User Model

```python
import uuid
from datetime import datetime
from sqlalchemy import BigInteger, String, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column
from app.dao.database import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    first_name: Mapped[str] = mapped_column(String(255))
    last_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    first_seen_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    last_seen_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
```

Key decisions:
- `telegram_id` is indexed for fast lookups
- `first_seen_at` is set once on INSERT, never updated
- `last_seen_at` updates on every upsert via `onupdate=func.now()`
- Inherits `created_at` / `updated_at` from `Base` as well (redundant but consistent)

### 2. `app/dao/user_dao.py` — User Data Access

```python
class UserDAO:
    async def upsert_user(self, session: AsyncSession, telegram_id: int, 
                          first_name: str, last_name: str | None, 
                          username: str | None) -> User:
        """Insert new user or update last_seen_at + profile fields."""
```

Uses PostgreSQL `INSERT ... ON CONFLICT DO UPDATE` for atomic upsert.

### 3. `app/bot/middleware.py` — User Tracking Middleware

```python
class UserTrackingMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        # Extract user info from event.from_user
        # Upsert user in database
        # Pass session to handler via data["db_session"]
        await handler(event, data)
```

Runs on every Telegram update (messages, callbacks, etc.). Creates/updates user record before the handler executes.

## Files to Modify

### 4. `app/dao/database.py` — Add session helper

- Add a `get_db_session()` async context manager for use in middleware
- Import the `User` model so Alembic's `target_metadata = Base.metadata` picks it up

### 5. `app/config.py` — Update DB_URL

```python
# Before:
DB_URL: str = "sqlite+aiosqlite:///data/db.sqlite3"

# After:
DB_URL: str = "postgresql+asyncpg://moodtracker:changeme@postgres:5432/moodtracker"
```

The default works inside Docker Compose where the `postgres` hostname resolves to the container. Override via `.env` for other setups.

### 6. `app/bot/bot_factory.py` — Register middleware

```python
from app.bot.middleware import UserTrackingMiddleware
dp.message.middleware(UserTrackingMiddleware())
dp.callback_query.middleware(UserTrackingMiddleware())
```

### 7. `app/main.py` — Run Alembic migrations on startup

In the `lifespan()` function, before starting the bot:

```python
from alembic import command
from alembic.config import Config as AlembicConfig

alembic_cfg = AlembicConfig("alembic.ini")
command.upgrade(alembic_cfg, "head")
```

Note: `command.upgrade` is **synchronous** — it handles its own async event loop internally via `env.py`. Do not `await` it. This replaces the previous `create_all()` approach.

### 8. `docker-compose.yml` — Add postgres service (dev)

```yaml
  postgres:
    image: postgres:16-alpine
    container_name: moodtracker_postgres
    environment:
      POSTGRES_USER: moodtracker
      POSTGRES_PASSWORD: changeme
      POSTGRES_DB: moodtracker
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - moodtracker_network
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U moodtracker"]
      interval: 5s
      timeout: 5s
      retries: 5
```

Add `depends_on: postgres` with condition `service_healthy` to the `app` service.
Add named volume `postgres_data`.

### 9. `docker-compose.prod.yml` — Add postgres service (prod)

Same as dev but with passwords from `.env` and no ngrok dependency.

### 10. `.env.example` — Add PostgreSQL vars

```env
# PostgreSQL
POSTGRES_USER=moodtracker
POSTGRES_PASSWORD=changeme
POSTGRES_DB=moodtracker
DATABASE_URL=postgresql+asyncpg://moodtracker:changeme@postgres:5432/moodtracker
```

### 11. `requirements.in` — Add asyncpg and alembic

```
asyncpg
alembic
```

Then regenerate `requirements.txt` with `uv pip compile requirements.in -o requirements.txt`.

## Migration Strategy

Since there's no production data yet (SQLite was just set up, no models existed), this is a **clean migration** — no data to migrate. Simply:

1. Remove the `./data` volume mount from Docker Compose (was for SQLite)
2. Add `postgres_data` named volume instead
3. Tables are created via Alembic migrations on first startup (`alembic upgrade head`)

Future schema changes follow this workflow:

1. Modify the model in `app/dao/models.py`
2. Run `alembic revision --autogenerate -m "description of change"`
3. Review the generated migration in `alembic/versions/`
4. Commit the migration file to git
5. On next startup, `alembic upgrade head` applies pending migrations automatically

Alembic migration files in `alembic/versions/` **should be committed to git** — they are source-controlled schema changes.

## Implementation Order

1. Add `asyncpg` and `alembic` to `requirements.in` and regenerate `requirements.txt`
2. Initialize Alembic: `alembic init alembic` (creates `alembic/` directory and `alembic.ini`)
3. Configure `alembic/env.py` for async mode with `run_async_migrations`, import `Base.metadata` as `target_metadata`, and read `DATABASE_URL` from `app.config.settings`
4. Configure `alembic.ini` — remove hardcoded `sqlalchemy.url` (env.py handles it)
5. Create `app/dao/models.py` with User model
6. Generate initial migration: `alembic revision --autogenerate -m "add users table"`
7. Create `app/dao/user_dao.py` with upsert logic
8. Update `app/dao/database.py` with session helper
9. Update `app/config.py` with new DB_URL default
10. Create `app/bot/middleware.py` with UserTrackingMiddleware
11. Update `app/bot/bot_factory.py` to register middleware
12. Update `app/main.py` to run `alembic upgrade head` on startup
13. Update `docker-compose.yml` — add postgres service
14. Update `docker-compose.prod.yml` — add postgres service
15. Update `.env.example` with new vars
16. Test locally: `docker compose up --build`
17. Deploy: commit, push, `make deploy-prod` on VPS
