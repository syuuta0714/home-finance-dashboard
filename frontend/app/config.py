"""Configuration management for the frontend application"""

import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Backend API
    backend_url: str = "http://home-finance-backend:8000"
    
    # Timezone
    timezone: str = "Asia/Tokyo"
    
    # Auto refresh
    auto_refresh_interval: int = 30  # seconds
    
    # Kiosk mode
    kiosk_mode: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
