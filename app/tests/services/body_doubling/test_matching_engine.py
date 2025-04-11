"""Unit tests for the MatchingEngine component."""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.body_doubling_model import BodyDoublingSessionModel
from app.models.enums_model import SessionStatus, SessionType, ActivityType
from app.services.body_doubling.matching_engine import MatchingEngine
from app.services.body_doubling.session_manager import SessionManager


@pytest.fixture
def mock_db():
    """Create a mock database session."""
    mock = AsyncMock(spec=AsyncSession)
    return mock


@pytest.fixture
def sample_user_id():
    """Return a sample user ID."""
    return UUID("11111111-1111-1111-1111-111111111111")


@pytest.fixture
def sample_match_id():
    """Return a sample match user ID."""
    return UUID("33333333-3333-3333-3333-333333333333")


@pytest.fixture
def sample_session_id():
    """Return a sample session ID."""
    return UUID("22222222-2222-2222-2222-222222222222")


@pytest.fixture
def sample_request_id():
    """Return a sample match request ID."""
    return UUID("44444444-4444-4444-4444-444444444444")


@pytest.fixture
def mock_session_manager(mock_db):
    """Create a mock SessionManager."""
    mock = AsyncMock(spec=SessionManager)
    mock.db = mock_db  # Add the db attribute to the mock
    return mock


@pytest.fixture
def matching_engine(mock_db, mock_session_manager):
    """Create a MatchingEngine with mock dependencies."""
    engine = MatchingEngine(mock_session_manager)
    return engine


@pytest.fixture
def sample_user_prefs():
    """Return sample user preferences."""
    return {
        "work_style": "focused",
        "focus_level": "high",
        "preferred_tasks": ["coding", "writing"],
        "preferred_activity_types": ["work", "study"],
    }


@pytest.fixture
def sample_match_prefs():
    """Return sample match preferences."""
    return {
        "work_style": "focused",
        "focus_level": "high",
        "preferred_tasks": ["coding", "reading"],
        "preferred_activity_types": ["work", "creative"],
    }


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
        meta_data={
            "preferences": {
                "work_style": "focused",
                "focus_level": "high",
                "preferred_tasks": ["coding", "writing"],
                "preferred_activity_types": ["work", "study"],
            }
        },
    )


@pytest.fixture
def sample_match_session(sample_match_id, sample_session_id):
    """Create a sample match session."""
    return BodyDoublingSessionModel(
        id=uuid4(),
        user_id=sample_match_id,
        host_id=sample_match_id,
        session_type=SessionType.ONE_ON_ONE,
        status=SessionStatus.ACTIVE,
        start_time=datetime.now(),
        activity_type=ActivityType.WORK,
        max_participants=2,
        meta_data={
            "preferences": {
                "work_style": "focused",
                "focus_level": "high",
                "preferred_tasks": ["coding", "reading"],
                "preferred_activity_types": ["work", "creative"],
            }
        },
    )


@pytest.fixture
def sample_match_criteria():
    """Return sample match criteria."""
    return {
        "activity_type": "WORK",
        "min_score": 10,
        "preferences": {
            "work_style": "focused",
            "focus_level": "high",
            "preferred_tasks": ["coding", "writing"],
            "preferred_activity_types": ["work", "study"],
        },
        "work_style_important": True,
    }


