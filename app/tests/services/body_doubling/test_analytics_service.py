"""Test analytics service."""

from datetime import datetime, timedelta
import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException
from sqlalchemy import JSON

from app.models.body_doubling_model import BodyDoublingSessionModel
from app.models.enums_model import ActivityType, SessionStatus, SessionType
from app.services.body_doubling.analytics_service import AnalyticsService


@pytest.fixture
def mock_db_session():
    """Create a mock database session."""
    mock = AsyncMock()
    return mock


@pytest.fixture
def mock_session_manager(mock_db_session):
    """Create a mock session manager with the db session."""
    mock = AsyncMock()
    mock.db = mock_db_session

    # Create a result for the db execute call that we can set differently in each test
    mock.db.execute_result = None

    # Override execute to return our awaitable result
    async def mock_execute(query):
        return mock.db.execute_result

    mock.db.execute = mock_execute

    return mock


@pytest.fixture
def sample_session():
    """Create a sample session model."""
    now = datetime.now()
    user_id = uuid.uuid4()
    session = MagicMock(spec=BodyDoublingSessionModel)

    # Set up the session attributes
    session.id = uuid.uuid4()
    session.user_id = user_id
    session.host_id = user_id
    session.start_time = now - timedelta(hours=2)
    session.end_time = now - timedelta(hours=1)
    session.status = SessionStatus.COMPLETED
    session.session_type = SessionType.BODY_DOUBLING
    session.activity_type = ActivityType.WORK
    session.task_description = "Test task description"
    session.meta_data = {
        "participants": [str(user_id)],
        "feedback": [
            {
                "user_id": str(user_id),
                "focus_rating": 4,
                "productivity_rating": 4,
                "distraction_level": 2,
                "notes": "Good session",
                "timestamp": (now - timedelta(minutes=65)).isoformat()
            }
        ]
    }
    session.focus_rating = None
    session.productivity_rating = None

    return session


@pytest.mark.asyncio
async def test_get_user_analytics_no_sessions(mock_session_manager):
    """Test getting user analytics when no sessions exist."""
    # Setup
    user_id = uuid.uuid4()

    # Create a result object with the scalars method
    class MockScalars:
        def all(self):
            return []

    class MockResult:
        def scalars(self):
            return MockScalars()

    # Set the execute result
    mock_session_manager.db.execute_result = MockResult()

    # Execute
    analytics_service = AnalyticsService(mock_session_manager)
    result = await analytics_service.get_user_analytics(user_id)

    # Verify
    assert result.total_sessions == 0
    assert result.total_duration == 0
    assert result.completion_rate == 0.0
    assert result.most_productive_times == []
    assert result.preferred_activity_types == []
    assert result.preferred_session_types == []
    assert result.average_focus_rating == 0.0
    assert result.average_productivity_rating == 0.0
    assert result.average_session_duration == 0


@pytest.mark.asyncio
async def test_get_user_analytics_with_sessions(mock_session_manager, sample_session):
    """Test getting user analytics with existing sessions."""
    # Setup
    user_id = sample_session.user_id
    session2 = MagicMock(spec=BodyDoublingSessionModel)
    session2.id = uuid.uuid4()
    session2.user_id = user_id
    session2.host_id = user_id
    session2.start_time = datetime.now() - timedelta(days=1, hours=3)
    session2.end_time = datetime.now() - timedelta(days=1, hours=2)
    session2.status = SessionStatus.COMPLETED
    session2.session_type = SessionType.ONE_ON_ONE
    session2.activity_type = ActivityType.WORK
    session2.task_description = "Second Session"
    session2.meta_data = {
        "participants": [str(user_id)],
        "feedback": [
            {
                "user_id": str(user_id),
                "focus_rating": 3,
                "productivity_rating": 3,
                "timestamp": (datetime.now() - timedelta(days=1, hours=2, minutes=5)).isoformat()
            }
        ]
    }
    session2.focus_rating = None
    session2.productivity_rating = None

    # Create a result object with the scalars method
    class MockScalars:
        def all(self):
            return [sample_session, session2]

    class MockResult:
        def scalars(self):
            return MockScalars()

    # Set the execute result
    mock_session_manager.db.execute_result = MockResult()

    # Execute
    analytics_service = AnalyticsService(mock_session_manager)
    result = await analytics_service.get_user_analytics(user_id)

    # Verify
    assert result.total_sessions == 2
    assert result.total_duration > 0
    assert result.completion_rate > 0
    assert len(result.most_productive_times) > 0
    assert len(result.preferred_activity_types) > 0
    assert len(result.preferred_session_types) > 0
    assert result.average_focus_rating > 0
    assert result.average_productivity_rating > 0
    assert result.average_session_duration > 0


