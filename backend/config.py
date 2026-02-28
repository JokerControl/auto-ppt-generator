"""
Configuration management for AutoPPT Generator
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # App settings
    APP_NAME: str = "AutoPPT Generator"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # MiniMax API settings
    MINIMAX_API_KEY: Optional[str] = os.getenv("MINIMAX_API_KEY")
    MINIMAX_BASE_URL: str = "https://api.minimax.chat/v1"
    MINIMAX_MODEL: str = "abab6.5s-chat"
    
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Storage settings
    OUTPUT_DIR: str = "./output"
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./autoppt.db"
    
    # CORS
    CORS_ORIGINS: list = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
