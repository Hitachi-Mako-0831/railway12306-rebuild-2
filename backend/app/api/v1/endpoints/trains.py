from typing import List, Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel


router = APIRouter(prefix="/trains", tags=["trains"])


class TrainSearchItem(BaseModel):
    train_number: str
    departure_city: str
    arrival_city: str
    departure_time: str
    arrival_time: str
    duration_minutes: int
    train_type: str
    from_station: str
    to_station: str
    seat_second_class: str


class TrainDetailResponse(BaseModel):
    train_number: str
    from_station: str
    to_station: str
    departure_time: str
    arrival_time: str
    duration_minutes: int
    arrival_day_offset: int
    stops: list[str]


class TrainAvailabilityResponse(BaseModel):
    train_number: str
    seat_second_class: str
    seat_first_class: Optional[str] = None
    soft_sleeper: Optional[str] = None


SAMPLE_TRAINS: List[TrainSearchItem] = [
    TrainSearchItem(
        train_number="G21",
        departure_city="北京",
        arrival_city="上海",
        departure_time="08:00",
        arrival_time="12:30",
        duration_minutes=270,
        train_type="G",
        from_station="北京南",
        to_station="上海虹桥",
        seat_second_class="有",
    ),
    TrainSearchItem(
        train_number="D3101",
        departure_city="北京",
        arrival_city="上海",
        departure_time="10:30",
        arrival_time="17:00",
        duration_minutes=390,
        train_type="D",
        from_station="北京南",
        to_station="上海站",
        seat_second_class="无",
    ),
    TrainSearchItem(
        train_number="Z99",
        departure_city="北京",
        arrival_city="上海",
        departure_time="05:00",
        arrival_time="13:00",
        duration_minutes=480,
        train_type="Z",
        from_station="北京站",
        to_station="上海站",
        seat_second_class="5",
    ),
    TrainSearchItem(
        train_number="G22",
        departure_city="上海",
        arrival_city="北京",
        departure_time="18:00",
        arrival_time="22:30",
        duration_minutes=270,
        train_type="G",
        from_station="上海虹桥",
        to_station="北京南",
        seat_second_class="有",
    ),
    TrainSearchItem(
        train_number="D2288",
        departure_city="南京",
        arrival_city="杭州",
        departure_time="09:00",
        arrival_time="10:30",
        duration_minutes=90,
        train_type="D",
        from_station="南京南",
        to_station="杭州东",
        seat_second_class="有",
    ),
]


@router.get("/search", summary="车票综合查询")
async def search_trains(
    departure_city: str = Query(..., description="出发城市"),
    arrival_city: str = Query(..., description="到达城市"),
    travel_date: str = Query(..., description="出发日期，格式 YYYY-MM-DD"),
    min_departure_time: str | None = Query(
        None, description="筛选最早出发时间，格式 HH:MM，可选"
    ),
):
    matched = [
        item
        for item in SAMPLE_TRAINS
        if item.departure_city == departure_city and item.arrival_city == arrival_city
    ]

    if min_departure_time:
        def to_minutes(value: str) -> int:
            hour, minute = value.split(":")
            return int(hour) * 60 + int(minute)

        threshold = to_minutes(min_departure_time)
        matched = [
            item for item in matched if to_minutes(item.departure_time) >= threshold
        ]

    data = [item.model_dump() for item in matched]

    return {"code": 200, "message": "操作成功", "data": data}


@router.get("/{train_number}", summary="车次详情")
async def get_train_detail(train_number: str):
    for item in SAMPLE_TRAINS:
        if item.train_number == train_number:
            detail = TrainDetailResponse(
                train_number=item.train_number,
                from_station=item.from_station,
                to_station=item.to_station,
                departure_time=item.departure_time,
                arrival_time=item.arrival_time,
                duration_minutes=item.duration_minutes,
                arrival_day_offset=0,
                stops=[item.from_station, item.to_station],
            )
            return {"code": 200, "message": "操作成功", "data": detail.model_dump()}

    return {"code": 404, "message": "车次不存在", "data": None}


@router.get("/{train_number}/availability", summary="余票查询")
async def get_train_availability(train_number: str):
    for item in SAMPLE_TRAINS:
        if item.train_number == train_number:
            availability = TrainAvailabilityResponse(
                train_number=item.train_number,
                seat_second_class=item.seat_second_class,
                seat_first_class=None,
                soft_sleeper=None,
            )
            return {
                "code": 200,
                "message": "操作成功",
                "data": availability.model_dump(),
            }

    return {"code": 404, "message": "车次不存在", "data": None}
