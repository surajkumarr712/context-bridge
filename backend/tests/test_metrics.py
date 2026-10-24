"""Tests for the Prometheus metrics endpoint."""

from fastapi.testclient import TestClient


def test_metrics_exposes_request_count(client: TestClient) -> None:
    client.get("/health")

    response = client.get("/metrics")

    assert response.status_code == 200
    assert "contextbridge_http_requests_total" in response.text
    assert 'path="/health"' in response.text
    assert 'status="200"' in response.text


def test_metrics_is_hidden_from_openapi(client: TestClient) -> None:
    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert "/metrics" not in response.json()["paths"]
