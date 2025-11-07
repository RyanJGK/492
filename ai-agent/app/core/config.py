"""
AI Agent configuration management.
"""

from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """AI Agent settings with environment variable support."""
    
    # Application
    APP_NAME: str = "492-Energy-Defense AI Agent"
    VERSION: str = "1.0.0"
    
    # OpenRouter API
    OPENROUTER_API_KEY: str
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    DEFAULT_MODEL: str = "anthropic/claude-3.5-sonnet"
    
    # Analysis settings
    MAX_TOKENS: int = 4096
    TEMPERATURE: float = 0.7
    TOP_P: float = 0.9
    
    # Cache settings
    CACHE_DIR: str = "/app/cache"
    CACHE_ENABLED: bool = True
    CACHE_TTL_HOURS: int = 24
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="allow"
    )


# Global settings instance
settings = Settings()
