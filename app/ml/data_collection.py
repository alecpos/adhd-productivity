"""Data collection module for ML features."""

from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy import select
import pandas as pd

from app.models.calendar_event_model import CalendarEventModel
from app.models.energy_model import EnergyLog
from app.models.mental_health_model import MentalHealthModel
from app.models.task_model import TaskModel


class DataCollector:
    """Data collection class for ML features."""

    def __init__(self, db: AsyncSession):
        """Initialize the data collector."""
        self.db = db

    async def get_mental_health_data(
        self,
        user_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """Get mental health data for a user."""
        query = select(MentalHealthModel).where(
            MentalHealthModel.user_id == user_id
        )
        if start_date:
            query = query.where(MentalHealthModel.created_at >= start_date)
        if end_date:
            query = query.where(MentalHealthModel.created_at <= end_date)
        result = await self.db.execute(query)
        logs = result.scalars().all()
        return [
            {
                "mood_score": log.mood_score,
                "stress_level": log.stress_level,
                "anxiety_level": log.anxiety_level,
                "energy_level": log.energy_level,
                "focus_level": log.focus_level,
                "sleep_hours": log.sleep_hours,
                "timestamp": log.created_at,
            }
            for log in logs
        ]

    async def get_energy_data(
        self,
        user_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """Get energy level data for a user."""
        query = select(EnergyLog).where(
            EnergyLog.user_id == user_id
        )
        if start_date:
            query = query.where(EnergyLog.timestamp >= start_date)
        if end_date:
            query = query.where(EnergyLog.timestamp <= end_date)
        result = await self.db.execute(query)
        logs = result.scalars().all()
        return [
            {"level": log.level.value, "timestamp": log.timestamp, "notes": log.notes}
            for log in logs
        ]

    async def get_task_data(
        self,
        user_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """Get task data for a user."""
        query = select(TaskModel).where(TaskModel.user_id == user_id)
        if start_date:
            query = query.where(TaskModel.created_at >= start_date)
        if end_date:
            query = query.where(TaskModel.created_at <= end_date)
        result = await self.db.execute(query)
        tasks = result.scalars().all()
        return [
            {
                "title": task.title,
                "priority": task.priority.value,
                "status": task.status.value,
                "estimated_duration": task.estimated_duration,
                "actual_duration": task.actual_duration,
                "energy_required": task.energy_required,
                "completion_rate": task.completion_rate,
                "created_at": task.created_at,
                "completed_at": task.completion_date if task.completed else None,
            }
            for task in tasks
        ]

    async def get_calendar_data(
        self,
        user_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """Get calendar event data for a user."""
        query = select(CalendarEventModel).where(
            CalendarEventModel.user_id == user_id
        )
        if start_date:
            query = query.where(CalendarEventModel.start_time >= start_date)
        if end_date:
            query = query.where(CalendarEventModel.end_time <= end_date)
        result = await self.db.execute(query)
        events = result.scalars().all()
        return [
            {
                "title": event.title,
                "event_type": event.event_type.value,
                "start_time": event.start_time,
                "end_time": event.end_time,
                "duration": event.duration,
                "energy_required": event.energy_required,
                "focus_required": event.focus_required,
                "completion_status": (
                    event.completion_status.value if event.completion_status else None
                ),
                "focus_score": event.focus_score,
                "energy_level": event.energy_level,
            }
            for event in events
        ]

    def prepare_features(
        self,
        mental_health_data: List[Dict[str, Any]],
        energy_data: List[Dict[str, Any]],
        task_data: List[Dict[str, Any]],
        calendar_data: List[Dict[str, Any]],
    ) -> pd.DataFrame:
        """Prepare features for ML model."""
        mh_df = pd.DataFrame(mental_health_data)
        energy_df = pd.DataFrame(energy_data)
        task_df = pd.DataFrame(task_data)
        calendar_df = pd.DataFrame(calendar_data)
        if not mh_df.empty:
            mh_df.set_index("timestamp", inplace=True)
        if not energy_df.empty:
            energy_df.set_index("timestamp", inplace=True)
        if not task_df.empty:
            task_df.set_index("created_at", inplace=True)
        if not calendar_df.empty:
            calendar_df.set_index("start_time", inplace=True)
        if not mh_df.empty:
            mh_df = mh_df.resample("h").mean()
        if not energy_df.empty:
            energy_df = energy_df.resample("h").last()
        if not task_df.empty:
            task_df = task_df.resample("h").agg(
                {
                    "estimated_duration": "sum",
                    "actual_duration": "sum",
                    "energy_required": "mean",
                    "completion_rate": "mean",
                }
            )
        if not calendar_df.empty:
            calendar_df = calendar_df.resample("h").agg(
                {
                    "duration": "sum",
                    "energy_required": "mean",
                    "focus_required": "mean",
                    "focus_score": "mean",
                    "energy_level": "mean",
                }
            )
        features = pd.concat([mh_df, energy_df, task_df, calendar_df], axis=1)
        features = features.ffill().bfill().fillna(0)
        
        return features
