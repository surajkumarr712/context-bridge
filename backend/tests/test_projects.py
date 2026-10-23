"""API behavior tests for projects."""

from uuid import UUID

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


def test_project_name_cannot_be_blank(client: TestClient) -> None:
    response = client.post("/api/v1/projects", json={"name": "   "})

    assert response.status_code == 422

