"""
User-related models. The custom User model is defined here.
"""
import uuid

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from core.mixins import TimestampMixin, UUIDPrimaryKeyMixin
from .managers import UserManager

phone_regex = RegexValidator(
    regex=r"^\+?1?\d{9,15}$",
    message=_("Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."),
)


class User(AbstractBaseUser, PermissionsMixin, UUIDPrimaryKeyMixin, TimestampMixin):
    """Custom user model keyed on email with a UUID primary key."""

    class Status(models.TextChoices):
        ACTIVE = "active", _("Active")
        INVITED = "invited", _("Invited")
        SUSPENDED = "suspended", _("Suspended")
        DEACTIVATED = "deactivated", _("Deactivated")

    email = models.EmailField(
        unique=True,
        db_index=True,
        verbose_name=_("email address"),
    )
    first_name = models.CharField(
        max_length=80,
        blank=True,
        default="",
        verbose_name=_("first name"),
    )
    last_name = models.CharField(
        max_length=80,
        blank=True,
        default="",
        verbose_name=_("last name"),
    )
    display_name = models.CharField(
        max_length=160,
        blank=True,
        default="",
        verbose_name=_("display name"),
    )
    avatar_url = models.URLField(
        max_length=512,
        blank=True,
        default="",
        verbose_name=_("avatar URL"),
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        default="",
        validators=[phone_regex],
        verbose_name=_("phone"),
    )
    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.ACTIVE,
        db_index=True,
        verbose_name=_("status"),
    )
    locale = models.CharField(
        max_length=16,
        blank=True,
        default="en",
        verbose_name=_("locale"),
    )
    timezone_name = models.CharField(
        max_length=64,
        blank=True,
        default="UTC",
        verbose_name=_("timezone"),
    )
    last_login_ip = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name=_("last login IP"),
    )
    is_staff = models.BooleanField(default=False, verbose_name=_("staff status"))
    is_active = models.BooleanField(default=True, verbose_name=_("active"))
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        editable=False,
        db_index=True,
        verbose_name=_("deleted at"),
    )
    date_joined = models.DateTimeField(
        default=timezone.now,
        editable=False,
        verbose_name=_("date joined"),
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: list[str] = []

    objects = UserManager()
    all_objects = models.Manager()

    class Meta:
        db_table = "accounts_user"
        verbose_name = _("user")
        verbose_name_plural = _("users")
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["status", "is_active"]),
            models.Index(fields=["-date_joined"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["email"],
                name="accounts_user_email_unique",
            ),
        ]

    # ---- Soft-delete support ----
    def delete(self, using=None, keep_parents=False):
        self.deleted_at = timezone.now()
        self.is_active = False
        self.save(update_fields=["deleted_at", "is_active", "updated_at"])

    def hard_delete(self, using=None, keep_parents=False):
        return super().delete(using=using, keep_parents=keep_parents)

    def restore(self):
        self.deleted_at = None
        self.is_active = True
        self.save(update_fields=["deleted_at", "is_active", "updated_at"])

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip() or self.display_name or self.email

    def __str__(self) -> str:
        return self.email


class APIKey(UUIDPrimaryKeyMixin, TimestampMixin):
    """Long-lived API tokens used for service-to-service authentication."""

    class Status(models.TextChoices):
        ACTIVE = "active", _("Active")
        REVOKED = "revoked", _("Revoked")
        EXPIRED = "expired", _("Expired")

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="api_keys",
        verbose_name=_("user"),
    )
    name = models.CharField(
        max_length=120,
        verbose_name=_("name"),
    )
    key_prefix = models.CharField(
        max_length=12,
        db_index=True,
        verbose_name=_("key prefix"),
    )
    key_hash = models.CharField(
        max_length=128,
        unique=True,
        verbose_name=_("key hash"),
    )
    last_used_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name=_("last used at"),
    )
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name=_("expires at"),
    )
    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.ACTIVE,
        db_index=True,
        verbose_name=_("status"),
    )

    class Meta:
        db_table = "accounts_api_key"
        ordering = ["-created_at"]
        verbose_name = _("API key")
        verbose_name_plural = _("API keys")
        indexes = [
            models.Index(fields=["user", "status"]),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.key_prefix}…)"

    @property
    def is_expired(self) -> bool:
        return self.expires_at is not None and self.expires_at <= timezone.now()

    @property
    def is_usable(self) -> bool:
        return self.status == self.Status.ACTIVE and not self.is_expired
