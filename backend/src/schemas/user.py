"""User schemas for the Todo Backend API.

This module contains Pydantic schemas for User management operations
including user creation, update, and read operations. It also includes
password handling schemas for secure authentication.
"""

from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime
import uuid


class UserBase(BaseModel):
    """Base schema for User with common fields shared across operations."""

    email: EmailStr = Field(..., description="User's email address")
    first_name: Optional[str] = Field(
        default=None,
        max_length=100,
        description="User's first name"
    )
    last_name: Optional[str] = Field(
        default=None,
        max_length=100,
        description="User's last name"
    )

    class Config:
        """Pydantic configuration for User schemas."""
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            uuid.UUID: lambda v: str(v)
        }


class UserCreate(UserBase):
    """Schema for creating new users with validation rules."""

    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="User's password (minimum 8 characters)"
    )
    first_name: Optional[str] = Field(
        default=None,
        max_length=100,
        description="User's first name"
    )
    last_name: Optional[str] = Field(
        default=None,
        max_length=100,
        description="User's last name"
    )

    @validator('password')
    def validate_password(cls, v):
        """Validate password strength requirements."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')

        # Check for password complexity
        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in v)

        if not (has_upper and has_lower and has_digit):
            raise ValueError(
                'Password must contain at least one uppercase letter, '
                'one lowercase letter, and one digit'
            )

        return v


class UserUpdate(BaseModel):
    """Schema for updating user information with optional fields."""

    first_name: Optional[str] = Field(
        default=None,
        max_length=100,
        description="User's first name"
    )
    last_name: Optional[str] = Field(
        default=None,
        max_length=100,
        description="User's last name"
    )
    email: Optional[EmailStr] = Field(
        default=None,
        description="User's email address"
    )
    is_active: Optional[bool] = Field(
        default=None,
        description="Whether the user account is active"
    )

    class Config:
        """Pydantic configuration for UserUpdate."""
        from_attributes = True
        str_strip_whitespace = True


class UserRead(UserBase):
    """Schema for reading user information (excludes sensitive data)."""

    id: uuid.UUID = Field(..., description="Unique identifier for the user")
    is_active: bool = Field(default=True, description="Whether the user account is active")
    is_verified: bool = Field(default=False, description="Whether the user has verified their email")
    created_at: datetime = Field(..., description="Timestamp when the user account was created")
    updated_at: datetime = Field(..., description="Timestamp when the user account was last updated")

    class Config:
        """Pydantic configuration for UserRead."""
        from_attributes = True


class UserLogin(BaseModel):
    """Schema for user login credentials."""

    email: EmailStr = Field(..., description="User's email address for login")
    password: str = Field(..., description="User's password")

    class Config:
        """Pydantic configuration for UserLogin."""
        from_attributes = True


class UserRegister(UserCreate):
    """Schema for user registration (extends UserCreate if needed)."""
    pass


class UserChangePassword(BaseModel):
    """Schema for changing user password."""

    current_password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Current password for verification"
    )
    new_password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="New password (minimum 8 characters)"
    )

    @validator('new_password')
    def validate_new_password(cls, v):
        """Validate new password strength requirements."""
        if len(v) < 8:
            raise ValueError('New password must be at least 8 characters long')

        # Check for password complexity
        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in v)

        if not (has_upper and has_lower and has_digit):
            raise ValueError(
                'New password must contain at least one uppercase letter, '
                'one lowercase letter, and one digit'
            )

        return v


class UserForgotPassword(BaseModel):
    """Schema for initiating password reset."""

    email: EmailStr = Field(..., description="Email address for password reset")


class UserResetPassword(BaseModel):
    """Schema for resetting password with token."""

    token: str = Field(..., description="Password reset token")
    new_password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="New password (minimum 8 characters)"
    )

    @validator('new_password')
    def validate_reset_password(cls, v):
        """Validate reset password strength requirements."""
        if len(v) < 8:
            raise ValueError('New password must be at least 8 characters long')

        # Check for password complexity
        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in v)

        if not (has_upper and has_lower and has_digit):
            raise ValueError(
                'New password must contain at least one uppercase letter, '
                'one lowercase letter, and one digit'
            )

        return v


class TokenResponse(BaseModel):
    """Schema for authentication token response."""

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Type of token")
    expires_in: int = Field(..., description="Token expiration time in seconds")


class UserPublic(BaseModel):
    """Public user information schema (minimal data for sharing)."""

    id: uuid.UUID = Field(..., description="Unique identifier for the user")
    email: EmailStr = Field(..., description="User's email address")
    first_name: Optional[str] = Field(
        default=None,
        description="User's first name"
    )
    last_name: Optional[str] = Field(
        default=None,
        description="User's last name"
    )
    created_at: datetime = Field(..., description="Account creation timestamp")

    class Config:
        """Pydantic configuration for UserPublic."""
        from_attributes = True
