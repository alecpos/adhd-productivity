"""Analytics service for processing body doubling session data."""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Union, Any
from uuid import UUID
from collections import Counter

from fastapi import HTTPException
from sqlalchemy import func, select, and_, or_, JSON
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.body_doubling_model import BodyDoublingSessionModel
from app.models.enums_model import SessionStatus, SessionType
from app.schemas.body_doubling_schema import SessionAnalyticsSchema, SessionFeedbackSchema
from app.services.body_doubling.session_manager import SessionManager


class AnalyticsService:
    """Service for analyzing body doubling session data and generating insights."""

    def __init__(self, session_manager: SessionManager):
        """Initialize the analytics service.

        Args:
            session_manager: The session manager instance
        """
        self.session_manager = session_manager
        self._db = session_manager.db

    async def get_user_analytics(self, user_id: UUID) -> SessionAnalyticsSchema:
        """Get analytics for a user based on their session history.

        Args:
            user_id: The user to get analytics for

        Returns:
            SessionAnalyticsSchema with user analytics
        """
        query = select(BodyDoublingSessionModel).where(
            and_(
                or_(
                    BodyDoublingSessionModel.user_id == user_id,
                    BodyDoublingSessionModel.meta_data.cast(JSON).contains(
                        {"participants": [str(user_id)]}
                    ),
                ),
                or_(
                    BodyDoublingSessionModel.status == SessionStatus.COMPLETED,
                    BodyDoublingSessionModel.status
                    == SessionStatus.ACTIVE,  # Include ACTIVE sessions
                ),
            )
        )

        result = await self._db.execute(query)
        sessions = result.scalars().all()

        # Add debug logging
        print(f"Found {len(sessions)} sessions for user {user_id}")
        for session in sessions:
            print(
                f"Session {session.id} - Status: {session.status} - Metadata: {session.meta_data}"
            )

        if not sessions:
            return SessionAnalyticsSchema(
                user_id=user_id,
                total_sessions=0,
                total_duration=0,
                completion_rate=0.0,
                most_productive_times=[],
                preferred_activity_types=[],
                preferred_session_types=[],
                average_focus_rating=0.0,
                average_productivity_rating=0.0,
                average_session_duration=0,
            )

        # Calculate analytics
        total_sessions = len(sessions)
        total_duration = 0
        focus_ratings = []
        productivity_ratings = []
        session_durations = []
        activity_types = []
        session_types = []
        productive_hours = []

        for session in sessions:
            # Duration
            if session.start_time and session.end_time:
                duration = (session.end_time - session.start_time).total_seconds() / 60
                total_duration += duration
                session_durations.append(duration)
                productive_hours.append(session.start_time.strftime("%H:00"))

            # Activity and session types
            if session.activity_type:
                activity_types.append(session.activity_type)
            if session.session_type:
                session_types.append(session.session_type)

            # Ratings from metadata
            if session.meta_data and "feedback" in session.meta_data:
                for feedback in session.meta_data["feedback"]:
                    if feedback.get("user_id") == str(user_id):
                        if "focus_rating" in feedback:
                            focus_ratings.append(feedback["focus_rating"])
                        if "productivity_rating" in feedback:
                            productivity_ratings.append(feedback["productivity_rating"])

        # Calculate averages and preferences
        avg_focus = sum(focus_ratings) / len(focus_ratings) if focus_ratings else 0.0
        avg_productivity = (
            sum(productivity_ratings) / len(productivity_ratings) if productivity_ratings else 0.0
        )
        avg_duration = sum(session_durations) / len(session_durations) if session_durations else 0

        # Get most common activity and session types
        preferred_activity_types = [
            activity for activity, _ in Counter(activity_types).most_common()
        ]
        preferred_session_types = [
            session_type for session_type, _ in Counter(session_types).most_common()
        ]

        # Get most productive times
        most_productive_times = [hour for hour, _ in Counter(productive_hours).most_common(3)]

        return SessionAnalyticsSchema(
            user_id=user_id,
            total_sessions=total_sessions,
            total_duration=int(total_duration),
            completion_rate=total_sessions
            / (total_sessions + len([s for s in sessions if s.status == SessionStatus.CANCELLED])),
            most_productive_times=most_productive_times,
            preferred_activity_types=preferred_activity_types,
            preferred_session_types=preferred_session_types,
            average_focus_rating=avg_focus,
            average_productivity_rating=avg_productivity,
            average_session_duration=int(avg_duration),
        )

    async def get_session_analytics(self, session_id: UUID) -> Dict[str, Any]:
        """Get analytics for a specific session.

        Args:
            session_id: The session to analyze

        Returns:
            Dictionary with session analytics

        Raises:
            HTTPException: If the session is not found
        """
        query = select(BodyDoublingSessionModel).where(BodyDoublingSessionModel.id == session_id)
        result = await self._db.execute(query)
        session = result.scalar_one_or_none()

        if not session:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

        # Calculate duration
        total_duration = 0
        if session.start_time and session.end_time:
            total_duration = (
                session.end_time - session.start_time
            ).total_seconds() / 60  # in minutes

        # Get feedback metrics
        feedback_points = []
        if session.meta_data and "feedback" in session.meta_data:
            feedback_points = session.meta_data["feedback"]

        # Calculate averages
        focus_ratings = [f.get("focus_rating", 0) for f in feedback_points if "focus_rating" in f]
        productivity_ratings = [
            f.get("productivity_rating", 0) for f in feedback_points if "productivity_rating" in f
        ]

        # Add session-level ratings if available
        if session.focus_rating is not None:
            focus_ratings.append(session.focus_rating)
        if session.productivity_rating is not None:
            productivity_ratings.append(session.productivity_rating)

        average_focus_rating = sum(focus_ratings) / len(focus_ratings) if focus_ratings else 0
        average_productivity_rating = (
            sum(productivity_ratings) / len(productivity_ratings) if productivity_ratings else 0
        )

        return {
            "total_duration": total_duration,
            "average_focus_rating": average_focus_rating,
            "average_productivity_rating": average_productivity_rating,
            "completion_rate": 1.0 if session.status == SessionStatus.COMPLETED else 0.0,
        }

    async def get_session_feedback(self, session_id: UUID) -> SessionFeedbackSchema:
        """Get feedback for a specific session.

        Args:
            session_id: The session to get feedback for

        Returns:
            SessionFeedbackSchema with feedback data

        Raises:
            HTTPException: If the session is not found
        """
        query = select(BodyDoublingSessionModel).where(BodyDoublingSessionModel.id == session_id)
        result = await self._db.execute(query)
        session = result.scalar_one_or_none()

        if not session:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

        feedback_points = []
        if session.meta_data and "feedback" in session.meta_data:
            feedback_points = session.meta_data["feedback"]

        # Calculate average focus level and productivity
        focus_ratings = [f["focus_rating"] for f in feedback_points if "focus_rating" in f]
        productivity_ratings = [
            f["productivity_rating"] for f in feedback_points if "productivity_rating" in f
        ]
        distraction_ratings = [
            f["distraction_level"] for f in feedback_points if "distraction_level" in f
        ]

        avg_focus = sum(focus_ratings) / len(focus_ratings) if focus_ratings else 0
        avg_productivity = (
            sum(productivity_ratings) / len(productivity_ratings) if productivity_ratings else 0
        )
        avg_distraction = (
            sum(distraction_ratings) / len(distraction_ratings) if distraction_ratings else 0
        )

        return SessionFeedbackSchema(
            session_id=str(session_id),
            user_id=session.user_id,
            feedback_points=feedback_points,
            average_focus_level=avg_focus,
            average_productivity=avg_productivity,
            average_distraction_level=avg_distraction,
            final_rating=None,  # This can be updated later if needed
        )

    async def add_session_feedback(
        self, session_id: UUID, user_id: UUID, feedback_data: Dict[str, Any]
    ) -> BodyDoublingSessionModel:
        """Add feedback for a session.

        Args:
            session_id: The session to add feedback for
            user_id: The user providing feedback
            feedback_data: Feedback data including ratings and notes

        Returns:
            Updated session model

        Raises:
            HTTPException: If the session is not found or user didn't participate
        """
        query = select(BodyDoublingSessionModel).where(BodyDoublingSessionModel.id == session_id)
        result = await self._db.execute(query)
        session = result.scalar_one_or_none()

        if not session:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

        # Verify user participated in the session
        user_id_str = str(user_id)
        participants = []
        if session.meta_data and "participants" in session.meta_data:
            participants = session.meta_data["participants"]

        if (
            user_id_str not in participants
            and session.user_id != user_id
            and session.host_id != user_id
        ):
            raise HTTPException(
                status_code=403, detail="Only session participants can provide feedback"
            )

        # Add user ID to feedback data
        feedback_entry = {
            "user_id": user_id_str,
            "timestamp": datetime.now().isoformat(),
            **feedback_data,
        }

        # Initialize meta_data if needed
        if not session.meta_data:
            session.meta_data = {}

        # Initialize feedback list if needed
        if "feedback" not in session.meta_data:
            session.meta_data["feedback"] = []

        # Add feedback entry
        session.meta_data["feedback"].append(feedback_entry)

        # Update session-level ratings if this is the first feedback
        if session.focus_rating is None and "focus_rating" in feedback_data:
            session.focus_rating = feedback_data["focus_rating"]

        if session.productivity_rating is None and "productivity_rating" in feedback_data:
            session.productivity_rating = feedback_data["productivity_rating"]

        # Commit changes
        await self._db.commit()
        await self._db.refresh(session)

        return session

    async def get_focus_pattern_insights(self, user_id: UUID) -> Dict[str, Any]:
        """Get insights about a user's focus patterns.

        Args:
            user_id: The user to analyze

        Returns:
            Dictionary with focus pattern insights
        """
        query = select(BodyDoublingSessionModel).where(
            and_(
                or_(
                    BodyDoublingSessionModel.user_id == user_id,
                    BodyDoublingSessionModel.meta_data.cast(JSON).contains(
                        {"participants": [str(user_id)]}
                    ),
                ),
                BodyDoublingSessionModel.status == SessionStatus.COMPLETED,
            )
        )

        result = await self._db.execute(query)
        sessions = result.scalars().all()

        if not sessions:
            return {
                "insights": [],
                "total_sessions": 0,
                "average_focus_rating": 0.0,
                "average_productivity_rating": 0.0,
            }

        # Collect session data
        focus_ratings = []
        productivity_ratings = []
        session_times = []
        session_days = []
        session_durations = []

        for session in sessions:
            if session.meta_data and "feedback" in session.meta_data:
                for feedback in session.meta_data["feedback"]:
                    if feedback.get("user_id") == str(user_id):
                        if "focus_rating" in feedback:
                            focus_ratings.append(feedback["focus_rating"])
                        if "productivity_rating" in feedback:
                            productivity_ratings.append(feedback["productivity_rating"])

            if session.start_time:
                session_times.append(session.start_time.hour)
                session_days.append(session.start_time.weekday())
                if session.end_time:
                    duration = (session.end_time - session.start_time).total_seconds() / 60
                    session_durations.append(duration)

        # Generate insights
        insights = []

        # Time of day insights
        if session_times:
            most_productive_hour = max(
                range(24), key=lambda h: sum(1 for t in session_times if t == h)
            )
            insights.append(
                {
                    "type": "time_of_day",
                    "insight": f"Your most frequent session time is {most_productive_hour}:00",
                    "confidence": "medium",
                }
            )

        # Day of week insights
        if session_days:
            day_names = [
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
                "Sunday",
            ]
            most_frequent_day = max(
                range(7), key=lambda d: sum(1 for day in session_days if day == d)
            )
            insights.append(
                {
                    "type": "day_of_week",
                    "insight": f"You most frequently schedule sessions on {day_names[most_frequent_day]}",
                    "confidence": "medium",
                }
            )

        # Duration insights
        if session_durations:
            avg_duration = sum(session_durations) / len(session_durations)
            insights.append(
                {
                    "type": "duration",
                    "insight": f"Your average session duration is {int(avg_duration)} minutes",
                    "confidence": "high",
                }
            )

        return {
            "insights": insights,
            "total_sessions": len(sessions),
            "average_focus_rating": (
                sum(focus_ratings) / len(focus_ratings) if focus_ratings else 0.0
            ),
            "average_productivity_rating": (
                sum(productivity_ratings) / len(productivity_ratings)
                if productivity_ratings
                else 0.0
            ),
        }

    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate the trend direction from a list of values.

        Args:
            values: List of numeric values

        Returns:
            String indicating trend: "improving", "declining", or "stable"
        """
        if not values or len(values) < 2:
            return "stable"

        # Simple linear trend
        changes = [values[i] - values[i - 1] for i in range(1, len(values))]
        avg_change = sum(changes) / len(changes)

        if avg_change > 0.1:  # Threshold for improvement
            return "improving"
        elif avg_change < -0.1:  # Threshold for decline
            return "declining"
        else:
            return "stable"
