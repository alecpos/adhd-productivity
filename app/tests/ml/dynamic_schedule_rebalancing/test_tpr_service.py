"""Tests for the TemporalPatternRecognitionService methods related to Epic 4."""

import pytest
import numpy as np
from unittest.mock import patch, MagicMock, AsyncMock
import os
from datetime import datetime

# Update import to use the file directly, not the package
import sys
import importlib.util
spec = importlib.util.spec_from_file_location(
    "temporal_pattern_recognition", 
    "/Users/alecposner/Documents/adhd_calendar_backend/app/ml/temporal_pattern_recognition.py"
)
temporal_pattern_recognition = importlib.util.module_from_spec(spec)
sys.modules["temporal_pattern_recognition"] = temporal_pattern_recognition
spec.loader.exec_module(temporal_pattern_recognition)
TemporalPatternRecognitionService = temporal_pattern_recognition.TemporalPatternRecognitionService

from app.ml.models.adhd17_reinforcement_model import CircadianDQNModel, TaskCognitiveProfile

class TestTPRServiceEpic4:
    """Test suite for the TemporalPatternRecognitionService methods related to Epic 4."""
    
    @pytest.mark.asyncio
    @patch('app.ml.models.model_factory_model.ModelFactory.create_circadian_dqn')
    @patch('app.ml.models.adhd17_reinforcement_model.CircadianDQNModel.load')
    @patch('os.path.exists')
    async def test_optimize_schedule_with_circadian_dqn_new_model(
        self, mock_exists, mock_load, mock_create_dqn
    ):
        """Test schedule optimization using a new CircadianDQNModel."""
        # Setup mocks
        mock_exists.return_value = False  # Model file doesn't exist
        mock_model = MagicMock()
        mock_create_dqn.return_value = mock_model
        mock_model.save = MagicMock()
        
        # Create service instance with mocked dependencies
        service = TemporalPatternRecognitionService()
        service.circadian_rhythm = MagicMock()
        service.circadian_rhythm.trained = False
        service.circadian_rhythm.save = MagicMock()
        
        # Sample tasks
        tasks = [
            {
                "id": "1",
                "title": "Write report",
                "description": "Write quarterly report",
                "estimated_duration": 120,
                "focus_required": 8,
                "executive_function_load": 7,
                "creative_required": 5,
                "complexity": 6,
                "priority": 3,
                "is_flexible": True
            },
            {
                "id": "2",
                "title": "Administrative task",
                "description": "Process emails",
                "estimated_duration": 45,
                "focus_required": 3,
                "executive_function_load": 2,
                "creative_required": 1,
                "complexity": 2,
                "priority": 2,
                "is_flexible": True
            }
        ]
        
        # Sample user data
        user_data = {
            "sleep_time": datetime.now().time(),
            "wake_time": datetime.now().time(),
            "sleep_quality": 0.7,
            "sleep_duration": 8.0,
            "medications": [],
            "circadian_profile": {
                "focus_intensive_preferred_hours": [9, 10, 11]
            }
        }
        
        # Call the method
        result = await service.optimize_schedule_with_circadian_dqn(
            user_id="user123",
            tasks=tasks,
            user_data=user_data
        )
        
        # Check that a new model was created
        mock_create_dqn.assert_called_once()
        mock_load.assert_not_called()
        
        # Check result structure
        assert "schedule" in result
        assert "energy_curve" in result
        assert "model_path" in result
        
        # Check that model was saved
        mock_model.save.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('app.ml.models.adhd17_reinforcement_model.CircadianDQNModel.load')
    @patch('os.path.exists')
    async def test_optimize_schedule_with_circadian_dqn_existing_model(
        self, mock_exists, mock_load, assert_dict_structure
    ):
        """Test schedule optimization using an existing CircadianDQNModel."""
        # Setup mocks
        mock_exists.return_value = True  # Model file exists
        mock_model = MagicMock()
        mock_load.return_value = mock_model
        mock_model.save = MagicMock()
        
        # Create service instance with mocked dependencies
        service = TemporalPatternRecognitionService()
        service.circadian_rhythm = MagicMock()
        service.circadian_rhythm.trained = True
        service.circadian_rhythm.predict_daily_curve = MagicMock(return_value={
            "curve_data": [
                {"hour": 9, "energy_level": 8.0},
                {"hour": 10, "energy_level": 7.5},
                {"hour": 14, "energy_level": 6.0}
            ]
        })
        service.circadian_rhythm.save = MagicMock()
        
        # Sample tasks
        tasks = [
            {
                "id": "1",
                "title": "Write report",
                "description": "Write quarterly report",
                "estimated_duration": 120,
                "focus_required": 8,
                "executive_function_load": 7,
                "creative_required": 5,
                "complexity": 6,
                "priority": 3,
                "is_flexible": True
            }
        ]
        
        # Sample user data
        user_data = {
            "sleep_time": datetime.now().time(),
            "wake_time": datetime.now().time(),
            "sleep_quality": 0.7,
            "sleep_duration": 8.0,
            "medications": [],
            "circadian_profile": {
                "focus_intensive_preferred_hours": [9, 10, 11]
            }
        }
        
        # Call the method with existing model path
        result = await service.optimize_schedule_with_circadian_dqn(
            user_id="user123",
            tasks=tasks,
            user_data=user_data,
            model_path="/path/to/existing/model"
        )
        
        # Check that the existing model was loaded
        mock_load.assert_called_once_with("/path/to/existing/model")
        
        # Check result structure using the fixture
        if assert_dict_structure:
            assert_dict_structure(result, ["schedule", "energy_curve", "model_path"])
        else:
            # Fallback if fixture not available
            assert "schedule" in result
            assert "energy_curve" in result
            assert "model_path" in result
        
        # Check tasks categorized correctly
        if result["schedule"]:
            # Verify that the high-focus task was categorized as FOCUS_INTENSIVE
            assert result["schedule"][0]["cognitive_category"] == TaskCognitiveProfile.FOCUS_INTENSIVE
    
    @pytest.mark.asyncio
    async def test_optimize_schedule_with_circadian_dqn_energy_prediction(self, assert_dict_structure):
        """Test energy curve prediction during schedule optimization."""
        # Create service instance with mocked dependencies
        service = TemporalPatternRecognitionService()
        service.circadian_rhythm = MagicMock()
        service.circadian_rhythm.trained = True
        service.circadian_rhythm.predict_daily_curve = MagicMock(return_value={
            "curve_data": [
                {"hour": 9, "energy_level": 8.0},
                {"hour": 10, "energy_level": 7.5},
                {"hour": 14, "energy_level": 6.0},
                {"hour": 15, "energy_level": 5.5},
                {"hour": 17, "energy_level": 4.0}
            ]
        })
        
        # Mock the model creation and loading
        with patch('app.ml.models.model_factory_model.ModelFactory.create_circadian_dqn') as mock_create_dqn, \
             patch('os.path.exists', return_value=False):
            
            mock_model = MagicMock()
            mock_create_dqn.return_value = mock_model
            mock_model.save = MagicMock()
            
            # Sample tasks with different cognitive requirements
            tasks = [
                {
                    "id": "1",
                    "title": "Focus task",
                    "description": "Focus-intensive task",
                    "estimated_duration": 60,
                    "focus_required": 8,
                    "executive_function_load": 7,
                    "creative_required": 3,
                    "priority": 3
                },
                {
                    "id": "2",
                    "title": "Creative task",
                    "description": "Creative task",
                    "estimated_duration": 60,
                    "focus_required": 5,
                    "executive_function_load": 4,
                    "creative_required": 8,
                    "priority": 2
                },
                {
                    "id": "3",
                    "title": "Admin task",
                    "description": "Administrative task",
                    "estimated_duration": 30,
                    "focus_required": 2,
                    "executive_function_load": 3,
                    "creative_required": 1,
                    "complexity": 2,
                    "priority": 1
                }
            ]
            
            # Sample user data
            user_data = {
                "sleep_time": datetime.now().time(),
                "wake_time": datetime.now().time(),
                "circadian_profile": {
                    "focus_intensive_preferred_hours": [9, 10, 11],
                    "creative_preferred_hours": [14, 15, 16],
                    "administrative_preferred_hours": [17, 18]
                }
            }
            
            # Call the method
            result = await service.optimize_schedule_with_circadian_dqn(
                user_id="user123",
                tasks=tasks,
                user_data=user_data
            )
            
            # Check that energy levels were fetched
            service.circadian_rhythm.predict_daily_curve.assert_called_once()
            
            # Check that energy curve data is in the result
            if assert_dict_structure:
                assert_dict_structure(result, ["energy_curve"])
            else:
                assert "energy_curve" in result
            
            # Get the energy levels from the result
            energy_curve = result["energy_curve"]
            
            # Verify the energy prediction was processed correctly
            assert 9 in energy_curve
            assert energy_curve[9] == 8.0
            assert 14 in energy_curve
            assert energy_curve[14] == 6.0
            
            # Check that schedule has energy level and suitability score for each task
            for task in result["schedule"]:
                if assert_dict_structure:
                    assert_dict_structure(task, ["energy_level", "suitability_score", "cognitive_category"])
                else:
                    assert "energy_level" in task
                    assert "suitability_score" in task
                    assert "cognitive_category" in task


if __name__ == "__main__":
    pytest.main(["-xvs", __file__]) 