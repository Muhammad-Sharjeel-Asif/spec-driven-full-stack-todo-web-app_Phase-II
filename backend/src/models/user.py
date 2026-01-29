from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime
import uuid
from pydantic import ConfigDict
import json


class UserBase(SQLModel):
    """Base model for User with common fields."""
    email: str = Field(..., max_length=255, unique=True, index=True)
    first_name: Optional[str] = Field(default=None, max_length=100)
    last_name: Optional[str] = Field(default=None, max_length=100)

    model_config = ConfigDict(from_attributes=True)


class User(UserBase, table=True):
    """
    User model representing application users.

    Contains user account information including authentication details,
    personal information, and timestamps for tracking account lifecycle.
    """
    __tablename__ = "users"

    # Primary key
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True
    )

    # User credentials and authentication
    hashed_password: str = Field(nullable=False)

    # Account status and metadata
    is_active: bool = Field(default=True)
    is_verified: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    tasks: list["Task"] = Relationship(back_populates="owner", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    auth_tokens: list["AuthenticationToken"] = Relationship(back_populates="user", sa_relationship_kwargs={"cascade": "all, delete-orphan"})

    # Notification preferences stored as JSON
    notification_preferences: Optional[str] = Field(default='{"due_date_reminders": true, "email_notifications": false}')

    def __str__(self) -> str:
        """String representation of the User."""
        return f"User(id={self.id}, email={self.email})"

    def __repr__(self) -> str:
        """Developer-friendly representation of the User."""
        return self.__str__()


class UserCreate(UserBase):
    """Model for creating new users."""
    password: str

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(SQLModel):
    """Model for updating user information."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    is_active: Optional[bool] = None

    model_config = ConfigDict(from_attributes=True)


class UserRead(UserBase):
    """Model for reading user information (excluding sensitive data)."""
    id: uuid.UUID
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
