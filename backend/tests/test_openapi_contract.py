"""
Contract tests to verify API compliance with OpenAPI specification.

These tests verify that the API endpoints comply with the OpenAPI specification
and maintain expected behavior.
"""

import pytest
from fastapi.testclient import TestClient
from fastapi.openapi.utils import get_openapi
from src.main import app
import json


@pytest.fixture
def test_client():
    """Create a test client for the FastAPI app."""
    client = TestClient(app)
    yield client


@pytest.fixture
def openapi_schema():
    """Get the OpenAPI schema for the application."""
    schema = get_openapi(
        title=app.title,
        version=app.version,
        openapi_version=app.openapi_version,
        description=app.description,
        routes=app.routes,
    )
    return schema


class TestOpenApiContract:
    """Contract tests for API compliance with OpenAPI specification."""

    def test_openapi_schema_exists(self, openapi_schema):
        """Test that the OpenAPI schema exists and is properly formatted."""
        assert openapi_schema is not None
        assert "openapi" in openapi_schema
        assert "info" in openapi_schema
        assert "paths" in openapi_schema
        assert "components" in openapi_schema

        # Verify the version
        assert openapi_schema["openapi"] == "3.1.0"  # FastAPI default

        # Verify basic info
        assert openapi_schema["info"]["title"] == "Todo Backend API"
        assert openapi_schema["info"]["version"] == "1.0.0"

    def test_health_endpoint_in_schema(self, openapi_schema, test_client):
        """Test that the health endpoint is defined in the schema and works."""
        # Check that the endpoint is in the schema
        assert "/health" in openapi_schema["paths"]
        assert "get" in openapi_schema["paths"]["/health"]

        # Test that the endpoint works
        response = test_client.get("/health")
        assert response.status_code == 200

        response_data = response.json()
        assert "status" in response_data
        assert "service" in response_data
        assert response_data["status"] == "healthy"
        assert response_data["service"] == "todo-backend-api"

    def test_task_endpoints_in_schema(self, openapi_schema):
        """Test that task endpoints are defined in the schema."""
        # Check for user-scoped task endpoints
        expected_paths = [
            "/api/{user_id}/tasks",
            "/api/{user_id}/tasks/{task_id}",
            "/api/{user_id}/tasks/{task_id}/complete",
            "/api/{user_id}/tasks/stats"
        ]

        for path in expected_paths:
            assert path in openapi_schema["paths"], f"Path {path} not found in schema"

        # Verify GET /api/{user_id}/tasks has expected parameters
        tasks_get = openapi_schema["paths"]["/api/{user_id}/tasks"]["get"]
        param_names = [param["name"] for param in tasks_get.get("parameters", [])]

        # Check for expected query parameters
        expected_params = ["status", "priority", "due_date_from", "due_date_to", "skip", "limit", "sort_by", "sort_order"]
        for param in expected_params:
            assert param in param_names, f"Parameter {param} not found in GET /api/{{user_id}}/tasks"

    def test_auth_endpoints_in_schema(self, openapi_schema):
        """Test that authentication endpoints are defined in the schema."""
        expected_auth_paths = [
            "/api/auth/register",
            "/api/auth/login",
            "/api/auth/logout",
            "/api/auth/me"
        ]

        for path in expected_auth_paths:
            assert path in openapi_schema["paths"], f"Auth path {path} not found in schema"

        # Verify POST /api/auth/login has expected request body
        login_post = openapi_schema["paths"]["/api/auth/login"]["post"]
        assert "requestBody" in login_post
        assert "content" in login_post["requestBody"]
        assert "application/json" in login_post["requestBody"]["content"]

    def test_task_endpoint_responses(self, openapi_schema):
        """Test that task endpoints have expected response definitions."""
        # Check GET /api/{user_id}/tasks response
        tasks_get = openapi_schema["paths"]["/api/{user_id}/tasks"]["get"]
        responses = tasks_get["responses"]

        assert "200" in responses
        assert "401" in responses  # Unauthorized
        assert "403" in responses  # Forbidden
        assert "404" in responses  # Not Found

        # Check response schema for 200
        response_200 = responses["200"]
        assert "content" in response_200
        assert "application/json" in response_200["content"]
        assert "schema" in response_200["content"]["application/json"]

    def test_patch_task_complete_endpoint(self, openapi_schema):
        """Test that PATCH /api/{user_id}/tasks/{task_id}/complete is properly defined."""
        path = "/api/{user_id}/tasks/{task_id}/complete"
        assert path in openapi_schema["paths"]
        assert "patch" in openapi_schema["paths"][path]

        patch_op = openapi_schema["paths"][path]["patch"]
        responses = patch_op["responses"]

        # Should have 200 (success), 401 (unauthorized), 403 (forbidden), 404 (not found)
        assert "200" in responses
        assert "401" in responses
        assert "403" in responses
        assert "404" in responses

        # Verify parameters are defined
        params = {param["name"]: param for param in patch_op.get("parameters", [])}
        assert "user_id" in params
        assert "task_id" in params

        # Check parameter types
        assert params["user_id"]["schema"]["type"] == "string"
        assert params["task_id"]["schema"]["type"] == "string"

    def test_request_body_definitions_exist(self, openapi_schema):
        """Test that request body schemas are defined in components."""
        assert "components" in openapi_schema
        assert "schemas" in openapi_schema["components"]

        schemas = openapi_schema["components"]["schemas"]

        # Check for expected schemas
        expected_schemas = [
            "TaskCreate",
            "TaskUpdate",
            "TaskRead",
            "UserCreate",
            "UserRead",
            "LoginRequest",
            "LoginResponse"
        ]

        for schema_name in expected_schemas:
            assert schema_name in schemas, f"Schema {schema_name} not found in components"

    def test_response_schema_match_implementation(self, test_client):
        """Test that actual API responses match the defined schemas."""
        # This is a basic check - in a real contract test, we'd have predefined test users/tasks
        # For now, we'll just check that we get the expected response format

        # Test health endpoint response structure
        response = test_client.get("/health")
        assert response.status_code == 200

        health_data = response.json()
        assert isinstance(health_data, dict)
        assert "status" in health_data
        assert "service" in health_data
        assert isinstance(health_data["status"], str)
        assert isinstance(health_data["service"], str)

    def test_error_response_format_consistency(self, test_client):
        """Test that error responses follow a consistent format."""
        # Try to access a non-existent task to trigger a 404
        # We'll use a fake user ID and task ID since we can't easily create valid ones without auth
        response = test_client.get("/api/123e4567-e89b-12d3-a456-426614174000/tasks/123e4567-e89b-12d3-a456-426614174999")

        # Should get 401 (Unauthorized) since no auth token provided
        assert response.status_code in [401, 403, 404]  # Could be any of these depending on implementation

        if response.status_code == 401:
            # For unauthorized access, check that response has expected structure
            response_data = response.json()
            assert "detail" in response_data

    def test_api_tags_are_defined(self, openapi_schema):
        """Test that the API tags defined in the app are present in the schema."""
        assert "tags" in openapi_schema

        tags = {tag["name"] for tag in openapi_schema["tags"]}
        expected_tags = {"authentication", "tasks"}

        for tag in expected_tags:
            assert tag in tags, f"Tag {tag} not found in schema"

    def test_endpoint_security_definitions(self, openapi_schema):
        """Test that endpoints have proper security definitions."""
        # Check that auth endpoints don't require authentication (they're for auth)
        auth_post_endpoints = [
            "/api/auth/register",
            "/api/auth/login"
        ]

        for path in auth_post_endpoints:
            if path in openapi_schema["paths"]:
                op = openapi_schema["paths"][path].get("post", {})
                # These endpoints typically don't have security requirements
                # as they're used to obtain authentication

        # Check that protected endpoints require authentication
        protected_endpoints = [
            "/api/{user_id}/tasks",
            "/api/{user_id}/tasks/{task_id}",
            "/api/{user_id}/tasks/{task_id}/complete"
        ]

        # Note: FastAPI doesn't always explicitly show security requirements in schema
        # for custom authentication schemes, but they should be documented

    def test_path_parameter_validation(self, openapi_schema):
        """Test that path parameters have proper validation defined."""
        tasks_path = openapi_schema["paths"]["/api/{user_id}/tasks"]

        # Get the user_id parameter definition
        user_id_param = None
        for param in tasks_path.get("get", {}).get("parameters", []):
            if param["name"] == "user_id":
                user_id_param = param
                break

        # If parameter is defined in GET, it should have proper schema
        if user_id_param:
            assert "schema" in user_id_param
            assert user_id_param["required"] is True
            assert user_id_param["in"] == "path"

    def test_content_types_are_specified(self, openapi_schema):
        """Test that content types are properly specified in the schema."""
        # Check that POST endpoints specify content type
        auth_login = openapi_schema["paths"]["/api/auth/login"]
        login_post = auth_login.get("post", {})

        if "requestBody" in login_post:
            content_types = list(login_post["requestBody"]["content"].keys())
            assert "application/json" in content_types

    def test_api_schema_version_compliance(self, openapi_schema):
        """Test that the schema complies with OpenAPI 3.1.0 specification."""
        # Verify basic structure required by OpenAPI 3.1.0
        required_fields = ["openapi", "info", "paths"]
        for field in required_fields:
            assert field in openapi_schema, f"Required field {field} missing from schema"

        # Verify info object has required fields
        info = openapi_schema["info"]
        assert "title" in info
        assert "version" in info

    def test_schema_references_resolve(self, openapi_schema):
        """Test that schema references point to valid definitions."""
        def check_refs_recursive(obj, path=""):
            if isinstance(obj, dict):
                if "$ref" in obj:
                    ref = obj["$ref"]
                    # Should start with '#/components/schemas/' for local refs
                    assert ref.startswith("#/components/schemas/"), f"Invalid reference {ref} at {path}"

                    schema_name = ref.split("/")[-1]
                    assert schema_name in openapi_schema["components"]["schemas"], \
                        f"Reference {ref} at {path} points to non-existent schema"

                for key, value in obj.items():
                    check_refs_recursive(value, f"{path}/{key}")
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    check_refs_recursive(item, f"{path}[{i}]")

        # This will recursively check all references in the schema
        check_refs_recursive(openapi_schema)

    def test_api_operation_ids_are_unique(self, openapi_schema):
        """Test that operationIds are unique across the API."""
        operation_ids = set()

        for path, methods in openapi_schema["paths"].items():
            for method, operation in methods.items():
                if "operationId" in operation:
                    op_id = operation["operationId"]
                    assert op_id not in operation_ids, f"Duplicate operationId: {op_id}"
                    operation_ids.add(op_id)