@pytest.mark.asyncio
async def test_get_session_analytics_not_found(mock_session_manager):
    """Test getting session analytics for a non-existent session."""
    # Setup
    session_id = uuid.uuid4()

    # Create a result object that returns None for scalar_one_or_none
    class MockResult:
        def scalar_one_or_none(self):
            return None

    # Set the execute result
    mock_session_manager.db.execute_result = MockResult()

    # Execute and verify exception
    analytics_service = AnalyticsService(mock_session_manager)
    with pytest.raises(HTTPException) as exc_info:
        await analytics_service.get_session_analytics(session_id)
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_get_session_analytics_success(mock_session_manager, sample_session):
    """Test getting analytics for a specific session."""
    # Setup
    session_id = sample_session.id

    # Create a result object with scalar_one_or_none method
    class MockResult:
        def scalar_one_or_none(self):
            return sample_session

    # Set the execute result
    mock_session_manager.db.execute_result = MockResult()

    # Execute
    analytics_service = AnalyticsService(mock_session_manager)
    result = await analytics_service.get_session_analytics(session_id)

    # Verify
    assert result["total_duration"] > 0
    assert result["average_focus_rating"] >= 0
    assert result["average_productivity_rating"] >= 0
    assert result["completion_rate"] >= 0


@pytest.mark.asyncio
async def test_get_session_feedback(mock_session_manager, sample_session):
    """Test getting feedback for a specific session."""
    # Setup
    session_id = sample_session.id

    # Create a result object with scalar_one_or_none method
    class MockResult:
        def scalar_one_or_none(self):
            return sample_session

    # Set the execute result
    mock_session_manager.db.execute_result = MockResult()

    # Execute
    analytics_service = AnalyticsService(mock_session_manager)
    result = await analytics_service.get_session_feedback(session_id)

    # Verify
    assert str(result.session_id) == str(session_id)
    assert result.user_id == sample_session.user_id
    assert len(result.feedback_points) > 0
    assert result.average_focus_level > 0
    assert result.average_productivity > 0
    assert result.average_distraction_level > 0


@pytest.mark.asyncio
async def test_add_session_feedback_not_found(mock_session_manager):
    """Test adding feedback for a non-existent session."""
    # Setup
    session_id = uuid.uuid4()
    user_id = uuid.uuid4()
    feedback_data = {"focus_rating": 5, "productivity_rating": 5, "notes": "Great session"}

    # Create a result object with scalar_one_or_none method
    class MockResult:
        def scalar_one_or_none(self):
            return None

    # Set the execute result
    mock_session_manager.db.execute_result = MockResult()

    # Execute and verify exception
    analytics_service = AnalyticsService(mock_session_manager)
    with pytest.raises(HTTPException) as exc_info:
        await analytics_service.add_session_feedback(session_id, user_id, feedback_data)
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_add_session_feedback_unauthorized(mock_session_manager, sample_session):
    """Test adding feedback from a user who didn't participate."""
    # Setup
    session_id = sample_session.id
    unauthorized_user_id = uuid.uuid4()  # Different user
    feedback_data = {"focus_rating": 5, "productivity_rating": 5, "notes": "Great session"}

    # Create a result object with scalar_one_or_none method
    class MockResult:
        def scalar_one_or_none(self):
            return sample_session

    # Set the execute result
    mock_session_manager.db.execute_result = MockResult()

    # Execute and verify exception
    analytics_service = AnalyticsService(mock_session_manager)
    with pytest.raises(HTTPException) as exc_info:
        await analytics_service.add_session_feedback(session_id, unauthorized_user_id, feedback_data)
    assert exc_info.value.status_code == 403


