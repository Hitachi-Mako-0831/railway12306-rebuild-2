from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import User

def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

# Mock auth for now since REQ-2 is not ready
def get_current_user(db: Session = Depends(get_db)) -> User:
    # Check if user 1 exists, if not create it (for development)
    user = db.query(User).filter(User.id == 1).first()
    if not user:
        # We need to make sure we don't break if User model has required fields.
        user = User(
            id=1,
            username="testuser",
            email="test@example.com",
            hashed_password="mock_hash_password"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user
