.PHONY: build up down restart logs logs-app logs-ngrok clean help \
        prod-build prod-up prod-down prod-logs prod-restart deploy-prod deploy-dev

help:
	@echo "Available commands (development - uses ngrok):"
	@echo "  make build        - Build Docker images"
	@echo "  make up           - Start all services (app + ngrok)"
	@echo "  make down         - Stop all services"
	@echo "  make restart      - Restart all services"
	@echo "  make logs         - View logs from all services"
	@echo "  make logs-app     - View logs from app service"
	@echo "  make logs-ngrok   - View logs from ngrok service"
	@echo "  make clean        - Remove containers and volumes"
	@echo ""
	@echo "Production commands (no ngrok, nginx on host):"
	@echo "  make prod-build   - Build production Docker image"
	@echo "  make prod-up      - Start production container"
	@echo "  make prod-down    - Stop production container"
	@echo "  make prod-logs    - Tail production logs"
	@echo "  make prod-restart - Restart production container"
	@echo "  make deploy-prod  - Git pull + rebuild + restart (master, run on VPS)"
	@echo "  make deploy-dev   - Git pull + rebuild + restart (develop, run on VPS)"
	@echo ""
	@echo "  make help         - Show this help message"

# ── Development (ngrok) ──────────────────────────────────────

build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

restart:
	docker compose restart

logs:
	docker compose logs -f

logs-app:
	docker compose logs -f app

logs-ngrok:
	docker compose logs -f ngrok

clean:
	docker compose down -v

# ── Production (nginx on host, no ngrok) ─────────────────────

prod-build:
	docker compose -f docker-compose.prod.yml build

prod-up:
	docker compose -f docker-compose.prod.yml up -d

prod-down:
	docker compose -f docker-compose.prod.yml down

prod-logs:
	docker compose -f docker-compose.prod.yml logs -f

prod-restart:
	docker compose -f docker-compose.prod.yml restart

deploy-prod:
	bash scripts/deploy.sh master

deploy-dev:
	bash scripts/deploy.sh develop
