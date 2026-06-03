"""Top-level configuration package for the FDD platform."""

from config.celery import app as celery_app

__all__ = ("celery_app",)
