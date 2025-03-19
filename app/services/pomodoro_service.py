"""Service for managing pomodoro sessions."""

from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException

from app.services.base_service import BaseService
from app.models.pomodoro_model import PomodoroSessionModel
from app.models.enums_model import BreakType, PomodoroStatus
from app.schemas.pomodoro_schema import (
    SessionStatusSchema,
    SessionAnalyticsSchema,
    PomodoroSchema,
    PomodoroCreateSchema,
    PomodoroUpdateSchema,
    PomodoroResponseSchema,
    PomodoroStatsSchema,
)
from app.utils.decorators import handle_service_error


class PomodoroService(BaseService[PomodoroSessionModel, PomodoroResponseSchema, PomodoroCreateSchema]):
    """Service for managing pomodoro sessions."""

    def __init__(self, db: AsyncSession):
        """Initialize the service with the PomodoroSession model."""
        super().__init__(db=db, model=PomodoroSessionModel, schema=PomodoroResponseSchema)

    async def get_session(self, session_id: UUID) -> PomodoroResponseSchema:
        """Get a pomodoro session by ID."""
        session = await self.get_one(filters={'id': session_id})
        if not session:
            raise HTTPException(status_code=404, detail='Session not found')
        return PomodoroResponseSchema.model_validate(session)

    async def get_user_sessions(self, user_id: UUID) -> List[PomodoroResponseSchema]:
        """Get all pomodoro sessions for a user."""
        query = select(PomodoroSessionModel).where(PomodoroSessionModel.user_id == user_id)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_session_stats(self, user_id: UUID) -> PomodoroStatsSchema:
        """Get session statistics for a user."""
        sessions = await self.get_user_sessions(user_id)
        total_sessions = len(sessions)
        total_duration = 0
        completed_sessions = 0
        for session in sessions:
            if session.end_time:
                duration = (session.end_time - session.start_time).total_seconds() / 60
                total_duration += duration
                completed_sessions += 1
        average_duration = total_duration / completed_sessions if completed_sessions > 0 else 0
        completion_rate = completed_sessions / total_sessions * 100 if total_sessions > 0 else 0
        return PomodoroStatsSchema(total_sessions=total_sessions, total_duration=int(total_duration), average_duration=round(average_duration, 2), completion_rate=round(completion_rate, 2))

    async def create_session(self, user_id: UUID, task_id: UUID, duration: int, break_duration: int, long_break_duration: int =15, sessions_until_long_break: Optional[int]=None, cycles_before_long_break: Optional[int]=None, notes: Optional[str]=None, auto_start_breaks: bool =False, sound_notifications: bool =True, strict_mode: bool =False) -> PomodoroResponseSchema:
        """Create a new pomodoro session."""
        if sessions_until_long_break is None and cycles_before_long_break is not None:
            sessions_until_long_break = cycles_before_long_break
        elif sessions_until_long_break is None:
            sessions_until_long_break = 4
        session_data = {'user_id': user_id, 'task_id': task_id, 'work_duration': duration, 'short_break_duration': break_duration, 'long_break_duration': long_break_duration, 'sessions_until_long_break': sessions_until_long_break, 'notes': notes, 'start_time': datetime.now(timezone.utc), 'status': PomodoroStatus.ACTIVE.value, 'completed_sessions': 0, 'current_session': 1, 'completed': False, 'meta_data': {'auto_start_breaks': auto_start_breaks, 'sound_notifications': sound_notifications, 'strict_mode': strict_mode}, 'completed_tasks': [], 'focus_scores': []}
        return await self.create(session_data)

    @handle_service_error
    async def complete_work_period(self, session_id: UUID, completion_data: Dict[str, Any]) -> Optional[PomodoroResponseSchema]:
        """Complete a work period and update session metrics."""
        session = await self.get_by_id(session_id)
        if not session:
            raise HTTPException(status_code=404, detail='Session not found')
        if not hasattr(session, 'focus_scores') or session.focus_scores is None:
            session.focus_scores = []
        elif not isinstance(session.focus_scores, list):
            session.focus_scores = []
        productivity_rating = completion_data.get('productivity_rating')
        if productivity_rating is not None:
            try:
                productivity_rating = float(productivity_rating)
                if not 0 <= productivity_rating <= 10:
                    raise HTTPException(status_code=400, detail='Productivity rating must be between 0 and 10')
            except (ValueError, TypeError):
                raise HTTPException(status_code=400, detail='Invalid productivity rating format')
        new_score = {'productivity_rating': productivity_rating, 'distractions': int(completion_data.get('distractions', 0)), 'notes': completion_data.get('notes'), 'timestamp': datetime.now(timezone.utc).isoformat()}
        focus_scores = list(session.focus_scores)
        focus_scores.append(new_score)
        completed_tasks = list(session.completed_tasks) if session.completed_tasks else []
        if 'completed_tasks' in completion_data:
            completed_tasks.extend(completion_data['completed_tasks'])
        update_data = {'focus_scores': focus_scores, 'completed_tasks': completed_tasks, 'completed_sessions': session.completed_sessions + 1, 'current_session': session.current_session + 1, 'status': PomodoroStatus.BREAK.value, 'break_type': BreakType.LONG.value if session.completed_sessions + 1 > 0 and (session.completed_sessions + 1) % session.sessions_until_long_break == 0 else BreakType.SHORT.value}
        updated_session = await self.update(session.id, update_data)
        await self.db.refresh(updated_session)
        refreshed_session = await self.get_by_id(session.id)
        if not refreshed_session.focus_scores or len(refreshed_session.focus_scores) == 0:
            raise HTTPException(status_code=500, detail='Failed to save focus scores')

    async def complete_break_period(self, session_id: UUID, break_data: Dict[str, Any]) -> PomodoroResponseSchema:
        """Complete a break period in a pomodoro session."""
        session = await self.get_session(session_id)
        if session.completed:
            raise HTTPException(status_code=400, detail='Session is already completed')
        if session.status not in [PomodoroStatus.BREAK, PomodoroStatus.LONG_BREAK]:
            raise HTTPException(status_code=400, detail='Cannot complete break period when not on break')
        if not hasattr(session, 'breaks_taken') or session.breaks_taken is None:
            session.breaks_taken = []
        elif not isinstance(session.breaks_taken, list):
            session.breaks_taken = []
        current_time = datetime.now(timezone.utc)
        break_record = {'start_time': session.start_time.isoformat(), 'end_time': current_time.isoformat(), 'activity': break_data.get('break_activity'), 'refreshed_rating': break_data.get('refreshed_rating'), 'notes': break_data.get('notes'), 'type': session.break_type}
        breaks_taken = list(session.breaks_taken) if session.breaks_taken else []
        breaks_taken.append(break_record)
        update_data = {'breaks_taken': breaks_taken, 'status': PomodoroStatus.READY.value}
        updated_session = await self.update(session.id, update_data)
        await self.db.refresh(updated_session)

    async def get_session_status(self, session_id: UUID) -> SessionStatusSchema:
        """Get the current status of a pomodoro session."""
        session = await self.get_session(session_id)
        if isinstance(session.status, str):
            session.status = PomodoroStatus(session.status)
        if isinstance(session.break_type, str):
            session.break_type = BreakType(session.break_type)
        is_long_break_due = session.completed_sessions > 0 and session.completed_sessions % session.sessions_until_long_break == 0
        next_break_duration = None
        if session.status != PomodoroStatus.COMPLETED:
            if is_long_break_due:
                next_break_duration = session.long_break_duration
            else:
                next_break_duration = session.short_break_duration
        return SessionStatusSchema(status=session.status.value, time_remaining=0, current_session=session.current_session, total_sessions=session.sessions_until_long_break, break_type=session.break_type.value if session.break_type else None, cycles_completed=session.completed_sessions, next_break_duration=next_break_duration, is_long_break_due=is_long_break_due)

    async def get_detailed_analytics(self, user_id: UUID) -> SessionAnalyticsSchema:
        """Get detailed analytics for a user's pomodoro sessions."""
        sessions = await self.get_user_sessions(user_id)
        if not sessions:
            return SessionAnalyticsSchema(total_sessions=0, completed_sessions=0, total_focus_time=0, average_productivity=0.0, productivity_trend='stable', distraction_trend='stable', completion_rate=0.0)
        total_sessions = len(sessions)
        completed_sessions = sum((1 for s in sessions if s.completed_sessions > 0))
        total_focus_time = sum((s.work_duration * s.completed_sessions for s in sessions if s.completed_sessions > 0 and s.work_duration is not None))
        productivity_ratings = []
        distraction_counts = []
        for session in sorted(sessions, key=lambda x: x.start_time):
            if not session.focus_scores or not isinstance(session.focus_scores, list):
                continue
            session_distractions = []
            session_productivity = None
            for score in session.focus_scores:
                if not isinstance(score, dict):
                    continue
                if 'productivity_rating' in score and score['productivity_rating'] is not None:
                    try:
                        rating = float(score['productivity_rating'])
                        if 0 <= rating <= 10:
                            session_productivity = rating
                    except (ValueError, TypeError):
                        pass
                try:
                    count = int(score.get('distractions', 0))
                    if count >= 0:
                        session_distractions.append(count)
                except (ValueError, TypeError):
                    pass
            if session_productivity is not None:
                productivity_ratings.append(session_productivity)
            if session_distractions:
                distraction_counts.append(sum(session_distractions))
        average_productivity = sum(productivity_ratings) / len(productivity_ratings) if productivity_ratings else 0.0
        productivity_trend = self.calculate_trend(productivity_ratings)
        if len(distraction_counts) >= 2:
            if all((distraction_counts[i] >= distraction_counts[i + 1] for i in range(len(distraction_counts) - 1))):
                distraction_trend = 'improving'
            elif all((distraction_counts[i] <= distraction_counts[i + 1] for i in range(len(distraction_counts) - 1))):
                distraction_trend = 'declining'
            else:
                distraction_trend = 'stable'
        else:
            distraction_trend = 'stable'
        completion_rate = completed_sessions / total_sessions * 100 if total_sessions > 0 else 0.0
        return SessionAnalyticsSchema(total_sessions=total_sessions, completed_sessions=completed_sessions, total_focus_time=total_focus_time, average_productivity=round(average_productivity, 2), productivity_trend=productivity_trend, distraction_trend=distraction_trend, completion_rate=round(completion_rate, 2))

    async def record_interruption(self, session_id: UUID, interruption_data: Dict[str, Any]) -> PomodoroResponseSchema:
        """Record an interruption during a session."""
        session = await self.get_session(session_id)
        if not session.interruptions:
            session.interruptions = []
            session.interruption_count = 0
        interruption = {'time': datetime.now(timezone.utc).isoformat(), 'type': interruption_data.get('type', 'unknown'), 'duration': interruption_data.get('duration', 0), 'reason': interruption_data.get('reason'), 'action_taken': interruption_data.get('action_taken')}
        interruptions = session.interruptions + [interruption]
        interruption_count = len(interruptions)
        update_data = {'interruptions': interruptions, 'interruption_count': interruption_count, 'status': PomodoroStatus.PAUSED.value, 'meta_data': {**session.meta_data, 'interruption_count': interruption_count}}
        updated_session = await self.update(session.id, update_data)

    async def resume_session(self, session_id: UUID, resume_data: Dict[str, Any]) -> PomodoroResponseSchema:
        """Resume a paused pomodoro session."""
        session = await self.get_session(session_id)
        if session.completed:
            raise HTTPException(status_code=400, detail='Cannot resume completed session')
        if session.status != PomodoroStatus.PAUSED:
            raise HTTPException(status_code=400, detail='Session is not paused')
        session.remaining_duration = resume_data.get('remaining_duration')
        if resume_data.get('notes'):
            session.notes = resume_data.get('notes')
        session.status = PomodoroStatus.ACTIVE
        session.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(session)

    async def update_session_preferences(self, session_id: UUID, preferences: Dict[str, Any]) -> PomodoroResponseSchema:
        """Update session preferences."""
        session = await self.get_session(session_id)
        valid_fields = {'work_duration', 'short_break_duration', 'long_break_duration', 'sessions_until_long_break', 'auto_start_breaks', 'sound_notifications', 'strict_mode'}
        update_data = {}
        meta_data = dict(session.meta_data or {})
        for key, value in preferences.items():
            if key not in valid_fields:
                raise HTTPException(status_code=400, detail=f'Invalid preference key: {key}')
            if key in {'work_duration', 'short_break_duration', 'long_break_duration', 'sessions_until_long_break'}:
                if not isinstance(value, int) or value <= 0:
                    raise HTTPException(status_code=400, detail=f'{key} must be a positive integer')
                update_data[key] = value
            else:
                if not isinstance(value, bool):
                    raise HTTPException(status_code=400, detail=f'{key} must be a boolean')
                meta_data[key] = value
        if meta_data != session.meta_data:
            update_data['meta_data'] = meta_data
        if not update_data:
            return session
        updated_session = await self.update(session.id, update_data)
        return updated_session
