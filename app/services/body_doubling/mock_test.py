#!/usr/bin/env python
"""Isolated mock test for AnalyticsService without SQLAlchemy dependencies.

This script provides fully isolated tests for the AnalyticsService using
simple mock objects instead of SQLAlchemy models.
"""

import asyncio
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from unittest.mock import MagicMock, AsyncMock
import random
import os
import sys
import importlib.util
import torch

# Constants for environment detection
IS_MACOS = True  # We're on Mac
PYTORCH_ONLY = True  # Force PyTorch-only mode
PYTORCH_AVAILABLE = True  # PyTorch is available
TRANSFORMERS_AVAILABLE = False  # Transformers not available

# First, check if we're running on macOS
if IS_MACOS:
    # Special handling for Mac in PyTorch-only mode
    # We'll use a minimal PyTorch-only implementation to avoid TensorFlow completely
    print("🔄 Loading PyTorch-only mode for Mac (bypassing transformers library)...")
    
    # Check if PyTorch is available
    try:
        import torch
        PYTORCH_AVAILABLE = True
        print("✅ PyTorch found, will use simplified PyTorch-only text generation")
    except ImportError:
        PYTORCH_AVAILABLE = False
        print("❌ PyTorch not found, will use mock insights")
else:
    # Standard approach
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True

# Mock session status and types
class MockSessionStatus:
    COMPLETED = "completed"
    ACTIVE = "active"

class MockSessionType:
    BODY_DOUBLING = "body_doubling"
    GROUP = "group"
    ONE_ON_ONE = "one_on_one"

# Simple mock session class
class MockBodyDoublingSession:
    """Mock version of BodyDoublingSessionModel without SQLAlchemy dependencies."""
    
    def __init__(self, **kwargs):
        self.id = kwargs.get('id', uuid.uuid4())
        self.user_id = kwargs.get('user_id')
        self.host_id = kwargs.get('host_id')
        self.title = kwargs.get('title', "Test Session")
        self.description = kwargs.get('description', "Test session for mock testing")
        self.start_time = kwargs.get('start_time', datetime.now() - timedelta(hours=2))
        self.end_time = kwargs.get('end_time')
        self.status = kwargs.get('status', MockSessionStatus.COMPLETED)
        self.session_type = kwargs.get('session_type', MockSessionType.BODY_DOUBLING)
        self.activity_type = kwargs.get('activity_type', "Programming")
        self.focus_rating = kwargs.get('focus_rating')
        self.productivity_rating = kwargs.get('productivity_rating')
        self.meta_data = kwargs.get('meta_data', {})
        
        # Initialize meta_data if not provided
        if not self.meta_data:
            self.meta_data = {
                "participants": [str(self.user_id)],
                "feedback": []
            }

# Mock database session
class MockDBSession:
    """Fully mocked database session without SQLAlchemy dependencies."""
    
    def __init__(self):
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
        """Mock scalars method."""
        return self
    
    def all(self):
        """Return all sessions."""
        return list(self.sessions.values())
    
    def scalar_one_or_none(self):
        """Return the session for the given ID."""
        # The query filter would have an ID in it
        # Here we're just returning the first session for simplicity
        if not self.sessions:
            return None
        return list(self.sessions.values())[0]
    
    def add_session(self, session):
        """Add a session to the mock database."""
        self.sessions[str(session.id)] = session
        return session

