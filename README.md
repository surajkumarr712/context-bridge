# ContextBridge

ContextBridge is a local-first memory layer for moving useful project context
between AI assistants. The user owns the data, reviews what is remembered, and
chooses what is shared.

## Local-only architecture

```text
React UI -> FastAPI -> PostgreSQL + pgvector
                  \-> Ollama local LLM

Prometheus -> Grafana
```

The first milestone contains only the FastAPI service and its first automated
test. We will add each remaining component as a separate learning milestone.

## Local development commands

The Makefile provides short, consistent commands for everyday work:

```bash
make help
make setup
make test
make up
make ps
make down
```

Every Make target expands to ordinary commands. The equivalent commands are:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r backend/requirements-dev.txt
.venv/bin/pytest
docker compose up -d database
.venv/bin/alembic upgrade head
.venv/bin/uvicorn app.main:app --app-dir backend --reload
```

Open <http://127.0.0.1:8000/health> while the server is running.

## Local Kubernetes Ingress

The local kind cluster uses Traefik as its Ingress controller. Install the
controller, apply the ContextBridge route, and expose it to the laptop:

```bash
helm repo add traefik https://traefik.github.io/charts
helm repo update
make ingress-install
make ingress-apply
make ingress-status
make ingress-forward
```

Keep `make ingress-forward` running, then use another terminal:

```bash
curl http://contextbridge.localhost:8080/health
```

The request travels through Traefik, the `contextbridge-api` Ingress, the
ClusterIP Service, and finally one of the API Pods.

## Prometheus and Grafana

The API publishes Prometheus-format metrics at `/metrics`. The local
`kube-prometheus-stack` installation adds Prometheus Operator, Prometheus,
Grafana, kube-state-metrics, and node-exporter.

After changing the API code, rebuild and reload the image into kind:

```bash
make k8s-image
make k8s-load-image
make k8s-rollout
```

Install the monitoring stack and its ContextBridge configuration:

```bash
make monitoring-install
make monitoring-apply
make monitoring-status
```

Open Prometheus:

```bash
make prometheus-forward
# http://127.0.0.1:9090
```

Open Grafana in another terminal:

```bash
make grafana-password
make grafana-forward
# http://127.0.0.1:3000 (username: admin)
```

Grafana automatically loads the `ContextBridge API` dashboard from the
dashboard ConfigMap.

## Local SonarQube analysis

SonarQube performs static analysis while pytest-cov supplies test coverage.
Start the local server:

```bash
make sonar-up
make sonar-status
```

Open <http://127.0.0.1:9000>, sign in with the initial local credentials
`admin` / `admin`, change the password, and generate a user token. Then run:

```bash
export SONAR_TOKEN='your-generated-token'
make sonar-scan
```

The token is passed through the environment and must never be committed. The
scanner reads `sonar-project.properties` and uploads its result to the local
SonarQube server.

