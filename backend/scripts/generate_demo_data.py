from loguru import logger

from app.db.init_db import init_db


def main() -> None:
    init_db()
    logger.info("Demo data seeding is not implemented yet.")


if __name__ == "__main__":
    main()

