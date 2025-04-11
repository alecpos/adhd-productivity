"""Body doubling service module."""

from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID
from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.body_doubling_model import BodyDoublingSessionModel
from app.models.enums_model import SessionStatus, SessionType
from app.schemas.body_doubling_schema import (
    BodyDoublingSchema,
    CreateBodyDoublingSchema,
    GroupSessionSchema,
    SessionAnalyticsSchema,
    SessionFeedbackSchema,
)
from app.services.base_service import BaseService
from app.services.body_doubling.analytics_service import AnalyticsService
from app.services.body_doubling.matching_engine import MatchingEngine
from app.services.body_doubling.notification_service import NotificationService
from app.services.body_doubling.session_manager import SessionManager
from app.services.body_doubling.body_doubling_types import (
    MatchCriteria,
    MatchResult,
    SessionParticipant,
    SessionStats,
    GroupSessionInfo,
    SessionFeedbackData,
)
from app.utils.error_handler import handle_service_error


class BodyDoublingService(BaseService[BodyDoublingSessionModel, BodyDoublingSchema, CreateBodyDoublingSchema]):
    """Service for managing body doubling sessions."""

    def __init__(
        self,
        session_manager: SessionManager,
        matching_engine: MatchingEngine,
        analytics_service: AnalyticsService,
        notification_service: NotificationService,
    ):
        """Initialize the service with required dependencies."""
        super().__init__(db=session_manager.db, model=BodyDoublingSessionModel, schema_class=BodyDoublingSchema)
        self.session_manager = session_manager
        self.matching_engine = matching_engine
        self.analytics_service = analytics_service
        self.notification_service = notification_service

    # Session Management Methods (delegated to SessionManager)

    async def create_session(
        self, session_data: CreateBodyDoublingSchema
    ) -> BodyDoublingSessionModel:
        """Create a new body doubling session."""
        session = await self.session_manager.create_session(session_data)
        
        # Send notifications
        await self.notification_service.notify_session_join(
            session.id, session.user_id, is_host=True
        )
        
        return session

    async def get_session(self, session_id: UUID) -> Optional[BodyDoublingSessionModel]:
        """Get a session by ID.
        
        Args:
            session_id: The UUID of the session to retrieve
            
        Returns:
            The session model if found, or None if not found
        """
        return await self.session_manager.get_session_by_id(session_id)

    async def get_user_sessions(self, user_id: UUID) -> List[BodyDoublingSessionModel]:
        """Get all sessions for a user.
        
        Args:
            user_id: The UUID of the user to get sessions for
            
        Returns:
            List of session models associated with the user
        """
        return await self.session_manager.get_user_sessions(user_id)

    async def get_active_sessions(self) -> List[BodyDoublingSessionModel]:
        """Get all active sessions.
        
        Returns:
            List of active session models
        """
        return await self.session_manager.get_active_sessions()

    async def get_session_participants(self, session_id: UUID) -> List[str]:
        """Get the list of participants in a session.
        
        Args:
            session_id: The UUID of the session to get participants for
            
        Returns:
            List of participant user IDs as strings
            
        Raises:
            HTTPException: If the session is not found
        """
        # First verify the session exists
        await self._get_session_or_404(session_id)
        
        # Then get the participant list
        return await self.session_manager.get_session_participants(session_id)

    async def get_session_join_requests(self, session_id: UUID) -> List[Dict[str, Any]]:
        """Get the list of join requests for a session.
        
        Args:
            session_id: The UUID of the session to get join requests for
            
        Returns:
            List of join request dictionaries
            
        Raises:
            HTTPException: If the session is not found
        """
        # First verify the session exists
        await self._get_session_or_404(session_id)
        
        # Then get the join requests
        return await self.session_manager.get_session_join_requests(session_id)

    async def get_active_session(self, user_id: UUID) -> Optional[BodyDoublingSessionModel]:
        """Get the active session for a user.
        
        Args:
            user_id: The UUID of the user to get the active session for
            
        Returns:
            The active session model if found, or None if not found
        """
        return await self.session_manager.get_active_session(user_id)

    async def join_session(self, session_id: UUID, user_id: UUID) -> BodyDoublingSessionModel:
        """Join a body doubling session.
        
        Args:
            session_id: The UUID of the session to join
            user_id: The UUID of the user joining the session
            
        Returns:
            The updated session model after joining
            
        Raises:
            HTTPException: If the session is not found or the user cannot join
        """
        try:
            # Join the session through the session manager
            session = await self.session_manager.join_session(session_id, user_id)
            
            # Send join notification
            await self.notification_service.notify_session_join(session_id, user_id)
            
            return session
            
        except Exception as e:
            # Handle specific error cases with appropriate status codes
            if "not found" in str(e).lower():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Session not found: {str(e)}"
                )
            elif "already" in str(e).lower():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Cannot join session: {str(e)}"
                )
            else:
                # Re-raise unhandled exceptions
                raise

    async def leave_session(self, session_id: UUID, user_id: UUID) -> BodyDoublingSessionModel:
        """Leave a body doubling session.
        
        Args:
            session_id: The UUID of the session to leave
            user_id: The UUID of the user leaving the session
            
        Returns:
            The updated session model after leaving
            
        Raises:
            HTTPException: If the session is not found or the user cannot leave
        """
        try:
            # Leave the session through the session manager
            session = await self.session_manager.leave_session(session_id, user_id)
            
            # Check if the user is the host
            is_host = str(session.host_id) == str(user_id)
            
            # Send leave notification
            await self.notification_service.notify_session_leave(
                session_id, user_id, is_host=is_host
            )
            
            return session
            
        except Exception as e:
            # Handle specific error cases with appropriate status codes
            if "not found" in str(e).lower():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Session not found: {str(e)}"
                )
            elif "not a participant" in str(e).lower():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Cannot leave session: {str(e)}"
                )
            else:
                # Re-raise unhandled exceptions
                raise

    async def end_session(self, session_id: UUID, user_id: UUID) -> BodyDoublingSessionModel:
        """End a body doubling session.
        
        Args:
            session_id: The UUID of the session to end
            user_id: The UUID of the user ending the session
            
        Returns:
            The updated session model after ending
            
        Raises:
            HTTPException: If the session is not found or cannot be ended
        """
        try:
            # End the session through the session manager
            session = await self.session_manager.end_session(session_id, user_id)
            
            # Send session completion notification
            await self.notification_service.notify_session_status_change(
                session_id, SessionStatus.COMPLETED
            )
            
            # Request feedback from all participants
            await self._request_feedback_from_participants(session)
            
            return session
            
        except Exception as e:
            # Handle specific error cases with appropriate status codes
            if "not found" in str(e).lower():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Session not found: {str(e)}"
                )
            elif "permission" in str(e).lower() or "not authorized" in str(e).lower():
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Cannot end session: {str(e)}"
                )
            else:
                # Re-raise unhandled exceptions
                raise
                
    async def _request_feedback_from_participants(self, session: BodyDoublingSessionModel) -> None:
        """Request feedback from all session participants.
        
        Args:
            session: The session model to request feedback for
        """
        # Get the list of participants from metadata
        meta_data = session.meta_data or {}
        participants = meta_data.get("participants", [str(session.user_id)])
        
        # Send feedback request to each participant
        for participant_id in participants:
            await self.notification_service.send_session_feedback_request(
                UUID(participant_id), session.id
            )

    # Matching Methods (delegated to MatchingEngine)

    async def find_matching_users(
        self, user_id: UUID, user_prefs: Dict[str, Any], criteria: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Find users matching the given criteria.
        
        Args:
            user_id: The UUID of the user seeking matches
            user_prefs: Dictionary of user preferences to consider in matching
            criteria: Dictionary of additional matching criteria
            
        Returns:
            List of dictionaries containing matching user information with scores
        """
        return await self.matching_engine.find_matching_users(user_id, user_prefs, criteria)

    async def request_match(
        self, user_id: UUID, match_criteria: Dict[str, Any]
    ) -> BodyDoublingSessionModel:
        """Create a session request for matching.
        
        Args:
            user_id: The UUID of the user requesting a match
            match_criteria: Dictionary of criteria for finding matches
            
        Returns:
            The created session model
            
        Raises:
            HTTPException: If the match request could not be created
        """
        # Create a pending session for matching
        session = await self.matching_engine.request_match(user_id, match_criteria)
        
        # Extract user preferences from match criteria
        user_prefs = match_criteria.get("preferences", {})
        
        # Find suitable matches for the user
        matches = await self._find_and_notify_matches(user_id, user_prefs, match_criteria, session)
        
        return session
        
    async def _find_and_notify_matches(
        self, 
        user_id: UUID, 
        user_prefs: Dict[str, Any], 
        match_criteria: Dict[str, Any],
        session: BodyDoublingSessionModel
    ) -> List[Dict[str, Any]]:
        """Find matching users and notify them of the match opportunity.
        
        Args:
            user_id: The UUID of the user seeking matches
            user_prefs: Dictionary of user preferences to consider in matching
            match_criteria: Dictionary of additional matching criteria
            session: The session model created for matching
            
        Returns:
            List of matching users that were notified
        """
        # Find potential matches based on criteria
        matches = await self.find_matching_users(user_id, user_prefs, match_criteria)
        
        # Limit to top 3 matches to avoid overwhelming users
        top_matches = matches[:3] if matches else []
        
        # Notify each potential match
        for match in top_matches:
            await self._send_match_suggestion(
                match_user_id=UUID(match["user_id"]),
                requester_id=user_id,
                match_score=match["score"],
                session_id=session.id,
                activity_type=match.get("activity_type")
            )
            
        return top_matches
        
    async def _send_match_suggestion(
        self,
        match_user_id: UUID,
        requester_id: UUID,
        match_score: float,
        session_id: UUID,
        activity_type: Optional[str] = None
    ) -> None:
        """Send a match suggestion notification to a potential matching user.
        
        Args:
            match_user_id: The UUID of the user to notify
            requester_id: The UUID of the user who requested the match
            match_score: The compatibility score between the users
            session_id: The UUID of the session for matching
            activity_type: Optional activity type for the session
        """
        context = {
            "session_id": str(session_id),
            "activity_type": activity_type,
        }
        
        await self.notification_service.send_match_suggestion(
            match_user_id, requester_id, match_score, context
        )

    async def accept_match(
        self, partner_id: UUID, request_id: UUID
    ) -> BodyDoublingSessionModel:
        """Accept a match request and create a paired session.
        
        Args:
            partner_id: The UUID of the partner accepting the match
            request_id: The UUID of the match request to accept
            
        Returns:
            The updated session model after acceptance
            
        Raises:
            HTTPException: If the match request could not be accepted
        """
        # Accept the match through the matching engine
        session = await self.matching_engine.accept_match(partner_id, request_id)
        
        # Send session activation and join notifications
        await self._send_match_acceptance_notifications(session, partner_id)
        
        return session
        
    async def _send_match_acceptance_notifications(
        self, session: BodyDoublingSessionModel, partner_id: UUID
    ) -> None:
        """Send notifications when a match is accepted.
        
        Args:
            session: The session model for the match
            partner_id: The UUID of the partner who accepted the match
        """
        # Notify all participants about the session status change
        await self.notification_service.notify_session_status_change(
            session.id, SessionStatus.ACTIVE
        )
        
        # Notify about the partner joining the session
        await self.notification_service.notify_session_join(
            session.id, partner_id
        )

    # Analytics Methods (delegated to AnalyticsService)

    async def _get_session_or_404(self, session_id: UUID) -> BodyDoublingSessionModel:
        """Get a session by ID or raise a 404 error.
        
        Args:
            session_id: The UUID of the session to retrieve
            
        Returns:
            The session model if found
            
        Raises:
            HTTPException: If the session is not found
        """
        session = await self.session_manager.get_session_by_id(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Session not found"
            )
        return session
    
    async def get_user_analytics(self, user_id: UUID) -> SessionAnalyticsSchema:
        """Get analytics for a user's body doubling sessions.
        
        Args:
            user_id: The UUID of the user to get analytics for
            
        Returns:
            SessionAnalyticsSchema containing analytics data
            
        Raises:
            HTTPException: If the analytics could not be generated
        """
        try:
            # Validate that the user exists (could be enhanced with a user check)
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Valid user ID is required"
                )
                
            # Get analytics from analytics service
            return await self.analytics_service.get_user_analytics(user_id)
            
        except Exception as e:
            # Log the error for debugging purposes
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error getting analytics for user {user_id}: {str(e)}")
            
            # Raise a formatted error
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate analytics: {str(e)}"
            )

    # Group Session Methods

    async def create_group_session(self, session_data: CreateBodyDoublingSchema) -> BodyDoublingSessionModel:
        """Create a new group session.
        
        Args:
            session_data: The data for creating a group session
            
        Returns:
            The created session model
            
        Raises:
            HTTPException: If session type is not GROUP
        """
        if session_data.session_type != SessionType.GROUP:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Session type must be GROUP",
            )

        # Create session
        session = await self.session_manager.create_session(session_data)
        return session

    async def get_group_session_info(self, session_id: UUID) -> GroupSessionSchema:
        """Get information about a group session.
        
        Args:
            session_id: The UUID of the group session
            
        Returns:
            GroupSessionSchema containing session information
            
        Raises:
            HTTPException: If the session is not found or not a group session
        """
        # Get and validate session
        session = await self._get_and_validate_group_session(session_id)
        
        # Extract session metadata
        meta_data = session.meta_data or {}
        
        # Build group session info
        session_info = self._build_group_session_info(session, meta_data)
        
        # Convert to schema
        return self._create_group_session_schema(session_info)
        
    async def _get_and_validate_group_session(self, session_id: UUID) -> BodyDoublingSessionModel:
        """Get and validate a group session.
        
        Args:
            session_id: The UUID of the session to get
            
        Returns:
            The session model if valid
            
        Raises:
            HTTPException: If the session is not found or not a group session
        """
        session = await self.session_manager.get_session_by_id(session_id)
        if not session:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
            
        if session.session_type != SessionType.GROUP:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Not a group session",
            )
            
        return session
        
    def _build_group_session_info(
        self, session: BodyDoublingSessionModel, meta_data: Dict[str, Any]
    ) -> GroupSessionInfo:
        """Build a GroupSessionInfo object from a session and its metadata.
        
        Args:
            session: The group session model
            meta_data: The session metadata
            
        Returns:
            A GroupSessionInfo object with session details
        """
        participants = meta_data.get("participants", [str(session.user_id)])
        pending_requests = meta_data.get("join_requests", [])
        
        return GroupSessionInfo(
            session_id=str(session.id),
            host_id=str(session.host_id),
            topic=meta_data.get("topic"),
            description=meta_data.get("description"),
            status=session.status.value,
            start_time=session.start_time,
            end_time=session.end_time,
            max_participants=session.max_participants,
            current_participants=participants,
            pending_requests=pending_requests,
            environment=meta_data.get("environment"),
            activity_type=session.activity_type.value if session.activity_type else None,
            duration_minutes=session.duration_minutes,
        )
        
    def _create_group_session_schema(self, session_info: GroupSessionInfo) -> GroupSessionSchema:
        """Create a GroupSessionSchema from GroupSessionInfo.
        
        Args:
            session_info: The GroupSessionInfo object
            
        Returns:
            A GroupSessionSchema object
        """
        return GroupSessionSchema(
            session_id=session_info.session_id,
            host_id=session_info.host_id,
            topic=session_info.topic,
            description=session_info.description,
            status=session_info.status,
            start_time=session_info.start_time,
            end_time=session_info.end_time,
            max_participants=session_info.max_participants,
            current_participants=session_info.current_participants,
            pending_requests=session_info.pending_requests,
            environment=session_info.environment,
            activity_type=session_info.activity_type,
            duration_minutes=session_info.duration_minutes,
        )

    async def request_join_group(
        self, user_id: UUID, session_id: UUID, join_request: Dict[str, Any]
    ) -> BodyDoublingSessionModel:
        """Request to join a group session.
        
        Args:
            user_id: The UUID of the user requesting to join
            session_id: The UUID of the session to join
            join_request: Additional data for the join request
            
        Returns:
            The updated session model with the join request added
            
        Raises:
            HTTPException: If the session is not found or other validation errors occur
        """
        # Get and validate the group session
        session = await self._get_and_validate_group_session(session_id)
        
        # Validate session is active
        if session.status != SessionStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Session is not active",
            )
        
        # Validate user can join the session
        await self._validate_user_can_join(user_id, session)
        
        # Initialize and prepare session metadata
        meta_data = self._initialize_session_metadata(session)
        
        # Create and add the join request
        meta_data = self._add_join_request(meta_data, user_id, join_request)
        session.meta_data = meta_data
        
        # Save changes
        await self._update_session_in_db(session)
        
        # Send notification to host
        await self.notification_service.notify_join_request(
            session_id, session.host_id, user_id
        )
        
        return session
        
    async def _validate_user_can_join(
        self, user_id: UUID, session: BodyDoublingSessionModel
    ) -> None:
        """Validate that a user can join a session.
        
        Args:
            user_id: The UUID of the user to validate
            session: The session to validate against
            
        Raises:
            HTTPException: If the user cannot join the session
        """
        # Check if user already has an active session
        active_session = await self.session_manager.get_active_session(user_id)
        if active_session:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already has an active session",
            )
            
        # Initialize metadata if not present
        meta_data = session.meta_data or {}
        participants = meta_data.get("participants", [str(session.user_id)])
        join_requests = meta_data.get("join_requests", [])
        
        # Check if user is already a participant
        if str(user_id) in participants:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already a participant",
            )
            
        # Check if user has already requested to join
        if any(req.get("user_id") == str(user_id) for req in join_requests):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User has already requested to join",
            )
            
    def _initialize_session_metadata(
        self, session: BodyDoublingSessionModel
    ) -> Dict[str, Any]:
        """Initialize session metadata for group sessions.
        
        Args:
            session: The session model to initialize metadata for
            
        Returns:
            The initialized metadata dictionary
        """
        meta_data = session.meta_data or {}
        
        if "join_requests" not in meta_data:
            meta_data["join_requests"] = []
            
        if "participants" not in meta_data:
            meta_data["participants"] = [str(session.user_id)]
            
        return meta_data
        
    def _add_join_request(
        self, meta_data: Dict[str, Any], user_id: UUID, join_request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Add a join request to session metadata.
        
        Args:
            meta_data: The session metadata to update
            user_id: The UUID of the user requesting to join
            join_request: Additional data for the join request
            
        Returns:
            The updated metadata dictionary
        """
        import uuid
        request_id = str(uuid.uuid4())
        
        # Create a new join request with required fields
        request_data = join_request.copy()
        request_data.update({
            "request_id": request_id,
            "user_id": str(user_id),
            "timestamp": str(join_request.get("timestamp")),
        })
        
        # Add to join requests
        meta_data["join_requests"].append(request_data)
        
        return meta_data

    async def accept_join_request(
        self, session_id: UUID, request_id: str
    ) -> BodyDoublingSessionModel:
        """Accept a request to join a group session.
        
        Args:
            session_id: The UUID of the session
            request_id: The ID of the join request to accept
            
        Returns:
            The updated session model
            
        Raises:
            HTTPException: If the session or request is not found or other validation errors occur
        """
        # Get and validate the group session
        session = await self._get_and_validate_group_session(session_id)
        
        # Validate session is active
        if session.status != SessionStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Session is not active",
            )
        
        # Initialize and prepare session metadata
        meta_data = self._initialize_session_metadata(session)
        
        # Find and validate the join request
        request_index, request_data = self._find_join_request(meta_data["join_requests"], request_id)
        if request_index is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Join request not found",
            )
        
        # Check if session is at capacity
        self._validate_session_capacity(session, meta_data)
        
        # Add user to participants and remove request
        user_id = request_data["user_id"]
        meta_data = self._add_participant_and_remove_request(meta_data, user_id, request_index)
        session.meta_data = meta_data
        
        # Save changes
        await self._update_session_in_db(session)
        
        # Send notifications
        await self._send_join_accepted_notifications(session_id, user_id)
        
        return session
        
    def _validate_session_capacity(
        self, session: BodyDoublingSessionModel, meta_data: Dict[str, Any]
    ) -> None:
        """Validate that a session has capacity for more participants.
        
        Args:
            session: The session model to validate
            meta_data: The session metadata
            
        Raises:
            HTTPException: If the session is at capacity
        """
        participants = meta_data.get("participants", [])
        if len(participants) >= session.max_participants:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Session is full",
            )
            
    def _add_participant_and_remove_request(
        self, meta_data: Dict[str, Any], user_id: str, request_index: int
    ) -> Dict[str, Any]:
        """Add a user to participants and remove their join request.
        
        Args:
            meta_data: The session metadata to update
            user_id: The user ID to add as a participant
            request_index: The index of the request to remove
            
        Returns:
            The updated metadata dictionary
        """
        # Add user to participants if not already there
        if user_id not in meta_data["participants"]:
            meta_data["participants"].append(user_id)
            
        # Remove the join request
        meta_data["join_requests"].pop(request_index)
        
        return meta_data
        
    async def _send_join_accepted_notifications(self, session_id: UUID, user_id: str) -> None:
        """Send notifications when a join request is accepted.
        
        Args:
            session_id: The UUID of the session
            user_id: The ID of the user who was accepted
        """
        await self.notification_service.notify_join_request_response(
            session_id, UUID(user_id), accepted=True
        )
        await self.notification_service.notify_session_join(
            session_id, UUID(user_id)
        )

    async def reject_join_request(
        self, session_id: UUID, request_id: str
    ) -> BodyDoublingSessionModel:
        """Reject a request to join a group session.
        
        Args:
            session_id: The UUID of the session
            request_id: The ID of the join request to reject
            
        Returns:
            The updated session model
            
        Raises:
            HTTPException: If the session or request is not found
        """
        # Get and validate the group session
        session = await self._get_and_validate_group_session(session_id)
        
        # Initialize and prepare session metadata
        meta_data = self._initialize_session_metadata(session)
        
        # Find and validate the join request
        request_index, request_data = self._find_join_request(meta_data["join_requests"], request_id)
        if request_index is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Join request not found",
            )
        
        # Remove the request
        user_id = request_data["user_id"]
        meta_data["join_requests"].pop(request_index)
        session.meta_data = meta_data
        
        # Save changes
        await self._update_session_in_db(session)
        
        # Send notification
        await self._send_join_rejected_notification(session_id, user_id)
        
        return session
        
    async def _send_join_rejected_notification(self, session_id: UUID, user_id: str) -> None:
        """Send notification when a join request is rejected.
        
        Args:
            session_id: The UUID of the session
            user_id: The ID of the user who was rejected
        """
        await self.notification_service.notify_join_request_response(
            session_id, UUID(user_id), accepted=False
        )

    def _find_join_request(
        self, join_requests: List[Dict[str, Any]], request_id: str
    ) -> Tuple[Optional[int], Optional[Dict[str, Any]]]:
        """Find a join request by its ID.
        
        Args:
            join_requests: List of join request dictionaries
            request_id: The ID of the request to find
            
        Returns:
            Tuple of (index, request_data) or (None, None) if not found
        """
        for i, req in enumerate(join_requests):
            if req.get("request_id") == request_id:
                return i, req
                
        return None, None

    # Feedback Methods

    async def add_session_feedback(
        self, session_id: UUID, feedback: SessionFeedbackSchema
    ) -> BodyDoublingSessionModel:
        """Add feedback to a session.
        
        Args:
            session_id: The UUID of the session to add feedback to
            feedback: The feedback data to add
            
        Returns:
            The updated session model
            
        Raises:
            HTTPException: If the session is not found
        """
        # Get the session
        session = await self.session_manager.get_session_by_id(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Initialize metadata if needed
        if not session.meta_data:
            session.meta_data = {}
            
        print(f"Session metadata before any changes: {session.meta_data}")
        
        # Initialize feedback list if needed
        if "feedback" not in session.meta_data:
            session.meta_data["feedback"] = []
            
        print(f"After initializing feedback: {session.meta_data}")
        
        # Add debug logging
        print(f"Feedback points input: {feedback.feedback_points}")
        
        # Process feedback points
        feedback_points = self._prepare_feedback_points(feedback)
        
        # Add debug logging
        print(f"Processed feedback points: {feedback_points}")
        
        # If there are no feedback points after processing but we have the original input,
        # use the original input directly (properly formatted)
        if not feedback_points and feedback.feedback_points:
            # Convert datetime objects to ISO strings
            processed_points = []
            for point in feedback.feedback_points:
                processed_point = point.copy()
                if isinstance(point.get("timestamp"), datetime):
                    processed_point["timestamp"] = point["timestamp"].isoformat()
                processed_point["user_id"] = str(feedback.user_id)
                processed_points.append(processed_point)
            feedback_points = processed_points
            print(f"Using direct feedback points: {feedback_points}")
        
        # Manually create a new dictionary to ensure we're not dealing with reference issues
        if not session.meta_data:
            session.meta_data = {}
        updated_metadata = dict(session.meta_data)
        
        # Ensure feedback array exists
        if "feedback" not in updated_metadata:
            updated_metadata["feedback"] = []
            
        # Add feedback points to the metadata
        if feedback_points:
            updated_metadata["feedback"].extend(feedback_points)
            
        # Update the session's metadata with our new dictionary
        session.meta_data = updated_metadata
        
        print(f"Session metadata after updating: {session.meta_data}")
        
        # Update session in database
        await self._update_session_in_db(session)
        
        # Verify the session was updated correctly by fetching it again
        updated_session = await self.session_manager.get_session_by_id(session_id)
        print(f"Session metadata after database update: {updated_session.meta_data}")
        
        # Log final state
        print(f"Final feedback array: {updated_session.meta_data.get('feedback', [])}")
        
        return updated_session
        
    def _prepare_feedback_points(self, feedback: SessionFeedbackSchema) -> list[dict]:
        """Process and format feedback points.
        
        Args:
            feedback: The feedback data containing feedback points
            
        Returns:
            A list of formatted feedback point dictionaries
        """
        result = []
        feedback_points = feedback.feedback_points or []
        
        for point in feedback_points:
            # Convert timestamp to ISO format if it's a datetime
            timestamp = point.get("timestamp")
            if isinstance(timestamp, datetime):
                timestamp = timestamp.isoformat()
            
            # Create feedback point
            feedback_point = {
                "timestamp": timestamp,
                "focus_rating": point.get("focus_rating"),
                "productivity_rating": point.get("productivity_rating"),
                "distraction_level": point.get("distraction_level"),
                "user_id": str(feedback.user_id)
            }
            
            result.append(feedback_point)
            
        # If no points were processed but we have average ratings, create a summary feedback point
        if not result and (feedback.average_focus_level or feedback.average_productivity or feedback.average_distraction_level):
            summary_point = {
                "timestamp": datetime.now().isoformat(),
                "focus_rating": feedback.average_focus_level if feedback.average_focus_level is not None else 0,
                "productivity_rating": feedback.average_productivity if feedback.average_productivity is not None else 0,
                "distraction_level": feedback.average_distraction_level if feedback.average_distraction_level is not None else 0,
                "user_id": str(feedback.user_id),
                "is_summary": True
            }
            result.append(summary_point)
            
        return result
        
    async def _update_session_in_db(self, session: BodyDoublingSessionModel) -> None:
        """Update a session in the database.
        
        Args:
            session: The session model to update
            
        Returns:
            None
        """
        # Make sure session.meta_data is properly serialized before saving
        if session.meta_data and isinstance(session.meta_data, dict):
            # Create a deep copy to avoid reference issues
            import copy
            import json
            from datetime import datetime
            
            # Helper function to convert datetime objects to ISO format strings
            def serialize_json(obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                if isinstance(obj, UUID):
                    return str(obj)
                return obj
            
            # Convert the meta_data to a properly serialized dictionary
            # First, convert to JSON and back to ensure it's serializable
            try:
                meta_data_copy = copy.deepcopy(session.meta_data)
                
                # Handle each field in meta_data
                for key, value in meta_data_copy.items():
                    if isinstance(value, list):
                        # Convert any datetime objects in lists
                        for i, item in enumerate(value):
                            if isinstance(item, dict):
                                for k, v in item.items():
                                    if isinstance(v, (datetime, UUID)):
                                        item[k] = serialize_json(v)
            
                # Set the updated meta_data back to the session
                session.meta_data = meta_data_copy
                
                # Print debug info
                print(f"Meta data before DB update: {session.meta_data}")
            except Exception as e:
                print(f"Error serializing meta_data: {e}")
        
        # Update session in database
        self.session_manager.db.add(session)
        await self.session_manager.db.commit()
        await self.session_manager.db.refresh(session)
        
        # Print debug info after update
        print(f"Meta data after DB update: {session.meta_data}")

    async def get_session_feedback(self, session_id: UUID) -> SessionFeedbackSchema:
        """Get feedback for a session.
        
        Args:
            session_id: The UUID of the session to get feedback for
            
        Returns:
            A SessionFeedbackSchema object containing the feedback data
            
        Raises:
            HTTPException: If the session is not found
        """
        # Get the session
        session = await self.session_manager.get_session_by_id(session_id)
        if not session:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
            
        # Extract feedback data from session
        feedback_data = self._extract_feedback_data(session)
        
        # Convert to schema and return
        return self._create_feedback_schema(feedback_data)
        
    def _extract_feedback_data(self, session: BodyDoublingSessionModel) -> SessionFeedbackData:
        """Extract feedback data from session metadata.
        
        Args:
            session: The session model containing feedback data
            
        Returns:
            A SessionFeedbackData object with extracted feedback information
        """
        # Get feedback points from metadata
        meta_data = session.meta_data or {}
        feedback_points = meta_data.get("feedback", [])
        
        # Calculate average focus level
        average_focus = self._calculate_average_focus(feedback_points)
        
        # Find final rating if available
        final_rating = self._find_final_rating(feedback_points)
        
        # Create and return feedback data object
        return SessionFeedbackData(
            feedback_points=feedback_points,
            session_id=session.id,
            user_id=session.user_id,
            average_focus_level=average_focus,
            final_rating=final_rating,
        )
        
    def _calculate_average_focus(self, feedback_points: List[Dict[str, Any]]) -> float:
        """Calculate the average focus level from feedback points.
        
        Args:
            feedback_points: List of feedback point dictionaries
            
        Returns:
            The average focus level as a float (0 if no valid focus ratings)
        """
        focus_levels = [
            fb.get("focus_rating", 0) for fb in feedback_points
            if isinstance(fb.get("focus_rating"), (int, float))
        ]
        
        return sum(focus_levels) / len(focus_levels) if focus_levels else 0
        
    def _find_final_rating(self, feedback_points: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Find the final rating from feedback points.
        
        Args:
            feedback_points: List of feedback point dictionaries
            
        Returns:
            The final rating dictionary or None if not found
        """
        for fb in reversed(feedback_points):
            if fb.get("final", False):
                return fb
                
        return None
        
    def _create_feedback_schema(self, feedback_data: SessionFeedbackData) -> SessionFeedbackSchema:
        """Create a SessionFeedbackSchema from SessionFeedbackData.
        
        Args:
            feedback_data: The SessionFeedbackData object
            
        Returns:
            A SessionFeedbackSchema object
        """
        return SessionFeedbackSchema(
            feedback_points=feedback_data.feedback_points,
            session_id=str(feedback_data.session_id),
            user_id=str(feedback_data.user_id),
            average_focus_level=feedback_data.average_focus_level,
            final_rating=feedback_data.final_rating,
        )

    # Preference Methods

    @handle_service_error
    async def update_preferences(
        self, session_id: UUID, preferences: Dict[str, Any]
    ) -> BodyDoublingSessionModel:
        """Update session preferences.
        
        Args:
            session_id: The UUID of the session to update preferences for
            preferences: Dictionary of preference key-value pairs to update
            
        Returns:
            The updated session model
            
        Raises:
            HTTPException: If the session is not found or preferences could not be updated
            ServiceError: If an error occurs in the service operation (handled by decorator)
        """
        try:
            # Get the session first to make sure it exists
            session = await self.session_manager.get_session_by_id(session_id)
            if not session:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, 
                    detail="Session not found"
                )
                
            # Update preferences through session manager
            updated_session = await self.session_manager.update_preferences(session_id, preferences)
            return updated_session
            
        except HTTPException:
            # Re-raise HTTPExceptions directly
            raise
        except Exception as e:
            # Let the decorator handle other exceptions
            raise

    # Session Metrics Methods

    async def update_session_metrics(
        self, session_id: UUID, metrics: Dict[str, Any]
    ) -> BodyDoublingSessionModel:
        """Update metrics for a session.
        
        Args:
            session_id: The UUID of the session to update metrics for
            metrics: Dictionary of metrics to update on the session
            
        Returns:
            The updated session model
            
        Raises:
            HTTPException: If the session is not found
        """
        # Get the session
        session = await self.session_manager.get_session_by_id(session_id)
        if not session:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
            
        # Apply metrics updates to session fields
        self._apply_metrics_to_session(session, metrics)
                
        # Save changes
        await self._update_session_in_db(session)
        
        return session
        
    def _apply_metrics_to_session(
        self, session: BodyDoublingSessionModel, metrics: Dict[str, Any]
    ) -> None:
        """Apply metrics updates to session fields.
        
        Args:
            session: The session model to update
            metrics: Dictionary of metrics to update on the session
            
        Returns:
            None
        """
        for field, value in metrics.items():
            if hasattr(session, field):
                setattr(session, field, value) 