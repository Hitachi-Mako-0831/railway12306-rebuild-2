import os
import sys

from fastapi.testclient import TestClient


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.main import app


client = TestClient(app)


def test_password_recovery_reset_success() -> None:
    response = client.post(
        "/api/v1/auth/password/recovery/reset",
        json={"username": "demo_user", "email": "demo@example.com"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert "重置链接" in data["message"]


def test_password_recovery_reset_missing_fields() -> None:
    response = client.post(
        "/api/v1/auth/password/recovery/reset",
        json={"username": "", "email": ""},
    )
    assert response.status_code == 400
    data = response.json()
    assert data["code"] == 400
    assert "必填" in data["message"]
