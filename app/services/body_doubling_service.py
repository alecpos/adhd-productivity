"""Body doubling service facade.

This module provides backward compatibility with the original BodyDoublingService.
"""

from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.body_doubling_model import BodyDoublingSessionModel
from app.schemas.body_doubling_schema import (
    BodyDoublingSchema,
    CreateBodyDoublingSchema,
    GroupSessionSchema,
    SessionAnalyticsSchema,
    SessionFeedbackSchema,
)
from app.services.body_doubling.body_doubling_service import BodyDoublingService


# For backward compatibility
async def create_session(
    db: AsyncSession, session_data: CreateBodyDoublingSchema
) -> BodyDoublingSessionModel:
    """Create a new body doubling session."""
    service = BodyDoublingService(db)
    return await service.create_session(session_data)


async def get_session(db: AsyncSession, session_id: UUID) -> Optional[BodyDoublingSessionModel]:
    """Get a session by ID."""
    service = BodyDoublingService(db)
    return await service.get_session(session_id)


async def get_session_participants(db: AsyncSession, session_id: UUID) -> List[str]:
    """Get the list of participants in a session."""
    service = BodyDoublingService(db)
    return await service.get_session_participants(session_id)


async def get_session_join_requests(db: AsyncSession, session_id: UUID) -> List[Dict[str, Any]]:
    """Get the list of join requests for a session."""
    service = BodyDoublingService(db)
    return await service.get_session_join_requests(session_id)


async def get_active_session(
    db: AsyncSession, user_id: UUID
) -> Optional[BodyDoublingSessionModel]:
    """Get the active session for a user."""
    service = BodyDoublingService(db)
    return await service.get_active_session(user_id)


async def join_session(
    db: AsyncSession, session_id: UUID, user_id: UUID
) -> BodyDoublingSessionModel:
    """Join a body doubling session."""
    service = BodyDoublingService(db)
    return await service.join_session(session_id, user_id)


async def leave_session(
    db: AsyncSession, session_id: UUID, user_id: UUID
) -> BodyDoublingSessionModel:
    """Leave a body doubling session."""
    service = BodyDoublingService(db)
    return await service.leave_session(session_id, user_id)


async def end_session(
    db: AsyncSession, session_id: UUID, user_id: UUID
) -> BodyDoublingSessionModel:
    """End a body doubling session."""
    service = BodyDoublingService(db)
    return await service.end_session(session_id, user_id)


async def get_user_sessions(
    db: AsyncSession, user_id: UUID
) -> List[BodyDoublingSessionModel]:
    """Get all sessions for a user."""
    service = BodyDoublingService(db)
    return await service.get_user_sessions(user_id)


async def get_active_sessions(db: AsyncSession) -> List[BodyDoublingSessionModel]:
    """Get all active sessions."""
    service = BodyDoublingService(db)
    return await service.get_active_sessions()


async def find_matching_users(
    db: AsyncSession, user_id: UUID, user_prefs: Dict[str, Any], criteria: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """Find users matching the given criteria."""
    service = BodyDoublingService(db)
    return await service.find_matching_users(user_id, user_prefs, criteria)


async def request_match(
    db: AsyncSession, user_id: UUID, match_criteria: Dict[str, Any]
) -> BodyDoublingSessionModel:
    """Create a session request for matching."""
    service = BodyDoublingService(db)
    return await service.request_match(user_id, match_criteria)


async def accept_match(
    db: AsyncSession, partner_id: UUID, request_id: UUID
) -> BodyDoublingSessionModel:
    """Accept a match request and create a paired session."""
    service = BodyDoublingService(db)
    return await service.accept_match(partner_id, request_id)


async def get_user_analytics(db: AsyncSession, user_id: UUID) -> SessionAnalyticsSchema:
    """Get analytics for a user's body doubling sessions."""
    service = BodyDoublingService(db)
    return await service.get_user_analytics(user_id)


async def create_group_session(
    db: AsyncSession, session_data: Dict[str, Any]
) -> BodyDoublingSessionModel:
    """Create a new group session."""
    service = BodyDoublingService(db)
    return await service.create_group_session(session_data)


async def get_group_session_info(db: AsyncSession, session_id: UUID) -> GroupSessionSchema:
    """Get information about a group session."""
    service = BodyDoublingService(db)
    return await service.get_group_session_info(session_id)


async def request_join_group(
    db: AsyncSession, user_id: UUID, session_id: UUID, join_request: Dict[str, Any]
) -> BodyDoublingSessionModel:
    """Request to join a group session."""
    service = BodyDoublingService(db)
    return await service.request_join_group(user_id, session_id, join_request)


async def accept_join_request(
    db: AsyncSession, session_id: UUID, request_id: str
) -> BodyDoublingSessionModel:
    """Accept a request to join a group session."""
    service = BodyDoublingService(db)
    return await service.accept_join_request(session_id, request_id)


async def reject_join_request(
    db: AsyncSession, session_id: UUID, request_id: str
) -> BodyDoublingSessionModel:
    """Reject a request to join a group session."""
    service = BodyDoublingService(db)
    return await service.reject_join_request(session_id, request_id)


async def add_session_feedback(
    db: AsyncSession, session_id: UUID, user_id: UUID, feedback: Dict[str, Any]
) -> BodyDoublingSessionModel:
    """Add feedback for a session."""
    service = BodyDoublingService(db)
    return await service.add_session_feedback(session_id, user_id, feedback)


async def get_session_feedback(db: AsyncSession, session_id: UUID) -> SessionFeedbackSchema:
    """Get feedback for a session."""
    service = BodyDoublingService(db)
    return await service.get_session_feedback(session_id)


async def update_preferences(
    db: AsyncSession, user_id: UUID, preferences: Dict[str, Any]
) -> Dict[str, Any]:
    """Update user preferences for body doubling."""
    service = BodyDoublingService(db)
    return await service.update_preferences(user_id, preferences)


async def update_session_metrics(
    db: AsyncSession, session_id: UUID, metrics: Dict[str, Any]
) -> BodyDoublingSessionModel:
    """Update metrics for a session."""
    service = BodyDoublingService(db)
    return await service.update_session_metrics(session_id, metrics)
