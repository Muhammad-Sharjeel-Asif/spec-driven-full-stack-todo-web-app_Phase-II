from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime
import uuid
from pydantic import ConfigDict
from .user import User


class AuthenticationTokenBase(SQLModel):
    """Base model for AuthenticationToken with common fields."""
    token: str = Field(..., max_length=500, unique=True, index=True)
    user_id: uuid.UUID = Field(..., foreign_key="users.id", index=True)
    issued_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime = Field(...)
    is_revoked: bool = Field(default=False)


class AuthenticationToken(AuthenticationTokenBase, table=True):
    """
    AuthenticationToken model representing JWT tokens in the database.

    Contains token information including the associated user, issue/expiration dates,
    and revocation status for proper session management.
    """
    __tablename__ = "auth_tokens"

    # Primary key
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True
    )

    # Relationships
    user: User = Relationship(back_populates="auth_tokens")

    model_config = ConfigDict(from_attributes=True)

    def __str__(self) -> str:
        """String representation of the AuthenticationToken."""
        return f"AuthenticationToken(id={self.id}, user_id={self.user_id}, expired={self.is_expired()})"

    def __repr__(self) -> str:
        """Developer-friendly representation of the AuthenticationToken."""
        return self.__str__()

    def is_expired(self) -> bool:
        """Check if the token has expired."""
        return datetime.utcnow() > self.expires_at

    def is_valid(self) -> bool:
        """Check if the token is valid (not expired and not revoked)."""
        return not self.is_expired() and not self.is_revoked


class AuthenticationTokenCreate(AuthenticationTokenBase):
    """Model for creating new authentication tokens."""
    token: str
    user_id: uuid.UUID
    expires_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AuthenticationTokenUpdate(SQLModel):
    """Model for updating authentication token information."""
    is_revoked: Optional[bool] = None

    model_config = ConfigDict(from_attributes=True)


class AuthenticationTokenRead(AuthenticationTokenBase):
    """Model for reading authentication token information."""
    id: uuid.UUID
    issued_at: datetime
    expires_at: datetime
    is_revoked: bool

    model_config = ConfigDict(from_attributes=True)