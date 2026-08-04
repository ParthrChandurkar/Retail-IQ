"""Environment-backed application settings."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables."""

    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@db:5432/retail_bi",
        validation_alias="DATABASE_URL",
    )
    environment: str = Field(default="development", validation_alias="ENV")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    """Return the process-wide immutable settings instance."""
    return Settings()
