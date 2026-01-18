from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base


class Station(Base):
    __tablename__ = "stations"

    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    city: Mapped[str] = mapped_column(String(50), index=True)
    pinyin: Mapped[str | None] = mapped_column(String(100))
    code: Mapped[str | None] = mapped_column(String(20), unique=True)
    is_hot: Mapped[bool] = mapped_column(Boolean, default=False)

