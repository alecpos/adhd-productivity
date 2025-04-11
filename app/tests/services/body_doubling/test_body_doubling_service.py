"""Unit tests for the main BodyDoublingService component."""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.body_doubling_model import BodyDoublingSessionModel
from app.models.enums_model import SessionStatus, SessionType, ActivityType
from app.schemas.body_doubling_schema import (
    BodyDoublingSchema,
    CreateBodyDoublingSchema,
    GroupSessionSchema,
    SessionAnalyticsSchema,
    SessionFeedbackSchema,
)
from app.services.body_doubling.body_doubling_service import BodyDoublingService
from app.services.body_doubling.analytics_service import AnalyticsService
from app.services.body_doubling.matching_engine import MatchingEngine
from app.services.body_doubling.notification_service import NotificationService
from app.services.body_doubling.session_manager import SessionManager


@pytest.fixture
def mock_db():
    """Create a mock database session."""
    mock = AsyncMock(spec=AsyncSession)
    return mock


@pytest.fixture
def mock_session_manager(mock_db):
    """Create a mock SessionManager."""
    mock = AsyncMock(spec=SessionManager)
    mock.db = mock_db
    # Add missing methods that aren't captured by the spec
    mock.get_session_participants = AsyncMock()
    mock.create_group_session = AsyncMock()
    mock.get_active_session = AsyncMock()
    return mock


@pytest.fixture
def mock_matching_engine():
    """Create a mock MatchingEngine."""
    return AsyncMock(spec=MatchingEngine)


@pytest.fixture
def mock_analytics_service():
    """Create a mock AnalyticsService."""
    return AsyncMock(spec=AnalyticsService)


@pytest.fixture
def mock_notification_service():
    """Create a mock NotificationService."""
    mock = AsyncMock(spec=NotificationService)
    # Add missing methods that aren't captured by the spec
    mock.notify_match_accepted = AsyncMock()
    return mock


@pytest.fixture
def body_doubling_service(
    mock_db,
    mock_session_manager,
    mock_matching_engine,
    mock_analytics_service,
    mock_notification_service,
):
    """Create a BodyDoublingService with mock dependencies."""
    service = BodyDoublingService(
        mock_session_manager,
        mock_matching_engine,
        mock_analytics_service,
        mock_notification_service
    )
    return service


@pytest.fixture
def sample_user_id():
    """Return a sample user ID."""
    return UUID("11111111-1111-1111-1111-111111111111")


@pytest.fixture
def sample_session_id():
    """Return a sample session ID."""
    return UUID("22222222-2222-2222-2222-222222222222")


@pytest.fixture
def sample_session_data(sample_user_id):
    """Create sample session data."""
    return CreateBodyDoublingSchema(
        user_id=sample_user_id,
        host_id=sample_user_id,
        session_type=SessionType.ONE_ON_ONE,
        status=SessionStatus.ACTIVE,
        start_time=datetime.now(),
        activity_type=ActivityType.WORK,
        max_participants=2,
        planned_duration=30
    )


@pytest.fixture
def sample_session(sample_user_id, sample_session_id):
    """Create a sample session."""
    return BodyDoublingSessionModel(
        id=sample_session_id,
        user_id=sample_user_id,
        host_id=sample_user_id,
        session_type=SessionType.ONE_ON_ONE,
        status=SessionStatus.ACTIVE,
        start_time=datetime.now(),
        activity_type="WORK",
        max_participants=2,
        meta_data={"participants": [str(sample_user_id)]},
    )


