"""Energy service."""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import select

from app.services.base_service import BaseService
from app.models.energy_model import EnergyLog
from app.schemas.energy_schema import (
    EnergyPatternsSchema,
    EnergyLogResponseSchema,
    EnergyLogCreateSchema,
)

logger = logging.getLogger(__name__)


class EnergyService(BaseService[EnergyLog, EnergyLogResponseSchema, EnergyLogCreateSchema]):
    """Service for managing energy levels."""

    def __init__(self, db):
        """Initialize the service with the EnergyLog model."""
        super().__init__(db=db, model=EnergyLog, schema=EnergyLogResponseSchema)

    async def create_energy_level(
        self,
        user_id: UUID,
        level: int,
        notes: Optional[str] = None,
        meta_data: Optional[Dict[str, Any]] = None,
    ) -> EnergyLog:
        """Create a new energy level entry."""
        energy_data = {
            "user_id": user_id,
            "level": level,
            "notes": notes,
            "meta_data": meta_data,
        }
        return await self.create(energy_data)

    async def get_user_energy_levels(
        self,
        user_id: UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[EnergyLog]:
        """Get energy levels for a user within a date range."""
        filters = {"user_id": user_id}
        if start_date:
            filters["timestamp__gte"] = start_date
        if end_date:
            filters["timestamp__lte"] = end_date
        return await self.get_many(filters=filters)

    async def get_energy_stats(
        self,
        user_id: UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Get energy statistics for a user within a date range."""
        levels = await self.get_user_energy_levels(user_id, start_date, end_date)
        if not levels:
            return {
                "average_level": 0,
                "peak_hours": [],
                "low_energy_periods": [],
                "total_entries": 0,
            }
        total_levels = len(levels)
        level_sum = sum((level.level for level in levels))
        hour_levels = {}
        for level in levels:
            hour = level.timestamp.hour
            if hour not in hour_levels:
                hour_levels[hour] = []
            hour_levels[hour].append(level.level)
        hour_averages = {hour: sum(levels) / len(levels) for hour, levels in hour_levels.items()}
        peak_threshold = 7
        low_threshold = 4
        peak_hours = [hour for hour, avg in hour_averages.items() if avg >= peak_threshold]
        low_energy_periods = [hour for hour, avg in hour_averages.items() if avg <= low_threshold]
        return {
            "average_level": round(level_sum / total_levels, 2),
            "peak_hours": sorted(peak_hours),
            "low_energy_periods": sorted(low_energy_periods),
            "total_entries": total_levels,
        }

    async def log_energy_level(
        self,
        user_id: UUID,
        energy_level: int,
        activity: str,
        notes: str = None,
        timestamp: datetime = None,
    ) -> EnergyLog:
        """Log an energy level for a user."""
        logger.info(f"Creating energy log for user {user_id}")
        try:
            energy_log = EnergyLog(
                user_id=user_id,
                energy_level=energy_level,
                activity=activity,
                notes=notes,
                timestamp=timestamp or datetime.utcnow(),
            )
            self.db.add(energy_log)
            await self.db.commit()
            await self.db.refresh(energy_log)
            logger.info(f"Successfully created energy log {energy_log.id}")
            return energy_log
        except Exception as e:
            logger.error(f"Error creating energy log: {str(e)}")
            await self.db.rollback()
            raise

    async def get_user_logs(self, user_id: UUID) -> List[EnergyLog]:
        """Get all energy logs for a user."""
        logger.info(f"Fetching energy logs for user {user_id}")
        try:
            query = (
                select(EnergyLog)
                .where(EnergyLog.user_id == user_id)
                .order_by(EnergyLog.created_at.desc())
            )
            result = await self.db.execute(query)
            logs = result.scalars().all()
            logger.info(f"Retrieved {len(logs)} energy logs for user {user_id}")
            return logs
        except Exception as e:
            logger.error(f"Error fetching energy logs: {str(e)}")
            raise

    async def get_energy_patterns(self, user_id: UUID) -> EnergyPatternsSchema:
        """Get energy patterns for a user."""
        logger.info(f"Analyzing energy patterns for user {user_id}")
        try:
            logs = await self.get_user_logs(user_id)
            daily_patterns = []
            time_slots = ["Morning", "Afternoon", "Evening", "Night"]
            for slot in time_slots:
                slot_logs = [log for log in logs if self._get_time_slot(log.created_at) == slot]
                if slot_logs:
                    avg_energy = sum((log.energy_level for log in slot_logs)) / len(slot_logs)
                    activities = list(set((log.activity for log in slot_logs)))
                    recommendations = self._generate_recommendations(avg_energy, activities)
                    daily_patterns.append({
                        "time_of_day": slot,
                        "average_energy": avg_energy,
                        "common_activities": activities[:5],
                        "recommendations": recommendations,
                    })
            weekly_patterns = []
            days = [
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
                "Sunday",
            ]
            for day in days:
                day_logs = [log for log in logs if log.created_at.strftime("%A") == day]
                if day_logs:
                    avg_energy = sum((log.energy_level for log in day_logs)) / len(day_logs)
                    activities = list(set((log.activity for log in day_logs)))
                    recommendations = self._generate_recommendations(avg_energy, activities)
                    weekly_patterns.append({
                        "time_of_day": day,
                        "average_energy": avg_energy,
                        "common_activities": activities[:5],
                        "recommendations": recommendations,
                    })
            peak_times = [
                pattern["time_of_day"] for pattern in daily_patterns if pattern["average_energy"] >= 7
            ]
            low_times = [
                pattern["time_of_day"] for pattern in daily_patterns if pattern["average_energy"] <= 4
            ]
            activity_correlations = self._calculate_activity_correlations(logs)
            logger.info(f"Successfully analyzed energy patterns for user {user_id}")
            return EnergyPatternsSchema(
                patterns={
                    "daily": daily_patterns,
                    "weekly": weekly_patterns,
                },
                analytics={
                    "peak_times": peak_times,
                    "low_times": low_times,
                    "activity_correlations": activity_correlations,
                },
                meta_data=None
            )
        except Exception as e:
            logger.error(f"Error analyzing energy patterns: {str(e)}")
            raise

    def _get_time_slot(self, timestamp: datetime) -> str:
        """Get the time slot for a timestamp."""
        hour = timestamp.hour
        if 5 <= hour < 12:
            return "Morning"
        elif 12 <= hour < 17:
            return "Afternoon"
        elif 17 <= hour < 22:
            return "Evening"
        else:
            return "Night"

    def _generate_recommendations(self, energy_level: float, activities: List[str]) -> List[str]:
        """Generate recommendations based on energy level and activities."""
        recommendations = []
        if energy_level >= 7:
            recommendations.extend([
                "This is a high energy period - great for challenging tasks",
                "Schedule important meetings or deep work during this time",
                "Take advantage of focus for complex problem-solving",
            ])
        elif 4 <= energy_level < 7:
            recommendations.extend([
                "Moderate energy level - good for routine tasks",
                "Balance between active work and breaks",
                "Consider collaborative activities",
            ])
        else:
            recommendations.extend([
                "Low energy period - focus on lighter tasks",
                "Take regular breaks and avoid demanding activities",
                "Consider scheduling rest or recovery time",
            ])
        return recommendations

    def _calculate_activity_correlations(self, logs: List[EnergyLog]) -> Dict[str, float]:
        """Calculate correlations between activities and energy levels."""
        correlations = {}
        for log in logs:
            if log.activity and log.activity not in correlations:
                activity_logs = [l for l in logs if l.activity == log.activity]
                avg_energy = sum((l.energy_level for l in activity_logs)) / len(activity_logs)
                correlations[log.activity] = round(avg_energy, 2)
        return dict(sorted(correlations.items(), key=lambda x: x[1], reverse=True)[:10])
