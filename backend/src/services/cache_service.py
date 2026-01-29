"""
Cache service for frequently accessed data in the Todo application.

This module implements caching functionality to improve performance
by reducing database queries for frequently accessed data.
"""
import asyncio
import json
from typing import Any, Optional, Dict
from datetime import datetime, timedelta
import hashlib
from functools import wraps


class CacheService:
    """
    Service class for managing cached data in the application.

    Provides methods for storing, retrieving, and invalidating cached data
    with configurable TTL (time-to-live) values.
    """

    def __init__(self):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = 300  # 5 minutes default TTL

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Store a value in the cache with an optional TTL.

        Args:
            key: Cache key
            value: Value to store (will be JSON serialized)
            ttl: Time-to-live in seconds (optional, defaults to default_ttl)

        Returns:
            True if the value was stored successfully, False otherwise
        """
        try:
            ttl_seconds = ttl or self.default_ttl
            expiry_time = datetime.utcnow() + timedelta(seconds=ttl_seconds)

            # Serialize the value to JSON for storage
            serialized_value = json.dumps(value, default=str)

            self.cache[key] = {
                "value": serialized_value,
                "expiry": expiry_time
            }

            return True
        except Exception as e:
            print(f"Error setting cache value for key {key}: {str(e)}")
            return False

    async def get(self, key: str) -> Optional[Any]:
        """
        Retrieve a value from the cache.

        Args:
            key: Cache key

        Returns:
            Cached value if found and not expired, None otherwise
        """
        try:
            if key not in self.cache:
                return None

            cache_entry = self.cache[key]
            expiry_time = cache_entry["expiry"]

            # Check if the entry has expired
            if datetime.utcnow() > expiry_time:
                del self.cache[key]  # Remove expired entry
                return None

            # Deserialize and return the value
            serialized_value = cache_entry["value"]
            return json.loads(serialized_value)
        except Exception as e:
            print(f"Error getting cache value for key {key}: {str(e)}")
            return None

    async def delete(self, key: str) -> bool:
        """
        Remove a value from the cache.

        Args:
            key: Cache key to remove

        Returns:
            True if the key was found and removed, False otherwise
        """
        try:
            if key in self.cache:
                del self.cache[key]
                return True
            return False
        except Exception as e:
            print(f"Error deleting cache value for key {key}: {str(e)}")
            return False

    async def clear(self) -> bool:
        """
        Clear all cached values.

        Returns:
            True if the cache was cleared successfully, False otherwise
        """
        try:
            self.cache.clear()
            return True
        except Exception as e:
            print(f"Error clearing cache: {str(e)}")
            return False

    async def invalidate_pattern(self, pattern: str) -> int:
        """
        Remove all cached values that match a pattern.

        Args:
            pattern: Pattern to match against cache keys

        Returns:
            Number of entries removed
        """
        try:
            keys_to_remove = []
            for key in self.cache:
                if pattern in key:
                    keys_to_remove.append(key)

            for key in keys_to_remove:
                del self.cache[key]

            return len(keys_to_remove)
        except Exception as e:
            print(f"Error invalidating cache pattern {pattern}: {str(e)}")
            return 0

    def make_key(self, prefix: str, *args) -> str:
        """
        Generate a cache key with a prefix and additional identifiers.

        Args:
            prefix: Cache key prefix
            *args: Additional identifiers to include in the key

        Returns:
            Generated cache key
        """
        key_parts = [prefix] + [str(arg) for arg in args]
        key_string = ":".join(key_parts)

        # If the key is too long, hash it
        if len(key_string) > 255:
            hash_part = hashlib.md5(key_string.encode()).hexdigest()
            return f"{prefix}:{hash_part}"

        return key_string

    def cached(self, ttl: Optional[int] = None, key_prefix: str = "func"):
        """
        Decorator to cache the result of a function.

        Args:
            ttl: Time-to-live in seconds for the cached result
            key_prefix: Prefix for the cache key
        """
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Create a cache key based on function name and arguments
                key_args = list(args)
                key_kwargs = sorted(kwargs.items())

                cache_key = self.make_key(
                    key_prefix,
                    func.__name__,
                    str(key_args),
                    str(key_kwargs)
                )

                # Try to get from cache first
                cached_result = await self.get(cache_key)
                if cached_result is not None:
                    return cached_result

                # Execute the function and cache the result
                result = await func(*args, **kwargs)
                await self.set(cache_key, result, ttl)

                return result
            return wrapper
        return decorator


# Global cache instance
cache_service = CacheService()


# Example usage functions
async def get_user_tasks_cached(user_id: str, db_session) -> list:
    """
    Example function that gets user tasks with caching.

    Args:
        user_id: ID of the user whose tasks to retrieve
        db_session: Database session

    Returns:
        List of user's tasks
    """
    cache_key = cache_service.make_key("user_tasks", user_id)

    # Try to get from cache first
    cached_tasks = await cache_service.get(cache_key)
    if cached_tasks is not None:
        print(f"Retrieved tasks for user {user_id} from cache")
        return cached_tasks

    # If not in cache, get from database (this is pseudo-code since we don't have direct DB access here)
    # In a real implementation, this would query the database
    tasks = []  # This would be the result of a database query
    print(f"Fetched tasks for user {user_id} from database")

    # Cache the result for 5 minutes
    await cache_service.set(cache_key, tasks, ttl=300)

    return tasks


async def get_user_profile_cached(user_id: str, db_session) -> dict:
    """
    Example function that gets user profile with caching.

    Args:
        user_id: ID of the user whose profile to retrieve
        db_session: Database session

    Returns:
        User's profile data
    """
    cache_key = cache_service.make_key("user_profile", user_id)

    # Try to get from cache first
    cached_profile = await cache_service.get(cache_key)
    if cached_profile is not None:
        print(f"Retrieved profile for user {user_id} from cache")
        return cached_profile

    # If not in cache, get from database (this is pseudo-code)
    profile = {"id": user_id, "name": "John Doe"}  # This would come from database
    print(f"Fetched profile for user {user_id} from database")

    # Cache the result for 10 minutes
    await cache_service.set(cache_key, profile, ttl=600)

    return profile