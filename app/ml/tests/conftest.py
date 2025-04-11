"""Test fixtures for ML tests."""

import pytest
from unittest.mock import AsyncMock, MagicMock, Mock
from dataclasses import dataclass
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4
import pandas as pd
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional


@dataclass
class MockUser:
    """Mock user class for testing that doesn't depend on SQLAlchemy."""

    id: str = str(uuid4())
    username: str = "testuser"
    email: str = "test@example.com"
    first_name: str = "Test"
    last_name: str = "User"
    password_hash: str = "hashed_password"
    is_active: bool = True
    created_at: datetime = datetime.now(timezone.utc)
    updated_at: datetime = datetime.now(timezone.utc)

    # Mock relationships
    mental_health_logs: List = None
    energy_logs: List = None
    tasks: List = None
    calendar_events: List = None

    def __post_init__(self):
        if self.mental_health_logs is None:
            self.mental_health_logs = []
        if self.energy_logs is None:
            self.energy_logs = []
        if self.tasks is None:
            self.tasks = []
        if self.calendar_events is None:
            self.calendar_events = []


@dataclass
class MockMentalHealthModel:
    """Mock mental health model for testing."""

    id: str = str(uuid4())
    user_id: str = None
    mood: int = 5
    anxiety_level: int = 3
    focus_level: int = 4
    energy_level: int = 4
    stress_level: int = 3
    created_at: datetime = datetime.now(timezone.utc)
    updated_at: datetime = datetime.now(timezone.utc)

    # Mock relationship
    user: Optional[MockUser] = None


@dataclass
class MockEnergyLog:
    """Mock energy log for testing."""

    id: str = str(uuid4())
    user_id: str = None
    energy_level: int = 5
    time_of_day: str = "morning"
    created_at: datetime = datetime.now(timezone.utc)
    updated_at: datetime = datetime.now(timezone.utc)

    # Mock relationship
    user: Optional[MockUser] = None


@dataclass
class MockTaskModel:
    """Mock task model for testing."""

    id: str = str(uuid4())
    user_id: str = None
    title: str = "Test Task"
    description: str = "This is a test task"
    status: str = "pending"
    priority: int = 3
    difficulty: int = 3
    estimated_duration: int = 45
    created_at: datetime = datetime.now(timezone.utc)
    updated_at: datetime = datetime.now(timezone.utc)

    # Mock relationship
    user: Optional[MockUser] = None


@dataclass
class MockCalendarEventModel:
    """Mock calendar event model for testing."""

    id: str = str(uuid4())
    user_id: str = None
    title: str = "Test Event"
    description: str = "This is a test event"
    start_time: datetime = datetime.now(timezone.utc)
    end_time: datetime = datetime.now(timezone.utc)
    created_at: datetime = datetime.now(timezone.utc)
    updated_at: datetime = datetime.now(timezone.utc)

    # Mock relationship
    user: Optional[MockUser] = None


class MockAsyncResult:
    """Mock result for async query methods."""

    def __init__(self, result):
        self.result = result

    def all(self):
        """Return all results."""
        return self.result

    def first(self):
        """Return first result or None."""
        return self.result[0] if self.result else None

    def scalars(self):
        """Return self to allow chaining with all() method."""
        return self


@pytest.fixture
def test_user():
    """Create a mock test user for tests."""
    return MockUser()


@pytest.fixture
def db_session():
    """Create a mock database session."""
    mock_session = AsyncMock(spec=AsyncSession)

    # Create an execute method that returns mocked results for different queries
    async def mock_execute(query):
        # This is a simplified implementation to make tests pass

        # Mock result object
        result = MockAsyncResult([])

        # Set mock to return the result
        mock_session.execute.return_value = result

        return result

    # Configure the session to use our mock execute
    mock_session.execute = mock_execute

    return mock_session


@pytest.fixture
async def sample_data(db_session, test_user):
    """Create sample data for testing."""
    user_id = test_user.id

    # Sample mental health data
    mental_health_data = [
        MockMentalHealthModel(
            id=str(uuid4()),
            user_id=user_id,
            mood=4,
            anxiety_level=2,
            focus_level=3,
            energy_level=4,
            stress_level=3,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            user=test_user,
        ),
        MockMentalHealthModel(
            id=str(uuid4()),
            user_id=user_id,
            mood=3,
            anxiety_level=3,
            focus_level=2,
            energy_level=3,
            stress_level=4,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            user=test_user,
        ),
    ]

    # Sample energy logs
    energy_logs = [
        MockEnergyLog(
            id=str(uuid4()),
            user_id=user_id,
            energy_level=4,
            time_of_day="morning",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            user=test_user,
        ),
        MockEnergyLog(
            id=str(uuid4()),
            user_id=user_id,
            energy_level=2,
            time_of_day="evening",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            user=test_user,
        ),
    ]

    # Sample tasks
    tasks = [
        MockTaskModel(
            id=str(uuid4()),
            user_id=user_id,
            title="Test Task 1",
            description="This is a test task",
            status="completed",
            priority=3,
            difficulty=3,
            estimated_duration=45,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            user=test_user,
        ),
        MockTaskModel(
            id=str(uuid4()),
            user_id=user_id,
            title="Test Task 2",
            description="This is another test task",
            status="pending",
            priority=4,
            difficulty=4,
            estimated_duration=90,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            user=test_user,
        ),
    ]

    # Sample calendar events
    calendar_events = [
        MockCalendarEventModel(
            id=str(uuid4()),
            user_id=user_id,
            title="Test Event 1",
            description="This is a test event",
            start_time=datetime.now(timezone.utc),
            end_time=datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            user=test_user,
        ),
        MockCalendarEventModel(
            id=str(uuid4()),
            user_id=user_id,
            title="Test Event 2",
            description="This is another test event",
            start_time=datetime.now(timezone.utc),
            end_time=datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            user=test_user,
        ),
    ]

    # Update user's mock relationships
    test_user.mental_health_logs = mental_health_data
    test_user.energy_logs = energy_logs
    test_user.tasks = tasks
    test_user.calendar_events = calendar_events

    # Override the db_session's execute method to return specific data based on the query
    async def mock_execute(query):
        # Very simple query "parsing" - in a real test you'd use more sophisticated matching
        query_str = str(query)

        if "MentalHealth" in query_str:
            return MockAsyncResult(mental_health_data)
        elif "Energy" in query_str:
            return MockAsyncResult(energy_logs)
        elif "Task" in query_str:
            return MockAsyncResult(tasks)
        elif "Calendar" in query_str:
            return MockAsyncResult(calendar_events)
        elif "User" in query_str:
            return MockAsyncResult([test_user])
        else:
            return MockAsyncResult([])

    db_session.execute = mock_execute

    # Return all test data
    return {
        "user": test_user,
        "mental_health_data": mental_health_data,
        "energy_logs": energy_logs,
        "tasks": tasks,
        "calendar_events": calendar_events,
    }
