import os
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Load configuration from environment variables.
    
    For local development:
        Create backend/.env with:
        OPENAI_API_KEY=sk-...
        OPENAI_MODEL=gpt-4o-mini
        WHISPER_MODEL=whisper-1
        APP_ENV=development
        QUEST_APP_SECRET=your-quest-app-secret  (for auth)
    
    For production (Heroku/AWS/etc):
        Set environment variables via platform UI or CLI:
        heroku config:set OPENAI_API_KEY=sk-...
        heroku config:set APP_ENV=production
    """
    
    openai_api_key: str
    openai_model: str = "gpt-4o-mini"
    whisper_model: str = "whisper-1"
    app_env: str = "development"
    api_base_url: str = "http://localhost:8000"
    quest_app_secret: str = "local-dev-secret-change-in-production"
    
    # Rate limiting (requests per minute per IP)
    rate_limit_requests: int = 60
    rate_limit_window: int = 60

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()
