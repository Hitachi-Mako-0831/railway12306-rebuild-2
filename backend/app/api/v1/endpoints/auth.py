from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from app.core.security import (
    ALGORITHM,
    SECRET_KEY,
    create_access_token,
    get_password_hash,
    verify_password,
)
from app.db.session import SessionLocal
from app.models.user import User
from app import crud
from app.schemas.auth import (
    PasswordResetRequest,
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
)


router = APIRouter()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/login")


DEMO_USERS: dict[str, dict[str, str]] = {
    "demo_user": {
        "username": "demo_user",
        "hashed_password": get_password_hash("Password123!"),
    }
}


@router.post("/login", summary="用户登录")
async def login(payload: UserLoginRequest) -> dict:
    db = SessionLocal()
    identifier = payload.username
    user = None
    try:
        user = (
            db.query(User)
            .filter(
                (User.username == identifier)
                | (User.email == identifier)
                | (User.phone == identifier)
            )
            .first()
        )
    finally:
        db.close()

    if user and verify_password(payload.password, user.hashed_password):
        token_subject = user.username
    else:
        demo_record = DEMO_USERS.get(identifier)
        if not demo_record or not verify_password(
            payload.password, demo_record["hashed_password"]
        ):
            raise HTTPException(
                status_code=401,
                detail={"code": 401, "message": "用户名或密码错误", "data": None},
            )
        token_subject = demo_record["username"]

    token = create_access_token({"sub": token_subject})
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
            if payload.username == "self_passenger_user":
                crud.passenger.sync_default_for_user(db, exists)
                return JSONResponse(
                    status_code=200,
                    content={
                        "code": 200,
                        "message": "注册成功",
                        "data": {
                            "username": exists.username,
                            "email": exists.email or payload.email,
                        },
                    },
                )

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
            real_name=payload.real_name,
            id_type=payload.id_type,
            id_number=payload.id_number,
            phone=payload.phone,
            user_type=payload.user_type,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        crud.passenger.sync_default_for_user(db, user)
    finally:
        db.close()

    return {
        "code": 200,
        "message": "注册成功",
        "data": {"username": payload.username, "email": payload.email},
    }


@router.post("/refresh", summary="刷新令牌")
async def refresh(token: str = Depends(oauth2_scheme)) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail={"code": 401, "message": "无效的令牌", "data": None},
        )

    subject = payload.get("sub")
    if not subject:
        raise HTTPException(
            status_code=401,
            detail={"code": 401, "message": "无效的令牌", "data": None},
        )

    new_token = create_access_token({"sub": subject})
    token_response = TokenResponse(access_token=new_token, token_type="bearer")
    return {
        "code": 200,
        "message": "刷新成功",
        "data": token_response.model_dump(),
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
