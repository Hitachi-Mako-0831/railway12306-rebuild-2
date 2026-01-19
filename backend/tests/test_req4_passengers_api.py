import pytest
import random
import datetime
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import SessionLocal
from sqlalchemy import text

client = TestClient(app)

@pytest.fixture(autouse=True)
def clean_db():
    db = SessionLocal()
    try:
        # Clean up passengers table before each test to ensure no invalid data from previous runs
        db.execute(text("DELETE FROM passengers"))
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
    
    # Create
    response = client.post(
        "/api/v1/passengers/",
        json={
            "name": "TestPassenger", # Valid English Name (No spaces needed for simple test)
            "id_type": 0,
            "id_card": id_card,
            "type": 0,
            "phone": "13800138000"
        }
    )
    assert response.status_code == 200, response.text
    data = response.json()
    passenger_id = data["id"]
    assert data["name"] == "TestPassenger"

    # Read
    response = client.get("/api/v1/passengers/")
    assert response.status_code == 200
    data = response.json()
    assert any(p["id"] == passenger_id for p in data)

    # Update
    response = client.put(
        f"/api/v1/passengers/{passenger_id}",
        json={
            "name": "UpdatedName"
        }
    )
    assert response.status_code == 200
    assert response.json()["name"] == "UpdatedName"

    # Delete
    response = client.delete(f"/api/v1/passengers/{passenger_id}")
    assert response.status_code == 200
    
    # Verify gone
    response = client.get("/api/v1/passengers/")
    data = response.json()
    assert not any(p["id"] == passenger_id for p in data)

def test_duplicate_passenger():
    id_card = get_valid_id_card()
    payload = {
        "name": "DupPassenger",
        "id_type": 0,
        "id_card": id_card,
        "type": 0,
        "phone": "13800138000"
    }
    
    # Create first
    response = client.post("/api/v1/passengers/", json=payload)
    assert response.status_code == 200

    # Create second (duplicate)
    response = client.post("/api/v1/passengers/", json=payload)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]

def test_search_passenger():
    id_card_1 = get_valid_id_card()
    id_card_2 = get_valid_id_card()
    # Ensure they are different
    while id_card_2 == id_card_1:
        id_card_2 = get_valid_id_card()
    
    client.post("/api/v1/passengers/", json={
        "name": "SearchTarget",
        "id_type": 0,
        "id_card": id_card_1,
        "type": 0,
        "phone": "13800138000"
    })
    
    client.post("/api/v1/passengers/", json={
        "name": "OtherPerson",
        "id_type": 0,
        "id_card": id_card_2,
        "type": 0,
        "phone": "13800138000"
    })
    
    # Search match
    response = client.get("/api/v1/passengers/?name=SearchTarget")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(p["name"] == "SearchTarget" for p in data)
    assert not any(p["name"] == "OtherPerson" for p in data)
