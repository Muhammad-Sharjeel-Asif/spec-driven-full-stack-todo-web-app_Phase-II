"""
Integration tests for the task completion toggle endpoint.

These tests verify that the PATCH /api/{user_id}/tasks/{task_id}/complete
endpoint works correctly with real database operations and authentication.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from src.main import app
from src.database import Base
from src.models.user import User
from src.models.task import Task
from src.services.user_service import UserService
from src.services.task_service import TaskService
from src.utils.jwt_utils import create_access_token
import uuid


@pytest.fixture
def test_client():
    """Create a test client for the FastAPI app."""
    client = TestClient(app)
    yield client


@pytest.fixture
def setup_test_database():
    """Set up an in-memory SQLite database for testing."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)

    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    yield TestingSessionLocal

    Base.metadata.drop_all(bind=engine)


@pytest.mark.integration
class TestTaskCompletionEndpoint:
    """Integration tests for the task completion toggle endpoint."""

    def test_toggle_task_completion_success(self, test_client, setup_test_database):
        """Test successful toggling of task completion status."""
        # Create a test user and task in the database
        db = setup_test_database()

        with db() as session:
            user_service = UserService(session)
            test_user = user_service.create_user("toggle@example.com", "password123")
            user_id = str(test_user.id)

            task_service = TaskService(session)
            task = task_service.create_task(
                TaskCreate(title="Toggle Test Task", description="Task for toggle testing",
                          is_completed=False, priority=1, due_date=None),
                test_user
            )
            task_id = str(task.id)

            session.commit()

        # Create a JWT token for the test user
        access_token = create_access_token(data={"sub": user_id, "email": "toggle@example.com"})

        # Test initial state (should be incomplete)
        response = test_client.get(
            f"/api/{user_id}/tasks/{task_id}",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        assert response.status_code == 200
        initial_task = response.json()
        assert initial_task["is_completed"] is False

        # Toggle the task completion status
        response = test_client.patch(
            f"/api/{user_id}/tasks/{task_id}/complete",
            headers={"Authorization": f"Bearer {access_token}"}
        )

        # Verify the response
        assert response.status_code == 200
        toggled_task = response.json()
        assert toggled_task["id"] == task_id
        assert toggled_task["is_completed"] is True  # Should now be completed

        # Toggle again to make it incomplete
        response = test_client.patch(
            f"/api/{user_id}/tasks/{task_id}/complete",
            headers={"Authorization": f"Bearer {access_token}"}
        )

        # Verify the response
        assert response.status_code == 200
        toggled_again_task = response.json()
        assert toggled_again_task["id"] == task_id
        assert toggled_again_task["is_completed"] is False  # Should now be incomplete again

    def test_toggle_nonexistent_task_returns_404(self, test_client, setup_test_database):
        """Test toggling a non-existent task returns 404."""
        # Create a test user
        db = setup_test_database()

        with db() as session:
            user_service = UserService(session)
            test_user = user_service.create_user("nonexistent@example.com", "password123")
            user_id = str(test_user.id)

            session.commit()

        # Create a JWT token for the test user
        access_token = create_access_token(data={"sub": user_id, "email": "nonexistent@example.com"})

        # Try to toggle a non-existent task
        fake_task_id = str(uuid.uuid4())
        response = test_client.patch(
            f"/api/{user_id}/tasks/{fake_task_id}/complete",
            headers={"Authorization": f"Bearer {access_token}"}
        )

        # Verify the response
        assert response.status_code == 404
        error_response = response.json()
        assert "detail" in error_response
        assert "not found" in error_response["detail"].lower()

    def test_toggle_task_without_authentication_returns_401(self, test_client, setup_test_database):
        """Test toggling a task without authentication returns 401."""
        # Create a test user and task in the database
        db = setup_test_database()

        with db() as session:
            user_service = UserService(session)
            test_user = user_service.create_user("auth@example.com", "password123")
            user_id = str(test_user.id)

            task_service = TaskService(session)
            task = task_service.create_task(
                TaskCreate(title="Auth Test Task", description="Task for auth testing",
                          is_completed=False, priority=1, due_date=None),
                test_user
            )
            task_id = str(task.id)

            session.commit()

        # Try to toggle the task without authentication
        response = test_client.patch(f"/api/{user_id}/tasks/{task_id}/complete")

        # Verify the response
        assert response.status_code == 401
        error_response = response.json()
        assert "detail" in error_response

    def test_toggle_task_with_invalid_token_returns_401(self, test_client, setup_test_database):
        """Test toggling a task with invalid token returns 401."""
        # Create a test user and task in the database
        db = setup_test_database()

        with db() as session:
            user_service = UserService(session)
            test_user = user_service.create_user("invalid@example.com", "password123")
            user_id = str(test_user.id)

            task_service = TaskService(session)
            task = task_service.create_task(
                TaskCreate(title="Invalid Token Test Task", description="Task for invalid token testing",
                          is_completed=False, priority=1, due_date=None),
                test_user
            )
            task_id = str(task.id)

            session.commit()

        # Try to toggle the task with an invalid token
        response = test_client.patch(
            f"/api/{user_id}/tasks/{task_id}/complete",
            headers={"Authorization": "Bearer invalid_token"}
        )

        # Verify the response
        assert response.status_code == 401
        error_response = response.json()
        assert "detail" in error_response

    def test_toggle_other_users_task_returns_403(self, test_client, setup_test_database):
        """Test that a user cannot toggle another user's task."""
        # Create two users and each has a task
        db = setup_test_database()

        with db() as session:
            user_service = UserService(session)

            # Create first user and their task
            user1 = user_service.create_user("user1@example.com", "password123")
            user1_id = str(user1.id)

            task_service = TaskService(session)
            task1 = task_service.create_task(
                TaskCreate(title="User1's Task", description="Task for user1",
                          is_completed=False, priority=1, due_date=None),
                user1
            )
            task1_id = str(task1.id)

            # Create second user and their task
            user2 = user_service.create_user("user2@example.com", "password123")
            user2_id = str(user2.id)

            task2 = task_service.create_task(
                TaskCreate(title="User2's Task", description="Task for user2",
                          is_completed=False, priority=1, due_date=None),
                user2
            )
            task2_id = str(task2.id)

            session.commit()

        # Create tokens for both users
        token1 = create_access_token(data={"sub": user1_id, "email": "user1@example.com"})
        token2 = create_access_token(data={"sub": user2_id, "email": "user2@example.com"})

        # User1 tries to toggle User2's task (should fail)
        response = test_client.patch(
            f"/api/{user2_id}/tasks/{task2_id}",  # Trying to toggle user2's task
            headers={"Authorization": f"Bearer {token1}"}  # Using user1's token
        )

        # Verify the response
        assert response.status_code == 403  # Forbidden
        error_response = response.json()
        assert "detail" in error_response
        assert "access denied" in error_response["detail"].lower()

        # User2 tries to toggle User1's task (should fail)
        response = test_client.patch(
            f"/api/{user1_id}/tasks/{task1_id}",  # Trying to toggle user1's task
            headers={"Authorization": f"Bearer {token2}"}  # Using user2's token
        )

        # Verify the response
        assert response.status_code == 403  # Forbidden
        error_response = response.json()
        assert "detail" in error_response
        assert "access denied" in error_response["detail"].lower()

    def test_toggle_task_with_mismatched_user_id_returns_403(self, test_client, setup_test_database):
        """Test toggling task with mismatched user ID in path returns 403."""
        # Create two users and each has a task
        db = setup_test_database()

        with db() as session:
            user_service = UserService(session)

            # Create first user and their task
            user1 = user_service.create_user("user1@example.com", "password123")
            user1_id = str(user1.id)

            task_service = TaskService(session)
            task1 = task_service.create_task(
                TaskCreate(title="User1's Task", description="Task for user1",
                          is_completed=False, priority=1, due_date=None),
                user1
            )
            task1_id = str(task1.id)

            # Create second user
            user2 = user_service.create_user("user2@example.com", "password123")
            user2_id = str(user2.id)

            session.commit()

        # Create token for user1
        token1 = create_access_token(data={"sub": user1_id, "email": "user1@example.com"})

        # User1 tries to toggle user1's task but uses user2's ID in the path (should fail)
        response = test_client.patch(
            f"/api/{user2_id}/tasks/{task1_id}",  # Using user2's ID in path but user1's token
            headers={"Authorization": f"Bearer {token1}"}
        )

        # Verify the response
        assert response.status_code == 403  # Forbidden
        error_response = response.json()
        assert "detail" in error_response
        assert "access denied" in error_response["detail"].lower()

    def test_toggle_task_preserves_other_attributes(self, test_client, setup_test_database):
        """Test that toggling task completion preserves other attributes."""
        # Create a test user and task with specific attributes
        from datetime import datetime

        db = setup_test_database()

        with db() as session:
            user_service = UserService(session)
            test_user = user_service.create_user("preserve@example.com", "password123")
            user_id = str(test_user.id)

            task_service = TaskService(session)
            original_due_date = datetime(2024, 12, 31, 23, 59, 59)

            task = task_service.create_task(
                TaskCreate(
                    title="Preservation Test Task",
                    description="Task to test attribute preservation",
                    is_completed=False,
                    priority=2,  # Medium priority
                    due_date=original_due_date
                ),
                test_user
            )
            task_id = str(task.id)

            session.commit()

        # Create a JWT token for the test user
        access_token = create_access_token(data={"sub": user_id, "email": "preserve@example.com"})

        # Toggle the task completion status
        response = test_client.patch(
            f"/api/{user_id}/tasks/{task_id}/complete",
            headers={"Authorization": f"Bearer {access_token}"}
        )

        # Verify the response
        assert response.status_code == 200
        toggled_task = response.json()

        # Verify that completion status changed but other attributes remained the same
        assert toggled_task["id"] == task_id
        assert toggled_task["is_completed"] is True  # Changed
        assert toggled_task["title"] == "Preservation Test Task"  # Preserved
        assert toggled_task["description"] == "Task to test attribute preservation"  # Preserved
        assert toggled_task["priority"] == 2  # Preserved
        # Note: The due_date format might differ depending on how it's serialized

        # Toggle back to verify it goes back to original state
        response = test_client.patch(
            f"/api/{user_id}/tasks/{task_id}/complete",
            headers={"Authorization": f"Bearer {access_token}"}
        )

        assert response.status_code == 200
        toggled_back_task = response.json()
        assert toggled_back_task["id"] == task_id
        assert toggled_back_task["is_completed"] is False  # Back to original state
        assert toggled_back_task["title"] == "Preservation Test Task"  # Still preserved
        assert toggled_back_task["description"] == "Task to test attribute preservation"  # Still preserved

    def test_concurrent_toggle_requests(self, test_client, setup_test_database):
        """Test handling of concurrent toggle requests (simulated)."""
        # Create a test user and task in the database
        db = setup_test_database()

        with db() as session:
            user_service = UserService(session)
            test_user = user_service.create_user("concurrent@example.com", "password123")
            user_id = str(test_user.id)

            task_service = TaskService(session)
            task = task_service.create_task(
                TaskCreate(title="Concurrent Test Task", description="Task for concurrent testing",
                          is_completed=False, priority=1, due_date=None),
                test_user
            )
            task_id = str(task.id)

            session.commit()

        # Create a JWT token for the test user
        access_token = create_access_token(data={"sub": user_id, "email": "concurrent@example.com"})

        # Simulate multiple toggle requests (though in real world these would be concurrent)
        for i in range(5):  # Toggle 5 times
            response = test_client.patch(
                f"/api/{user_id}/tasks/{task_id}/complete",
                headers={"Authorization": f"Bearer {access_token}"}
            )

            assert response.status_code == 200
            toggled_task = response.json()

            # After odd number of toggles, task should be completed; after even, incomplete
            expected_status = (i + 1) % 2 == 1  # True for odd, False for even
            assert toggled_task["is_completed"] == expected_status

    def test_toggle_task_with_special_characters_in_attributes(self, test_client, setup_test_database):
        """Test toggling task with special characters in title/description."""
        # Create a test user and task with special characters
        db = setup_test_database()

        with db() as session:
            user_service = UserService(session)
            test_user = user_service.create_user("special@example.com", "password123")
            user_id = str(test_user.id)

            task_service = TaskService(session)
            task = task_service.create_task(
                TaskCreate(
                    title="Special Char Task: !@#$%^&*()",
                    description="Task with special chars: áéíóú ñ ü ¿¡",
                    is_completed=False,
                    priority=1,
                    due_date=None
                ),
                test_user
            )
            task_id = str(task.id)

            session.commit()

        # Create a JWT token for the test user
        access_token = create_access_token(data={"sub": user_id, "email": "special@example.com"})

        # Toggle the task completion status
        response = test_client.patch(
            f"/api/{user_id}/tasks/{task_id}/complete",
            headers={"Authorization": f"Bearer {access_token}"}
        )

        # Verify the response
        assert response.status_code == 200
        toggled_task = response.json()

        # Verify that special characters are preserved
        assert toggled_task["id"] == task_id
        assert toggled_task["is_completed"] is True
        assert "Special Char Task: !@#$%^&*()" in toggled_task["title"]
        assert "áéíóú ñ ü ¿¡" in toggled_task["description"]