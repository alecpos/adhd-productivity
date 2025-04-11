"""
Tests for the Contextual Stressor Detector module.

This module contains unit and integration tests for the ContextualStressorDetector
class that detects stress levels from health metrics and wearable data.
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


# Import BaseModel for MockHealthMetrics
from app.models.base_model import BaseModel
from app.models.enums_model import MetricType
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from uuid import uuid4


# Mock HealthMetrics
class MockHealthMetrics:
    """Mock HealthMetrics for testing."""

    def __init__(self, **kwargs):
        self.id = str(uuid4())
        self.user_id = "user-test-123"
        self.timestamp = datetime.utcnow()
        self.metric_type = MetricType.SLEEP
        self.energy_level = 8
        self.mood_level = 7
        self.focus_level = 6
        self.notes = "Test health metrics"
        self.heart_rate = 70
        self.heart_rate_variability = 50
        self.anxiety_level = 3
        self.environment_data = {}

        # Override defaults with any provided values
        for key, value in kwargs.items():
            setattr(self, key, value)

    @property
    def is_low_energy(self) -> bool:
        """Check if energy level is low."""
        return self.energy_level < 4

    @property
    def needs_break(self) -> bool:
        """Check if user needs a break based on focus and energy levels."""
        return self.focus_level < 3 or self.energy_level < 3


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

# Patch HealthMetrics
health_module = MagicMock()
health_module.HealthMetrics = MockHealthMetrics
sys.modules["app.models.health_model"] = health_module

# Patch BaseMLModel
ml_models_module = MagicMock()
ml_models_module.BaseMLModel = MockBaseMLModel
sys.modules["app.ml.models"] = ml_models_module

# Patch FeatureEngineer
feature_eng_module = MagicMock()
feature_eng_module.FeatureEngineer = MockFeatureEngineer
sys.modules["app.ml.feature_engineering"] = feature_eng_module

# Patch StressLevel and StressorType enums
from enum import Enum


class MockStressLevel(Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    EXTREME = "extreme"


class MockStressorType(Enum):
    PHYSIOLOGICAL = "physiological"
    ENVIRONMENTAL = "environmental"
    COGNITIVE = "cognitive"
    EMOTIONAL = "emotional"
    SOCIAL = "social"


# Now import the rest
import pytest
import asyncio
import os
import tempfile
import json
from datetime import datetime, timedelta

from app.tests.ml.stochastic_time_estimation.test_utils import (
    create_mock_task,
    create_mock_user,
    create_mock_health_metrics,
    mock_db,
    run_async_test,
)

from app.ml.stochastic_time_estimation import ContextualStressorDetector


class TestContextualStressorDetector:
    """Tests for the ContextualStressorDetector class."""

    @pytest.fixture
    def detector(self, mock_db):
        """Create a ContextualStressorDetector instance for testing."""
        return ContextualStressorDetector(
            db=mock_db,
            lookback_period=24,
            stress_threshold_hr={"low": 0.1, "moderate": 0.2, "high": 0.3, "extreme": 0.4},
            stress_threshold_hrv={"low": 0.1, "moderate": 0.2, "high": 0.3, "extreme": 0.4},
            stress_impact_weights={
                "physiological": 0.3,
                "environmental": 0.2,
                "cognitive": 0.2,
                "emotional": 0.2,
                "social": 0.1,
            },
        )

    @pytest.mark.asyncio
    async def test_init(self, detector):
        """Test initialization of the detector."""
        assert detector.db is not None
        assert detector.lookback_period == 24
        assert "low" in detector.stress_threshold_hr
        assert "physiological" in detector.stress_impact_weights
        assert "noise_level" in detector.env_thresholds

    @pytest.mark.asyncio
    async def test_detect_current_stress(self, detector):
        """Test detecting current stress levels."""
        # Mock user and health metrics
        user = create_mock_user(user_id="user-123", resting_heart_rate=65)

        # Mock recent health metrics
        metrics = [
            MockHealthMetrics(
                user_id="user-123",
                heart_rate=85,  # Elevated heart rate
                heart_rate_variability=40,
                focus_level=5,  # Moderate focus
                mood_level=6,  # Moderate mood
                anxiety_level=4,  # Moderate anxiety
                timestamp=datetime.now() - timedelta(hours=1),
            ),
            MockHealthMetrics(
                user_id="user-123",
                heart_rate=80,
                heart_rate_variability=45,
                focus_level=6,
                mood_level=7,
                anxiety_level=3,
                timestamp=datetime.now(),
            ),
        ]

        # Mock methods
        detector._get_user = AsyncMock(return_value=user)
        detector._get_recent_health_metrics = AsyncMock(return_value=metrics)
        detector._determine_stress_trend = AsyncMock(return_value="stable")

        # Test the method
        result = await detector.detect_current_stress("user-123")

        # Verify method calls
        detector._get_user.assert_called_once_with("user-123")
        detector._get_recent_health_metrics.assert_called_once_with("user-123")

        # Verify result structure
        assert "overall_stress_level" in result
        assert "stress_score" in result
        assert "detected_stressors" in result
        assert "time_impact_factor" in result
        assert "trend" in result
        assert "analysis_timestamp" in result

        # Verify sensible values
        assert isinstance(result["stress_score"], int)
        assert 0 <= result["stress_score"] <= 100
        assert result["time_impact_factor"] >= 1.0

    @pytest.mark.asyncio
    async def test_detect_current_stress_no_metrics(self, detector):
        """Test detecting stress with no metrics available."""
        # Mock user retrieval
        user = create_mock_user(user_id="user-123")
        detector._get_user = AsyncMock(return_value=user)

        # Mock empty metrics
        detector._get_recent_health_metrics = AsyncMock(return_value=[])

        # Test the method
        result = await detector.detect_current_stress("user-123")

        # Verify result contains expected fallback values
        assert "error" in result
        assert result["overall_stress_level"] == "low"
        assert result["stress_score"] == 0
        assert result["time_impact_factor"] == 1.0

    @pytest.mark.asyncio
    async def test_get_task_stress_adjustment(self, detector):
        """Test getting stress-based adjustment factor for a task."""
        # Mock task
        task = create_mock_task(
            task_id="task-123",
            user_id="user-123",
            difficulty=4,  # Higher difficulty
            focus_required=5,  # High focus requirement
        )

        # Mock methods
        detector._get_task = AsyncMock(return_value=task)
        detector.detect_current_stress = AsyncMock(
            return_value={
                "user_id": "user-123",
                "overall_stress_level": "moderate",
                "stress_score": 45,
                "time_impact_factor": 1.3,
                "detected_stressors": [],
            }
        )
        detector._calculate_task_stress_sensitivity = MagicMock(return_value=0.7)

        # Test the method
        result = await detector.get_task_stress_adjustment("task-123")

        # Verify method calls
        detector._get_task.assert_called_once_with("task-123")
        detector.detect_current_stress.assert_called_once_with("user-123")

        # Verify result is a sensible adjustment factor
        assert isinstance(result, float)
        assert 1.0 <= result <= 2.0
        assert result > 1.3  # Should be higher than the base factor due to task difficulty

    def test_analyze_physiological_stress(self, detector):
        """Test analyzing physiological stress from health metrics."""
        # Create health metrics with elevated heart rate
        metrics = [
            MockHealthMetrics(
                heart_rate=80,  # Higher than resting
                heart_rate_variability=40,
                timestamp=datetime.now() - timedelta(hours=2),
            ),
            MockHealthMetrics(
                heart_rate=85,  # Even higher
                heart_rate_variability=35,  # Lower HRV indicates stress
                timestamp=datetime.now() - timedelta(hours=1),
            ),
            MockHealthMetrics(
                heart_rate=90,  # Highest
                heart_rate_variability=30,  # Lowest
                timestamp=datetime.now(),
            ),
        ]

        # Test the method
        result = detector._analyze_physiological_stress(metrics, resting_hr=65)

        # Verify result
        assert result is not None
        assert result["stressor_type"] == "physiological"
        assert "stress_level" in result
        assert "stress_score" in result
        assert "details" in result
        assert "heart_rate" in result["details"]
        assert "hrv" in result["details"]

        # Verify sensible values
        assert 0 <= result["stress_score"] <= 100
        assert result["details"]["heart_rate"]["value"] == 90  # Latest value

    def test_analyze_physiological_stress_no_metrics(self, detector):
        """Test analyzing physiological stress with no metrics."""
        # Test with empty metrics
        result = detector._analyze_physiological_stress([], resting_hr=65)
        assert result is None

    def test_analyze_environmental_stress(self, detector):
        """Test analyzing environmental stress from metrics."""
        # Create health metrics with environment data
        metrics = [
            MockHealthMetrics(
                environment_data={
                    "noise_level": 75,  # Moderately high
                    "temperature": 27,  # Above comfort zone
                },
                timestamp=datetime.now() - timedelta(hours=1),
            ),
            MockHealthMetrics(
                environment_data={"noise_level": 80, "temperature": 29},  # High  # Higher
                timestamp=datetime.now(),
            ),
        ]

        # Test the method
        result = detector._analyze_environmental_stress(metrics)

        # Verify result
        assert result is not None
        assert result["stressor_type"] == "environmental"
        assert "stress_level" in result
        assert "stress_score" in result
        assert "details" in result

        # Verify sensible values
        assert 0 <= result["stress_score"] <= 100

    def test_analyze_cognitive_stress(self, detector):
        """Test analyzing cognitive stress from focus metrics."""
        # Create health metrics with focus data
        metrics = [
            MockHealthMetrics(
                focus_level=7, timestamp=datetime.now() - timedelta(hours=2)  # Good focus
            ),
            MockHealthMetrics(
                focus_level=5, timestamp=datetime.now() - timedelta(hours=1)  # Moderate focus
            ),
            MockHealthMetrics(
                focus_level=4, timestamp=datetime.now()  # Lower focus indicates stress
            ),
        ]

        # Test the method
        result = detector._analyze_cognitive_stress(metrics)

        # Verify result
        assert result is not None
        assert result["stressor_type"] == "cognitive"
        assert "stress_level" in result
        assert "stress_score" in result
        assert "details" in result
        assert "focus_level" in result["details"]

        # Verify sensible values
        assert 0 <= result["stress_score"] <= 100

    def test_analyze_emotional_stress(self, detector):
        """Test analyzing emotional stress from mood and anxiety metrics."""
        # Create health metrics with mood and anxiety data
        metrics = [
            MockHealthMetrics(
                mood_level=8,  # Good mood
                anxiety_level=3,  # Low anxiety
                timestamp=datetime.now() - timedelta(hours=2),
            ),
            MockHealthMetrics(
                mood_level=6,  # Moderate mood
                anxiety_level=5,  # Moderate anxiety
                timestamp=datetime.now() - timedelta(hours=1),
            ),
            MockHealthMetrics(
                mood_level=5,  # Lower mood
                anxiety_level=6,  # Higher anxiety
                timestamp=datetime.now(),
            ),
        ]

        # Test the method
        result = detector._analyze_emotional_stress(metrics)

        # Verify result
        assert result is not None
        assert result["stressor_type"] == "emotional"
        assert "stress_level" in result
        assert "stress_score" in result
        assert "details" in result
        assert "mood_level" in result["details"]
        assert "anxiety_level" in result["details"]

        # Verify sensible values
        assert 0 <= result["stress_score"] <= 100

    def test_calculate_overall_stress(self, detector):
        """Test calculating overall stress from multiple stressors."""
        # Create stressors with different levels
        stressors = [
            {"stressor_type": "physiological", "stress_level": "moderate", "stress_score": 45},
            {"stressor_type": "environmental", "stress_level": "high", "stress_score": 65},
            {"stressor_type": "cognitive", "stress_level": "low", "stress_score": 25},
        ]

        # Test the method
        stress_score, stress_level = detector._calculate_overall_stress(stressors)

        # Verify results
        assert isinstance(stress_score, int)
        assert 0 <= stress_score <= 100
        assert stress_level in ["low", "moderate", "high", "extreme"]

        # Test with empty stressors
        empty_score, empty_level = detector._calculate_overall_stress([])
        assert empty_score == 0
        assert empty_level == "low"

    def test_calculate_stress_time_impact(self, detector):
        """Test calculating time impact factor from stress score."""
        # Test with various stress scores
        assert detector._calculate_stress_time_impact(0) == 1.0  # No stress = no impact
        assert detector._calculate_stress_time_impact(50) == 1.5  # Moderate stress = 50% more time
        assert detector._calculate_stress_time_impact(100) == 2.0  # Extreme stress = double time

        # Test with values in between
        impact_25 = detector._calculate_stress_time_impact(25)
        impact_75 = detector._calculate_stress_time_impact(75)
        assert 1.0 < impact_25 < impact_75 < 2.0  # Verify monotonic relationship

    def test_stress_level_to_numeric(self, detector):
        """Test conversion of stress level strings to numeric values."""
        assert detector.stress_level_to_numeric("low") == 1
        assert detector.stress_level_to_numeric("moderate") == 2
        assert detector.stress_level_to_numeric("high") == 3
        assert detector.stress_level_to_numeric("extreme") == 4
        assert detector.stress_level_to_numeric("unknown") == 0  # Invalid values

    def test_save_and_load(self, detector):
        """Test saving and loading model parameters."""
        # Setup custom thresholds
        detector.stress_threshold_hr = {
            "low": 0.15,
            "moderate": 0.25,
            "high": 0.35,
            "extreme": 0.45,
        }
        detector.lookback_period = 36

        # Save to a temporary file
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as temp:
            filepath = temp.name
            detector.save(filepath)

            # Verify file exists and contains data
            assert os.path.exists(filepath)
            with open(filepath, "r") as f:
                data = json.load(f)
                assert "stress_threshold_hr" in data
                assert "lookback_period" in data
                assert data["lookback_period"] == 36

        # Load parameters to a new detector
        loaded_detector = ContextualStressorDetector.load(filepath)

        # Verify loaded parameters match saved ones
        assert loaded_detector.stress_threshold_hr == detector.stress_threshold_hr
        assert loaded_detector.lookback_period == detector.lookback_period

        # Clean up
        os.unlink(filepath)
