# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## Project Documentation Rules (Non-Obvious Only)

- README.md installation instructions are outdated - project uses uv not pip
- `app/dao/` directory contains database models and connection logic (not just DAOs)
- Bot operates in webhook mode, not polling - affects deployment and testing
- FastAPI and Aiogram run together in single process - not separate services
- `.env.example` includes `APP_ENV` for switching between development (ngrok) and production (nginx)
- `app/pydantic_test.py` is not a test file - it's a development scratchpad with syntax error
- Production Docker Compose: `docker-compose.prod.yml` (root); Development: `docker-compose.yml` (root)
- Deployment guide: `docs/deployment.md` — VPS setup, nginx config, code sync strategies
- All `__init__.py` files are empty - Python package structure only
- Admin router exists but has no handlers - placeholder for future features
- Database URL defaults to SQLite in `data/` directory - created automatically