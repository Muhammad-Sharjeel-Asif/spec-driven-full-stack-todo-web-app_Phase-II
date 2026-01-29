"""
Logging Middleware for API requests and security events.

This module implements comprehensive logging for API requests and security events
to provide visibility into application behavior and potential security issues.
"""
import json
import time
import uuid
from datetime import datetime
from typing import Callable, Awaitable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp, Scope, Receive, Send
import logging
from starlette.background import BackgroundTask


# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    ASGI Middleware for comprehensive request logging and security event tracking.

    This middleware logs all API requests with relevant information including
    client IP, user ID (when authenticated), request details, response status,
    and timing information. It also tracks potential security events.
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.logger = logger

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        # Generate a unique request ID for tracing
        request_id = str(uuid.uuid4())

        # Get client IP address
        client_ip = self._get_client_ip(request)

        # Start timer for request duration
        start_time = time.time()

        # Log the incoming request
        self._log_request_start(request, request_id, client_ip)

        try:
            # Process the request
            response = await call_next(request)

            # Calculate request duration
            duration = time.time() - start_time

            # Log the successful response
            self._log_response_success(request, response, request_id, client_ip, duration)

            # Add request ID to response headers for tracing
            response.headers["X-Request-ID"] = request_id

            return response

        except Exception as exc:
            # Calculate request duration even for exceptions
            duration = time.time() - start_time

            # Log the error
            self._log_request_error(request, exc, request_id, client_ip, duration)

            # Re-raise the exception
            raise exc

    def _get_client_ip(self, request: Request) -> str:
        """
        Extract client IP address from the request, considering potential proxy headers.

        Args:
            request: The incoming request

        Returns:
            Client IP address
        """
        # Check for forwarded-for header (common in proxy setups)
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            # Take the first IP if multiple are provided
            return forwarded_for.split(",")[0].strip()

        # Check for real-ip header (used by some proxies)
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip.strip()

        # Fall back to the direct client IP
        client_addr = request.client
        if client_addr and client_addr.host:
            return client_addr.host

        # Default fallback
        return "unknown"

    def _get_user_id(self, request: Request) -> str:
        """
        Extract user ID from the request if available.

        Args:
            request: The incoming request

        Returns:
            User ID if available, otherwise "anonymous"
        """
        # Check for authorization header to extract user info
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            # In a real implementation, we would decode the JWT to get user ID
            # For now, we'll return a placeholder
            return "authenticated_user"  # This would be extracted from JWT in real implementation

        return "anonymous"

    def _log_request_start(self, request: Request, request_id: str, client_ip: str):
        """
        Log the start of a request.

        Args:
            request: The incoming request
            request_id: Unique request ID
            client_ip: Client IP address
        """
        log_data = {
            "event": "request_started",
            "request_id": request_id,
            "method": request.method,
            "path": str(request.url.path),
            "client_ip": client_ip,
            "user_id": self._get_user_id(request),
            "timestamp": datetime.utcnow().isoformat(),
            "headers": {
                "user_agent": request.headers.get("user-agent", ""),
                "content_type": request.headers.get("content-type", ""),
                "accept": request.headers.get("accept", "")
            }
        }

        self.logger.info(f"REQUEST_START: {json.dumps(log_data)}")

    def _log_response_success(self, request: Request, response: Response, request_id: str, client_ip: str, duration: float):
        """
        Log a successful response.

        Args:
            request: The original request
            response: The response
            request_id: Unique request ID
            client_ip: Client IP address
            duration: Request duration in seconds
        """
        log_data = {
            "event": "response_completed",
            "request_id": request_id,
            "method": request.method,
            "path": str(request.url.path),
            "client_ip": client_ip,
            "user_id": self._get_user_id(request),
            "status_code": response.status_code,
            "duration_ms": round(duration * 1000, 2),
            "timestamp": datetime.utcnow().isoformat()
        }

        # Log different levels based on status code
        if 400 <= response.status_code < 500:
            self.logger.warning(f"CLIENT_ERROR: {json.dumps(log_data)}")
        elif 500 <= response.status_code < 600:
            self.logger.error(f"SERVER_ERROR: {json.dumps(log_data)}")
        else:
            self.logger.info(f"REQUEST_SUCCESS: {json.dumps(log_data)}")

    def _log_request_error(self, request: Request, exc: Exception, request_id: str, client_ip: str, duration: float):
        """
        Log an error during request processing.

        Args:
            request: The original request
            exc: The exception that occurred
            request_id: Unique request ID
            client_ip: Client IP address
            duration: Request duration in seconds
        """
        log_data = {
            "event": "request_error",
            "request_id": request_id,
            "method": request.method,
            "path": str(request.url.path),
            "client_ip": client_ip,
            "user_id": self._get_user_id(request),
            "error_type": type(exc).__name__,
            "error_message": str(exc),
            "duration_ms": round(duration * 1000, 2),
            "timestamp": datetime.utcnow().isoformat()
        }

        self.logger.error(f"REQUEST_ERROR: {json.dumps(log_data)}")

    def _log_security_event(self, request: Request, event_type: str, details: dict):
        """
        Log a security-related event.

        Args:
            request: The request associated with the security event
            event_type: Type of security event
            details: Additional details about the event
        """
        client_ip = self._get_client_ip(request)

        log_data = {
            "event": "security_event",
            "event_type": event_type,
            "method": request.method,
            "path": str(request.url.path),
            "client_ip": client_ip,
            "user_id": self._get_user_id(request),
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        }

        self.logger.warning(f"SECURITY_EVENT: {json.dumps(log_data)}")


# Alternative standalone logging middleware function
async def log_api_requests(app: ASGIApp, receive: Receive, send: Send) -> None:
    """
    Standalone logging function that can be used as middleware.

    Args:
        app: The ASGI application
        receive: Receive channel
        send: Send channel
    """
    scope = {}

    # This is a simplified version - the LoggingMiddleware class above is preferred
    await app(scope, receive, send)


def setup_logging_config():
    """
    Set up logging configuration for the application.
    """
    import logging.config

    LOGGING_CONFIG = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "()": "uvicorn.logging.DefaultFormatter",
                "fmt": "%(levelprefix)s %(asctime)s %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "default": {
                "formatter": "default",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stderr",
            },
        },
        "loggers": {
            "src.middleware.logging_middleware": {"handlers": ["default"], "level": "INFO"},
            "uvicorn.access": {"handlers": ["default"], "level": "INFO", "propagate": False},
            "uvicorn.error": {"handlers": ["default"], "level": "INFO", "propagate": False},
        },
    }

    logging.config.dictConfig(LOGGING_CONFIG)