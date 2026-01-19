import os
import sys

from fastapi.testclient import TestClient


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.main import app
from app.db.session import SessionLocal
from app.models.user import User


client = TestClient(app)


def clear_users() -> None:
    db = SessionLocal()
    try:
        db.query(User).delete()
        db.commit()
    finally:
        db.close()


def test_register_success_creates_user():
    clear_users()

    payload = {
        "username": "testuser1",
        "password": "abc12345",
        "confirm_password": "abc12345",
        "email": "test1@example.com",
    }

    response = client.post("/api/v1/register", json=payload)

    assert response.status_code == 200

    body = response.json()
    assert body["code"] == 200
    assert body["message"] == "注册成功"
    assert body["data"]["username"] == "testuser1"

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == "testuser1").first()
        assert user is not None
        assert user.hashed_password != "abc12345"
    finally:
        db.close()


def test_register_duplicate_username_returns_error():
    clear_users()

    db = SessionLocal()
    try:
        user = User(username="exists_user", email="exists@example.com", hashed_password="x")
        db.add(user)
        db.commit()
    finally:
        db.close()

    payload = {
        "username": "exists_user",
        "password": "abc12345",
        "confirm_password": "abc12345",
        "email": "another@example.com",
    }

    response = client.post("/api/v1/register", json=payload)

    assert response.status_code == 400

    body = response.json()
    assert body["code"] == 400
    assert "用户名已存在" in body["message"]

