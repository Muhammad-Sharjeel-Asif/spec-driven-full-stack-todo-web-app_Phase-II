from datetime import datetime
from typing import Optional
import uuid
from sqlmodel import SQLModel, Field, Relationship
from pydantic import BaseModel, ConfigDict
from .user import User


class TaskBase(SQLModel):
    """Base model for Task with common fields."""

    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    is_completed: bool = Field(default=False)
    priority: int = Field(default=1, ge=1, le=5)  # 1-5 scale, 1 being lowest priority
    due_date: Optional[datetime] = Field(default=None)

    model_config = ConfigDict(from_attributes=True)


class Task(TaskBase, table=True):
    """Task model representing a todo item in the database."""

    __tablename__ = "tasks"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)
    version: int = Field(default=1)  # For optimistic locking

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = Field(default=None)  # For soft deletes

    # Relationships
    owner: "User" = Relationship(back_populates="tasks")

    # Notification settings stored as JSON
    notification_settings: Optional[str] = Field(default='{"reminder_enabled": false, "reminder_time": null}')

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class TaskCreate(TaskBase):
    """Schema for creating a new task."""

    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    priority: int = Field(default=1, ge=1, le=5)
    due_date: Optional[datetime] = Field(default=None)
    user_id: uuid.UUID  # Required for creating a task for a specific user


class TaskUpdate(SQLModel):
    """Schema for updating an existing task."""

    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    is_completed: Optional[bool] = None
    priority: Optional[int] = Field(default=None, ge=1, le=5)
    due_date: Optional[datetime] = Field(default=None)

    model_config = ConfigDict(from_attributes=True)


class TaskRead(TaskBase):
    """Schema for reading task data."""

    id: uuid.UUID
    user_id: uuid.UUID
    version: int
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None  # For soft deletes
    notification_settings: Optional[str] = '{"reminder_enabled": false, "reminder_time": null}'

    model_config = ConfigDict(from_attributes=True)
