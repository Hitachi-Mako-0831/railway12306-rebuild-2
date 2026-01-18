from fastapi import APIRouter

from app.api.v1.endpoints import health, trains


api_router = APIRouter()

api_router.include_router(health.router, prefix="", tags=["health"])
api_router.include_router(trains.router)
