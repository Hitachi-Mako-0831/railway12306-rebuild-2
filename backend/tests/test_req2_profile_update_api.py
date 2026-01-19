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


def create_user() -> tuple[str, str]:
    username = "update_profile_user"
    password = "UpdateProfile123"
    db = SessionLocal()
    try:
        user = User(
            username=username,
            email="old@example.com",
            hashed_password=get_password_hash(password),
            real_name="王五",
            id_type="id_card",
            id_number="110101199001010033",
            phone="13600000000",
            user_type="成人",
        )
        db.add(user)
        db.commit()
    finally:
        db.close()
    return username, password


def test_update_profile_persists_changes() -> None:
    clear_users()
    username, password = create_user()

    login_response = client.post(
        "/api/v1/login",
        json={"username": username, "password": password},
    )
    assert login_response.status_code == 200
    token = login_response.json()["data"]["access_token"]

    update_payload = {
        "real_name": "新王五",
        "phone": "13700000000",
        "email": "new@example.com",
        "user_type": "学生",
    }

    update_response = client.put(
        "/api/v1/users/profile",
        json=update_payload,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert update_response.status_code == 200
    body = update_response.json()
    assert body["code"] == 200
    data = body["data"]
    assert data["real_name"] == "新王五"
    assert data["phone"] == "13700000000"
    assert data["email"] == "new@example.com"
    assert data["user_type"] == "学生"

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        assert user is not None
        assert user.real_name == "新王五"
        assert user.phone == "13700000000"
        assert user.email == "new@example.com"
        assert user.user_type == "学生"
    finally:
        db.close()

