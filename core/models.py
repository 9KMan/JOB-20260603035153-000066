"""
Core domain models. These models are shared across multiple apps
and provide the foundation for the data layer.
"""
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.mixins import BaseModel


class AuditLog(BaseModel):
    """Append-only audit log for tracking changes to important records."""

    class Action(models.TextChoices):
        CREATE = "create", _("Create")
        UPDATE = "update", _("Update")
        DELETE = "delete", _("Delete")
        RESTORE = "restore", _("Restore")
        LOGIN = "login", _("Login")
        LOGOUT = "logout", _("Logout")
        OTHER = "other", _("Other")

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
        verbose_name=_("actor"),
    )
    action = models.CharField(
        max_length=16,
        choices=Action.choices,
        default=Action.OTHER,
        db_index=True,
        verbose_name=_("action"),
    )
    object_id = models.UUIDField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name=_("object id"),
    )
    object_repr = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name=_("object representation"),
    )
    content_type = models.ForeignKey(
        "contenttypes.ContentType",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
        verbose_name=_("content type"),
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_("metadata"),
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name=_("IP address"),
    )
    user_agent = models.CharField(
        max_length=512,
        blank=True,
        default="",
        verbose_name=_("user agent"),
    )

    class Meta:
        db_table = "core_audit_log"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["actor", "action"]),
            models.Index(fields=["content_type", "object_id"]),
            models.Index(fields=["-created_at"]),
        ]
        verbose_name = _("audit log")
        verbose_name_plural = _("audit logs")

    def __str__(self):
        return f"{self.actor} {self.action} {self.object_repr}"


class Tag(BaseModel):
    """
    A reusable label that can be attached to any object via
    the generic Tagging junction table.
    """

    name = models.CharField(
        max_length=64,
        unique=True,
        db_index=True,
        verbose_name=_("name"),
    )
    slug = models.SlugField(
        max_length=80,
        unique=True,
        db_index=True,
        verbose_name=_("slug"),
    )
    description = models.TextField(
        blank=True,
        default="",
        verbose_name=_("description"),
    )
    color = models.CharField(
        max_length=7,
        blank=True,
        default="#cccccc",
        verbose_name=_("color (hex)"),
    )

    class Meta:
        db_table = "core_tag"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["name"]),
        ]
        verbose_name = _("tag")
        verbose_name_plural = _("tags")

    def __str__(self):
        return self.name


class Tagging(BaseModel):
    """
    Generic many-to-many relationship between Tags and any other model.
    Uses content types to support tagging of multiple model kinds.
    """

    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name="taggings",
        verbose_name=_("tag"),
    )
    content_type = models.ForeignKey(
        "contenttypes.ContentType",
        on_delete=models.CASCADE,
        related_name="taggings",
        verbose_name=_("content type"),
    )
    object_id = models.UUIDField(
        db_index=True,
        verbose_name=_("object id"),
    )

    class Meta:
        db_table = "core_tagging"
        unique_together = [("tag", "content_type", "object_id")]
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
            models.Index(fields=["tag", "content_type"]),
        ]
        verbose_name = _("tagging")
        verbose_name_plural = _("taggings")

    def __str__(self):
        return f"{self.tag} on {self.content_type}#{self.object_id}"
