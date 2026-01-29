"""
Unit tests for task completion toggle functionality.

These tests verify the functionality of toggling task completion status
and related business logic.
"""

import pytest
from unittest.mock import Mock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.task import Task, TaskCreate
from src.models.user import User
from src.services.task_service import TaskService


class TestTaskCompletionFunctionality:
    """Test cases for task completion toggle functionality."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.mock_db_session = Mock(spec=AsyncSession)
        self.task_service = TaskService(self.mock_db_session)

        # Create a mock user for testing
        self.mock_user = User(
            id="123e4567-e89b-12d3-a456-426614174000",
            email="test@example.com",
            hashed_password="hashed_password"
        )

    async def test_toggle_task_completion_from_false_to_true(self):
        """Test toggling task completion from false to true."""
        # Arrange
        task_id = "123e4567-e89b-12d3-a456-426614174001"

        mock_task = Task(
            id=task_id,
            title="Test Task",
            description="Test Description",
            user_id=self.mock_user.id,
            is_completed=False,  # Initially not completed
            priority=1
        )

        # Mock the get_task_by_id method to return the mock task
        original_get_task_by_id = self.task_service.get_task_by_id
        self.task_service.get_task_by_id = Mock(return_value=mock_task)

        # Act
        result = await self.task_service.toggle_task_completion(task_id, self.mock_user)

        # Assert
        assert result == mock_task
        assert result.is_completed is True  # Should be toggled to True

        # Verify database operations were called
        self.mock_db_session.commit.assert_called_once()
        self.mock_db_session.refresh.assert_called_once()

        # Restore original method
        self.task_service.get_task_by_id = original_get_task_by_id

    async def test_toggle_task_completion_from_true_to_false(self):
        """Test toggling task completion from true to false."""
        # Arrange
        task_id = "123e4567-e89b-12d3-a456-426614174001"

        mock_task = Task(
            id=task_id,
            title="Test Task",
            description="Test Description",
            user_id=self.mock_user.id,
            is_completed=True,  # Initially completed
            priority=1
        )

        # Mock the get_task_by_id method to return the mock task
        original_get_task_by_id = self.task_service.get_task_by_id
        self.task_service.get_task_by_id = Mock(return_value=mock_task)

        # Act
        result = await self.task_service.toggle_task_completion(task_id, self.mock_user)

        # Assert
        assert result == mock_task
        assert result.is_completed is False  # Should be toggled to False

        # Verify database operations were called
        self.mock_db_session.commit.assert_called_once()
        self.mock_db_session.refresh.assert_called_once()

        # Restore original method
        self.task_service.get_task_by_id = original_get_task_by_id

    async def test_toggle_nonexistent_task_returns_none(self):
        """Test that toggling a non-existent task returns None."""
        # Arrange
        task_id = "non-existent-id"

        # Mock the get_task_by_id method to return None
        original_get_task_by_id = self.task_service.get_task_by_id
        self.task_service.get_task_by_id = Mock(return_value=None)

        # Act
        result = await self.task_service.toggle_task_completion(task_id, self.mock_user)

        # Assert
        assert result is None

        # Verify no database operations were called
        self.mock_db_session.commit.assert_not_called()
        self.mock_db_session.refresh.assert_not_called()

        # Restore original method
        self.task_service.get_task_by_id = original_get_task_by_id

    async def test_toggle_task_with_different_user_returns_none(self):
        """Test that toggling a task owned by a different user returns None."""
        # Arrange
        task_id = "123e4567-e89b-12d3-a456-426614174001"

        # Create a task owned by a different user
        different_user = User(
            id="different-user-id",
            email="different@example.com",
            hashed_password="hashed_password"
        )

        mock_task = Task(
            id=task_id,
            title="Test Task",
            description="Test Description",
            user_id=different_user.id,  # Different user owns this task
            is_completed=False,
            priority=1
        )

        # Mock the get_task_by_id method to return the mock task
        original_get_task_by_id = self.task_service.get_task_by_id
        self.task_service.get_task_by_id = Mock(return_value=mock_task)

        # Act
        result = await self.task_service.toggle_task_completion(task_id, self.mock_user)

        # Assert
        assert result is None  # Should return None because the task doesn't belong to the current user

        # Restore original method
        self.task_service.get_task_by_id = original_get_task_by_id

    async def test_toggle_task_completeness_multiple_times(self):
        """Test toggling task completion multiple times maintains correct state."""
        # Arrange
        task_id = "123e4567-e89b-12d3-a456-426614174001"

        mock_task = Task(
            id=task_id,
            title="Test Task",
            description="Test Description",
            user_id=self.mock_user.id,
            is_completed=False,  # Starts as False
            priority=1
        )

        # Mock the get_task_by_id method to return the same mock task each time
        original_get_task_by_id = self.task_service.get_task_by_id
        self.task_service.get_task_by_id = Mock(return_value=mock_task)

        # Reset commit/refresh call counts
        self.mock_db_session.commit.reset_mock()
        self.mock_db_session.refresh.reset_mock()

        # Act & Assert: Toggle multiple times
        # First toggle: False -> True
        result1 = await self.task_service.toggle_task_completion(task_id, self.mock_user)
        assert result1.is_completed is True

        # Second toggle: True -> False
        result2 = await self.task_service.toggle_task_completion(task_id, self.mock_user)
        assert result2.is_completed is False

        # Third toggle: False -> True
        result3 = await self.task_service.toggle_task_completion(task_id, self.mock_user)
        assert result3.is_completed is True

        # Fourth toggle: True -> False
        result4 = await self.task_service.toggle_task_completion(task_id, self.mock_user)
        assert result4.is_completed is False

        # Verify database operations were called each time
        assert self.mock_db_session.commit.call_count == 4
        assert self.mock_db_session.refresh.call_count == 4

        # Restore original method
        self.task_service.get_task_by_id = original_get_task_by_id

    async def test_toggle_task_database_commit_failure(self):
        """Test behavior when database commit fails during toggle."""
        # Arrange
        task_id = "123e4567-e89b-12d3-a456-426614174001"

        mock_task = Task(
            id=task_id,
            title="Test Task",
            description="Test Description",
            user_id=self.mock_user.id,
            is_completed=False,
            priority=1
        )

        # Mock the get_task_by_id method to return the mock task
        original_get_task_by_id = self.task_service.get_task_by_id
        self.task_service.get_task_by_id = Mock(return_value=mock_task)

        # Mock commit to raise an exception
        self.mock_db_session.commit.side_effect = Exception("Database commit failed")

        # Act & Assert: Should raise an exception
        with pytest.raises(Exception, match="Database commit failed"):
            await self.task_service.toggle_task_completion(task_id, self.mock_user)

        # Restore original method and reset side effect
        self.task_service.get_task_by_id = original_get_task_by_id
        self.mock_db_session.commit.side_effect = None

    async def test_toggle_task_refresh_failure(self):
        """Test behavior when database refresh fails during toggle."""
        # Arrange
        task_id = "123e4567-e89b-12d3-a456-426614174001"

        mock_task = Task(
            id=task_id,
            title="Test Task",
            description="Test Description",
            user_id=self.mock_user.id,
            is_completed=False,
            priority=1
        )

        # Mock the get_task_by_id method to return the mock task
        original_get_task_by_id = self.task_service.get_task_by_id
        self.task_service.get_task_by_id = Mock(return_value=mock_task)

        # Mock refresh to raise an exception
        self.mock_db_session.refresh.side_effect = Exception("Database refresh failed")

        # Act & Assert: Should raise an exception
        with pytest.raises(Exception, match="Database refresh failed"):
            await self.task_service.toggle_task_completion(task_id, self.mock_user)

        # Verify commit was called but refresh failed
        self.mock_db_session.commit.assert_called_once()
        self.mock_db_session.refresh.assert_called_once()

        # Restore original method and reset side effect
        self.task_service.get_task_by_id = original_get_task_by_id
        self.mock_db_session.refresh.side_effect = None

    async def test_toggle_task_edge_case_empty_title(self):
        """Test toggling task with empty title (edge case)."""
        # Arrange
        task_id = "123e4567-e89b-12d3-a456-426614174001"

        mock_task = Task(
            id=task_id,
            title="",  # Empty title
            description="Test Description",
            user_id=self.mock_user.id,
            is_completed=False,
            priority=1
        )

        # Mock the get_task_by_id method to return the mock task
        original_get_task_by_id = self.task_service.get_task_by_id
        self.task_service.get_task_by_id = Mock(return_value=mock_task)

        # Act
        result = await self.task_service.toggle_task_completion(task_id, self.mock_user)

        # Assert
        assert result == mock_task
        assert result.is_completed is True  # Should still toggle correctly
        assert result.title == ""  # Title remains empty

        # Restore original method
        self.task_service.get_task_by_id = original_get_task_by_id

    async def test_toggle_task_high_priority(self):
        """Test toggling task with high priority."""
        # Arrange
        task_id = "123e4567-e89b-12d3-a456-426614174001"

        mock_task = Task(
            id=task_id,
            title="High Priority Task",
            description="Critical task",
            user_id=self.mock_user.id,
            is_completed=False,
            priority=3  # High priority
        )

        # Mock the get_task_by_id method to return the mock task
        original_get_task_by_id = self.task_service.get_task_by_id
        self.task_service.get_task_by_id = Mock(return_value=mock_task)

        # Act
        result = await self.task_service.toggle_task_completion(task_id, self.mock_user)

        # Assert
        assert result == mock_task
        assert result.is_completed is True  # Should toggle correctly
        assert result.priority == 3  # Priority should remain unchanged

        # Restore original method
        self.task_service.get_task_by_id = original_get_task_by_id

    async def test_toggle_task_with_due_date(self):
        """Test toggling task that has a due date."""
        from datetime import datetime

        # Arrange
        task_id = "123e4567-e89b-12d3-a456-426614174001"
        due_date = datetime.now()

        mock_task = Task(
            id=task_id,
            title="Due Date Task",
            description="Task with due date",
            user_id=self.mock_user.id,
            is_completed=False,
            priority=2,
            due_date=due_date
        )

        # Mock the get_task_by_id method to return the mock task
        original_get_task_by_id = self.task_service.get_task_by_id
        self.task_service.get_task_by_id = Mock(return_value=mock_task)

        # Act
        result = await self.task_service.toggle_task_completion(task_id, self.mock_user)

        # Assert
        assert result == mock_task
        assert result.is_completed is True  # Should toggle correctly
        assert result.due_date == due_date  # Due date should remain unchanged

        # Restore original method
        self.task_service.get_task_by_id = original_get_task_by_id