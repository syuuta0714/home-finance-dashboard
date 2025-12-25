"""Configuration management for the backend application"""

import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Database
    database_url: str = "sqlite:////data/home_finance.db"
    
    # Timezone
    timezone: str = "Asia/Tokyo"
    
    # Logging
    log_level: str = "INFO"
    
    # CORS
    cors_origins: List[str] = ["*"]
    
    # API
    api_prefix: str = "/api"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