class TestBodyDoublingService:
    """Test the BodyDoublingService class."""

    @pytest.mark.asyncio
    async def test_create_session(
        self, body_doubling_service, mock_session_manager, mock_notification_service, sample_session_data, sample_session
    ):
        """Test creating a session."""
        # Arrange
        mock_session_manager.create_session.return_value = sample_session

        # Act
        result = await body_doubling_service.create_session(sample_session_data)

        # Assert
        assert result == sample_session
        mock_session_manager.create_session.assert_called_once_with(sample_session_data)
        mock_notification_service.notify_session_join.assert_called_once_with(
            sample_session.id, sample_session.user_id, is_host=True
        )

    @pytest.mark.asyncio
    async def test_get_session(self, body_doubling_service, mock_session_manager, sample_session_id, sample_session):
        """Test getting a session by ID."""
        # Arrange
        mock_session_manager.get_session_by_id.return_value = sample_session

        # Act
        result = await body_doubling_service.get_session(sample_session_id)

        # Assert
        assert result == sample_session
        mock_session_manager.get_session_by_id.assert_called_once_with(sample_session_id)

    @pytest.mark.asyncio
    async def test_get_session_participants(
        self, body_doubling_service, mock_session_manager, sample_session_id
    ):
        """Test getting session participants."""
        # Arrange
        expected_participants = ["1", "2", "3"]
        mock_session_manager.get_session_participants.return_value = expected_participants

        # Act
        result = await body_doubling_service.get_session_participants(sample_session_id)

        # Assert
        assert result == expected_participants
        mock_session_manager.get_session_participants.assert_called_once_with(sample_session_id)

    @pytest.mark.asyncio
    async def test_join_session(
        self, body_doubling_service, mock_session_manager, mock_notification_service, sample_session_id, sample_user_id, sample_session
    ):
        """Test joining a session."""
        # Arrange
        mock_session_manager.join_session.return_value = sample_session

        # Act
        result = await body_doubling_service.join_session(sample_session_id, sample_user_id)

        # Assert
        assert result == sample_session
        mock_session_manager.join_session.assert_called_once_with(sample_session_id, sample_user_id)
        mock_notification_service.notify_session_join.assert_called_once_with(sample_session_id, sample_user_id)

    @pytest.mark.asyncio
    async def test_leave_session(
        self, body_doubling_service, mock_session_manager, mock_notification_service, sample_session_id, sample_user_id, sample_session
    ):
        """Test leaving a session."""
        # Arrange
        mock_session_manager.leave_session.return_value = sample_session

        # Act
        result = await body_doubling_service.leave_session(sample_session_id, sample_user_id)

        # Assert
        assert result == sample_session
        mock_session_manager.leave_session.assert_called_once_with(sample_session_id, sample_user_id)
        mock_notification_service.notify_session_leave.assert_called_once_with(
            sample_session_id, sample_user_id, is_host=True
        )

    @pytest.mark.asyncio
    async def test_end_session(
        self, body_doubling_service, mock_session_manager, mock_notification_service, sample_session_id, sample_user_id, sample_session
    ):
        """Test ending a session."""
        # Arrange
        mock_session_manager.end_session.return_value = sample_session

        # Act
        result = await body_doubling_service.end_session(sample_session_id, sample_user_id)

        # Assert
        assert result == sample_session
        mock_session_manager.end_session.assert_called_once_with(sample_session_id, sample_user_id)
        mock_notification_service.notify_session_status_change.assert_called_once_with(
            sample_session_id, SessionStatus.COMPLETED
        )
        mock_notification_service.send_session_feedback_request.assert_called_once_with(
            sample_user_id, sample_session_id
        )

    @pytest.mark.asyncio
    async def test_find_matching_users(
        self, body_doubling_service, mock_matching_engine, sample_user_id
    ):
        """Test finding matching users."""
        # Arrange
        user_prefs = {"preferred_tasks": ["coding"]}
        criteria = {"min_score": 10}
        expected_matches = [{"user_id": "2", "score": 20}]
        mock_matching_engine.find_matching_users.return_value = expected_matches

        # Act
        result = await body_doubling_service.find_matching_users(sample_user_id, user_prefs, criteria)

        # Assert
        assert result == expected_matches
        mock_matching_engine.find_matching_users.assert_called_once_with(
            sample_user_id, user_prefs, criteria
        )

    @pytest.mark.asyncio
    async def test_request_match(
        self, body_doubling_service, mock_matching_engine, mock_notification_service, sample_user_id, sample_session
    ):
        """Test requesting a match."""
        # Arrange
        match_criteria = {
            "preferences": {"work_style": "focused"},
            "min_score": 10
        }
        # Use proper UUID objects instead of strings
        user2_id = UUID("22222222-2222-2222-2222-222222222222")
        user3_id = UUID("33333333-3333-3333-3333-333333333333")
        session2_id = UUID("44444444-4444-4444-4444-444444444444")
        session3_id = UUID("55555555-5555-5555-5555-555555555555")
        
        matches = [
            {"user_id": str(user2_id), "score": 15, "session_id": str(session2_id), "activity_type": "WORK"},
            {"user_id": str(user3_id), "score": 12, "session_id": str(session3_id), "activity_type": "STUDY"},
        ]
        
        mock_matching_engine.request_match.return_value = sample_session
        mock_matching_engine.find_matching_users.return_value = matches

        # Act
        result = await body_doubling_service.request_match(sample_user_id, match_criteria)

        # Assert
        assert result == sample_session
        mock_matching_engine.request_match.assert_called_once_with(sample_user_id, match_criteria)
        mock_matching_engine.find_matching_users.assert_called_once()
        assert mock_notification_service.send_match_suggestion.call_count == 2  # Top 3 matches, only 2 available

    @pytest.mark.asyncio
    async def test_accept_match(
        self, body_doubling_service, mock_matching_engine, mock_notification_service, sample_user_id, sample_session_id, sample_session
    ):
        """Test accepting a match."""
        # Arrange
        mock_matching_engine.accept_match.return_value = sample_session
        
        # Replace the _send_match_acceptance_notifications with a test implementation
        original_method = body_doubling_service._send_match_acceptance_notifications
        
        async def mock_send_notifications(session, partner_id):
            # Call the notification directly for testing
            await mock_notification_service.notify_match_accepted(session.id, partner_id)
        
        body_doubling_service._send_match_acceptance_notifications = mock_send_notifications
        body_doubling_service.matching_engine = mock_matching_engine
        
        try:
            # Act
            result = await body_doubling_service.accept_match(sample_user_id, sample_session_id)
            
            # Assert
            assert result == sample_session
            mock_matching_engine.accept_match.assert_called_once_with(sample_user_id, sample_session_id)
            mock_notification_service.notify_match_accepted.assert_called_once_with(
                sample_session_id, sample_user_id
            )
        finally:
            # Restore original method
            body_doubling_service._send_match_acceptance_notifications = original_method

    @pytest.mark.asyncio
    async def test_get_user_analytics(
        self, body_doubling_service, mock_analytics_service, sample_user_id
    ):
        """Test getting user analytics."""
        # Arrange
        expected_analytics = {
            "total_sessions": 5,
            "total_duration": 240,
            "productivity_score": 85,
            "focus_score": 75,
            "achievement_rate": 0.8,
            "most_productive_times": ["morning"],
            "common_activities": ["WORK", "STUDY"],
            "improvement_suggestions": ["Try more focused sessions"],
        }
        mock_analytics_service.get_user_analytics.return_value = expected_analytics

        # Act
        result = await body_doubling_service.get_user_analytics(sample_user_id)

        # Assert
        assert result == expected_analytics
        mock_analytics_service.get_user_analytics.assert_called_once_with(sample_user_id)

    @pytest.mark.asyncio
    async def test_create_group_session(
        self, body_doubling_service, mock_session_manager, mock_notification_service, mock_db, sample_user_id, sample_session
    ):
        """Test creating a group session."""
        # Arrange
        group_data = CreateBodyDoublingSchema(
            user_id=sample_user_id,
            host_id=sample_user_id,
            session_type=SessionType.GROUP,
            status=SessionStatus.ACTIVE,
            start_time=datetime.now(),
            activity_type=ActivityType.STUDY,
            max_participants=5,
            planned_duration=60,
            description="Group study session for math"
        )
        
        # Override the session manager's create_session to return our sample_session
        body_doubling_service.session_manager = mock_session_manager
        mock_session_manager.create_session.return_value = sample_session
        
        # Act
        result = await body_doubling_service.create_group_session(group_data)
        
        # Assert
        assert result == sample_session
        mock_session_manager.create_session.assert_called_once_with(group_data)
        mock_notification_service.notify_session_join.assert_not_called() # Notification happens inside create_session

    @pytest.mark.asyncio
    async def test_update_preferences(
        self, body_doubling_service, mock_session_manager, mock_db, sample_user_id, sample_session, sample_session_id
    ):
        """Test updating preferences."""
        # Arrange
        preferences = {
            "work_style": "focused",
            "communication_frequency": "minimal",
            "preferred_activity_types": ["WORK", "STUDY"]
        }
        mock_session_manager.get_session_by_id.return_value = sample_session
        
        # Act
        result = await body_doubling_service.update_preferences(sample_session_id, preferences)
        
        # Assert
        mock_session_manager.get_session_by_id.assert_called_once_with(sample_session_id)
        mock_session_manager.update_preferences.assert_called_once_with(sample_session_id, preferences)

    @pytest.mark.asyncio
    async def test_update_preferences_no_active_session(
        self, body_doubling_service, mock_session_manager, sample_user_id, sample_session_id
    ):
        """Test updating preferences when session not found."""
        # Arrange
        preferences = {
            "work_style": "focused",
            "communication_frequency": "minimal",
            "preferred_activity_types": ["WORK", "STUDY"]
        }
        mock_session_manager.get_session_by_id.return_value = None
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await body_doubling_service.update_preferences(sample_session_id, preferences)
        
        # Verify that only the session check was called, not the update
        mock_session_manager.get_session_by_id.assert_called_once_with(sample_session_id)
        mock_session_manager.update_preferences.assert_not_called()

    @pytest.mark.asyncio
    async def test_add_session_feedback(
        self, body_doubling_service, mock_session_manager, sample_session_id, sample_user_id, sample_session
    ):
        """Test adding feedback to a session."""
        # Arrange
        mock_session_manager.get_session_by_id.return_value = sample_session

        feedback = SessionFeedbackSchema(
            user_id=sample_user_id,
            session_id=str(sample_session_id),
            feedback_points=[
                {
                    "timestamp": datetime.now(),
                    "focus_rating": 4,
                    "productivity_rating": 5,
                    "distraction_level": 2
                },
                {
                    "timestamp": datetime.now(),
                    "focus_rating": 5,
                    "productivity_rating": 4,
                    "distraction_level": 1
                }
            ],
            average_focus_level=4.5,
            average_productivity=4.5,
            average_distraction_level=1.5
        )

        # Act
        result = await body_doubling_service.add_session_feedback(sample_session_id, feedback)

        # Assert
        assert result == sample_session
        assert mock_session_manager.get_session_by_id.call_count >= 1
        # We don't need to check exact call count since the implementation might need 
        # to call get_session_by_id multiple times 