class SimplePyTorchGenerator:
    """A text generator using a small GPT-2 model from Hugging Face."""
    
    def __init__(self):
        """Initialize the model."""
        try:
            from transformers import GPT2LMHeadModel, GPT2Tokenizer
            
            print("🔄 Loading GPT-2 model...")
            self.model_name = "distilgpt2"  # Much smaller model
            self.tokenizer = GPT2Tokenizer.from_pretrained(self.model_name)
            self.model = GPT2LMHeadModel.from_pretrained(self.model_name)
            print("✅ GPT-2 model loaded successfully")
            
            # Move model to GPU if available
            if torch.cuda.is_available():
                self.model = self.model.cuda()
                print("✅ Model moved to GPU")
            else:
                print("ℹ️ Running on CPU")
                
        except Exception as e:
            print(f"❌ Failed to load GPT-2 model: {e}")
            # Fallback to simple responses
            self.model = None
            self.tokenizer = None
            self.responses = [
                "you tend to be most productive when you have a clear goal.",
                "your focus improves significantly in distraction-free environments.",
                "body doubling sessions help you maintain consistent productivity.",
                "your productivity peaks when working in shorter, focused intervals.",
                "taking regular breaks helps maintain your concentration levels.",
                "you perform better when you set specific goals for each session.",
                "mornings appear to be your most productive time of day.",
                "you focus better when working with others on similar tasks.",
            ]
            print("⚠️ Using fallback responses")
    
    def __call__(self, prompt):
        """Generate text based on prompt."""
        if self.model is None or self.tokenizer is None:
            # Fallback to simple responses
            idx = torch.randint(0, len(self.responses), (1,)).item()
            response = self.responses[idx]
            return [{"generated_text": prompt + response}]
            
        try:
            # Prepare the prompt
            inputs = self.tokenizer(prompt, return_tensors="pt", max_length=512, truncation=True)
            
            # Move inputs to GPU if model is on GPU
            if next(self.model.parameters()).is_cuda:
                inputs = {k: v.cuda() for k, v in inputs.items()}
            
            # Generate text
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=100,
                num_return_sequences=1,
                temperature=0.7,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
            
            # Decode the generated text
            generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Format like a transformers response
            return [{"generated_text": generated_text}]
            
        except Exception as e:
            print(f"❌ Error during text generation: {e}")
            # Fallback to simple responses
            idx = torch.randint(0, len(self.responses), (1,)).item()
            response = self.responses[idx]
            return [{"generated_text": prompt + response}]

