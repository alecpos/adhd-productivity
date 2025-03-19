import pytest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from app.ml.feature_engineering import FeatureEngineer


@pytest.fixture
def feature_engineer():
    return FeatureEngineer()


@pytest.fixture
def sample_user_data():
    now = datetime.now()

    mental_health_data = [
        {
            "user_id": "test-user",
            "mood_score": 7,
            "stress_level": 4,
            "anxiety_level": 3,
            "energy_level": 6,
            "sleep_quality": 8,
            "notes": "Test log",
            "activity_log": ["Exercise", "Meditation"],
            "timestamp": now - timedelta(days=i),
        }
        for i in range(5)
    ]

    energy_data = [
        {
            "user_id": "test-user",
            "energy_level": 7,
            "focus_level": 8,
            "motivation_level": 6,
            "notes": "Test energy log",
            "timestamp": now - timedelta(days=i),
        }
        for i in range(5)
    ]

    task_data = [
        {
            "user_id": "test-user",
            "title": f"Test task {i}",
            "description": "Test description",
            "priority": "medium",
            "status": "completed" if i % 2 == 0 else "pending",
            "due_date": now + timedelta(days=i + 1),
            "created_at": now - timedelta(days=i),
        }
        for i in range(5)
    ]

    return {
        "mental_health": mental_health_data,
        "energy": energy_data,
        "tasks": task_data,
    }


def test_prepare_features(feature_engineer, sample_user_data):
    """Test preparing features from user data."""
    features, targets = feature_engineer.prepare_features(sample_user_data)

    # Check that features and targets are dictionaries
    assert isinstance(features, dict)
    assert isinstance(targets, dict)

    # Check that all expected keys are present
    expected_keys = ["mental_health", "energy", "tasks"]
    assert all(key in features for key in expected_keys)
    assert all(key in targets for key in expected_keys)

    # Check that all features and targets are numpy arrays
    for key in expected_keys:
        assert isinstance(features[key], np.ndarray)
        assert isinstance(targets[key], np.ndarray)

    # Check dimensions
    assert len(features["mental_health"]) == 5  # Number of mental health logs
    assert len(features["energy"]) == 5  # Number of energy logs
    assert len(features["tasks"]) == 5  # Number of tasks


def test_prepare_mental_health_features(feature_engineer, sample_user_data):
    """Test preparing mental health features."""
    df = pd.DataFrame(sample_user_data["mental_health"])
    features, targets = feature_engineer._prepare_mental_health_features(df)

    # Check dimensions
    assert features.shape[0] == 5  # Number of logs
    assert features.shape[1] > 0  # Should have multiple features
    assert targets.shape[0] == 5  # Number of targets

    # Check that targets are mood scores
    assert np.array_equal(targets, df["mood_score"].values)


def test_prepare_energy_features(feature_engineer, sample_user_data):
    """Test preparing energy features."""
    df = pd.DataFrame(sample_user_data["energy"])
    features, targets = feature_engineer._prepare_energy_features(df)

    # Check dimensions
    assert features.shape[0] == 5  # Number of logs
    assert features.shape[1] > 0  # Should have multiple features
    assert targets.shape[0] == 5  # Number of targets

    # Check that targets are energy levels
    assert np.array_equal(targets, df["energy_level"].values)


def test_prepare_task_features(feature_engineer, sample_user_data):
    """Test preparing task features."""
    df = pd.DataFrame(sample_user_data["tasks"])
    features, targets = feature_engineer._prepare_task_features(df)

    # Check dimensions
    assert features.shape[0] == 5  # Number of tasks
    assert features.shape[1] > 0  # Should have multiple features
    assert targets.shape[0] == 5  # Number of targets

    # Check that targets are binary (completed/not completed)
    assert set(targets) == {0, 1}


def test_extract_time_features(feature_engineer):
    """Test extracting time features."""
    now = datetime.now()
    timestamps = pd.Series([now - timedelta(days=i) for i in range(5)])
    features = feature_engineer._extract_time_features(timestamps)

    # Check dimensions
    assert features.shape[0] == 5  # Number of timestamps
    assert features.shape[1] == 8  # 4 time components * 2 (sin/cos)

    # Check that values are between -1 and 1 (sin/cos)
    assert np.all(features >= -1)
    assert np.all(features <= 1)


def test_encode_activity_log(feature_engineer):
    """Test encoding activity logs."""
    activity_logs = pd.Series(
        [
            ["Exercise", "Meditation"],
            ["Reading", "Exercise"],
            ["Meditation", "Reading"],
            [],
            None,
        ]
    )
    features = feature_engineer._encode_activity_log(activity_logs)

    # Check dimensions
    assert features.shape[0] == 5  # Number of logs
    assert features.shape[1] == 3  # Number of unique activities

    # Check that values are binary
    assert set(np.unique(features)) == {0, 1}


def test_encode_categorical(feature_engineer):
    """Test encoding categorical variables."""
    categories = pd.Series(["high", "medium", "low", "medium", "high"])
    encoded = feature_engineer._encode_categorical(categories)

    # Check dimensions
    assert encoded.shape[0] == 5  # Number of samples
    assert encoded.shape[1] == 3  # Number of unique categories

    # Check that values are binary
    assert set(np.unique(encoded)) == {0, 1}

    # Check that each row has exactly one 1
    assert np.all(encoded.sum(axis=1) == 1)


def test_calculate_time_until_due(feature_engineer):
    """Test calculating time until due date."""
    now = datetime.now()
    due_dates = pd.Series([now + timedelta(days=i) for i in range(5)])
    time_until_due = feature_engineer._calculate_time_until_due(due_dates)

    # Check dimensions
    assert time_until_due.shape[0] == 5  # Number of dates

    # Check that values increase
    assert np.all(np.diff(time_until_due) > 0)
