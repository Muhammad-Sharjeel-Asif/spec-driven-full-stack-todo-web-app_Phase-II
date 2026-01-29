"""
Unit tests for the CacheService class.

These tests verify the functionality of the CacheService including
storing, retrieving, and invalidating cached data with TTL.
"""

import pytest
from datetime import datetime, timedelta
import asyncio
from src.services.cache_service import CacheService


class TestCacheService:
    """Test cases for the CacheService class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.cache_service = CacheService()

    async def test_set_and_get_success(self):
        """Test successful storing and retrieving of cached data."""
        # Arrange
        key = "test_key"
        value = {"data": "test_value"}

        # Act
        set_result = await self.cache_service.set(key, value)
        get_result = await self.cache_service.get(key)

        # Assert
        assert set_result is True
        assert get_result == value

    async def test_get_nonexistent_key(self):
        """Test retrieving a non-existent cache key."""
        # Arrange
        key = "nonexistent_key"

        # Act
        result = await self.cache_service.get(key)

        # Assert
        assert result is None

    async def test_cache_expiration(self):
        """Test that cache entries expire after TTL."""
        # Arrange
        key = "expiring_key"
        value = "expiring_value"

        # Set with a short TTL
        await self.cache_service.set(key, value, ttl=1)  # 1 second TTL

        # Wait for the cache to expire
        await asyncio.sleep(2)

        # Act
        result = await self.cache_service.get(key)

        # Assert
        assert result is None

    async def test_cache_does_not_expire_before_ttl(self):
        """Test that cache entries do not expire before TTL."""
        # Arrange
        key = "non_expiring_key"
        value = "non_expiring_value"

        # Set with a TTL
        await self.cache_service.set(key, value, ttl=10)  # 10 second TTL

        # Act
        result = await self.cache_service.get(key)

        # Assert
        assert result == value

    async def test_delete_cache_entry(self):
        """Test deleting a cache entry."""
        # Arrange
        key = "deletable_key"
        value = "deletable_value"

        # Set the value
        await self.cache_service.set(key, value)
        initial_result = await self.cache_service.get(key)
        assert initial_result == value

        # Act
        delete_result = await self.cache_service.delete(key)
        after_delete_result = await self.cache_service.get(key)

        # Assert
        assert delete_result is True
        assert after_delete_result is None

    async def test_delete_nonexistent_key(self):
        """Test deleting a non-existent cache key."""
        # Arrange
        key = "nonexistent_key_for_deletion"

        # Act
        result = await self.cache_service.delete(key)

        # Assert
        assert result is False

    async def test_clear_cache(self):
        """Test clearing all cache entries."""
        # Arrange
        key1 = "key1"
        key2 = "key2"
        value1 = "value1"
        value2 = "value2"

        # Set multiple values
        await self.cache_service.set(key1, value1)
        await self.cache_service.set(key2, value2)

        # Verify they exist
        result1_before = await self.cache_service.get(key1)
        result2_before = await self.cache_service.get(key2)
        assert result1_before == value1
        assert result2_before == value2

        # Act
        clear_result = await self.cache_service.clear()

        # Verify they're gone
        result1_after = await self.cache_service.get(key1)
        result2_after = await self.cache_service.get(key2)

        # Assert
        assert clear_result is True
        assert result1_after is None
        assert result2_after is None

    async def test_invalidate_pattern(self):
        """Test invalidating cache entries by pattern."""
        # Arrange
        keys = ["user:profile:123", "user:settings:123", "other:data:456", "user:tasks:123"]
        values = ["profile_data", "settings_data", "other_data", "tasks_data"]

        # Set multiple values
        for key, value in zip(keys, values):
            await self.cache_service.set(key, value)

        # Verify they exist
        for key, value in zip(keys, values):
            assert await self.cache_service.get(key) == value

        # Act
        invalidated_count = await self.cache_service.invalidate_pattern("user:")

        # Verify user-related keys are gone but others remain
        user_keys_after = [await self.cache_service.get(key) for key in keys[:3]]  # First 3 are user keys
        other_key_after = await self.cache_service.get(keys[2])  # This is "other:data:456"

        # Actually, let me fix this - "other:data:456" doesn't contain "user:"
        # So only the first 3 keys should match: "user:profile:123", "user:settings:123", "user:tasks:123"
        # Wait, no - "user:tasks:123" is the 4th element, so indices 0, 1, and 3 contain "user:"
        user_keys = [keys[0], keys[1], keys[3]]  # "user:profile:123", "user:settings:123", "user:tasks:123"
        other_key = keys[2]  # "other:data:456"

        # Check results
        for user_key in user_keys:
            assert await self.cache_service.get(user_key) is None

        assert await self.cache_service.get(other_key) == "other_data"

        # Assert
        assert invalidated_count == 3

    async def test_make_key_generation(self):
        """Test cache key generation with prefix and arguments."""
        # Arrange
        prefix = "user"
        args = ["profile", "123"]

        # Act
        result = self.cache_service.make_key(prefix, *args)

        # Assert
        assert result == "user:profile:123"

    async def test_make_key_with_long_string(self):
        """Test cache key generation with a very long string (should be hashed)."""
        # Arrange
        prefix = "user"
        long_arg = "a" * 300  # Very long string

        # Act
        result = self.cache_service.make_key(prefix, long_arg)

        # Assert
        assert result.startswith(f"{prefix}:")
        assert len(result) <= 255  # Should be shortened

    async def test_cache_complex_objects(self):
        """Test caching complex objects like nested dictionaries and lists."""
        # Arrange
        key = "complex_object"
        value = {
            "user": {
                "id": 123,
                "name": "John Doe",
                "preferences": ["email", "notifications"],
                "settings": {
                    "theme": "dark",
                    "language": "en"
                }
            },
            "tasks": [
                {"id": 1, "title": "Task 1", "completed": False},
                {"id": 2, "title": "Task 2", "completed": True}
            ]
        }

        # Act
        set_result = await self.cache_service.set(key, value)
        get_result = await self.cache_service.get(key)

        # Assert
        assert set_result is True
        assert get_result == value

    async def test_cache_numeric_values(self):
        """Test caching numeric values."""
        # Arrange
        key = "numeric_value"
        value = 42

        # Act
        set_result = await self.cache_service.set(key, value)
        get_result = await self.cache_service.get(key)

        # Assert
        assert set_result is True
        assert get_result == value

    async def test_cache_boolean_values(self):
        """Test caching boolean values."""
        # Arrange
        key = "boolean_value"
        value = True

        # Act
        set_result = await self.cache_service.set(key, value)
        get_result = await self.cache_service.get(key)

        # Assert
        assert set_result is True
        assert get_result == value

    async def test_cache_none_values(self):
        """Test caching None values."""
        # Arrange
        key = "none_value"
        value = None

        # Act
        set_result = await self.cache_service.set(key, value)
        get_result = await self.cache_service.get(key)

        # Assert
        assert set_result is True
        assert get_result == value

    async def test_decorator_caching(self):
        """Test the caching decorator functionality."""
        # Arrange
        call_count = 0

        @self.cache_service.cached(ttl=10, key_prefix="test_func")
        async def test_function(x, y):
            nonlocal call_count
            call_count += 1
            return x + y

        # Act - Call the function twice with same arguments
        result1 = await test_function(1, 2)
        result2 = await test_function(1, 2)

        # Assert
        assert result1 == 3
        assert result2 == 3
        assert call_count == 1  # Function should only be called once due to caching

    async def test_decorator_different_arguments(self):
        """Test the caching decorator with different arguments."""
        # Arrange
        call_count = 0

        @self.cache_service.cached(ttl=10, key_prefix="test_func_diff")
        async def test_function(x, y):
            nonlocal call_count
            call_count += 1
            return x * y

        # Act - Call the function with different arguments
        result1 = await test_function(2, 3)  # Should call function
        result2 = await test_function(2, 3)  # Should use cache
        result3 = await test_function(3, 4)  # Should call function again

        # Assert
        assert result1 == 6
        assert result2 == 6
        assert result3 == 12
        assert call_count == 2  # Function should be called twice (once for each unique args)