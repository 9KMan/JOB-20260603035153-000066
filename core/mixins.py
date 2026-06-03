"""
Reusable model mixins for the data layer.
"""
import uuid

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .managers import SoftDeleteManager, SoftDeleteQuerySet


class UUIDPrimaryKeyMixin(models.Model):
    """Mixin that adds a UUID primary key column."""

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True,
        verbose_name=_("ID"),
    )

    class Meta:
        abstract = True


class TimestampMixin(models.Model):
    """Mixin that adds created_at and updated_at columns."""

    created_at = models.DateTimeField(
        auto_now_add=True,
        editable=False,
        db_index=True,
        verbose_name=_("created at"),
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        editable=False,
        db_index=True,
        verbose_name=_("updated at"),
    )

    class Meta:
        abstract = True


class SoftDeleteMixin(models.Model):
    """Mixin that implements the soft-delete pattern."""

    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        editable=False,
        db_index=True,
        verbose_name=_("deleted at"),
    )

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True
        base_manager_name = "objects"

    def delete(self, using=None, keep_parents=False):
        """Soft-delete the instance."""
        self.deleted_at = timezone.now()
        self.save(update_fields=["deleted_at", "updated_at"] if hasattr(self, "updated_at") else ["deleted_at"])

    def hard_delete(self, using=None, keep_parents=False):
        """Permanently delete the instance."""
        return super().delete(using=using, keep_parents=keep_parents)

    def restore(self):
        """Restore a soft-deleted instance."""
        self.deleted_at = None
        self.save(update_fields=["deleted_at", "updated_at"] if hasattr(self, "updated_at") else ["deleted_at"])

    @property
    def is_deleted(self):
        return self.deleted_at is not None


class BaseModel(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """Convenience base model combining all three mixins."""

    class Meta:
        abstract = True
        ordering = ["-created_at"]
