"""URLs for accounts."""
from rest_framework.routers import DefaultRouter

from .views import APIKeyViewSet, UserViewSet

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")
router.register(r"api-keys", APIKeyViewSet, basename="api-key")

urlpatterns = router.urls
