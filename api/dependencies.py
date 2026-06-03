"""FastAPI dependency providers."""
from typing import Generator

from sqlalchemy.orm import Session

from models.base import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """Yield a database session and ensure it is closed."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
