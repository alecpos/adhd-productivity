#!/usr/bin/env python
"""Run tests for the Analytics Service component."""

import os
import sys
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))

# Mock dependencies
sys.modules['app.main'] = MagicMock()
sys.modules['app.routes'] = MagicMock()
sys.modules['app.routes.body_doubling_routes'] = MagicMock()

# Create HTTP Exception
class HTTPException(Exception):
    def __init__(self, status_code, detail):
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"{status_code}: {detail}")

sys.modules['fastapi'] = MagicMock()
sys.modules['fastapi'].HTTPException = HTTPException

# Create mock models
class MockSessionStatus:
    COMPLETED = "completed"
    ACTIVE = "active"
    CANCELLED = "cancelled"

class MockSessionType:
    WORKING = "working"
    STUDYING = "studying"
    CREATIVE = "creative"

# Create mock schemas
class MockSessionAnalyticsSchema:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

class MockSessionFeedbackSchema:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

# Mock the model
class MockBodyDoublingSessionModel:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

# Set up mocks
sys.modules['app.models.body_doubling_model'] = MagicMock()
sys.modules['app.models.body_doubling_model'].BodyDoublingSessionModel = MockBodyDoublingSessionModel

sys.modules['app.models.enums_model'] = MagicMock()
sys.modules['app.models.enums_model'].SessionStatus = MockSessionStatus
sys.modules['app.models.enums_model'].SessionType = MockSessionType

sys.modules['app.schemas.body_doubling_schema'] = MagicMock()
sys.modules['app.schemas.body_doubling_schema'].SessionAnalyticsSchema = MockSessionAnalyticsSchema
sys.modules['app.schemas.body_doubling_schema'].SessionFeedbackSchema = MockSessionFeedbackSchema

# Mock sqlalchemy
sys.modules['sqlalchemy'] = MagicMock()
sys.modules['sqlalchemy.ext.asyncio'] = MagicMock()
sys.modules['sqlalchemy.ext.asyncio'].AsyncSession = MagicMock()

# Import the service
from app.services.body_doubling.analytics_service import AnalyticsService

@pytest.fixture
def mock_db_session():
    """Create a mock database session."""
    session = AsyncMock()
    return session

@pytest.fixture
def sample_session():
    """Create a sample session model."""
    now = datetime.now()
    user_id = uuid.uuid4()

    return MockBodyDoublingSessionModel(
        id=uuid.uuid4(),
        user_id=user_id,
        host_id=user_id,
        title="Test Session",
        description="Test description",
        start_time=now - timedelta(hours=2),
        end_time=now - timedelta(hours=1),
        status=MockSessionStatus.COMPLETED,
        session_type=MockSessionType.WORKING,
        activity_type="Programming",
        focus_rating=4,
        productivity_rating=4,
        meta_data={
            "participants": [str(user_id), str(uuid.uuid4())],
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
    )

@pytest.mark.asyncio
async def test_calculate_trend():
    """Test the trend calculation functionality."""
    service = AnalyticsService(AsyncMock())

    # Improving trend
    assert service._calculate_trend([1, 2, 3, 4, 5]) == "improving"

    # Declining trend
    assert service._calculate_trend([5, 4, 3, 2, 1]) == "declining"

    # Stable trend
    assert service._calculate_trend([3, 3, 3, 3, 3]) == "stable"

    # Small changes
    assert service._calculate_trend([3.0, 3.01, 3.02, 3.01, 3.0]) == "stable"

    # Empty list
    assert service._calculate_trend([]) == "stable"

    # Single value
    assert service._calculate_trend([4]) == "stable"

@pytest.mark.asyncio
async def test_get_user_analytics_no_sessions(mock_db_session):
    """Test getting user analytics when no sessions exist."""
    # Setup
    user_id = uuid.uuid4()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_db_session.execute.return_value = mock_result

    # Execute
    analytics_service = AnalyticsService(mock_db_session)
    result = await analytics_service.get_user_analytics(user_id)

    # Verify
    assert result.total_sessions == 0
    assert result.total_focus_time == 0
    assert result.average_productivity == 0
    assert result.productivity_trend == "none"
    assert result.completion_rate == 0
    assert len(result.most_productive_times) == 0
    assert len(result.preferred_activity_types) == 0

@pytest.mark.asyncio
async def test_get_session_analytics_not_found(mock_db_session):
    """Test getting session analytics for a non-existent session."""
    # Setup
    session_id = uuid.uuid4()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db_session.execute.return_value = mock_result

    # Execute and verify exception
    analytics_service = AnalyticsService(mock_db_session)
    with pytest.raises(HTTPException) as exc_info:
        await analytics_service.get_session_analytics(session_id)

    assert exc_info.value.status_code == 404
    assert f"Session {session_id}" in str(exc_info.value.detail)

@pytest.mark.asyncio
async def test_add_session_feedback_success(mock_db_session, sample_session):
    """Test successfully adding feedback to a session."""
    # Setup
    session_id = sample_session.id
    user_id = sample_session.user_id
    feedback_data = {"focus_rating": 5, "productivity_rating": 5, "notes": "Great session"}

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = sample_session
    mock_db_session.execute.return_value = mock_result

    # Execute
    analytics_service = AnalyticsService(mock_db_session)
    result = await analytics_service.add_session_feedback(session_id, user_id, feedback_data)

    # Verify
    assert result.id == session_id
    assert len(result.meta_data["feedback"]) == 2  # Original + new
    assert result.meta_data["feedback"][-1]["user_id"] == str(user_id)
    assert result.meta_data["feedback"][-1]["focus_rating"] == 5
    assert result.meta_data["feedback"][-1]["productivity_rating"] == 5
    assert result.meta_data["feedback"][-1]["notes"] == "Great session"
    assert "timestamp" in result.meta_data["feedback"][-1]

    # Verify DB operations
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once_with(sample_session)

if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
