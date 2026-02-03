from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database Configuration
    DATABASE_URL: str

    # JWT Configuration
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # API Configuration
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Todo App Phase II"

    # CORS Configuration
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    # Environment
    ENVIRONMENT: str = "development"

    # Authentication Toggle (for testing)
    DISABLE_AUTH: bool = False

    # OpenAI Configuration (Phase III - Chat Feature)
    OPENAI_API_KEY: str = "your-openai-api-key-here"
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    OPENAI_MAX_TOKENS: int = 1000
    OPENAI_TEMPERATURE: float = 0.7

    # Phase II API Configuration (for chat backend to call existing APIs)
    PHASE2_API_BASE_URL: str = "http://localhost:8000/api/v1"

    # Chat Configuration
    CHAT_SESSION_TIMEOUT_MINUTES: int = 30
    CHAT_MAX_MESSAGES_PER_SESSION: int = 20
    CHAT_MAX_CONTEXT_TURNS: int = 10

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
