from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Gemini API
    gemini_api_key: str

    # Optional services
    jina_api_key: str = ""
    serper_api_key: str = ""

    # App behaviour
    max_pages_per_competitor: int = 4
    request_timeout_seconds: int = 15
    max_tokens_per_chunk: int = 6000
    default_model: str = "gemini-2.0-flash"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()