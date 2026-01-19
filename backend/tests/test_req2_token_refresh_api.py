import os
import sys

from fastapi.testclient import TestClient


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.main import app


client = TestClient(app)


def test_refresh_with_valid_token_returns_new_access_token() -> None:
    login_response = client.post(
        "/api/v1/login",
        json={"username": "demo_user", "password": "Password123!"},
    )

    assert login_response.status_code == 200
    login_body = login_response.json()
    assert login_body["code"] == 200
    token = login_body["data"]["access_token"]

    refresh_response = client.post(
        "/api/v1/refresh",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert refresh_response.status_code == 200
    body = refresh_response.json()
    assert body["code"] == 200
    assert "data" in body
    assert "access_token" in body["data"]
    assert body["data"]["token_type"] == "bearer"


def test_refresh_with_invalid_token_returns_401() -> None:
    response = client.post(
        "/api/v1/refresh",
        headers={"Authorization": "Bearer invalid-token"},
    )

    assert response.status_code == 401
    body = response.json()
    assert body["detail"]["code"] == 401
    assert body["detail"]["message"] == "无效的令牌"

