from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from app.core.security import ALGORITHM, SECRET_KEY
from app.db.session import SessionLocal
from app.models.user import User
from app import crud
from app.schemas.user import UserResponse, UserUpdateRequest


router = APIRouter(prefix="/users", tags=["users"])


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/login")


def get_current_username(token: str = Depends(oauth2_scheme)) -> str:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    username = payload.get("sub")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    return username


@router.get("/profile", summary="获取当前用户信息")
async def get_profile(current_username: str = Depends(get_current_username)) -> dict:
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == current_username).first()
    finally:
        db.close()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    response = UserResponse(
        username=user.username,
        real_name=user.real_name,
        country="中国",
        id_type=user.id_type,
        id_number=user.id_number,
        phone=user.phone,
        email=user.email or "",
        user_type=user.user_type,
    )

    return {
        "code": 200,
        "message": "获取成功",
        "data": response.model_dump(),
    }


@router.put("/profile", summary="更新当前用户信息")
async def update_profile(
    payload: UserUpdateRequest, current_username: str = Depends(get_current_username)
) -> dict:
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == current_username).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        user.real_name = payload.real_name
        user.phone = payload.phone
        user.email = payload.email
        user.user_type = payload.user_type
        db.commit()
        db.refresh(user)
        crud.passenger.sync_default_for_user(db, user)

        response = UserResponse(
            username=user.username,
            real_name=user.real_name,
            country="中国",
            id_type=user.id_type,
            id_number=user.id_number,
            phone=user.phone,
            email=user.email or "",
            user_type=user.user_type,
        )
    finally:
        db.close()

    return {
        "code": 200,
        "message": "更新成功",
        "data": response.model_dump(),
    }
