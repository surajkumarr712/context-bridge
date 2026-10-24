"""Prometheus metrics for the ContextBridge HTTP API."""

from time import perf_counter

from fastapi import Request, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

HTTP_REQUESTS = Counter(
    "contextbridge_http_requests_total",
    "Total HTTP requests handled by ContextBridge.",
    ("method", "path", "status"),
)

HTTP_REQUEST_DURATION = Histogram(
    "contextbridge_http_request_duration_seconds",
    "Time spent handling ContextBridge HTTP requests.",
    ("method", "path"),
)


class PrometheusMiddleware(BaseHTTPMiddleware):
    """Record request count, status, and duration for every API route."""

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        if request.url.path == "/metrics":
            return await call_next(request)

        started_at = perf_counter()
        response = await call_next(request)
        route = request.scope.get("route")
        path = getattr(route, "path", request.url.path)

        HTTP_REQUESTS.labels(
            method=request.method,
            path=path,
            status=str(response.status_code),
        ).inc()
        HTTP_REQUEST_DURATION.labels(
            method=request.method,
            path=path,
        ).observe(perf_counter() - started_at)
        return response


def prometheus_metrics() -> Response:
    """Return the current process and application metrics."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
