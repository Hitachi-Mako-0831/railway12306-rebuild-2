import os
import sys

from fastapi.testclient import TestClient


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.main import app


client = TestClient(app)


def test_login_success_returns_token():
    payload = {"username": "demo_user", "password": "Password123!"}

    response = client.post("/api/v1/login", json=payload)

    assert response.status_code == 200

    body = response.json()
    assert body["code"] == 200
    assert body["message"] == "登录成功"
    assert "data" in body
    assert "access_token" in body["data"]
    assert body["data"]["token_type"] == "bearer"


def test_login_invalid_credentials_returns_401():
    payload = {"username": "demo_user", "password": "wrong"}

    response = client.post("/api/v1/login", json=payload)

    assert response.status_code == 401

    body = response.json()
    assert body["detail"]["code"] == 401
    assert body["detail"]["message"] == "用户名或密码错误"

