import os
import sys

from fastapi.testclient import TestClient


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.main import app
from app.db.session import SessionLocal
from app.models.user import User
from app.models.passenger import Passenger


client = TestClient(app)


def clear_users() -> None:
    db = SessionLocal()
    try:
        db.query(Passenger).delete()
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
        "real_name": "张三",
        "id_type": "id_card",
        "id_number": "110101199001010011",
        "phone": "13800000000",
        "user_type": "adult",
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
        assert user.real_name == "张三"
        assert user.id_type == "id_card"
        assert user.id_number == "110101199001010011"
        assert user.phone == "13800000000"
        assert user.user_type == "adult"
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
        "real_name": "李四",
        "id_type": "id_card",
        "id_number": "110101199001010022",
        "phone": "13800000001",
        "user_type": "adult",
    }

    response = client.post("/api/v1/register", json=payload)

    assert response.status_code == 400

    body = response.json()
    assert body["code"] == 400
    assert "用户名已存在" in body["message"]
