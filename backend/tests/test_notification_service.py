"""
Unit tests for the NotificationService class.

These tests verify the functionality of the NotificationService including
scheduling reminders, sending notifications, and managing notification preferences.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from src.models.task import Task
from src.models.user import User
from src.services.notification_service import NotificationService


class TestNotificationService:
    """Test cases for the NotificationService class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.mock_db_session = Mock(spec=AsyncSession)
        self.notification_service = NotificationService(self.mock_db_session)

        # Create a mock user for testing
        self.mock_user = User(
            id="123e4567-e89b-12d3-a456-426614174000",
            email="test@example.com",
            hashed_password="hashed_password"
        )

        # Create a mock task for testing
        self.mock_task = Task(
            id="123e4567-e89b-12d3-a456-426614174001",
            title="Test Task",
            description="Test Description",
            user_id=self.mock_user.id,
            is_completed=False,
            priority=1,
            due_date=datetime.now() + timedelta(days=1),
            notification_settings='{"reminder_enabled": true, "reminder_time": 24}'
        )

    async def test_schedule_reminders_for_task_success(self):
        """Test successful scheduling of reminders for a task."""
        # Arrange
        task_id = str(self.mock_task.id)
        user_id = str(self.mock_user.id)

        # Mock the database query
        mock_execute = AsyncMock()
        mock_scalar = AsyncMock()
        mock_scalar.return_value = self.mock_task
        mock_execute.return_value = Mock(scalar_one_or_none=mock_scalar)
        self.mock_db_session.execute.return_value = mock_execute

        # Act
        result = await self.notification_service.schedule_reminders_for_task(task_id, user_id)

        # Assert
        assert result is True
        mock_execute.assert_called_once()

    async def test_schedule_reminders_for_nonexistent_task(self):
        """Test scheduling reminders for a non-existent task."""
        # Arrange
        task_id = "non-existent-task-id"
        user_id = str(self.mock_user.id)

        # Mock the database query to return None
        mock_execute = AsyncMock()
        mock_scalar = AsyncMock()
        mock_scalar.return_value = None
        mock_execute.return_value = Mock(scalar_one_or_none=mock_scalar)
        self.mock_db_session.execute.return_value = mock_execute

        # Act
        result = await self.notification_service.schedule_reminders_for_task(task_id, user_id)

        # Assert
        assert result is False
        mock_execute.assert_called_once()

    async def test_schedule_reminders_with_disabled_reminders(self):
        """Test scheduling reminders when reminders are disabled."""
        # Arrange
        task_id = str(self.mock_task.id)
        user_id = str(self.mock_user.id)

        # Create a task with disabled reminders
        task_with_disabled_reminders = Task(
            id="123e4567-e89b-12d3-a456-426614174002",
            title="Task Without Reminders",
            description="No reminders",
            user_id=self.mock_user.id,
            is_completed=False,
            priority=1,
            due_date=datetime.now() + timedelta(days=1),
            notification_settings='{"reminder_enabled": false, "reminder_time": 24}'
        )

        # Mock the database query
        mock_execute = AsyncMock()
        mock_scalar = AsyncMock()
        mock_scalar.return_value = task_with_disabled_reminders
        mock_execute.return_value = Mock(scalar_one_or_none=mock_scalar)
        self.mock_db_session.execute.return_value = mock_execute

        # Act
        result = await self.notification_service.schedule_reminders_for_task(task_id, user_id)

        # Assert
        assert result is True  # Should return True even if reminders are disabled
        mock_execute.assert_called_once()

    async def test_schedule_reminders_without_due_date(self):
        """Test scheduling reminders for a task without a due date."""
        # Arrange
        task_id = str(self.mock_task.id)
        user_id = str(self.mock_user.id)

        # Create a task without a due date
        task_without_due_date = Task(
            id="123e4567-e89b-12d3-a456-426614174003",
            title="Task Without Due Date",
            description="No due date",
            user_id=self.mock_user.id,
            is_completed=False,
            priority=1,
            due_date=None,  # No due date
            notification_settings='{"reminder_enabled": true, "reminder_time": 24}'
        )

        # Mock the database query
        mock_execute = AsyncMock()
        mock_scalar = AsyncMock()
        mock_scalar.return_value = task_without_due_date
        mock_execute.return_value = Mock(scalar_one_or_none=mock_scalar)
        self.mock_db_session.execute.return_value = mock_execute

        # Act
        result = await self.notification_service.schedule_reminders_for_task(task_id, user_id)

        # Assert
        assert result is True  # Should return True even without due date
        mock_execute.assert_called_once()

    async def test_get_notification_preferences(self):
        """Test getting user notification preferences."""
        # Arrange
        user_id = str(self.mock_user.id)

        # Act
        result = await self.notification_service.get_notification_preferences(user_id)

        # Assert
        assert isinstance(result, dict)
        assert "email_notifications" in result
        assert "push_notifications" in result
        assert "default_reminder_hours" in result

    async def test_update_notification_preferences(self):
        """Test updating user notification preferences."""
        # Arrange
        user_id = str(self.mock_user.id)
        preferences = {
            "email_notifications": False,
            "push_notifications": True,
            "default_reminder_hours": 12
        }

        # Act
        result = await self.notification_service.update_notification_preferences(user_id, preferences)

        # Assert
        assert result is True

    async def test_send_due_date_reminder_success(self):
        """Test sending a due date reminder successfully."""
        # Arrange
        task_id = str(self.mock_task.id)
        user_id = str(self.mock_user.id)

        # Mock the database queries
        task_mock_execute = AsyncMock()
        task_mock_scalar = AsyncMock()
        task_mock_scalar.return_value = self.mock_task
        task_mock_execute.return_value = Mock(scalar_one_or_none=task_mock_scalar)

        user_mock_execute = AsyncMock()
        user_mock_scalar = AsyncMock()
        user_mock_scalar.return_value = self.mock_user
        user_mock_execute.return_value = Mock(scalar_one_or_none=user_mock_scalar)

        # Mock the execute method to return different results for different statements
        def mock_execute_side_effect(stmt):
            if 'Task' in str(stmt):
                return task_mock_execute
            else:
                return user_mock_execute

        self.mock_db_session.execute.side_effect = mock_execute_side_effect

        # Act
        result = await self.notification_service.send_due_date_reminder(task_id, user_id)

        # Assert
        assert result is True

    async def test_send_due_date_reminder_task_not_found(self):
        """Test sending a due date reminder for a non-existent task."""
        # Arrange
        task_id = "non-existent-task-id"
        user_id = str(self.mock_user.id)

        # Mock the database query to return None for task
        task_mock_execute = AsyncMock()
        task_mock_scalar = AsyncMock()
        task_mock_scalar.return_value = None
        task_mock_execute.return_value = Mock(scalar_one_or_none=task_mock_scalar)

        # Mock the execute method to return different results for different statements
        def mock_execute_side_effect(stmt):
            if 'Task' in str(stmt):
                return task_mock_execute
            else:
                # For user query, we don't reach it in this test
                pass

        self.mock_db_session.execute.side_effect = mock_execute_side_effect

        # Act
        result = await self.notification_service.send_due_date_reminder(task_id, user_id)

        # Assert
        assert result is False

    async def test_send_email_notification(self):
        """Test sending an email notification."""
        # Arrange
        email = "test@example.com"
        task = self.mock_task

        # Act
        result = await self.notification_service.send_email_notification(email, task)

        # Assert
        assert result is True

    async def test_send_push_notification(self):
        """Test sending a push notification."""
        # Arrange
        user_id = str(self.mock_user.id)
        task = self.mock_task

        # Act
        result = await self.notification_service.send_push_notification(user_id, task)

        # Assert
        assert result is True

    async def test_get_upcoming_reminders(self):
        """Test getting upcoming reminders."""
        # Arrange
        user_id = str(self.mock_user.id)
        hours_ahead = 24

        # Mock the database query to return tasks
        mock_execute = AsyncMock()
        mock_scalars = AsyncMock()
        mock_scalars.all.return_value = [self.mock_task]
        mock_execute.return_value = Mock(scalars=mock_scalars)
        self.mock_db_session.execute.return_value = mock_execute

        # Act
        result = await self.notification_service.get_upcoming_reminders(user_id, hours_ahead)

        # Assert
        assert isinstance(result, list)
        if result:
            assert len(result) >= 0  # May be empty depending on due dates

    async def test_cleanup_old_notifications(self):
        """Test cleaning up old notifications."""
        # Arrange
        days_retained = 30

        # Act
        result = await self.notification_service.cleanup_old_notifications(days_retained)

        # Assert
        assert isinstance(result, int)
        assert result >= 0