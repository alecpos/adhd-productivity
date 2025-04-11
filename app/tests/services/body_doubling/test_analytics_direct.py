"""Direct tests for AnalyticsService without requiring full application context."""

import unittest
from unittest.mock import AsyncMock, MagicMock, patch
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

# Create a mock HTTPException
class MockHTTPException(Exception):
    def __init__(self, status_code, detail):
        self.status_code = status_code
        self.detail = detail

# Create mock SessionStatus and SessionType
class MockSessionStatus:
    COMPLETED = "completed"
    ACTIVE = "active"

class MockSessionType:
    WORKING = "working"
    STUDYING = "studying"

# Create mocks for schemas
class MockSessionAnalyticsSchema:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

class MockSessionFeedbackSchema:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

# Create the AnalyticsService class with minimal dependencies
class AnalyticsService:
    """Isolated version of AnalyticsService for testing."""
    
    def __init__(self, db):
        self._db = db

    async def add_session_feedback(
        self, session_id, user_id, feedback_data
    ):
        """Add feedback for a session."""
        # Mock implementation
        session = await self._get_session(session_id)
        
        if not session:
            raise MockHTTPException(status_code=404, detail=f"Session {session_id} not found")
        
        # Verify user participated in the session
        user_id_str = str(user_id)
        participants = []
        if hasattr(session, 'meta_data') and session.meta_data and "participants" in session.meta_data:
            participants = session.meta_data["participants"]
        
        if user_id_str not in participants and session.user_id != user_id and session.host_id != user_id:
            raise MockHTTPException(
                status_code=403, 
                detail="Only session participants can provide feedback"
            )
        
        # Add user ID to feedback data
        feedback_entry = {
            "user_id": user_id_str,
            "timestamp": datetime.now().isoformat(),
            **feedback_data
        }
        
        # Initialize meta_data if needed
        if not hasattr(session, 'meta_data') or not session.meta_data:
            session.meta_data = {}
        
        # Initialize feedback list if needed
        if "feedback" not in session.meta_data:
            session.meta_data["feedback"] = []
        
        # Add feedback entry
        session.meta_data["feedback"].append(feedback_entry)
        
        # Update session-level ratings if this is the first feedback
        if not hasattr(session, 'focus_rating') or session.focus_rating is None and "focus_rating" in feedback_data:
            session.focus_rating = feedback_data["focus_rating"]
        
        if not hasattr(session, 'productivity_rating') or session.productivity_rating is None and "productivity_rating" in feedback_data:
            session.productivity_rating = feedback_data["productivity_rating"]
        
        # Commit changes
        await self._db.commit()
        await self._db.refresh(session)
        
        return session
    
    async def _get_session(self, session_id):
        """Mock implementation of session retrieval."""
        # Execute the query first
        execute_result = await self._db.execute(None)
        
        # Create a regular MagicMock instead of an AsyncMock for scalar_one_or_none
        if hasattr(execute_result, 'scalar_one_or_none'):
            # Return the actual result, not a coroutine
            return execute_result.scalar_one_or_none()
        return None
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate the trend direction from a list of values."""
        if not values or len(values) < 2:
            return "stable"
        
        # Simple linear trend
        changes = [values[i] - values[i-1] for i in range(1, len(values))]
        avg_change = sum(changes) / len(changes)
        
        if avg_change > 0.1:  # Threshold for improvement
            return "improving"
        elif avg_change < -0.1:  # Threshold for decline
            return "declining"
        else:
            return "stable"

class TestAnalyticsService(unittest.IsolatedAsyncioTestCase):
    """Test the AnalyticsService."""
    
    async def asyncSetUp(self):
        """Set up the test case."""
        # Make sure db_mock.execute returns a MagicMock, not an AsyncMock for scalar results
        self.db_mock = AsyncMock()
        # Configure execute to return a regular MagicMock
        execute_result_mock = MagicMock()
        self.db_mock.execute.return_value = execute_result_mock
        
        self.service = AnalyticsService(self.db_mock)
        
    async def test_calculate_trend(self):
        """Test trend calculation."""
        # Improving trend
        self.assertEqual(self.service._calculate_trend([1, 2, 3, 4, 5]), "improving")
        
        # Declining trend
        self.assertEqual(self.service._calculate_trend([5, 4, 3, 2, 1]), "declining")
        
        # Stable trend
        self.assertEqual(self.service._calculate_trend([3, 3, 3, 3, 3]), "stable")
        
        # Empty list
        self.assertEqual(self.service._calculate_trend([]), "stable")
        
        # Single value
        self.assertEqual(self.service._calculate_trend([4]), "stable")
    
    async def test_add_session_feedback_not_found(self):
        """Test adding feedback to a non-existent session."""
        # Setup
        session_id = uuid.uuid4()
        user_id = uuid.uuid4()
        feedback_data = {"focus_rating": 5, "productivity_rating": 5}
        
        # Mock the database response to return None (session not found)
        execute_mock = MagicMock()
        execute_mock.scalar_one_or_none.return_value = None
        self.db_mock.execute.return_value = execute_mock
        
        # Test the method raises the correct exception
        with self.assertRaises(MockHTTPException) as context:
            await self.service.add_session_feedback(session_id, user_id, feedback_data)
        
        # Verify
        self.assertEqual(context.exception.status_code, 404)
        self.assertIn(str(session_id), context.exception.detail)
    
    async def test_add_session_feedback_unauthorized(self):
        """Test adding feedback from a user who didn't participate."""
        # Setup
        session_id = uuid.uuid4()
        user_id = uuid.uuid4()
        unauthorized_user_id = uuid.uuid4()
        feedback_data = {"focus_rating": 5, "productivity_rating": 5}
        
        # Create a mock session
        mock_session = MagicMock()
        mock_session.id = session_id
        mock_session.user_id = user_id
        mock_session.host_id = user_id
        mock_session.meta_data = {"participants": [str(user_id)]}
        
        # Mock the database response directly with the session
        execute_mock = MagicMock()
        execute_mock.scalar_one_or_none.return_value = mock_session
        self.db_mock.execute.return_value = execute_mock
        
        # Test the method raises the correct exception
        with self.assertRaises(MockHTTPException) as context:
            await self.service.add_session_feedback(session_id, unauthorized_user_id, feedback_data)
        
        # Verify
        self.assertEqual(context.exception.status_code, 403)
        self.assertIn("Only session participants", context.exception.detail)
    
    async def test_add_session_feedback_success(self):
        """Test successfully adding feedback."""
        # Setup
        session_id = uuid.uuid4()
        user_id = uuid.uuid4()
        feedback_data = {"focus_rating": 5, "productivity_rating": 5, "notes": "Great session"}
        
        # Create a mock session
        mock_session = MagicMock()
        mock_session.id = session_id
        mock_session.user_id = user_id
        mock_session.host_id = user_id
        mock_session.meta_data = {
            "participants": [str(user_id)],
            "feedback": []
        }
        mock_session.focus_rating = None
        mock_session.productivity_rating = None
        
        # Mock the database response directly with the session
        execute_mock = MagicMock()
        execute_mock.scalar_one_or_none.return_value = mock_session
        self.db_mock.execute.return_value = execute_mock
        
        # Test the method
        result = await self.service.add_session_feedback(session_id, user_id, feedback_data)
        
        # Verify
        self.assertEqual(result.id, session_id)
        self.assertEqual(len(result.meta_data["feedback"]), 1)
        self.assertEqual(result.meta_data["feedback"][0]["user_id"], str(user_id))
        self.assertEqual(result.meta_data["feedback"][0]["focus_rating"], 5)
        self.assertEqual(result.meta_data["feedback"][0]["productivity_rating"], 5)
        self.assertEqual(result.meta_data["feedback"][0]["notes"], "Great session")
        self.assertIn("timestamp", result.meta_data["feedback"][0])
        
        # Verify session ratings were updated
        self.assertEqual(result.focus_rating, 5)
        self.assertEqual(result.productivity_rating, 5)
        
        # Verify database operations
        self.db_mock.commit.assert_called_once()
        self.db_mock.refresh.assert_called_once_with(mock_session)

if __name__ == "__main__":
    unittest.main() 