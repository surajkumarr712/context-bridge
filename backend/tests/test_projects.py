"""API behavior tests for projects."""

from uuid import UUID

import pytest
from fastapi.testclient import TestClient


def test_project_list_starts_empty(client: TestClient) -> None:
    response = client.get("/api/v1/projects")

    assert response.status_code == 200
    assert response.json() == []


def test_create_project_returns_generated_fields(client: TestClient) -> None:
    response = client.post(
        "/api/v1/projects",
        json={
            "name": "ContextBridge",
            "description": "Portable context for local AI tools",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "ContextBridge"
    assert body["description"] == "Portable context for local AI tools"
    assert UUID(body["id"])
    assert body["created_at"].endswith("Z")


def test_created_project_appears_in_list(client: TestClient) -> None:
    client.post("/api/v1/projects", json={"name": "Interview preparation"})

    response = client.get("/api/v1/projects")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "Interview preparation"


@pytest.mark.parametrize(
    "invalid_name",
    ["", "   ", "a" * 101],
    ids=["empty", "whitespace-only", "longer-than-100-characters"],
)
def test_project_name_rejects_invalid_values(
    client: TestClient,
    invalid_name: str,
) -> None:
    response = client.post("/api/v1/projects", json={"name": invalid_name})

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "name"]


def test_project_name_is_trimmed(client: TestClient) -> None:
    response = client.post(
        "/api/v1/projects",
        json={"name": "  ContextBridge  "},
    )

    assert response.status_code == 201
    assert response.json()["name"] == "ContextBridge"

