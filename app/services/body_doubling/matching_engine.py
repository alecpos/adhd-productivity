"""Matching engine component for body doubling service."""

from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.body_doubling_model import BodyDoublingSessionModel
from app.models.enums_model import SessionStatus, SessionType, ActivityType
from app.services.body_doubling.session_manager import SessionManager


class MatchingEngine:
    """Handles user matching for body doubling sessions."""

    def __init__(self, session_manager: SessionManager):
        """Initialize the matching engine with session manager."""
        self.session_manager = session_manager
        self.db = session_manager.db

    def _score_preferences_match(
        self, user_prefs: Dict[str, Any], match_prefs: Dict[str, Any]
    ) -> float:
        """Calculate preference match score between users."""
        score = 0.0

        # Score work style match
        if (
            "work_style" in user_prefs
            and "work_style" in match_prefs
            and user_prefs["work_style"] == match_prefs["work_style"]
        ):
            score += 10.0

        # Score focus level match
        if (
            "focus_level" in user_prefs
            and "focus_level" in match_prefs
            and user_prefs["focus_level"] == match_prefs["focus_level"]
        ):
            score += 8.0

        # Score task similarity
        if (
            "preferred_tasks" in user_prefs
            and "preferred_tasks" in match_prefs
            and isinstance(user_prefs["preferred_tasks"], list)
            and isinstance(match_prefs["preferred_tasks"], list)
        ):
            matching_tasks = set(user_prefs["preferred_tasks"]) & set(
                match_prefs["preferred_tasks"]
            )
            score += len(matching_tasks) * 5.0

        # Score activity type preference
        if (
            "preferred_activity_types" in user_prefs
            and "preferred_activity_types" in match_prefs
            and isinstance(user_prefs["preferred_activity_types"], list)
            and isinstance(match_prefs["preferred_activity_types"], list)
        ):
            matching_activities = set(user_prefs["preferred_activity_types"]) & set(
                match_prefs["preferred_activity_types"]
            )
            score += len(matching_activities) * 4.0

        return score

    def _score_history_compatibility(
        self,
        user_history: Optional[List[Dict[str, Any]]],
        match_history: Optional[List[Dict[str, Any]]],
    ) -> float:
        """Calculate compatibility score based on session history."""
        if not user_history or not match_history:
            return 0.0

        score = 0.0

        # Score high productivity sessions
        productive_user = any(session.get("productivity_rating", 0) > 3 for session in user_history)
        productive_match = any(
            session.get("productivity_rating", 0) > 3 for session in match_history
        )
        if productive_user and productive_match:
            score += 5.0

        # Score session duration preference
        user_durations = [
            session.get("duration_minutes", 0)
            for session in user_history
            if "duration_minutes" in session
        ]
        match_durations = [
            session.get("duration_minutes", 0)
            for session in match_history
            if "duration_minutes" in session
        ]

        if user_durations and match_durations:
            avg_user_duration = sum(user_durations) / len(user_durations)
            avg_match_duration = sum(match_durations) / len(match_durations)

            # Score higher if average durations are similar
            duration_diff = abs(avg_user_duration - avg_match_duration)
            if duration_diff < 15:  # Within 15 minutes
                score += 4.0
            elif duration_diff < 30:  # Within 30 minutes
                score += 2.0

        return score

    def _calculate_match_score(
        self,
        user_prefs: Dict[str, Any],
        match_prefs: Dict[str, Any],
        criteria: Dict[str, Any],
        user_history: Optional[List[Dict[str, Any]]] = None,
        match_history: Optional[List[Dict[str, Any]]] = None,
    ) -> float:
        """Calculate overall match score between users."""
        # Early return if either user has no preferences
        if not user_prefs or not match_prefs:
            return 0.0

        # Calculate preference match score
        score = self._score_preferences_match(user_prefs, match_prefs)

        # Add history compatibility score
        score += self._score_history_compatibility(user_history, match_history)

        # Apply criteria weights if provided
        if criteria:
            # Weight work style higher if specified
            if criteria.get("work_style_important"):
                if (
                    "work_style" in user_prefs
                    and "work_style" in match_prefs
                    and user_prefs["work_style"] == match_prefs["work_style"]
                ):
                    score += 5.0  # Additional points for this criteria

            # Weight focus level higher if specified
            if criteria.get("focus_level_important"):
                if (
                    "focus_level" in user_prefs
                    and "focus_level" in match_prefs
                    and user_prefs["focus_level"] == match_prefs["focus_level"]
                ):
                    score += 5.0  # Additional points for this criteria

        return score

    async def find_matching_users(
        self, user_id: UUID, user_prefs: Dict[str, Any], criteria: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Find users matching the given criteria."""
        # Get all active sessions for potential matches
        active_sessions = await self.session_manager.get_active_sessions()

        matches = []
        user_history = criteria.get("session_history", [])

        for session in active_sessions:
            # Skip own sessions
            if str(session.user_id) == str(user_id):
                continue

            # Skip non-matchable sessions
            if not session.host_id or session.session_type != SessionType.ONE_ON_ONE:
                continue

            # Get other user's preferences
            match_prefs = session.meta_data.get("preferences", {}) if session.meta_data else {}
            match_history = (
                session.meta_data.get("session_history", []) if session.meta_data else []
            )

            # Calculate match score
            match_score = self._calculate_match_score(
                user_prefs, match_prefs, criteria, user_history, match_history
            )

            # Add to matches if score is above threshold
            if match_score > criteria.get("min_score", 10):
                matches.append(
                    {
                        "user_id": str(session.user_id),
                        "session_id": str(session.id),
                        "score": match_score,
                        "activity_type": (
                            session.activity_type.value if session.activity_type else None
                        ),
                        "preferences": match_prefs,
                    }
                )

        # Sort matches by score (highest first)
        matches.sort(key=lambda x: x["score"], reverse=True)

        return matches

    async def request_match(
        self, user_id: UUID, match_criteria: Dict[str, Any]
    ) -> BodyDoublingSessionModel:
        """Create a session request for matching."""
        # Check if user already has an active session
        active_session = await self.session_manager.get_active_session(user_id)
        if active_session:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already has an active session",
            )

        # Create a new session in pending state
        from app.schemas.body_doubling_schema import CreateBodyDoublingSchema
        from datetime import datetime

        # Convert activity_type to enum if it's a string
        activity_type = match_criteria.get("activity_type", "work")
        if isinstance(activity_type, str):
            activity_type = ActivityType(activity_type.lower())

        session_data = CreateBodyDoublingSchema(
            user_id=user_id,
            host_id=user_id,
            session_type=SessionType.ONE_ON_ONE,
            status=SessionStatus.PENDING,
            start_time=datetime.now(),
            activity_type=activity_type,
            planned_duration=match_criteria.get("planned_duration", 30),  # Default to 30 minutes
            max_participants=2,
        )

        # Create the session
        session = await self.session_manager.create_session(session_data)

        # Store match criteria in meta_data
        if not session.meta_data:
            session.meta_data = {}
        session.meta_data["match_criteria"] = match_criteria
        await self.db.commit()

        return session

    async def accept_match(self, partner_id: UUID, session_id: UUID) -> BodyDoublingSessionModel:
        """Accept a match request."""
        # Get the session
        request_session = await self.session_manager.get_session_by_id(session_id)
        if not request_session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found",
            )

        # Check if partner already has an active session
        partner_session = await self.session_manager.get_active_session(partner_id)
        if partner_session:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Partner already has an active session",
            )

        # Initialize metadata if needed
        if not request_session.meta_data:
            request_session.meta_data = {}

        if "participants" not in request_session.meta_data:
            request_session.meta_data["participants"] = [str(request_session.user_id)]

        # Add the partner's ID to the participants list if not already there
        if str(partner_id) not in request_session.meta_data["participants"]:
            request_session.meta_data["participants"].append(str(partner_id))

        # Ensure we're using a new dictionary to avoid reference issues
        updated_meta_data = dict(request_session.meta_data)

        # Print debug info
        print(f"Updated meta_data with participants: {updated_meta_data}")

        # Directly update the session in the database
        from sqlalchemy import update
        from app.models.body_doubling_model import BodyDoublingSessionModel

        # Update the session status to ACTIVE and set the meta_data
        session_update = (
            update(BodyDoublingSessionModel)
            .where(BodyDoublingSessionModel.id == session_id)
            .values(status=SessionStatus.ACTIVE, meta_data=updated_meta_data)
        )

        await self.db.execute(session_update)
        await self.db.commit()

        # Refresh the session to get the updated data
        await self.db.refresh(request_session)

        # Verify the update worked
        updated_session = await self.session_manager.get_session_by_id(session_id)
        print(f"Final session state after update: {updated_session.status}")
        print(f"Final meta_data after update: {updated_session.meta_data}")

        return updated_session
