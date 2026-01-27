"""
Base Pydantic models for the Todo Backend API.

This module contains base schema classes and common fields that can be
inherited by other Pydantic models throughout the application.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """
    Base schema class with common configurations for all Pydantic models.

    This class provides shared configuration settings and common fields
    that can be inherited by other schema classes.
    """

    # Pydantic v2 configuration
    model_config = ConfigDict(
        # Allow extra fields during development, can be changed to 'forbid' for stricter validation
        extra='ignore',
        # Validate default values during model creation
        validate_default=True,
        # Use aliases for field names
        populate_by_name=True,
        # Enable arbitrary types to support custom types
        arbitrary_types_allowed=True,
        # Set validation error handling
        strict=False,
    )


class TimestampMixin(BaseModel):
    """
    Mixin class to add timestamp fields to Pydantic models.

    Provides created_at and updated_at timestamp fields that can be
    included in other schema classes that need temporal tracking.
    """

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(populate_by_name=True)


class IDMixin(BaseModel):
    """
    Mixin class to add ID field to Pydantic models.

    Provides a common id field that can be included in other schema classes
    that need a primary identifier.
    """

    id: int

    model_config = ConfigDict(populate_by_name=True)


class BaseResponse(BaseSchema):
    """
    Base response schema with common fields for API responses.

    This class can be inherited by specific response models to ensure
    consistent response structure across the API.
    """

    success: bool = True
    message: Optional[str] = None


class BaseRequest(BaseSchema):
    """
    Base request schema with common configurations for API requests.

    This class can be inherited by specific request models to ensure
    consistent request structure across the API.
    """

    pass


class PaginatedResponse(BaseResponse):
    """
    Base paginated response schema with pagination metadata.

    Used for API responses that return collections of items with pagination.
    """

    total: int
    page: int
    size: int
    pages: int


# Common response schemas
class SuccessResponse(BaseResponse):
    """Standard success response schema."""
    success: bool = True
    message: str


class ErrorResponse(BaseResponse):
    """Standard error response schema."""
    success: bool = False
    message: str
    error_code: Optional[str] = None
    details: Optional[dict] = None


# Common request schemas
class CreateRequest(BaseRequest):
    """Base schema for create operations."""
    pass


class UpdateRequest(BaseRequest):
    """Base schema for update operations."""
    pass


__all__ = [
    'BaseSchema',
    'TimestampMixin',
    'IDMixin',
    'BaseResponse',
    'BaseRequest',
    'PaginatedResponse',
    'SuccessResponse',
    'ErrorResponse',
    'CreateRequest',
    'UpdateRequest',
]