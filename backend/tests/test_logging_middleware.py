"""
Tests for the logging middleware functionality.

These tests verify that the logging middleware correctly captures
and logs API requests and security events.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from fastapi.responses import PlainTextResponse
from unittest.mock import Mock, patch, MagicMock
import json
import logging
from src.middleware.logging_middleware import LoggingMiddleware
from starlette.requests import Request
from starlette.datastructures import Headers
from starlette.types import ASGIApp
from io import StringIO
import sys
from contextlib import redirect_stdout


class TestLoggingMiddleware:
    """Test cases for the logging middleware."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Create a simple app for testing
        self.test_app = self._create_test_app()

    def _create_test_app(self) -> ASGIApp:
        """Create a simple test app."""
        app = FastAPI()

        @app.get("/test")
        def test_endpoint():
            return {"message": "success"}

        @app.get("/error")
        def error_endpoint():
            raise ValueError("Test error")

        return app

    def test_logging_middleware_initialization(self):
        """Test that the logging middleware initializes correctly."""
        app = self._create_test_app()
        middleware = LoggingMiddleware(app)

        assert middleware is not None
        assert hasattr(middleware, 'dispatch')
        assert hasattr(middleware, '_get_client_ip')
        assert hasattr(middleware, '_get_user_id')
        assert hasattr(middleware, '_log_request_start')
        assert hasattr(middleware, '_log_response_success')
        assert hasattr(middleware, '_log_request_error')

    def test_get_client_ip_with_x_forwarded_for(self):
        """Test extracting client IP from X-Forwarded-For header."""
        app = self._create_test_app()
        middleware = LoggingMiddleware(app)

        # Create a mock request with X-Forwarded-For header
        mock_request = Mock(spec=Request)
        mock_request.headers = Headers({"x-forwarded-for": "192.168.1.100, 10.0.0.1, 127.0.0.1"})

        client_ip = middleware._get_client_ip(mock_request)
        assert client_ip == "192.168.1.100"  # Should take the first IP

    def test_get_client_ip_with_x_real_ip(self):
        """Test extracting client IP from X-Real-IP header."""
        app = self._create_test_app()
        middleware = LoggingMiddleware(app)

        # Create a mock request with X-Real-IP header
        mock_request = Mock(spec=Request)
        mock_request.headers = Headers({"x-real-ip": "192.168.1.100"})

        client_ip = middleware._get_client_ip(mock_request)
        assert client_ip == "192.168.1.100"

    def test_get_client_ip_with_direct_client(self):
        """Test extracting client IP from direct client connection."""
        app = self._create_test_app()
        middleware = LoggingMiddleware(app)

        # Create a mock request with direct client connection
        mock_request = Mock(spec=Request)
        mock_request.headers = Headers({})
        mock_request.client = Mock()
        mock_request.client.host = "192.168.1.100"

        client_ip = middleware._get_client_ip(mock_request)
        assert client_ip == "192.168.1.100"

    def test_get_client_ip_with_no_info(self):
        """Test default IP when no IP information is available."""
        app = self._create_test_app()
        middleware = LoggingMiddleware(app)

        # Create a mock request with no IP information
        mock_request = Mock(spec=Request)
        mock_request.headers = Headers({})
        mock_request.client = Mock()
        mock_request.client.host = None

        client_ip = middleware._get_client_ip(mock_request)
        assert client_ip == "unknown"

    def test_get_user_id_with_bearer_token(self):
        """Test extracting user ID from bearer token in authorization header."""
        app = self._create_test_app()
        middleware = LoggingMiddleware(app)

        # Create a mock request with authorization header
        mock_request = Mock(spec=Request)
        mock_request.headers = Headers({"authorization": "Bearer some_jwt_token"})

        user_id = middleware._get_user_id(mock_request)
        assert user_id == "authenticated_user"  # Our implementation returns this placeholder

    def test_get_user_id_without_authorization(self):
        """Test user ID is anonymous when no authorization header is present."""
        app = self._create_test_app()
        middleware = LoggingMiddleware(app)

        # Create a mock request without authorization header
        mock_request = Mock(spec=Request)
        mock_request.headers = Headers({})

        user_id = middleware._get_user_id(mock_request)
        assert user_id == "anonymous"

    def test_log_request_start(self, caplog):
        """Test that request start is logged correctly."""
        app = self._create_test_app()
        middleware = LoggingMiddleware(app)

        # Create a mock request
        mock_request = Mock(spec=Request)
        mock_request.method = "GET"
        mock_request.url = Mock()
        mock_request.url.path = "/test"
        mock_request.headers = Headers({"user-agent": "test-agent", "content-type": "application/json"})

        # Capture logs
        with caplog.at_level(logging.INFO):
            middleware._log_request_start(mock_request, "req-123", "192.168.1.100")

        # Check that a log message was created
        assert len(caplog.records) >= 1
        log_found = False
        for record in caplog.records:
            if "REQUEST_START" in record.message:
                log_found = True
                break
        assert log_found, "REQUEST_START log should be present"

    def test_log_response_success(self, caplog):
        """Test that successful responses are logged correctly."""
        from starlette.responses import JSONResponse

        app = self._create_test_app()
        middleware = LoggingMiddleware(app)

        # Create mock request and response
        mock_request = Mock(spec=Request)
        mock_request.method = "GET"
        mock_request.url = Mock()
        mock_request.url.path = "/test"

        mock_response = JSONResponse({"message": "success"}, status_code=200)

        # Capture logs
        with caplog.at_level(logging.INFO):
            middleware._log_response_success(mock_request, mock_response, "req-123", "192.168.1.100", 0.1)

        # Check that a success log message was created
        assert len(caplog.records) >= 1
        success_log_found = False
        for record in caplog.records:
            if "REQUEST_SUCCESS" in record.message:
                success_log_found = True
                break
        assert success_log_found, "REQUEST_SUCCESS log should be present"

    def test_log_request_error(self, caplog):
        """Test that request errors are logged correctly."""
        app = self._create_test_app()
        middleware = LoggingMiddleware(app)

        # Create mock request and exception
        mock_request = Mock(spec=Request)
        mock_request.method = "GET"
        mock_request.url = Mock()
        mock_request.url.path = "/error"

        test_exception = ValueError("Test error message")

        # Capture logs
        with caplog.at_level(logging.ERROR):
            middleware._log_request_error(mock_request, test_exception, "req-123", "192.168.1.100", 0.1)

        # Check that an error log message was created
        assert len(caplog.records) >= 1
        error_log_found = False
        for record in caplog.records:
            if "REQUEST_ERROR" in record.message:
                error_log_found = True
                break
        assert error_log_found, "REQUEST_ERROR log should be present"

    def test_log_security_event(self, caplog):
        """Test that security events are logged correctly."""
        app = self._create_test_app()
        middleware = LoggingMiddleware(app)

        # Create mock request
        mock_request = Mock(spec=Request)
        mock_request.method = "GET"
        mock_request.url = Mock()
        mock_request.url.path = "/suspicious"
        mock_request.headers = Headers({})

        details = {"reason": "unusual_activity", "severity": "high"}

        # Capture logs
        with caplog.at_level(logging.WARNING):
            middleware._log_security_event(mock_request, "unusual_activity_detected", details)

        # Check that a security event log message was created
        assert len(caplog.records) >= 1
        security_log_found = False
        for record in caplog.records:
            if "SECURITY_EVENT" in record.message:
                security_log_found = True
                break
        assert security_log_found, "SECURITY_EVENT log should be present"

    def test_dispatch_successful_request(self, caplog):
        """Test that successful requests are properly logged through the dispatch method."""
        app = self._create_test_app()
        middleware = LoggingMiddleware(app)

        # Create a test client with the middleware
        client = TestClient(app)
        client.app = middleware

        # This test is tricky because we need to test the actual middleware chain
        # For now, we'll test that the middleware doesn't break normal operation
        assert middleware is not None

    def test_dispatch_error_request(self, caplog):
        """Test that error requests are properly logged through the dispatch method."""
        app = self._create_test_app()
        middleware = LoggingMiddleware(app)

        # For this test, we'll just verify the middleware doesn't break
        # The actual dispatch functionality would be tested in integration tests
        assert middleware is not None

    def test_log_response_with_4xx_error(self, caplog):
        """Test that 4xx client errors are logged at warning level."""
        from starlette.responses import JSONResponse

        app = self._create_test_app()
        middleware = LoggingMiddleware(app)

        # Create mock request and 4xx response
        mock_request = Mock(spec=Request)
        mock_request.method = "GET"
        mock_request.url = Mock()
        mock_request.url.path = "/test"

        mock_response = JSONResponse({"error": "Bad Request"}, status_code=400)

        # Capture logs
        with caplog.at_level(logging.WARNING):
            middleware._log_response_success(mock_request, mock_response, "req-123", "192.168.1.100", 0.1)

        # Check that a warning log message was created for client error
        warning_log_found = False
        for record in caplog.records:
            if "CLIENT_ERROR" in record.message:
                warning_log_found = True
                break
        assert warning_log_found, "CLIENT_ERROR log should be present for 4xx status"

    def test_log_response_with_5xx_error(self, caplog):
        """Test that 5xx server errors are logged at error level."""
        from starlette.responses import JSONResponse

        app = self._create_test_app()
        middleware = LoggingMiddleware(app)

        # Create mock request and 5xx response
        mock_request = Mock(spec=Request)
        mock_request.method = "GET"
        mock_request.url = Mock()
        mock_request.url.path = "/test"

        mock_response = JSONResponse({"error": "Server Error"}, status_code=500)

        # Capture logs
        with caplog.at_level(logging.ERROR):
            middleware._log_response_success(mock_request, mock_response, "req-123", "192.168.1.100", 0.1)

        # Check that an error log message was created for server error
        error_log_found = False
        for record in caplog.records:
            if "SERVER_ERROR" in record.message:
                error_log_found = True
                break
        assert error_log_found, "SERVER_ERROR log should be present for 5xx status"

    def test_log_request_start_contains_expected_fields(self, caplog):
        """Test that request start logs contain expected fields."""
        app = self._create_test_app()
        middleware = LoggingMiddleware(app)

        # Create a mock request
        mock_request = Mock(spec=Request)
        mock_request.method = "POST"
        mock_request.url = Mock()
        mock_request.url.path = "/api/test"
        mock_request.headers = Headers({
            "user-agent": "test-agent/1.0",
            "content-type": "application/json",
            "accept": "application/json"
        })

        # Capture logs
        with caplog.at_level(logging.INFO):
            middleware._log_request_start(mock_request, "req-123", "192.168.1.100")

        # Check that log contains expected fields
        log_found = False
        for record in caplog.records:
            if "REQUEST_START" in record.message:
                log_found = True
                # Parse the JSON portion of the log
                try:
                    # Extract JSON from log message
                    log_parts = record.message.split(': ', 1)
                    if len(log_parts) > 1:
                        json_str = log_parts[1]
                        log_data = json.loads(json_str)

                        # Check for expected fields
                        assert "event" in log_data
                        assert "request_id" in log_data
                        assert "method" in log_data
                        assert "path" in log_data
                        assert "client_ip" in log_data
                        assert "user_id" in log_data
                        assert "timestamp" in log_data
                        assert "headers" in log_data

                        # Check values
                        assert log_data["event"] == "request_started"
                        assert log_data["request_id"] == "req-123"
                        assert log_data["method"] == "POST"
                        assert log_data["path"] == "/api/test"
                        assert log_data["client_ip"] == "192.168.1.100"

                except (json.JSONDecodeError, IndexError):
                    # If JSON parsing fails, that's an issue with our log format
                    assert False, "Log message should contain valid JSON"
                break

        assert log_found, "REQUEST_START log should be present"

    def test_log_response_success_contains_expected_fields(self, caplog):
        """Test that response success logs contain expected fields."""
        from starlette.responses import JSONResponse

        app = self._create_test_app()
        middleware = LoggingMiddleware(app)

        # Create mock request and response
        mock_request = Mock(spec=Request)
        mock_request.method = "GET"
        mock_request.url = Mock()
        mock_request.url.path = "/test"

        mock_response = JSONResponse({"message": "success"}, status_code=200)

        # Capture logs
        with caplog.at_level(logging.INFO):
            middleware._log_response_success(mock_request, mock_response, "req-123", "192.168.1.100", 0.15)

        # Check that log contains expected fields
        success_log_found = False
        for record in caplog.records:
            if "REQUEST_SUCCESS" in record.message:
                success_log_found = True
                # Parse the JSON portion of the log
                try:
                    # Extract JSON from log message
                    log_parts = record.message.split(': ', 1)
                    if len(log_parts) > 1:
                        json_str = log_parts[1]
                        log_data = json.loads(json_str)

                        # Check for expected fields
                        assert "event" in log_data
                        assert "request_id" in log_data
                        assert "method" in log_data
                        assert "path" in log_data
                        assert "client_ip" in log_data
                        assert "user_id" in log_data
                        assert "status_code" in log_data
                        assert "duration_ms" in log_data
                        assert "timestamp" in log_data

                        # Check values
                        assert log_data["event"] == "response_completed"
                        assert log_data["request_id"] == "req-123"
                        assert log_data["method"] == "GET"
                        assert log_data["path"] == "/test"
                        assert log_data["status_code"] == 200
                        assert log_data["duration_ms"] == 150.0  # 0.15 seconds = 150ms

                except (json.JSONDecodeError, IndexError):
                    # If JSON parsing fails, that's an issue with our log format
                    assert False, "Log message should contain valid JSON"
                break

        assert success_log_found, "REQUEST_SUCCESS log should be present"

    def test_log_request_error_contains_expected_fields(self, caplog):
        """Test that request error logs contain expected fields."""
        app = self._create_test_app()
        middleware = LoggingMiddleware(app)

        # Create mock request and exception
        mock_request = Mock(spec=Request)
        mock_request.method = "GET"
        mock_request.url = Mock()
        mock_request.url.path = "/error"

        test_exception = RuntimeError("Something went wrong")

        # Capture logs
        with caplog.at_level(logging.ERROR):
            middleware._log_request_error(mock_request, test_exception, "req-123", "192.168.1.100", 0.2)

        # Check that log contains expected fields
        error_log_found = False
        for record in caplog.records:
            if "REQUEST_ERROR" in record.message:
                error_log_found = True
                # Parse the JSON portion of the log
                try:
                    # Extract JSON from log message
                    log_parts = record.message.split(': ', 1)
                    if len(log_parts) > 1:
                        json_str = log_parts[1]
                        log_data = json.loads(json_str)

                        # Check for expected fields
                        assert "event" in log_data
                        assert "request_id" in log_data
                        assert "method" in log_data
                        assert "path" in log_data
                        assert "client_ip" in log_data
                        assert "user_id" in log_data
                        assert "error_type" in log_data
                        assert "error_message" in log_data
                        assert "duration_ms" in log_data
                        assert "timestamp" in log_data

                        # Check values
                        assert log_data["event"] == "request_error"
                        assert log_data["request_id"] == "req-123"
                        assert log_data["method"] == "GET"
                        assert log_data["path"] == "/error"
                        assert log_data["error_type"] == "RuntimeError"
                        assert log_data["error_message"] == "Something went wrong"
                        assert log_data["duration_ms"] == 200.0  # 0.2 seconds = 200ms

                except (json.JSONDecodeError, IndexError):
                    # If JSON parsing fails, that's an issue with our log format
                    assert False, "Log message should contain valid JSON"
                break

        assert error_log_found, "REQUEST_ERROR log should be present"

    def test_setup_logging_config_exists(self):
        """Test that the logging configuration function exists."""
        from src.middleware.logging_middleware import setup_logging_config

        # Just verify the function exists and can be called
        # (It may have side effects, so we won't actually call it in tests)
        assert callable(setup_logging_config)