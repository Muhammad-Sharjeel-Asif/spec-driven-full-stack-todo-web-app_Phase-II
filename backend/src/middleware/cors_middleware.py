from fastapi.middleware.cors import CORSMiddleware
from typing import List
from ..config.settings import settings


def add_cors_middleware(app):
    """
    Add CORS middleware to the FastAPI application with specific origins.

    This function configures CORS to allow only specific origins as defined
    in the BACKEND_CORS_ORIGINS setting, enhancing security by restricting
    cross-origin requests to only trusted domains.

    Args:
        app: The FastAPI application instance
    """
    # Parse the comma-separated list of origins from settings
    origins = []
    if settings.BACKEND_CORS_ORIGINS:
        origins = [origin.strip() for origin in settings.BACKEND_CORS_ORIGINS.split(",")]
    else:
        # Default to localhost origins if no specific origins are configured
        origins = [
            "http://localhost:3000",  # Default Next.js dev server
            "http://localhost:3001",  # Alternative Next.js dev server
            "http://127.0.0.1:3000",  # Alternative localhost format
            "http://127.0.0.1:3001",  # Alternative localhost format
        ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,  # Allow cookies and authorization headers
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],  # Allow specific HTTP methods
        allow_headers=["*"],  # Allow all headers including Authorization
        # Expose headers that browsers can access in response
        expose_headers=["Access-Control-Allow-Origin", "Access-Control-Allow-Credentials"],
        # Set max age for preflight requests (in seconds)
        max_age=86400,  # 24 hours
    )


def get_allowed_origins() -> List[str]:
    """
    Get the list of allowed origins from settings.

    Returns:
        List of allowed origins for CORS configuration
    """
    if settings.BACKEND_CORS_ORIGINS:
        return [origin.strip() for origin in settings.BACKEND_CORS_ORIGINS.split(",")]
    else:
        return [
            "http://localhost:3000",
            "http://localhost:3001",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:3001",
        ]