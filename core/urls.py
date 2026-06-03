"""URL routes for the core app (audit logs and tags)."""
from django.urls import path

from . import views

urlpatterns = [
    path("tags/", views.TagListCreateView.as_view(), name="tag-list"),
    path("tags/<uuid:pk>/", views.TagDetailView.as_view(), name="tag-detail"),
    path("audit-logs/", views.AuditLogListView.as_view(), name="audit-log-list"),
]
