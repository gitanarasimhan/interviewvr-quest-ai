from __future__ import annotations

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Load configuration from environment variables.
    
    Example .env file:
        OPENAI_API_KEY=sk-...
        OPENAI_MODEL=gpt-4o-mini
        WHISPER_MODEL=whisper-1
        APP_ENV=development
    """
    
    openai_api_key: str
    openai_model: str = "gpt-4o-mini"
    whisper_model: str = "whisper-1"
    app_env: str = "development"
    api_base_url: str = "http://localhost:8000"

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()
