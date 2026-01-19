from loguru import logger
from sqlalchemy.orm import Session
from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.models.user import User

def seed_user(db: Session) -> None:
    user = db.query(User).first()
    if not user:
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashedpassword"
        )
        db.add(user)
        db.commit()
        logger.info("Seeded test user")
    else:
        logger.info("Test user already exists")

def main() -> None:
    init_db()
    db = SessionLocal()
    try:
        seed_user(db)
    finally:
        db.close()
    logger.info("Demo data seeding completed.")

if __name__ == "__main__":
    main()
