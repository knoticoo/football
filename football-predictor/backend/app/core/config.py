"""
Configuration settings for the Football Prediction API
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Football Prediction API"
    VERSION: str = "1.0.0"
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8001  # Different port to avoid conflicts
    DEBUG: bool = False
    
    # CORS Configuration
    ALLOWED_HOSTS: List[str] = [
        "http://localhost:3001",  # Frontend port
        "http://localhost:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:3000",
        # Note: Ports 5000 and 5001 are occupied by existing services
    ]
    
    # Database Configuration
    DATABASE_URL: str = "sqlite:///./football_predictor.db"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Telegram Bot Configuration
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    TELEGRAM_WEBHOOK_URL: Optional[str] = None
    TELEGRAM_WEBHOOK_PORT: int = 8002  # Different port for bot webhook
    
    # External APIs
    FOOTBALL_DATA_API_KEY: Optional[str] = None
    FOOTBALL_DATA_BASE_URL: str = "https://api.football-data.org/v4"
    
    API_SPORTS_KEY: Optional[str] = None
    API_SPORTS_BASE_URL: str = "https://v3.football.api-sports.io"
    
    # Redis Configuration (for Celery)
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Prediction Engine
    PREDICTION_CONFIDENCE_THRESHOLD: float = 0.6
    MAX_PREDICTIONS_PER_USER: int = 100
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60  # seconds
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()