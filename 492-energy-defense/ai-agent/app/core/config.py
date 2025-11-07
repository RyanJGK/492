"""AI Agent configuration"""

from functools import lru_cache
from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """AI Agent settings"""
    
    DATABASE_URL: PostgresDsn = Field(
        default="postgresql://postgres:postgres@postgres:5432/energy_defense",
        description="PostgreSQL connection string",
    )
    
    MODEL_PATH: str = Field(
        default="/app/models",
        description="Path to store ML models",
    )
    
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    DEBUG: bool = Field(default=False, description="Debug mode")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
