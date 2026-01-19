from typing import Any, List
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class Passenger(BaseModel):
    id: int
    name: str
    type: str
    id_card: str

@router.get("/", response_model=List[Passenger])
def read_passengers() -> Any:
    """
    Get mock passengers for REQ-3-1 testing.
    """
    return [
        {"id": 1, "name": "张三", "type": "成人票", "id_card": "110101199001011234"},
        {"id": 2, "name": "李四", "type": "成人票", "id_card": "110101199001011235"},
        {"id": 3, "name": "王五", "type": "学生票", "id_card": "110101199001011236"},
    ]
