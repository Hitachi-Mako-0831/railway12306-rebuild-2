from datetime import time
from typing import List

from sqlalchemy import Enum as SQLEnum, ForeignKey, Integer, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.models.enums import TrainType
from app.models.station import Station


class Train(Base):
    __tablename__ = "trains"

    train_number: Mapped[str] = mapped_column(unique=True, index=True)
    train_type: Mapped[TrainType] = mapped_column(SQLEnum(TrainType, name="train_type"))
    from_station_id: Mapped[int] = mapped_column(ForeignKey("stations.id"), index=True)
    to_station_id: Mapped[int] = mapped_column(ForeignKey("stations.id"), index=True)
    departure_time: Mapped[time] = mapped_column(Time)
    arrival_time: Mapped[time] = mapped_column(Time)
    duration_minutes: Mapped[int] = mapped_column(Integer)
    arrival_day_offset: Mapped[int] = mapped_column(Integer, default=0)

    from_station: Mapped[Station] = relationship(foreign_keys=[from_station_id])
    to_station: Mapped[Station] = relationship(foreign_keys=[to_station_id])
    orders: Mapped[List["Order"]] = relationship(back_populates="train")

