from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from src.schemas.task import TaskCreate, TaskRead, TaskUpdate
from src.services.task_service import TaskService
from src.models.task import Task
from src.api.deps import get_task_service
from src.api.auth import get_current_active_user
from src.models.user import User


router = APIRouter()


@router.post("/tasks/", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(
    task: TaskCreate,
    task_service: TaskService = Depends(get_task_service),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new task"""
    return await task_service.create_task(task, current_user)


@router.get("/tasks/{task_id}", response_model=TaskRead)
async def get_task(
    task_id: str,
    task_service: TaskService = Depends(get_task_service),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific task by ID"""
    task = await task_service.get_task_by_id(task_id, current_user)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put("/tasks/{task_id}", response_model=TaskRead)
async def update_task(
    task_id: str,
    task_update: TaskUpdate,
    task_service: TaskService = Depends(get_task_service),
    current_user: User = Depends(get_current_active_user)
):
    """Update a specific task by ID"""
    updated_task = await task_service.update_task(task_id, task_update, current_user)
    if not updated_task:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated_task


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: str,
    task_service: TaskService = Depends(get_task_service),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a specific task by ID"""
    deleted = await task_service.delete_task(task_id, current_user)
    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found")


@router.get("/tasks/", response_model=List[TaskRead])
async def get_tasks(
    skip: int = 0,
    limit: int = 100,
    task_service: TaskService = Depends(get_task_service),
    current_user: User = Depends(get_current_active_user)
):
    """Get all tasks with pagination"""
    return await task_service.get_tasks(skip=skip, limit=limit, current_user=current_user)