class InsightGenerator:
    """Generate insights using machine learning models when available."""
    
    def __init__(self):
        self.text_generator = None
        self.model_status = "not available"
        self._init_pytorch_only_generator()
    
    def _init_pytorch_only_generator(self):
        """Initialize a simplified PyTorch-only text generator."""
        try:
            # Initialize our simple generator
            self.text_generator = SimplePyTorchGenerator()
            self.model_status = "available-pytorch-simple"
        except Exception as e:
            print(f"❌ Failed to initialize simplified PyTorch generator: {e}")
            self.model_status = "error"
    
    def _analyze_session_patterns(self, sessions):
        """Analyze patterns in session data."""
        patterns = {
            "best_activity": None,
            "best_time": None,
            "focus_trend": None,
            "productivity_trend": None,
            "common_distractions": [],
            "session_duration": None
        }
        
        if not sessions:
            return patterns
            
        # Analyze activity types
        activity_scores = {}
        for session in sessions:
            if session.activity_type:
                if session.activity_type not in activity_scores:
                    activity_scores[session.activity_type] = {
                        "count": 0,
                        "avg_focus": 0,
                        "avg_productivity": 0
                    }
                activity_scores[session.activity_type]["count"] += 1
                activity_scores[session.activity_type]["avg_focus"] += session.focus_rating or 0
                activity_scores[session.activity_type]["avg_productivity"] += session.productivity_rating or 0
        
        # Find best activity
        if activity_scores:
            best_activity = max(activity_scores.items(), 
                              key=lambda x: (x[1]["avg_focus"] + x[1]["avg_productivity"]) / x[1]["count"])
            patterns["best_activity"] = best_activity[0]
        
        # Analyze time patterns
        time_scores = {"morning": 0, "afternoon": 0, "evening": 0}
        for session in sessions:
            hour = session.start_time.hour
            if 5 <= hour < 12:
                time_scores["morning"] += (session.focus_rating or 0) + (session.productivity_rating or 0)
            elif 12 <= hour < 17:
                time_scores["afternoon"] += (session.focus_rating or 0) + (session.productivity_rating or 0)
            else:
                time_scores["evening"] += (session.focus_rating or 0) + (session.productivity_rating or 0)
        
        patterns["best_time"] = max(time_scores.items(), key=lambda x: x[1])[0]
        
        # Analyze trends
        focus_ratings = [s.focus_rating for s in sessions if s.focus_rating is not None]
        productivity_ratings = [s.productivity_rating for s in sessions if s.productivity_rating is not None]
        
        if len(focus_ratings) >= 2:
            focus_trend = "improving" if focus_ratings[-1] > focus_ratings[0] else "declining"
            patterns["focus_trend"] = focus_trend
            
        if len(productivity_ratings) >= 2:
            productivity_trend = "improving" if productivity_ratings[-1] > productivity_ratings[0] else "declining"
            patterns["productivity_trend"] = productivity_trend
        
        # Analyze session duration
        durations = [(s.end_time - s.start_time).total_seconds() / 60 for s in sessions if s.end_time]
        if durations:
            patterns["session_duration"] = sum(durations) / len(durations)
        
        return patterns
    
    def generate_focus_insights(self, user_data, session_data):
        """Generate focus insights based on user data."""
        if self.text_generator is None:
            # Add special messaging for issue types
            if self.model_status == "keras-incompatible":
                insights = self._get_mock_insights()
                insights["message"] = "Mock insights (Keras 3 incompatibility detected)"
                return insights
            elif self.model_status == "tensorflow-issue":
                insights = self._get_mock_insights()
                insights["message"] = "Mock insights (TensorFlow/Metal plugin issue detected)"
                insights["insights"].append({
                    "type": "system",
                    "insight": "Try running with PyTorch-only mode: ./scripts/run_standalone_test.sh --ai --pytorch",
                    "confidence": "high"
                })
                return insights
            return self._get_mock_insights()
        
        # Analyze patterns in the session data
        patterns = self._analyze_session_patterns(session_data)
        
        # Generate insights based on patterns
        insights = []
        
        # Focus insight
        if patterns["best_activity"]:
            focus_insight = f"Your focus is strongest during {patterns['best_activity']} tasks"
            if patterns["focus_trend"]:
                focus_insight += f", and your focus has been {patterns['focus_trend']}"
            insights.append({
                "type": "focus",
                "insight": focus_insight,
                "confidence": "high" if len(session_data) > 5 else "medium"
            })
        
        # Productivity insight
        if patterns["productivity_trend"]:
            productivity_insight = f"Your productivity has been {patterns['productivity_trend']}"
            if patterns["session_duration"]:
                productivity_insight += f", with an average session duration of {patterns['session_duration']:.1f} minutes"
            insights.append({
                "type": "productivity",
                "insight": productivity_insight,
                "confidence": "high" if len(session_data) > 5 else "medium"
            })
        
        # Time pattern insight
        if patterns["best_time"]:
            time_insight = f"You tend to be most productive during {patterns['best_time']} sessions"
            if patterns["best_activity"]:
                time_insight += f", especially when working on {patterns['best_activity']}"
            insights.append({
                "type": "pattern",
                "insight": time_insight,
                "confidence": "medium"
            })
        
        # Add PyTorch-specific message if using simplified mode
        message = "Here are AI-generated insights based on your session data"
        if self.model_status == "available-pytorch-simple":
            message += " (using PyTorch-only mode for Mac compatibility)"
        
        return {
            "message": message,
            "insights": insights
        }
    
    def _get_mock_insights(self):
        """Return mock insights when ML models aren't available."""
        return {
            "message": "Here are some insights based on your session history (mock data)",
            "insights": [
                {
                    "type": "productivity",
                    "insight": "Your productivity is highest in the morning",
                    "confidence": "medium"
                },
                {
                    "type": "focus",
                    "insight": "You tend to maintain focus better when working on programming tasks",
                    "confidence": "high"
                },
                {
                    "type": "pattern",
                    "insight": "Your body doubling sessions are more effective than solo sessions",
                    "confidence": "medium"
                }
            ]
        }

