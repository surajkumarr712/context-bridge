.DEFAULT_GOAL := help

PYTHON ?= python3
VENV ?= .venv
VENV_PYTHON := $(VENV)/bin/python
VENV_PIP := $(VENV_PYTHON) -m pip
DEPS_STAMP := $(VENV)/.dependencies-installed
COMPOSE ?= docker compose
SONAR_COMPOSE ?= docker compose -f compose.sonarqube.yaml
API_PORT ?= 8001
KUBE_CONTEXT ?= kind-contextbridge
MONITORING_CHART_VERSION ?= 92.10.0

.PHONY: help setup install test test-verbose coverage ci compose-config build up down restart ps logs api-logs database-logs migrate k8s-image k8s-load-image k8s-rollout ingress-install ingress-apply ingress-status ingress-forward monitoring-install monitoring-apply monitoring-status prometheus-forward grafana-forward grafana-password sonar-up sonar-down sonar-status sonar-logs sonar-scan

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

coverage: $(DEPS_STAMP) ## Run tests and create the XML report consumed by SonarQube.
	$(VENV_PYTHON) -m pytest \
		--cov=backend/app \
		--cov-report=term-missing \
		--cov-report=xml:coverage.xml

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

k8s-image: ## Build the API image used by the local Kubernetes cluster.
	docker build --tag context-bridge-api:local backend

k8s-load-image: ## Copy the local API image into the kind node.
	kind load docker-image context-bridge-api:local --name contextbridge

k8s-rollout: ## Restart the API Pods so they use the newly loaded image.
	kubectl rollout restart deployment/contextbridge-api --namespace contextbridge --context $(KUBE_CONTEXT)
	kubectl rollout status deployment/contextbridge-api --namespace contextbridge --context $(KUBE_CONTEXT)

ingress-install: ## Install the Traefik Ingress controller in the local cluster.
	helm upgrade --install traefik traefik/traefik \
		--version 42.1.3 \
		--namespace traefik \
		--create-namespace \
		--values k8s/ingress/traefik-values.yaml \
		--wait

ingress-apply: ## Create the ContextBridge Ingress routing rule.
	kubectl apply --context kind-contextbridge -f k8s/base/api-ingress.yaml

ingress-status: ## Show the controller, IngressClass, and ContextBridge Ingress.
	kubectl get pods,service --namespace traefik --context kind-contextbridge
	kubectl get ingressclass,ingress --all-namespaces --context kind-contextbridge

ingress-forward: ## Expose Traefik at http://contextbridge.localhost:8080 locally.
	kubectl port-forward --namespace traefik --context kind-contextbridge service/traefik 8080:80

monitoring-install: ## Install Prometheus Operator, Prometheus, and Grafana.
	helm upgrade --install monitoring \
		oci://ghcr.io/prometheus-community/charts/kube-prometheus-stack \
		--version $(MONITORING_CHART_VERSION) \
		--namespace monitoring \
		--create-namespace \
		--values k8s/monitoring/values.yaml \
		--wait \
		--timeout 10m

monitoring-apply: ## Add the API scrape configuration and Grafana dashboard.
	kubectl apply --context $(KUBE_CONTEXT) -f k8s/base/api-service-monitor.yaml
	kubectl apply --context $(KUBE_CONTEXT) -f k8s/monitoring/contextbridge-dashboard.yaml

monitoring-status: ## Show monitoring Pods, Services, and the API ServiceMonitor.
	kubectl get pods,service --namespace monitoring --context $(KUBE_CONTEXT)
	kubectl get servicemonitor --all-namespaces --context $(KUBE_CONTEXT)

prometheus-forward: ## Expose Prometheus at http://127.0.0.1:9090 locally.
	kubectl port-forward --namespace monitoring --context $(KUBE_CONTEXT) service/monitoring-kube-prometheus-prometheus 9090:9090

grafana-forward: ## Expose Grafana at http://127.0.0.1:3000 locally.
	kubectl port-forward --namespace monitoring --context $(KUBE_CONTEXT) service/monitoring-grafana 3000:80

grafana-password: ## Print the generated local Grafana admin password.
	@kubectl get secret monitoring-grafana --namespace monitoring --context $(KUBE_CONTEXT) --output jsonpath='{.data.admin-password}' | base64 --decode
	@printf '\n'

sonar-up: ## Start the local SonarQube Community Build server.
	$(SONAR_COMPOSE) up -d sonarqube

sonar-down: ## Stop SonarQube while preserving its local data volumes.
	$(SONAR_COMPOSE) down

sonar-status: ## Show the local SonarQube container status.
	$(SONAR_COMPOSE) ps

sonar-logs: ## Follow SonarQube server logs until interrupted.
	$(SONAR_COMPOSE) logs -f sonarqube

sonar-scan: coverage ## Analyze ContextBridge and upload the result to local SonarQube.
	@test -n "$(SONAR_TOKEN)" || (printf 'SONAR_TOKEN is required. Generate it in SonarQube and export it first.\n'; exit 1)
	$(SONAR_COMPOSE) --profile tools run --rm --no-deps sonar-scanner
