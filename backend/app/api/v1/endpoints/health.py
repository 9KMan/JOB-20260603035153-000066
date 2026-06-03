"""Health and readiness endpoints for orchestrators."""
from datetime import datetime, timezone

from fastapi import APIRouter
from sqlalchemy import text

from app.database import engine

router = APIRouter()


@router.get("", summary="Liveness probe")
async def liveness() -> dict:
    return {
        "status": "ok",
        "time": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/ready", summary="Readiness probe")
async def readiness() -> dict:
    checks: dict = {"database": "unknown"}
    overall = "ok"
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception as exc:  # noqa: BLE001
        checks["database"] = f"error: {exc.__class__.__name__}"
        overall = "degraded"
    return {"status": overall, "checks": checks}
