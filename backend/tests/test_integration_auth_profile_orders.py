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
from app.models.train import Train


client = TestClient(app)


def ensure_demo_user_and_train():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == "integration_user").first()
        if not user:
            user = User(
                username="integration_user",
                email="integration_user@example.com",
                hashed_password=get_password_hash("Integration123"),
            )
            db.add(user)
            db.commit()
        train = db.query(Train).first()
        if not train:
            train = Train(
                train_number="INT1001",
                from_station_id=1,
                to_station_id=1,
                departure_time="08:00:00",
                arrival_time="12:00:00",
                duration_minutes=240,
            )
            db.add(train)
            db.commit()
        db.refresh(user)
        db.refresh(train)
        return user, train
    finally:
        db.close()


def test_full_flow_register_login_profile_and_order():
    db = SessionLocal()
    try:
        db.query(User).filter(User.username == "integration_user").delete()
        db.commit()
    finally:
        db.close()

    register_payload = {
        "username": "integration_user",
        "password": "Integration123",
        "confirm_password": "Integration123",
        "email": "integration_user@example.com",
        "real_name": "集成用户",
        "id_type": "id_card",
        "id_number": "110101199001019999",
        "phone": "13800009999",
        "user_type": "adult",
    }

    register_response = client.post("/api/v1/register", json=register_payload)
    assert register_response.status_code == 200
    body = register_response.json()
    assert body["code"] == 200

    login_response = client.post(
        "/api/v1/login",
        json={"username": "integration_user", "password": "Integration123"},
    )
    assert login_response.status_code == 200
    login_body = login_response.json()
    assert login_body["code"] == 200
    token = login_body["data"]["access_token"]

    profile_response = client.get(
        "/api/v1/users/profile",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert profile_response.status_code == 200
    profile_body = profile_response.json()
    assert profile_body["code"] == 200
    profile_data = profile_body["data"]
    assert profile_data["username"] == "integration_user"
    assert profile_data["email"] == "integration_user@example.com"

    user, train = ensure_demo_user_and_train()

    order_payload = {
        "train_id": train.id,
        "departure_date": "2024-01-01",
        "total_price": 100.0,
        "items": [
            {
                "passenger_name": "集成用户",
                "passenger_id_card": "110101199001019999",
                "seat_type": "second_class",
                "price": 100.0,
            }
        ],
    }

    create_order_response = client.post(
        "/api/v1/orders/", json=order_payload, headers={"Authorization": f"Bearer {token}"}
    )
    assert create_order_response.status_code == 200
    created_order = create_order_response.json()
    assert created_order["total_price"] == 100.0
    assert len(created_order["items"]) == 1

    order_id = created_order["id"]

    pay_response = client.post(
        f"/api/v1/orders/{order_id}/pay",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert pay_response.status_code == 200
    paid_order = pay_response.json()
    assert paid_order["status"] == "paid"

    cancel_response = client.post(
        f"/api/v1/orders/{order_id}/cancel",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert cancel_response.status_code in (200, 400)
    if cancel_response.status_code == 200:
        cancelled_order = cancel_response.json()
        assert cancelled_order["status"] == "cancelled"
