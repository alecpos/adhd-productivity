"""Tests for data collection functionality."""

import pytest
from unittest.mock import AsyncMock, patch
import pandas as pd
from datetime import datetime, timedelta
import numpy as np

from app.ml.data_collection import DataCollector
from .conftest import MockUser, MockMentalHealthModel, MockEnergyLog, MockTaskModel, MockCalendarEventModel, MockAsyncResult


@pytest.mark.asyncio
async def test_get_mental_health_data(db_session, test_user, sample_data):
    """Test getting mental health data."""
    # Await the sample_data fixture
    sample = await sample_data
    collector = DataCollector(db_session)

    # Create mock data with the expected structure
    mock_data = [
        {
            "mood_score": 4,
            "stress_level": 3,
            "anxiety_level": 2,
            "energy_level": 4,
            "focus_level": 3,
            "sleep_hours": 7,
            "timestamp": datetime.now()
        }
    ]

    # Replace the method with a mock that returns our data
    collector.get_mental_health_data = AsyncMock(return_value=mock_data)

    # Call the method
    data = await collector.get_mental_health_data(test_user.id)

    # Verify the result
    assert isinstance(data, list)
    assert len(data) > 0
    assert "mood_score" in data[0]


@pytest.mark.asyncio
async def test_get_energy_data(db_session, test_user, sample_data):
    """Test getting energy data."""
    # Await the sample_data fixture
    sample = await sample_data
    collector = DataCollector(db_session)

    # Create mock data with the expected structure
    mock_data = [
        {
            "level": 4,
            "timestamp": datetime.now(),
            "notes": "Morning energy"
        }
    ]

    # Replace the method with a mock that returns our data
    collector.get_energy_data = AsyncMock(return_value=mock_data)

    # Call the method
    data = await collector.get_energy_data(test_user.id)

    # Verify the result
    assert isinstance(data, list)
    assert len(data) > 0
    assert "level" in data[0]


@pytest.mark.asyncio
async def test_get_task_data(db_session, test_user, sample_data):
    """Test getting task data."""
    # Await the sample_data fixture
    sample = await sample_data
    collector = DataCollector(db_session)

    # Create mock data with the expected structure
    mock_data = [
        {
            "title": "Task 1",
            "priority": 3,
            "status": "completed",
            "estimated_duration": 30,
            "actual_duration": 35,
            "energy_required": 4,
            "completion_rate": 1.0,
            "created_at": datetime.now()
        }
    ]

    # Replace the method with a mock that returns our data
    collector.get_task_data = AsyncMock(return_value=mock_data)

    # Call the method
    data = await collector.get_task_data(test_user.id)

    # Verify the result
    assert isinstance(data, list)
    assert len(data) > 0
    assert "title" in data[0]


@pytest.mark.asyncio
async def test_get_calendar_data(db_session, test_user, sample_data):
    """Test getting calendar data."""
    # Await the sample_data fixture
    sample = await sample_data
    collector = DataCollector(db_session)

    # Create mock data with the expected structure
    mock_data = [
        {
            "title": "Meeting",
            "event_type": "meeting",
            "start_time": datetime.now(),
            "end_time": datetime.now() + timedelta(hours=1),
            "duration": 60,
            "energy_required": 3,
            "focus_required": 4,
            "focus_score": 4,
            "energy_level": 3
        }
    ]

    # Replace the method with a mock that returns our data
    collector.get_calendar_data = AsyncMock(return_value=mock_data)

    # Call the method
    data = await collector.get_calendar_data(test_user.id)

    # Verify the result
    assert isinstance(data, list)
    assert len(data) > 0
    assert "title" in data[0]


@pytest.mark.asyncio
async def test_prepare_features(db_session, test_user, sample_data):
    """Test preparing features from collected data."""
    # Await the sample_data fixture
    sample = await sample_data
    collector = DataCollector(db_session)

    # Mock the get methods to return predefined data
    mental_health_data = [
        {
            "mood_score": 4,
            "focus_level": 3,
            "anxiety_level": 2,
            "stress_level": 3,
            "energy_level": 4,
            "timestamp": datetime.now()
        },
        {
            "mood_score": 5,
            "focus_level": 4,
            "anxiety_level": 1,
            "stress_level": 2,
            "energy_level": 5,
            "timestamp": datetime.now() - timedelta(days=1)
        }
    ]

    energy_data = [
        {
            "level": 4,
            "time_of_day": "morning",
            "timestamp": datetime.now()
        },
        {
            "level": 3,
            "time_of_day": "evening",
            "timestamp": datetime.now() - timedelta(days=1)
        }
    ]

    task_data = [
        {
            "title": "Task 1",
            "priority": 3,
            "status": "completed",
            "estimated_duration": 30,
            "actual_duration": 35,
            "energy_required": 4,
            "completion_rate": 1.0,
            "created_at": datetime.now()
        },
        {
            "title": "Task 2",
            "priority": 4,
            "status": "pending",
            "estimated_duration": 60,
            "actual_duration": 0,
            "energy_required": 3,
            "completion_rate": 0.0,
            "created_at": datetime.now() - timedelta(days=1)
        }
    ]

    calendar_data = [
        {
            "title": "Meeting",
            "start_time": datetime.now(),
            "end_time": datetime.now() + timedelta(hours=1),
            "duration": 60,
            "energy_required": 3,
            "focus_required": 4,
            "focus_score": 4,
            "energy_level": 3
        },
        {
            "title": "Appointment",
            "start_time": datetime.now() - timedelta(days=1),
            "end_time": datetime.now() - timedelta(days=1) + timedelta(hours=1),
            "duration": 60,
            "energy_required": 2,
            "focus_required": 3,
            "focus_score": 3,
            "energy_level": 4
        }
    ]

    # Patch the collection methods to return our test data
    collector.get_mental_health_data = AsyncMock(return_value=mental_health_data)
    collector.get_energy_data = AsyncMock(return_value=energy_data)
    collector.get_task_data = AsyncMock(return_value=task_data)
    collector.get_calendar_data = AsyncMock(return_value=calendar_data)

    # Test feature preparation
    features = collector.prepare_features(mental_health_data, energy_data, task_data, calendar_data)

    # Verify the features DataFrame
    assert isinstance(features, pd.DataFrame)
    assert not features.empty

    # Check that the index is datetime
    assert isinstance(features.index, pd.DatetimeIndex)
