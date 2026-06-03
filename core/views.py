"""
Read-only / minimal views for the core app.
In a real codebase these would live in a separate API app, but
they are included here to round out the data model and provide
working URL examples.
"""
from rest_framework import generics, permissions

from .models import AuditLog, Tag
from .serializers import AuditLogSerializer, TagSerializer


class TagListCreateView(generics.ListCreateAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    search_fields = ["name", "slug"]
    ordering_fields = ["name", "created_at"]


class TagDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = "id"


class AuditLogListView(generics.ListAPIView):
    queryset = (
        AuditLog.objects.select_related("actor", "content_type")
        .all()
        .order_by("-created_at")
    )
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["action", "actor", "content_type"]
    ordering_fields = ["created_at"]
