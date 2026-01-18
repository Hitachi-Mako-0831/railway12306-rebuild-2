from typing import Any

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    def __repr__(self) -> str:
        attrs = ", ".join(
            f"{key}={getattr(self, key)!r}" for key in self.__mapper__.c.keys()
        )
        return f"{self.__class__.__name__}({attrs})"

