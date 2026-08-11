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
    jwt_secret: str = Field(default="change-me", validation_alias="JWT_SECRET")
    jwt_access_expire_minutes: int = Field(
        default=30, validation_alias="JWT_ACCESS_EXPIRE_MINUTES"
    )
    jwt_refresh_expire_days: int = Field(
        default=14, validation_alias="JWT_REFRESH_EXPIRE_DAYS"
    )
    admin_email: str | None = Field(default=None, validation_alias="ADMIN_EMAIL")
    admin_password: str | None = Field(default=None, validation_alias="ADMIN_PASSWORD")
    cors_origins: str = Field(
        default="http://localhost:3000", validation_alias="CORS_ORIGINS"
    )
    powerbi_reader_password: str | None = Field(
        default=None, validation_alias="POWERBI_READER_PASSWORD"
    )
    data_raw_dir: Path = Field(
        default=Path("../data/raw"), validation_alias="DATA_RAW_DIR"
    )
    report_dir: Path = Field(
        default=Path("../analytics/reports"), validation_alias="REPORT_DIR"
    )
    model_registry_dir: Path = Field(
        default=Path("ml/registry"), validation_alias="MODEL_REGISTRY_DIR"
    )

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        """Return configured browser origins without empty entries."""
        return [
            origin.strip() for origin in self.cors_origins.split(",") if origin.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    """Return the process-wide immutable settings instance."""
    return Settings()
