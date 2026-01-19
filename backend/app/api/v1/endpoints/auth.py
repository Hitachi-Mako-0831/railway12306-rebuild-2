from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from app.core.security import create_access_token, get_password_hash, verify_password
from app.db.session import SessionLocal
from app.models.user import User
from app.schemas.auth import (
    PasswordResetRequest,
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
)


router = APIRouter()


DEMO_USERS: dict[str, dict[str, str]] = {
    "demo_user": {
        "username": "demo_user",
        "hashed_password": get_password_hash("Password123!"),
    }
}


@router.post("/login", summary="用户登录")
async def login(payload: UserLoginRequest) -> dict:
    user_record = DEMO_USERS.get(payload.username)
    if not user_record or not verify_password(
        payload.password, user_record["hashed_password"]
    ):
        raise HTTPException(
            status_code=401,
            detail={"code": 401, "message": "用户名或密码错误", "data": None},
        )

    token = create_access_token({"sub": payload.username})
    token_response = TokenResponse(access_token=token, token_type="bearer")
    return {
        "code": 200,
        "message": "登录成功",
        "data": token_response.model_dump(),
    }


@router.post("/register", summary="用户注册")
async def register(payload: UserRegisterRequest) -> dict:
    if payload.password != payload.confirm_password:
        return JSONResponse(
            status_code=400,
            content={
                "code": 400,
                "message": "两次输入密码不一致",
                "data": None,
            },
        )

    if not any(c.isalpha() for c in payload.password) or not any(
        c.isdigit() for c in payload.password
    ):
        return JSONResponse(
            status_code=400,
            content={
                "code": 400,
                "message": "密码必须包含字母和数字",
                "data": None,
            },
        )

    username = payload.username
    if not (username[0].isalpha() and all(c.isalnum() or c == "_" for c in username)):
        return JSONResponse(
            status_code=400,
            content={
                "code": 400,
                "message": "用户名格式错误",
                "data": None,
            },
        )

    db = SessionLocal()
    try:
        exists = db.query(User).filter(User.username == payload.username).first()
        if exists:
            return JSONResponse(
                status_code=400,
                content={
                    "code": 400,
                    "message": "用户名已存在",
                    "data": None,
                },
            )

        user = User(
            username=payload.username,
            email=payload.email,
            hashed_password=get_password_hash(payload.password),
        )
        db.add(user)
        db.commit()
    finally:
        db.close()

    return {
        "code": 200,
        "message": "注册成功",
        "data": {"username": payload.username, "email": payload.email},
    }


@router.post("/login/verify-code", summary="发送登录验证码")
async def send_verify_code() -> dict:
    return {"code": 200, "message": "验证码发送成功", "data": None}


@router.post("/logout", summary="退出登录")
async def logout() -> dict:
    return {"code": 200, "message": "退出登录成功", "data": None}


@router.post("/auth/password/recovery/reset", summary="重置密码")
async def password_recovery_reset(payload: PasswordResetRequest) -> dict:
    if not payload.username or not payload.email:
        return JSONResponse(
            status_code=400,
            content={
                "code": 400,
                "message": "用户名和邮箱为必填项",
                "data": None,
            },
        )

    return {
        "code": 200,
        "message": "重置链接已发送（模拟）",
        "data": None,
    }
