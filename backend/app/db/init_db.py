from loguru import logger

from app.db.base import Base  # noqa
from app.db.session import engine


def init_db() -> None:
    logger.info("Creating database tables if not exist")
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()

