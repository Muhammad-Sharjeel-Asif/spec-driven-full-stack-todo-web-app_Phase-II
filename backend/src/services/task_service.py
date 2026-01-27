from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.models.task import Task, TaskCreate, TaskUpdate
from src.schemas.task import TaskRead


class TaskService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_task(self, task_create: TaskCreate) -> TaskRead:
        """Create a new task"""
        task = Task(**task_create.dict())
        self.db_session.add(task)
        await self.db_session.commit()
        await self.db_session.refresh(task)
        
        # Convert to TaskRead format
        return TaskRead.from_orm(task) if hasattr(TaskRead, 'from_orm') else TaskRead(**task.__dict__)

    async def get_task_by_id(self, task_id: str) -> Optional[Task]:
        """Get a task by ID"""
        stmt = select(Task).where(Task.id == task_id)
        result = await self.db_session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_task(self, task_id: str, task_update: TaskUpdate) -> Optional[Task]:
        """Update a task"""
        task = await self.get_task_by_id(task_id)
        if not task:
            return None
        
        update_data = task_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(task, field, value)
        
        self.db_session.add(task)
        await self.db_session.commit()
        await self.db_session.refresh(task)
        return task

    async def delete_task(self, task_id: str) -> bool:
        """Delete a task"""
        task = await self.get_task_by_id(task_id)
        if not task:
            return False
        
        await self.db_session.delete(task)
        await self.db_session.commit()
        return True

    async def get_tasks(self, skip: int = 0, limit: int = 100) -> List[Task]:
        """Get all tasks with pagination"""
        stmt = select(Task).offset(skip).limit(limit)
        result = await self.db_session.execute(stmt)
        return result.scalars().all()