@pytest.mark.asyncio
async def test_add_session_feedback_success(mock_session_manager, sample_session):
    """Test successfully adding feedback to a session."""
    # Setup
    session_id = sample_session.id
    user_id = sample_session.user_id
    feedback_data = {"focus_rating": 5, "productivity_rating": 5, "notes": "Great session"}

    # Create a result object with scalar_one_or_none method
    class MockResult:
        def scalar_one_or_none(self):
            return sample_session

    # Set the execute result
    mock_session_manager.db.execute_result = MockResult()

    # Also mock the commit and refresh methods to be async no-ops
    mock_session_manager.db.commit = AsyncMock()
    mock_session_manager.db.refresh = AsyncMock()

    # Execute
    analytics_service = AnalyticsService(mock_session_manager)
    result = await analytics_service.add_session_feedback(session_id, user_id, feedback_data)

    # Verify
    assert result.meta_data["feedback"][-1]["focus_rating"] == 5
    assert result.meta_data["feedback"][-1]["productivity_rating"] == 5
    assert result.meta_data["feedback"][-1]["notes"] == "Great session"


@pytest.mark.asyncio
async def test_get_focus_pattern_insights_no_sessions(mock_session_manager):
    """Test getting focus pattern insights for a user with no sessions."""
    # Setup
    user_id = uuid.uuid4()

    # Create a result object with the scalars method
    class MockScalars:
        def all(self):
            return []

    class MockResult:
        def scalars(self):
            return MockScalars()

    # Set the execute result
    mock_session_manager.db.execute_result = MockResult()

    # Execute
    analytics_service = AnalyticsService(mock_session_manager)
    result = await analytics_service.get_focus_pattern_insights(user_id)

    # Verify
    assert isinstance(result, dict)
    assert "insights" in result
    assert "average_focus_rating" in result
    assert "average_productivity_rating" in result
    assert "total_sessions" in result
    assert len(result["insights"]) == 0
    assert result["total_sessions"] == 0
    assert result["average_focus_rating"] == 0
    assert result["average_productivity_rating"] == 0


@pytest.mark.asyncio
async def test_get_focus_pattern_insights_with_data(mock_session_manager, sample_session):
    """Test getting focus pattern insights with session data."""
    # Setup similar to test_get_user_analytics_with_sessions
    user_id = sample_session.user_id
    session2 = MagicMock(spec=BodyDoublingSessionModel)
    session2.id = uuid.uuid4()
    session2.user_id = user_id
    session2.host_id = user_id
    session2.start_time = datetime.now() - timedelta(days=1, hours=3)
    session2.end_time = datetime.now() - timedelta(days=1, hours=2)
    session2.status = SessionStatus.COMPLETED
    session2.session_type = SessionType.GROUP
    session2.activity_type = ActivityType.STUDY
    session2.meta_data = {
        "participants": [str(user_id)],
        "feedback": [
            {
                "user_id": str(user_id),
                "focus_rating": 3,
                "productivity_rating": 4,
                "timestamp": (datetime.now() - timedelta(days=1, hours=2, minutes=5)).isoformat()
            }
        ]
    }

    # Create a result object with the scalars method
    class MockScalars:
        def all(self):
            return [sample_session, session2]

    class MockResult:
        def scalars(self):
            return MockScalars()

    # Set the execute result
    mock_session_manager.db.execute_result = MockResult()

    # Execute
    analytics_service = AnalyticsService(mock_session_manager)
    result = await analytics_service.get_focus_pattern_insights(user_id)

    # Verify
    assert isinstance(result, dict)
    assert "insights" in result
    assert "average_focus_rating" in result
    assert "average_productivity_rating" in result
    assert "total_sessions" in result
    assert len(result["insights"]) > 0
    assert result["total_sessions"] == 2
    assert result["average_focus_rating"] > 0
    assert result["average_productivity_rating"] > 0


@pytest.mark.asyncio
async def test_calculate_trend():
    """Test trend calculation."""
    analytics_service = AnalyticsService(AsyncMock())

    # Test improving trend
    values = [1, 2, 3, 4, 5]
    assert analytics_service._calculate_trend(values) == "improving"

    # Test declining trend
    values = [5, 4, 3, 2, 1]
    assert analytics_service._calculate_trend(values) == "declining"

    # Test stable trend
    values = [3, 3, 3, 3, 3]
    assert analytics_service._calculate_trend(values) == "stable"
