"""
Custom managers for soft-deletable models.
"""
from django.db import models
from django.db.models.query import QuerySet
from django.utils import timezone


class SoftDeleteQuerySet(QuerySet):
    """QuerySet that excludes soft-deleted records by default."""

    def delete(self):
        """Soft-delete all records in the queryset."""
        return super().update(deleted_at=timezone.now())

    def hard_delete(self):
        """Permanently delete all records in the queryset."""
        return super().delete()

    def alive(self):
        """Return only records that have not been soft-deleted."""
        return self.filter(deleted_at__isnull=True)

    def dead(self):
        """Return only soft-deleted records."""
        return self.filter(deleted_at__isnull=False)

    def restore(self):
        """Restore (un-delete) all records in the queryset."""
        return super().update(deleted_at=None)


class SoftDeleteManager(models.Manager):
    """Manager that returns only non-deleted records by default."""

    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db).filter(
            deleted_at__isnull=True
        )

    def all_with_deleted(self):
        """Return all records, including soft-deleted ones."""
        return SoftDeleteQuerySet(self.model, using=self._db)

    def deleted(self):
        """Return only soft-deleted records."""
        return self.all_with_deleted().dead()

    def restore(self, pk):
        """Restore a single record by primary key."""
        return self.all_with_deleted().filter(pk=pk).restore()
