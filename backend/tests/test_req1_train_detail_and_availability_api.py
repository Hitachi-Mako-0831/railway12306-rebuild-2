import os
import sys

from fastapi.testclient import TestClient


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.main import app


client = TestClient(app)


def test_get_train_detail_basic_fields():
    response = client.get("/api/v1/trains/G21")

    assert response.status_code == 200

    body = response.json()
    assert body["code"] == 200
    data = body["data"]

    assert data["train_number"] == "G21"
    for field in [
        "from_station",
        "to_station",
        "departure_time",
        "arrival_time",
        "duration_minutes",
        "arrival_day_offset",
        "stops",
    ]:
        assert field in data


def test_get_train_availability_basic_fields():
    response = client.get("/api/v1/trains/G21/availability")

    assert response.status_code == 200

    body = response.json()
    assert body["code"] == 200
    data = body["data"]

    assert data["train_number"] == "G21"
    assert "seat_second_class" in data

