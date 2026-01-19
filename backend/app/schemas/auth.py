from pydantic import BaseModel, EmailStr, Field


class UserLoginRequest(BaseModel):
    username: str
    password: str


class UserRegisterRequest(BaseModel):
    username: str = Field(min_length=6, max_length=30)
    password: str = Field(min_length=6, max_length=20)
    confirm_password: str
    email: EmailStr


class PasswordResetRequest(BaseModel):
    username: str
    email: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
