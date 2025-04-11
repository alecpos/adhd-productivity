#!/usr/bin/env python
"""Manual test script for AnalyticsService.

This script provides examples of how to use the AnalyticsService
and can be run to manually test the functionality.
"""

import asyncio
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any

from app.services.body_doubling.analytics_service import AnalyticsService
from app.models.body_doubling_model import BodyDoublingSessionModel
from app.models.enums_model import SessionStatus, SessionType


# Mock database session for testing
class MockDBSession:
    """Mock database session for testing."""

    def __init__(self):
        self.sessions = {}

    async def execute(self, query):
        """Mock query execution."""
        return self

    async def commit(self):
        """Mock commit."""
        pass

    async def refresh(self, obj):
        """Mock refresh."""
        pass

    def scalars(self):
        """Mock scalars method."""
        return self

    def all(self):
        """Return all sessions."""
        return list(self.sessions.values())

    def scalar_one_or_none(self):
        """Return the session for the given ID."""
        # The query filter would have an ID in it
        # Here we're just returning the first session for simplicity
        if not self.sessions:
            return None
        return list(self.sessions.values())[0]

    def add_session(self, session):
        """Add a session to the mock database."""
        self.sessions[str(session.id)] = session
        return session


# Helper function to create a sample session
def create_sample_session(user_id=None, session_id=None, completed=True):
    """Create a sample session for testing."""
    if user_id is None:
        user_id = uuid.uuid4()
    if session_id is None:
        session_id = uuid.uuid4()

    now = datetime.now()

    return BodyDoublingSessionModel(
        id=session_id,
        user_id=user_id,
        host_id=user_id,
        title="Test Session",
        description="Test session for manual testing",
        start_time=now - timedelta(hours=2),
        end_time=now - timedelta(hours=1) if completed else None,
        status=SessionStatus.COMPLETED if completed else SessionStatus.ACTIVE,
        session_type=SessionType.BODY_DOUBLING,
        activity_type="Programming",
        focus_rating=None,
        productivity_rating=None,
        meta_data={"participants": [str(user_id), str(uuid.uuid4())], "feedback": []},
    )


async def test_add_feedback():
    """Test adding feedback to a session."""
    # Create mock DB session
    db_session = MockDBSession()

    # Create analytics service
    analytics_service = AnalyticsService(db_session)

    # Create a user and session
    user_id = uuid.uuid4()
    session_id = uuid.uuid4()
    session = create_sample_session(user_id, session_id)

    # Add session to mock DB
    db_session.add_session(session)

    # Add feedback
    feedback_data = {
        "focus_rating": 4,
        "productivity_rating": 5,
        "distraction_level": 2,
        "notes": "This was a productive session",
    }

    print(f"Adding feedback for session {session_id}...")
    updated_session = await analytics_service.add_session_feedback(
        session_id, user_id, feedback_data
    )

    # Verify feedback was added
    print("\nFeedback added successfully!")
    print(f"Session focus rating: {updated_session.focus_rating}")
    print(f"Session productivity rating: {updated_session.productivity_rating}")
    print(f"Feedback count: {len(updated_session.meta_data['feedback'])}")
    print(f"First feedback item: {updated_session.meta_data['feedback'][0]}")

    return updated_session


async def test_get_user_analytics():
    """Test getting user analytics."""
    # Create mock DB session
    db_session = MockDBSession()

    # Create analytics service
    analytics_service = AnalyticsService(db_session)

    # Create a user and multiple sessions
    user_id = uuid.uuid4()

    # Add several sessions with different characteristics
    session1 = create_sample_session(user_id, uuid.uuid4())
    session1.focus_rating = 4
    session1.productivity_rating = 4
    session1.activity_type = "Programming"

    session2 = create_sample_session(user_id, uuid.uuid4())
    session2.focus_rating = 5
    session2.productivity_rating = 5
    session2.activity_type = "Reading"

    session3 = create_sample_session(user_id, uuid.uuid4())
    session3.focus_rating = 3
    session3.productivity_rating = 3
    session3.activity_type = "Programming"

    # Add sessions to mock DB
    db_session.add_session(session1)
    db_session.add_session(session2)
    db_session.add_session(session3)

    # Get analytics
    print(f"\nGetting analytics for user {user_id}...")
    analytics = await analytics_service.get_user_analytics(user_id)

    # Display analytics
    print("\nUser Analytics:")
    print(f"Total sessions: {analytics.total_sessions}")
    print(f"Total focus time: {analytics.total_focus_time} minutes")
    print(f"Average productivity: {analytics.average_productivity}")
    print(f"Productivity trend: {analytics.productivity_trend}")
    print(f"Most productive times: {analytics.most_productive_times}")
    print(f"Preferred activity types: {analytics.preferred_activity_types}")

    return analytics


async def test_get_focus_pattern_insights():
    """Test getting focus pattern insights."""
    # Create mock DB session
    db_session = MockDBSession()

    # Create analytics service
    analytics_service = AnalyticsService(db_session)

    # Create a user and multiple sessions
    user_id = uuid.uuid4()
    partner_id = uuid.uuid4()

    # Add several sessions with different characteristics
    for i in range(3):
        session = create_sample_session(user_id, uuid.uuid4())
        session.meta_data["participants"] = [str(user_id), str(partner_id)]
        session.meta_data["feedback"] = [
            {
                "user_id": str(user_id),
                "focus_rating": 4 + i % 2,
                "productivity_rating": 4 + i % 2,
                "distraction_level": 2,
                "notes": f"Session {i+1}",
                "timestamp": (datetime.now() - timedelta(days=i)).isoformat(),
            }
        ]
        session.activity_type = "Programming" if i % 2 == 0 else "Reading"
        db_session.add_session(session)

    # Get insights
    print(f"\nGetting focus pattern insights for user {user_id}...")
    insights = await analytics_service.get_focus_pattern_insights(user_id)

    # Display insights
    print("\nFocus Pattern Insights:")
    print(f"Message: {insights['message']}")
    print("\nInsights:")
    for idx, insight in enumerate(insights["insights"]):
        print(
            f"{idx+1}. [{insight['type']}] {insight['insight']} (Confidence: {insight['confidence']})"
        )

    return insights


async def run_all_tests():
    """Run all tests."""
    print("=== Running AnalyticsService Manual Tests ===")

    await test_add_feedback()
    await test_get_user_analytics()
    await test_get_focus_pattern_insights()

    print("\n=== All Manual Tests Completed Successfully ===")


if __name__ == "__main__":
    asyncio.run(run_all_tests())
