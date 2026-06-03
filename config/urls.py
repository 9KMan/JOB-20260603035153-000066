"""URL configuration for config project."""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include("core.urls")),
    path("api/v1/accounts/", include("accounts.urls")),
    path("api/v1/organizations/", include("organizations.urls")),
    path("api/v1/projects/", include("projects.urls")),
    path("api/v1/tasks/", include("tasks.urls")),
]
