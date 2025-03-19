"""Body doubling service module."""

import json
from datetime import datetime, timezone
from types import SimpleNamespace
from typing import Any, Dict, List, NamedTuple, Optional, TypedDict, cast
from uuid import UUID, uuid4
import logging

from fastapi import HTTPException, status
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums_model import ActivityType, EnergyLevel, SessionStatus, SessionType
from app.models.body_doubling_model import BodyDoublingSessionModel
from app.schemas.body_doubling_schema import (
    BodyDoublingSchema,
    CreateBodyDoublingSchema,
    GroupSessionSchema,
    SessionAnalyticsSchema,
    SessionFeedbackSchema,
)
from app.schemas.hyperfocus_schema import (
    HyperfocusSessionSchema,
    HyperfocusStatsSchema,
)
from app.services.base_service import BaseService
from app.utils.error_handler import handle_service_error


class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder for datetime objects."""

    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


class SessionMetaData(TypedDict, total=False):
    """Type definition for session meta data."""

    participants: List[str]
    join_requests: List[Dict[str, Any]]
    original_session_id: str


class SessionAnalyticsService(NamedTuple):
    """Analytics for body doubling sessions."""

    total_sessions: int
    total_focus_time: int
    average_productivity: float
    productivity_trend: str
    distraction_trend: str
    completion_rate: float
    most_productive_times: List[int]
    preferred_activity_types: List[str]
    preferred_session_types: List[str]
    session_stats: Dict[str, int]
    average_duration: float
    average_focus_rating: float
    average_productivity_rating: float


class SessionFeedbackService(NamedTuple):
    """Feedback for a body doubling session."""

    feedback_points: List[Dict[str, Any]]
    session_id: UUID
    user_id: UUID
    average_focus_level: float
    final_rating: Optional[Dict[str, Any]]


class GroupSessionInfoService(NamedTuple):
    """Information about a group session."""

    session_id: str
    host_id: str
    topic: Optional[str]
    description: Optional[str]
    status: str
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    max_participants: int
    current_participants: List[str]
    pending_requests: List[Dict[str, Any]]
    environment: Optional[Dict[str, Any]]
    activity_type: str
    duration_minutes: Optional[int]


class BodyDoublingService(BaseService[BodyDoublingSessionModel, BodyDoublingSchema, CreateBodyDoublingSchema]):
    """Service for managing body doubling sessions."""

    def __init__(self, db: AsyncSession):
        """Initialize the service with database session."""
        super().__init__(db=db, model=BodyDoublingSessionModel, schema_class=BodyDoublingSchema)

    def _get_meta_data(self, session: BodyDoublingSessionModel) -> Optional[SessionMetaData]:
        """Safely get and cast the session meta_data."""
        if not session.meta_data:
            return None
        return cast(SessionMetaData, session.meta_data)

    def _init_meta_data(self, session: BodyDoublingSessionModel) -> SessionMetaData:
        """Initialize meta_data with default values."""
        meta_data = SessionMetaData(participants=[str(session.user_id)], join_requests=[])
        session.meta_data = meta_data
        return meta_data

    def _ensure_meta_data(self, session: BodyDoublingSessionModel) -> SessionMetaData:
        """Ensure meta_data exists and has required fields."""
        meta_data = self._get_meta_data(session)
        if not meta_data:
            return self._init_meta_data(session)

        if "participants" not in meta_data:
            meta_data["participants"] = [str(session.user_id)]
        if "join_requests" not in meta_data:
            meta_data["join_requests"] = []

        return meta_data

    async def create_session(
        self, session_data: CreateBodyDoublingSchema
    ) -> BodyDoublingSessionModel:
        """Create a new body doubling session."""
        session = BodyDoublingSessionModel(
            user_id=session_data.user_id,
            host_id=session_data.host_id,
            session_type=session_data.session_type,
            status=session_data.status,
            start_time=session_data.start_time,
            activity_type=session_data.activity_type,
            max_participants=session_data.max_participants,
            meta_data=(
                {"participants": [str(session_data.user_id)], "join_requests": []}
                if session_data.session_type == SessionType.GROUP
                else None
            ),
        )

        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        return session

    async def get_session_participants(self, session_id: UUID) -> List[str]:
        """Get the list of participants in a session."""
        session = await self.get_by_id(session_id)
        if not session:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

        meta_data = self._get_meta_data(session)
        if not meta_data or "participants" not in meta_data:
            return [str(session.user_id)]

        return meta_data["participants"]

    async def get_session_join_requests(self, session_id: UUID) -> List[Dict[str, Any]]:
        """Get the list of join requests for a session."""
        session = await self.get_by_id(session_id)
        if not session:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

        meta_data = self._get_meta_data(session)
        if not meta_data or "join_requests" not in meta_data:
            return []

        return meta_data["join_requests"]

    async def start_session(self, session_data: Dict[str, Any]) -> BodyDoublingSessionModel:
        """Start a new body doubling session."""
        user_id = session_data.get("user_id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="UserModelSchema ID is required",
            )
        active_session = await self.get_active_session(user_id)
        if active_session and active_session.status == SessionStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="UserModelSchema already has an active session",
            )
        session_type = session_data.get("session_type", SessionType.ONE_ON_ONE)
        if session_type == SessionType.GROUP and "max_participants" not in session_data:
            session_data["max_participants"] = 5
        environment = session_data.get("environment")
        if environment is not None:
            if hasattr(environment, "model_dump"):
                session_data["environment"] = environment.model_dump()
            elif not isinstance(environment, dict):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Environment must be a dictionary",
                )
        status_value = session_data.get("status")
        if not status_value:
            status_value = (
                SessionStatus.SCHEDULED
                if not session_data.get("immediate", True)
                else SessionStatus.ACTIVE
            )
        session = BodyDoublingSessionModel(
            id=uuid4(),
            user_id=user_id,
            session_type=session_type,
            status=status_value,
            start_time=session_data["start_time"],
            duration_minutes=session_data.get("duration_minutes"),
            task_description=session_data.get("task_description"),
            goals=session_data.get("goals"),
            environment=session_data.get("environment"),
            is_virtual=session_data.get("is_virtual", True),
            notes=session_data.get("notes"),
            created_at=datetime.utcnow(),
        )
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)

    async def get_active_session(self, user_id: UUID) -> Optional[BodyDoublingSessionModel]:
        """Get the active session for a user."""
        query = select(BodyDoublingSessionModel).where(
            and_(
                BodyDoublingSessionModel.user_id == user_id,
                BodyDoublingSessionModel.status == SessionStatus.ACTIVE,
                BodyDoublingSessionModel.end_time.is_(None),
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def end_session(self, session_id: UUID, user_id: UUID) -> BodyDoublingSessionModel:
        """End a body doubling session."""
        session = await self.get_by_id(session_id)
        if not session:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
        if session.status != SessionStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Session is not active"
            )
        if session.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the host can end the session",
            )
        session.status = SessionStatus.COMPLETED
        session.end_time = datetime.utcnow()
        session.updated_at = datetime.utcnow()
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)

    async def create_group_session(self, session_data: Dict[str, Any]) -> BodyDoublingSessionModel:
        """Create a group body doubling session."""
        if "max_participants" not in session_data:
            session_data["max_participants"] = 5
        session_data["session_type"] = SessionType.GROUP
        session_data["host_id"] = session_data["user_id"]
        if "topic" in session_data:
            session_data["task_description"] = session_data["topic"]
        if "description" in session_data:
            session_data["notes"] = session_data["description"]
        meta_data = session_data.get("meta_data", {})
        meta_data["participants"] = [str(session_data["user_id"])]
        meta_data["join_requests"] = []
        session_data["meta_data"] = meta_data
        session = await self.start_session(session_data)
        if not session.meta_data:
            session.meta_data = meta_data
        else:
            session.meta_data.update(meta_data)
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)

    async def update_session_metrics(
        self, session_id: UUID, metrics: Dict[str, Any]
    ) -> BodyDoublingSessionModel:
        """Update metrics for a body doubling session."""
        session = await self.get_by_id(session_id)
        if not session:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
        metric_mapping = {
            "focus_rating": "focus_score",
            "productivity_rating": "productivity_score",
            "engagement_level": "energy_level",
            "distractions": "total_break_time",
            "achievements": "completed_tasks",
        }
        feedback_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "focus_rating": metrics.get("focus_rating"),
            "productivity_rating": metrics.get("productivity_rating"),
            "engagement_level": metrics.get("engagement_level"),
            "distractions": metrics.get("distractions"),
            "achievements": metrics.get("achievements", []),
        }
        current_feedback = session.session_feedback or []
        current_feedback.append(feedback_entry)
        session.session_feedback = current_feedback
        mapped_metrics = {}
        for key, value in metrics.items():
            if key in metric_mapping:
                mapped_metrics[metric_mapping[key]] = value
            else:
                mapped_metrics[key] = value
        valid_metrics = {
            "focus_score",
            "productivity_score",
            "task_completion_rate",
            "energy_level",
            "social_comfort_level",
            "partner_compatibility",
            "communication_quality",
            "completed_tasks",
            "total_break_time",
        }
        invalid_metrics = set(mapped_metrics.keys()) - valid_metrics
        if invalid_metrics:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid metrics: {invalid_metrics}",
            )
        for key, value in mapped_metrics.items():
            if key == "energy_level" and isinstance(value, str):
                try:
                    value = EnergyLevel(value.upper())
                except ValueError:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid energy level value",
                    )
            setattr(session, key, value)
        session.updated_at = datetime.utcnow()
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        if not session.session_feedback or len(session.session_feedback) != len(current_feedback):
            session.session_feedback = current_feedback
            self.db.add(session)
            await self.db.commit()
            await self.db.refresh(session)

    async def add_session_feedback(
        self, session_id: UUID, user_id: UUID, feedback: Dict[str, Any]
    ) -> BodyDoublingSessionModel:
        """Add feedback for a body doubling session."""
        session = await self.get_by_id(session_id)
        if not session:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
        required_fields = {"focus_level", "mood"}
        missing_fields = required_fields - set(feedback.keys())
        if missing_fields:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required fields: {missing_fields}",
            )
        feedback_entry = {
            "timestamp": feedback.get("timestamp", datetime.utcnow()).isoformat(),
            "user_id": str(user_id),
            "focus_level": feedback.get("focus_level"),
            "mood": feedback.get("mood"),
            "notes": feedback.get("notes"),
        }
        if session.session_feedback is None:
            session.session_feedback = []
        current_feedback = session.session_feedback.copy() if session.session_feedback else []
        if feedback_entry not in current_feedback:
            current_feedback.append(feedback_entry)
        session.session_feedback = current_feedback
        if "focus_level" in feedback:
            session.focus_score = feedback["focus_level"]
        session.updated_at = datetime.utcnow()
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        if not session.session_feedback or len(session.session_feedback) != len(current_feedback):
            session.session_feedback = current_feedback
            self.db.add(session)
            await self.db.commit()
            await self.db.refresh(session)

    async def get_session_feedback(self, session_id: UUID) -> SessionFeedbackSchema:
        """Get feedback for a session."""
        session = await self.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        feedback_points = session.session_feedback or []
        focus_levels = [
            point.get("focus_level", 0)
            for point in feedback_points
            if point.get("focus_level") is not None
        ]
        average_focus_level = sum(focus_levels) / len(focus_levels) if focus_levels else 0.0
        final_rating = None
        if session.status == SessionStatus.COMPLETED and session.session_rating:
            final_rating = session.session_rating
            if isinstance(final_rating, dict):
                if "overall_rating" not in final_rating and "session_rating" in final_rating:
                    final_rating["overall_rating"] = final_rating["session_rating"]
                final_rating = SimpleNamespace(**final_rating)
        return SessionFeedbackSchema(
            feedback_points=feedback_points,
            session_id=session_id,
            user_id=session.user_id,
            average_focus_level=average_focus_level,
            final_rating=final_rating,
        )

    @handle_service_error
    async def update_preferences(
        self, user_id: UUID, preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update user's body doubling preferences."""
        valid_keys = {
            "preferred_activity_types",
            "preferred_session_types",
            "preferred_times",
            "timezone",
            "language",
            "interests",
            "experience_level",
        }
        invalid_keys = set(preferences.keys()) - valid_keys
        if invalid_keys:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid preference keys: {invalid_keys}",
            )
        query = select(BodyDoublingSessionModel).where(
            and_(
                BodyDoublingSessionModel.user_id == user_id,
                BodyDoublingSessionModel.preferences.isnot(None),
            )
        )
        result = await self.db.execute(query)
        session = result.scalar_one_or_none()
        if not session:
            session = BodyDoublingSessionModel(
                user_id=user_id,
                preferences=preferences,
                status=SessionStatus.SCHEDULED,
                session_type=SessionType.ONE_ON_ONE,
                activity_type=ActivityType.OTHER,
                start_time=datetime.utcnow(),
            )
            self.db.add(session)
        else:
            session.preferences.update(preferences)
        await self.db.commit()
        await self.db.refresh(session)
        return session.preferences

    async def request_match(
        self, user_id: UUID, match_criteria: Dict[str, Any]
    ) -> BodyDoublingSessionModel:
        """Request a match for body doubling."""
        session_data = {
            "user_id": user_id,
            "session_type": match_criteria.get("session_type", SessionType.ONE_ON_ONE),
            "activity_type": match_criteria.get("activity_type", ActivityType.WORK),
            "duration_minutes": match_criteria.get("duration_minutes", 60),
            "environment": {"noise_level": "quiet", "lighting": "good"},
            "immediate": False,
            "status": SessionStatus.PENDING,
            "preferences": {},
        }
        return await self.start_session(session_data)

    def _calculate_match_score(
        self,
        user_prefs: Dict[str, Any],
        match_prefs: Dict[str, Any],
        criteria: Dict[str, Any],
    ) -> float:
        """Calculate match score between two users."""
        score = 0.0
        if criteria.get("activity_type") in user_prefs.get(
            "preferred_activity_types", []
        ) and criteria.get("activity_type") in match_prefs.get("preferred_activity_types", []):
            score += 0.3
        if criteria.get("session_type") in user_prefs.get(
            "preferred_session_types", []
        ) and criteria.get("session_type") in match_prefs.get("preferred_session_types", []):
            score += 0.2
        if set(user_prefs.get("preferred_times", [])) & set(match_prefs.get("preferred_times", [])):
            score += 0.2
        if user_prefs.get("language") == match_prefs.get("language"):
            score += 0.1
        common_interests = set(user_prefs.get("interests", [])) & set(
            match_prefs.get("interests", [])
        )
        score += len(common_interests) * 0.1
        return min(1.0, score)

    async def request_join_group(
        self, user_id: UUID, session_id: UUID, join_request: Dict[str, Any]
    ) -> BodyDoublingSessionModel:
        """Request to join a group session."""
        session = await self.get_by_id(session_id)
        if not session:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
        if session.session_type != SessionType.GROUP:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Session is not a group session",
            )
        if session.status not in {SessionStatus.ACTIVE, SessionStatus.SCHEDULED}:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Session is not accepting join requests",
            )

        # Initialize meta_data if not present
        meta_data = self._ensure_meta_data(session)

        current_participants = meta_data["participants"]
        if str(user_id) in current_participants:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already in the session",
            )

        if len(current_participants) >= session.max_participants:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Session is full")

        request_id = uuid4()
        join_request_entry = {
            "id": str(request_id),
            "user_id": str(user_id),
            "timestamp": datetime.utcnow().isoformat(),
            "message": join_request.get("message"),
            "status": "pending",
        }
        meta_data["join_requests"].append(join_request_entry)

        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)

        request_session = BodyDoublingSessionModel(
            id=request_id,
            user_id=user_id,
            host_id=session.host_id,
            session_type=SessionType.GROUP,
            status=SessionStatus.PENDING,
            start_time=datetime.utcnow(),
            activity_type=session.activity_type,
            meta_data={"original_session_id": str(session_id)},
        )
        self.db.add(request_session)
        await self.db.commit()
        await self.db.refresh(request_session)
        return request_session

    async def accept_join_request(
        self, session_id: UUID, request_id: str
    ) -> BodyDoublingSessionModel:
        """Accept a join request for a group session."""
        session = await self.get_by_id(session_id)
        if not session:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

        meta_data = self._ensure_meta_data(session)

        join_request = None
        for req in meta_data["join_requests"]:
            if req["id"] == request_id:
                join_request = req
                break

        if not join_request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Join request not found"
            )

        if join_request["status"] != "pending":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Join request is not pending",
            )

        join_request["status"] = "accepted"
        if str(join_request["user_id"]) not in meta_data["participants"]:
            meta_data["participants"].append(str(join_request["user_id"]))

        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)

        return session

    async def reject_join_request(
        self, session_id: UUID, request_id: str
    ) -> BodyDoublingSessionModel:
        """Reject a join request for a group session."""
        session = await self.get_by_id(session_id)
        if not session:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

        meta_data = self._ensure_meta_data(session)

        join_request = None
        for req in meta_data["join_requests"]:
            if req["id"] == request_id:
                join_request = req
                break

        if not join_request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Join request not found"
            )

        if join_request["status"] != "pending":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Join request is not pending",
            )

        join_request["status"] = "rejected"

        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)

        return session

    async def get_user_analytics(self, user_id: UUID) -> SessionAnalyticsSchema:
        """Get analytics for a user's sessions."""
        sessions = await self.get_user_sessions(user_id)
        if not sessions:
            return SessionFeedbackSchema(
                total_sessions=0,
                total_focus_time=0,
                average_productivity=0.0,
                productivity_trend="stable",
                distraction_trend="stable",
                completion_rate=0.0,
                most_productive_times=[],
                preferred_activity_types=[],
                preferred_session_types=[],
                session_stats={},
                average_duration=0.0,
                average_focus_rating=0.0,
                average_productivity_rating=0.0,
            )
        total_sessions = len(sessions)
        total_focus_time = 0
        total_duration = 0
        productivity_ratings = []
        focus_ratings = []
        session_type_counts = {
            SessionType.ONE_ON_ONE: 0,
            SessionType.GROUP: 0,
            SessionType.ASYNC: 0,
        }
        hourly_productivity = {}
        completed_sessions = 0
        for session in sessions:
            session_type_counts[session.session_type] = (
                session_type_counts.get(session.session_type, 0) + 1
            )
            if session.status == SessionStatus.COMPLETED:
                completed_sessions += 1
            if session.end_time and session.start_time:
                duration = (session.end_time - session.start_time).total_seconds() / 60
                break_time = session.total_break_time or 0
                total_focus_time += max(0, duration - break_time)
                total_duration += duration
                if session.session_feedback:
                    for feedback in session.session_feedback:
                        if isinstance(feedback, dict):
                            focus = feedback.get("focus_rating")
                            productivity = feedback.get("productivity_rating")
                            if focus is not None:
                                focus_ratings.append(float(focus))
                            if productivity is not None:
                                productivity_ratings.append(float(productivity))
                                hour = session.start_time.hour
                                if hour not in hourly_productivity:
                                    hourly_productivity[hour] = []
                                hourly_productivity[hour].append(float(productivity))
        average_duration = total_duration / total_sessions if total_sessions > 0 else 0.0
        average_focus_rating = sum(focus_ratings) / len(focus_ratings) if focus_ratings else 0.0
        average_productivity_rating = (
            sum(productivity_ratings) / len(productivity_ratings) if productivity_ratings else 0.0
        )
        completion_rate = completed_sessions / total_sessions * 100 if total_sessions > 0 else 0.0
        threshold = total_sessions * 0.2
        preferred_session_types = [
            session_type.value
            for session_type, count in session_type_counts.items()
            if count >= threshold
        ]
        most_productive_times = []
        PRODUCTIVITY_THRESHOLD = 5.0
        if hourly_productivity:
            for hour, ratings in hourly_productivity.items():
                hour_avg = sum(ratings) / len(ratings)
                if hour_avg >= PRODUCTIVITY_THRESHOLD:
                    most_productive_times.append(hour)
        most_productive_times.sort()
        return SessionAnalyticsSchema(
            total_sessions=total_sessions,
            total_focus_time=total_focus_time,
            average_productivity=average_productivity_rating,
            productivity_trend="stable",
            distraction_trend="stable",
            completion_rate=completion_rate,
            most_productive_times=most_productive_times,
            preferred_activity_types=[],
            preferred_session_types=preferred_session_types,
            session_stats={
                "one_on_one": session_type_counts[SessionType.ONE_ON_ONE],
                "group": session_type_counts[SessionType.GROUP],
                "async": session_type_counts[SessionType.ASYNC],
            },
            average_duration=average_duration,
            average_focus_rating=average_focus_rating,
            average_productivity_rating=average_productivity_rating,
        )

    async def accept_match(self, partner_id: UUID, request_id: UUID) -> BodyDoublingSessionModel:
        """Accept a match request."""
        request_session = await self.get_by_id(request_id)
        if not request_session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Match request not found"
            )
        if request_session.status != SessionStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Match request is not pending",
            )
        request_session.status = SessionStatus.ACTIVE
        request_session.partner_id = partner_id
        request_session.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(request_session)

    async def get_group_session_info(self, session_id: UUID) -> GroupSessionSchema:
        """Get detailed information about a group session."""
        session = await self.get_by_id(session_id)
        if not session:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
        if session.session_type != SessionType.GROUP:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Not a group session"
            )

        # Initialize meta_data if not present
        meta_data = self._ensure_meta_data(session)

        current_participants = meta_data["participants"]
        current_join_requests = meta_data["join_requests"]
        pending_requests = [
            request for request in current_join_requests if request.get("status") == "pending"
        ]

        if str(session.user_id) not in current_participants:
            current_participants.append(str(session.user_id))

            return GroupSessionSchema(
            session_id=str(session.id),
            host_id=str(session.host_id),
            topic=session.task_description,
            description=session.notes,
            status=session.status,
            start_time=session.start_time,
            end_time=session.end_time,
            max_participants=session.max_participants or 5,
            current_participants=current_participants,
            pending_requests=pending_requests,
            environment=session.environment,
            activity_type=session.activity_type,
            duration_minutes=session.planned_duration,
        )

    async def get_session(self, session_id: UUID) -> Optional[BodyDoublingSessionModel]:
        """Get a session by ID."""
        query = select(BodyDoublingSessionModel).where(BodyDoublingSessionModel.id == session_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_user_sessions(self, user_id: UUID) -> List[BodyDoublingSessionModel]:
        """Get all completed sessions for a user."""
        query = (
            select(BodyDoublingSessionModel)
            .where(
                and_(
                    BodyDoublingSessionModel.user_id == user_id,
                    BodyDoublingSessionModel.status == SessionStatus.COMPLETED,
                    BodyDoublingSessionModel.end_time.isnot(None),
                )
            )
            .order_by(BodyDoublingSessionModel.end_time.desc())
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    def calculate_average_productivity(self, sessions: List[BodyDoublingSessionModel]) -> float:
        """Calculate average productivity from session feedback."""
        productivity_ratings = []
        for session in sessions:
            if session.session_feedback:
                for feedback in session.session_feedback:
                    if feedback.get("productivity_rating") is not None:
                        productivity_ratings.append(feedback["productivity_rating"])
        return (
            sum(productivity_ratings) / len(productivity_ratings) if productivity_ratings else 0.0
        )

    def calculate_trend(self, values: List[float]) -> str:
        """Calculate trend from a list of values."""
        if not values or len(values) < 2:
            return "stable"
        if all((values[i] <= values[i + 1] for i in range(len(values) - 1))):
            return "improving"
        elif all((values[i] >= values[i + 1] for i in range(len(values) - 1))):
            return "declining"
        return "stable"

    def calculate_distraction_trend(self, sessions: List[BodyDoublingSessionModel]) -> str:
        """Calculate trend in distractions."""
        distraction_counts = []
        for session in sessions:
            if session.session_feedback:
                session_distractions = 0
                for feedback in session.session_feedback:
                    if feedback.get("distractions") is not None:
                        session_distractions += feedback["distractions"]
                distraction_counts.append(session_distractions)
        return self.calculate_trend(distraction_counts)

    def calculate_completion_rate(self, sessions: List[BodyDoublingSessionModel]) -> float:
        """Calculate task completion rate."""
        completed_tasks = 0
        total_tasks = 0
        for session in sessions:
            if session.session_feedback:
                for feedback in session.session_feedback:
                    if feedback.get("achievements"):
                        completed_tasks += len(feedback["achievements"])
                    if feedback.get("goals"):
                        total_tasks += len(feedback["goals"])
        return completed_tasks / total_tasks if total_tasks > 0 else 0.0

    def calculate_most_productive_time(
        self, sessions: List[BodyDoublingSessionModel]
    ) -> Optional[int]:
        """Calculate most productive time of day."""
        time_productivity = {}
        for session in sessions:
            if session.start_time and session.session_feedback:
                hour = session.start_time.hour
                for feedback in session.session_feedback:
                    if feedback.get("productivity_rating") is not None:
                        if hour not in time_productivity:
                            time_productivity[hour] = []
                        time_productivity[hour].append(feedback["productivity_rating"])
        if not time_productivity:
            return None
        best_hour = max(
            time_productivity.keys(),
            key=lambda h: sum(time_productivity[h]) / len(time_productivity[h]),
        )

    def calculate_preferred_activities(self, sessions: List[BodyDoublingSessionModel]) -> List[str]:
        """Calculate preferred activity types."""
        activity_counts = {}
        for session in sessions:
            if session.activity_type:
                activity_counts[session.activity_type] = (
                    activity_counts.get(session.activity_type, 0) + 1
                )
        return sorted(activity_counts.keys(), key=lambda x: activity_counts[x], reverse=True)

    def calculate_session_type_stats(
        self, sessions: List[BodyDoublingSessionModel]
    ) -> Dict[str, int]:
        """Calculate statistics for different session types."""
        return {
            "one_on_one": sum((1 for s in sessions if s.session_type == SessionType.ONE_ON_ONE)),
            "group": sum((1 for s in sessions if s.session_type == SessionType.GROUP)),
            "async": sum((1 for s in sessions if s.session_type == SessionType.ASYNC)),
        }

    async def get_active_sessions(self) -> List[BodyDoublingSessionModel]:
        """Get all active body doubling sessions."""
        query = select(BodyDoublingSessionModel).where(
            BodyDoublingSessionModel.status == SessionStatus.ACTIVE
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def join_session(self, session_id: UUID, user_id: UUID) -> BodyDoublingSessionModel:
        """Join an existing body doubling session."""
        session = await self.get_by_id(session_id)
        if not session:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
        if session.status != SessionStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Session is not active"
            )
        active_session = await self.get_active_session(user_id)
        if active_session:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already in an active session",
            )

        # Initialize meta_data if needed
        meta_data = self._ensure_meta_data(session)

        if session.session_type == SessionType.GROUP:
            current_participants = meta_data["participants"]
            max_participants = session.max_participants or 5
            if len(current_participants) >= max_participants:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Session has reached maximum participants",
                )
            if str(user_id) not in current_participants:
                current_participants.append(str(user_id))
        else:
            if session.partner_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Session already has a partner",
                )
            session.partner_id = user_id

        session.updated_at = datetime.utcnow()
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        return session

    async def leave_session(self, session_id: UUID, user_id: UUID) -> BodyDoublingSessionModel:
        """Leave a body doubling session."""
        session = await self.get_by_id(session_id)
        if not session:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
        if session.status != SessionStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Session is not active"
            )

        # Initialize meta_data if needed
        meta_data = self._ensure_meta_data(session)

        if session.session_type == SessionType.GROUP:
            current_participants = meta_data["participants"]
            if str(user_id) not in current_participants:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User is not in this session",
                )
            current_participants.remove(str(user_id))
            if not current_participants:
                session.status = SessionStatus.COMPLETED
                session.end_time = datetime.utcnow()
        else:
            if session.partner_id != user_id and session.user_id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User is not in this session",
                )
            if session.partner_id == user_id:
                session.partner_id = None
            elif session.user_id == user_id:
                session.status = SessionStatus.COMPLETED
                session.end_time = datetime.utcnow()

        session.updated_at = datetime.utcnow()
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        return session

    async def end_session(self, session_id: UUID, user_id: UUID) -> BodyDoublingSessionModel:
        """End a body doubling session."""
        session = await self.get_by_id(session_id)
        if not session:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
        if session.status != SessionStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Session is not active"
            )
        if session.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the host can end the session",
            )
        session.status = SessionStatus.COMPLETED
        session.end_time = datetime.utcnow()
        session.updated_at = datetime.utcnow()
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
