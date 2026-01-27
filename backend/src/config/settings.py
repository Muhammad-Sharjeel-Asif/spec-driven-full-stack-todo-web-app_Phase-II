from pydantic_settings import BaseSettings
from typing import Optional
from datetime import timedelta


class Settings(BaseSettings):
    """
    Application settings configuration using Pydantic settings.
    Loads configuration from environment variables.
    """

    # Database configuration for Neon Serverless PostgreSQL
    DATABASE_URL: str

    # Better Auth configuration (for verifying tokens issued by frontend)
    BETTER_AUTH_SECRET: str
    # Note: Backend only verifies tokens issued by Better Auth, does not issue its own tokens

    # Password hashing configuration
    BCRYPT_ROUNDS: int = 12

    # Database configuration additional settings
    DB_ECHO: str = "false"
    # Note: Connection pooling settings are typically managed by Neon for serverless instances
    # DB_POOL_SIZE, DB_MAX_OVERFLOW, DB_POOL_TIMEOUT, DB_POOL_RECYCLE may not be needed for Neon Serverless

    # Debug mode
    DEBUG: bool = False

    # Server configuration
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8000
    API_V1_STR: str = "/api/v1"

    # CORS configuration
    BACKEND_CORS_ORIGINS: str = "*"  # Comma-separated list of origins

    class Config:
        env_file = ".env"
        case_sensitive = True

    @property
    def access_token_expire_delta(self) -> timedelta:
        """Get access token expiration as timedelta."""
        return timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)

    @property
    def refresh_token_expire_delta(self) -> timedelta:
        """Get refresh token expiration as timedelta."""
        return timedelta(days=self.REFRESH_TOKEN_EXPIRE_DAYS)


# Create a singleton instance of settings
settings = Settings()
