"""Integration tests for the Pomodoro service."""

import uuid
from datetime import datetime, timezone, timedelta
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.pomodoro_model import PomodoroSessionModel
from app.models.enums_model import PomodoroStatus, BreakType
from app.services.pomodoro_service import PomodoroService


@pytest_asyncio.fixture(scope="function")
async def setup_pomodoro_table(db_session: AsyncSession):
    """Ensure the pomodoro_sessions table exists."""
    # Get the connection from the session
    connection = await db_session.connection()

    # Create the table if it doesn't exist
    await connection.run_sync(
        lambda sync_conn: PomodoroSessionModel.__table__.create(sync_conn, checkfirst=True)
    )

    # Return the session for other fixtures to use
    return db_session


class TestPomodoroIntegration:
    """Integration tests for the Pomodoro service components."""

    @pytest.mark.asyncio
    async def test_create_and_retrieve_session(
        self, setup_pomodoro_table, db_session: AsyncSession
    ):
        """Test creating and retrieving a session."""
        # Arrange
        service = PomodoroService(db=db_session)
        user_id = uuid.uuid4()
        task_id = uuid.uuid4()

        # Act - Create a new session
        session = await service.create_session(
            user_id=user_id, task_id=task_id, duration=25, break_duration=5, long_break_duration=15
        )

        # Act - Retrieve the session
        retrieved_session = await service.get_session(session.id)

        # Assert
        assert retrieved_session is not None
        assert retrieved_session.id == session.id
        assert retrieved_session.user_id == user_id
        assert retrieved_session.task_id == task_id
        assert retrieved_session.work_duration == 25
        assert retrieved_session.short_break_duration == 5
        assert retrieved_session.long_break_duration == 15
        assert retrieved_session.status == PomodoroStatus.ACTIVE.value
        assert retrieved_session.completed_sessions == 0

    @pytest.mark.asyncio
    async def test_session_lifecycle(self, setup_pomodoro_table, db_session: AsyncSession):
        """Test the full lifecycle of a pomodoro session."""
        # Arrange
        service = PomodoroService(db=db_session)
        user_id = uuid.uuid4()
        task_id = uuid.uuid4()

        # Act - Create a new session
        session = await service.create_session(
            user_id=user_id, task_id=task_id, duration=25, break_duration=5, long_break_duration=15
        )

        # Act - Complete a work period
        completion_data = {
            "productivity_rating": 8,
            "distractions": 2,
            "notes": "Productive session",
            "completed_tasks": [str(uuid.uuid4())],
        }
        await service.complete_work_period(session.id, completion_data)

        # Act - Get updated session status
        session_status = await service.get_session_status(session.id)

        # Assert - Check session status after work period
        assert session_status.status == PomodoroStatus.BREAK.value
        assert session_status.current_session == 2
        assert session_status.cycles_completed == 1

        # Act - Complete a break period
        break_data = {
            "break_activity": "Quick walk",
            "refreshed_rating": 9,
            "notes": "Felt refreshed",
        }
        await service.complete_break_period(session.id, break_data)

        # Act - Get updated session
        updated_session = await service.get_session(session.id)

        # Assert - Check session after break period
        assert updated_session.status == PomodoroStatus.READY.value
        assert hasattr(updated_session, "breaks_taken")
        assert len(updated_session.breaks_taken) == 1
        assert updated_session.breaks_taken[0]["activity"] == "Quick walk"

        # Act - Record an interruption
        interruption_data = {
            "type": "phone_call",
            "duration": 5,
            "reason": "Important call",
            "action_taken": "Paused timer",
        }
        await service.record_interruption(session.id, interruption_data)

        # Act - Get updated session after interruption
        interrupted_session = await service.get_session(session.id)

        # Assert - Check session after interruption
        assert interrupted_session.status == PomodoroStatus.PAUSED.value
        assert len(interrupted_session.interruptions) == 1
        assert interrupted_session.interruptions[0]["type"] == "phone_call"

    @pytest.mark.asyncio
    async def test_session_preferences_update(self, setup_pomodoro_table, db_session: AsyncSession):
        """Test updating session preferences."""
        # Arrange
        service = PomodoroService(db=db_session)
        user_id = uuid.uuid4()
        task_id = uuid.uuid4()

        # Act - Create a new session
        session = await service.create_session(
            user_id=user_id, task_id=task_id, duration=25, break_duration=5, long_break_duration=15
        )

        # Act - Update session preferences
        preferences = {
            "work_duration": 30,
            "short_break_duration": 10,
            "sound_notifications": False,
        }
        updated_session = await service.update_session_preferences(session.id, preferences)

        # Assert
        assert updated_session.work_duration == 30
        assert updated_session.short_break_duration == 10
        assert updated_session.meta_data["sound_notifications"] == False

        # Act - Retrieve the session again to confirm persistence
        retrieved_session = await service.get_session(session.id)

        # Assert - Check persistence
        assert retrieved_session.work_duration == 30
        assert retrieved_session.short_break_duration == 10
        assert retrieved_session.meta_data["sound_notifications"] == False

    @pytest.mark.asyncio
    async def test_user_sessions_and_analytics(
        self, setup_pomodoro_table, db_session: AsyncSession
    ):
        """Test retrieving user sessions and analytics."""
        # Arrange
        service = PomodoroService(db=db_session)
        user_id = uuid.uuid4()
        task_id = uuid.uuid4()

        # Act - Create multiple sessions for the user
        session1 = await service.create_session(
            user_id=user_id, task_id=task_id, duration=25, break_duration=5
        )

        session2 = await service.create_session(
            user_id=user_id, task_id=task_id, duration=30, break_duration=10
        )

        # Complete first session's work period
        completion_data = {"productivity_rating": 8, "distractions": 2, "notes": "Good focus"}
        await service.complete_work_period(session1.id, completion_data)

        # Act - Get user sessions
        user_sessions = await service.get_user_sessions(user_id)

        # Assert - Check user sessions
        assert len(user_sessions) == 2

        # Act - Get session stats
        stats = await service.get_session_stats(user_id)

        # Assert - Check stats
        assert stats.total_sessions == 2

        # Act - Get detailed analytics
        analytics = await service.get_detailed_analytics(user_id)

        # Assert - Check analytics
        assert analytics.total_sessions == 2
        assert analytics.completed_sessions >= 0  # At least some completed work periods
