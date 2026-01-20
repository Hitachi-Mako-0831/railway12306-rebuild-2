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


def create_user_for_profile() -> tuple[str, str]:
    username = "profile_user"
    password = "ProfilePass123"
    db = SessionLocal()
    try:
        user = User(
            username=username,
            email="profile@example.com",
            hashed_password=get_password_hash(password),
            real_name="李四",
            id_type="id_card",
            id_number="110101199001010022",
            phone="13900000000",
            user_type="成人",
        )
        db.add(user)
        db.commit()
    finally:
        db.close()
    return username, password


def test_get_profile_returns_user_fields_for_logged_in_user() -> None:
    clear_users()
    username, password = create_user_for_profile()

    login_response = client.post(
        "/api/v1/login",
        json={"username": username, "password": password},
    )
    assert login_response.status_code == 200
    token = login_response.json()["data"]["access_token"]

    response = client.get(
        "/api/v1/users/profile",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200

    body = response.json()
    assert body["code"] == 200
    data = body["data"]

    for field in [
        "username",
        "real_name",
        "country",
        "id_type",
        "id_number",
        "phone",
        "email",
        "user_type",
    ]:
        assert field in data
    assert data["username"] == username
    assert data["real_name"] == "李四"
