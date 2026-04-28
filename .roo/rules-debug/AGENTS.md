# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## Project Debug Rules (Non-Obvious Only)

- Bot logs to `app/log.txt` with rotation - check this file for persistent logs
- Webhook validation failures are silent - add logging in `/webhook` endpoint to debug
- Database engine has typo: `enging` instead of `engine` - this causes connection errors
- Admin notifications use `contextlib.suppress(Exception)` - failures won't appear in logs
- SQLite database created at `data/db.sqlite3` relative to project root
- FastAPI runs on port 8000 by default - webhook URL must match this
- Bot requires webhook setup before processing updates - check webhook_info after setting
- MemoryStorage for FSM means state lost on restart - don't rely on persisted state
- Pydantic test file (`app/pydantic_test.py`) has syntax error that may affect imports
- Docker volume mapping mounts entire project - changes reflected immediately in container
- `APP_ENV` controls webhook URL resolution: `development` = ngrok API, `production` = BASE_URL directly
- Production runs via `docker-compose.prod.yml` (no ngrok) — check nginx logs if webhook not reaching app