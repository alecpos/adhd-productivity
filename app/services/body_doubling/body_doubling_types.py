"""Shared types for body doubling services."""

import json
from datetime import datetime
from typing import Any, Dict, List, NamedTuple, Optional, TypedDict
from uuid import UUID


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


class SessionAnalyticsData(NamedTuple):
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


class SessionFeedbackData(NamedTuple):
    """Feedback for a body doubling session."""

    feedback_points: List[Dict[str, Any]]
    session_id: UUID
    user_id: UUID
    average_focus_level: float
    final_rating: Optional[Dict[str, Any]]


class GroupSessionInfo(NamedTuple):
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


class MatchCriteria(NamedTuple):
    """Criteria for matching users in body doubling sessions."""

    activity_type: Optional[str] = None
    session_type: Optional[str] = None
    min_duration: Optional[int] = None
    max_duration: Optional[int] = None
    preferred_participants: Optional[List[str]] = None
    excluded_participants: Optional[List[str]] = None
    timezone_preference: Optional[str] = None
    skill_level: Optional[str] = None


class MatchResult(NamedTuple):
    """Result of a matching operation for body doubling sessions."""

    success: bool
    session_id: Optional[str] = None
    matched_user_ids: List[str] = []
    score: float = 0.0
    match_details: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


class SessionParticipant(NamedTuple):
    """Information about a participant in a body doubling session."""

    user_id: str
    join_time: datetime
    leave_time: Optional[datetime] = None
    status: str = "active"
    feedback_provided: bool = False
    role: str = "participant"
    activity_type: Optional[str] = None


class SessionStats(NamedTuple):
    """Statistics for body doubling sessions."""

    total_sessions: int
    active_sessions: int
    completed_sessions: int
    cancelled_sessions: int
    avg_participants: float
    avg_duration: float
    most_popular_time: Optional[str] = None
    most_popular_activity: Optional[str] = None
    total_focus_hours: float = 0.0
    user_participation: Dict[str, int] = {}
