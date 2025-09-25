"""
API Configuration settings
"""
import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings from environment variables."""

    # API Settings
    api_title: str = "SlayFlashcards API"
    api_version: str = "1.0.0"
    api_description: str = "REST API for SlayFlashcards - An interactive flashcard learning platform"

    # Server Settings
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    reload: bool = False
    workers: int = 1

    # Database Settings
    database_url: str = "sqlite:///./slayflashcards.db"
    database_echo: bool = False

    # Authentication Settings
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7

    # CORS Settings
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173"
    ]
    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = ["*"]
    cors_allow_headers: List[str] = ["*"]

    # Pagination Settings
    default_page_size: int = 20
    max_page_size: int = 100

    # File Upload Settings
    max_file_size_mb: int = 10
    allowed_file_extensions: List[str] = [".json", ".txt", ".csv"]

    # Logging Settings
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Redis Settings (optional, for caching)
    redis_url: str = "redis://localhost:6379/0"
    redis_enabled: bool = False

    # Rate Limiting Settings
    rate_limit_enabled: bool = True
    rate_limit_calls: int = 100
    rate_limit_period: int = 60  # seconds

    # Application Settings
    environment: str = "development"
    timezone: str = "UTC"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

        # Allow environment variable overrides
        env_prefix = "SLAY_"

        @classmethod
        def parse_env_var(cls, field_name: str, raw_val: str) -> any:
            if field_name == 'cors_origins':
                return [x.strip() for x in raw_val.split(',')]
            return cls.json_loads(raw_val)


# Create settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings."""
    return settings


# Environment-specific configurations
def is_development() -> bool:
    """Check if running in development mode."""
    return settings.environment.lower() in ["dev", "development", "local"]


def is_production() -> bool:
    """Check if running in production mode."""
    return settings.environment.lower() in ["prod", "production"]


def is_testing() -> bool:
    """Check if running in test mode."""
    return settings.environment.lower() in ["test", "testing"]


# Database URL helpers
def get_database_url() -> str:
    """Get database URL with environment variable support."""
    return os.getenv("DATABASE_URL", settings.database_url)


def is_sqlite() -> bool:
    """Check if using SQLite database."""
    return get_database_url().startswith("sqlite")


def is_postgresql() -> bool:
    """Check if using PostgreSQL database."""
    return get_database_url().startswith("postgresql")