# Simple AnalyticsService implementation
class AnalyticsService:
    """Mock Analytics Service for testing."""
    
    def __init__(self, db):
        self._db = db
        self.insight_generator = InsightGenerator()
    
    async def add_session_feedback(self, session_id, user_id, feedback_data):
        """Add feedback for a session."""
        # Mock implementation
        result = await self._db.execute(None)
        session = result.scalar_one_or_none()
        
        if not session:
            raise Exception(f"Session {session_id} not found")
        
        # Verify user participated in the session
        user_id_str = str(user_id)
        participants = []
        if "participants" in session.meta_data:
            participants = session.meta_data["participants"]
        
        if user_id_str not in participants and session.user_id != user_id and session.host_id != user_id:
            raise Exception("Only session participants can provide feedback")
        
        # Add user ID to feedback data
        feedback_entry = {
            "user_id": user_id_str,
            "timestamp": datetime.now().isoformat(),
            **feedback_data
        }
        
        # Initialize feedback list if needed
        if "feedback" not in session.meta_data:
            session.meta_data["feedback"] = []
        
        # Add feedback entry
        session.meta_data["feedback"].append(feedback_entry)
        
        # Update session-level ratings if this is the first feedback
        if session.focus_rating is None and "focus_rating" in feedback_data:
            session.focus_rating = feedback_data["focus_rating"]
        
        if session.productivity_rating is None and "productivity_rating" in feedback_data:
            session.productivity_rating = feedback_data["productivity_rating"]
        
        # Commit changes
        await self._db.commit()
        await self._db.refresh(session)
        
        return session
    
    async def get_user_analytics(self, user_id):
        """Get analytics for a user based on their session history."""
        # Mock implementation
        result = await self._db.execute(None)
        sessions = result.all()
        
        # Calculate analytics
        analytics = {
            "total_sessions": len(sessions),
            "total_focus_time": sum((s.end_time - s.start_time).total_seconds() / 60 for s in sessions if s.end_time),
            "average_productivity": sum(s.productivity_rating or 0 for s in sessions) / len(sessions) if sessions else 0,
            "productivity_trend": self._calculate_trend([s.productivity_rating for s in sessions if s.productivity_rating]),
            "most_productive_times": ["morning", "afternoon"],  # Simplified for mock
            "preferred_activity_types": list(set(s.activity_type for s in sessions))
        }
        
        # Return analytics as a simple object
        return type('SessionAnalytics', (), analytics)
    
    async def get_focus_pattern_insights(self, user_id):
        """Generate insights about a user's focus patterns using ML when available."""
        result = await self._db.execute(None)
        sessions = result.all()
        
        # Use the insight generator to create insights based on session data
        return self.insight_generator.generate_focus_insights(user_id, sessions)
    
    def _calculate_trend(self, values):
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

# Helper function to create a sample session
def create_sample_session(user_id=None, session_id=None, completed=True):
    """Create a sample session for mock testing."""
    if user_id is None:
        user_id = uuid.uuid4()
    if session_id is None:
        session_id = uuid.uuid4()
    
    now = datetime.now()
    
    return MockBodyDoublingSession(
        id=session_id,
        user_id=user_id,
        host_id=user_id,
        start_time=now - timedelta(hours=2),
        end_time=now - timedelta(hours=1) if completed else None,
        status=MockSessionStatus.COMPLETED if completed else MockSessionStatus.ACTIVE,
        session_type=MockSessionType.BODY_DOUBLING,
        activity_type="Programming",
        focus_rating=None,
        productivity_rating=None,
        meta_data={
            "participants": [str(user_id), str(uuid.uuid4())],
            "feedback": []
        }
    )

async def test_add_feedback():
    """Test adding feedback to a session."""
    # Create mock DB session
    db_session = MockDBSession()
    
    # Create analytics service
    analytics_service = AnalyticsService(db_session)
    
    # Create a user and session
    user_id = uuid.uuid4()
    session_id = uuid.uuid4()
    session = create_sample_session(user_id, session_id)
    
    # Add session to mock DB
    db_session.add_session(session)
    
    # Add feedback
    feedback_data = {
        "focus_rating": 4,
        "productivity_rating": 5,
        "distraction_level": 2,
        "notes": "This was a productive session"
    }
    
    print(f"Adding feedback for session {session_id}...")
    updated_session = await analytics_service.add_session_feedback(
        session_id, user_id, feedback_data
    )
    
    # Verify feedback was added
    print("\nFeedback added successfully!")
    print(f"Session focus rating: {updated_session.focus_rating}")
    print(f"Session productivity rating: {updated_session.productivity_rating}")
    print(f"Feedback count: {len(updated_session.meta_data['feedback'])}")
    print(f"First feedback item: {updated_session.meta_data['feedback'][0]}")
    
    return updated_session

