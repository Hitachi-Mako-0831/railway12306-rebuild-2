from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.endpoints import auth, health, trains, users, passengers


app = FastAPI(title="Railway 12306 Backend", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(trains.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1", tags=["auth"])
app.include_router(users.router, prefix="/api/v1")
app.include_router(passengers.router, prefix="/api/v1/passengers", tags=["passengers"])


@app.get("/health", summary="Health check")
async def health_check():
    return {"status": "ok"}
