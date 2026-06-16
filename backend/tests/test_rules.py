"""Tests for rule endpoints."""

from fastapi.testclient import TestClient


def test_create_rule(client: TestClient):
    """Test creating a new rule."""
    response = client.post(
        "/api/v1/rules",
        json={
            "name": "User Profile Mock",
            "url_pattern": "/user/profile",
            "status_code": 200,
            "delay_ms": 0,
            "mode": "always",
            "mock_data": {"id": 1, "name": "Test User"}
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "User Profile Mock"
    assert data["url_pattern"] == "/user/profile"
    assert data["status_code"] == 200
    assert data["delay_ms"] == 0
    assert data["mode"] == "always"
    assert data["mock_data"]["id"] == 1
    assert data["is_enabled"] is True


def test_create_rule_invalid_url_pattern(client: TestClient):
    """Test creating a rule with invalid URL pattern."""
    response = client.post(
        "/api/v1/rules",
        json={
            "name": "Invalid Rule",
            "url_pattern": "invalid",  # Doesn't start with /
            "status_code": 200,
            "delay_ms": 0,
            "mode": "always",
            "mock_data": {}
        }
    )

    assert response.status_code == 400


def test_list_rules(client: TestClient, sample_rule):
    """Test listing all rules."""
    response = client.get("/api/v1/rules")

    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1


def test_list_rules_enabled_only(client: TestClient, sample_rule):
    """Test listing only enabled rules."""
    response = client.get("/api/v1/rules?enabled_only=true")

    assert response.status_code == 200
    data = response.json()
    assert all(rule["is_enabled"] for rule in data)


def test_get_rule(client: TestClient, sample_rule):
    """Test getting a specific rule."""
    response = client.get(f"/api/v1/rules/{sample_rule.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == sample_rule.id


def test_get_nonexistent_rule(client: TestClient):
    """Test getting a non-existent rule."""
    response = client.get("/api/v1/rules/nonexistent-id")

    assert response.status_code == 404


def test_update_rule(client: TestClient, sample_rule):
    """Test updating a rule."""
    response = client.put(
        f"/api/v1/rules/{sample_rule.id}",
        json={"name": "Updated Rule Name"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Rule Name"


def test_update_rule_disable(client: TestClient, sample_rule):
    """Test disabling a rule."""
    response = client.put(
        f"/api/v1/rules/{sample_rule.id}",
        json={"is_enabled": False}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["is_enabled"] is False


def test_update_nonexistent_rule(client: TestClient):
    """Test updating a non-existent rule."""
    response = client.put(
        "/api/v1/rules/nonexistent-id",
        json={"name": "Updated"}
    )

    assert response.status_code == 404


def test_delete_rule(client: TestClient, sample_rule):
    """Test deleting a rule."""
    response = client.delete(f"/api/v1/rules/{sample_rule.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"


def test_delete_nonexistent_rule(client: TestClient):
    """Test deleting a non-existent rule."""
    response = client.delete("/api/v1/rules/nonexistent-id")

    assert response.status_code == 404
