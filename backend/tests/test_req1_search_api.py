import os
import sys

from fastapi.testclient import TestClient

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.main import app


client = TestClient(app)


def test_search_trains_basic_fields_exist():
    params = {
        "departure_city": "北京",
        "arrival_city": "上海",
        "travel_date": "2025-12-30",
    }

    response = client.get("/api/v1/trains/search", params=params)

    assert response.status_code == 200

    body = response.json()

    assert body["code"] == 200
    assert isinstance(body["data"], list)

    if body["data"]:
        item = body["data"][0]
        for field in [
            "train_number",
            "departure_city",
            "arrival_city",
            "departure_time",
            "arrival_time",
            "duration_minutes",
        ]:
            assert field in item
