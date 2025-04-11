"""Focus session service."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.focus_model import FocusSessionModel
from app.schemas.focus_schema import (
    FocusSessionCreateSchema,
    FocusSessionSchema,
    FocusSessionUpdate,
)
from app.services.base_service import BaseService


class FocusService(BaseService[FocusSessionModel, FocusSessionSchema, FocusSessionCreateSchema]):
    """Service for managing focus sessions."""

    def __init__(self, db: AsyncSession):
        """Initialize the focus service."""
        super().__init__(db, FocusSessionModel, FocusSessionSchema)

    async def start_session(self, data: FocusSessionCreateSchema) -> FocusSessionSchema:
        """Start a new focus session."""
        session = FocusSessionModel(
            **data.dict(),
            status="active",
            start_time=datetime.utcnow(),
        )
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        return self.schema_class.from_orm(session)

    async def end_session(
        self, id: UUID, productivity_score: Optional[int] = None, notes: Optional[str] = None
    ) -> Optional[FocusSessionSchema]:
        """End a focus session."""
        session = await self.get_by_id(id)
        if not session:
            return None

        session.status = "completed"
        session.end_time = datetime.utcnow()
        if productivity_score is not None:
            session.productivity_score = productivity_score
        if notes is not None:
            session.notes = notes

        # Calculate actual focus duration
        total_break_duration = sum(b.duration for b in (session.breaks or []))
        session.actual_focus_duration = (
            (session.end_time - session.start_time).total_seconds() // 60
        ) - total_break_duration

        await self.db.commit()
        await self.db.refresh(session)
        return self.schema_class.from_orm(session)

    async def pause_session(
        self, id: UUID, reason: Optional[str] = None
    ) -> Optional[FocusSessionSchema]:
        """Pause a focus session."""
        session = await self.get_by_id(id)
        if not session:
            return None

        session.status = "paused"
        if reason:
            session.meta_data = {**(session.meta_data or {}), "pause_reason": reason}

        await self.db.commit()
        await self.db.refresh(session)
        return self.schema_class.from_orm(session)

    async def resume_session(self, id: UUID) -> Optional[FocusSessionSchema]:
        """Resume a paused focus session."""
        session = await self.get_by_id(id)
        if not session:
            return None

        session.status = "active"
        await self.db.commit()
        await self.db.refresh(session)
        return self.schema_class.from_orm(session)

    async def get_statistics(
        self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None
    ) -> dict:
        """Get focus session statistics."""
        query = select(FocusSessionModel)
        if start_date:
            query = query.where(FocusSessionModel.start_time >= start_date)
        if end_date:
            query = query.where(FocusSessionModel.start_time <= end_date)

        result = await self.db.execute(query)
        sessions = result.scalars().all()

        total_sessions = len(sessions)
        total_duration = sum(s.duration for s in sessions)
        total_actual_duration = sum(s.actual_focus_duration for s in sessions if s.actual_focus_duration)
        avg_focus_level = sum(s.focus_level for s in sessions) / total_sessions if total_sessions else 0
        avg_energy_level = sum(s.energy_level for s in sessions) / total_sessions if total_sessions else 0
        avg_productivity = (
            sum(s.productivity_score for s in sessions if s.productivity_score is not None)
            / len([s for s in sessions if s.productivity_score is not None])
            if any(s.productivity_score is not None for s in sessions)
            else 0
        )

        return {
            "total_sessions": total_sessions,
            "total_planned_duration": total_duration,
            "total_actual_duration": total_actual_duration,
            "average_focus_level": round(avg_focus_level, 2),
            "average_energy_level": round(avg_energy_level, 2),
            "average_productivity_score": round(avg_productivity, 2),
        }
