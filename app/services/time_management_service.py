"""Time management service module."""

from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from uuid import UUID
from sqlalchemy import and_, select

from app.models.time_block_model import TimeBlockModel, BlockType
from app.schemas.time_block_schema import TimePreferences, TimeAnalytics
from app.schemas.scheduling_schema import ScheduleResponseSchema
from app.schemas.focus_schema import FocusSessionSchema
from app.models.focus_model import FocusSessionType
from app.schemas.schema_manager_schema import DictSchema


class TimeManagementService:
    """Service for managing time blocks and scheduling."""

    def __init__(self, db: AsyncSession):
        """Initialize the service with database session."""
        self.db = db

    async def schedule_blocks(
        self,
        user_id: UUID,
        start_time: datetime,
        end_time: datetime,
        block_duration: int = 25,
        break_duration: int = 5,
        preferred_hours: Optional[List[int]] = None,
    ) -> ScheduleResponseSchema:
        """Schedule time blocks considering user preferences and calendar availability."""
        blocks = []
        total_focus_time = 0
        total_breaks = 0
        current_time = start_time
        while current_time < end_time:
            if preferred_hours and current_time.hour not in preferred_hours:
                current_time += timedelta(hours=1)
                current_time = current_time.replace(minute=0, second=0)
            focus_block = TimeBlockModel(
                user_id=user_id,
                start_time=current_time,
                end_time=current_time + timedelta(minutes=block_duration),
                block_type=BlockType.POMODORO,
                title=f"Focus Block {current_time.strftime('%H:%M')}",
            )
            blocks.append(focus_block)
            total_focus_time += block_duration
            current_time += timedelta(minutes=block_duration)
            if current_time < end_time:
                break_block = TimeBlockModel(
                    user_id=user_id,
                    start_time=current_time,
                    end_time=current_time + timedelta(minutes=break_duration),
                    block_type=BlockType.BREAK,
                    title="Break",
                )
                blocks.append(break_block)
                total_breaks += 1
                current_time += timedelta(minutes=break_duration)
        self.db.add_all(blocks)
        await self.db.commit()
        return ScheduleResponseSchema(
            blocks=blocks, total_focus_time=total_focus_time, total_breaks=total_breaks
        )

    async def start_focus_session(
        self, user_id: UUID, duration: int, session_type: str = "pomodoro"
    ) -> FocusSessionSchema:
        """Start a focus session (pomodoro or hyperfocus)."""
        start_time = datetime.utcnow()
        end_time = start_time + timedelta(minutes=duration)
        session = FocusSessionSchema(
            user_id=user_id,
            start_time=start_time,
            session_type=FocusSessionType(session_type),
            metrics={"planned_duration": duration},
        )
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        return session

    async def end_focus_session(self, user_id: UUID, session_id: UUID) -> FocusSessionSchema:
        """End a focus session and record metrics."""
        session = await self.db.execute(
            select(FocusSessionSchema).where(
                and_(FocusSessionSchema.id == session_id, FocusSessionSchema.user_id == user_id)
            )
        )
        session = session.scalar_one_or_none()
        if not session:
            raise ValueError("Session not found")
        session.end_time = datetime.utcnow()
        actual_duration = (session.end_time - session.start_time).total_seconds() / 60
        session.metrics = {
            **(session.metrics or {}),
            "actual_duration": actual_duration,
            "completion_rate": actual_duration / session.metrics["planned_duration"] * 100,
        }
        await self.db.commit()
        await self.db.refresh(session)

    async def get_time_analytics(
        self, user_id: UUID, start_date: datetime, end_date: datetime
    ) -> DictSchema:
        """Get analytics about time usage and productivity."""
        blocks_query = await self.db.execute(
            select(TimeBlockModel).where(
                and_(
                    TimeBlockModel.user_id == user_id,
                    TimeBlockModel.start_time >= start_date,
                    TimeBlockModel.start_time <= end_date,
                )
            )
        )
        blocks = blocks_query.scalars().all()
        sessions_query = await self.db.execute(
            select(FocusSessionSchema).where(
                and_(
                    FocusSessionSchema.user_id == user_id,
                    FocusSessionSchema.start_time >= start_date,
                    FocusSessionSchema.start_time <= end_date,
                )
            )
        )
        sessions = sessions_query.scalars().all()
        total_focus_time = sum(
            (
                (block.end_time - block.start_time).total_seconds() / 3600
                for block in blocks
                if block.block_type != BlockType.BREAK
            )
        )
        completed_sessions = [s for s in sessions if s.end_time is not None]
        avg_completion_rate = (
            sum((s.metrics.get("completion_rate", 0) for s in completed_sessions))
            / len(completed_sessions)
            if completed_sessions
            else 0
        )
        return {
            "total_focus_hours": round(total_focus_time, 2),
            "completed_sessions": len(completed_sessions),
            "average_completion_rate": round(avg_completion_rate, 2),
            "most_productive_hours": self._calculate_productive_hours(blocks),
        }

    def _calculate_productive_hours(self, blocks: List[TimeBlockModel]) -> List[int]:
        """Helper method to calculate most productive hours based on completed blocks."""
        hour_completion_rates = {}
        for block in blocks:
            if block.block_type == BlockType.BREAK:
                continue
            hour = block.start_time.hour
            if hour not in hour_completion_rates:
                hour_completion_rates[hour] = {"completed": 0, "total": 0}
            hour_completion_rates[hour]["total"] += 1
            if block.is_completed:
                hour_completion_rates[hour]["completed"] += 1
        hour_rates = [
            (hour, stats["completed"] / stats["total"] * 100)
            for hour, stats in hour_completion_rates.items()
            if stats["total"] > 0
        ]
        return [hour for hour, rate in sorted(hour_rates, key=lambda x: x[1], reverse=True)]