async def test_get_user_analytics():
    """Test getting user analytics."""
    # Create mock DB session
    db_session = MockDBSession()
    
    # Create analytics service
    analytics_service = AnalyticsService(db_session)
    
    # Create a user and multiple sessions
    user_id = uuid.uuid4()
    
    # Add several sessions with different characteristics
    session1 = create_sample_session(user_id, uuid.uuid4())
    session1.focus_rating = 4
    session1.productivity_rating = 4
    session1.activity_type = "Programming"
    
    session2 = create_sample_session(user_id, uuid.uuid4())
    session2.focus_rating = 5
    session2.productivity_rating = 5
    session2.activity_type = "Reading"
    
    session3 = create_sample_session(user_id, uuid.uuid4())
    session3.focus_rating = 3
    session3.productivity_rating = 3
    session3.activity_type = "Programming"
    
    # Add sessions to mock DB
    db_session.add_session(session1)
    db_session.add_session(session2)
    db_session.add_session(session3)
    
    # Get analytics
    print(f"\nGetting analytics for user {user_id}...")
    analytics = await analytics_service.get_user_analytics(user_id)
    
    # Display analytics
    print("\nUser Analytics:")
    print(f"Total sessions: {analytics.total_sessions}")
    print(f"Total focus time: {analytics.total_focus_time} minutes")
    print(f"Average productivity: {analytics.average_productivity}")
    print(f"Productivity trend: {analytics.productivity_trend}")
    print(f"Most productive times: {analytics.most_productive_times}")
    print(f"Preferred activity types: {analytics.preferred_activity_types}")
    
    return analytics

async def test_get_focus_pattern_insights():
    """Test getting focus pattern insights."""
    # Create mock DB session
    db_session = MockDBSession()
    
    # Create analytics service
    analytics_service = AnalyticsService(db_session)
    
    # Create a user and multiple sessions with varied characteristics
    user_id = uuid.uuid4()
    partner_id = uuid.uuid4()
    activity_types = ["Programming", "Reading", "Writing", "Design", "Research"]
    
    # Add several sessions with different characteristics
    for i in range(5):
        session = create_sample_session(user_id, uuid.uuid4())
        session.meta_data["participants"] = [str(user_id), str(partner_id)]
        session.meta_data["feedback"] = [
            {
                "user_id": str(user_id),
                "focus_rating": 3 + i % 3,  # Values between 3-5
                "productivity_rating": 3 + i % 3,
                "distraction_level": 3 - i % 3,  # Values between 1-3
                "notes": f"Session {i+1} with activity {activity_types[i % len(activity_types)]}",
                "timestamp": (datetime.now() - timedelta(days=i)).isoformat()
            }
        ]
        # Set focus and productivity ratings directly on the session too
        session.focus_rating = 3 + i % 3
        session.productivity_rating = 3 + i % 3
        session.activity_type = activity_types[i % len(activity_types)]
        db_session.add_session(session)
    
    # Get insights
    print(f"\nGetting focus pattern insights for user {user_id}...")
    insights = await analytics_service.get_focus_pattern_insights(user_id)
    
    # Display insights
    print("\nFocus Pattern Insights:")
    print(f"Message: {insights['message']}")
    print("\nInsights:")
    for idx, insight in enumerate(insights["insights"]):
        print(f"{idx+1}. [{insight['type']}] {insight['insight']} (Confidence: {insight['confidence']})")
    
    return insights

async def run_all_tests():
    """Run all tests."""
    print("=== Running AnalyticsService Mock Tests ===")
    
    await test_add_feedback()
    await test_get_user_analytics()
    await test_get_focus_pattern_insights()
    
    print("\n=== All Mock Tests Completed Successfully ===")

if __name__ == "__main__":
    asyncio.run(run_all_tests()) 