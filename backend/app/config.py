"""Configuration management for the backend application"""

import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    """Application settings"""
    
    model_config = ConfigDict(extra='ignore')
    
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


# Global settings instance
settings = Settings()
