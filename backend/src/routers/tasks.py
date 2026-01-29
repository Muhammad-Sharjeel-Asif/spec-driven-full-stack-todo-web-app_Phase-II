"""
Router for task-related endpoints.

This module defines all the API routes related to task management
in the Todo App Evolution project.
"""
from fastapi import APIRouter


router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/")
async def get_tasks():
    """Get all tasks for the authenticated user."""
    return {"message": "Get all tasks endpoint"}


@router.post("/")
async def create_task():
    """Create a new task for the authenticated user."""
    return {"message": "Create task endpoint"}