class TestMatchingEngine:
    """Test the MatchingEngine class."""

    def test_score_preferences_match(self, matching_engine, sample_user_prefs, sample_match_prefs):
        """Test scoring preferences match."""
        # Act
        score = matching_engine._score_preferences_match(sample_user_prefs, sample_match_prefs)

        # Assert - should match on work_style, focus_level, some tasks, some activities
        assert score > 0
        assert score == 10.0 + 8.0 + 5.0 + 4.0  # Based on our algorithm

    def test_score_preferences_match_empty(self, matching_engine):
        """Test scoring preferences match with empty preferences."""
        # Act
        score = matching_engine._score_preferences_match({}, {})

        # Assert
        assert score == 0.0

    def test_score_history_compatibility(self, matching_engine):
        """Test scoring history compatibility."""
        # Arrange
        user_history = [
            {"productivity_rating": 4, "duration_minutes": 60},
            {"productivity_rating": 5, "duration_minutes": 45},
        ]
        match_history = [
            {"productivity_rating": 4, "duration_minutes": 55},
            {"productivity_rating": 3, "duration_minutes": 50},
        ]

        # Act
        score = matching_engine._score_history_compatibility(user_history, match_history)

        # Assert - should match on productivity and similar duration
        assert score > 0
        assert score == 5.0 + 4.0  # Based on our algorithm

    def test_score_history_compatibility_no_history(self, matching_engine):
        """Test scoring history compatibility with no history."""
        # Act
        score = matching_engine._score_history_compatibility(None, None)

        # Assert
        assert score == 0.0

    def test_calculate_match_score(self, matching_engine, sample_user_prefs, sample_match_prefs):
        """Test calculating overall match score."""
        # Arrange
        criteria = {"work_style_important": True}
        user_history = [{"productivity_rating": 4, "duration_minutes": 60}]
        match_history = [{"productivity_rating": 4, "duration_minutes": 55}]

        # Act
        score = matching_engine._calculate_match_score(
            sample_user_prefs, sample_match_prefs, criteria, user_history, match_history
        )

        # Assert
        assert score > 0
        # Base score + history score + criteria bonus
        expected_score = (10.0 + 8.0 + 5.0 + 4.0) + (5.0 + 4.0) + 5.0
        assert score == expected_score

    @pytest.mark.asyncio
    async def test_find_matching_users(
        self,
        matching_engine,
        mock_session_manager,
        sample_user_id,
        sample_match_id,
        sample_user_prefs,
        sample_match_criteria,
        sample_match_session,
    ):
        """Test finding matching users."""
        # Arrange
        mock_session_manager.get_active_sessions.return_value = [sample_match_session]

        # Act
        matches = await matching_engine.find_matching_users(
            sample_user_id, sample_user_prefs, sample_match_criteria
        )

        # Assert
        assert len(matches) > 0
        assert matches[0]["user_id"] == str(sample_match_id)
        assert matches[0]["score"] > sample_match_criteria["min_score"]

    @pytest.mark.asyncio
    async def test_find_matching_users_no_matches(
        self, matching_engine, mock_session_manager, sample_user_id, sample_user_prefs
    ):
        """Test finding matching users when no matches exist."""
        # Arrange
        mock_session_manager.get_active_sessions.return_value = []
        criteria = {"min_score": 10}

        # Act
        matches = await matching_engine.find_matching_users(
            sample_user_id, sample_user_prefs, criteria
        )

        # Assert
        assert len(matches) == 0

    @pytest.mark.asyncio
    async def test_request_match(
        self, matching_engine, mock_db, mock_session_manager, sample_user_id, sample_match_criteria
    ):
        """Test requesting a match."""
        # Arrange
        sample_session = BodyDoublingSessionModel(
            id=uuid4(),
            user_id=sample_user_id,
            host_id=sample_user_id,
            session_type=SessionType.ONE_ON_ONE,
            status=SessionStatus.PENDING,
        )
        mock_session_manager.get_active_session.return_value = None
        mock_session_manager.create_session.return_value = sample_session

        # Act
        result = await matching_engine.request_match(sample_user_id, sample_match_criteria)

        # Assert
        assert result == sample_session
        assert mock_session_manager.get_active_session.called
        assert mock_session_manager.create_session.called
        # Note: We're not checking mock_db.commit/refresh as they're internal to the session_manager

    @pytest.mark.asyncio
    async def test_request_match_already_active(
        self,
        matching_engine,
        mock_session_manager,
        sample_user_id,
        sample_match_criteria,
        sample_session,
    ):
        """Test requesting a match when user already has an active session."""
        # Arrange
        mock_session_manager.get_active_session.return_value = sample_session

        # Act/Assert
        with pytest.raises(HTTPException) as exc_info:
            await matching_engine.request_match(sample_user_id, sample_match_criteria)
        assert exc_info.value.status_code == 400
        assert "already has an active session" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_accept_match(
        self, matching_engine, mock_db, mock_session_manager, sample_match_id, sample_request_id
    ):
        """Test accepting a match request."""
        # Arrange
        from sqlalchemy import Update
        from sqlalchemy.ext.asyncio import AsyncSession

        # Create a session with empty metadata that will be updated
        request_session = BodyDoublingSessionModel(
            id=sample_request_id,
            user_id=uuid4(),
            host_id=uuid4(),
            session_type=SessionType.ONE_ON_ONE,
            status=SessionStatus.PENDING,
            meta_data={},
        )

        # Mock the session_manager behavior
        mock_session_manager.get_session_by_id.return_value = request_session
        mock_session_manager.get_active_session.return_value = None

        # Create a mock for db.execute to handle the update call
        async def mock_execute(query):
            # This simulates the database update by setting the session status to ACTIVE
            request_session.status = SessionStatus.ACTIVE
            if not request_session.meta_data.get("participants"):
                request_session.meta_data["participants"] = []
            if str(sample_match_id) not in request_session.meta_data["participants"]:
                request_session.meta_data["participants"].append(str(sample_match_id))

            # Return a mock result object compatible with SQLAlchemy's execute()
            result_mock = AsyncMock()
            return result_mock

        # Set up the mock db
        mock_db.execute.side_effect = mock_execute

        # Act
        result = await matching_engine.accept_match(sample_match_id, sample_request_id)

        # Assert
        assert result == request_session
        assert result.status == SessionStatus.ACTIVE
        assert str(sample_match_id) in result.meta_data.get("participants", [])
        assert mock_session_manager.get_session_by_id.called
        assert mock_session_manager.get_active_session.called

    @pytest.mark.asyncio
    async def test_accept_match_not_found(
        self, matching_engine, mock_session_manager, sample_match_id, sample_request_id
    ):
        """Test accepting a match request that doesn't exist."""
        # Arrange
        mock_session_manager.get_session_by_id.return_value = None

        # Act/Assert
        with pytest.raises(HTTPException) as exc_info:
            await matching_engine.accept_match(sample_match_id, sample_request_id)
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_accept_match_not_pending(
        self, matching_engine, mock_session_manager, sample_match_id, sample_request_id
    ):
        """Test accepting a match request that is not pending."""
        # Arrange
        request_session = BodyDoublingSessionModel(
            id=sample_request_id,
            status=SessionStatus.ACTIVE,
        )
        mock_session_manager.get_session_by_id.return_value = request_session

        # Act/Assert
        with pytest.raises(HTTPException) as exc_info:
            await matching_engine.accept_match(sample_match_id, sample_request_id)
        assert exc_info.value.status_code == 400
        # Print the actual error message for debugging
        print(f"Error message: {exc_info.value.detail}")
        # Accept any error message about status not being valid
        assert (
            "status" in exc_info.value.detail.lower() or "active" in exc_info.value.detail.lower()
        )

    @pytest.mark.asyncio
    async def test_accept_match_partner_already_active(
        self, matching_engine, mock_session_manager, sample_match_id, sample_request_id
    ):
        """Test accepting a match when partner already has an active session."""
        # Arrange
        request_session = BodyDoublingSessionModel(
            id=sample_request_id,
            status=SessionStatus.PENDING,
        )
        active_session = BodyDoublingSessionModel(
            id=uuid4(),
            status=SessionStatus.ACTIVE,
        )
        mock_session_manager.get_session_by_id.return_value = request_session
        mock_session_manager.get_active_session.return_value = active_session

        # Act/Assert
        with pytest.raises(HTTPException) as exc_info:
            await matching_engine.accept_match(sample_match_id, sample_request_id)
        assert exc_info.value.status_code == 400
        assert "already has an active session" in exc_info.value.detail
