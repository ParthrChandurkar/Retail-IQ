"""Environment-backed application settings."""

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables."""

    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@db:5432/retail_bi",
        validation_alias="DATABASE_URL",
    )
    environment: str = Field(default="development", validation_alias="ENV")
    data_raw_dir: Path = Field(
        default=Path("../data/raw"), validation_alias="DATA_RAW_DIR"
    )
    report_dir: Path = Field(
        default=Path("../analytics/reports"), validation_alias="REPORT_DIR"
    )

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    """Return the process-wide immutable settings instance."""
    return Settings()
