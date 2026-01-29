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
    BETTER_AUTH_URL: str = "http://localhost:3000"
    NEXT_PUBLIC_BETTER_AUTH_URL: str = "http://localhost:3000"
    # Note: Backend only verifies tokens issued by Better Auth, does not issue its own tokens

    # Password hashing configuration
    BCRYPT_ROUNDS: int = 12

    # Token expiration settings (these are referenced in properties but not defined)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Database configuration additional settings
    DB_ECHO: str = "false"
    # Note: Connection pooling settings are typically managed by Neon for serverless instances
    # However, the database config file expects these values, so we define them with reasonable defaults
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 3600  # 1 hour

    # Debug mode
    DEBUG: bool = False

    # Server configuration
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8000
    API_V1_STR: str = "/api/v1"

    # CORS configuration
    BACKEND_CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000,https://localhost:3000"  # Comma-separated list of origins

    @property
    def ALLOWED_ORIGINS(self) -> list:
        """Parse comma-separated CORS origins into a list."""
        if self.BACKEND_CORS_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.BACKEND_CORS_ORIGINS.split(",") if origin.strip()]

    # SSL/HTTPS configuration
    SSL_REDIRECT: bool = True
    SECURE_SSL_REDIRECT: bool = True
    SECURE_PROXY_SSL_HEADER: tuple = ("X-Forwarded-Proto", "https")
    USE_HTTPS_INSTEAD_OF_SSL: bool = True

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
