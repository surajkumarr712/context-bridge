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

