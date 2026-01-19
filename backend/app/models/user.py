from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base


class User(Base):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str | None] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    real_name: Mapped[str] = mapped_column(String(50), default="")
    id_type: Mapped[str] = mapped_column(String(20), default="id_card")
    id_number: Mapped[str] = mapped_column(String(50), default="000000000000000000")
    phone: Mapped[str] = mapped_column(String(20), default="")
    user_type: Mapped[str] = mapped_column(String(20), default="adult")
