from typing import Optional
import re
from pydantic import BaseModel, Field, field_validator, ValidationInfo
from app.models.enums import PassengerType, IdType, VerifyStatus

# Validation Patterns
PATTERN_PHONE_CN = r"^1[3-9]\d{9}$"
PATTERN_ID_CARD_CN = r"^[1-9]\d{5}(18|19|20)\d{2}((0[1-9])|(1[0-2]))(([0-2][1-9])|10|20|30|31)\d{3}[0-9Xx]$"
PATTERN_CHINESE_NAME = r"^[\u4e00-\u9fa5]{2,15}(?:·[\u4e00-\u9fa5]{2,15})*$"
PATTERN_PASSPORT_NAME = r"^[a-zA-Z]+(?:\s[a-zA-Z]+)*$"
PATTERN_PASSPORT = r"^[a-zA-Z0-9]{5,15}$"

# Shared properties
class PassengerBase(BaseModel):
    name: str = Field(..., max_length=50, description="Passenger Name")
    id_type: IdType = Field(default=IdType.ID_CARD, description="ID Type")
    id_card: str = Field(..., max_length=30, description="ID Card Number")
    type: PassengerType = Field(default=PassengerType.ADULT, description="Passenger Type")
    phone: str = Field(..., max_length=20, description="Phone Number")
    is_default: bool = Field(default=False, description="Is Self/Default Passenger")

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        if not re.match(PATTERN_PHONE_CN, v):
            raise ValueError('Invalid phone number format')
        return v

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError('Name cannot be empty')
        # Check if matches either Chinese or English name pattern
        is_chinese = re.match(PATTERN_CHINESE_NAME, v)
        is_english = re.match(PATTERN_PASSPORT_NAME, v)
        if not (is_chinese or is_english):
             raise ValueError('Invalid name format (Must be valid Chinese or English name)')
        return v

    @field_validator('id_card')
    @classmethod
    def validate_id_card_format(cls, v: str, info: ValidationInfo) -> str:
        v = v.strip().upper()
        # We need to check id_type to apply specific regex
        # In Pydantic v2, info.data gives access to other fields
        id_type = info.data.get('id_type')
        
        # If id_type is missing (e.g. validation error on id_type), skip strict check or assume default
        if id_type == IdType.ID_CARD:
            if not re.match(PATTERN_ID_CARD_CN, v):
                raise ValueError('Invalid ID Card format')
        elif id_type == IdType.PASSPORT:
            if not re.match(PATTERN_PASSPORT, v):
                raise ValueError('Invalid Passport format')
        
        return v

class PassengerCreate(PassengerBase):
    pass

class PassengerUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=50)
    id_type: Optional[IdType] = None
    id_card: Optional[str] = Field(None, max_length=30)
    type: Optional[PassengerType] = None
    phone: Optional[str] = Field(None, max_length=20)

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        if v is None: return v
        if not re.match(PATTERN_PHONE_CN, v):
            raise ValueError('Invalid phone number format')
        return v

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        if v is None: return v
        v = v.strip()
        is_chinese = re.match(PATTERN_CHINESE_NAME, v)
        is_english = re.match(PATTERN_PASSPORT_NAME, v)
        if not (is_chinese or is_english):
             raise ValueError('Invalid name format')
        return v
    
    @field_validator('id_card')
    @classmethod
    def validate_id_card_format(cls, v: str, info: ValidationInfo) -> str:
        if v is None: return v
        v = v.strip().upper()
        
        # For Update, id_type might not be in the request.
        # If id_type is in request, use it. If not, we can't strictly validate against type unless we query DB.
        # But here we are in Schema validation, no DB access.
        # We can only validate if id_type is present.
        id_type = info.data.get('id_type')
        
        if id_type is not None:
            if id_type == IdType.ID_CARD:
                if not re.match(PATTERN_ID_CARD_CN, v):
                    raise ValueError('Invalid ID Card format')
            elif id_type == IdType.PASSPORT:
                if not re.match(PATTERN_PASSPORT, v):
                    raise ValueError('Invalid Passport format')
        
        # If id_type is NOT present, we can try to guess or just let it pass regex check if it matches EITHER?
        # Or better, just ensure it's not garbage.
        # However, typically updating ID card implies you might also update ID type, or you are correcting it.
        # Without DB context, strict validation is hard. 
        # But we can at least ensure it matches *one* of the known patterns if we want to be strict,
        # or just sanitize it (upper case).
        return v

class PassengerInDBBase(PassengerBase):
    id: int
    user_id: int
    # is_default is already in PassengerBase
    verify_status: VerifyStatus = VerifyStatus.UNVERIFIED
    phone_verified: bool = False

    class Config:
        from_attributes = True

# Properties to return to client
class Passenger(PassengerInDBBase):
    pass
