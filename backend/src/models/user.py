from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime
import uuid


class UserBase(SQLModel):
    """Base model for User with common fields."""
    email: str = Field(unique=True, index=True, nullable=False)
    first_name: Optional[str] = Field(default=None, max_length=100)
    last_name: Optional[str] = Field(default=None, max_length=100)


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
    email: str = Field(unique=True, index=True, nullable=False)
    hashed_password: str = Field(nullable=False)

    # Personal information
    first_name: Optional[str] = Field(default=None, max_length=100)
    last_name: Optional[str] = Field(default=None, max_length=100)

    # Account status and metadata
    is_active: bool = Field(default=True)
    is_verified: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationships
    tasks: list["Task"] = Relationship(back_populates="owner", sa_relationship_kwargs={"cascade": "all, delete-orphan"})

    def __str__(self) -> str:
        """String representation of the User."""
        return f"User(id={self.id}, email={self.email})"

    def __repr__(self) -> str:
        """Developer-friendly representation of the User."""
        return self.__str__()


class UserCreate(UserBase):
    """Model for creating new users."""
    email: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    class Config:
        """Pydantic configuration for UserCreate."""
        from_attributes = True


class UserUpdate(SQLModel):
    """Model for updating user information."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    is_active: Optional[bool] = None

    class Config:
        """Pydantic configuration for UserUpdate."""
        from_attributes = True


class UserRead(UserBase):
    """Model for reading user information (excluding sensitive data)."""
    id: uuid.UUID
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic configuration for UserRead."""
        from_attributes = True
