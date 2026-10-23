"""Typed, environment-derived application configuration."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "BizIntel AI"
    environment: str = "development"
    log_level: str = "INFO"
    database_url: str | None = None
    analytics_database_url: str | None = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
