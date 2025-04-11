"""Voice command service module."""

import logging
from datetime import datetime
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.task_schema import Task

logger = logging.getLogger(__name__)


class VoiceCommandService:
    """Service to handle voice command processing and task creation."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def parse_command(self, command_text: str) -> Dict[str, Any]:
        """
        Parse a voice command into structured data.

        Args:
            command_text: The text of the voice command

        Returns:
            Dict containing parsed command data
        """
        command_text = command_text.lower()
        if "remind" in command_text:
            return {
                "command_type": "create_reminder",
                "title": command_text,
                "reminder_time": datetime.now(),
            }
        else:
            return {
                "command_type": "create_task",
                "title": command_text,
                "due_date": datetime.now(),
                "priority": 1,
            }

    async def create_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a task from parsed command data."""
        try:
            task = Task(
                title=task_data["title"],
                due_date=task_data.get("due_date"),
                priority=task_data.get("priority", 1),
                user_id=task_data.get("user_id"),
            )
            self.db.add(task)
            await self.db.commit()
            await self.db.refresh(task)
            return {"success": True, "message": "Task created successfully", "task": task}
        except Exception as e:
            logger.error(f"Error creating task: {str(e)}")
            return {"success": False, "message": f"Error creating task: {str(e)}"}

    async def create_reminder(self, reminder_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a reminder from parsed command data."""
        try:
            reminder = Task(
                title=reminder_data["title"],
                due_date=reminder_data.get("reminder_time"),
                priority=reminder_data.get("priority", 1),
                user_id=reminder_data.get("user_id"),
                is_reminder=True,
            )
            self.db.add(reminder)
            await self.db.commit()
            await self.db.refresh(reminder)
            return {
                "success": True,
                "message": "Reminder created successfully",
                "reminder": reminder,
            }
        except Exception as e:
            logger.error(f"Error creating reminder: {str(e)}")
            return {"success": False, "message": f"Error creating reminder: {str(e)}"}
