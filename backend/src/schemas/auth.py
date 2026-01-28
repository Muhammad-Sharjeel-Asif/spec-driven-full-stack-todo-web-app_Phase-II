from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator
import re
import uuid


class LoginRequest(BaseModel):
    """
    Schema for login request payload
    """
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="User's password (min 8 characters)"
    )


class LoginResponse(BaseModel):
    """
    Schema for login response payload
    """
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Type of token")
    user_id: int = Field(..., description="User's unique identifier")
    email: EmailStr = Field(..., description="User's email address")


class RegisterRequest(BaseModel):
    """
    Schema for registration request payload
    """
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="User's password (min 8 characters)"
    )
    confirm_password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Password confirmation"
    )

    @field_validator('password')
    def validate_password_strength(cls, v):
        """
        Validate password strength requirements
        """
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v

    @field_validator('confirm_password')
    def passwords_match(cls, v, info):
        """
        Validate that passwords match
        """
        if info.data and 'password' in info.data and v != info.data['password']:
            raise ValueError('Passwords do not match')
        return v


class RegisterResponse(BaseModel):
    """
    Schema for registration response payload
    """
    user_id: int = Field(..., description="Newly created user's unique identifier")
    email: EmailStr = Field(..., description="User's email address")
    message: str = Field(default="User registered successfully", description="Success message")


class Token(BaseModel):
    """
    Schema for JWT token
    """
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(..., description="Type of token")
    refresh_token: Optional[str] = Field(None, description="Refresh token")


class TokenData(BaseModel):
    """
    Schema for token data payload
    """
    user_id: Optional[uuid.UUID] = Field(None, description="User's unique identifier")
    email: Optional[EmailStr] = Field(None, description="User's email address")


class RefreshTokenRequest(BaseModel):
    """
    Schema for refresh token request
    """
    refresh_token: str = Field(..., description="Refresh token")


class RefreshTokenResponse(BaseModel):
    """
    Schema for refresh token response
    """
    access_token: str = Field(..., description="New JWT access token")
    token_type: str = Field(default="bearer", description="Type of token")


class ForgotPasswordRequest(BaseModel):
    """
    Schema for forgot password request
    """
    email: EmailStr = Field(..., description="User's email address")


class ForgotPasswordResponse(BaseModel):
    """
    Schema for forgot password response
    """
    message: str = Field(
        default="Password reset email sent if account exists",
        description="Message indicating the action taken"
    )


class ResetPasswordRequest(BaseModel):
    """
    Schema for password reset request
    """
    token: str = Field(..., description="Password reset token")
    new_password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="New password (min 8 characters)"
    )
    confirm_new_password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Confirmation of new password"
    )

    @field_validator('new_password')
    def validate_new_password_strength(cls, v):
        """
        Validate new password strength requirements
        """
        if not re.search(r'[A-Z]', v):
            raise ValueError('New password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('New password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('New password must contain at least one digit')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('New password must contain at least one special character')
        return v

    @field_validator('confirm_new_password')
    def new_passwords_match(cls, v, info):
        """
        Validate that new passwords match
        """
        if info.data and 'new_password' in info.data and v != info.data['new_password']:
            raise ValueError('New passwords do not match')
        return v


class ResetPasswordResponse(BaseModel):
    """
    Schema for password reset response
    """
    message: str = Field(default="Password reset successful", description="Success message")


class ChangePasswordRequest(BaseModel):
    """
    Schema for password change request
    """
    current_password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Current password (min 8 characters)"
    )
    new_password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="New password (min 8 characters)"
    )
    confirm_new_password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Confirmation of new password"
    )

    @field_validator('new_password')
    def validate_new_password_strength_change(cls, v):
        """
        Validate new password strength requirements for change
        """
        if not re.search(r'[A-Z]', v):
            raise ValueError('New password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('New password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('New password must contain at least one digit')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('New password must contain at least one special character')
        return v

    @field_validator('confirm_new_password')
    def new_passwords_match_change(cls, v, info):
        """
        Validate that new passwords match for change
        """
        if info.data and 'new_password' in info.data and v != info.data['new_password']:
            raise ValueError('New passwords do not match')
        return v


class ChangePasswordResponse(BaseModel):
    """
    Schema for password change response
    """
    message: str = Field(default="Password changed successfully", description="Success message")


class UserProfileResponse(BaseModel):
    """
    Schema for user profile response
    """
    user_id: int = Field(..., description="User's unique identifier")
    email: EmailStr = Field(..., description="User's email address")
    created_at: str = Field(..., description="Account creation timestamp")
    updated_at: str = Field(..., description="Last account update timestamp")
