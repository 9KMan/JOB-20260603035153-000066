"""Celery task definitions."""
import logging
from uuid import UUID

from workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="workers.tasks.process_item", bind=True, max_retries=3)
def process_item(self, item_id: str) -> dict:
    """Example idempotent background task that processes an item."""
    try:
        UUID(item_id)
    except ValueError as exc:
        logger.exception("Invalid item_id: %s", item_id)
        raise self.retry(exc=exc, countdown=10)

    logger.info("Processing item %s", item_id)
    return {"item_id": item_id, "status": "processed"}


@celery_app.task(name="workers.tasks.healthcheck")
def healthcheck() -> dict:
    """Simple worker liveness check."""
    return {"status": "ok"}
