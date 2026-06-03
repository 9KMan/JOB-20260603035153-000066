"""ViewSets for accounts."""
from rest_framework import permissions, viewsets

from .models import APIKey, User
from .serializers import APIKeySerializer, UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = (
        User.objects.filter(deleted_at__isnull=True)
        .order_by("-date_joined")
    )
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ["email", "first_name", "last_name", "display_name"]
    ordering_fields = ["date_joined", "email"]

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_staff:
            qs = qs.filter(id=self.request.user.id)
        return qs


class APIKeyViewSet(viewsets.ModelViewSet):
    serializer_class = APIKeySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return APIKey.objects.select_related("user").filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
