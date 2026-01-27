"""
Custom exception definitions for the Todo Backend API.

This module defines custom exception classes for various error scenarios
in the application, including authentication, authorization, validation,
database, and business logic errors. These exceptions integrate with
FastAPI's HTTPException for proper HTTP error responses.
"""

from typing import Any, Dict, Optional
from fastapi import HTTPException, status


class BaseAppException(Exception):
    """Base application exception"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class UserNotFoundException(BaseAppException):
    """Raised when a user is not found"""
    pass


class TaskNotFoundException(BaseAppException):
    """Raised when a task is not found"""
    pass


class AuthenticationException(HTTPException):
    """Raised when authentication fails"""
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class AuthorizationException(HTTPException):
    """Raised when authorization fails"""
    def __init__(self, detail: str = "Not enough permissions"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )


class ValidationErrorException(BaseAppException):
    """Raised when validation fails"""
    pass


class TodoBaseException(Exception):
    """
    Base exception class for all custom exceptions in the Todo API.

    This serves as the parent class for all custom exceptions to allow
    catching multiple exception types with a single except clause.
    """
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class AuthenticationError(TodoBaseException):
    """
    Exception raised when authentication fails.

    This occurs when user credentials are invalid, token is expired,
    or JWT verification fails.
    """
    def __init__(self, message: str = "Authentication failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)

    def to_http_exception(self) -> HTTPException:
        """Convert this exception to an HTTPException with appropriate status code."""
        return HTTPException(
            status_code=401,
            detail={
                "error": "authentication_error",
                "message": self.message,
                "details": self.details
            }
        )


class AuthorizationError(TodoBaseException):
    """
    Exception raised when a user is authenticated but lacks sufficient permissions.

    This occurs when a user tries to access resources they don't have permission to access.
    """
    def __init__(self, message: str = "Insufficient permissions", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)

    def to_http_exception(self) -> HTTPException:
        """Convert this exception to an HTTPException with appropriate status code."""
        return HTTPException(
            status_code=403,
            detail={
                "error": "authorization_error",
                "message": self.message,
                "details": self.details
            }
        )


class ValidationError(TodoBaseException):
    """
    Exception raised when input validation fails.

    This occurs when request data doesn't meet validation requirements,
    such as invalid format, missing required fields, or out-of-range values.
    """
    def __init__(self, message: str = "Validation failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)

    def to_http_exception(self) -> HTTPException:
        """Convert this exception to an HTTPException with appropriate status code."""
        return HTTPException(
            status_code=422,
            detail={
                "error": "validation_error",
                "message": self.message,
                "details": self.details
            }
        )


class DatabaseError(TodoBaseException):
    """
    Exception raised when database operations fail.

    This occurs when there are issues with database connectivity,
    query execution, or constraint violations.
    """
    def __init__(self, message: str = "Database error occurred", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)

    def to_http_exception(self) -> HTTPException:
        """Convert this exception to an HTTPException with appropriate status code."""
        return HTTPException(
            status_code=500,
            detail={
                "error": "database_error",
                "message": self.message,
                "details": self.details
            }
        )


class BusinessLogicError(TodoBaseException):
    """
    Exception raised when business logic validation fails.

    This occurs when an operation violates business rules, such as
    attempting to delete a protected resource or performing an
    invalid state transition.
    """
    def __init__(self, message: str = "Business logic violation", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)

    def to_http_exception(self) -> HTTPException:
        """Convert this exception to an HTTPException with appropriate status code."""
        # Using 422 for business logic errors as they often indicate invalid requests
        # based on business rules, though 400 could also be appropriate
        return HTTPException(
            status_code=422,
            detail={
                "error": "business_logic_error",
                "message": self.message,
                "details": self.details
            }
        )


class ResourceNotFoundError(TodoBaseException):
    """
    Exception raised when a requested resource is not found.

    This occurs when trying to access or modify a resource that doesn't exist.
    """
    def __init__(self, message: str = "Resource not found", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)

    def to_http_exception(self) -> HTTPException:
        """Convert this exception to an HTTPException with appropriate status code."""
        return HTTPException(
            status_code=404,
            detail={
                "error": "resource_not_found",
                "message": self.message,
                "details": self.details
            }
        )


class DuplicateResourceError(TodoBaseException):
    """
    Exception raised when attempting to create a resource that already exists.

    This occurs when trying to create a resource with a unique identifier
    that is already in use.
    """
    def __init__(self, message: str = "Resource already exists", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)

    def to_http_exception(self) -> HTTPException:
        """Convert this exception to an HTTPException with appropriate status code."""
        return HTTPException(
            status_code=409,
            detail={
                "error": "duplicate_resource",
                "message": self.message,
                "details": self.details
            }
        )


# Convenience functions for raising exceptions
def raise_auth_error(message: str = "Authentication failed", details: Optional[Dict[str, Any]] = None) -> None:
    """Raise an AuthenticationError with the given message and details."""
    raise AuthenticationError(message, details)


def raise_authz_error(message: str = "Insufficient permissions", details: Optional[Dict[str, Any]] = None) -> None:
    """Raise an AuthorizationError with the given message and details."""
    raise AuthorizationError(message, details)


def raise_validation_error(message: str = "Validation failed", details: Optional[Dict[str, Any]] = None) -> None:
    """Raise a ValidationError with the given message and details."""
    raise ValidationError(message, details)


def raise_db_error(message: str = "Database error occurred", details: Optional[Dict[str, Any]] = None) -> None:
    """Raise a DatabaseError with the given message and details."""
    raise DatabaseError(message, details)


def raise_business_error(message: str = "Business logic violation", details: Optional[Dict[str, Any]] = None) -> None:
    """Raise a BusinessLogicError with the given message and details."""
    raise BusinessLogicError(message, details)


def raise_not_found_error(message: str = "Resource not found", details: Optional[Dict[str, Any]] = None) -> None:
    """Raise a ResourceNotFoundError with the given message and details."""
    raise ResourceNotFoundError(message, details)


def raise_duplicate_error(message: str = "Resource already exists", details: Optional[Dict[str, Any]] = None) -> None:
    """Raise a DuplicateResourceError with the given message and details."""
    raise DuplicateResourceError(message, details)
