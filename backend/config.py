"""Configuration management for Energy Defense backend."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    DATABASE_URL: str = "postgresql://defense_user:SecureDefense2024!@localhost:5432/energy_defense"
    
    # Security
    JWT_SECRET: str = "your-secret-key-change-in-production-min-32-chars-long"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # AI Models
    MODEL_PATH: str = "./models"
    
    # Data Replay
    REPLAY_SPEED: int = 100  # Multiplier for timestamp replay
    
    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
