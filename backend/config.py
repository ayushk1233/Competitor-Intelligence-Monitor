from functools import lru_cache

from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class Settings(BaseSettings):
    # OpenRouter API
    openrouter_api_key: str = ""

    # Optional services
    jina_api_key: str = ""
    serper_api_key: str = ""

    # Infrastructure (set in docker-compose, default to local dev values)
    database_url: str = "postgresql+asyncpg://cim_user:cim_password@localhost:5432/competitor_intel"
    redis_url: str = "redis://localhost:6379/0"

    # App behaviour
    max_pages_per_competitor: int = 6
    request_timeout_seconds: int = 15
    max_tokens_per_chunk: int = 6000
    default_model: str = "anthropic/claude-3-haiku"

    # Email
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from_email: str = ""
    admin_email: str = ""

    # Slack
    slack_webhook_url: str = ""

    # Feature Flags
    enable_email_notifications: bool = False
    enable_slack_notifications: bool = False
    enable_webhook_notifications: bool = True

    # JWT
    jwt_secret_key: str = "CHANGE_THIS_IN_PRODUCTION"
    jwt_algorithm: str = "HS256"
    jwt_expire_hours: int = 24

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()