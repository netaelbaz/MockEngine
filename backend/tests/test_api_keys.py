"""Tests for API key endpoints."""

from fastapi.testclient import TestClient


def test_create_api_key(client: TestClient):
    """Test creating a new API key."""
    response = client.post(
        "/api/v1/api-keys",
        json={"key_name": "My Test Key"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "My Test Key"
    assert len(data["api_key"]) == 64  # 32 bytes = 64 hex chars
    assert data["is_active"] is True
    assert "id" in data
    assert "created_at" in data


def test_create_api_key_invalid_name(client: TestClient):
    """Test creating an API key with invalid name."""
    response = client.post(
        "/api/v1/api-keys",
        json={"key_name": ""}  # Empty name
    )

    assert response.status_code == 422  # Validation error


def test_list_api_keys(client: TestClient, sample_api_key):
    """Test listing all API keys."""
    response = client.get("/api/v1/api-keys")

    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    # API keys should be hidden in list
    assert data[0]["api_key"] == "***HIDDEN***"


def test_delete_api_key(client: TestClient, sample_api_key):
    """Test deleting an API key."""
    db_key, _ = sample_api_key

    response = client.delete(f"/api/v1/api-keys/{db_key.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"


def test_delete_nonexistent_api_key(client: TestClient):
    """Test deleting a non-existent API key."""
    response = client.delete("/api/v1/api-keys/nonexistent-id")

    assert response.status_code == 404


def test_update_api_key_status(client: TestClient, sample_api_key):
    """Test updating API key active status."""
    db_key, _ = sample_api_key

    # Disable the key
    response = client.patch(
        f"/api/v1/api-keys/{db_key.id}/status",
        params={"is_active": False}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["is_active"] is False


def test_update_nonexistent_api_key_status(client: TestClient):
    """Test updating status of non-existent API key."""
    response = client.patch(
        "/api/v1/api-keys/nonexistent-id/status",
        params={"is_active": False}
    )

    assert response.status_code == 404
