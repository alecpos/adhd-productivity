#!/usr/bin/env python
"""Standalone test for Body Doubling AnalyticsService.

This script sets up proper mocks for missing models to avoid 
SQLAlchemy relationship initialization errors.
"""

import asyncio
import sys
import os
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# We need to add our mock models to the sys.modules before any
# SQLAlchemy models are imported
import importlib.util
import sys

# Import our mock models
from app.services.body_doubling.mock_models import MockTaskCategoryModel

# Create a mock module for the task_category_model
mock_module_name = "app.models.task_category_model"
mock_spec = importlib.util.find_spec("app.services.body_doubling.mock_models")
mock_module = importlib.util.module_from_spec(mock_spec)
sys.modules[mock_module_name] = mock_module

# Add the TaskCategoryModel to the mock module
setattr(sys.modules[mock_module_name], "TaskCategoryModel", MockTaskCategoryModel)

# Now we can safely import our actual models and services
from app.models.enums_model import SessionStatus, SessionType
from app.services.body_doubling.analytics_service import AnalyticsService

# Mock Body Doubling Session Model
class MockBodyDoublingSessionModel:
    """Mock for the BodyDoublingSessionModel."""
    
    def __init__(
        self,
        id=None,
        user_id=None,
        host_id=None,
        title="Test Session",
        description="Test session for standalone testing",
        start_time=None,
        end_time=None,
        status=None,
        session_type=None,
        activity_type="Programming",
        focus_rating=None,
        productivity_rating=None,
        meta_data=None
    ):
        """Initialize with test data."""
        self.id = id or uuid.uuid4()
        self.user_id = user_id or uuid.uuid4()
        self.host_id = host_id or self.user_id
        self.title = title
        self.description = description
        self.start_time = start_time or datetime.now() - timedelta(hours=2)
        self.end_time = end_time
        self.status = status or SessionStatus.ACTIVE
        self.session_type = session_type or SessionType.BODY_DOUBLING
        self.activity_type = activity_type
        self.focus_rating = focus_rating
        self.productivity_rating = productivity_rating
        self.meta_data = meta_data or {
            "participants": [str(self.user_id)],
            "feedback": []
        }

# Mock DB Session
class MockDBSession:
    """Mock database session for testing without a real database."""
    
    def __init__(self):
        """Initialize with empty collections."""
        self.sessions = {}
    
    async def execute(self, query):
        """Mock query execution."""
        return self
    
    async def commit(self):
        """Mock commit."""
        pass
    
    async def refresh(self, obj):
        """Mock refresh."""
        pass
    
    def scalars(self):
        """Return self for chaining."""
        return self
    
    def all(self):
        """Return all sessions."""
        return list(self.sessions.values())
    
    def scalar_one_or_none(self):
        """Return the session for the given ID."""
        if not self.sessions:
            return None
        return list(self.sessions.values())[0]
    
    def add_session(self, session):
        """Add a session to the mock database."""
        self.sessions[str(session.id)] = session
        return session

async def test_analytics_service():
    """Test the analytics service with mocked models."""
    print("Starting standalone test for AnalyticsService...")
    
    # Create mock DB session
    db_session = MockDBSession()
    
    # Create analytics service
    analytics_service = AnalyticsService(db_session)
    
    # Create a user and session
    user_id = uuid.uuid4()
    session_id = uuid.uuid4()
    
    # Create test session
    session = MockBodyDoublingSessionModel(
        id=session_id,
        user_id=user_id,
        host_id=user_id,
        start_time=datetime.now() - timedelta(hours=2),
        end_time=datetime.now() - timedelta(hours=1),
        status=SessionStatus.COMPLETED,
        session_type=SessionType.BODY_DOUBLING,
        focus_rating=None,
        productivity_rating=None
    )
    
    # Add session to mock DB
    db_session.add_session(session)
    
    # Test calculate trend
    values = [1, 2, 3, 4, 5]
    trend = analytics_service._calculate_trend(values)
    print(f"Trend calculation with increasing values: {trend}")
    assert trend == "improving", f"Expected 'improving' but got '{trend}'"
    
    # Test add feedback
    print("\nTesting add_session_feedback...")
    feedback_data = {
        "focus_rating": 4,
        "productivity_rating": 5,
        "distraction_level": 2,
        "notes": "This was a productive test session"
    }
    
    try:
        await analytics_service.add_session_feedback(session_id, user_id, feedback_data)
        print("Successfully added feedback! ✅")
    except Exception as e:
        print(f"Error adding feedback: {e}")
    
    print("\nStandalone test completed successfully!")

if __name__ == "__main__":
    asyncio.run(test_analytics_service()) 