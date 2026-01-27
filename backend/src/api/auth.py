"""
Authentication middleware and utilities for the Todo Backend API.

This module handles JWT token validation, user authentication,
and permission checking for protected endpoints using Better Auth.
"""

from typing import Optional, Dict, Any
from datetime import datetime
import logging
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from src.api.deps import get_current_user as deps_get_current_user
from src.models.user import User as UserModel  # Import the actual User model from models


logger = logging.getLogger(__name__)


class User(BaseModel):
    """User model representing authenticated user."""
    id: str
    email: str
    username: Optional[str] = None


# Initialize security scheme
security = HTTPBearer()


# Re-export the main authentication function from deps
get_current_user = deps_get_current_user


async def get_current_active_user(current_user: UserModel = Depends(get_current_user)) -> UserModel:
    """
    Get current active user, extending basic authentication with additional checks.

    Args:
        current_user: The currently authenticated user

    Returns:
        User object if active and authorized
    """
    # In a real application, you might check if the user is active, suspended, etc.
    # For now, we'll just return the current user
    # Additional checks could include:
    # - User account status (active/suspended)
    # - Account verification status
    # - Role-based access checks

    # Placeholder for additional user validation
    # if current_user.is_suspended:
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="User account is inactive"
    #     )

    return current_user


def require_permission(permission: str):
    """
    Create a dependency that requires a specific permission.

    Args:
        permission: The permission required to access the endpoint

    Returns:
        Dependency function for FastAPI
    """
    async def permission_checker(current_user: UserModel = Depends(get_current_active_user)):
        # In a real application, this would check user permissions against a permission system
        # For now, we'll implement a basic permission check
        user_permissions = await get_user_permissions(str(current_user.id))

        if permission not in user_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission}' required"
            )

        return current_user

    return permission_checker


async def get_user_permissions(user_id: str) -> list[str]:
    """
    Get permissions for a specific user.

    Args:
        user_id: The ID of the user to get permissions for

    Returns:
        List of permissions for the user
    """
    # This would typically fetch permissions from a database
    # For now, return default permissions for all users
    # In production, implement proper permission system

    # Default permissions for all users
    default_permissions = [
        "read:tasks",
        "create:tasks",
        "update:tasks",
        "delete:tasks"
    ]

    # In a real implementation, you would query the database:
    # permissions = await db.execute(
    #     select(Permission.name)
    #     .join(UserPermission)
    #     .where(UserPermission.user_id == user_id)
    # )
    # return [perm[0] for perm in permissions.fetchall()]

    return default_permissions


# Convenience aliases for common dependencies
CurrentUser = Depends(get_current_user)
CurrentActiveUser = Depends(get_current_active_user)


def CurrentUserWithPermission(permission: str):
    """
    Convenience function to get current user with required permission.

    Args:
        permission: The permission required

    Returns:
        Dependency for the current user with the specified permission
    """
    return Depends(require_permission(permission))