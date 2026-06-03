"""Admin for accounts."""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import APIKey, User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    ordering = ("-date_joined",)
    list_display = ("email", "display_name", "status", "is_staff", "is_active", "date_joined")
    list_filter = ("status", "is_staff", "is_active")
    search_fields = ("email", "first_name", "last_name", "display_name")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Profile", {"fields": ("first_name", "last_name", "display_name", "avatar_url", "phone", "locale", "timezone_name")}),
        ("Status", {"fields": ("status", "is_active", "is_staff", "is_superuser", "deleted_at")}),
        ("Important dates", {"fields": ("last_login", "date_joined", "last_login_ip")}),
        ("Permissions", {"fields": ("groups", "user_permissions")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2"),
        }),
    )


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "key_prefix", "status", "expires_at", "last_used_at")
    list_filter = ("status",)
    search_fields = ("name", "user__email", "key_prefix")
    readonly_fields = ("key_hash", "last_used_at")
