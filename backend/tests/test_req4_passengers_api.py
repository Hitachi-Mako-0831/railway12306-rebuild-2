import pytest
import random
import datetime
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import SessionLocal
from app.models.user import User
from app.models.passenger import Passenger
from app.core.security import create_access_token, get_password_hash
from sqlalchemy import text

client = TestClient(app)

@pytest.fixture(autouse=True)
def clean_db():
    db = SessionLocal()
    try:
        db.execute(text("DELETE FROM passengers"))
        db.execute(text("DELETE FROM users"))
        db.commit()
    except Exception as e:
        print(f"Error cleaning DB: {e}")
    finally:
        db.close()

def get_valid_id_card():
    # Generate a valid Chinese ID card
    # 1. Address Code (6 digits)
    addr = "110101"
    
    # 2. Birth Date (8 digits)
    start_date = datetime.date(1980, 1, 1)
    end_date = datetime.date(2000, 12, 31)
    days_between = (end_date - start_date).days
    random_days = random.randrange(days_between)
    birth_date = start_date + datetime.timedelta(days=random_days)
    birth_code = birth_date.strftime("%Y%m%d")
    
    # 3. Sequence Code (3 digits)
    seq = f"{random.randint(0, 999):03d}"
    
    # 4. Checksum
    body = addr + birth_code + seq
    factors = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
    checksum_map = ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2']
    
    total = sum(int(body[i]) * factors[i] for i in range(17))
    checksum = checksum_map[total % 11]
    
    return body + checksum

def test_passenger_lifecycle():
    id_card = get_valid_id_card()

    db = SessionLocal()
    try:
        user = User(
            username="passenger_test_user",
            email="passenger_test_user@example.com",
            hashed_password=get_password_hash("PassengerTest123"),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        token = create_access_token({"sub": user.username})
    finally:
        db.close()
    
    # Create
    response = client.post(
        "/api/v1/passengers/",
        json={
            "name": "TestPassenger", # Valid English Name (No spaces needed for simple test)
            "id_type": 0,
            "id_card": id_card,
            "type": 0,
            "phone": "13800138000"
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    passenger_id = data["id"]
    assert data["name"] == "TestPassenger"

    # Read
    response = client.get("/api/v1/passengers/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert any(p["id"] == passenger_id for p in data)

    # Update
    response = client.put(
        f"/api/v1/passengers/{passenger_id}",
        json={"name": "UpdatedName"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "UpdatedName"

    # Delete
    response = client.delete(
        f"/api/v1/passengers/{passenger_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    
    # Verify gone
    response = client.get("/api/v1/passengers/", headers={"Authorization": f"Bearer {token}"})
    data = response.json()
    assert not any(p["id"] == passenger_id for p in data)

def test_duplicate_passenger():
    id_card = get_valid_id_card()
    db = SessionLocal()
    try:
        user = User(
            username="passenger_dup_user",
            email="passenger_dup_user@example.com",
            hashed_password=get_password_hash("PassengerTest123"),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        token = create_access_token({"sub": user.username})
    finally:
        db.close()
    payload = {
        "name": "DupPassenger",
        "id_type": 0,
        "id_card": id_card,
        "type": 0,
        "phone": "13800138000"
    }
    
    # Create first
    response = client.post(
        "/api/v1/passengers/",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200

    # Create second (duplicate)
    response = client.post(
        "/api/v1/passengers/",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]

def test_search_passenger():
    id_card_1 = get_valid_id_card()
    id_card_2 = get_valid_id_card()
    while id_card_2 == id_card_1:
        id_card_2 = get_valid_id_card()

    db = SessionLocal()
    try:
        user = User(
            username="passenger_search_user",
            email="passenger_search_user@example.com",
            hashed_password=get_password_hash("PassengerTest123"),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        token = create_access_token({"sub": user.username})
    finally:
        db.close()

    headers = {"Authorization": f"Bearer {token}"}

    client.post(
        "/api/v1/passengers/",
        json={
            "name": "SearchTarget",
            "id_type": 0,
            "id_card": id_card_1,
            "type": 0,
            "phone": "13800138000",
        },
        headers=headers,
    )

    client.post(
        "/api/v1/passengers/",
        json={
            "name": "OtherPerson",
            "id_type": 0,
            "id_card": id_card_2,
            "type": 0,
            "phone": "13800138000",
        },
        headers=headers,
    )

    response = client.get("/api/v1/passengers/?name=SearchTarget", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(p["name"] == "SearchTarget" for p in data)
    assert not any(p["name"] == "OtherPerson" for p in data)


def test_no_default_passenger_when_profile_incomplete():
    db = SessionLocal()
    try:
        user = User(
            username="incomplete_profile_user",
            email="incomplete@example.com",
            hashed_password=get_password_hash("PassengerTest123"),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        token = create_access_token({"sub": user.username})
    finally:
        db.close()

    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/v1/passengers/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data == []

    db = SessionLocal()
    try:
        count = db.query(Passenger).count()
        assert count == 0
    finally:
        db.close()


def test_self_passenger_syncs_with_profile_and_no_duplicates():
    payload = {
        "username": "passenger_integration_user",
        "password": "abc12345",
        "confirm_password": "abc12345",
        "email": "integration@example.com",
        "real_name": "赵六",
        "id_type": "id_card",
        "id_number": "110101199001010044",
        "phone": "13800000002",
        "user_type": "adult",
    }

    register_response = client.post("/api/v1/register", json=payload)
    assert register_response.status_code == 200

    login_response = client.post(
        "/api/v1/login",
        json={"username": payload["username"], "password": payload["password"]},
    )
    assert login_response.status_code == 200
    token = login_response.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    first_list_response = client.get("/api/v1/passengers/", headers=headers)
    assert first_list_response.status_code == 200
    first_list = first_list_response.json()
    assert len(first_list) == 1
    self_passenger = first_list[0]
    assert self_passenger["is_default"] is True
    assert self_passenger["name"] == payload["real_name"]
    assert self_passenger["id_card"] == payload["id_number"]
    assert self_passenger["phone"] == payload["phone"]

    update_payload = {
        "real_name": "新赵六",
        "phone": "13900000002",
        "email": "integration_new@example.com",
        "user_type": "student",
    }

    update_response = client.put(
        "/api/v1/users/profile",
        json=update_payload,
        headers=headers,
    )
    assert update_response.status_code == 200

    second_list_response = client.get("/api/v1/passengers/", headers=headers)
    assert second_list_response.status_code == 200
    second_list = second_list_response.json()
    assert len(second_list) == 1
    updated_self = second_list[0]
    assert updated_self["is_default"] is True
    assert updated_self["name"] == update_payload["real_name"]
    assert updated_self["id_card"] == payload["id_number"]
    assert updated_self["phone"] == update_payload["phone"]

    create_response = client.post(
        "/api/v1/passengers/",
        json={
            "name": "其他乘车人",
            "id_type": 0,
            "id_card": get_valid_id_card(),
            "type": 0,
            "phone": "13800138003",
        },
        headers=headers,
    )
    assert create_response.status_code == 200

    final_list_response = client.get("/api/v1/passengers/", headers=headers)
    assert final_list_response.status_code == 200
    final_list = final_list_response.json()
    assert len(final_list) == 2
    default_count = sum(1 for p in final_list if p["is_default"] is True)
    assert default_count == 1
