"""Django admin registration for core models."""
from django.contrib import admin

from .models import AuditLog, Tag, Tagging


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "color", "created_at")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Tagging)
class TaggingAdmin(admin.ModelAdmin):
    list_display = ("tag", "content_type", "object_id", "created_at")
    list_filter = ("content_type",)
    search_fields = ("tag__name",)


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("actor", "action", "object_repr", "created_at")
    list_filter = ("action", "content_type")
    search_fields = ("object_repr", "actor__email")
    readonly_fields = tuple(f.name for f in AuditLog._meta.fields)
