# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## Project Architecture Rules (Non-Obvious Only)

- FastAPI + Aiogram hybrid architecture: Web server handles webhook endpoints, bot processes Telegram updates in same process
- Bot factory pattern centralizes all bot creation - don't instantiate Bot/Dispatcher directly
- Memory storage for FSM means no state persistence - affects scaling and restart behavior
- Webhook mode requires external URL exposure - affects deployment architecture
- SQLite with aiosqlite requires async patterns throughout - no sync database operations
- Admin notifications are tightly coupled to bot lifecycle - consider decoupling for scalability
- Database models inherit from Base with automatic timestamps - affects migration strategy
- Configuration loaded relative to `app/config.py` - affects containerization and deployment
- No test framework present - testing strategy needs to be established
- Docker volume mapping mounts entire project - affects development vs production separation
- Dual environment: `APP_ENV=development` (ngrok) vs `APP_ENV=production` (nginx + domain)
- Production uses `docker-compose.prod.yml`; development uses `docker-compose.yml`
- Deployment guide at `docs/deployment.md` covers VPS setup, nginx, and sync strategies