"""
Notification service for handling task-related notifications and reminders.

This module implements functionality for task due date reminders and other
notification-related features as specified in the requirements.
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from ..models.task import Task
from ..models.user import User
import json
import asyncio
import logging

logger = logging.getLogger(__name__)


class NotificationService:
    """
    Service class for handling task-related notifications and reminders.

    Provides functionality for scheduling and sending task due date reminders
    and other notification-related features.
    """

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def schedule_reminders_for_task(self, task_id: str, user_id: str) -> bool:
        """
        Schedule reminders for a specific task based on its due date and notification settings.

        Args:
            task_id: The ID of the task to schedule reminders for
            user_id: The ID of the user who owns the task

        Returns:
            True if reminders were scheduled successfully, False otherwise
        """
        try:
            # Get the task by ID
            stmt = select(Task).where(and_(Task.id == task_id, Task.user_id == user_id))
            result = await self.db_session.execute(stmt)
            task = result.scalar_one_or_none()

            if not task:
                logger.warning(f"Task {task_id} not found for user {user_id}")
                return False

            # Parse notification settings
            notification_settings = json.loads(task.notification_settings or '{}')
            reminder_enabled = notification_settings.get('reminder_enabled', False)

            if not reminder_enabled:
                logger.info(f"Reminders disabled for task {task_id}")
                return True

            # Get the reminder time setting (defaults to 24 hours before due date)
            reminder_time = notification_settings.get('reminder_time', 24)  # hours before due date

            if not task.due_date:
                logger.info(f"No due date set for task {task_id}, skipping reminder scheduling")
                return True

            # Calculate the reminder time
            reminder_datetime = task.due_date - timedelta(hours=reminder_time)
            current_time = datetime.utcnow()

            # Only schedule if the reminder time is in the future
            if reminder_datetime > current_time:
                # In a real implementation, this would schedule the reminder in a job queue
                # For now, we'll log that a reminder would be scheduled
                logger.info(f"Scheduled reminder for task {task_id} at {reminder_datetime}")

                # In a real system, we would schedule this in a job queue like Celery
                # await self.schedule_job(task_id, user_id, reminder_datetime)

                return True
            else:
                logger.info(f"Reminder time for task {task_id} has already passed")
                return True

        except Exception as e:
            logger.error(f"Error scheduling reminders for task {task_id}: {str(e)}")
            return False

    async def get_notification_preferences(self, user_id: str) -> Dict[str, Any]:
        """
        Get the user's notification preferences.

        Args:
            user_id: The ID of the user

        Returns:
            Dictionary containing user's notification preferences
        """
        try:
            # In a real implementation, this would fetch from a user preferences table
            # For now, we'll return default preferences
            return {
                "email_notifications": True,
                "push_notifications": True,
                "sms_notifications": False,
                "default_reminder_hours": 24,
                "notification_timezone": "UTC"
            }
        except Exception as e:
            logger.error(f"Error getting notification preferences for user {user_id}: {str(e)}")
            return {}

    async def update_notification_preferences(self, user_id: str, preferences: Dict[str, Any]) -> bool:
        """
        Update the user's notification preferences.

        Args:
            user_id: The ID of the user
            preferences: Dictionary containing notification preferences to update

        Returns:
            True if preferences were updated successfully, False otherwise
        """
        try:
            # In a real implementation, this would update a user preferences table
            # For now, we'll just log the update
            logger.info(f"Updated notification preferences for user {user_id}: {preferences}")
            return True
        except Exception as e:
            logger.error(f"Error updating notification preferences for user {user_id}: {str(e)}")
            return False

    async def send_due_date_reminder(self, task_id: str, user_id: str) -> bool:
        """
        Send a due date reminder for a specific task.

        Args:
            task_id: The ID of the task to send reminder for
            user_id: The ID of the user who owns the task

        Returns:
            True if reminder was sent successfully, False otherwise
        """
        try:
            # Get the task and user
            task_stmt = select(Task).where(and_(Task.id == task_id, Task.user_id == user_id))
            task_result = await self.db_session.execute(task_stmt)
            task = task_result.scalar_one_or_none()

            if not task:
                logger.warning(f"Task {task_id} not found for user {user_id}")
                return False

            user_stmt = select(User).where(User.id == user_id)
            user_result = await self.db_session.execute(user_stmt)
            user = user_result.scalar_one_or_none()

            if not user:
                logger.warning(f"User {user_id} not found")
                return False

            # Parse notification settings
            notification_settings = json.loads(task.notification_settings or '{}')

            # In a real implementation, this would send actual notifications
            # via email, push notification, SMS, etc.
            logger.info(f"Sending due date reminder for task '{task.title}' to user {user.email}")

            # Example notification logic based on settings
            if notification_settings.get('email_enabled', True):
                # Send email notification
                await self.send_email_notification(user.email, task)

            if notification_settings.get('push_enabled', True):
                # Send push notification (would need device tokens in a real implementation)
                await self.send_push_notification(user_id, task)

            return True

        except Exception as e:
            logger.error(f"Error sending due date reminder for task {task_id}: {str(e)}")
            return False

    async def send_email_notification(self, email: str, task: Task) -> bool:
        """
        Send an email notification about a task.

        Args:
            email: The recipient's email address
            task: The task object

        Returns:
            True if email was sent successfully, False otherwise
        """
        try:
            # In a real implementation, this would use an email service like SMTP, SendGrid, etc.
            subject = f"Task Reminder: {task.title}"
            body = f"Your task '{task.title}' is due soon!"
            if task.due_date:
                body += f"\n\nDue date: {task.due_date.strftime('%Y-%m-%d %H:%M')}"

            if task.description:
                body += f"\n\nDescription: {task.description}"

            logger.info(f"Would send email to {email} with subject: {subject}")
            logger.info(f"Email body: {body}")

            # In a real implementation:
            # await email_service.send_email(email, subject, body)

            return True
        except Exception as e:
            logger.error(f"Error sending email notification: {str(e)}")
            return False

    async def send_push_notification(self, user_id: str, task: Task) -> bool:
        """
        Send a push notification about a task.

        Args:
            user_id: The ID of the user to notify
            task: The task object

        Returns:
            True if push notification was sent successfully, False otherwise
        """
        try:
            # In a real implementation, this would use a push notification service
            # like Firebase Cloud Messaging, Apple Push Notification Service, etc.
            message = f"Task '{task.title}' is due soon!"
            if task.due_date:
                message += f" (due: {task.due_date.strftime('%Y-%m-%d %H:%M')})"

            logger.info(f"Would send push notification to user {user_id}: {message}")

            # In a real implementation:
            # await push_service.send_push(user_id, message)

            return True
        except Exception as e:
            logger.error(f"Error sending push notification: {str(e)}")
            return False

    async def get_upcoming_reminders(self, user_id: str, hours_ahead: int = 24) -> List[Dict[str, Any]]:
        """
        Get upcoming reminders for a user within the specified time window.

        Args:
            user_id: The ID of the user
            hours_ahead: Number of hours ahead to look for reminders

        Returns:
            List of dictionaries containing upcoming reminder information
        """
        try:
            cutoff_time = datetime.utcnow() + timedelta(hours=hours_ahead)

            # Get tasks with due dates within the cutoff time that have reminders enabled
            stmt = select(Task).where(
                and_(
                    Task.user_id == user_id,
                    Task.due_date.isnot(None),
                    Task.due_date <= cutoff_time,
                    Task.deleted_at.is_(None)  # Exclude soft-deleted tasks
                )
            ).order_by(Task.due_date.asc())

            result = await self.db_session.execute(stmt)
            tasks = result.scalars().all()

            upcoming_reminders = []
            for task in tasks:
                notification_settings = json.loads(task.notification_settings or '{}')
                if notification_settings.get('reminder_enabled', False):
                    reminder_info = {
                        "task_id": str(task.id),
                        "task_title": task.title,
                        "due_date": task.due_date,
                        "reminder_time": notification_settings.get('reminder_time', 24),
                        "is_overdue": task.due_date < datetime.utcnow()
                    }
                    upcoming_reminders.append(reminder_info)

            return upcoming_reminders

        except Exception as e:
            logger.error(f"Error getting upcoming reminders for user {user_id}: {str(e)}")
            return []

    async def cleanup_old_notifications(self, days_retained: int = 30) -> int:
        """
        Clean up old notification records to free up storage.

        Args:
            days_retained: Number of days to retain notification records

        Returns:
            Number of records cleaned up
        """
        try:
            # In a real implementation, this would clean up a notifications table
            # For now, we'll just return 0 since we don't have an actual notifications table
            logger.info(f"Would clean up notification records older than {days_retained} days")
            return 0
        except Exception as e:
            logger.error(f"Error cleaning up old notifications: {str(e)}")
            return 0