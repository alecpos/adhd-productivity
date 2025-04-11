"""Test for productivity pattern model."""

import numpy as np
import pandas as pd
import pytest
import tensorflow as tf
from datetime import datetime, timedelta

from app.ml.models.productivity_pattern_model import ProductivityPatternLSTM


@pytest.fixture
def lstm_model():
    """Create a simple productivity pattern LSTM model for testing."""
    model = ProductivityPatternLSTM(
        sequence_length=7,
        n_features=10,
        lstm_units=[32, 16],
        dropout_rate=0.2,
        learning_rate=0.001,
        attention_enabled=True,
    )
    return model


@pytest.fixture
def sample_data():
    """Generate sample data for LSTM model."""
    # Generate random input data
    n_samples = 10
    sequence_length = 7
    n_features = 10

    X = np.random.random((n_samples, sequence_length, n_features))

    # Generate sample target data
    completion_rate = np.random.random((n_samples, 1))
    focus_level = np.random.random((n_samples, 1)) * 10
    energy_level = np.random.random((n_samples, 1)) * 10
    optimal_time = np.zeros((n_samples, 24))
    for i in range(n_samples):
        optimal_time[i, np.random.randint(0, 24)] = 1.0
    bottleneck_score = np.random.random((n_samples, 1))

    y = {
        "completion_rate": completion_rate,
        "focus_level": focus_level,
        "energy_level": energy_level,
        "optimal_time": optimal_time,
        "bottleneck_score": bottleneck_score,
    }

    return X, y


@pytest.fixture
def historical_blocks():
    """Generate sample historical time blocks."""
    now = datetime.now()

    return [
        {
            "start_time": now.replace(hour=9),
            "end_time": now.replace(hour=10),
            "completion_rate": 0.8,
            "focus_level": 7,
            "energy_level": 8,
        },
        {
            "start_time": now.replace(hour=12),
            "end_time": now.replace(hour=13),
            "completion_rate": 0.3,
            "focus_level": 4,
            "energy_level": 3,
        },
        {
            "start_time": now.replace(hour=15),
            "end_time": now.replace(hour=16),
            "completion_rate": 0.9,
            "focus_level": 8,
            "energy_level": 7,
        },
        {
            "start_time": now.replace(hour=12),
            "end_time": now.replace(hour=13),
            "completion_rate": 0.4,
            "focus_level": 3,
            "energy_level": 4,
        },
    ]


def test_model_initialization(lstm_model):
    """Test model initialization."""
    assert lstm_model.sequence_length == 7
    assert lstm_model.n_features == 10
    assert lstm_model.lstm_units == [32, 16]
    assert lstm_model.dropout_rate == 0.2
    assert lstm_model.learning_rate == 0.001
    assert lstm_model.attention_enabled == True
    assert isinstance(lstm_model.model, tf.keras.Model)
    assert not lstm_model.trained


def test_model_build_structure(lstm_model):
    """Test model architecture structure."""
    model = lstm_model.model

    # Check input shape
    assert model.inputs[0].shape.as_list() == [None, 7, 10]

    # Check output structure
    assert len(model.outputs) == 5

    # Check output names
    output_names = [output.name.split("/")[0] for output in model.outputs]
    expected_names = [
        "completion_rate",
        "focus_level",
        "energy_level",
        "optimal_time",
        "bottleneck_score",
    ]
    for name in expected_names:
        assert any(name in output for output in output_names)


def test_detect_productivity_bottlenecks(lstm_model, historical_blocks):
    """Test bottleneck detection."""
    bottlenecks = lstm_model.detect_productivity_bottlenecks(historical_blocks)

    # Should detect hour 12 as a bottleneck
    assert len(bottlenecks) == 1
    assert bottlenecks[0]["hour"] == 12
    assert bottlenecks[0]["avg_completion_rate"] == 0.35  # (0.3 + 0.4) / 2
    assert bottlenecks[0]["bottleneck_score"] == 0.65  # 1.0 - 0.35


def test_analyze_flexible_blocks(lstm_model):
    """Test analyzing flexible blocks."""
    # Mock predictions
    predictions = {
        "completion_rate": np.array([[0.8]]),
        "focus_level": np.array([[7.5]]),
        "energy_level": np.array([[8.0]]),
        "optimal_time": np.zeros((1, 24)),
        "bottleneck_score": np.array([[0.2]]),
    }

    # Set optimal hours
    predictions["optimal_time"][0, 9] = 0.9  # 9am
    predictions["optimal_time"][0, 14] = 0.8  # 2pm
    predictions["optimal_time"][0, 16] = 0.7  # 4pm

    # Test with time constraints
    recommendations = lstm_model.analyze_flexible_blocks(
        flexible_block_indices=[0, 1, 2],
        predictions=predictions,
        time_constraints={"start_hour": 9, "end_hour": 17},
    )

    assert len(recommendations) == 3
    assert recommendations[0]["recommended_hour"] == 9  # First choice
    assert recommendations[1]["recommended_hour"] == 14  # Second choice
    assert recommendations[2]["recommended_hour"] == 16  # Third choice


def test_detect_optimal_windows(lstm_model):
    """Test detecting optimal windows."""
    # Mock predictions
    predictions = {
        "completion_rate": np.array([[0.8]]),
        "focus_level": np.array([[7.5]]),
        "energy_level": np.array([[8.0]]),
        "optimal_time": np.zeros((1, 24)),
        "bottleneck_score": np.array([[0.2]]),
    }

    # Set optimal hours
    predictions["optimal_time"][0, 9] = 0.9  # 9am
    predictions["optimal_time"][0, 14] = 0.8  # 2pm
    predictions["optimal_time"][0, 16] = 0.6  # 4pm (below threshold)

    windows = lstm_model.detect_optimal_windows(
        predictions=predictions, threshold=0.7, min_focus_level=6.0
    )

    assert len(windows) == 2  # Only 9am and 2pm are above threshold
    assert windows[0]["hour"] == 9
    assert windows[0]["confidence"] == 0.9
    assert windows[1]["hour"] == 14
    assert windows[1]["confidence"] == 0.8
