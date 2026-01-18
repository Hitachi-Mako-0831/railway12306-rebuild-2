from datetime import date

from sqlalchemy import Date, Enum as SQLEnum, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base
from app.models.enums import SeatType


class Seat(Base):
    __tablename__ = "seats"
    __table_args__ = (
        UniqueConstraint("train_id", "travel_date", "seat_type", name="uq_seat_train_date_type"),
    )

    train_id: Mapped[int] = mapped_column(ForeignKey("trains.id"), index=True)
    travel_date: Mapped[date] = mapped_column(Date)
    seat_type: Mapped[SeatType] = mapped_column(SQLEnum(SeatType, name="seat_type"))
    total: Mapped[int] = mapped_column(Integer)
    available: Mapped[int] = mapped_column(Integer)

