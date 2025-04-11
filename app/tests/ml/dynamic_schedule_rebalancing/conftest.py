"""Fixtures for Epic 4 tests."""

import pytest
import numpy as np
from datetime import datetime, time
from unittest.mock import MagicMock, AsyncMock
import tensorflow as tf

from app.ml.models.adhd17_reinforcement_model import DQNScheduler, CircadianDQNModel, TaskCognitiveProfile


@pytest.fixture
def sample_task_data():
    """Return sample task data for testing."""
    return {
        "focus_intensive_task": {
            "id": "1",
            "title": "Write report",
            "description": "Write quarterly report",
            "estimated_duration": 120,
            "focus_required": 8,
            "executive_function_load": 7,
            "creative_required": 3,
            "complexity": 6
        },
        "creative_task": {
            "id": "2",
            "title": "Brainstorm ideas",
            "description": "Creative brainstorming session",
            "estimated_duration": 60,
            "focus_required": 5,
            "executive_function_load": 4,
            "creative_required": 8,
            "complexity": 5
        },
        "administrative_task": {
            "id": "3",
            "title": "Process emails",
            "description": "Administrative task",
            "estimated_duration": 30,
            "focus_required": 2,
            "executive_function_load": 3,
            "creative_required": 1,
            "complexity": 2
        },
        "routine_task": {
            "id": "4",
            "title": "Review documents",
            "description": "Routine review",
            "estimated_duration": 45,
            "focus_required": 5,
            "executive_function_load": 5,
            "creative_required": 4,
            "complexity": 4
        }
    }


@pytest.fixture
def sample_user_data():
    """Return sample user data for testing."""
    return {
        "sleep_time": time(23, 0),
        "wake_time": time(7, 0),
        "sleep_quality": 0.8,
        "sleep_duration": 8.0,
        "medications": [
            {
                "name": "Medication A",
                "time_taken": time(8, 0)
            }
        ],
        "circadian_profile": {
            "focus_intensive_preferred_hours": [9, 10, 11],
            "creative_preferred_hours": [14, 15, 16],
            "routine_preferred_hours": [12, 13, 17],
            "administrative_preferred_hours": [8, 18, 19]
        }
    }


@pytest.fixture
def mock_dqn_model():
    """Return a mocked DQNScheduler for testing."""
    model = MagicMock(spec=DQNScheduler)
    model.get_action.return_value = 1
    model.train.return_value = {"loss": 0.25}
    model.state_size = 12
    model.action_size = 5
    model.trained = False
    model.main_model = MagicMock()
    model.target_model = MagicMock()
    model.memory = MagicMock()

    return model


@pytest.fixture
def mock_circadian_dqn_model():
    """Return a mocked CircadianDQNModel for testing."""
    model = MagicMock(spec=CircadianDQNModel)
    model.get_action.return_value = 1
    model.train.return_value = {"loss": 0.25}
    model.state_size = 16
    model.action_size = 5
    model.trained = False
    model.circadian_importance = 0.4
    model.main_model = MagicMock()
    model.target_model = MagicMock()
    model.memory = MagicMock()
    model.circadian_model = MagicMock()
    model.calculate_circadian_reward.return_value = 1.5
    model.combine_rewards.return_value = 1.2

    return model


@pytest.fixture
def sample_state_data():
    """Return sample state data for testing."""
    return {
        "task_state": np.ones(12),
        "circadian_state": np.array([0.5, 0.866, 0.7, 0.49]),  # sin/cos of hour, energy, energy²
        "combined_state": np.concatenate([np.ones(12), np.array([0.5, 0.866, 0.7, 0.49])])
    }


@pytest.fixture
def setup_task_cognitive_profile():
    """Return a helper function to create TaskCognitiveProfile instances."""
    def _setup(task_type=None):
        if task_type == "focus_intensive":
            return TaskCognitiveProfile.FOCUS_INTENSIVE
        elif task_type == "creative":
            return TaskCognitiveProfile.CREATIVE
        elif task_type == "administrative":
            return TaskCognitiveProfile.ADMINISTRATIVE
        else:
            return TaskCognitiveProfile.ROUTINE

    return _setup


@pytest.fixture
def create_simple_keras_model():
    """Create a simple Keras model for testing."""
    def _create(input_shape, output_shape):
        model = tf.keras.Sequential([
            tf.keras.layers.Dense(16, activation='relu', input_shape=input_shape),
            tf.keras.layers.Dense(output_shape, activation='linear')
        ])
        model.compile(optimizer='adam', loss='mse')
        return model

    return _create


@pytest.fixture
def assert_dict_structure():
    """Assert that a dictionary has the expected keys."""
    def _assert(actual, expected_keys):
        for key in expected_keys:
            assert key in actual, f"Key '{key}' not found in dictionary"

    return _assert


# Add a pytest helper to compare objects by field
@pytest.fixture
def assert_objects_equal():
    """Assert that two objects have the same field values."""
    def _assert(obj1, obj2, fields):
        for field in fields:
            assert getattr(obj1, field) == getattr(obj2, field), f"Field '{field}' differs between objects"

    return _assert
