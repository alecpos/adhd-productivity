"""Pomodoro Service for managing Pomodoro Technique sessions."""

import json
import uuid
from uuid import UUID
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional, Union

from fastapi import HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.pomodoro_model import PomodoroSessionModel
from app.models.enums_model import PomodoroStatus, BreakType
from app.schemas.pomodoro_schema import (
    PomodoroResponseSchema,
    PomodoroResponse,
    PomodoroStatsSchema,
    SessionStatusSchema,
    SessionStatsSchema,
    DetailedAnalyticsSchema,
    PomodoroCreateSchema
)
from app.utils.decorators import handle_service_error
from app.services.base_service import BaseService


class PomodoroService(BaseService[PomodoroSessionModel, PomodoroResponseSchema, PomodoroCreateSchema]):
    """Service for managing pomodoro sessions."""

    def __init__(self, db: AsyncSession):
        """Initialize the service with the PomodoroSession model."""
        super().__init__(db=db, model=PomodoroSessionModel, schema_class=PomodoroResponseSchema)

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
        sessions = result.scalars().all()

        # Convert each model instance to the response schema
        return [PomodoroResponseSchema.model_validate(session) for session in sessions]

    async def get_session_stats(self, user_id: UUID) -> SessionStatsSchema:
        """Get basic session statistics for a user."""
        sessions = await self.get_user_sessions(user_id)

        total_sessions = len(sessions)
        completed_sessions = sum(1 for s in sessions if s.completed)
        total_focus_time = sum(s.work_duration * s.completed_sessions for s in sessions)

        return SessionStatsSchema(
            total_sessions=total_sessions,
            completed_sessions=completed_sessions,
            total_focus_time=total_focus_time
        )

    async def calculate_trend(self, data_points: list) -> float:
        """Calculate a simple trend from a list of numeric data points."""
        if not data_points or len(data_points) < 2:
            return 0.0

        # Simple linear trend calculation (positive = improving, negative = declining)
        first_point = data_points[0]
        last_point = data_points[-1]

        if first_point == last_point:
            return 0.0

        return (last_point - first_point) / max(1, len(data_points) - 1)

    async def get_detailed_analytics(self, user_id: UUID) -> DetailedAnalyticsSchema:
        """Get detailed analytics for a user's pomodoro sessions."""
        sessions = await self.get_user_sessions(user_id)

        # Basic stats
        total_sessions = len(sessions)
        completed_sessions = sum(1 for s in sessions if s.completed)
        active_sessions = sum(1 for s in sessions if s.status == PomodoroStatus.ACTIVE.value)

        # Focus scores
        all_focus_scores = []
        for session in sessions:
            if hasattr(session, 'focus_scores') and session.focus_scores:
                for score in session.focus_scores:
                    if 'productivity_rating' in score:
                        all_focus_scores.append(score['productivity_rating'])

        avg_productivity = sum(all_focus_scores) / max(1, len(all_focus_scores)) if all_focus_scores else 0
        productivity_trend = await self.calculate_trend(all_focus_scores) if all_focus_scores else 0

        # Interruption data
        total_interruptions = sum(getattr(s, 'interruption_count', 0) for s in sessions)

        return DetailedAnalyticsSchema(
            total_sessions=total_sessions,
            completed_sessions=completed_sessions,
            active_sessions=active_sessions,
            avg_productivity=avg_productivity,
            productivity_trend=productivity_trend,
            total_interruptions=total_interruptions
        )

    async def create_session(self, user_id: UUID, task_id: UUID, duration: int, break_duration: int, long_break_duration: int =15, sessions_until_long_break: Optional[int]=None, cycles_before_long_break: Optional[int]=None, notes: Optional[str]=None, auto_start_breaks: bool =False, sound_notifications: bool =True, strict_mode: bool =False) -> PomodoroResponseSchema:
        """Create a new pomodoro session."""
        if sessions_until_long_break is None and cycles_before_long_break is not None:
            sessions_until_long_break = cycles_before_long_break
        elif sessions_until_long_break is None:
            sessions_until_long_break = 4

        # Get the current time for both created_at and updated_at
        now = datetime.now(timezone.utc)
        session_id = uuid.uuid4()

        # Prepare the model data - only include fields that exist in the model
        model_data = {
            'id': session_id,
            'user_id': user_id,
            'task_id': task_id,
            'work_duration': duration,  # Use work_duration in the model (not duration)
            'short_break_duration': break_duration,
            'long_break_duration': long_break_duration,
            'sessions_until_long_break': sessions_until_long_break,
            'notes': notes,
            'start_time': now,
            'status': PomodoroStatus.ACTIVE.value,
            'completed_sessions': 0,
            'current_session': 1,
            'completed': False,
            'meta_data': {
                'auto_start_breaks': auto_start_breaks,
                'sound_notifications': sound_notifications,
                'strict_mode': strict_mode
            },
            'completed_tasks': [],
            'focus_scores': [],
            'breaks_taken': [],
            'interruptions': [],
            'interruption_count': 0,
            'break_type': BreakType.SHORT.value,
            'created_at': now,
            'updated_at': now  # Set updated_at to be the same as created_at
        }

        # Create the model instance directly
        model_instance = PomodoroSessionModel(**model_data)

        # Add to database - don't need to await since it's a synchronous operation
        self.db.add(model_instance)
        await self.db.commit()
        await self.db.refresh(model_instance)

        # Convert to response schema
        return PomodoroResponseSchema.model_validate(model_instance)

    async def get_by_id(self, id: UUID) -> Optional[PomodoroSessionModel]:
        """Get a model by id."""
        query = select(self.model).where(self.model.id == id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    @handle_service_error
    async def complete_work_period(self, session_id: UUID, completion_data: Dict[str, Any]) -> PomodoroResponseSchema:
        """Complete a work period for a pomodoro session."""
        # Retrieve the session
        session = await self.get_by_id(session_id)
        if not session:
            raise HTTPException(status_code=404, detail='Session not found')

        # Create a record for the focus/productivity score
        focus_record = {
            'productivity_rating': float(completion_data.get('productivity_rating', 5)),
            'distractions': int(completion_data.get('distractions', 0)),
            'notes': completion_data.get('notes', ''),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

        # Initialize arrays if they don't exist
        if not hasattr(session, 'focus_scores') or session.focus_scores is None:
            session.focus_scores = []
        if not hasattr(session, 'completed_tasks') or session.completed_tasks is None:
            session.completed_tasks = []

        # Handle focus scores
        if isinstance(session.focus_scores, str):
            try:
                focus_scores = json.loads(session.focus_scores)
            except:
                focus_scores = []
        else:
            focus_scores = list(session.focus_scores or [])

        focus_scores.append(focus_record)

        # Handle completed tasks
        completed_tasks = []
        if 'completed_tasks' in completion_data and completion_data['completed_tasks']:
            if isinstance(session.completed_tasks, str):
                try:
                    completed_tasks = json.loads(session.completed_tasks)
                except:
                    completed_tasks = []
            else:
                completed_tasks = list(session.completed_tasks or [])

            # Add any new tasks
            for task in completion_data['completed_tasks']:
                if task not in completed_tasks:
                    completed_tasks.append(task)

        # Update session status and counters
        completed_sessions = session.completed_sessions + 1 if hasattr(session, 'completed_sessions') and session.completed_sessions is not None else 1
        current_session = session.current_session + 1 if hasattr(session, 'current_session') and session.current_session is not None else 2

        # Update the database using our own update method instead of direct SQL
        update_data = {
            'status': PomodoroStatus.BREAK.value,
            'completed_sessions': completed_sessions,
            'current_session': current_session,
            'focus_scores': focus_scores,
            'completed_tasks': completed_tasks,
            'updated_at': datetime.now(timezone.utc)
        }

        # Use our update method which calls commit and returns the updated session
        updated_session = await self.update(session_id, update_data)

        # Return the updated session
        return updated_session

    async def complete_break_period(self, session_id: UUID, break_data: Dict[str, Any]) -> PomodoroResponseSchema:
        """Complete a break period."""
        session = await self.get_by_id(session_id)
        if not session:
            raise HTTPException(status_code=404, detail='Session not found')

        # Initialize empty arrays if they don't exist yet
        if not hasattr(session, 'breaks_taken') or session.breaks_taken is None:
            session.breaks_taken = []

        # Create a record for the break activity
        break_record = {
            'activity': break_data.get('break_activity', ''),
            'refreshed_rating': break_data.get('refreshed_rating', 5),
            'notes': break_data.get('notes', ''),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

        # Handle breaks_taken
        if isinstance(session.breaks_taken, str):
            try:
                breaks_taken = json.loads(session.breaks_taken)
            except:
                breaks_taken = []
        else:
            breaks_taken = list(session.breaks_taken or [])

        breaks_taken.append(break_record)

        # Update the database using our update method
        update_data = {
            'status': PomodoroStatus.READY.value,
            'breaks_taken': breaks_taken,
            'updated_at': datetime.now(timezone.utc)
        }

        # Use our update method which calls commit
        updated_session = await self.update(session_id, update_data)

        # Return the updated session
        return updated_session

    async def get_session_status(self, session_id: UUID) -> SessionStatusSchema:
        """Get the current status and timing information for a session."""
        session = await self.get_by_id(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Calculate if the next break should be a long break
        is_long_break_due = False
        if hasattr(session, 'completed_sessions') and hasattr(session, 'sessions_until_long_break'):
            is_long_break_due = (session.completed_sessions > 0 and
                                session.completed_sessions % session.sessions_until_long_break == 0)

        # Determine next break duration
        next_break_duration = session.short_break_duration
        if is_long_break_due:
            next_break_duration = session.long_break_duration

        return SessionStatusSchema(
            status=session.status,
            time_remaining=0,
            current_session=session.current_session,
            total_sessions=session.sessions_until_long_break,
            break_type=session.break_type if hasattr(session, 'break_type') else 'short',
            cycles_completed=session.completed_sessions,  # This should be equal to the completed_sessions attribute
            next_break_duration=next_break_duration,
            is_long_break_due=is_long_break_due
        )

    async def record_interruption(self, session_id: UUID, interruption_data: Dict[str, Any]) -> PomodoroResponseSchema:
        """Record an interruption during a session."""
        session = await self.get_session(session_id)
        if not session.interruptions:
            session.interruptions = []
            session.interruption_count = 0
        interruption = {'time': datetime.now(timezone.utc).isoformat(), 'type': interruption_data.get('type', 'unknown'), 'duration': interruption_data.get('duration', 0), 'reason': interruption_data.get('reason'), 'action_taken': interruption_data.get('action_taken')}

        # Update model attributes directly
        session_model = await self.get_by_id(session_id)
        if not session_model:
            raise HTTPException(status_code=404, detail='Session not found')

        # Get existing interruptions as list
        interruptions = list(session_model.interruptions) if session_model.interruptions else []
        interruptions.append(interruption)

        # Update model fields
        session_model.interruptions = interruptions
        session_model.interruption_count = len(interruptions)
        session_model.status = PomodoroStatus.PAUSED.value

        # Update meta_data
        meta_data = dict(session_model.meta_data) if session_model.meta_data else {}
        meta_data['interruption_count'] = len(interruptions)
        session_model.meta_data = meta_data

        # Update the timestamp
        session_model.updated_at = datetime.now(timezone.utc)

        # Commit changes
        await self.db.commit()

        # Convert to schema before returning
        return PomodoroResponseSchema.model_validate(session_model)

    async def resume_session(self, session_id: UUID, resume_data: Dict[str, Any]) -> PomodoroResponseSchema:
        """Resume a paused pomodoro session."""
        session = await self.get_by_id(session_id)
        if not session:
            raise HTTPException(status_code=404, detail='Session not found')

        if session.completed:
            raise HTTPException(status_code=400, detail='Cannot resume completed session')
        if session.status != PomodoroStatus.PAUSED:
            raise HTTPException(status_code=400, detail='Session is not paused')

        # Update session directly
        session.status = PomodoroStatus.ACTIVE.value
        session.updated_at = datetime.now(timezone.utc)

        # Update meta_data if remaining_duration is provided
        if 'remaining_duration' in resume_data:
            meta_data = dict(session.meta_data) if session.meta_data else {}
            meta_data['remaining_duration'] = resume_data.get('remaining_duration')
            session.meta_data = meta_data

        # Update notes if provided
        if resume_data.get('notes'):
            session.notes = resume_data.get('notes')

        # Commit changes
        await self.db.commit()

        # Convert to schema before returning
        return PomodoroResponseSchema.model_validate(session)

    async def update_session_preferences(self, session_id: UUID, preferences: Dict[str, Any]) -> PomodoroResponseSchema:
        """Update session preferences."""
        session = await self.get_by_id(session_id)
        if not session:
            raise HTTPException(status_code=404, detail='Session not found')

        valid_fields = {'work_duration', 'short_break_duration', 'long_break_duration', 'sessions_until_long_break', 'auto_start_breaks', 'sound_notifications', 'strict_mode'}

        # Initialize meta_data
        meta_data = dict(session.meta_data or {})

        # Extract direct model fields vs. meta_data fields
        update_data = {}

        for field, value in preferences.items():
            if field in {'work_duration', 'short_break_duration', 'long_break_duration', 'sessions_until_long_break'}:
                update_data[field] = value
            elif field in {'auto_start_breaks', 'sound_notifications', 'strict_mode'}:
                meta_data[field] = value

        # Add the meta_data to update_data
        update_data['meta_data'] = meta_data
        update_data['updated_at'] = datetime.now(timezone.utc)

        # Use our update method to commit changes and return updated session
        updated_session = await self.update(session_id, update_data)

        # Return the updated session
        return updated_session

    async def update(self, id: UUID, update_data: Dict[str, Any]) -> PomodoroResponseSchema:
        """Update a model by ID with the given data."""
        query = select(self.model).where(self.model.id == id)
        result = await self.db.execute(query)
        model_instance = result.scalar_one_or_none()

        if not model_instance:
            raise HTTPException(status_code=404, detail=f"{self.model.__name__} not found")

        # Update the model with new data (compatible with SQLAlchemy 2.0)
        for key, value in update_data.items():
            setattr(model_instance, key, value)

        # Update the updated_at timestamp for all updates
        setattr(model_instance, 'updated_at', datetime.now(timezone.utc))

        await self.db.commit()
        await self.db.refresh(model_instance)

        return self.schema_class.model_validate(model_instance)
