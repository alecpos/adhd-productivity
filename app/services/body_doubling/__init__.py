"""Body Doubling Service components.

This package contains all components related to the Body Doubling Service,
which enables users to work together in virtual sessions to improve focus.
"""

from app.services.body_doubling.analytics_service import AnalyticsService
from app.services.body_doubling.body_doubling_service import BodyDoublingService
from app.services.body_doubling.matching_engine import MatchingEngine
from app.services.body_doubling.notification_service import NotificationService
from app.services.body_doubling.session_manager import SessionManager
from app.services.body_doubling.body_doubling_types import (
    MatchCriteria,
    MatchResult,
    SessionParticipant,
    SessionStats,
)

__all__ = [
    "AnalyticsService",
    "BodyDoublingService",
    "MatchingEngine",
    "NotificationService",
    "SessionManager",
    "MatchCriteria",
    "MatchResult",
    "SessionParticipant",
    "SessionStats",
]
