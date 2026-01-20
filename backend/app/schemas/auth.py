from pydantic import BaseModel, EmailStr, Field


class UserLoginRequest(BaseModel):
    username: str
    password: str


class UserRegisterRequest(BaseModel):
    username: str = Field(min_length=6, max_length=30)
    password: str = Field(min_length=6, max_length=20)
    confirm_password: str
    email: EmailStr
    real_name: str
    id_type: str
    id_number: str
    phone: str
    user_type: str


class PasswordResetRequest(BaseModel):
    username: str
    email: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
