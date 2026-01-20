from sqlalchemy import String, Boolean, ForeignKey, SmallInteger, UniqueConstraint, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.db.base_class import Base
from app.models.enums import PassengerType, IdType, VerifyStatus
from typing import TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from app.models.user import User

class Passenger(Base):
    __tablename__ = "passengers"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    id_type: Mapped[int] = mapped_column(SmallInteger, default=IdType.ID_CARD.value, nullable=False)
    id_card: Mapped[str] = mapped_column(String(30), nullable=False)
    type: Mapped[int] = mapped_column(SmallInteger, default=PassengerType.ADULT.value)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    verify_status: Mapped[int] = mapped_column(SmallInteger, default=VerifyStatus.UNVERIFIED.value)
    phone_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user: Mapped["User"] = relationship(back_populates="passengers")

    __table_args__ = (
        UniqueConstraint('user_id', 'id_type', 'id_card', name='uq_user_id_card'),
    )
