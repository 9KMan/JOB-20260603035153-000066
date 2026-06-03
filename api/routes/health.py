"""Health check endpoints."""
from fastapi import APIRouter, status
from sqlalchemy import text

from api.dependencies import get_db
from config import settings
from fastapi import Depends
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/", status_code=status.HTTP_200_OK)
def healthcheck() -> dict:
    """Liveness probe."""
    return {
        "status": "ok",
        "app": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
    }


@router.get("/ready", status_code=status.HTTP_200_OK)
def readiness(db: Session = Depends(get_db)) -> dict:
    """Readiness probe that verifies DB connectivity."""
    db.execute(text("SELECT 1"))
    return {"status": "ready"}
