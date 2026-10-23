.DEFAULT_GOAL := help

PYTHON ?= python3
VENV ?= .venv
VENV_PYTHON := $(VENV)/bin/python
VENV_PIP := $(VENV_PYTHON) -m pip
DEPS_STAMP := $(VENV)/.dependencies-installed
COMPOSE ?= docker compose
API_PORT ?= 8001

.PHONY: help setup install test test-verbose ci compose-config build up down restart ps logs api-logs database-logs migrate

help: ## Show the available commands.
	@printf "ContextBridge development commands\n\n"
	@awk 'BEGIN {FS = ":.*## "} /^[a-zA-Z0-9_-]+:.*## / {printf "  %-18s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

setup: install ## Create the virtual environment and install dependencies.

install: $(DEPS_STAMP) ## Install or refresh Python dependencies when requirements change.

$(VENV_PYTHON):
	$(PYTHON) -m venv $(VENV)

$(DEPS_STAMP): backend/requirements.txt backend/requirements-dev.txt | $(VENV_PYTHON)
	$(VENV_PIP) install --upgrade pip
	$(VENV_PIP) install -r backend/requirements-dev.txt
	@touch $(DEPS_STAMP)

test: $(DEPS_STAMP) ## Run the complete pytest suite.
	$(VENV_PYTHON) -m pytest

test-verbose: $(DEPS_STAMP) ## Run pytest and display every test name.
	$(VENV_PYTHON) -m pytest -v

ci: test ## Run the same fast validation used by continuous integration.
	$(COMPOSE) config --quiet

compose-config: ## Validate and print the resolved Compose configuration.
	$(COMPOSE) config

build: ## Build the API container image.
	$(COMPOSE) build api

up: ## Build and start the complete application stack.
	API_PORT=$(API_PORT) $(COMPOSE) up -d --build

down: ## Stop the stack while preserving the PostgreSQL volume.
	$(COMPOSE) down

restart: ## Restart existing containers without rebuilding them.
	$(COMPOSE) restart

ps: ## Show Compose container status and health.
	$(COMPOSE) ps

logs: ## Follow logs from every service until interrupted.
	$(COMPOSE) logs -f

api-logs: ## Follow only FastAPI container logs.
	$(COMPOSE) logs -f api

database-logs: ## Follow only PostgreSQL container logs.
	$(COMPOSE) logs -f database

migrate: $(DEPS_STAMP) ## Apply all pending Alembic database migrations.
	$(VENV)/bin/alembic upgrade head
