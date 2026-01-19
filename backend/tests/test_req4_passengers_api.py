import pytest
import random
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def get_random_id_card():
    return f"1234567890{random.randint(10000000, 99999999)}"

def test_passenger_lifecycle():
    id_card = get_random_id_card()
    
    # Create
    response = client.post(
        "/api/v1/passengers/",
        json={
            "name": "Test Passenger",
            "id_type": 0,
            "id_card": id_card,
            "type": 0,
            "phone": "13800138000"
        }
    )
    assert response.status_code == 200
    data = response.json()
    passenger_id = data["id"]
    assert data["name"] == "Test Passenger"

    # Read
    response = client.get("/api/v1/passengers/")
    assert response.status_code == 200
    data = response.json()
    assert any(p["id"] == passenger_id for p in data)

    # Update
    response = client.put(
        f"/api/v1/passengers/{passenger_id}",
        json={
            "name": "Updated Name"
        }
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Name"

    # Delete
    response = client.delete(f"/api/v1/passengers/{passenger_id}")
    assert response.status_code == 200
    
    # Verify gone
    response = client.get("/api/v1/passengers/")
    data = response.json()
    assert not any(p["id"] == passenger_id for p in data)
