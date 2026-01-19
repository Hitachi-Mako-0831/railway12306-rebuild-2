from datetime import datetime, date
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from app.models.enums import OrderStatus, SeatType

# --- OrderItem Schemas ---

class OrderItemBase(BaseModel):
    passenger_name: str
    passenger_id_card: str
    seat_type: SeatType
    price: float

class OrderItemCreate(OrderItemBase):
    pass

class OrderItemUpdate(BaseModel):
    status: Optional[OrderStatus] = None
    seat_number: Optional[str] = None

class OrderItem(OrderItemBase):
    id: int
    order_id: int
    seat_number: Optional[str] = None
    status: OrderStatus
    
    model_config = ConfigDict(from_attributes=True)

# --- Order Schemas ---

class OrderBase(BaseModel):
    train_id: int
    departure_date: date
    total_price: float

class OrderCreate(OrderBase):
    items: List[OrderItemCreate]

class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None

class Order(OrderBase):
    id: int
    user_id: int
    status: OrderStatus
    created_at: datetime
    expires_at: datetime
    items: List[OrderItem]
    train: Optional[Train] = None
    
    model_config = ConfigDict(from_attributes=True)
