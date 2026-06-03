"""Centralized application configuration loaded from environment variables."""
from functools import lru_cache
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings sourced from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = Field(default="app", description="Service name")
    app_version: str = Field(default="0.1.0", description="Service version")
    environment: str = Field(default="development", description="deployment environment")
    secret_key: str = Field(..., min_length=16, description="application secret")
    cors_origins: str = Field(default="*", description="comma separated allowed origins")
    log_level: str = Field(default="INFO")

    # Database
    database_url: str = Field(..., description="SQLAlchemy database URL")
    db_pool_size: int = Field(default=5, ge=1)
    db_max_overflow: int = Field(default=10, ge=0)
    db_pool_recycle: int = Field(default=1800, ge=60)
    db_echo: bool = Field(default=False)

    # Celery
    celery_broker_url: str = Field(default="redis://redis:6379/0")
    celery_result_backend: str = Field(default="redis://redis:6379/1")

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, value: str) -> str:
        allowed = {"development", "staging", "production", "test"}
        if value not in allowed:
            raise ValueError(f"environment must be one of {allowed}")
        return value

    @property
    def cors_origins_list(self) -> List[str]:
        if self.cors_origins.strip() == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]


settings = get_settings()
