"""
Configuration for Telegram Bot
"""

import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class BotConfig:
    """Bot configuration settings"""
    
    # Bot Configuration
    BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    WEBHOOK_URL: Optional[str] = os.getenv("TELEGRAM_WEBHOOK_URL")
    WEBHOOK_PORT: int = int(os.getenv("TELEGRAM_WEBHOOK_PORT", "8002"))
    
    # API Configuration
    API_BASE_URL: str = os.getenv("API_BASE_URL", "http://localhost:8001")
    API_V1_STR: str = "/api/v1"
    
    # Bot Settings
    BOT_USERNAME: Optional[str] = os.getenv("BOT_USERNAME")
    ADMIN_USER_IDS: list = [int(x) for x in os.getenv("ADMIN_USER_IDS", "").split(",") if x]
    
    # Rate Limiting
    RATE_LIMIT_MESSAGES: int = 30  # Messages per minute per user
    RATE_LIMIT_WINDOW: int = 60    # Seconds
    
    # Prediction Settings
    MAX_PREDICTIONS_PER_DAY: int = 10
    PREDICTION_DEADLINE_HOURS: int = 2  # Hours before match
    
    # Notification Settings
    NOTIFICATION_ENABLED: bool = True
    DAILY_PREDICTIONS_TIME: str = "09:00"  # UTC time
    MATCH_REMINDER_HOURS: int = 1  # Hours before match
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./football_predictor.db")
    
    # External APIs
    FOOTBALL_DATA_API_KEY: Optional[str] = os.getenv("FOOTBALL_DATA_API_KEY")
    API_SPORTS_KEY: Optional[str] = os.getenv("API_SPORTS_KEY")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = "bot.log"
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration"""
        if not cls.BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN is required")
        return True


# Create config instance
config = BotConfig()