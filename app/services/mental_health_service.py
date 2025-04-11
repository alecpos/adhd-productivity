"""Mental health service."""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Type
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.database import get_db
from app.services.base_service import BaseService
from app.models.mental_health_model import MentalHealthLogModel
from app.schemas.mental_health_schema import (
    MentalHealthLogResponseSchema,
    MentalHealthLogCreateSchema,
)
from app.utils.metrics import ServiceMetrics

logger = logging.getLogger(__name__)
service_metrics = ServiceMetrics("mental_health_service")


class MentalHealthService(
    BaseService[MentalHealthLogModel, MentalHealthLogResponseSchema, MentalHealthLogCreateSchema]
):
    """Service for managing mental health logs."""

    def __init__(self, db: AsyncSession):
        """Initialize the service with the MentalHealthLogModelSchema model."""
        super().__init__(db=db, model=MentalHealthLogModel, schema=MentalHealthLogResponseSchema)
        self.metrics = service_metrics

    async def create_log(
        self,
        user_id: UUID,
        mood_score: int,
        stress_level: int,
        anxiety_level: int,
        energy_level: Optional[int] = None,
        focus_level: Optional[int] = None,
        sleep_hours: Optional[float] = None,
        sleep_quality: Optional[int] = None,
        notes: Optional[str] = None,
        activities: Optional[List[str]] = None,
        activity_log: Optional[List[str]] = None,
        triggers: Optional[List[str]] = None,
        coping_strategies: Optional[List[str]] = None,
        timestamp: Optional[datetime] = None,
        meta_data: Optional[Dict[str, Any]] = None,
    ) -> MentalHealthLogModel:
        """Create a new mental health log."""
        try:
            if hasattr(user_id, "id"):
                user_id = user_id.id
            elif not isinstance(user_id, UUID):
                try:
                    user_id = UUID(str(user_id))
                except ValueError as e:
                    logger.error(f"Invalid user_id: {user_id}. Error: {e}", exc_info=True)
                    raise ValueError(f"Invalid user_id: {user_id}")
            log_data = {
                "user_id": user_id,
                "mood_score": int(mood_score),
                "stress_level": int(stress_level),
                "anxiety_level": int(anxiety_level),
                "energy_level": int(energy_level) if energy_level is not None else None,
                "focus_level": int(focus_level) if focus_level is not None else None,
                "sleep_hours": float(sleep_hours) if sleep_hours is not None else None,
                "sleep_quality": int(sleep_quality) if sleep_quality is not None else None,
                "notes": str(notes) if notes else "",
                "activities": list(activities) if activities else [],
                "activity_log": list(activity_log) if activity_log else [],
                "triggers": list(triggers) if triggers else [],
                "coping_strategies": list(coping_strategies) if coping_strategies else [],
                "timestamp": timestamp if timestamp else datetime.now(),
                "meta_data": dict(meta_data) if meta_data else {},
            }
            logger.debug(f"Creating mental health log with data: {log_data}")
            return await self.create(log_data)
        except Exception as e:
            logger.error(f"Error creating mental health log: {str(e)}", exc_info=True)

    async def get_user_logs(
        self,
        user_id: UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[MentalHealthLogModel]:
        """Get mental health logs for a user within a date range."""
        filters = {"user_id": user_id}
        if start_date:
            filters["timestamp__gte"] = start_date
        if end_date:
            filters["timestamp__lte"] = end_date
        return await self.get_many(filters=filters)

    async def get_user_stats(
        self,
        user_id: UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Get mental health statistics for a user within a date range."""
        logs = await self.get_user_logs(user_id, start_date, end_date)
        if not logs:
            return {
                "mood_average": 0,
                "stress_level_average": 0,
                "anxiety_level_average": 0,
                "energy_level_average": 0,
                "focus_level_average": 0,
                "sleep_hours_average": 0,
                "sleep_quality_average": 0,
                "total_logs": 0,
                "recent_moods": [],
                "streak": 0,
                "most_common_activities": [],
                "most_common_triggers": [],
                "most_common_coping_strategies": [],
                "updated_at": datetime.now(),
            }
        total_logs = len(logs)
        mood_sum = sum((log.mood_score for log in logs))
        stress_sum = sum((log.stress_level for log in logs))
        anxiety_sum = sum((log.anxiety_level for log in logs))
        energy_sum = sum((log.energy_level or 0 for log in logs))
        focus_sum = sum((log.focus_level or 0 for log in logs))
        sleep_hours_sum = sum((log.sleep_hours or 0 for log in logs))
        sleep_quality_sum = sum((log.sleep_quality or 0 for log in logs))
        recent_moods = [
            {"date": log.timestamp, "mood": log.mood_score, "notes": log.notes}
            for log in sorted(logs, key=lambda x: x.timestamp, reverse=True)[:7]
        ]
        sorted_logs = sorted(logs, key=lambda x: x.timestamp)
        streak = 1
        for i in range(1, len(sorted_logs)):
            if (sorted_logs[i].timestamp - sorted_logs[i - 1].timestamp).days <= 1:
                streak += 1
            else:
                break
        all_activities = []
        all_triggers = []
        all_coping_strategies = []
        for log in logs:
            if log.activities:
                all_activities.extend(log.activities)
            if log.activity_log:
                all_activities.extend(log.activity_log)
            if log.triggers:
                all_triggers.extend(log.triggers)
            if log.coping_strategies:
                all_coping_strategies.extend(log.coping_strategies)
        activity_counts = {}
        for activity in all_activities:
            activity_counts[activity] = activity_counts.get(activity, 0) + 1
        most_common_activities = sorted(activity_counts.items(), key=lambda x: x[1], reverse=True)[
            :5
        ]
        trigger_counts = {}
        for trigger in all_triggers:
            trigger_counts[trigger] = trigger_counts.get(trigger, 0) + 1
        most_common_triggers = sorted(trigger_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        strategy_counts = {}
        for strategy in all_coping_strategies:
            strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1
        most_common_strategies = sorted(strategy_counts.items(), key=lambda x: x[1], reverse=True)[
            :5
        ]
        return {
            "mood_average": round(mood_sum / total_logs, 2),
            "stress_level_average": round(stress_sum / total_logs, 2),
            "anxiety_level_average": round(anxiety_sum / total_logs, 2),
            "energy_level_average": round(energy_sum / total_logs, 2),
            "focus_level_average": round(focus_sum / total_logs, 2),
            "sleep_hours_average": round(sleep_hours_sum / total_logs, 2),
            "sleep_quality_average": round(sleep_quality_sum / total_logs, 2),
            "total_logs": total_logs,
            "recent_moods": recent_moods,
            "streak": streak,
            "most_common_activities": [activity for activity, _ in most_common_activities],
            "most_common_triggers": [trigger for trigger, _ in most_common_triggers],
            "most_common_coping_strategies": [strategy for strategy, _ in most_common_strategies],
            "updated_at": datetime.now(),
        }

    async def get_user_trends(
        self,
        user_id: UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Get mental health trends for a user within a date range."""
        logs = await self.get_user_logs(user_id, start_date, end_date)
        if not logs:
            return {
                "mood_trends": [],
                "stress_trends": [],
                "anxiety_trends": [],
                "energy_trends": [],
                "focus_trends": [],
                "sleep_hours_trends": [],
                "sleep_quality_trends": [],
                "period_start": start_date or datetime.now(),
                "period_end": end_date or datetime.now(),
                "updated_at": datetime.now(),
            }
        logs.sort(key=lambda x: x.timestamp)
        trends = {
            "mood_trends": [{"date": log.timestamp, "value": log.mood_score} for log in logs],
            "stress_trends": [{"date": log.timestamp, "value": log.stress_level} for log in logs],
            "anxiety_trends": [{"date": log.timestamp, "value": log.anxiety_level} for log in logs],
            "energy_trends": [
                {"date": log.timestamp, "value": log.energy_level or 0} for log in logs
            ],
            "focus_trends": [
                {"date": log.timestamp, "value": log.focus_level or 0} for log in logs
            ],
            "sleep_hours_trends": [
                {"date": log.timestamp, "value": log.sleep_hours or 0} for log in logs
            ],
            "sleep_quality_trends": [
                {"date": log.timestamp, "value": log.sleep_quality or 0} for log in logs
            ],
            "period_start": logs[0].timestamp,
            "period_end": logs[-1].timestamp,
            "updated_at": datetime.now(),
        }


def get_mental_health_service(db: AsyncSession = Depends(get_db)) -> MentalHealthService:
    """Get an instance of the mental health service."""
    return MentalHealthService(db)
