from typing import Generator
from fastapi import Depends
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import User


def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def get_current_user(db: Session = Depends(get_db)) -> User:
    user = db.query(User).filter(User.username == "testuser").first()
    if not user:
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="mock_hash_password",
            real_name="",
            id_type="id_card",
            id_number="110101199001010099",
            phone="13800000000",
            user_type="adult",
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user
