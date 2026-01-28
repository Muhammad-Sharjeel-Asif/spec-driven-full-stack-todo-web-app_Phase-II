from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.models.task import Task, TaskCreate, TaskUpdate
from src.schemas.task import TaskRead
from src.models.user import User


class TaskService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_task(self, task_create: TaskCreate, current_user: User) -> TaskRead:
        """Create a new task for the current user"""
        # Set the user_id to the current user's ID
        task_data = task_create.model_dump()
        task_data['user_id'] = current_user.id
        task = Task(**task_data)
        self.db_session.add(task)
        await self.db_session.commit()
        await self.db_session.refresh(task)

        # Convert to TaskRead format
        return TaskRead.model_validate(task)

    async def get_task_by_id(self, task_id: str, current_user: User) -> Optional[Task]:
        """Get a task by ID for the current user"""
        stmt = select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
        result = await self.db_session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_task(self, task_id: str, task_update: TaskUpdate, current_user: User) -> Optional[Task]:
        """Update a task for the current user"""
        task = await self.get_task_by_id(task_id, current_user)
        if not task:
            return None

        update_data = task_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(task, field, value)

        self.db_session.add(task)
        await self.db_session.commit()
        await self.db_session.refresh(task)
        return task

    async def delete_task(self, task_id: str, current_user: User) -> bool:
        """Delete a task for the current user"""
        task = await self.get_task_by_id(task_id, current_user)
        if not task:
            return False

        await self.db_session.delete(task)
        await self.db_session.commit()
        return True

    async def get_tasks(self, skip: int = 0, limit: int = 100, current_user: User = None) -> List[Task]:
        """Get tasks for the current user with pagination"""
        if current_user is None:
            # If no user is provided, return empty list (or could raise an exception)
            return []

        stmt = select(Task).where(Task.user_id == current_user.id).offset(skip).limit(limit)
        result = await self.db_session.execute(stmt)
        return result.scalars().all()
