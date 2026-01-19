import os
import sys

from fastapi.testclient import TestClient


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.main import app
from app.core.security import get_password_hash
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


def create_user(username: str, password: str) -> None:
    db = SessionLocal()
    try:
        user = User(
            username=username,
            email=f"{username}@example.com",
            hashed_password=get_password_hash(password),
        )
        db.add(user)
        db.commit()
    finally:
        db.close()


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


def test_login_with_registered_user_uses_database():
    clear_users()
    username = "db_login_user"
    password = "DbPass1234"
    create_user(username, password)

    response = client.post(
        "/api/v1/login",
        json={"username": username, "password": password},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 200
    assert "data" in body
    assert "access_token" in body["data"]


def test_login_with_registered_user_using_email_or_phone():
    clear_users()
    username = "db_login_user3"
    password = "DbPass9999"
    db = SessionLocal()
    try:
        user = User(
            username=username,
            email="db_login_user3@example.com",
            phone="13800009999",
            hashed_password=get_password_hash(password),
        )
        db.add(user)
        db.commit()
    finally:
        db.close()

    for identifier in [username, "db_login_user3@example.com", "13800009999"]:
        response = client.post(
            "/api/v1/login",
            json={"username": identifier, "password": password},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 200
        assert "access_token" in body["data"]


def test_login_with_registered_user_wrong_password_returns_401():
    clear_users()
    username = "db_login_user2"
    password = "DbPass5678"
    create_user(username, password)

    response = client.post(
        "/api/v1/login",
        json={"username": username, "password": "wrong"},
    )

    assert response.status_code == 401
    body = response.json()
    assert body["detail"]["code"] == 401
    assert body["detail"]["message"] == "用户名或密码错误"


def test_login_after_register_persists_user_in_database():
    clear_users()

    register_payload = {
        "username": "registered_user",
        "password": "RegUser123",
        "confirm_password": "RegUser123",
        "email": "registered_user@example.com",
        "real_name": "注册用户",
        "id_type": "id_card",
        "id_number": "110101199001010033",
        "phone": "13800000002",
        "user_type": "adult",
    }

    register_response = client.post("/api/v1/register", json=register_payload)
    assert register_response.status_code == 200

    login_response = client.post(
        "/api/v1/login",
        json={"username": "registered_user", "password": "RegUser123"},
    )

    assert login_response.status_code == 200
    body = login_response.json()
    assert body["code"] == 200
    assert "access_token" in body["data"]
