import os
import sys

from fastapi.testclient import TestClient


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.main import app


client = TestClient(app)


def test_logout_returns_success_response() -> None:
    response = client.post("/api/v1/logout")

    assert response.status_code == 200

    body = response.json()
    assert body["code"] == 200
    assert body["message"] == "退出登录成功"

