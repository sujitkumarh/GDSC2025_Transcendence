"""
Configuration settings for Transcendence backend.
Environment-driven configuration with secure defaults.
"""
import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application Info
    APP_NAME: str = "Transcendence - Green Agents of Change"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "AI-powered assistant ecosystem for Brazilian youth green job exploration"
    
    # Server Configuration
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    DEBUG: bool = Field(default=True, env="DEBUG")
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:5173", "http://127.0.0.1:5173"], 
        env="CORS_ORIGINS"
    )
    
    # AWS Mistral AI Configuration
    AWS_REGION: str = Field(default="us-east-1", env="AWS_REGION")
    AWS_MISTRAL_MODEL: str = Field(
        default="mistral.mistral-7b-instruct-v0:2", 
        env="AWS_MISTRAL_MODEL"
    )
    AWS_ACCESS_KEY_ID: Optional[str] = Field(default=None, env="AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: Optional[str] = Field(default=None, env="AWS_SECRET_ACCESS_KEY")
    AWS_SESSION_TOKEN: Optional[str] = Field(default=None, env="AWS_SESSION_TOKEN")
    
    # Development Settings
    MOCK_MODE: bool = Field(default=True, env="MOCK_MODE")
    TELEMETRY_ENABLED: bool = Field(default=True, env="TELEMETRY_ENABLED")
    
    # Database Configuration
    DATABASE_URL: str = Field(default="sqlite:///./transcendence.db", env="DATABASE_URL")
    DATA_DIR: str = Field(default="./data", env="DATA_DIR")
    
    # Security Settings
    SECRET_KEY: str = Field(
        default="transcendence_dev_secret_key_change_in_production", 
        env="SECRET_KEY"
    )
    TOKEN_EXPIRE_MINUTES: int = Field(default=60, env="TOKEN_EXPIRE_MINUTES")
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    RATE_LIMIT_WINDOW: int = Field(default=60, env="RATE_LIMIT_WINDOW")
    
    # Caching Configuration
    CACHE_TTL: int = Field(default=3600, env="CACHE_TTL")  # 1 hour
    CACHE_MAX_SIZE: int = Field(default=1000, env="CACHE_MAX_SIZE")
    
    # Agent Configuration
    DEFAULT_TEMPERATURE: float = Field(default=0.7, env="DEFAULT_TEMPERATURE")
    MAX_TOKENS: int = Field(default=500, env="MAX_TOKENS")
    CONTEXT_WINDOW: int = Field(default=2000, env="CONTEXT_WINDOW")
    
    # Internationalization
    DEFAULT_LANGUAGE: str = Field(default="en", env="DEFAULT_LANGUAGE")
    SUPPORTED_LANGUAGES: List[str] = Field(
        default=["en", "pt-BR"], 
        env="SUPPORTED_LANGUAGES"
    )
    
    # Analytics Configuration
    ANALYTICS_RETENTION_DAYS: int = Field(default=90, env="ANALYTICS_RETENTION_DAYS")
    ENABLE_DETAILED_LOGGING: bool = Field(default=True, env="ENABLE_DETAILED_LOGGING")
    
    # Content Configuration
    MAX_RECOMMENDATIONS: int = Field(default=5, env="MAX_RECOMMENDATIONS")
    MIN_RELEVANCE_SCORE: float = Field(default=0.3, env="MIN_RELEVANCE_SCORE")
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }
        
    def get_aws_credentials(self) -> dict:
        """Get AWS credentials for Mistral AI"""
        if self.MOCK_MODE:
            return {"mock_mode": True}
            
        return {
            "aws_access_key_id": self.AWS_ACCESS_KEY_ID,
            "aws_secret_access_key": self.AWS_SECRET_ACCESS_KEY,
            "aws_session_token": self.AWS_SESSION_TOKEN,
            "region_name": self.AWS_REGION
        }
    
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return not self.DEBUG and not self.MOCK_MODE
    
    def get_cors_origins(self) -> List[str]:
        """Get CORS origins as list"""
        if isinstance(self.CORS_ORIGINS, str):
            return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
        return self.CORS_ORIGINS


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Global settings instance
settings = get_settings()