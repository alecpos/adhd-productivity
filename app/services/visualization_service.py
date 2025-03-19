"""Visualization service module."""

from typing import List, Dict

from app.models.task_model import TaskModel
from app.schemas.task_schema import TaskResponse


class VisualizationService:
    """Service for generating visualizations."""

    @staticmethod
    def generate_task_timeline(tasks: List[TaskModel]) -> List[Dict]:
        """
        Generate a timeline for tasks with titles and due dates.
        """
        return [
            {"title": task.title, "due_date": task.due_date.strftime("%Y-%m-%d %H:%M")}
            for task in sorted(tasks, key=lambda x: x.due_date)
        ]

    @staticmethod
    def generate_subscription_timeline(subscriptions: List[Dict]) -> List[Dict]:
        """
        Generate a timeline for subscription payment dates.
        """
        return [
            {"name": sub["name"], "due_date": sub["due_date"].strftime("%Y-%m-%d")}
            for sub in sorted(subscriptions, key=lambda x: x["due_date"])
        ]
