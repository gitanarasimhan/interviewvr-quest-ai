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

    # HMAC request signing
    require_signature: bool = False
    signature_max_age_seconds: int = 300

    # Conversation session management
    session_history_window: int = 6
    session_max_questions: int = 6
    session_ttl_seconds: int = 3600

    # Directory audio files must live under for /api/interview/transcribe
    # (prevents path traversal to arbitrary filesystem locations).
    audio_upload_dir: str = "uploads"

    # Rate limiting (requests per minute per IP)
    rate_limit_requests: int = 60
    rate_limit_window: int = 60

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()
