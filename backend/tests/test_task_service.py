"""
Unit tests for the TaskService class.

These tests verify the functionality of the TaskService including
creating, retrieving, updating, deleting, and toggling tasks.
"""

import pytest
from unittest.mock import Mock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.task import Task, TaskCreate, TaskUpdate
from src.models.user import User
from src.services.task_service import TaskService


class TestTaskService:
    """Test cases for the TaskService class."""

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

    async def test_create_task_success(self):
        """Test successful task creation."""
        # Arrange
        task_create = TaskCreate(
            title="Test Task",
            description="Test Description",
            is_completed=False,
            priority=1,
            due_date=None
        )

        # Mock the database operations
        mock_task_instance = Task(
            id="123e4567-e89b-12d3-a456-426614174001",
            title=task_create.title,
            description=task_create.description,
            user_id=self.mock_user.id,
            is_completed=task_create.is_completed,
            priority=task_create.priority,
            due_date=task_create.due_date
        )

        self.mock_db_session.add.return_value = None
        self.mock_db_session.commit.return_value = None
        self.mock_db_session.refresh.return_value = None

        # Act
        result = await self.task_service.create_task(task_create, self.mock_user)

        # Assert
        assert result.title == task_create.title
        assert result.description == task_create.description
        assert result.user_id == self.mock_user.id
        assert result.is_completed == task_create.is_completed
        assert result.priority == task_create.priority
        assert result.due_date == task_create.due_date

        # Verify database operations were called
        self.mock_db_session.add.assert_called_once()
        self.mock_db_session.commit.assert_called_once()
        self.mock_db_session.refresh.assert_called_once()

    async def test_get_task_by_id_success(self):
        """Test successful retrieval of a task by ID."""
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

        # Mock the database query
        mock_execute = Mock()
        mock_execute.scalar_one_or_none.return_value = mock_task
        self.mock_db_session.execute.return_value = mock_execute

        # Act
        result = await self.task_service.get_task_by_id(task_id, self.mock_user)

        # Assert
        assert result == mock_task
        assert result.id == task_id

    async def test_get_task_by_id_not_found(self):
        """Test retrieval of a non-existent task."""
        # Arrange
        task_id = "non-existent-id"

        # Mock the database query to return None
        mock_execute = Mock()
        mock_execute.scalar_one_or_none.return_value = None
        self.mock_db_session.execute.return_value = mock_execute

        # Act
        result = await self.task_service.get_task_by_id(task_id, self.mock_user)

        # Assert
        assert result is None

    async def test_update_task_success(self):
        """Test successful task update."""
        # Arrange
        task_id = "123e4567-e89b-12d3-a456-426614174001"
        task_update = TaskUpdate(
            title="Updated Task",
            description="Updated Description",
            is_completed=True
        )

        mock_task = Task(
            id=task_id,
            title="Original Task",
            description="Original Description",
            user_id=self.mock_user.id,
            is_completed=False,
            priority=1
        )

        # Mock the get_task_by_id method to return the mock task
        original_get_task_by_id = self.task_service.get_task_by_id
        self.task_service.get_task_by_id = Mock(return_value=mock_task)

        # Act
        result = await self.task_service.update_task(task_id, task_update, self.mock_user)

        # Assert
        assert result == mock_task
        assert result.title == task_update.title
        assert result.description == task_update.description
        assert result.is_completed == task_update.is_completed

        # Restore original method
        self.task_service.get_task_by_id = original_get_task_by_id

    async def test_update_task_not_found(self):
        """Test updating a non-existent task."""
        # Arrange
        task_id = "non-existent-id"
        task_update = TaskUpdate(title="Updated Task")

        # Mock the get_task_by_id method to return None
        original_get_task_by_id = self.task_service.get_task_by_id
        self.task_service.get_task_by_id = Mock(return_value=None)

        # Act
        result = await self.task_service.update_task(task_id, task_update, self.mock_user)

        # Assert
        assert result is None

        # Restore original method
        self.task_service.get_task_by_id = original_get_task_by_id

    async def test_delete_task_success(self):
        """Test successful task deletion."""
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

        # Act
        result = await self.task_service.delete_task(task_id, self.mock_user)

        # Assert
        assert result is True

        # Verify database operations were called
        self.mock_db_session.delete.assert_called_once_with(mock_task)
        self.mock_db_session.commit.assert_called_once()

        # Restore original method
        self.task_service.get_task_by_id = original_get_task_by_id

    async def test_delete_task_not_found(self):
        """Test deleting a non-existent task."""
        # Arrange
        task_id = "non-existent-id"

        # Mock the get_task_by_id method to return None
        original_get_task_by_id = self.task_service.get_task_by_id
        self.task_service.get_task_by_id = Mock(return_value=None)

        # Act
        result = await self.task_service.delete_task(task_id, self.mock_user)

        # Assert
        assert result is False

        # Verify no database operations were called
        self.mock_db_session.delete.assert_not_called()
        self.mock_db_session.commit.assert_not_called()

        # Restore original method
        self.task_service.get_task_by_id = original_get_task_by_id

    async def test_toggle_task_completion_success(self):
        """Test successful task completion toggle."""
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

    async def test_toggle_task_completion_not_found(self):
        """Test toggling completion of a non-existent task."""
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

    async def test_get_tasks_success(self):
        """Test successful retrieval of user's tasks."""
        # Arrange
        mock_tasks = [
            Task(
                id="123e4567-e89b-12d3-a456-426614174001",
                title="Task 1",
                description="Description 1",
                user_id=self.mock_user.id,
                is_completed=False,
                priority=1
            ),
            Task(
                id="123e4567-e89b-12d3-a456-426614174002",
                title="Task 2",
                description="Description 2",
                user_id=self.mock_user.id,
                is_completed=True,
                priority=2
            )
        ]

        # Mock the database query
        mock_execute = Mock()
        mock_execute.scalars.return_value.all.return_value = mock_tasks
        self.mock_db_session.execute.return_value = mock_execute

        # Act
        result = await self.task_service.get_tasks(skip=0, limit=100, current_user=self.mock_user)

        # Assert
        assert result == mock_tasks
        assert len(result) == 2

    async def test_get_tasks_no_user(self):
        """Test retrieval of tasks when no user is provided."""
        # Act
        result = await self.task_service.get_tasks(skip=0, limit=100, current_user=None)

        # Assert
        assert result == []