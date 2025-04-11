"""Temporal Pattern Recognition Module."""

from .service import TemporalPatternRecognitionService
from .mock_models import (
    MockProductivityPatternLSTM,
    MockTemporalPatternRecognitionService
)

__all__ = [
    'TemporalPatternRecognitionService',
    'MockProductivityPatternLSTM',
    'MockTemporalPatternRecognitionService'
]

# Mock class for testing
class ProductivityPatternLSTM:
    """Mock class for ProductivityPatternLSTM."""

    def __init__(self):
        """Initialize with mock data."""
        self.feature_names = ["time_of_day", "day_of_week", "task_type", "energy_level", "location"]
        self.input_dim = len(self.feature_names)

    def predict(self, features):
        """Mock prediction."""
        import numpy as np
        return np.array([0.8])

    def get_background_data(self):
        """Get mock background data."""
        import numpy as np
        return np.random.rand(10, self.input_dim)


# Mock service class for testing
class TemporalPatternRecognitionService:
    """Mock service for Temporal Pattern Recognition."""

    def __init__(self):
        """Initialize with mock models."""
        self.productivity_model = ProductivityPatternLSTM()

    async def analyze_productivity_patterns(self, user_id):
        """Mock method for analyzing productivity patterns."""
        return {
            "optimal_times": [
                {"start_time": "09:00", "end_time": "11:00", "score": 0.9},
                {"start_time": "15:00", "end_time": "17:00", "score": 0.8}
            ],
            "productivity_score": 0.85
        }

    async def predict_optimal_time_windows(self, user_id, task_type=None, count=3):
        """Mock method for predicting optimal time windows."""
        return [
            {"start_time": "09:00", "end_time": "11:00", "productivity_score": 0.9, "confidence": 0.85},
            {"start_time": "15:00", "end_time": "17:00", "productivity_score": 0.8, "confidence": 0.82},
            {"start_time": "20:00", "end_time": "22:00", "productivity_score": 0.7, "confidence": 0.75}
        ]
