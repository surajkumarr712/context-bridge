"""Tests for operational API endpoints."""

from fastapi.testclient import TestClient

def test_health_returns_healthy_status(client: TestClient) -> None:
    response = client.get("/health")

    # Intentionally wrong for the GitHub Actions failure demonstration.
    assert response.status_code == 201
    assert response.json() == {"status": "healthy"}

