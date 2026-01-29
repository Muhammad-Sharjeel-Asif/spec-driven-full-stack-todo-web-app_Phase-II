"""
HTTPS Redirect Middleware for production environments.

This middleware ensures all HTTP requests are redirected to HTTPS
for production security requirements.
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.types import ASGIApp, Scope, Receive, Send
from src.config.settings import settings


class HTTPSRedirectMiddleware(BaseHTTPMiddleware):
    """
    Middleware to enforce HTTPS in production environments.

    This middleware redirects all HTTP requests to HTTPS equivalents
    to ensure secure communication for production deployments.
    """

    def __init__(self, app: ASGIApp, force_https: bool = None):
        super().__init__(app)
        self.force_https = force_https if force_https is not None else settings.DEBUG is False

    async def dispatch(self, request: Request, call_next):
        # Check if we should enforce HTTPS based on environment
        if self.force_https and request.url.scheme == "http":
            # Redirect to HTTPS version of the same URL
            https_url = str(request.url).replace("http://", "https://", 1)
            return RedirectResponse(url=https_url, status_code=301)

        # Continue with normal request processing
        response = await call_next(request)
        return response


def add_security_headers(response, is_production: bool = None):
    """
    Add security headers to responses for enhanced security.

    Args:
        response: The response object to add headers to
        is_production: Whether to apply production security headers
    """
    if is_production is None:
        from src.config.settings import settings
        is_production = settings.DEBUG is False

    # Add security headers for production
    if is_production:
        # Prevent MIME type sniffing
        response.headers.setdefault("X-Content-Type-Options", "nosniff")

        # Prevent clickjacking
        response.headers.setdefault("X-Frame-Options", "DENY")

        # XSS protection
        response.headers.setdefault("X-XSS-Protection", "1; mode=block")

        # Referrer policy
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")

        # Content Security Policy
        response.headers.setdefault(
            "Content-Security-Policy",
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self' https://*.supabase.co; "
            "frame-ancestors 'none';"
        )

    # Always add Strict-Transport-Security for HTTPS
    if is_production:
        response.headers.setdefault(
            "Strict-Transport-Security",
            "max-age=31536000; includeSubDomains; preload"
        )

    return response