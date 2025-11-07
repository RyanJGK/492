# 492-Energy-Defense Makefile
# Convenient commands for system management

.PHONY: help init start stop restart logs clean test health

help:
	@echo "492-Energy-Defense - Available Commands"
	@echo "======================================="
	@echo ""
	@echo "  make init      - Initialize and start the system"
	@echo "  make start     - Start all services"
	@echo "  make stop      - Stop all services"
	@echo "  make restart   - Restart all services"
	@echo "  make logs      - View logs from all services"
	@echo "  make health    - Check system health"
	@echo "  make test      - Run test suite"
	@echo "  make clean     - Remove containers and volumes"
	@echo "  make backup    - Backup database"
	@echo ""

init:
	@bash scripts/init-system.sh

start:
	@echo "🚀 Starting services..."
	@docker-compose up -d
	@echo "✅ Services started"

stop:
	@echo "🛑 Stopping services..."
	@docker-compose down
	@echo "✅ Services stopped"

restart:
	@echo "🔄 Restarting services..."
	@docker-compose restart
	@echo "✅ Services restarted"

logs:
	@docker-compose logs -f

logs-backend:
	@docker-compose logs -f backend

logs-ai:
	@docker-compose logs -f ai-agent

logs-frontend:
	@docker-compose logs -f frontend

logs-db:
	@docker-compose logs -f postgres

health:
	@bash scripts/check-health.sh

test:
	@echo "🧪 Running backend tests..."
	@docker-compose exec backend pytest tests/ -v

clean:
	@echo "🧹 Cleaning up..."
	@docker-compose down -v
	@echo "✅ Cleanup complete"

backup:
	@echo "💾 Creating database backup..."
	@mkdir -p backups
	@docker-compose exec -T postgres pg_dump -U energydefense energy_defense | gzip > backups/backup_$(shell date +%Y%m%d_%H%M%S).sql.gz
	@echo "✅ Backup created in backups/"

build:
	@echo "🔨 Building Docker images..."
	@docker-compose build
	@echo "✅ Build complete"

rebuild:
	@echo "🔨 Rebuilding Docker images..."
	@docker-compose build --no-cache
	@echo "✅ Rebuild complete"

ps:
	@docker-compose ps

shell-backend:
	@docker-compose exec backend /bin/bash

shell-db:
	@docker-compose exec postgres psql -U energydefense energy_defense
