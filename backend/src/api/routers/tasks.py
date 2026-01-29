from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from ...config.database import get_db_session  # Use async database session
from ...models.task import Task, TaskCreate, TaskUpdate, TaskRead
from ...models.user import User
from ...services.task_service import TaskService
from ...middleware.auth_middleware import get_current_user_from_request
from ...utils.jwt_utils import validate_better_auth_token


router = APIRouter()


@router.get("/{user_id}/tasks", response_model=List[TaskRead])
async def get_user_tasks(
    user_id: UUID,
    status: Optional[str] = Query(None, description="Filter by completion status: 'all', 'completed', 'pending'"),
    priority: Optional[str] = Query(None, description="Filter by priority: 'high', 'medium', 'low'"),
    due_date_from: Optional[datetime] = Query(None, description="Filter tasks with due date on or after this date"),
    due_date_to: Optional[datetime] = Query(None, description="Filter tasks with due date on or before this date"),
    skip: int = Query(0, ge=0, description="Number of records to skip for pagination"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    sort_by: str = Query("created_at", description="Field to sort by"),
    sort_order: str = Query("desc", description="Sort order: 'asc' or 'desc'"),
    current_user: User = Depends(get_current_user_from_request),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get all tasks for a specific user with optional filtering and sorting.

    This endpoint returns tasks that belong to the specified user ID,
    with various filtering options to narrow down the results.
    """
    # Verify that the requested user_id matches the authenticated user's ID
    if str(current_user.id) != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Cannot access another user's tasks"
        )

    # Initialize task service with the database session
    task_service = TaskService(db)

    # Retrieve tasks for the user with all filters
    all_tasks = await task_service.get_tasks(
        skip=skip,
        limit=limit,
        current_user=current_user,
        status=status,
        priority=priority,
        due_date_from=due_date_from,
        due_date_to=due_date_to
    )

    # Apply filters manually since the service doesn't have filter-by-user-id method
    filtered_tasks = []
    for task in all_tasks:
        if str(task.user_id) == str(user_id):  # Ensure task belongs to requested user
            # Apply additional filters
            include_task = True

            # Status filter
            if status and include_task:
                if status == "completed" and not task.is_completed:
                    include_task = False
                elif status == "pending" and task.is_completed:
                    include_task = False

            # Priority filter (assuming priority is stored as an integer: 1=low, 2=medium, 3=high)
            if priority and include_task:
                priority_map = {"low": 1, "medium": 2, "high": 3}
                if priority in priority_map and task.priority != priority_map[priority]:
                    include_task = False

            # Due date filters
            if due_date_from and include_task and task.due_date:
                if task.due_date < due_date_from:
                    include_task = False

            if due_date_to and include_task and task.due_date:
                if task.due_date > due_date_to:
                    include_task = False

            if include_task:
                filtered_tasks.append(task)

    # Apply sorting
    if sort_by == "created_at":
        filtered_tasks.sort(key=lambda x: x.created_at, reverse=(sort_order == "desc"))
    elif sort_by == "updated_at":
        filtered_tasks.sort(key=lambda x: x.updated_at or x.created_at, reverse=(sort_order == "desc"))
    elif sort_by == "due_date":
        filtered_tasks.sort(key=lambda x: x.due_date or datetime.max, reverse=(sort_order == "desc"))
    elif sort_by == "priority":
        filtered_tasks.sort(key=lambda x: x.priority or 0, reverse=(sort_order == "desc"))

    # Apply pagination
    start_idx = skip
    end_idx = min(skip + limit, len(filtered_tasks))
    paginated_tasks = filtered_tasks[start_idx:end_idx]

    return paginated_tasks


@router.post("/{user_id}/tasks", response_model=TaskRead)
async def create_user_task(
    user_id: UUID,
    task_create: TaskCreate,
    current_user: User = Depends(get_current_user_from_request),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Create a new task for a specific user.

    This endpoint creates a task that belongs to the specified user ID.
    The user must be authenticated and match the user_id in the path.
    """
    # Verify that the requested user_id matches the authenticated user's ID
    if str(current_user.id) != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Cannot create tasks for another user"
        )

    # Initialize task service with the database session
    task_service = TaskService(db)

    # Ensure the task is created for the correct user
    task_create.user_id = user_id

    # Create the task
    task = await task_service.create_task(task_create, current_user)
    return task


@router.get("/{user_id}/tasks/{task_id}", response_model=TaskRead)
async def get_user_task(
    user_id: UUID,
    task_id: UUID,
    current_user: User = Depends(get_current_user_from_request),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get a specific task for a user.

    This endpoint retrieves a specific task that belongs to the specified user ID.
    The user must be authenticated and match the user_id in the path.
    """
    # Verify that the requested user_id matches the authenticated user's ID
    if str(current_user.id) != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Cannot access another user's task"
        )

    # Initialize task service with the database session
    task_service = TaskService(db)

    # Retrieve the specific task
    task = await task_service.get_task_by_id(task_id, current_user)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return task


@router.put("/{user_id}/tasks/{task_id}", response_model=TaskRead)
async def update_user_task(
    user_id: UUID,
    task_id: UUID,
    task_update: TaskUpdate,
    current_user: User = Depends(get_current_user_from_request),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Update a specific task for a user.

    This endpoint updates a specific task that belongs to the specified user ID.
    The user must be authenticated and match the user_id in the path.
    """
    # Verify that the requested user_id matches the authenticated user's ID
    if str(current_user.id) != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Cannot update another user's task"
        )

    # Initialize task service with the database session
    task_service = TaskService(db)

    # Update the task
    updated_task = await task_service.update_task(task_id, task_update, current_user)
    if not updated_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or access denied"
        )

    return updated_task


