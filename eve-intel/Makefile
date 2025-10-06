.PHONY: help install dev up down logs test fmt lint clean seed migrate

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install dependencies with Poetry
	poetry install

dev: ## Run API in development mode (local)
	poetry run uvicorn eve_intel.api.main:app --reload --host 0.0.0.0 --port 8000

up: ## Start all services with docker-compose
	docker-compose up -d

down: ## Stop all services
	docker-compose down

logs: ## Show logs from all services
	docker-compose logs -f

test: ## Run tests with coverage
	poetry run pytest -v

fmt: ## Format code with black and ruff
	poetry run black eve_intel tests
	poetry run ruff check --fix eve_intel tests

lint: ## Lint code with ruff and mypy
	poetry run ruff check eve_intel tests
	poetry run black --check eve_intel tests
	poetry run mypy eve_intel

clean: ## Clean cache and build artifacts
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete
	find . -type d -name .pytest_cache -exec rm -rf {} +
	find . -type d -name .mypy_cache -exec rm -rf {} +
	rm -rf htmlcov .coverage

seed: ## Seed database with initial data
	poetry run python scripts/seed.py

migrate: ## Run database migrations
	poetry run alembic upgrade head

build: ## Build Docker images
	docker-compose build

rebuild: ## Rebuild Docker images from scratch
	docker-compose build --no-cache

shell: ## Open a shell in the API container
	docker-compose exec api bash

psql: ## Connect to PostgreSQL database
	docker-compose exec postgres psql -U eve_intel_user -d eve_intel

redis-cli: ## Connect to Redis CLI
	docker-compose exec redis redis-cli

find-arb: ## Run arbitrage finder CLI
	poetry run python -m eve_intel.cli find-arb

pre-commit: ## Install pre-commit hooks
	poetry run pre-commit install

pre-commit-run: ## Run pre-commit on all files
	poetry run pre-commit run --all-files
