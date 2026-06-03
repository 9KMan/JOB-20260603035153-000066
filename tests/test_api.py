"""API route tests."""
from fastapi.testclient import TestClient


def test_healthcheck(client: TestClient) -> None:
    response = client.get("/health/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "app" in data
    assert "version" in data


def test_readiness(client: TestClient) -> None:
    response = client.get("/health/ready")
    assert response.status_code == 200
    assert response.json()["status"] == "ready"


def test_create_and_get_item(client: TestClient) -> None:
    payload = {"name": "Widget", "description": "A test widget"}
    create_response = client.post("/api/v1/items/", json=payload)
    assert create_response.status_code == 201
    created = create_response.json()
    assert created["name"] == "Widget"
    assert created["description"] == "A test widget"
    assert "id" in created

    item_id = created["id"]
    get_response = client.get(f"/api/v1/items/{item_id}")
    assert get_response.status_code == 200
    assert get_response.json()["id"] == item_id


def test_list_items(client: TestClient) -> None:
    for i in range(3):
        client.post("/api/v1/items/", json={"name": f"item-{i}"})
    response = client.get("/api/v1/items/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3


def test_update_item(client: TestClient) -> None:
    create = client.post("/api/v1/items/", json={"name": "original"}).json()
    item_id = create["id"]
    update = client.patch(f"/api/v1/items/{item_id}", json={"name": "updated"})
    assert update.status_code == 200
    assert update.json()["name"] == "updated"


def test_delete_item(client: TestClient) -> None:
    create = client.post("/api/v1/items/", json={"name": "to-delete"}).json()
    item_id = create["id"]
    delete = client.delete(f"/api/v1/items/{item_id}")
    assert delete.status_code == 204
    get_after = client.get(f"/api/v1/items/{item_id}")
    assert get_after.status_code == 404


def test_get_missing_item_returns_404(client: TestClient) -> None:
    response = client.get("/api/v1/items/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


def test_blank_name_rejected(client: TestClient) -> None:
    response = client.post("/api/v1/items/", json={"name": "   "})
    assert response.status_code == 422
