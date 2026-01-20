from pydantic import BaseModel, EmailStr


class UserResponse(BaseModel):
    username: str
    real_name: str
    country: str
    id_type: str
    id_number: str
    phone: str
    email: str
    user_type: str


class UserUpdateRequest(BaseModel):
    real_name: str
    phone: str
    email: EmailStr
    user_type: str
