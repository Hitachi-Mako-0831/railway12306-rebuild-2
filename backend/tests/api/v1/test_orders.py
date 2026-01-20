from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import get_password_hash, create_access_token
from app.models.user import User
from app.models.order import Order
from app.models.train import Train

API_V1_STR = "/api/v1"


def create_user(db: Session, username: str) -> User:
    user = db.query(User).filter(User.username == username).first()
    if user:
        return user

    password = "OrderUser123"
    user = User(
        username=username,
        email=f"{username}@example.com",
        hashed_password=get_password_hash(password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def auth_header_for(user: User) -> dict[str, str]:
    token = create_access_token({"sub": user.username})
    return {"Authorization": f"Bearer {token}"}


def test_create_order_uses_current_user(client: TestClient, db: Session):
    user = create_user(db, "order_owner")
    headers = auth_header_for(user)

    data = {
        "train_id": 1,
        "departure_date": "2023-12-12",
        "total_price": 100.0,
        "items": [
            {
                "passenger_name": "Test Passenger",
                "passenger_id_card": "123456789012345678",
                "seat_type": "second_class",
                "price": 100.0,
            }
        ],
    }
    response = client.post(f"{API_V1_STR}/orders/", json=data, headers=headers)
    assert response.status_code == 200
    content = response.json()
    assert content["total_price"] == 100.0
    assert len(content["items"]) == 1
    assert "id" in content

    order_id = content["id"]
    order = db.query(Order).filter(Order.id == order_id).first()
    assert order is not None
    assert order.user_id is not None


def test_orders_are_scoped_by_user(client: TestClient, db: Session):
    db.query(Order).delete()
    db.commit()

    user1 = create_user(db, "order_user1")
    user2 = create_user(db, "order_user2")

    headers1 = auth_header_for(user1)
    headers2 = auth_header_for(user2)

    payload = {
        "train_id": 1,
        "departure_date": "2023-12-12",
        "total_price": 50.0,
        "items": [
            {
                "passenger_name": "P1",
                "passenger_id_card": "111111111111111111",
                "seat_type": "second_class",
                "price": 50.0,
            }
        ],
    }

    r1 = client.post(f"{API_V1_STR}/orders/", json=payload, headers=headers1)
    assert r1.status_code == 200
    r2 = client.post(f"{API_V1_STR}/orders/", json=payload, headers=headers2)
    assert r2.status_code == 200

    list1 = client.get(f"{API_V1_STR}/orders/", headers=headers1)
    assert list1.status_code == 200
    data1 = list1.json()
    assert len(data1) == 1
    assert data1[0]["user_id"] != 0

    list2 = client.get(f"{API_V1_STR}/orders/", headers=headers2)
    assert list2.status_code == 200
    data2 = list2.json()
    assert len(data2) == 1
    assert data1[0]["id"] != data2[0]["id"]


def test_user_cannot_access_other_users_order_detail(client: TestClient, db: Session):
    db.query(Order).delete()
    db.commit()

    owner = create_user(db, "order_owner_detail")
    other = create_user(db, "order_other_detail")

    headers_owner = auth_header_for(owner)
    headers_other = auth_header_for(other)

    payload = {
        "train_id": 1,
        "departure_date": "2023-12-12",
        "total_price": 80.0,
        "items": [
            {
                "passenger_name": "Owner",
                "passenger_id_card": "222222222222222222",
                "seat_type": "second_class",
                "price": 80.0,
            }
        ],
    }

    create_resp = client.post(f"{API_V1_STR}/orders/", json=payload, headers=headers_owner)
    assert create_resp.status_code == 200
    order_id = create_resp.json()["id"]

    ok_resp = client.get(f"{API_V1_STR}/orders/{order_id}", headers=headers_owner)
    assert ok_resp.status_code == 200

    forbidden_resp = client.get(f"{API_V1_STR}/orders/{order_id}", headers=headers_other)
    assert forbidden_resp.status_code == 404


def test_create_order_validation_error_returns_structured_detail(client: TestClient, db: Session):
    user = create_user(db, "order_validation_user")
    headers = auth_header_for(user)

    data = {
        "train_id": 1,
        "total_price": 100.0,
        "items": [
            {
                "passenger_name": "Test Passenger",
                "passenger_id_card": "123456789012345678",
                "seat_type": "second_class",
                "price": 100.0,
            }
        ],
    }

    response = client.post(f"{API_V1_STR}/orders/", json=data, headers=headers)
    assert response.status_code == 422
    body = response.json()
    assert "detail" in body
    assert isinstance(body["detail"], list)


def test_order_detail_includes_train_info(client: TestClient, db: Session):
    user = create_user(db, "order_train_info_user")
    headers = auth_header_for(user)

    train = db.query(Train).first()
    assert train is not None

    data = {
        "train_id": train.id,
        "departure_date": "2025-12-30",
        "total_price": 120.0,
        "items": [
            {
                "passenger_name": "TrainInfoUser",
                "passenger_id_card": "123456789012345678",
                "seat_type": "second_class",
                "price": 120.0,
            }
        ],
    }

    create_resp = client.post(f"{API_V1_STR}/orders/", json=data, headers=headers)
    assert create_resp.status_code == 200
    order_id = create_resp.json()["id"]

    detail_resp = client.get(f"{API_V1_STR}/orders/{order_id}", headers=headers)
    assert detail_resp.status_code == 200
    body = detail_resp.json()

    assert body["train_id"] == train.id
    assert "train" in body
    train_data = body["train"]
    assert train_data is not None
    assert train_data["id"] == train.id
    assert "train_number" in train_data
    assert "from_station" in train_data
    assert "to_station" in train_data
