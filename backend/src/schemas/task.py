from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class TaskBase(BaseModel):
    """
    Base schema for Task containing common fields for both creation and updates.
    """
    title: str = Field(
        min_length=1,
        max_length=255,
        description="Task title with 1-255 characters"
    )
    description: Optional[str] = Field(
        None,
        max_length=1000,
        description="Optional task description (max 1000 characters)"
    )
    status: str = Field(
        "pending",
        pattern=r"^(pending|in_progress|completed|cancelled)$",
        description="Task status: pending, in_progress, completed, or cancelled"
    )

    @field_validator('status')
    @classmethod
    def validate_status(cls, value):
        """Validate that status is one of the allowed values."""
        allowed_statuses = ["pending", "in_progress", "completed", "cancelled"]
        if value not in allowed_statuses:
            raise ValueError(f"Status must be one of {allowed_statuses}")
        return value


class TaskCreate(TaskBase):
    """
    Schema for creating a new Task.
    Inherits all fields from TaskBase with no additional constraints.
    """
    user_id: int


class TaskUpdate(BaseModel):
    """
    Schema for updating an existing Task.
    All fields are optional to allow partial updates.
    """
    title: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=255,
        description="Task title with 1-255 characters (optional)"
    )
    description: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Optional task description (max length 1000 characters)"
    )
    status: Optional[str] = Field(
        default=None,
        pattern=r"^(pending|in_progress|completed|cancelled)$",
        description="Task status: pending, in_progress, completed, or cancelled (optional)"
    )

    @field_validator('status')
    @classmethod
    def validate_status(cls, value):
        """Validate that status is one of the allowed values."""
        if value is not None:
            allowed_statuses = ["pending", "in_progress", "completed", "cancelled"]
            if value not in allowed_statuses:
                raise ValueError(f"Status must be one of {allowed_statuses}")
        return value


class TaskResponse(TaskBase):
    """
    Schema for returning Task data in API responses.
    Includes all base fields plus database-specific fields.
    """
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    version: int = Field(
        1,
        ge=1,
        description="Version number for optimistic locking"
    )

    class Config:
        """
        Configuration for the Pydantic model to handle ORM objects.
        """
        from_attributes = True


class TaskListResponse(BaseModel):
    """
    Schema for returning a list of tasks in API responses.
    """
    tasks: list[TaskResponse]
    total: int
    page: Optional[int] = None
    limit: Optional[int] = None


class TaskDeleteResponse(BaseModel):
    """
    Schema for successful deletion response.
    """
    success: bool
    message: str
    deleted_task_id: int


class TaskBatchUpdateRequest(BaseModel):
    """
    Schema for batch updating tasks.
    """
    task_ids: list[int] = Field(min_items=1, description="List of task IDs to update")
    status: str = Field(
        pattern=r"^(pending|in_progress|completed|cancelled)$",
        description="New status for all specified tasks"
    )

    @field_validator('status')
    @classmethod
    def validate_status(cls, value):
        """Validate that status is one of the allowed values."""
        allowed_statuses = ["pending", "in_progress", "completed", "cancelled"]
        if value not in allowed_statuses:
            raise ValueError(f"Status must be one of {allowed_statuses}")
        return value


class TaskBatchUpdateResponse(BaseModel):
    """
    Schema for batch update response.
    """
    success: bool
    updated_count: int
    failed_count: int
    message: str


# Alias for backward compatibility
TaskRead = TaskResponse
