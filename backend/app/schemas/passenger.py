from typing import Optional
from pydantic import BaseModel, Field
from app.models.enums import PassengerType, IdType, VerifyStatus

# Shared properties
class PassengerBase(BaseModel):
    name: str = Field(..., max_length=50, description="Passenger Name")
    id_type: IdType = Field(default=IdType.ID_CARD, description="ID Type")
    id_card: str = Field(..., max_length=30, description="ID Card Number")
    type: PassengerType = Field(default=PassengerType.ADULT, description="Passenger Type")
    phone: str = Field(..., max_length=20, description="Phone Number")
    is_default: bool = Field(default=False, description="Is Self/Default Passenger")
    
class PassengerCreate(PassengerBase):
    pass

class PassengerUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=50)
    id_type: Optional[IdType] = None
    id_card: Optional[str] = Field(None, max_length=30)
    type: Optional[PassengerType] = None
    phone: Optional[str] = Field(None, max_length=20)
    
class PassengerInDBBase(PassengerBase):
    id: int
    user_id: int
    is_default: bool = False
    verify_status: VerifyStatus = VerifyStatus.UNVERIFIED
    phone_verified: bool = False

    class Config:
        from_attributes = True

# Properties to return to client
class Passenger(PassengerInDBBase):
    pass
