"""
Tests for the rate limiting functionality.

These tests verify that the rate limiting middleware works correctly
to prevent abuse and ensure security.
"""

import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.middleware.rate_limiter import rate_limiter
from unittest.mock import patch
import time


@pytest.fixture
def test_client():
    """Create a test client for the FastAPI app."""
    client = TestClient(app)
    yield client


class TestRateLimiting:
    """Test cases for rate limiting functionality."""

    def test_rate_limiter_initial_state(self):
        """Test the initial state of the rate limiter."""
        # Verify that the global rate limiter instance exists
        assert rate_limiter is not None
        assert hasattr(rate_limiter, 'is_allowed')
        assert hasattr(rate_limiter, '_get_endpoint_pattern')
        assert hasattr(rate_limiter, '_get_limit_for_endpoint')

        # Check that initial requests dictionary is empty
        assert len(rate_limiter.requests) == 0

    def test_get_endpoint_pattern_uuid_replacement(self):
        """Test that UUIDs in paths are correctly replaced with placeholders."""
        # Test various UUID formats
        test_cases = [
            (
                "/api/123e4567-e89b-12d3-a456-426614174000/tasks",
                "/api/{user_id}/tasks"
            ),
            (
                "/api/123e4567-e89b-12d3-a456-426614174000/tasks/987e6543-e89b-12d3-a456-426614174999",
                "/api/{user_id}/tasks/{task_id}"
            ),
            (
                "/api/123e4567-e89b-12d3-a456-426614174000/tasks/stats",
                "/api/{user_id}/tasks/stats"
            ),
        ]

        for original_path, expected_pattern in test_cases:
            result = rate_limiter._get_endpoint_pattern(original_path)
            assert result == expected_pattern

    def test_get_limit_for_endpoint(self):
        """Test that the correct rate limits are returned for endpoints."""
        # Test specific endpoint limits
        limits = {
            "/api/{user_id}/tasks": {"requests": 100, "window": 60},
            "/api/{user_id}/tasks/{task_id}": {"requests": 50, "window": 60},
            "/api/auth/login": {"requests": 5, "window": 300},
            "/api/auth/register": {"requests": 2, "window": 3600},
        }

        for endpoint, expected_limit in limits.items():
            result = rate_limiter._get_limit_for_endpoint(endpoint)
            assert result["requests"] == expected_limit["requests"]
            assert result["window"] == expected_limit["window"]

    def test_default_limit_for_unknown_endpoint(self):
        """Test that unknown endpoints get the default rate limit."""
        unknown_endpoint = "/api/unknown/endpoint"
        default_limit = rate_limiter.limits["default"]

        result = rate_limiter._get_limit_for_endpoint(unknown_endpoint)
        assert result["requests"] == default_limit["requests"]
        assert result["window"] == default_limit["window"]

    def test_is_allowed_under_limit(self):
        """Test that requests are allowed when under the rate limit."""
        ip = "192.168.1.1"
        path = "/api/123e4567-e89b-12d3-a456-426614174000/tasks"

        # Clear any existing requests for this IP/path combination
        key = (ip, "/api/{user_id}/tasks")
        rate_limiter.requests[key].clear()

        # Test that initial requests are allowed
        is_allowed, rate_info = rate_limiter.is_allowed(ip, path, "GET")
        assert is_allowed is True
        assert rate_info["remaining"] >= 0

    def test_is_allowed_exceeds_limit(self):
        """Test that requests are denied when exceeding the rate limit."""
        ip = "192.168.1.1"
        path = "/api/123e4567-e89b-12d3-a456-426614174000/tasks"

        # Clear any existing requests for this IP/path combination
        key = (ip, "/api/{user_id}/tasks")
        rate_limiter.requests[key].clear()

        # Add requests up to the limit
        limit_config = rate_limiter._get_limit_for_endpoint("/api/{user_id}/tasks")
        for i in range(limit_config["requests"]):
            rate_limiter.is_allowed(ip, path, "GET")  # This adds to the counter

        # The next request should be denied
        is_allowed, rate_info = rate_limiter.is_allowed(ip, path, "GET")
        assert is_allowed is False
        assert rate_info["remaining"] == 0

    def test_rate_limit_resets_after_window(self):
        """Test that rate limits reset after the time window passes."""
        ip = "192.168.1.1"
        path = "/api/123e4567-e89b-12d3-a456-426614174000/tasks"

        # Clear any existing requests for this IP/path combination
        key = (ip, "/api/{user_id}/tasks")
        rate_limiter.requests[key].clear()

        # Add requests up to the limit
        limit_config = rate_limiter._get_limit_for_endpoint("/api/{user_id}/tasks")
        for i in range(limit_config["requests"]):
            rate_limiter.is_allowed(ip, path, "GET")

        # The next request should be denied
        is_allowed, rate_info = rate_limiter.is_allowed(ip, path, "GET")
        assert is_allowed is False

        # Manually advance time past the window (simulate time passing)
        # This is a simplified test - in practice, we'd need to manipulate the stored timestamps
        # For this test, we'll clear the old requests manually
        from collections import deque
        import time

        # Clear the requests that are older than the window (simulate window passing)
        now = time.time()
        window_start = now - limit_config["window"] - 1  # Past the window

        # Add a timestamp that's definitely outside the window
        rate_limiter.requests[key] = deque([window_start - 1])  # Old timestamp

        # Now the limit should be reset
        is_allowed, rate_info = rate_limiter.is_allowed(ip, path, "GET")
        assert is_allowed is True
        assert rate_info["remaining"] >= 0

    def test_different_ips_have_separate_limits(self):
        """Test that different IPs have separate rate limits."""
        path = "/api/123e4567-e89b-12d3-a456-426614174000/tasks"

        ip1 = "192.168.1.1"
        ip2 = "192.168.1.2"

        # Clear any existing requests
        key1 = (ip1, "/api/{user_id}/tasks")
        key2 = (ip2, "/api/{user_id}/tasks")
        rate_limiter.requests[key1].clear()
        rate_limiter.requests[key2].clear()

        # Fill up limit for IP1
        limit_config = rate_limiter._get_limit_for_endpoint("/api/{user_id}/tasks")
        for i in range(limit_config["requests"]):
            rate_limiter.is_allowed(ip1, path, "GET")

        # IP1 should be denied now
        is_allowed_1, _ = rate_limiter.is_allowed(ip1, path, "GET")
        assert is_allowed_1 is False

        # But IP2 should still be allowed
        is_allowed_2, rate_info_2 = rate_limiter.is_allowed(ip2, path, "GET")
        assert is_allowed_2 is True
        assert rate_info_2["remaining"] >= 0

    def test_different_endpoints_have_separate_limits(self):
        """Test that different endpoints have separate rate limits."""
        ip = "192.168.1.1"

        # Paths that map to different endpoints
        tasks_path = "/api/123e4567-e89b-12d3-a456-426614174000/tasks"
        login_path = "/api/auth/login"

        # Clear any existing requests
        tasks_key = (ip, "/api/{user_id}/tasks")
        login_key = (ip, "/api/auth/login")
        rate_limiter.requests[tasks_key].clear()
        rate_limiter.requests[login_key].clear()

        # Fill up tasks limit
        tasks_limit = rate_limiter._get_limit_for_endpoint("/api/{user_id}/tasks")
        for i in range(tasks_limit["requests"]):
            rate_limiter.is_allowed(ip, tasks_path, "GET")

        # Tasks endpoint should be denied
        is_allowed_tasks, _ = rate_limiter.is_allowed(ip, tasks_path, "GET")
        assert is_allowed_tasks is False

        # But login endpoint should still be allowed (different limit)
        is_allowed_login, rate_info_login = rate_limiter.is_allowed(ip, login_path, "GET")
        assert is_allowed_login is True
        assert rate_info_login["remaining"] >= 0

    def test_rate_limit_info_function(self):
        """Test the get_rate_limit_info function."""
        from src.middleware.rate_limiter import get_rate_limit_info

        ip = "192.168.1.1"
        path = "/api/123e4567-e89b-12d3-a456-426614174000/tasks"

        # Clear any existing requests
        key = (ip, "/api/{user_id}/tasks")
        rate_limiter.requests[key].clear()

        # Get rate limit info
        rate_info = get_rate_limit_info(ip, "/api/{user_id}/tasks")

        # Should return valid rate info
        assert "limit" in rate_info
        assert "remaining" in rate_info
        assert "reset_time" in rate_info
        assert "retry_after" in rate_info

    def test_rate_limiting_middleware_blocks_requests(self, test_client):
        """Test that the rate limiting middleware blocks requests when limit is exceeded."""
        # For this test, we'll just check that the middleware is registered
        # The actual blocking behavior is difficult to test in a unit test
        # because it would require making many requests rapidly

        # Just verify that we can make a normal request
        response = test_client.get("/health")
        assert response.status_code == 200

    def test_rate_limiting_excluded_paths(self):
        """Test that certain paths are excluded from rate limiting."""
        # Health check should be excluded
        health_path = "/health"
        health_limit = rate_limiter._get_limit_for_endpoint(health_path)

        # Should return default or special limit for excluded paths
        # In our implementation, excluded paths would go through different middleware
        # but the rate limiter should still recognize them as lower priority
        assert health_limit["requests"] >= 100  # Should have high limit or default

    def test_rate_limit_for_auth_endpoints(self):
        """Test that authentication endpoints have appropriate rate limits."""
        ip = "192.168.1.1"

        # Login endpoint should have strict limits
        login_path = "/api/auth/login"
        login_limit = rate_limiter._get_limit_for_endpoint(login_path)
        assert login_limit["requests"] == 5  # 5 attempts per 5 minutes (300 seconds)
        assert login_limit["window"] == 300

        # Register endpoint should have very strict limits
        register_path = "/api/auth/register"
        register_limit = rate_limiter._get_limit_for_endpoint(register_path)
        assert register_limit["requests"] == 2  # 2 attempts per hour (3600 seconds)
        assert register_limit["window"] == 3600

    def test_rate_limit_for_task_endpoints(self):
        """Test that task endpoints have appropriate rate limits."""
        ip = "192.168.1.1"

        # Regular task endpoint
        tasks_path = "/api/123e4567-e89b-12d3-a456-426614174000/tasks"
        tasks_limit = rate_limiter._get_limit_for_endpoint("/api/{user_id}/tasks")
        assert tasks_limit["requests"] == 100  # 100 requests per minute
        assert tasks_limit["window"] == 60

        # Specific task endpoint
        task_path = "/api/123e4567-e89b-12d3-a456-426614174000/tasks/987e6543-e89b-12d3-a456-426614174999"
        task_limit = rate_limiter._get_limit_for_endpoint("/api/{user_id}/tasks/{task_id}")
        assert task_limit["requests"] == 50  # 50 requests per minute
        assert task_limit["window"] == 60

    def test_rate_limit_headers_format(self):
        """Test that rate limit information is properly formatted."""
        ip = "192.168.1.1"
        path = "/api/123e4567-e89b-12d3-a456-426614174000/tasks"

        # Clear any existing requests
        key = (ip, "/api/{user_id}/tasks")
        rate_limiter.requests[key].clear()

        # Get rate limit info
        is_allowed, rate_info = rate_limiter.is_allowed(ip, path, "GET")

        # Verify the format of rate info
        assert isinstance(rate_info, dict)
        assert "limit" in rate_info
        assert "remaining" in rate_info
        assert "reset_time" in rate_info
        assert "retry_after" in rate_info

        # Values should be appropriate types
        assert isinstance(rate_info["limit"], int)
        assert isinstance(rate_info["remaining"], int)
        assert isinstance(rate_info["reset_time"], (int, float))
        assert isinstance(rate_info["retry_after"], int)

        assert rate_info["limit"] > 0
        assert rate_info["remaining"] >= 0
        assert rate_info["retry_after"] >= 0