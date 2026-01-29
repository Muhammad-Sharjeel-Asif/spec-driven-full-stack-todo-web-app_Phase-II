from datetime import datetime
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from src.models.task import Task, TaskCreate, TaskUpdate
from src.models.user import User
from .notification_service import NotificationService


class TaskService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_task(self, task_create: TaskCreate, current_user: User):
        """Create a new task for the current user"""
        # Set the user_id to the current user's ID
        task_data = task_create.model_dump()
        task_data['user_id'] = current_user.id
        task = Task(**task_data)
        self.db_session.add(task)
        await self.db_session.commit()
        await self.db_session.refresh(task)

        # Convert to TaskRead format using model_validate
        from src.schemas.task import TaskRead

        # Schedule notifications if notification settings are enabled
        try:
            notification_service = NotificationService(self.db_session)
            await notification_service.schedule_reminders_for_task(str(task.id), str(task.user_id))
        except Exception as e:
            # If notification scheduling fails, still return the task
            # Notifications are not critical for task creation
            import logging
            logging.warning(f"Failed to schedule notifications for task {task.id}: {str(e)}")

        return TaskRead.model_validate(task)

    async def get_task_by_id(self, task_id: str, current_user: User):
        """Get a task by ID for the current user (excludes soft-deleted tasks)"""
        from sqlalchemy import and_
        stmt = select(Task).where(
            and_(Task.id == task_id, Task.user_id == current_user.id, Task.deleted_at.is_(None))
        )
        result = await self.db_session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_task(self, task_id: str, task_update: TaskUpdate, current_user: User):
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

        # Reschedule notifications if due date or notification settings changed
        try:
            notification_service = NotificationService(self.db_session)
            await notification_service.schedule_reminders_for_task(str(task.id), str(task.user_id))
        except Exception as e:
            # If notification scheduling fails, still return the task
            # Notifications are not critical for task updates
            import logging
            logging.warning(f"Failed to reschedule notifications for task {task.id}: {str(e)}")

        from src.schemas.task import TaskRead
        return TaskRead.model_validate(task)

    async def delete_task(self, task_id: str, current_user: User) -> bool:
        """Soft delete a task for the current user with 30-day retention"""
        task = await self.get_task_by_id(task_id, current_user)
        if not task:
            return False

        # Instead of hard deleting, set the deleted_at timestamp
        from datetime import datetime
        task.deleted_at = datetime.utcnow()
        await self.db_session.commit()
        await self.db_session.refresh(task)
        return True

    async def hard_delete_task(self, task_id: str, current_user: User) -> bool:
        """Hard delete a task for the current user (permanent deletion)"""
        task = await self.get_task_by_id(task_id, current_user)
        if not task:
            return False

        self.db_session.delete(task)
        await self.db_session.commit()
        return True

    async def get_deleted_tasks(self, skip: int = 0, limit: int = 100, current_user: User = None) -> List:
        """Get soft-deleted tasks for the current user with pagination"""
        if current_user is None:
            return []

        from sqlalchemy import and_
        stmt = select(Task).where(
            and_(Task.user_id == current_user.id, Task.deleted_at.isnot(None))
        ).offset(skip).limit(limit)

        result = await self.db_session.execute(stmt)
        tasks = result.scalars().all()

        # Convert to TaskRead format
        from src.schemas.task import TaskRead
        return [TaskRead.model_validate(task) for task in tasks]

    async def restore_task(self, task_id: str, current_user: User):
        """Restore a soft-deleted task for the current user"""
        from sqlalchemy import and_
        stmt = select(Task).where(
            and_(Task.id == task_id, Task.user_id == current_user.id, Task.deleted_at.isnot(None))
        )
        result = await self.db_session.execute(stmt)
        task = result.scalar_one_or_none()

        if not task:
            return None

        # Clear the deleted_at timestamp to restore the task
        task.deleted_at = None
        await self.db_session.commit()
        await self.db_session.refresh(task)

        from src.schemas.task import TaskRead
        return TaskRead.model_validate(task)

    async def cleanup_soft_deleted_tasks(self, days_retained: int = 30) -> int:
        """Clean up soft-deleted tasks older than the retention period"""
        from datetime import datetime, timedelta
        from sqlalchemy import and_

        cutoff_date = datetime.utcnow() - timedelta(days=days_retained)

        # Find soft-deleted tasks older than the retention period
        stmt = select(Task).where(
            and_(Task.deleted_at.isnot(None), Task.deleted_at < cutoff_date)
        )
        result = await self.db_session.execute(stmt)
        tasks_to_purge = result.scalars().all()

        # Hard delete these tasks
        purged_count = 0
        for task in tasks_to_purge:
            await self.db_session.delete(task)
            purged_count += 1

        await self.db_session.commit()
        return purged_count

    async def toggle_task_completion(self, task_id: str, current_user: User):
        """Toggle the completion status of a task for the current user"""
        task = await self.get_task_by_id(task_id, current_user)
        if not task:
            return None

        # Toggle the completion status
        task.is_completed = not task.is_completed
        await self.db_session.commit()
        await self.db_session.refresh(task)
        from src.schemas.task import TaskRead
        return TaskRead.model_validate(task)

    async def get_tasks(self, skip: int = 0, limit: int = 100, current_user: User = None,
                       status: Optional[str] = None, priority: Optional[str] = None,
                       due_date_from: Optional[datetime] = None, due_date_to: Optional[datetime] = None) -> List:
        """Get active tasks for the current user with pagination and filtering (excludes soft-deleted tasks)"""
        if current_user is None:
            # If no user is provided, return empty list (or could raise an exception)
            return []

        # Only return tasks that have not been soft-deleted
        from sqlalchemy import and_, or_

        # Build the query with all filters
        query_filters = [
            Task.user_id == current_user.id,
            Task.deleted_at.is_(None)
        ]

        # Add status filter
        if status:
            if status == "completed":
                query_filters.append(Task.is_completed == True)
            elif status == "pending":
                query_filters.append(Task.is_completed == False)
            elif status != "all":
                query_filters.append(Task.is_completed.in_([True, False]))  # Any status

        # Add priority filter
        if priority:
            priority_map = {"low": 1, "medium": 2, "high": 3}
            if priority in priority_map:
                query_filters.append(Task.priority == priority_map[priority])

        # Add due date filters
        if due_date_from:
            query_filters.append(Task.due_date >= due_date_from)
        if due_date_to:
            query_filters.append(Task.due_date <= due_date_to)

        # Construct the query with all filters
        stmt = select(Task).where(and_(*query_filters)).offset(skip).limit(limit)

        result = await self.db_session.execute(stmt)
        tasks = result.scalars().all()

        # Convert to TaskRead format
        from src.schemas.task import TaskRead
        return [TaskRead.model_validate(task) for task in tasks]

    async def get_tasks_count(self, current_user: User = None,
                             status: Optional[str] = None, priority: Optional[str] = None,
                             due_date_from: Optional[datetime] = None, due_date_to: Optional[datetime] = None) -> int:
        """Get the total count of tasks for the current user with optional filtering"""
        if current_user is None:
            return 0

        from sqlalchemy import and_, func

        # Build the query with all filters
        query_filters = [
            Task.user_id == current_user.id,
            Task.deleted_at.is_(None)
        ]

        # Add status filter
        if status:
            if status == "completed":
                query_filters.append(Task.is_completed == True)
            elif status == "pending":
                query_filters.append(Task.is_completed == False)
            elif status != "all":
                query_filters.append(Task.is_completed.in_([True, False]))

        # Add priority filter
        if priority:
            priority_map = {"low": 1, "medium": 2, "high": 3}
            if priority in priority_map:
                query_filters.append(Task.priority == priority_map[priority])

        # Add due date filters
        if due_date_from:
            query_filters.append(Task.due_date >= due_date_from)
        if due_date_to:
            query_filters.append(Task.due_date <= due_date_to)

        # Construct the count query
        stmt = select(func.count(Task.id)).where(and_(*query_filters))

        result = await self.db_session.execute(stmt)
        count = result.scalar_one()

        return count