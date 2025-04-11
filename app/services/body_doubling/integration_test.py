#!/usr/bin/env python
"""Integration test for AnalyticsService with a real database connection.

This script provides a complete end-to-end test of the AnalyticsService
with a real database connection. It requires a working database setup.

To run:
    python -m app.services.body_doubling.integration_test
"""

import asyncio
import uuid
import sys
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Add project root to path if needed
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

# Import required components
try:
    from app.database import get_session, init_db
    from app.services.body_doubling.analytics_service import AnalyticsService
    from app.models.body_doubling_model import BodyDoublingSessionModel
    from app.models.enums_model import SessionStatus, SessionType
except ImportError as e:
    logger.error(f"Import error: {e}")
    logger.error("Make sure the database and model dependencies are properly set up")
    sys.exit(1)

async def create_test_session(db, user_id=None, completed=True):
    """Create a test session in the database."""
    if user_id is None:
        user_id = uuid.uuid4()

    now = datetime.now()
    session = BodyDoublingSessionModel(
        id=uuid.uuid4(),
        user_id=user_id,
        host_id=user_id,
        title="Integration Test Session",
        description="Session for integration testing",
        start_time=now - timedelta(hours=2),
        end_time=now - timedelta(hours=1) if completed else None,
        status=SessionStatus.COMPLETED if completed else SessionStatus.ACTIVE,
        session_type=SessionType.WORKING,
        activity_type="Programming",
        focus_rating=None,
        productivity_rating=None,
        meta_data={
            "participants": [str(user_id), str(uuid.uuid4())],
            "feedback": []
        }
    )

    db.add(session)
    await db.commit()
    await db.refresh(session)

    logger.info(f"Created test session: {session.id}")
    return session

async def cleanup_test_sessions(db, session_ids):
    """Clean up test sessions from the database."""
    for session_id in session_ids:
        try:
            # Find and delete the session
            session = await db.get(BodyDoublingSessionModel, session_id)
            if session:
                await db.delete(session)

            logger.info(f"Deleted test session: {session_id}")
        except Exception as e:
            logger.warning(f"Error deleting session {session_id}: {e}")

    await db.commit()
    logger.info("Cleanup completed")

async def test_add_feedback(db, analytics_service):
    """Test adding feedback to a session."""
    # Create a test user and session
    user_id = uuid.uuid4()
    session = await create_test_session(db, user_id)

    # Add feedback
    feedback_data = {
        "focus_rating": 4,
        "productivity_rating": 5,
        "distraction_level": 2,
        "notes": "This was a productive integration test session"
    }

    logger.info(f"Adding feedback for session {session.id}")
    try:
        updated_session = await analytics_service.add_session_feedback(
            session.id, user_id, feedback_data
        )

        # Verify feedback was added
        logger.info("Feedback added successfully!")
        logger.info(f"Session focus rating: {updated_session.focus_rating}")
        logger.info(f"Session productivity rating: {updated_session.productivity_rating}")
        logger.info(f"Feedback count: {len(updated_session.meta_data['feedback'])}")

        assert updated_session.focus_rating == 4
        assert updated_session.productivity_rating == 5
        assert len(updated_session.meta_data['feedback']) == 1

        return session.id
    except Exception as e:
        logger.error(f"Error adding feedback: {e}")
        return session.id

async def test_get_user_analytics(db, analytics_service):
    """Test getting user analytics."""
    # Create a test user and multiple sessions
    user_id = uuid.uuid4()
    session_ids = []

    try:
        # Create 3 sessions with different characteristics
        for i in range(3):
            session = await create_test_session(db, user_id)
            session_ids.append(session.id)

            # Add different ratings
            rating = 3 + i  # 3, 4, 5

            # Add feedback to get ratings
            feedback_data = {
                "focus_rating": rating,
                "productivity_rating": rating,
                "distraction_level": 3 - i,  # 3, 2, 1
                "notes": f"Integration test session {i+1}"
            }

            await analytics_service.add_session_feedback(
                session.id, user_id, feedback_data
            )

            # Set different activity types
            activity_types = ["Programming", "Reading", "Programming"]
            session.activity_type = activity_types[i]
            await db.commit()

        # Get analytics
        logger.info(f"Getting analytics for user {user_id}")
        analytics = await analytics_service.get_user_analytics(user_id)

        # Verify analytics
        logger.info("User Analytics:")
        logger.info(f"Total sessions: {analytics.total_sessions}")
        logger.info(f"Total focus time: {analytics.total_focus_time} minutes")
        logger.info(f"Average productivity: {analytics.average_productivity}")
        logger.info(f"Productivity trend: {analytics.productivity_trend}")
        logger.info(f"Preferred activity types: {analytics.preferred_activity_types}")

        assert analytics.total_sessions == 3
        assert analytics.total_focus_time == 180  # 3 sessions × 60 minutes
        assert 3.9 < analytics.average_productivity < 4.1  # Should be around 4.0
        assert analytics.productivity_trend == "improving"
        assert "Programming" in analytics.preferred_activity_types

        return session_ids
    except Exception as e:
        logger.error(f"Error testing user analytics: {e}")
        return session_ids

async def test_get_focus_pattern_insights(db, analytics_service, session_ids):
    """Test getting focus pattern insights."""
    if not session_ids:
        logger.warning("No session IDs provided, skipping focus pattern insights test")
        return

    try:
        # Get the user ID from one of the sessions
        session = await db.get(BodyDoublingSessionModel, session_ids[0])
        user_id = session.user_id

        # Get insights
        logger.info(f"Getting focus pattern insights for user {user_id}")
        insights = await analytics_service.get_focus_pattern_insights(user_id)

        # Display insights
        logger.info("Focus Pattern Insights:")
        logger.info(f"Message: {insights['message']}")
        logger.info("Insights:")
        for idx, insight in enumerate(insights["insights"]):
            logger.info(f"{idx+1}. [{insight['type']}] {insight['insight']}")

        assert len(insights["insights"]) > 0
        assert "insights generated successfully" in insights["message"]
    except Exception as e:
        logger.error(f"Error testing focus pattern insights: {e}")

async def run_integration_tests():
    """Run all integration tests."""
    logger.info("=== Starting AnalyticsService Integration Tests ===")

    # Initialize database if needed
    try:
        await init_db()
    except Exception as e:
        logger.warning(f"Database initialization error (may be already initialized): {e}")

    # Create a db session
    session_ids = []
    try:
        async with get_session() as db:
            # Create analytics service
            analytics_service = AnalyticsService(db)

            # Run tests
            feedback_session_id = await test_add_feedback(db, analytics_service)
            if feedback_session_id:
                session_ids.append(feedback_session_id)

            analytics_session_ids = await test_get_user_analytics(db, analytics_service)
            if analytics_session_ids:
                session_ids.extend(analytics_session_ids)

            await test_get_focus_pattern_insights(db, analytics_service, analytics_session_ids)
    except Exception as e:
        logger.error(f"Error during integration tests: {e}")
    finally:
        # Clean up the test data
        try:
            async with get_session() as db:
                await cleanup_test_sessions(db, session_ids)
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

    logger.info("=== AnalyticsService Integration Tests Completed ===")

if __name__ == "__main__":
    # Run the async tests
    asyncio.run(run_integration_tests())
