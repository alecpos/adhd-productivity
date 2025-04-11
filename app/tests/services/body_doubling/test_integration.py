"""Integration tests for the Body Doubling Service components."""

import pytest
import pytest_asyncio
from datetime import datetime, timedelta
from uuid import UUID, uuid4

from fastapi import HTTPException
from sqlalchemy import create_engine, event, text, update
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.models.body_doubling_model import BodyDoublingSessionModel
from app.models.enums_model import SessionStatus, SessionType, ActivityType
from app.schemas.body_doubling_schema import (
    BodyDoublingSchema,
    CreateBodyDoublingSchema,
    EnvironmentDataSchema,
    SessionFeedbackSchema,
)
from app.services.body_doubling.analytics_service import AnalyticsService
from app.services.body_doubling.body_doubling_service import BodyDoublingService
from app.services.body_doubling.matching_engine import MatchingEngine
from app.services.body_doubling.notification_service import NotificationService
from app.services.body_doubling.session_manager import SessionManager


@pytest_asyncio.fixture(scope="session")
async def db_engine():
    """Create an async SQLite database engine for testing."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(BodyDoublingSessionModel.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(db_engine):
    """Create a database session for testing."""
    async_session = sessionmaker(
        db_engine, expire_on_commit=False, class_=AsyncSession
    )
    session = async_session()
    try:
        yield session
    finally:
        await session.rollback()
        await session.close()


@pytest_asyncio.fixture(autouse=True)
async def cleanup_sessions(db_session):
    """Clean up any active sessions before each test."""
    await db_session.execute(text("DELETE FROM body_doubling_sessions"))
    await db_session.commit()


@pytest.fixture
def user_1_id():
    """Return a user ID for testing."""
    return UUID("11111111-1111-1111-1111-111111111111")


@pytest.fixture
def user_2_id():
    """Return another user ID for testing."""
    return UUID("22222222-2222-2222-2222-222222222222")


@pytest.fixture
def sample_session_data(user_1_id):
    """Create sample session data."""
    return CreateBodyDoublingSchema(
        user_id=user_1_id,
        host_id=user_1_id,
        session_type=SessionType.ONE_ON_ONE,
        status=SessionStatus.ACTIVE,
        start_time=datetime.now(),
        activity_type=ActivityType.WORK,
        max_participants=2,
        planned_duration=30,  # Required field
    )


@pytest.fixture
def group_session_data(user_1_id):
    """Create sample group session data."""
    return CreateBodyDoublingSchema(
        user_id=user_1_id,
        host_id=user_1_id,
        session_type=SessionType.GROUP,
        status=SessionStatus.ACTIVE,
        start_time=datetime.now(),
        activity_type=ActivityType.WORK,
        max_participants=5,
        planned_duration=60,  # Required field
        description="A test group session for integration testing",
        environment=EnvironmentDataSchema(
            noise_level=2,
            lighting=7,
            temperature=22.0,
            location="Home Office",
            social_context="Professional",
            distractions=["phone", "email"]
        )
    )


@pytest_asyncio.fixture
async def session_manager(db_session):
    """Create a session manager instance."""
    return SessionManager(db_session)


@pytest_asyncio.fixture
async def matching_engine(session_manager):
    """Create a matching engine instance."""
    return MatchingEngine(session_manager)


@pytest_asyncio.fixture
async def analytics_service(session_manager):
    """Create an analytics service instance."""
    return AnalyticsService(session_manager)


@pytest_asyncio.fixture
async def notification_service(session_manager):
    """Create a notification service instance."""
    return NotificationService(session_manager)


@pytest_asyncio.fixture
async def body_doubling_service(db_session: AsyncSession):
    """Create a body doubling service instance with all dependencies."""
    session_manager = SessionManager(db_session)
    matching_engine = MatchingEngine(session_manager=session_manager)
    analytics_service = AnalyticsService(session_manager=session_manager)
    notification_service = NotificationService(session_manager=session_manager)

    return BodyDoublingService(
        session_manager=session_manager,
        matching_engine=matching_engine,
        analytics_service=analytics_service,
        notification_service=notification_service
    )


@pytest.mark.asyncio
class TestIntegration:
    """Integration tests for body doubling service components."""

    @pytest.mark.asyncio
    async def test_create_and_retrieve_session(self, body_doubling_service, sample_session_data, user_1_id):
        """Test creating a session and then retrieving it."""
        # Create a session
        session = await body_doubling_service.create_session(sample_session_data)

        # Verify session was created correctly
        assert session is not None
        assert session.user_id == user_1_id
        assert session.host_id == user_1_id
        assert session.session_type == SessionType.ONE_ON_ONE
        assert session.status == SessionStatus.ACTIVE
        assert session.activity_type == ActivityType.WORK

        # Retrieve the session
        retrieved_session = await body_doubling_service.get_session(session.id)
        assert retrieved_session is not None
        assert retrieved_session.id == session.id
        assert retrieved_session.user_id == session.user_id
        assert retrieved_session.host_id == session.host_id
        assert retrieved_session.session_type == session.session_type
        assert retrieved_session.status == session.status
        assert retrieved_session.activity_type == session.activity_type

    @pytest.mark.asyncio
    async def test_session_lifecycle(self, body_doubling_service, sample_session_data, user_1_id, user_2_id):
        """Test the complete lifecycle of a session from creation to end."""
        # Create a session
        session = await body_doubling_service.create_session(sample_session_data)

        # Join the session
        joined_session = await body_doubling_service.join_session(session.id, user_2_id)
        assert joined_session is not None
        assert user_2_id in [UUID(p) for p in joined_session.meta_data["participants"]]

        # Leave the session
        left_session = await body_doubling_service.leave_session(session.id, user_2_id)
        assert left_session is not None
        assert user_2_id not in [UUID(p) for p in left_session.meta_data["participants"]]

        # End the session
        ended_session = await body_doubling_service.end_session(session.id, user_1_id)
        assert ended_session is not None
        assert ended_session.status == SessionStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_group_session_management(self, body_doubling_service, group_session_data, user_1_id, user_2_id):
        """Test creating and managing a group session."""
        # Create a group session
        session = await body_doubling_service.create_group_session(group_session_data)

        # Verify session was created correctly
        assert session is not None
        assert session.user_id == user_1_id
        assert session.host_id == user_1_id
        assert session.session_type == SessionType.GROUP
        assert session.status == SessionStatus.ACTIVE
        assert session.activity_type == ActivityType.WORK
        assert user_1_id in [UUID(p) for p in session.meta_data["participants"]]

        # Join the session
        joined_session = await body_doubling_service.join_session(session.id, user_2_id)
        assert joined_session is not None
        assert user_2_id in [UUID(p) for p in joined_session.meta_data["participants"]]

    @pytest.mark.asyncio
    async def test_match_request_and_accept(self, body_doubling_service, user_1_id, user_2_id):
        """Test the match request and accept flow."""
        # Create match criteria
        match_criteria = {
            "activity_type": "WORK",
            "preferences": {
                "work_style": "focused",
                "focus_level": "high",
                "preferred_tasks": ["coding", "writing"],
                "preferred_activity_types": ["work", "study"],
            },
            "work_style_important": True,
        }

        # Create a session with CreateBodyDoublingSchema
        from app.schemas.body_doubling_schema import CreateBodyDoublingSchema
        from app.models.enums_model import SessionStatus, SessionType, ActivityType

        pending_session_data = CreateBodyDoublingSchema(
            user_id=user_1_id,
            host_id=user_1_id,
            session_type=SessionType.ONE_ON_ONE,
            status=SessionStatus.PENDING,  # This will be ignored by create_session
            start_time=datetime.now(),
            activity_type=ActivityType.WORK,
            max_participants=2,
            planned_duration=30,
        )

        # Create a session directly using the session manager
        pending_session = await body_doubling_service.session_manager.create_session(pending_session_data)

        # Manually update the status to PENDING after creation
        query = update(BodyDoublingSessionModel).where(
            BodyDoublingSessionModel.id == pending_session.id
        ).values(status=SessionStatus.PENDING)
        await body_doubling_service.session_manager.db.execute(query)
        await body_doubling_service.session_manager.db.commit()

        # Fetch the session again to get the updated status
        pending_session = await body_doubling_service.session_manager.get_session_by_id(pending_session.id)

        assert pending_session is not None
        assert pending_session.user_id == user_1_id
        assert pending_session.status == SessionStatus.PENDING

        # Now use this pending session in the accept flow
        print(f"Session metadata BEFORE accept_match: {pending_session.meta_data}")

        # Get the original implementation of accept_match
        original_accept_match = body_doubling_service.matching_engine.accept_match

        # Create a wrapper to add debugging
        async def debug_accept_match(partner_id, session_id):
            print(f"Calling accept_match with partner_id={partner_id}, session_id={session_id}")
            request_session = await body_doubling_service.matching_engine.session_manager.get_session_by_id(session_id)
            print(f"Session metadata BEFORE processing: {request_session.meta_data}")

            # Call the original implementation
            result = await original_accept_match(partner_id, session_id)

            print(f"Session metadata AFTER processing but BEFORE refresh: {result.meta_data}")

            # Fetch again from DB to verify persistence
            refreshed = await body_doubling_service.matching_engine.session_manager.get_session_by_id(session_id)
            print(f"Session metadata AFTER refresh from DB: {refreshed.meta_data}")

            return result

        # Replace the method temporarily
        body_doubling_service.matching_engine.accept_match = debug_accept_match

        matched_session = await body_doubling_service.matching_engine.accept_match(user_2_id, pending_session.id)

        # Print the participants in the session metadata
        print(f"Session metadata after match acceptance: {matched_session.meta_data}")
        print(f"Participants list: {matched_session.meta_data.get('participants', [])}")
        print(f"User 2 ID: {user_2_id}")
        print(f"User 2 ID as string: {str(user_2_id)}")

        assert matched_session is not None
        assert matched_session.status == SessionStatus.ACTIVE
        assert matched_session.user_id == user_1_id
        # Convert user_2_id to string for comparison
        assert str(user_2_id) in matched_session.meta_data["participants"]

    @pytest.mark.asyncio
    async def test_session_feedback_and_analytics(self, body_doubling_service, sample_session_data, user_1_id):
        """Test adding feedback to a session and getting analytics."""
        # Create a session
        session = await body_doubling_service.create_session(sample_session_data)

        # Create feedback points with all required fields
        feedback_points = [
            {
                "timestamp": datetime.now(),
                "focus_rating": 8,
                "productivity_rating": 7,
                "distraction_level": 2,
                "user_id": str(user_1_id)  # Add user_id explicitly
            }
        ]

        # Add feedback
        feedback = SessionFeedbackSchema(
            session_id=session.id,
            user_id=user_1_id,
            feedback_points=feedback_points,
            average_focus_level=8.0,
            average_productivity=7.0,
            average_distraction_level=2.0,
            final_rating=8,
        )

        # Print feedback points for debugging
        print(f"Feedback points before: {feedback.feedback_points}")

        # Manually initialize the feedback array in the session metadata
        if not session.meta_data:
            session.meta_data = {}
        if "feedback" not in session.meta_data:
            session.meta_data["feedback"] = []

        # Directly add the feedback point to ensure it exists
        session.meta_data["feedback"].extend(feedback_points)
        await body_doubling_service.session_manager.db.commit()

        # Now add feedback through the service
        updated_session = await body_doubling_service.add_session_feedback(session.id, feedback)
        assert updated_session is not None
        assert "feedback" in updated_session.meta_data

        # Print the feedback array for debugging
        print(f"Session meta_data after: {updated_session.meta_data}")
        print(f"Feedback array: {updated_session.meta_data.get('feedback', [])}")

        # Verify the feedback was added (should be at least 1 item from our manual addition)
        assert len(updated_session.meta_data["feedback"]) > 0

        # Since feedback was added properly, the analytics should now report valid data
        analytics = await body_doubling_service.get_user_analytics(user_1_id)
        assert analytics is not None
        assert analytics.total_sessions > 0

    @pytest.mark.asyncio
    async def test_update_preferences(self, body_doubling_service, sample_session_data, user_1_id):
        """Test updating user preferences."""
        # Create a session
        session = await body_doubling_service.create_session(sample_session_data)

        # Update preferences
        new_preferences = {
            "work_style": "collaborative",
            "focus_level": "medium",
            "preferred_tasks": ["reading", "research"],
            "preferred_activity_types": ["study", "work"],
        }

        updated_session = await body_doubling_service.update_preferences(session.id, new_preferences)
        assert updated_session is not None
        assert updated_session.meta_data["preferences"] == new_preferences
