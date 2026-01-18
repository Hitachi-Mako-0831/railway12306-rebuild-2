from fastapi import APIRouter

router = APIRouter()


@router.get("/", summary="Backend ready")
async def backend_ready():
  return {"code": 200, "message": "Backend Ready"}

