"""
Tests for the Stochastic Time Estimation Engine

This module contains unit and integration tests for the StochasticTimeEstimationEngine
class that integrates various predictive components to estimate task durations
with uncertainty quantification.
"""

# Mock dependencies before importing the tested module
import sys
from unittest.mock import MagicMock, patch, AsyncMock

# Fix numpy bool issue
import numpy as np

if not hasattr(np, "bool_"):
    np.bool_ = bool

# Create mock modules for all dependencies
mock_theano = MagicMock()
mock_theano_tensor = MagicMock()
mock_pymc3 = MagicMock()


# Mock MentalHealthModel
class MockMentalHealthModel:
    """Mock implementation of MentalHealthModel for testing."""

    id = "mh-test-123"
    user_id = "user-test-123"
    mood_score = 7
    anxiety_level = 3
    focus_level = 8
    energy_level = 6
    stress_level = 4
    sleep_hours = 7.5

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "mood_score": self.mood_score,
            "anxiety_level": self.anxiety_level,
            "focus_level": self.focus_level,
            "energy_level": self.energy_level,
            "stress_level": self.stress_level,
            "sleep_hours": self.sleep_hours,
        }


# Mock EnergyModel
class MockEnergyModel:
    """Mock implementation of EnergyModel for testing."""

    id = "energy-test-123"
    user_id = "user-test-123"
    morning_energy = 7
    afternoon_energy = 8
    evening_energy = 6
    overall_energy = 7.0

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "morning_energy": self.morning_energy,
            "afternoon_energy": self.afternoon_energy,
            "evening_energy": self.evening_energy,
            "overall_energy": self.overall_energy,
        }


# Mock BaseMLModel
class MockBaseMLModel:
    """Mock implementation of BaseMLModel."""

    def __init__(self, model_path=None):
        self.model_path = model_path
        self.model = None

    async def fit(self, *args, **kwargs):
        """Mock implementation of fit method."""
        return None

    async def predict(self, *args, **kwargs):
        """Mock implementation of predict method."""
        return {"predicted_value": 100}

    def save(self, filepath):
        """Mock implementation of save method."""
        return None

    @classmethod
    def load(cls, filepath):
        """Mock implementation of load method."""
        return cls(model_path=filepath)


# Mock FeatureEngineer
class MockFeatureEngineer:
    """Mock implementation of FeatureEngineer."""

    def extract_features(self, data, *args, **kwargs):
        """Mock implementation of extract_features."""
        return {"feature1": 1.0, "feature2": 2.0, "feature3": 3.0}

    def transform(self, features, *args, **kwargs):
        """Mock implementation of transform method."""
        return features


# Create mock modules
sys.modules["theano"] = mock_theano
sys.modules["theano.tensor"] = mock_theano_tensor
sys.modules["pymc3"] = mock_pymc3

# Patch MentalHealthModel
mental_health_module = MagicMock()
mental_health_module.MentalHealthModel = MockMentalHealthModel
sys.modules["app.models.mental_health_model"] = mental_health_module

# Patch EnergyModel
energy_module = MagicMock()
energy_module.EnergyModel = MockEnergyModel
sys.modules["app.models.energy_model"] = energy_module

# Patch BaseMLModel
ml_models_module = MagicMock()
ml_models_module.BaseMLModel = MockBaseMLModel
sys.modules["app.ml.models"] = ml_models_module

# Patch FeatureEngineer
feature_eng_module = MagicMock()
feature_eng_module.FeatureEngineer = MockFeatureEngineer
sys.modules["app.ml.feature_engineering"] = feature_eng_module

# Now import the rest
import pytest
import asyncio
import pandas as pd
from datetime import datetime, timedelta

from app.tests.ml.stochastic_time_estimation.test_utils import (
    create_mock_task,
    create_mock_user,
    create_mock_health_metrics,
    mock_db,
    run_async_test,
    create_mock_model_result,
    create_mock_task_sequence,
)

from app.ml.stochastic_time_estimation import StochasticTimeEstimationEngine


