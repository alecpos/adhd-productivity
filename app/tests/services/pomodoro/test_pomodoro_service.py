"""Unit tests for the PomodoroService component."""

import json
import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException
from sqlalchemy import update, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.pomodoro_model import PomodoroSessionModel
from app.models.enums_model import PomodoroStatus, BreakType
from app.schemas.pomodoro_schema import PomodoroResponseSchema
from app.services.pomodoro_service import PomodoroService


class TestPomodoroService:
    """Tests for the PomodoroService."""

    @pytest.fixture
    def sample_session(self):
        """Create a sample session for testing."""
        return {
            "id": uuid.uuid4(),
            "user_id": uuid.uuid4(),
            "task_id": uuid.uuid4(),
            "work_duration": 25,
            "short_break_duration": 5,
            "long_break_duration": 15,
            "sessions_until_long_break": 4,
            "notes": "Test session",
            "start_time": datetime.now(timezone.utc),
            "end_time": None,
            "status": PomodoroStatus.ACTIVE.value,
            "break_type": BreakType.SHORT.value,
            "completed_sessions": 0,
            "current_session": 1,
            "completed": False,
            "meta_data": {
                "auto_start_breaks": False,
                "sound_notifications": True,
                "strict_mode": False,
            },
            "completed_tasks": [],
            "focus_scores": [],
            # Add fields required by PomodoroResponseSchema
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "duration": 25,
            "break_duration": 5,
            "cycles": 4,
            "current_cycle": 1,
            "completed_cycles": 0,
            "total_focus_time": 0,
            "success_rate": 0.0,
            "productivity_score": None,
            "focus_level": None,
        }

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        mock = AsyncMock(spec=AsyncSession)
        mock.execute = AsyncMock()
        mock.commit = AsyncMock()
        mock.refresh = AsyncMock()
        return mock

    def setup_db_mocks(self, mock_db, sample_session, scenario="success"):
        """Set up database mocks for testing."""

        # Setup a class that simulates scalars().all() behavior
        class ScalarsMock:
            def all(self):
                if scenario == "empty":
                    return []
                return [sample_session]

        # Setup the mock for db.execute for different query types
        async def mock_execute(query):
            result_mock = MagicMock()

            # For a select query looking for a single item by id
            if (
                isinstance(query, select.__class__)
                and hasattr(query, "_where_criteria")
                and len(query._where_criteria) > 0
            ):
                # Simulate looking for a session by ID
                result_mock.scalar_one_or_none.return_value = (
                    sample_session if scenario != "not_found" else None
                )
                result_mock.scalars.return_value = ScalarsMock()

            # For an update operation
            elif isinstance(query, update.__class__):
                values = query._values
                # Apply the update to our sample session
                for key, value in values.items():
                    sample_session[key] = value

            return result_mock

        # Set the side effect for the execute method
        mock_db.execute.side_effect = mock_execute

        return sample_session

    @pytest.mark.asyncio
    async def test_get_session_found(self, mock_db, sample_session):
        """Test retrieving a session by ID when it exists."""
        # Arrange
        session_manager = PomodoroService(db=mock_db)

        # Create a response schema for the get_one result
        response_schema = PomodoroResponseSchema.model_validate(sample_session)

        # Mock the get_one method
        session_manager.get_one = AsyncMock(return_value=sample_session)

        # Mock the schema conversion in the service method
        with patch(
            "app.schemas.pomodoro_schema.PomodoroResponseSchema.model_validate"
        ) as mock_validate:
            mock_validate.return_value = response_schema

            # Act
            result = await session_manager.get_session(sample_session["id"])

            # Assert
            assert result is not None
            assert result.id == sample_session["id"]
            session_manager.get_one.assert_called_once_with(filters={"id": sample_session["id"]})

    @pytest.mark.asyncio
    async def test_get_session_not_found(self, mock_db, sample_session):
        """Test retrieving a session by ID when it doesn't exist."""
        # Arrange
        session_manager = PomodoroService(db=mock_db)
        random_id = uuid.uuid4()

        # Mock the get_one method to return None
        session_manager.get_one = AsyncMock(return_value=None)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await session_manager.get_session(random_id)

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Session not found"
        session_manager.get_one.assert_called_once_with(filters={"id": random_id})

    @pytest.mark.asyncio
    async def test_get_user_sessions(self, mock_db, sample_session):
        """Test retrieving all sessions for a user."""
        # Arrange
        session_manager = PomodoroService(db=mock_db)

        # Mock the db.execute method to return our sample session
        result_mock = MagicMock()
        scalars_mock = MagicMock()
        scalars_mock.all.return_value = [sample_session]
        result_mock.scalars.return_value = scalars_mock
        mock_db.execute.return_value = result_mock

        # Act
        result = await session_manager.get_user_sessions(sample_session["user_id"])

        # Assert
        assert len(result) == 1
        # Check key fields rather than comparing entire objects
        assert str(result[0].id) == str(sample_session["id"])
        assert str(result[0].user_id) == str(sample_session["user_id"])
        assert result[0].work_duration == sample_session["work_duration"]
        assert result[0].status == sample_session["status"]

    @pytest.mark.asyncio
    async def test_get_user_sessions_empty(self, mock_db, sample_session):
        """Test retrieving sessions for a user when none exist."""
        # Arrange
        session_manager = PomodoroService(db=mock_db)
        self.setup_db_mocks(mock_db, sample_session, scenario="empty")

        # Act
        result = await session_manager.get_user_sessions(uuid.uuid4())

        # Assert
        assert len(result) == 0
        mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_session(self, mock_db, sample_session):
        """Test creating a new session."""
        # Arrange
        session_manager = PomodoroService(db=mock_db)

        # Mock the create method to return a mocked model with our sample_session fields
        session_model = MagicMock()
        for key, value in sample_session.items():
            setattr(session_model, key, value)

        # Set up the mocks with proper return values
        mock_db.add = MagicMock()  # Synchronous operation, use regular MagicMock
        mock_db.commit = AsyncMock()  # Async operation
        mock_db.refresh = AsyncMock()  # Async operation

        # Mock the model_validate to return the sample session as a schema
        with patch(
            "app.schemas.pomodoro_schema.PomodoroResponseSchema.model_validate",
            return_value=PomodoroResponseSchema.model_validate(sample_session),
        ):
            # Act
            result = await session_manager.create_session(
                user_id=sample_session["user_id"],
                task_id=sample_session["task_id"],
                duration=sample_session["work_duration"],
                break_duration=sample_session["short_break_duration"],
                long_break_duration=sample_session["long_break_duration"],
            )

            # Assert - check individual fields
            assert str(result.user_id) == str(sample_session["user_id"])
            assert str(result.task_id) == str(sample_session["task_id"])
            assert result.work_duration == sample_session["work_duration"]
            assert result.short_break_duration == sample_session["short_break_duration"]
            assert result.status == sample_session["status"]

            # Verify that the db methods were called
            mock_db.add.assert_called_once()
            mock_db.commit.assert_awaited_once()
            mock_db.refresh.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_complete_work_period(self, mock_db, sample_session):
        """Test completing a work period in a session."""
        # Arrange
        session_manager = PomodoroService(db=mock_db)

        # Create a simple PomodoroSessionModel object from the sample_session dict
        session_obj = MagicMock()
        for key, value in sample_session.items():
            setattr(session_obj, key, value)
        session_obj.focus_scores = []
        session_obj.completed_tasks = []

        # Create an updated object for the update method to return
        updated_obj = MagicMock()
        for key, value in sample_session.items():
            setattr(updated_obj, key, value)
        updated_obj.focus_scores = [
            {"productivity_rating": 8, "distractions": 2, "notes": "Productive session"}
        ]
        updated_obj.completed_tasks = []
        updated_obj.status = "break"
        updated_obj.completed_sessions = 1
        updated_obj.current_session = 2

        # Mock methods
        session_manager.get_by_id = AsyncMock(return_value=session_obj)
        session_manager.update = AsyncMock(return_value=updated_obj)

        completion_data = {
            "productivity_rating": 8,
            "distractions": 2,
            "notes": "Productive session",
            "completed_tasks": [str(uuid.uuid4())],
        }

        # Act
        result = await session_manager.complete_work_period(sample_session["id"], completion_data)

        # Assert
        assert session_manager.get_by_id.call_count == 1
        session_manager.get_by_id.assert_called_once_with(sample_session["id"])
        session_manager.update.assert_called_once()

        # Check the update was called with correct data
        update_data = session_manager.update.call_args[0][1]
        assert update_data["status"] == PomodoroStatus.BREAK.value
        assert update_data["completed_sessions"] == 1
        assert update_data["current_session"] == 2

        # Check the result contains expected values
        assert result.status == "break"
        assert result.completed_sessions == 1
        assert result.current_session == 2
        assert len(result.focus_scores) == 1
        assert result.focus_scores[0]["productivity_rating"] == 8

    @pytest.mark.asyncio
    async def test_complete_break_period(self, mock_db, sample_session):
        """Test completing a break period in a session."""
        # Arrange
        session_manager = PomodoroService(db=mock_db)

        # Modify sample session to be in BREAK state
        sample_session["status"] = PomodoroStatus.BREAK.value

        # Create a session model object from the sample_session dict
        session_obj = MagicMock()
        for key, value in sample_session.items():
            setattr(session_obj, key, value)
        session_obj.breaks_taken = []

        # Setup mocks
        session_manager.get_by_id = AsyncMock(return_value=session_obj)
        session_manager.update = AsyncMock(return_value=session_obj)

        break_data = {
            "break_activity": "Quick walk",
            "refreshed_rating": 9,
            "notes": "Felt refreshed",
        }

        # Act
        result = await session_manager.complete_break_period(sample_session["id"], break_data)

        # Assert
        session_manager.get_by_id.assert_called_once_with(sample_session["id"])
        session_manager.update.assert_called_once()
        # Verify the update data
        update_data = session_manager.update.call_args[0][1]
        assert update_data["status"] == PomodoroStatus.READY.value
        assert len(update_data["breaks_taken"]) == 1
        assert update_data["breaks_taken"][0]["activity"] == "Quick walk"
        assert update_data["breaks_taken"][0]["refreshed_rating"] == 9

    @pytest.mark.asyncio
    async def test_update_session_preferences(self, mock_db, sample_session):
        """Test updating session preferences."""
        # Arrange
        session_manager = PomodoroService(db=mock_db)

        # Create a session model from the sample_session
        session_obj = MagicMock()
        for key, value in sample_session.items():
            setattr(session_obj, key, value)

        # Setup mocks
        session_manager.get_by_id = AsyncMock(return_value=session_obj)
        session_manager.update = AsyncMock()

        preferences = {
            "work_duration": 30,
            "short_break_duration": 10,
            "sound_notifications": False,
        }

        # Act
        await session_manager.update_session_preferences(sample_session["id"], preferences)

        # Assert
        session_manager.get_by_id.assert_called_once_with(sample_session["id"])
        session_manager.update.assert_called_once()
        # Verify the update data
        update_data = session_manager.update.call_args[0][1]
        assert update_data["work_duration"] == 30
        assert update_data["short_break_duration"] == 10
        assert update_data["meta_data"]["sound_notifications"] == False

    # Let's add the method we're mocking
    @pytest.fixture
    def pomodoro_service_with_mocks(self, mock_db, sample_session):
        """Create a pomodoro service with mocked methods."""
        service = PomodoroService(db=mock_db)

        # Add get_one method as it's used but not in BaseService
        async def get_one(filters=None):
            if filters and "id" in filters:
                if filters["id"] == sample_session["id"]:
                    return sample_session
            return None

        service.get_one = AsyncMock(side_effect=get_one)

        return service
