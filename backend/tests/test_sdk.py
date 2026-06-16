"""Tests for SDK endpoints with authentication."""

from fastapi.testclient import TestClient


def test_get_sdk_config_no_auth(client: TestClient):
    """Test getting SDK config without authentication."""
    response = client.get("/api/sdk/config")

    assert response.status_code == 401


def test_get_sdk_config_with_auth(client: TestClient, sample_api_key):
    """Test getting SDK config with valid API key."""
    _, plain_key = sample_api_key

    response = client.get(
        "/api/sdk/config",
        headers={"X-API-KEY": plain_key}
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_sdk_config_with_invalid_auth(client: TestClient):
    """Test getting SDK config with invalid API key."""
    response = client.get(
        "/api/sdk/config",
        headers={"X-API-KEY": "invalid_key"}
    )

    assert response.status_code == 403


def test_register_device(client: TestClient, sample_api_key):
    """Test device registration."""
    _, plain_key = sample_api_key

    response = client.post(
        "/api/sdk/register",
        headers={"X-API-KEY": plain_key},
        json={
            "deviceId": "test_device_001",
            "appVersion": "1.0.0",
            "androidVersion": "10",
            "internetMode": "wifi"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["device_id"] == "test_device_001"
    assert data["app_version"] == "1.0.0"


def test_register_device_no_auth(client: TestClient):
    """Test device registration without authentication."""
    response = client.post(
        "/api/sdk/register",
        json={
            "deviceId": "test_device_002",
            "appVersion": "1.0.0",
            "internetMode": "wifi"
        }
    )

    assert response.status_code == 401


def test_log_intercept(client: TestClient, sample_api_key, sample_device, sample_rule):
    """Test logging an interception event."""
    _, plain_key = sample_api_key

    response = client.post(
        "/api/sdk/log-intercept",
        headers={"X-API-KEY": plain_key},
        json={
            "deviceId": sample_device.device_id,
            "ruleId": sample_rule.id,
            "endpoint": "/api/test",
            "requestData": {"test": "data"},
            "responseMockData": {"result": "mocked"}
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"


def test_log_intercept_no_auth(client: TestClient):
    """Test logging interception without authentication."""
    response = client.post(
        "/api/sdk/log-intercept",
        json={
            "deviceId": "test_device",
            "ruleId": "test_rule",
            "endpoint": "/api/test",
            "responseMockData": {}
        }
    )

    assert response.status_code == 401


def test_log_call(client: TestClient, sample_api_key, sample_device):
    """Test logging an API call."""
    _, plain_key = sample_api_key

    response = client.post(
        "/api/sdk/log-call",
        headers={"X-API-KEY": plain_key},
        json={
            "deviceId": sample_device.device_id,
            "endpoint": "/api/users",
            "method": "GET",
            "wasIntercepted": True,
            "responseTimeMs": 150
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"


def test_log_call_no_auth(client: TestClient):
    """Test logging call without authentication."""
    response = client.post(
        "/api/sdk/log-call",
        json={
            "deviceId": "test_device",
            "endpoint": "/api/test",
            "method": "GET"
        }
    )

    assert response.status_code == 401


def test_list_devices(client: TestClient, sample_api_key, sample_device):
    """Test listing devices for authenticated API key."""
    _, plain_key = sample_api_key

    response = client.get(
        "/api/sdk/devices",
        headers={"X-API-KEY": plain_key}
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
