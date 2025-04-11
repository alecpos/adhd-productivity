"""
Configuration settings for the ADHD Calendar application.

This module provides access to application configuration settings from various sources
(environment variables, configuration files, etc.) through a unified settings object.
"""

import os
import secrets
from typing import Any, Dict, List, Optional, Union
from pathlib import Path

from pydantic import AnyHttpUrl, PostgresDsn, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file."""
    
    # General settings
    APP_NAME: str = "ADHD Calendar"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    
    # Database settings
    DB_CONNECTION_STRING: str = "sqlite:///./adhd_calendar.db"
    
    # Security settings
    SECRET_KEY: str = "change_this_in_production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 60 * 24  # 24 hours
    
    # ML model settings
    MODEL_DIRECTORY: str = "app/ml/models"
    FAIRNESS_AUDIT_DIRECTORY: str = "app/ml/audit_reports"
    
    # Fairness thresholds
    FAIRNESS_THRESHOLDS: Dict[str, float] = {
        "disparate_impact": 0.8,
        "statistical_parity_difference": 0.1,
        "equal_opportunity_difference": 0.1,
        "average_odds_difference": 0.1,
    }
    
    # Explanation settings
    EXPLANATION_MIN_CONFIDENCE: float = 0.6
    EXPLANATION_VISUAL_ENABLED: bool = True
    
    # Fallback settings
    FALLBACK_DEFAULT_CONFIDENCE_THRESHOLD: float = 0.7
    FALLBACK_TIMEOUT_SECONDS: float = 5.0
    
    # Logging settings
    LOG_LEVEL: str = "INFO"
    
    # App settings
    PROJECT_NAME: str = "ADHD Calendar API"
    APP_ENV: str = os.getenv("APP_ENV", "development")
    TESTING: bool = os.getenv("TESTING", "false").lower() == "true"
    API_V1_STR: str = "/api/v1"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    SERVER_NAME: str = "localhost"
    SERVER_HOST: AnyHttpUrl = "http://localhost:8000"
    # BACKEND_CORS_ORIGINS is a JSON-formatted list of origins
    # e.g: '["http://localhost", "http://localhost:4200", "http://localhost:3000", \
    # "http://localhost:8080", "http://local.dockertoolbox.tiangolo.com"]'
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        """Parse CORS origins."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # AI/ML settings
    HUGGINGFACE_API_KEY: str = os.getenv("HUGGINGFACE_API_KEY", "")
    HUGGINGFACE_TEXT_MODEL: str = os.getenv("HUGGINGFACE_TEXT_MODEL", "deepseek-ai/DeepSeek-R1")
    HUGGINGFACE_SENTIMENT_MODEL: str = os.getenv(
        "HUGGINGFACE_SENTIMENT_MODEL", 
        "distilbert-base-uncased-finetuned-sst-2-english"
    )
    HUGGINGFACE_TASK_MODEL: str = os.getenv(
        "HUGGINGFACE_TASK_MODEL", 
        "microsoft/deberta-v3-base"
    )

    # Database settings
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "adhd_calendar")
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:postgres@localhost:5432/adhd_calendar",
    )
    TEST_DATABASE_URL: str = os.getenv(
        "TEST_DATABASE_URL",
        "postgresql+asyncpg://postgres:postgres@localhost:5432/adhd_calendar_test",
    )
    DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "20"))
    DB_POOL_MIN_SIZE: int = int(os.getenv("DB_POOL_MIN_SIZE", "5"))
    DB_POOL_MAX_OVERFLOW: int = int(os.getenv("DB_POOL_MAX_OVERFLOW", "10"))
    DB_POOL_TIMEOUT: int = int(os.getenv("DB_POOL_TIMEOUT", "30"))
    DB_POOL_RECYCLE: int = int(os.getenv("DB_POOL_RECYCLE", "1800"))
    DB_ECHO: bool = os.getenv("DB_ECHO", "false").lower() == "true"

    # Redis settings
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    REDIS_SSL: bool = os.getenv("REDIS_SSL", "false").lower() == "true"
    REDIS_TIMEOUT: int = int(os.getenv("REDIS_TIMEOUT", "5"))
    REDIS_CACHE_TTL: int = int(os.getenv("REDIS_CACHE_TTL", "3600"))
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")

    # JWT settings
    JWT_SECRET_KEY: str = secrets.token_urlsafe(32)
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    JWT_REFRESH_SECRET_KEY: str = os.getenv(
        "JWT_REFRESH_SECRET_KEY", "your-refresh-secret-key-for-testing"
    )

    # Security settings
    BCRYPT_ROUNDS: int = 12
    PASSWORD_MIN_LENGTH: int = 8
    PASSWORD_MAX_LENGTH: int = 50

    # Email settings
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM_EMAIL: Optional[str] = os.getenv("SMTP_FROM_EMAIL")
    VERIFY_EMAIL: bool = os.getenv("VERIFY_EMAIL", "false").lower() == "true"
    RESET_PASSWORD_TOKEN_EXPIRE_HOURS: int = int(
        os.getenv("RESET_PASSWORD_TOKEN_EXPIRE_HOURS", "48")
    )

    # Google Calendar settings
    GOOGLE_CREDENTIALS_PATH: Path = Path("credentials.json")
    GOOGLE_TOKEN_PATH: Path = Path("token.json")

    # BioAuth-25 configuration
    BIOAUTH_API_BASE_URL: str = "https://api.bioauth.example.com/v1"
    BIOAUTH_API_KEY: str = "dummy_api_key"
    BIOAUTH_CLIENT_ID: str = "adhd_calendar_app"
    BIOAUTH_CLIENT_SECRET: str = secrets.token_urlsafe(32)
    BIOAUTH_ENABLED: bool = True
    
    # Post-Quantum Cryptography Configuration
    PQ_ENABLED: bool = True
    PQ_DEFAULT_ALGORITHM: str = "ml_kem_768"  # ML-KEM-768 (NIST level 3)
    PQ_TLS_MIN_VERSION: str = "TLS1.3"
    PQ_HYBRID_MODE: bool = True  # Use both classical and PQ crypto
    
    # ML Services Configuration
    ML_MODEL_DIR: str = "app/ml/saved_models"
    ML_DATA_DIR: str = "app/ml/data"
    ML_LOGS_DIR: str = "app/ml/logs"
    HYPERFOLD_MODEL_PATH: str = "app/ml/saved_models/hyperfold_v2.pt"

    class Config:
        """Pydantic config."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "allow"


# Create global settings instance
settings = Settings()

def get_settings() -> Settings:
    """Get application settings."""
    return settings
