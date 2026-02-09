"""
Production configuration for the Todo Application Backend.

This configuration is used in production environments.
All sensitive values should be set via environment variables.
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Production settings for the application."""

    # Application
    APP_NAME: str = "Todo Application API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 4
    RELOAD: bool = False

    # Database
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    DATABASE_POOL_TIMEOUT: int = 30
    DATABASE_POOL_RECYCLE: int = 3600

    # JWT Authentication
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days

    # Password Security
    PASSWORD_MIN_LENGTH: int = 8
    PASSWORD_BCRYPT_ROUNDS: int = 12

    # Email Configuration
    SMTP_HOST: str
    SMTP_PORT: int = 587
    SMTP_USERNAME: str
    SMTP_PASSWORD: str
    SMTP_FROM_EMAIL: str
    SMTP_FROM_NAME: str = "Todo App"
    SMTP_USE_TLS: bool = True

    # Email Templates
    FRONTEND_URL: str
    PASSWORD_RESET_URL: str = "{FRONTEND_URL}/reset-password?token={token}"
    EMAIL_VERIFICATION_URL: str = "{FRONTEND_URL}/verify-email?token={token}"

    # Token Expiration
    PASSWORD_RESET_TOKEN_EXPIRE_HOURS: int = 1
    EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS: int = 24

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_STORAGE: str = "redis"
    REDIS_URL: Optional[str] = None

    # Rate Limit Rules (requests per window)
    RATE_LIMIT_REGISTER: int = 5
    RATE_LIMIT_REGISTER_WINDOW: int = 3600  # 1 hour
    RATE_LIMIT_LOGIN: int = 5
    RATE_LIMIT_LOGIN_WINDOW: int = 900  # 15 minutes
    RATE_LIMIT_FORGOT_PASSWORD: int = 5
    RATE_LIMIT_FORGOT_PASSWORD_WINDOW: int = 900  # 15 minutes
    RATE_LIMIT_RESEND_VERIFICATION: int = 3
    RATE_LIMIT_RESEND_VERIFICATION_WINDOW: int = 3600  # 1 hour

    # Account Lockout
    MAX_FAILED_LOGIN_ATTEMPTS: int = 5
    ACCOUNT_LOCKOUT_DURATION_MINUTES: int = 15

    # Security
    ALLOWED_ORIGINS: list[str] = [
        "https://todoapp.com",
        "https://www.todoapp.com"
    ]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_MAX_AGE: int = 3600

    # Security Headers
    HSTS_MAX_AGE: int = 31536000  # 1 year
    HSTS_INCLUDE_SUBDOMAINS: bool = True
    HSTS_PRELOAD: bool = True

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    LOG_FILE: Optional[str] = "/var/log/todoapp/app.log"

    # Monitoring
    SENTRY_DSN: Optional[str] = None
    SENTRY_ENVIRONMENT: str = "production"
    SENTRY_TRACES_SAMPLE_RATE: float = 0.1

    # Audit Logging
    AUDIT_LOG_ENABLED: bool = True
    AUDIT_LOG_RETENTION_DAYS: int = 90

    # Session Management (if implementing stateful sessions)
    SESSION_STORAGE: str = "database"  # or "redis"
    SESSION_EXPIRE_DAYS: int = 7
    SESSION_CLEANUP_INTERVAL_HOURS: int = 24

    # Feature Flags
    ENABLE_EMAIL_VERIFICATION: bool = True
    ENABLE_PASSWORD_RESET: bool = True
    ENABLE_RATE_LIMITING: bool = True
    ENABLE_AUDIT_LOGGING: bool = True

    # Performance
    ENABLE_QUERY_LOGGING: bool = False
    SLOW_QUERY_THRESHOLD_MS: int = 1000

    # Maintenance
    MAINTENANCE_MODE: bool = False
    MAINTENANCE_MESSAGE: str = "System is under maintenance. Please try again later."

    class Config:
        env_file = ".env.production"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Create settings instance
settings = Settings()


# Validation
def validate_settings():
    """Validate critical settings on startup."""
    errors = []

    # Check required settings
    if not settings.DATABASE_URL:
        errors.append("DATABASE_URL is required")

    if not settings.JWT_SECRET_KEY:
        errors.append("JWT_SECRET_KEY is required")
    elif len(settings.JWT_SECRET_KEY) < 32:
        errors.append("JWT_SECRET_KEY must be at least 32 characters")

    if not settings.SMTP_HOST:
        errors.append("SMTP_HOST is required")

    if not settings.SMTP_USERNAME:
        errors.append("SMTP_USERNAME is required")

    if not settings.SMTP_PASSWORD:
        errors.append("SMTP_PASSWORD is required")

    if not settings.FRONTEND_URL:
        errors.append("FRONTEND_URL is required")

    # Check security settings
    if settings.DEBUG:
        errors.append("DEBUG should be False in production")

    if "*" in settings.ALLOWED_ORIGINS:
        errors.append("ALLOWED_ORIGINS should not contain wildcard in production")

    # Check rate limiting
    if settings.RATE_LIMIT_ENABLED and not settings.REDIS_URL:
        errors.append("REDIS_URL is required when rate limiting is enabled")

    if errors:
        raise ValueError(f"Configuration errors:\n" + "\n".join(f"  - {e}" for e in errors))


# Validate on import
if settings.ENVIRONMENT == "production":
    validate_settings()
