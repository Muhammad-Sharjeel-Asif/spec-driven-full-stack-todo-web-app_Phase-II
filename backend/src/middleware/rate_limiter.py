"""
Rate Limiting Middleware for API endpoints.

This module implements rate limiting functionality to prevent abuse and ensure security
by controlling the number of requests a client can make within a specified time window.
"""
import time
from collections import defaultdict, deque
from typing import Dict, Deque
from fastapi import Request, HTTPException
from starlette.types import ASGIApp, Scope, Receive, Send
from starlette.responses import JSONResponse
import hashlib


class RateLimiter:
    """
    Rate limiter implementation that tracks requests per IP address and endpoint.

    This class provides rate limiting functionality with configurable limits per endpoint.
    """

    def __init__(self):
        # Dictionary to store request timestamps per IP and endpoint
        # Format: {(ip, endpoint): deque of timestamps}
        self.requests: Dict[tuple, Deque[float]] = defaultdict(deque)

        # Default rate limits per endpoint (requests per minute)
        self.limits = {
            "/api/{user_id}/tasks": {"requests": 100, "window": 60},  # 100 requests per minute for tasks
            "/api/{user_id}/tasks/{task_id}": {"requests": 50, "window": 60},  # 50 requests per minute for specific task
            "/api/auth/login": {"requests": 5, "window": 300},  # 5 login attempts per 5 minutes
            "/api/auth/register": {"requests": 2, "window": 3600},  # 2 registrations per hour
            "/api/auth/me": {"requests": 20, "window": 60},  # 20 profile requests per minute
            "/api/{user_id}/tasks/stats": {"requests": 30, "window": 60},  # 30 stats requests per minute
            "default": {"requests": 100, "window": 60}  # Default rate limit
        }

    def _get_endpoint_pattern(self, path: str) -> str:
        """
        Convert a specific path to a generic pattern by replacing UUIDs with placeholders.

        Args:
            path: The actual request path

        Returns:
            A generic pattern that represents the endpoint type
        """
        import re

        # Replace UUID patterns with placeholders
        # Common UUID formats
        uuid_pattern = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
        generic_path = re.sub(uuid_pattern, '{user_id}', path, count=1)
        generic_path = re.sub(uuid_pattern, '{task_id}', generic_path)

        return generic_path

    def _get_limit_for_endpoint(self, endpoint: str) -> dict:
        """
        Get the rate limit configuration for a specific endpoint.

        Args:
            endpoint: The endpoint pattern

        Returns:
            Rate limit configuration dictionary
        """
        # Check for exact match first
        if endpoint in self.limits:
            return self.limits[endpoint]

        # Check for partial matches (prefix matching)
        for key, limit in self.limits.items():
            if key.startswith(endpoint.replace('{user_id}', '').replace('{task_id}', '')):
                return limit

        # Return default if no specific limit found
        return self.limits["default"]

    def is_allowed(self, ip: str, path: str, method: str = "GET") -> tuple[bool, dict]:
        """
        Check if a request is allowed based on rate limits.

        Args:
            ip: Client IP address
            path: Request path
            method: HTTP method

        Returns:
            Tuple of (is_allowed: bool, rate_info: dict)
        """
        # Normalize the path to get the endpoint pattern
        endpoint_pattern = self._get_endpoint_pattern(path)

        # Get rate limit configuration for this endpoint
        limit_config = self._get_limit_for_endpoint(endpoint_pattern)

        # Create a key for this IP and endpoint combination
        key = (ip, endpoint_pattern)

        # Current timestamp
        now = time.time()
        window_start = now - limit_config["window"]

        # Remove outdated requests from the queue
        while self.requests[key] and self.requests[key][0] < window_start:
            self.requests[key].popleft()

        # Check if we're under the limit
        current_requests = len(self.requests[key])

        if current_requests >= limit_config["requests"]:
            # Rate limit exceeded
            oldest_request = self.requests[key][0] if self.requests[key] else now
            reset_time = oldest_request + limit_config["window"]

            return False, {
                "limit": limit_config["requests"],
                "remaining": 0,
                "reset_time": reset_time,
                "retry_after": int(reset_time - now)
            }

        # Add current request to the queue
        self.requests[key].append(now)

        return True, {
            "limit": limit_config["requests"],
            "remaining": limit_config["requests"] - current_requests - 1,
            "reset_time": now + limit_config["window"],
            "retry_after": limit_config["window"]
        }


# Global rate limiter instance
rate_limiter = RateLimiter()


class RateLimitMiddleware:
    """
    ASGI Middleware for rate limiting API requests.

    This middleware intercepts incoming requests and checks if they exceed
    the configured rate limits before passing them to the application.
    """

    def __init__(self, app: ASGIApp, exclude_paths: list = None):
        self.app = app
        self.exclude_paths = exclude_paths or ["/health", "/docs", "/redoc", "/openapi.json"]
        self.rate_limiter = rate_limiter

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope)

        # Check if the path should be excluded from rate limiting
        if request.url.path in self.exclude_paths:
            await self.app(scope, receive, send)
            return

        # Get client IP address (considering potential proxies)
        client_ip = self._get_client_ip(request)

        # Check if the request is allowed
        is_allowed, rate_info = self.rate_limiter.is_allowed(
            client_ip, request.url.path, request.method
        )

        if not is_allowed:
            # Rate limit exceeded - return 429 Too Many Requests
            response = JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded",
                    "error_code": "RATE_LIMIT_EXCEEDED",
                    "rate_info": {
                        "limit": rate_info["limit"],
                        "remaining": rate_info["remaining"],
                        "reset_time": rate_info["reset_time"],
                        "retry_after": rate_info["retry_after"]
                    }
                },
                headers={
                    "X-RateLimit-Limit": str(rate_info["limit"]),
                    "X-RateLimit-Remaining": str(rate_info["remaining"]),
                    "X-RateLimit-Reset": str(int(rate_info["reset_time"])),
                    "Retry-After": str(rate_info["retry_after"])
                }
            )
            await response(scope, receive, send)
            return

        # Add rate limit headers to the response
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                # Add rate limit headers to the response
                headers = message.get("headers", [])
                headers.append((b"x-ratelimit-limit", str(rate_info["limit"]).encode()))
                headers.append((b"x-ratelimit-remaining", str(rate_info["remaining"]).encode()))
                headers.append((b"x-ratelimit-reset", str(int(rate_info["reset_time"])).encode()))
                message["headers"] = headers

            await send(message)

        await self.app(scope, receive, send_wrapper)

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


def get_rate_limit_info(ip: str, path: str) -> dict:
    """
    Get current rate limit information for a specific IP and path.

    Args:
        ip: Client IP address
        path: Request path

    Returns:
        Dictionary containing rate limit information
    """
    return rate_limiter.is_allowed(ip, path)[1]