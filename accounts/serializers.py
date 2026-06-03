"""Serializers for accounts."""
from rest_framework import serializers

from .models import User, APIKey


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "display_name",
            "full_name",
            "avatar_url",
            "phone",
            "status",
            "locale",
            "timezone_name",
            "is_active",
            "is_staff",
            "date_joined",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "is_staff", "date_joined", "created_at", "updated_at", "full_name"]


class APIKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = APIKey
        fields = [
            "id",
            "user",
            "name",
            "key_prefix",
            "last_used_at",
            "expires_at",
            "status",
            "created_at",
        ]
        read_only_fields = ["id", "key_prefix", "last_used_at", "created_at"]
