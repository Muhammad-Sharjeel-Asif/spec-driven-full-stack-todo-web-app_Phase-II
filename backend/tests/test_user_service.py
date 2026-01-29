"""
Unit tests for the UserService class.

These tests verify the functionality of the UserService including
user creation, retrieval, and authentication.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.user import User
from src.services.user_service import UserService
from src.models.auth_token import AuthToken


class TestUserService:
    """Test cases for the UserService class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.mock_db_session = Mock(spec=AsyncSession)
        self.user_service = UserService()

    async def test_create_user_success(self):
        """Test successful user creation."""
        # Arrange
        email = "test@example.com"
        password = "securepassword"

        # Mock the database operations
        mock_user = User(
            id="123e4567-e89b-12d3-a456-426614174000",
            email=email,
            hashed_password="hashed_securepassword"
        )

        self.mock_db_session.add.return_value = None
        self.mock_db_session.commit.return_value = None
        self.mock_db_session.refresh.return_value = None

        # Mock the password hashing
        with patch.object(self.user_service, 'get_password_hash') as mock_hash:
            mock_hash.return_value = "hashed_securepassword"

            # Act
            result = await self.user_service.create_user(self.mock_db_session, email, password)

            # Assert
            assert result.email == email
            assert result.hashed_password == "hashed_securepassword"
            mock_hash.assert_called_once_with(password)
            self.mock_db_session.add.assert_called_once()
            self.mock_db_session.commit.assert_called_once()
            self.mock_db_session.refresh.assert_called_once()

    async def test_get_user_by_email_found(self):
        """Test retrieving a user by email when user exists."""
        # Arrange
        email = "test@example.com"
        mock_user = User(
            id="123e4567-e89b-12d3-a456-426614174000",
            email=email,
            hashed_password="hashed_password"
        )

        # Mock the database query
        mock_execute = Mock()
        mock_execute.scalar_one_or_none.return_value = mock_user
        self.mock_db_session.execute.return_value = mock_execute

        # Act
        result = await self.user_service.get_user_by_email(self.mock_db_session, email)

        # Assert
        assert result == mock_user
        assert result.email == email

    async def test_get_user_by_email_not_found(self):
        """Test retrieving a user by email when user does not exist."""
        # Arrange
        email = "nonexistent@example.com"

        # Mock the database query to return None
        mock_execute = Mock()
        mock_execute.scalar_one_or_none.return_value = None
        self.mock_db_session.execute.return_value = mock_execute

        # Act
        result = await self.user_service.get_user_by_email(self.mock_db_session, email)

        # Assert
        assert result is None

    async def test_get_user_by_id_found(self):
        """Test retrieving a user by ID when user exists."""
        # Arrange
        user_id = "123e4567-e89b-12d3-a456-426614174000"
        mock_user = User(
            id=user_id,
            email="test@example.com",
            hashed_password="hashed_password"
        )

        # Mock the database query
        mock_execute = Mock()
        mock_execute.scalar_one_or_none.return_value = mock_user
        self.mock_db_session.execute.return_value = mock_execute

        # Act
        result = await self.user_service.get_user_by_id(self.mock_db_session, user_id)

        # Assert
        assert result == mock_user
        assert result.id == user_id

    async def test_get_user_by_id_not_found(self):
        """Test retrieving a user by ID when user does not exist."""
        # Arrange
        user_id = "non-existent-id"

        # Mock the database query to return None
        mock_execute = Mock()
        mock_execute.scalar_one_or_none.return_value = None
        self.mock_db_session.execute.return_value = mock_execute

        # Act
        result = await self.user_service.get_user_by_id(self.mock_db_session, user_id)

        # Assert
        assert result is None

    async def test_authenticate_user_success(self):
        """Test successful user authentication."""
        # Arrange
        email = "test@example.com"
        password = "correctpassword"

        mock_user = User(
            id="123e4567-e89b-12d3-a456-426614174000",
            email=email,
            hashed_password="hashed_correctpassword"
        )

        # Mock the database query
        mock_execute = Mock()
        mock_execute.scalar_one_or_none.return_value = mock_user
        self.mock_db_session.execute.return_value = mock_execute

        # Mock the password verification
        with patch.object(self.user_service, 'verify_password') as mock_verify:
            mock_verify.return_value = True

            # Act
            result = await self.user_service.authenticate_user(self.mock_db_session, email, password)

            # Assert
            assert result == mock_user
            mock_verify.assert_called_once_with(password, "hashed_correctpassword")

    async def test_authenticate_user_wrong_password(self):
        """Test user authentication with wrong password."""
        # Arrange
        email = "test@example.com"
        password = "wrongpassword"

        mock_user = User(
            id="123e4567-e89b-12d3-a456-426614174000",
            email=email,
            hashed_password="hashed_correctpassword"
        )

        # Mock the database query
        mock_execute = Mock()
        mock_execute.scalar_one_or_none.return_value = mock_user
        self.mock_db_session.execute.return_value = mock_execute

        # Mock the password verification
        with patch.object(self.user_service, 'verify_password') as mock_verify:
            mock_verify.return_value = False

            # Act
            result = await self.user_service.authenticate_user(self.mock_db_session, email, password)

            # Assert
            assert result is None
            mock_verify.assert_called_once_with(password, "hashed_correctpassword")

    async def test_authenticate_user_not_found(self):
        """Test user authentication with non-existent user."""
        # Arrange
        email = "nonexistent@example.com"
        password = "anypassword"

        # Mock the database query to return None
        mock_execute = Mock()
        mock_execute.scalar_one_or_none.return_value = None
        self.mock_db_session.execute.return_value = mock_execute

        # Act
        result = await self.user_service.authenticate_user(self.mock_db_session, email, password)

        # Assert
        assert result is None

    async def test_update_user_success(self):
        """Test successful user update."""
        # Arrange
        user_id = "123e4567-e89b-12d3-a456-426614174000"
        new_email = "updated@example.com"

        mock_user = User(
            id=user_id,
            email="original@example.com",
            hashed_password="hashed_password"
        )

        # Mock the get_user_by_id method to return the mock user
        original_get_user_by_id = self.user_service.get_user_by_id
        self.user_service.get_user_by_id = Mock(return_value=mock_user)

        # Act
        result = await self.user_service.update_user(self.mock_db_session, user_id, new_email)

        # Assert
        assert result == mock_user
        assert result.email == new_email

        # Restore original method
        self.user_service.get_user_by_id = original_get_user_by_id

    async def test_update_user_not_found(self):
        """Test updating a non-existent user."""
        # Arrange
        user_id = "non-existent-id"
        new_email = "updated@example.com"

        # Mock the get_user_by_id method to return None
        original_get_user_by_id = self.user_service.get_user_by_id
        self.user_service.get_user_by_id = Mock(return_value=None)

        # Act
        result = await self.user_service.update_user(self.mock_db_session, user_id, new_email)

        # Assert
        assert result is None

        # Restore original method
        self.user_service.get_user_by_id = original_get_user_by_id

    async def test_delete_user_success(self):
        """Test successful user deletion."""
        # Arrange
        user_id = "123e4567-e89b-12d3-a456-426614174000"

        mock_user = User(
            id=user_id,
            email="test@example.com",
            hashed_password="hashed_password"
        )

        # Mock the get_user_by_id method to return the mock user
        original_get_user_by_id = self.user_service.get_user_by_id
        self.user_service.get_user_by_id = Mock(return_value=mock_user)

        # Act
        result = await self.user_service.delete_user(self.mock_db_session, user_id)

        # Assert
        assert result is True

        # Verify database operations were called
        self.mock_db_session.delete.assert_called_once_with(mock_user)
        self.mock_db_session.commit.assert_called_once()

        # Restore original method
        self.user_service.get_user_by_id = original_get_user_by_id

    async def test_delete_user_not_found(self):
        """Test deleting a non-existent user."""
        # Arrange
        user_id = "non-existent-id"

        # Mock the get_user_by_id method to return None
        original_get_user_by_id = self.user_service.get_user_by_id
        self.user_service.get_user_by_id = Mock(return_value=None)

        # Act
        result = await self.user_service.delete_user(self.mock_db_session, user_id)

        # Assert
        assert result is False

        # Verify no database operations were called
        self.mock_db_session.delete.assert_not_called()
        self.mock_db_session.commit.assert_not_called()

        # Restore original method
        self.user_service.get_user_by_id = original_get_user_by_id

    async def test_change_user_password_success(self):
        """Test successful password change."""
        # Arrange
        user_id = "123e4567-e89b-12d3-a456-426614174000"
        new_password = "newsecurepassword"

        mock_user = User(
            id=user_id,
            email="test@example.com",
            hashed_password="old_hashed_password"
        )

        # Mock the get_user_by_id method to return the mock user
        original_get_user_by_id = self.user_service.get_user_by_id
        self.user_service.get_user_by_id = Mock(return_value=mock_user)

        # Mock the password hashing
        with patch.object(self.user_service, 'get_password_hash') as mock_hash:
            mock_hash.return_value = "new_hashed_password"

            # Act
            result = await self.user_service.change_user_password(self.mock_db_session, user_id, new_password)

            # Assert
            assert result == mock_user
            assert result.hashed_password == "new_hashed_password"
            mock_hash.assert_called_once_with(new_password)

        # Restore original method
        self.user_service.get_user_by_id = original_get_user_by_id

    async def test_change_user_password_not_found(self):
        """Test changing password for non-existent user."""
        # Arrange
        user_id = "non-existent-id"
        new_password = "newsecurepassword"

        # Mock the get_user_by_id method to return None
        original_get_user_by_id = self.user_service.get_user_by_id
        self.user_service.get_user_by_id = Mock(return_value=None)

        # Act
        result = await self.user_service.change_user_password(self.mock_db_session, user_id, new_password)

        # Assert
        assert result is None

        # Restore original method
        self.user_service.get_user_by_id = original_get_user_by_id

    async def test_create_auth_token_success(self):
        """Test successful auth token creation."""
        # Arrange
        user_id = "123e4567-e89b-12d3-a456-426614174000"
        token_value = "some_jwt_token"

        # Mock the database operations
        mock_token = AuthToken(
            id="token_id_123",
            user_id=user_id,
            token=token_value
        )

        self.mock_db_session.add.return_value = None
        self.mock_db_session.commit.return_value = None
        self.mock_db_session.refresh.return_value = None

        # Act
        result = await self.user_service.create_auth_token(self.mock_db_session, user_id, token_value)

        # Assert
        assert result.user_id == user_id
        assert result.token == token_value
        self.mock_db_session.add.assert_called_once()
        self.mock_db_session.commit.assert_called_once()
        self.mock_db_session.refresh.assert_called_once()

    async def test_get_user_by_token_success(self):
        """Test retrieving user by auth token when token exists."""
        # Arrange
        token_value = "valid_token"
        user_id = "123e4567-e89b-12d3-a456-426614174000"

        mock_token = AuthToken(
            id="token_id_123",
            user_id=user_id,
            token=token_value
        )

        mock_user = User(
            id=user_id,
            email="test@example.com",
            hashed_password="hashed_password"
        )

        # Mock the database query for token
        mock_token_execute = Mock()
        mock_token_execute.scalar_one_or_none.return_value = mock_token
        self.mock_db_session.execute.return_value = mock_token_execute

        # Mock the database query for user
        mock_user_execute = Mock()
        mock_user_execute.scalar_one_or_none.return_value = mock_user
        # We need to mock the second execute call
        original_execute = self.mock_db_session.execute
        def mock_execute_side_effect(query):
            if "AuthToken" in str(query):
                return mock_token_execute
            else:
                return mock_user_execute

        self.mock_db_session.execute.side_effect = mock_execute_side_effect

        # Act
        result = await self.user_service.get_user_by_token(self.mock_db_session, token_value)

        # Assert
        assert result == mock_user
        assert result.id == user_id

        # Restore original execute method
        self.mock_db_session.execute = original_execute