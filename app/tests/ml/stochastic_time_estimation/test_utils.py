"""
Test utilities for the Stochastic Time Estimation Engine tests

This module contains utility functions and fixtures used across multiple test files
in the Stochastic Time Estimation Engine tests.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
import uuid
from typing import Dict, List, Any, Optional
import numpy as np
import pandas as pd
from unittest.mock import MagicMock, AsyncMock

# Mock model classes
from app.models.task_model import TaskModel
from app.models.user_model import UserModel
from app.models.health_model import HealthMetrics


class MockDatabase:
    """Mock database for testing async database operations."""
    
    def __init__(self):
        self.tasks = {}
        self.users = {}
        self.health_metrics = {}
        self.task_analysis = {}
        self.transition_observations = {}
    
    async def execute(self, statement):
        """Mock execute method that returns a result proxy."""
        result = MockResultProxy(self, statement)
        return result


class MockResultProxy:
    """Mock result proxy for database query results."""
    
    def __init__(self, db, statement):
        self.db = db
        self.statement = statement
        self._result = []
        
        # Populate results based on statement
        # This is a simplified implementation
        if hasattr(statement, 'whereclause'):
            if 'TaskModel' in str(statement):
                for task_id, task in self.db.tasks.items():
                    self._result.append((task,))
            elif 'UserModel' in str(statement):
                for user_id, user in self.db.users.items():
                    self._result.append((user,))
            elif 'HealthMetrics' in str(statement):
                for metric_id, metric in self.db.health_metrics.items():
                    self._result.append((metric,))
    
    def first(self):
        """Return the first result or None."""
        return self._result[0] if self._result else None
    
    def all(self):
        """Return all results."""
        return self._result
    
    def scalars(self):
        """Return a ScalarResult."""
        return MockScalarResult(self._result)


class MockScalarResult:
    """Mock scalar result for database queries."""
    
    def __init__(self, result):
        self._result = result
    
    def all(self):
        """Return all scalar values."""
        return [item[0] for item in self._result if item]


# Mock model generators
def create_mock_task(
    task_id=None, 
    user_id=None, 
    title="Test Task", 
    description="This is a test task", 
    category="work", 
    focus_required=3, 
    energy_required=3, 
    difficulty=3, 
    estimated_duration=60, 
    actual_duration=None, 
    day_of_week=None, 
    hour_of_day=None, 
    location="home", 
    tools_required=None,  # Named consistently with the test errors 
    tools_needed=None,    # Keep original for backward compatibility
    is_collaborative=False, 
    focus_type="analytical",
    complexity=None,
    stress_factors=None,
    base_duration=None
):
    """Create a mock task with the given properties."""
    if task_id is None:
        task_id = f"task-{uuid.uuid4().hex[:8]}"
    if user_id is None:
        user_id = f"user-{uuid.uuid4().hex[:8]}"
    
    # Handle both tools_needed and tools_required for compatibility
    if tools_needed is None and tools_required is None:
        tools_needed = []
    elif tools_needed is None and tools_required is not None:
        tools_needed = tools_required
    
    if day_of_week is None:
        day_of_week = datetime.now().weekday()
    if hour_of_day is None:
        hour_of_day = datetime.now().hour
    if actual_duration is None:
        actual_duration = estimated_duration
    if stress_factors is None:
        stress_factors = {
            "time_pressure": 3, 
            "task_complexity": difficulty, 
            "fatigue": 2
        }
    if complexity is None:
        complexity = difficulty
    if base_duration is None:
        base_duration = estimated_duration
        
    return {
        "id": task_id,
        "user_id": user_id,
        "title": title,
        "description": description,
        "category": category,
        "focus_required": focus_required,
        "energy_required": energy_required,
        "difficulty": difficulty,
        "complexity": complexity,
        "stress_factors": stress_factors,
        "base_duration": base_duration,
        "estimated_duration": estimated_duration,
        "actual_duration": actual_duration,
        "day_of_week": day_of_week,
        "hour_of_day": hour_of_day,
        "location": location,
        "tools_needed": tools_needed,
        "tools_required": tools_needed,  # Add both versions for consistency
        "is_collaborative": is_collaborative,
        "focus_type": focus_type
    }


def create_mock_task_model(
    task_id=None, 
    user_id=None, 
    title="Test Task", 
    description="This is a test task", 
    category="work", 
    focus_required=3, 
    energy_required=3, 
    difficulty=3, 
    estimated_duration=60, 
    actual_duration=None, 
    day_of_week=None, 
    hour_of_day=None, 
    location="home", 
    tools_needed=None, 
    is_collaborative=False, 
    focus_type="analytical",
    complexity=None,
    stress_factors=None,
    base_duration=None,
    subtasks=None,
    is_recurring=False,
    priority=None
):
    """Create a mock TaskModel for testing."""
    if task_id is None:
        task_id = f"task-{uuid.uuid4().hex[:8]}"
    if user_id is None:
        user_id = f"user-{uuid.uuid4().hex[:8]}"
    if tools_needed is None:
        tools_needed = []
    if day_of_week is None:
        day_of_week = datetime.now().weekday()
    if hour_of_day is None:
        hour_of_day = datetime.now().hour
    if actual_duration is None:
        actual_duration = estimated_duration
    if stress_factors is None:
        stress_factors = {
            "time_pressure": 3, 
            "task_complexity": difficulty, 
            "fatigue": 2
        }
    if complexity is None:
        complexity = difficulty
    if base_duration is None:
        base_duration = estimated_duration
    
    # Create a TaskModel instance
    task = MagicMock(spec=TaskModel)
    
    # Set attributes
    task.id = task_id
    task.user_id = user_id
    task.title = title
    task.description = description
    task.category = category
    task.focus_required = focus_required
    task.energy_required = energy_required
    task.difficulty = difficulty
    task.complexity = complexity
    task.stress_factors = stress_factors
    task.base_duration = base_duration
    task.estimated_duration = estimated_duration
    task.actual_duration = actual_duration
    task.day_of_week = day_of_week
    task.hour_of_day = hour_of_day
    task.location = location
    task.tools_needed = tools_needed
    task.is_collaborative = is_collaborative
    task.focus_type = focus_type
    task.subtasks = subtasks or []
    task.is_recurring = is_recurring
    task.priority = priority
    
    return task


def create_mock_user(
    user_id: Optional[str] = None,
    username: str = "testuser",
    email: str = "test@example.com",
    resting_heart_rate: int = 65,
    **kwargs
) -> UserModel:
    """Create a mock user with the given properties."""
    user_id = user_id or str(uuid.uuid4())
    
    user = MagicMock(spec=UserModel)
    user.id = user_id
    user.username = username
    user.email = email
    user.resting_heart_rate = resting_heart_rate
    
    # Add any additional attributes
    for key, value in kwargs.items():
        setattr(user, key, value)
    
    return user


def create_mock_health_metrics(
    metric_id: Optional[str] = None,
    user_id: Optional[str] = None,
    timestamp: Optional[datetime] = None,
    heart_rate: Optional[int] = 75,
    heart_rate_variability: Optional[float] = 50.0,
    mood_level: Optional[int] = 7,
    focus_level: Optional[int] = 6,
    energy_level: Optional[int] = 5,
    anxiety_level: Optional[int] = 3,
    social_pressure: Optional[int] = 4,
    environment_data: Optional[Dict[str, Any]] = None,
    **kwargs
) -> HealthMetrics:
    """Create mock health metrics with the given properties."""
    metric_id = metric_id or str(uuid.uuid4())
    user_id = user_id or str(uuid.uuid4())
    timestamp = timestamp or datetime.now()
    
    metric = MagicMock(spec=HealthMetrics)
    metric.id = metric_id
    metric.user_id = user_id
    metric.timestamp = timestamp
    metric.heart_rate = heart_rate
    metric.heart_rate_variability = heart_rate_variability
    metric.mood_level = mood_level
    metric.focus_level = focus_level
    metric.energy_level = energy_level
    metric.anxiety_level = anxiety_level
    metric.social_pressure = social_pressure
    metric.environment_data = environment_data or {}
    
    # Add any additional attributes
    for key, value in kwargs.items():
        setattr(metric, key, value)
    
    return metric


# Mock database setup
@pytest.fixture
def mock_db():
    """Fixture to create a mock database with test data."""
    db = AsyncMock()
    
    # Create sample tasks
    user_id = "test-user-1"
    tasks = {
        "task-1": create_mock_task(
            task_id="task-1",
            user_id=user_id,
            title="Write report",
            description="Write a detailed report on project progress",
            category="work",
            focus_required=4,
            energy_required=3,
            difficulty=4,
            estimated_duration=90,
            actual_duration=120,
            location="office",
            tools_needed=["computer", "notebook"],
            focus_type="analytical"
        ),
        "task-2": create_mock_task(
            task_id="task-2",
            user_id=user_id,
            title="Team meeting",
            description="Weekly team sync meeting",
            category="work",
            focus_required=3,
            energy_required=4,
            difficulty=2,
            estimated_duration=60,
            actual_duration=75,
            location="conference_room",
            tools_needed=["computer", "whiteboard"],
            is_collaborative=True,
            focus_type="collaborative"
        ),
        "task-3": create_mock_task(
            task_id="task-3",
            user_id=user_id,
            title="Grocery shopping",
            description="Buy groceries for the week",
            category="personal",
            focus_required=2,
            energy_required=3,
            difficulty=2,
            estimated_duration=45,
            actual_duration=60,
            location="store",
            tools_needed=["car", "shopping_list"],
            focus_type="routine"
        )
    }
    
    # Create sample user
    users = {
        user_id: create_mock_user(
            user_id=user_id,
            username="testuser",
            email="test@example.com"
        )
    }
    
    # Create sample health metrics
    health_metrics = {
        f"hm-{i}": create_mock_health_metrics(
            metric_id=f"hm-{i}",
            user_id=user_id,
            timestamp=datetime.now() - timedelta(hours=i),
            heart_rate=75 - (i % 10),
            energy_level=5 + (i % 3),
            focus_level=6 - (i % 4)
        ) for i in range(24)
    }
    
    # Setup execute method to return task, user, or health metrics
    async def mock_execute(statement):
        result = AsyncMock()
        
        # Mock scalar results for different queries
        scalar_result = AsyncMock()
        
        if 'TaskModel' in str(statement):
            # Extract task_id from statement for simple WHERE id = X queries
            task_id = None
            if hasattr(statement, 'whereclause') and 'id' in str(statement.whereclause):
                # This is a simplified extraction, in a real test we'd parse the statement properly
                for task_id in tasks:
                    if task_id in str(statement.whereclause):
                        break
            
            if task_id and task_id in tasks:
                # Single task query
                scalar_result.all.return_value = [tasks[task_id]]
                result.scalars.return_value = scalar_result
                result.first.return_value = (tasks[task_id],)
            else:
                # All tasks query
                scalar_result.all.return_value = list(tasks.values())
                result.scalars.return_value = scalar_result
                result.all.return_value = [(task,) for task in tasks.values()]
        
        elif 'UserModel' in str(statement):
            # Extract user_id from statement
            user_id = None
            if hasattr(statement, 'whereclause') and 'id' in str(statement.whereclause):
                for uid in users:
                    if uid in str(statement.whereclause):
                        user_id = uid
                        break
            
            if user_id and user_id in users:
                # Single user query
                result.first.return_value = (users[user_id],)
            else:
                # All users query
                result.all.return_value = [(user,) for user in users.values()]
        
        elif 'HealthMetrics' in str(statement):
            # Health metrics query - return all for simplicity
            scalar_result.all.return_value = list(health_metrics.values())
            result.scalars.return_value = scalar_result
        
        # Mock transition observations
        elif 'transition_observations' in str(statement):
            # Mock transition query results
            result.all.return_value = [
                {
                    "id": f"transition-{i}",
                    "user_id": user_id,
                    "from_task_id": "task-1", 
                    "to_task_id": "task-2", 
                    "predicted_minutes": 15, 
                    "actual_minutes": 20, 
                    "timestamp": datetime.now() - timedelta(days=i)
                } for i in range(5)
            ]
            
        return result
    
    # Set the execute method on the db mock
    db.execute = mock_execute
    
    return db


# Helper async functions
async def run_async_test(coroutine):
    """Helper function to run an async test."""
    return await coroutine 

def create_mock_model_result(mean=30.0, std=5.0, size=100):
    """Create a mock model result with normal distribution samples
    
    Args:
        mean: Mean of the distribution
        std: Standard deviation of the distribution
        size: Number of samples
        
    Returns:
        A numpy array of samples from a normal distribution
    """
    return np.random.normal(mean, std, size)

def create_mock_pymc3_trace(value_dict=None):
    """Create a mock PyMC3 trace object with specified values
    
    Args:
        value_dict: Dictionary of variable names to values
        
    Returns:
        A mock trace object
    """
    if value_dict is None:
        value_dict = {'duration': np.random.normal(30.0, 5.0, 100)}
        
    mock_trace = MagicMock()
    mock_trace.varnames = list(value_dict.keys())
    
    def get_values_side_effect(varname, **kwargs):
        return value_dict.get(varname, np.array([]))
    
    mock_trace.get_values.side_effect = get_values_side_effect
    mock_trace.__len__.return_value = 100
    
    return mock_trace

def create_mock_task_sequence(num_tasks=3, locations=None, 
                             base_durations=None, complexities=None):
    """Create a sequence of mock tasks for testing
    
    Args:
        num_tasks: Number of tasks to create
        locations: List of locations for the tasks
        base_durations: List of base durations for the tasks
        complexities: List of complexity scores for the tasks
        
    Returns:
        A list of task dictionaries
    """
    if locations is None:
        locations = ["Home", "Office", "Cafe", "Home"]
    
    if base_durations is None:
        base_durations = [30, 60, 45, 90]
        
    if complexities is None:
        complexities = [0.3, 0.5, 0.7, 0.4]
        
    tasks = []
    for i in range(num_tasks):
        loc_idx = i % len(locations)
        dur_idx = i % len(base_durations)
        comp_idx = i % len(complexities)
        
        tasks.append(create_mock_task(
            complexity=complexities[comp_idx],
            base_duration=base_durations[dur_idx],
            location=locations[loc_idx]
        ))
    
    return tasks 

def create_mock_time_block_model(
    id="time-block-1", 
    user_id="test-user-1", 
    title="Test Time Block",
    description="Test Time Block Description",
    start_time=None,
    end_time=None,
    energy_level=5,
    focus_level=5,
    mental_health_score=5,
    buffer_before=None,
    buffer_after=None,
    is_flexible=False,
    task_id=None
):
    """Create a mock TimeBlockModel for testing."""
    # Create a mock
    mock_time_block = MagicMock(spec="TimeBlockModel")
    
    # Set default times if not provided
    if start_time is None:
        start_time = datetime.now()
    if end_time is None:
        end_time = start_time + timedelta(minutes=60)
    
    # Set all the attributes
    mock_time_block.id = id
    mock_time_block.user_id = user_id
    mock_time_block.title = title
    mock_time_block.description = description
    mock_time_block.start_time = start_time
    mock_time_block.end_time = end_time
    mock_time_block.energy_level = energy_level
    mock_time_block.focus_level = focus_level
    mock_time_block.mental_health_score = mental_health_score
    mock_time_block.buffer_before = buffer_before
    mock_time_block.buffer_after = buffer_after
    mock_time_block.is_flexible = is_flexible
    mock_time_block.task_id = task_id
    
    return mock_time_block 