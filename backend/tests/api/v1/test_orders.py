from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.core.config import settings

def test_create_order(client: TestClient, db: Session):
    data = {
        "train_id": 1,
        "departure_date": "2023-12-12",
        "total_price": 100.0,
        "items": [
            {
                "passenger_name": "Test Passenger",
                "passenger_id_card": "123456789012345678",
                "seat_type": "second_class",
                "price": 100.0
            }
        ]
    }
    # Expect success, but currently it returns 501
    response = client.post(f"{settings.API_V1_STR}/orders/", json=data)
    assert response.status_code == 200
    content = response.json()
    assert content["total_price"] == 100.0
    assert len(content["items"]) == 1
    assert "id" in content

def test_read_orders(client: TestClient, db: Session):
    response = client.get(f"{settings.API_V1_STR}/orders/")
    assert response.status_code == 200
    content = response.json()
    assert isinstance(content, list)
