from datetime import datetime
from typing import List, Optional

from sqlalchemy import ForeignKey, DateTime, Integer, Float, String, Enum as SQLEnum, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base_class import Base
from app.models.enums import OrderStatus, SeatType
from app.models.train import Train

class Order(Base):
    __tablename__ = "orders"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    train_id: Mapped[int] = mapped_column(ForeignKey("trains.id"), index=True)
    
    # The specific date of travel
    departure_date: Mapped[datetime] = mapped_column(Date)
    
    status: Mapped[OrderStatus] = mapped_column(
        SQLEnum(OrderStatus, name="order_status"), 
        default=OrderStatus.PENDING, 
        index=True
    )
    
    total_price: Mapped[float] = mapped_column(Float)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True)) # Created + 45 mins
    
    # Relationships
    items: Mapped[List["OrderItem"]] = relationship(back_populates="order", cascade="all, delete-orphan")
    # We can add backrefs to User and Train if needed, but IDs are sufficient for now.


class OrderItem(Base):
    __tablename__ = "order_items"

    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), index=True)
    
    passenger_name: Mapped[str] = mapped_column(String(100))
    passenger_id_card: Mapped[str] = mapped_column(String(50))
    
    seat_type: Mapped[SeatType] = mapped_column(SQLEnum(SeatType, name="seat_type"))
    price: Mapped[float] = mapped_column(Float)
    
    seat_number: Mapped[Optional[str]] = mapped_column(String(20), nullable=True) # e.g. "05车12A"
    
    status: Mapped[OrderStatus] = mapped_column(
        SQLEnum(OrderStatus, name="order_item_status"), 
        default=OrderStatus.PENDING
    )
    
    order: Mapped["Order"] = relationship(back_populates="items")
