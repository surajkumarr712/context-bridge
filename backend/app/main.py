"""Entry point for the ContextBridge HTTP API."""

from fastapi import FastAPI

from app.metrics import PrometheusMiddleware, prometheus_metrics
from app.routes.projects import router as projects_router

app = FastAPI(
    title="ContextBridge API",
    description="A local-first memory layer for AI assistants.",
    version="0.1.0",
)

app.add_middleware(PrometheusMiddleware)
app.include_router(projects_router, prefix="/api/v1")
app.add_api_route(
    "/metrics",
    prometheus_metrics,
    methods=["GET"],
    include_in_schema=False,
)


@app.get("/health", tags=["operations"])
def health() -> dict[str, str]:
    """Report whether the API process is running."""
    return {"status": "healthy"}

