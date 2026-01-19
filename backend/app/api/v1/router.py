from fastapi import APIRouter

from app.api.v1.endpoints import health, trains, orders, passengers


api_router = APIRouter()

api_router.include_router(health.router, prefix="", tags=["health"])
api_router.include_router(trains.router)
api_router.include_router(orders.router, prefix="/orders", tags=["orders"])
api_router.include_router(passengers.router, prefix="/passengers", tags=["passengers"])
