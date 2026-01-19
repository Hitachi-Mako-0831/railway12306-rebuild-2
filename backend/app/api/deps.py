from typing import Generator
from app.db.session import SessionLocal

def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

# Mock current user for now
def get_current_active_user():
    return None
