"""Notification service component for body doubling service."""

from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.body_doubling_model import BodyDoublingSessionModel
from app.models.enums_model import SessionStatus
from app.services.body_doubling.session_manager import SessionManager


class NotificationService:
    """Handles notifications for body doubling sessions."""

    def __init__(self, session_manager: SessionManager):
        """Initialize the notification service with session manager."""
        self.session_manager = session_manager
        self.db = session_manager.db

    async def notify_session_invitation(
        self, user_id: UUID, session_id: UUID, data: Dict[str, Any]
    ) -> bool:
        """Send a notification for a session invitation."""
        # This would connect to a notification service in a real implementation
        # For now, we'll just log and return success
        print(f"Notification: User {user_id} invited to session {session_id}")
        return True

    async def notify_session_join(
        self, session_id: UUID, user_id: UUID, is_host: bool = False
    ) -> bool:
        """Send a notification that a user has joined the session."""
        if is_host:
            print(f"Notification: Host {user_id} started session {session_id}")
        else:
            print(f"Notification: User {user_id} joined session {session_id}")
        return True

    async def notify_session_leave(
        self, session_id: UUID, user_id: UUID, is_host: bool = False
    ) -> bool:
        """Send a notification that a user has left the session."""
        if is_host:
            print(f"Notification: Host {user_id} ended session {session_id}")
        else:
            print(f"Notification: User {user_id} left session {session_id}")
        return True

    async def notify_session_status_change(
        self, session_id: UUID, new_status: SessionStatus
    ) -> bool:
        """Send a notification that a session's status has changed."""
        status_message = {
            SessionStatus.PENDING: "is pending",
            SessionStatus.ACTIVE: "has started",
            SessionStatus.COMPLETED: "has ended",
            SessionStatus.CANCELLED: "has been cancelled",
        }.get(new_status, "has changed status")

        print(f"Notification: Session {session_id} {status_message}")
        return True

    async def notify_join_request(
        self, session_id: UUID, host_id: UUID, requester_id: UUID
    ) -> bool:
        """Send a notification about a join request."""
        print(f"Notification: User {requester_id} requested to join session {session_id} (host: {host_id})")
        return True

    async def notify_join_request_response(
        self, session_id: UUID, user_id: UUID, accepted: bool
    ) -> bool:
        """Send a notification about a join request response."""
        status = "accepted" if accepted else "rejected"
        print(f"Notification: Your request to join session {session_id} was {status}")
        return True

    async def notify_session_reminder(
        self, user_id: UUID, session_id: UUID, minutes_until: int
    ) -> bool:
        """Send a reminder notification about an upcoming session."""
        print(f"Notification: Reminder - your session {session_id} starts in {minutes_until} minutes")
        return True

    async def send_match_suggestion(
        self, user_id: UUID, match_id: UUID, score: float, data: Dict[str, Any]
    ) -> bool:
        """Send a notification about a potential session match."""
        print(f"Notification: Found matching partner {match_id} for user {user_id} (score: {score})")
        return True

    async def send_session_feedback_request(self, user_id: UUID, session_id: UUID) -> bool:
        """Send a request for session feedback."""
        print(f"Notification: Please provide feedback for your session {session_id}")
        return True
