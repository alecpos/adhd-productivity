"""Service for managing hyperfocus sessions."""
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.hyperfocus_schema import (
    HyperfocusSchema,
    HyperfocusSessionCreate,
    HyperfocusSessionResponseSchema,
    HyperfocusStatsSchema,
)
from app.services.base_service import BaseService

logger = logging.getLogger(__name__)


class HyperfocusService(BaseService[HyperfocusSchema, HyperfocusSessionResponseSchema, HyperfocusSessionCreate]):
    """Service for managing hyperfocus sessions."""

    def __init__(self, db: AsyncSession):
        """Initialize the service with the HyperfocusSession model."""
        super().__init__(db=db, model=HyperfocusSchema, schema=HyperfocusSessionResponseSchema)

    async def start_session(self, session_data: Dict[str, Any]) -> HyperfocusSchema:
        """Start a new hyperfocus session."""
        logger.info(f"Starting hyperfocus session for user {session_data.get('user_id')}")
        try:
            session_data["start_time"] = datetime.now(timezone.utc)
            session_data["status"] = "ACTIVE"
            if "task_id" in session_data and (not session_data["task_id"]):
                del session_data["task_id"]
            session = await self.create(session_data)
            logger.info(f"Successfully created hyperfocus session {session.id}")
            return session
        except Exception as e:
            logger.error(f"Error creating hyperfocus session: {str(e)}")
            raise

    async def create_session(
        self,
        user_id: UUID,
        purpose: str,
        duration_minutes: int,
        focus_area: str,
        task_id: Optional[UUID] = None,
        environment: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> HyperfocusSchema:
        """Create a new hyperfocus session."""
        session_data = {
            "user_id": user_id,
            "purpose": purpose,
            "duration_minutes": duration_minutes,
            "focus_area": focus_area,
            "task_id": task_id,
            "environment": environment,
            "notes": notes,
            "start_time": datetime.now(timezone.utc),
        }
        return await self.create(session_data)

    async def end_session(self, session_id: UUID, user_id: UUID) -> HyperfocusSchema:
        """End a hyperfocus session and calculate productivity score."""
        session = await self.get_one(filters={"id": session_id, "user_id": user_id})
        if not session:
            raise ValueError("Session not found")
        session.end_time = datetime.now(timezone.utc)
        session.productivity_score = session.calculate_productivity_score()
        session.status = "completed"
        return await self.update(
            session_id,
            {
                "end_time": session.end_time,
                "productivity_score": session.productivity_score,
                "status": session.status,
            },
        )

    async def get_user_sessions(self, user_id: UUID) -> List[HyperfocusSchema]:
        """Get all hyperfocus sessions for a user."""
        query = select(HyperfocusSchema).where(
            HyperfocusSchema.user_id == user_id
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_session_stats(self, user_id: UUID) -> HyperfocusStatsSchema:
        """Get session statistics for a user."""
        sessions = await self.get_user_sessions(user_id)
        total_sessions = len(sessions)
        total_duration = 0
        completed_sessions = 0
        total_productivity = 0
        total_focus = 0
        total_quality = 0
        for session in sessions:
            if session.end_time:
                duration = (session.end_time - session.start_time).total_seconds() / 60
                total_duration += duration
                completed_sessions += 1
                if session.productivity_score:
                    total_productivity += session.productivity_score
                if session.focus_level:
                    total_focus += session.focus_level
                if session.quality_score:
                    total_quality += session.quality_score
        average_duration = total_duration / completed_sessions if completed_sessions > 0 else 0
        completion_rate = completed_sessions / total_sessions * 100 if total_sessions > 0 else 0
        average_productivity = (
            total_productivity / completed_sessions if completed_sessions > 0 else 0
        )
        average_focus = total_focus / completed_sessions if completed_sessions > 0 else 0
        average_quality = total_quality / completed_sessions if completed_sessions > 0 else 0
        task_type_distribution = {}
        for session in sessions:
            task_type = session.task_type
            task_type_distribution[task_type] = task_type_distribution.get(task_type, 0) + 1
        return HyperfocusStatsSchema(
            total_sessions=total_sessions,
            total_duration=int(total_duration),
            average_duration=round(average_duration, 2),
            average_productivity=round(average_productivity, 2),
            average_focus=round(average_focus, 2),
            average_quality=round(average_quality, 2),
            completion_rate=round(completion_rate, 2),
            most_productive_times=[],
            optimal_session_length=None,
            optimal_break_patterns=[],
            common_triggers=[],
            effective_environments=[],
            task_type_distribution=task_type_distribution,
            interruption_patterns=[],
            updated_at=datetime.utcnow(),
        )
