.PHONY: build up down restart logs logs-app logs-ngrok clean help

help:
	@echo "Available commands:"
	@echo "  make build    - Build Docker images"
	@echo "  make up       - Start all services"
	@echo "  make down     - Stop all services"
	@echo "  make restart  - Restart all services"
	@echo "  make logs     - View logs from all services"
	@echo "  make logs-app - View logs from app service"
	@echo "  make logs-ngrok - View logs from ngrok service"
	@echo "  make clean    - Remove containers and volumes"
	@echo "  make help     - Show this help message"

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