class TestStochasticTimeEstimationEngine:
    """Tests for the StochasticTimeEstimationEngine class."""

    @pytest.fixture
    def engine(self, mock_db):
        """Create a StochasticTimeEstimationEngine instance for testing."""
        # Create mock components
        mock_duration_predictor = MagicMock()
        mock_complexity_analyzer = MagicMock()
        mock_stressor_detector = MagicMock()
        mock_buffer_calculator = MagicMock()

        # Configure default return values for common methods
        mock_duration_predictor.predict.return_value = (30.0, 5.0)
        mock_complexity_analyzer.analyze_task.return_value = {
            "complexity_score": 0.6,
            "cognitive_load": 0.7,
            "steps": 5,
            "ambiguity": 0.3,
            "focus_requirements": 0.8,
            "time_impact": 1.2,
        }
        mock_stressor_detector.detect_current_stress.return_value = {
            "overall_stress": 0.4,
            "physiological": 0.3,
            "environmental": 0.5,
            "cognitive": 0.4,
            "emotional": 0.6,
            "social": 0.2,
            "time_impact": 1.15,
        }
        mock_buffer_calculator.calculate_buffer.return_value = (10.0, 0.8)

        engine = StochasticTimeEstimationEngine(
            db=mock_db,
            duration_predictor=mock_duration_predictor,
            complexity_analyzer=mock_complexity_analyzer,
            stressor_detector=mock_stressor_detector,
            buffer_calculator=mock_buffer_calculator,
        )

        return engine

    @pytest.mark.asyncio
    async def test_init(self, engine):
        """Test that the engine initializes correctly with all components."""
        assert engine.db is not None
        assert engine.duration_predictor is not None
        assert engine.complexity_analyzer is not None
        assert engine.stressor_detector is not None
        assert engine.buffer_calculator is not None

    @pytest.mark.asyncio
    async def test_estimate_task_duration(self, engine):
        """Test the estimation of a single task's duration."""
        # Mock task
        task = create_mock_task(
            title="Write unit tests",
            description="Create comprehensive test suite for the time estimation module",
            difficulty=4,
            estimated_duration=60,
            location="Office",
        )

        # Mock component returns
        engine.duration_predictor.predict.return_value = (45.0, 10.0)
        engine.complexity_analyzer.analyze_task.return_value = {
            "complexity_score": 0.7,
            "time_impact": 1.3,
        }
        engine.stressor_detector.detect_current_stress.return_value = {
            "overall_stress": 0.5,
            "time_impact": 1.2,
        }

        # Test the method
        result = await engine.estimate_task_duration(task["id"])

        # Verify interactions
        engine.duration_predictor.predict.assert_called_once_with(task["id"], user_id=None)
        engine.complexity_analyzer.analyze_task.assert_called_once_with(task["id"])
        engine.stressor_detector.detect_current_stress.assert_called_once_with(
            task["id"], user_id=None
        )

        # Verify results
        assert "base_estimate" in result
        assert "confidence_interval" in result
        assert "factors" in result
        assert isinstance(result["factors"], dict)

        # The result should reflect the combination of the mocked component outputs
        assert result["base_estimate"] > 45.0  # Should be adjusted by complexity and stress

    @pytest.mark.asyncio
    async def test_estimate_schedule(self, engine):
        """Test estimation of a sequence of tasks with transitions."""
        # Create a sequence of tasks
        tasks = create_mock_task_sequence(
            num_tasks=3,
            locations=["Home", "Office", "Coffee Shop"],
            base_durations=[30, 60, 45],
            complexities=[0.4, 0.7, 0.5],
        )

        task_ids = [task["id"] for task in tasks]

        # Mock the buffer calculator
        engine.buffer_calculator.calculate_buffers_for_task_sequence.return_value = [
            (5.0, 0.9),
            (15.0, 0.7),
        ]

        # Mock individual task estimates
        async def mock_estimate_task_duration(task_id):
            for i, task in enumerate(tasks):
                if task["id"] == task_id:
                    return {
                        "base_estimate": task["estimated_duration"] * (1 + tasks[i]["complexity"]),
                        "confidence_interval": (
                            task["estimated_duration"] * 0.8,
                            task["estimated_duration"] * 1.2,
                        ),
                        "factors": {
                            "complexity": tasks[i]["complexity"],
                            "stress": 0.3 + (0.1 * i),
                            "location_familiarity": 0.8 - (0.2 * i),
                        },
                    }

        engine.estimate_task_duration = AsyncMock(side_effect=mock_estimate_task_duration)

        # Test the method
        result = await engine.estimate_schedule(task_ids)

        # Verify calls
        assert engine.estimate_task_duration.call_count == len(tasks)
        engine.buffer_calculator.calculate_buffers_for_task_sequence.assert_called_once_with(
            task_ids
        )

        # Verify results
        assert "tasks" in result
        assert "total_duration" in result
        assert "confidence_interval" in result
        assert "buffers" in result

        assert len(result["tasks"]) == len(tasks)
        assert isinstance(result["total_duration"], (int, float))
        assert len(result["buffers"]) == len(tasks) - 1

    @pytest.mark.asyncio
    async def test_update_with_actual_duration(self, engine):
        """Test updating the model with actual task durations."""
        task_id = "task-123"
        actual_duration = 75

        # Test the method
        await engine.update_with_actual_duration(task_id, actual_duration)

        # Verify all components were updated
        engine.duration_predictor.update_with_observation.assert_called_once_with(
            task_id, actual_duration
        )
        engine.complexity_analyzer.update_with_observation.assert_called_once_with(
            task_id, actual_duration
        )
        engine.stressor_detector.update_with_observation.assert_called_once_with(
            task_id, actual_duration
        )

    @pytest.mark.asyncio
    async def test_update_with_transition_time(self, engine):
        """Test updating the model with actual transition times."""
        from_task_id = "task-123"
        to_task_id = "task-456"
        transition_time = 12

        # Test the method
        await engine.update_with_transition_time(from_task_id, to_task_id, transition_time)

        # Verify buffer calculator was updated
        engine.buffer_calculator.update_with_observation.assert_called_once_with(
            from_task_id, to_task_id, transition_time
        )

    @pytest.mark.asyncio
    async def test_analyze_task_factors(self, engine):
        """Test analysis of factors affecting task duration."""
        task_id = "task-123"

        # Mock component returns for detailed analysis
        engine.complexity_analyzer.analyze_task.return_value = {
            "complexity_score": 0.65,
            "cognitive_load": 0.7,
            "steps": 8,
            "ambiguity": 0.4,
            "focus_requirements": 0.8,
            "topics": ["coding", "testing"],
            "time_impact": 1.25,
        }

        engine.stressor_detector.detect_current_stress.return_value = {
            "overall_stress": 0.45,
            "physiological": 0.4,
            "environmental": 0.5,
            "cognitive": 0.6,
            "emotional": 0.3,
            "social": 0.4,
            "time_impact": 1.18,
        }

        engine.duration_predictor.get_prediction_factors.return_value = {
            "location_factor": 1.1,
            "time_of_day_factor": 0.95,
            "day_of_week_factor": 1.05,
            "feature_importances": {
                "complexity": 0.35,
                "focus_required": 0.25,
                "stress_level": 0.20,
                "previous_similar_tasks": 0.15,
                "location": 0.05,
            },
        }

        # Test the method
        result = await engine.analyze_task_factors(task_id)

        # Verify interactions
        engine.complexity_analyzer.analyze_task.assert_called_once_with(task_id)
        engine.stressor_detector.detect_current_stress.assert_called_once_with(
            task_id, user_id=None
        )
        engine.duration_predictor.get_prediction_factors.assert_called_once_with(task_id)

        # Verify result structure
        assert "complexity_factors" in result
        assert "stress_factors" in result
        assert "prediction_factors" in result
        assert "overall_impact" in result

        # Verify the overall impact calculation
        assert isinstance(result["overall_impact"], dict)
        assert "total_factor" in result["overall_impact"]
        assert result["overall_impact"]["total_factor"] > 1.0  # Given our mock values

    @pytest.mark.asyncio
    async def test_get_historical_accuracy(self, engine):
        """Test retrieval of historical prediction accuracy statistics."""
        user_id = "user-123"

        # Mock component method
        engine.duration_predictor.evaluate.return_value = {
            "mean_absolute_error": 8.5,
            "mean_squared_error": 120.3,
            "r2_score": 0.68,
            "median_absolute_error": 7.2,
            "mean_absolute_percentage_error": 0.22,
            "accuracy_trend": [0.75, 0.78, 0.82, 0.79],
            "sample_count": 35,
        }

        # Test the method
        result = await engine.get_historical_accuracy(user_id)

        # Verify interactions
        engine.duration_predictor.evaluate.assert_called_once_with(user_id=user_id)

        # Verify results structure
        assert "overall_metrics" in result
        assert "trend" in result
        assert "sample_size" in result

        # Verify specific metrics
        assert "accuracy_percentage" in result["overall_metrics"]
        assert result["sample_size"] == 35

    def test_save_and_load(self, engine, tmp_path):
        """Test saving and loading the entire engine state."""
        save_path = str(tmp_path / "engine_state")

        # Test save method
        engine.save(save_path)

        # Verify components' save methods were called
        engine.duration_predictor.save.assert_called_once()
        engine.complexity_analyzer.save.assert_called_once()
        engine.stressor_detector.save.assert_called_once()
        engine.buffer_calculator.save.assert_called_once()

        # Reset mock call counts
        for component in [
            engine.duration_predictor,
            engine.complexity_analyzer,
            engine.stressor_detector,
            engine.buffer_calculator,
        ]:
            component.save.reset_mock()
            component.load.reset_mock()

        # Test load method
        engine.load(save_path)

        # Verify components' load methods were called
        engine.duration_predictor.load.assert_called_once()
        engine.complexity_analyzer.load.assert_called_once()
        engine.stressor_detector.load.assert_called_once()
        engine.buffer_calculator.load.assert_called_once()
