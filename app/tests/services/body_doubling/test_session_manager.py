"""Unit tests for the SessionManager component."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.models.body_doubling_model import BodyDoublingSessionModel
from app.models.enums_model import SessionStatus, SessionType, ActivityType
from app.schemas.body_doubling_schema import CreateBodyDoublingSchema
from app.services.body_doubling.session_manager import SessionManager
from app.services.body_doubling.body_doubling_types import SessionMetaData
from app.utils.route_utils import validation_error


class ScalarsMock:
    """A mock for scalars() return values"""

    def __init__(self, result=None):
        self.result = result if result else []

    def all(self):
        return self.result if isinstance(self.result, list) else [self.result]

    def first(self):
        return (
            self.result[0]
            if self.result and isinstance(self.result, list) and len(self.result) > 0
            else self.result
        )


@pytest.fixture
def mock_db():
    """Create a mock database session."""
    mock = AsyncMock(spec=AsyncSession)
    return mock


@pytest.fixture
def session_manager(mock_db):
    """Create a SessionManager instance with a mock db."""
    return SessionManager(mock_db)


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
        activity_type=ActivityType.WORK,
        planned_duration=30,
        description=None,
        energy_level=None,
        environment_data=None,
    )


@pytest.fixture
def sample_session(sample_user_id, sample_session_id):
    """Create a sample session."""
    return BodyDoublingSessionModel(
        id=sample_session_id,
        user_id=sample_user_id,
        host_id=sample_user_id,
        session_type=SessionType.ONE_ON_ONE,
        activity_type=ActivityType.WORK,
        planned_duration=30,
        task_description=None,
        energy_level=None,
        environment=None,
        status=SessionStatus.ACTIVE,
        start_time=datetime.now(),
        meta_data={
            "participants": [str(sample_user_id)],
            "interactions": [],
            "breaks": [],
            "feedback": None,
        },
    )


class TestSessionManager:
    """Test the SessionManager class."""

    def setup_db_mocks(self, mock_db, execute_side_effect=None):
        """Set up common database mocks with proper async behavior.

        Args:
            mock_db: The database mock to configure
            execute_side_effect: Optional side effect function for execute

        Returns:
            Tuple of (original_execute, mock_db)
        """
        original_execute = mock_db.execute

        if execute_side_effect:
            mock_db.execute = AsyncMock(side_effect=execute_side_effect)
        else:
            mock_db.execute = AsyncMock(return_value=MagicMock())

        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()

        return original_execute, mock_db

    @pytest.mark.asyncio
    async def test_create_session(self, session_manager, mock_db, sample_session_data):
        """Test creating a session."""
        # Setup
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()
        mock_db.add = MagicMock()

        # Execute
        session = await session_manager.create_session(sample_session_data)

        # Verify
        assert mock_db.add.called
        assert mock_db.commit.called
        assert mock_db.refresh.called
        assert session.user_id == sample_session_data.user_id
        assert session.host_id == sample_session_data.host_id
        assert session.session_type == sample_session_data.session_type
        assert session.status == SessionStatus.ACTIVE
        assert session.activity_type == sample_session_data.activity_type

    @pytest.mark.asyncio
    async def test_get_session_by_id_found(
        self, session_manager, mock_db, sample_session, sample_session_id
    ):
        """Test getting a session by ID when it exists."""
        # Create a custom mock for the entire db.execute method
        # This approach ensures we're not trying to await the mock itself

        # Create a results mock that will be returned by execute()
        results_mock = MagicMock()
        results_mock.scalar_one_or_none = MagicMock(return_value=sample_session)

        # Make db.execute return our results when awaited
        async def mock_execute(*args, **kwargs):
            return results_mock

        # Replace the mock's side_effect with our custom function
        mock_db.execute.side_effect = mock_execute

        # Act
        result = await session_manager.get_session_by_id(sample_session_id)

        # Assert
        assert result == sample_session
        assert mock_db.execute.called

    @pytest.mark.asyncio
    async def test_get_session_by_id_not_found(self, session_manager, mock_db, sample_session_id):
        """Test getting a session by ID when it doesn't exist."""
        # Create a custom mock for the entire db.execute method

        # Create a results mock that will be returned by execute()
        results_mock = MagicMock()
        results_mock.scalar_one_or_none = MagicMock(return_value=None)

        # Make db.execute return our results when awaited
        async def mock_execute(*args, **kwargs):
            return results_mock

        # Replace the mock's side_effect with our custom function
        mock_db.execute.side_effect = mock_execute

        # Act
        result = await session_manager.get_session_by_id(sample_session_id)

        # Assert
        assert result is None
        assert mock_db.execute.called

    @pytest.mark.asyncio
    async def test_get_active_session(
        self, session_manager, mock_db, sample_session, sample_user_id
    ):
        """Test getting active session for a user."""
        # Create a custom mock for the entire db.execute method

        # Create a results mock that will be returned by execute()
        results_mock = MagicMock()
        results_mock.scalar_one_or_none = MagicMock(return_value=sample_session)

        # Make db.execute return our results when awaited
        async def mock_execute(*args, **kwargs):
            return results_mock

        # Replace the mock's side_effect with our custom function
        mock_db.execute.side_effect = mock_execute

        # Act
        result = await session_manager.get_active_session(sample_user_id)

        # Assert
        assert result == sample_session
        assert mock_db.execute.called

    @pytest.mark.asyncio
    async def test_get_active_session_none(self, session_manager, mock_db, sample_user_id):
        """Test getting active session when user has none."""
        # Create a custom mock for the entire db.execute method

        # Create a results mock that will be returned by execute()
        results_mock = MagicMock()
        results_mock.scalar_one_or_none = MagicMock(return_value=None)

        # Make db.execute return our results when awaited
        async def mock_execute(*args, **kwargs):
            return results_mock

        # Replace the mock's side_effect with our custom function
        mock_db.execute.side_effect = mock_execute

        # Act
        result = await session_manager.get_active_session(sample_user_id)

        # Assert
        assert result is None
        assert mock_db.execute.called

    @pytest.mark.asyncio
    async def test_join_session(
        self, session_manager, mock_db, sample_session, sample_session_id, sample_user_id
    ):
        """Test joining a session."""
        # Configure the sample session for the test
        sample_session.session_type = SessionType.GROUP
        sample_session.status = SessionStatus.ACTIVE

        # Create a different user id for the session to ensure the test user isn't already a participant
        different_user_id = uuid4()
        sample_session.user_id = different_user_id
        sample_session.meta_data = {"participants": [str(different_user_id)], "join_requests": []}

        # Store original methods
        original_get_session_by_id = session_manager.get_session_by_id

        # Create async mock for session retrieval
        async def mock_get_session_by_id(session_id, **kwargs):
            assert session_id == sample_session_id
            return sample_session

        # Track if execute is called for update
        execute_called = False

        # Set up mocks for database operations
        async def mock_execute(query, **kwargs):
            nonlocal execute_called
            execute_called = True
            # Update the metadata as the real implementation would
            if str(sample_user_id) not in sample_session.meta_data["participants"]:
                sample_session.meta_data["participants"].append(str(sample_user_id))
            return MagicMock()

        # Apply mocks with our helper function
        original_execute, mock_db = self.setup_db_mocks(mock_db, mock_execute)

        try:
            # Apply session manager mocks
            session_manager.get_session_by_id = mock_get_session_by_id

            # Act
            result = await session_manager.join_session(sample_session_id, sample_user_id)

            # Assert
            assert execute_called, "Should update participant list via execute"
            assert str(sample_user_id) in sample_session.meta_data["participants"]
            assert result == sample_session
            assert mock_db.execute.called
            assert mock_db.commit.called
            assert mock_db.refresh.called

        finally:
            # Restore original methods
            session_manager.get_session_by_id = original_get_session_by_id
            mock_db.execute = original_execute

    @pytest.mark.asyncio
    async def test_join_session_already_active(
        self, session_manager, mock_db, sample_session, sample_session_id, sample_user_id
    ):
        """Test joining when user is already in the session."""
        # Configure the test session
        sample_session.session_type = SessionType.GROUP
        sample_session.status = SessionStatus.ACTIVE

        # Important part: User ID is already in participants
        sample_session.meta_data = {
            "participants": [str(sample_user_id), str(sample_session.user_id)],
            "join_requests": [],
        }

        # Store original method
        original_get_session_by_id = session_manager.get_session_by_id

        # Create mock that returns session with user already in participants
        async def mock_get_session_by_id(session_id, **kwargs):
            assert session_id == sample_session_id
            return sample_session

        # Set up tracking for execute
        execute_called = False

        async def mock_execute(*args, **kwargs):
            nonlocal execute_called
            execute_called = True
            return MagicMock()

        # Apply mocks with our helper function
        original_execute, mock_db = self.setup_db_mocks(mock_db, mock_execute)

        try:
            # Apply session manager mocks
            session_manager.get_session_by_id = mock_get_session_by_id

            # Act
            result = await session_manager.join_session(sample_session_id, sample_user_id)

            # Assert - no error should be raised, but execute should not be called
            assert result == sample_session
            assert not execute_called, "Should not update database since user already in session"
            assert mock_db.commit.call_count == 0
            assert mock_db.refresh.call_count == 0

        finally:
            # Restore original method
            session_manager.get_session_by_id = original_get_session_by_id
            mock_db.execute = original_execute

    @pytest.mark.asyncio
    async def test_join_session_not_active(
        self, session_manager, mock_db, sample_session, sample_session_id, sample_user_id
    ):
        """Test joining when session is not active."""
        # Arrange
        sample_session.status = SessionStatus.COMPLETED
        session_manager.get_session_by_id = AsyncMock(return_value=sample_session)
        session_manager.get_active_session = AsyncMock(return_value=None)

        # Act/Assert
        with pytest.raises(HTTPException) as exc_info:
            await session_manager.join_session(sample_session_id, sample_user_id)

        assert exc_info.value.status_code == 400
        assert "not active" in exc_info.value.detail
        session_manager.get_session_by_id.assert_called_once_with(sample_session_id)

    @pytest.mark.asyncio
    async def test_leave_session(
        self, session_manager, mock_db, sample_session, sample_session_id, sample_user_id
    ):
        """Test leaving a group session."""
        # Arrange
        new_user_id = uuid4()
        sample_session.session_type = SessionType.GROUP

        # Make sure the user ID is converted to string
        new_user_id_str = str(new_user_id)
        sample_session.meta_data = {
            "participants": [str(sample_session.user_id), new_user_id_str],
            "join_requests": [],
        }

        # Store original method
        original_get_session_by_id = session_manager.get_session_by_id

        # Mock session_manager.get_session_by_id
        async def mock_get_session_by_id(session_id, **kwargs):
            assert session_id == sample_session_id
            return sample_session

        session_manager.get_session_by_id = AsyncMock(side_effect=mock_get_session_by_id)

        # Set up tracking for execute
        execute_called = False

        async def mock_execute(query, **kwargs):
            nonlocal execute_called
            execute_called = True
            # Simulate update by removing user from participants
            if new_user_id_str in sample_session.meta_data["participants"]:
                sample_session.meta_data["participants"].remove(new_user_id_str)
            return MagicMock()

        # Apply mock DB operations
        original_execute, mock_db = self.setup_db_mocks(mock_db, mock_execute)

        try:
            # Act
            result = await session_manager.leave_session(sample_session_id, new_user_id)

            # Assert
            assert execute_called, "Should update participant list via execute"
            assert mock_db.execute.called
            assert mock_db.commit.called
            assert mock_db.refresh.called
            assert new_user_id_str not in result.meta_data["participants"]
            session_manager.get_session_by_id.assert_called_once_with(sample_session_id)

        finally:
            # Restore original methods
            session_manager.get_session_by_id = original_get_session_by_id
            mock_db.execute = original_execute

    @pytest.mark.asyncio
    async def test_leave_session_not_found(
        self, session_manager, mock_db, sample_session_id, sample_user_id
    ):
        """Test leaving a session that doesn't exist."""
        # Arrange
        session_manager.get_session_by_id = AsyncMock(return_value=None)

        # Act/Assert
        with pytest.raises(HTTPException) as exc_info:
            await session_manager.leave_session(sample_session_id, sample_user_id)

        assert exc_info.value.status_code == 404
        session_manager.get_session_by_id.assert_called_once_with(sample_session_id)

    @pytest.mark.asyncio
    async def test_end_session(
        self, session_manager, mock_db, sample_session, sample_session_id, sample_user_id
    ):
        """Test ending a session."""
        # Store original method
        original_get_session_by_id = session_manager.get_session_by_id

        # Mock session_manager.get_session_by_id
        async def mock_get_session_by_id(session_id, **kwargs):
            assert session_id == sample_session_id
            return sample_session

        session_manager.get_session_by_id = AsyncMock(side_effect=mock_get_session_by_id)

        # Set up tracking for execute
        status_updated = False

        async def mock_execute(query, **kwargs):
            nonlocal status_updated
            status_updated = True
            # Simulate updating the status to COMPLETED
            sample_session.status = SessionStatus.COMPLETED
            return MagicMock()

        # Apply mock DB operations
        original_execute, mock_db = self.setup_db_mocks(mock_db, mock_execute)

        try:
            # Act
            result = await session_manager.end_session(sample_session_id, sample_user_id)

            # Assert
            assert status_updated, "Should update session status via execute"
            assert mock_db.execute.called
            assert mock_db.commit.called
            assert mock_db.refresh.called
            assert result.status == SessionStatus.COMPLETED

        finally:
            # Restore original methods
            session_manager.get_session_by_id = original_get_session_by_id
            mock_db.execute = original_execute

    @pytest.mark.asyncio
    async def test_end_session_not_host(
        self, session_manager, mock_db, sample_session, sample_session_id
    ):
        """Test ending a session when not the host."""
        # Arrange
        different_user_id = uuid4()
        session_manager.get_session_by_id = AsyncMock(return_value=sample_session)

        # Act/Assert
        with pytest.raises(HTTPException) as exc_info:
            await session_manager.end_session(sample_session_id, different_user_id)

        assert exc_info.value.status_code == 403
        assert "only the host" in exc_info.value.detail.lower()
        session_manager.get_session_by_id.assert_called_once_with(sample_session_id)

    @pytest.mark.asyncio
    async def test_get_user_sessions(
        self, session_manager, mock_db, sample_session, sample_user_id
    ):
        """Test getting all sessions for a user."""
        # Arrange
        result_mock = AsyncMock()
        scalars_mock = ScalarsMock([sample_session])
        result_mock.scalars = MagicMock(return_value=scalars_mock)

        mock_db.execute = AsyncMock(return_value=result_mock)

        # Act
        result = await session_manager.get_user_sessions(sample_user_id)

        # Assert
        assert result == [sample_session]
        mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_active_sessions(self, session_manager, mock_db, sample_session):
        """Test getting all active sessions."""
        # Arrange
        result_mock = AsyncMock()
        scalars_mock = ScalarsMock([sample_session])
        result_mock.scalars = MagicMock(return_value=scalars_mock)

        mock_db.execute = AsyncMock(return_value=result_mock)

        # Act
        result = await session_manager.get_active_sessions()

        # Assert
        assert result == [sample_session]
        mock_db.execute.assert_called_once()
