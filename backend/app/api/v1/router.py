from fastapi import APIRouter

from app.api.v1.endpoints import auth, health, trains, users, passengers, orders


api_router = APIRouter()

api_router.include_router(health.router, prefix="", tags=["health"])
api_router.include_router(trains.router)
api_router.include_router(auth.router, prefix="", tags=["auth"])
api_router.include_router(users.router)
api_router.include_router(orders.router, prefix="/orders", tags=["orders"])
api_router.include_router(passengers.router, prefix="/passengers", tags=["passengers"])
