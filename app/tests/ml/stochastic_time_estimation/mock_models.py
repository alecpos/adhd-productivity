"""
Mock implementations of core application models for testing.
This avoids the need for a real database connection during tests.
"""

from datetime import datetime
from unittest.mock import MagicMock


class MockBaseModel:
    """Base class for mock models"""

    id = None
    created_at = datetime.now()
    updated_at = datetime.now()

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class MockMentalHealthModel(MockBaseModel):
    """Mock implementation of MentalHealthModel"""

    __tablename__ = "mental_health"

    id = "mh-test-123"
    user_id = "user-test-123"
    date = datetime.now().date()
    mood_score = 7
    anxiety_level = 3
    focus_level = 8
    energy_level = 6
    stress_level = 4
    sleep_hours = 7.5
    meditation_minutes = 15
    exercise_minutes = 30
    notes = "Feeling good today"

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "date": self.date,
            "mood_score": self.mood_score,
            "anxiety_level": self.anxiety_level,
            "focus_level": self.focus_level,
            "energy_level": self.energy_level,
            "stress_level": self.stress_level,
            "sleep_hours": self.sleep_hours,
            "meditation_minutes": self.meditation_minutes,
            "exercise_minutes": self.exercise_minutes,
            "notes": self.notes,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


class MockEnergyModel(MockBaseModel):
    """Mock implementation of EnergyModel"""

    __tablename__ = "energy_levels"

    id = "energy-test-123"
    user_id = "user-test-123"
    date = datetime.now().date()
    morning_energy = 7
    afternoon_energy = 8
    evening_energy = 5
    overall_energy = 6.7
    notes = "Good energy today"

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "date": self.date,
            "morning_energy": self.morning_energy,
            "afternoon_energy": self.afternoon_energy,
            "evening_energy": self.evening_energy,
            "overall_energy": self.overall_energy,
            "notes": self.notes,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


class MockBaseMLModel:
    """Mock implementation of BaseMLModel"""

    def __init__(self, model_path=None):
        self.model_path = model_path
        self.model = None

    async def fit(self, *args, **kwargs):
        """Mock implementation of fit method"""
        return None

    async def predict(self, *args, **kwargs):
        """Mock implementation of predict method"""
        return {"predicted_value": 100}

    def save(self, filepath):
        """Mock implementation of save method"""
        return None

    @classmethod
    def load(cls, filepath):
        """Mock implementation of load method"""
        return cls(model_path=filepath)


class MockFeatureEngineer:
    """Mock implementation of FeatureEngineer"""

    def extract_features(self, data, *args, **kwargs):
        """Mock implementation of extract_features"""
        return {"feature1": 1.0, "feature2": 2.0, "feature3": 3.0}

    def transform(self, features, *args, **kwargs):
        """Mock implementation of transform method"""
        return features
