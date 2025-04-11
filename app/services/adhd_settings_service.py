"""ADHD settings service module."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.schemas.user_schema import User, UserSchema
from app.schemas.adhd_settings_schema import (
    ADHDSettings,
    ADHDSettingsCreate,
    ADHDSettingsUpdate,
    DistractionLogCreate,
    DistractionLogResponse,
    MedicationLogCreate,
    MedicationLogResponse,
    ADHDMetricsResponse,
    ADHDRecommendationsResponse,
    ADHDPatternsResponse,
    ADHDDailyPlanResponse,
)


class ADHDSettingsService:
    """Service for managing ADHD settings."""

    def __init__(self, db: AsyncSession):
        """Initialize the service with a database session."""
        self.db = db

    async def get_settings(self, user_id: UUID) -> Optional[ADHDSettings]:
        """Get ADHD settings for a user."""
        query = select(ADHDSettings).where(ADHDSettings.user_id == user_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_settings(
        self, user_id: UUID, settings_data: ADHDSettingsCreate
    ) -> Optional[ADHDSettings]:
        """Create ADHD settings for a user."""
        existing_settings = await self.get_settings(user_id)
        if existing_settings:
            raise ValueError("ADHD settings already exist for this user")
        settings = ADHDSettings(user_id=user_id, **settings_data.model_dump())
        self.db.add(settings)
        await self.db.flush()
        return settings

    async def update_settings(
        self, user_id: UUID, settings_data: ADHDSettingsUpdate
    ) -> Optional[ADHDSettings]:
        """Update ADHD settings for a user."""
        settings = await self.get_settings(user_id)
        if not settings:
            return None
        update_data = settings_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(settings, field, value)
        settings.updated_at = datetime.now()
        await self.db.flush()
        return settings

    async def delete_settings(self, user_id: UUID) -> bool:
        """Delete ADHD settings for a user."""
        db_settings = await self.get_settings(user_id)
        if not db_settings:
            return False
        await self.db.delete(db_settings)
        await self.db.flush()
        return True

    async def log_distraction(
        self, user_id: UUID, distraction_data: DistractionLogCreate
    ) -> Optional[DistractionLogResponse]:
        """Log a distraction for a user."""
        if not 0 <= distraction_data.impact <= 10:
            raise ValueError("Impact must be between 0 and 10")
        settings = await self.get_settings(user_id)
        if not settings:
            return None
        log_entry = {
            "id": str(uuid4()),
            "timestamp": datetime.now().isoformat(),
            "type": distraction_data.type,
            "duration": distraction_data.duration,
            "impact": distraction_data.impact,
            "user_id": str(user_id),
        }
        if not settings.distraction_logs:
            settings.distraction_logs = []
        settings.distraction_logs.append(log_entry)
        settings.updated_at = datetime.now()
        await self.db.flush()
        return DistractionLogResponse(**log_entry)

    async def log_medication(
        self, user_id: UUID, medication_data: MedicationLogCreate
    ) -> Optional[MedicationLogResponse]:
        """Log a medication for a user."""
        if not 0 <= medication_data.effectiveness <= 1:
            raise ValueError("Effectiveness must be between 0 and 1")
        settings = await self.get_settings(user_id)
        if not settings:
            return None
        log_entry = {
            "id": str(uuid4()),
            "timestamp": datetime.now().isoformat(),
            "effectiveness": medication_data.effectiveness,
            "side_effects": medication_data.side_effects,
            "user_id": str(user_id),
        }
        if not settings.medication_logs:
            settings.medication_logs = []
        settings.medication_logs.append(log_entry)
        settings.updated_at = datetime.now()
        await self.db.flush()
        return MedicationLogResponse(**log_entry)

    async def get_metrics(
        self, user_id: UUID, start_date: datetime, end_date: datetime
    ) -> Optional[ADHDMetricsResponse]:
        """Get ADHD-related metrics for a user."""
        if start_date >= end_date:
            raise ValueError("Start date must be before end date")
        current_time = datetime.utcnow()
        if start_date > current_time or end_date > current_time:
            raise ValueError("Date range cannot be in the future")
        settings = await self.get_settings(user_id)
        if not settings:
            return None
        distraction_logs = (
            [
                log
                for log in settings.distraction_logs
                if start_date <= datetime.fromisoformat(log["timestamp"]) <= end_date
            ]
            if settings.distraction_logs
            else []
        )
        medication_logs = (
            [
                log
                for log in settings.medication_logs
                if start_date <= datetime.fromisoformat(log["timestamp"]) <= end_date
            ]
            if settings.medication_logs
            else []
        )
        daily_focus_scores = {}
        for log in distraction_logs:
            date = datetime.fromisoformat(log["timestamp"]).date().isoformat()
            if date not in daily_focus_scores:
                daily_focus_scores[date] = 10
            daily_focus_scores[date] -= log["impact"] * 0.1
        avg_effectiveness = (
            sum((log["effectiveness"] for log in medication_logs)) / len(medication_logs)
            if medication_logs
            else 0.0
        )
        return ADHDMetricsResponse(
            focus_scores={
                "daily": daily_focus_scores,
                "weekly": (
                    sum(daily_focus_scores.values()) / len(daily_focus_scores)
                    if daily_focus_scores
                    else 0.0
                ),
                "monthly": 0.0,
            },
            task_completion={"onTime": 0.8, "late": 0.15, "incomplete": 0.05},
            medication_effectiveness=avg_effectiveness,
            productive_hours=["09:00-11:00", "14:00-16:00"],
            distraction_patterns=[
                {
                    "type": "noise",
                    "frequency": len([log for log in distraction_logs if log["type"] == "noise"]),
                },
                {
                    "type": "visual",
                    "frequency": len([log for log in distraction_logs if log["type"] == "visual"]),
                },
                {
                    "type": "internal",
                    "frequency": len(
                        [log for log in distraction_logs if log["type"] == "internal"]
                    ),
                },
            ],
        )

    async def get_recommendations(self, user_id: UUID) -> Optional[ADHDRecommendationsResponse]:
        """Get personalized ADHD recommendations."""
        settings = await self.get_settings(user_id)
        if not settings:
            return None
        return ADHDRecommendationsResponse(
            scheduling=[
                "Schedule important tasks during peak energy hours",
                "Take regular breaks every 45 minutes",
                "Use time-blocking for focused work",
            ],
            environment=[
                "Minimize visual distractions in workspace",
                "Use noise-canceling headphones during focused work",
                "Maintain consistent lighting conditions",
            ],
            strategies=[
                "Break large tasks into smaller, manageable chunks",
                "Use visual aids and checklists",
                "Set reminders for task transitions",
            ],
            accommodations=[
                "Request deadline extensions when needed",
                "Use text-to-speech for reading comprehension",
                "Work in a quiet environment",
            ],
        )

    async def get_patterns(self, user_id: UUID) -> Optional[ADHDPatternsResponse]:
        """Get ADHD behavior patterns analysis."""
        settings = await self.get_settings(user_id)
        if not settings:
            return None
        return ADHDPatternsResponse(
            productivity=[
                {"time": "morning", "level": "high"},
                {"time": "afternoon", "level": "medium"},
                {"time": "evening", "level": "low"},
            ],
            distractions=[
                {"type": "noise", "frequency": "high", "impact": "medium"},
                {"type": "visual", "frequency": "medium", "impact": "high"},
                {"type": "internal", "frequency": "high", "impact": "high"},
            ],
            success_factors=[
                "Regular medication schedule",
                "Structured environment",
                "Clear task prioritization",
            ],
        )

    async def generate_daily_plan(self, user_id: UUID) -> Optional[ADHDDailyPlanResponse]:
        """Generate an ADHD-optimized daily plan."""
        settings = await self.get_settings(user_id)
        if not settings:
            return None
        return ADHDDailyPlanResponse(
            medication_timing=settings.medication_schedule["times"],
            break_schedule=["10:30", "12:00", "14:30", "16:00"],
            focus_blocks=[
                {"start": "09:00", "end": "10:30", "task_type": "high_priority"},
                {"start": "11:00", "end": "12:00", "task_type": "medium_priority"},
                {"start": "14:00", "end": "15:30", "task_type": "high_priority"},
            ],
            accommodations=[
                "Use noise-canceling headphones during focus blocks",
                "Enable screen reader for complex texts",
                "Set timers for each task block",
            ],
        )