@router.delete("/{user_id}/tasks/{task_id}")
async def delete_user_task(
    user_id: UUID,
    task_id: UUID,
    current_user: User = Depends(get_current_user_from_request),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Delete a specific task for a user.

    This endpoint performs a soft delete of a specific task that belongs to the specified user ID.
    The user must be authenticated and match the user_id in the path.
    """
    # Verify that the requested user_id matches the authenticated user's ID
    if str(current_user.id) != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Cannot delete another user's task"
        )

    # Initialize task service with the database session
    task_service = TaskService(db)

    # Delete the task
    success = await task_service.delete_task(task_id, current_user)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or access denied"
        )

    return {"message": "Task deleted successfully"}


@router.patch("/{user_id}/tasks/{task_id}/complete", response_model=TaskRead)
async def toggle_task_completion(
    user_id: UUID,
    task_id: UUID,
    current_user: User = Depends(get_current_user_from_request),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Toggle the completion status of a task.

    This endpoint toggles the completion status of a specific task that belongs to the specified user ID.
    The user must be authenticated and match the user_id in the path.
    """
    # Verify that the requested user_id matches the authenticated user's ID
    if str(current_user.id) != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Cannot modify another user's task"
        )

    # Initialize task service with the database session
    task_service = TaskService(db)

    # Toggle task completion status
    updated_task = await task_service.toggle_task_completion(task_id, current_user)
    if not updated_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or access denied"
        )

    return updated_task


@router.get("/{user_id}/tasks/stats")
async def get_user_task_stats(
    user_id: UUID,
    current_user: User = Depends(get_current_user_from_request),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get task statistics for a user.

    This endpoint returns statistics about a user's tasks, such as total count,
    completed count, and pending count.
    """
    # Verify that the requested user_id matches the authenticated user's ID
    if str(current_user.id) != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Cannot access another user's task stats"
        )

    # Initialize task service with the database session
    task_service = TaskService(db)

    # Get all tasks for the user to calculate statistics
    all_user_tasks = await task_service.get_tasks(skip=0, limit=10000, current_user=current_user)

    # Filter tasks for this specific user
    user_tasks = [task for task in all_user_tasks if str(task.user_id) == str(user_id)]

    # Calculate statistics
    total_count = len(user_tasks)
    completed_count = len([task for task in user_tasks if task.is_completed])
    pending_count = len([task for task in user_tasks if not task.is_completed])

    return {
        "total": total_count,
        "completed": completed_count,
        "pending": pending_count
    }


@router.get("/{user_id}/tasks/deleted")
async def get_user_deleted_tasks(
    user_id: UUID,
    skip: int = Query(0, ge=0, description="Number of records to skip for pagination"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    current_user: User = Depends(get_current_user_from_request),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get soft-deleted tasks for a specific user.

    This endpoint returns tasks that belong to the specified user ID that have been soft-deleted.
    The user must be authenticated and match the user_id in the path.
    """
    # Verify that the requested user_id matches the authenticated user's ID
    if str(current_user.id) != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Cannot access another user's tasks"
        )

    # Initialize task service with the database session
    task_service = TaskService(db)

    # Get soft-deleted tasks for the user
    deleted_tasks = await task_service.get_deleted_tasks(skip=skip, limit=limit, current_user=current_user)

    return deleted_tasks


@router.post("/{user_id}/tasks/{task_id}/restore", response_model=TaskRead)
async def restore_user_task(
    user_id: UUID,
    task_id: UUID,
    current_user: User = Depends(get_current_user_from_request),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Restore a soft-deleted task for a user.

    This endpoint restores a task that was previously soft-deleted for the specified user ID.
    The user must be authenticated and match the user_id in the path.
    """
    # Verify that the requested user_id matches the authenticated user's ID
    if str(current_user.id) != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Cannot restore another user's task"
        )

    # Initialize task service with the database session
    task_service = TaskService(db)

    # Restore the task
    restored_task = await task_service.restore_task(task_id, current_user)
    if not restored_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or access denied"
        )

    return restored_task