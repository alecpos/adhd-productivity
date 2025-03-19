"""Tests for the CircadianDQNModel from ADHD-18."""

import os
import numpy as np
import pytest
import tensorflow as tf
from unittest.mock import patch, MagicMock, Mock
import tempfile
import json
from datetime import datetime, time

from app.ml.models.adhd17_reinforcement_model import CircadianDQNModel, TaskCognitiveProfile

class TestCircadianDQNModel:
    """Test suite for the CircadianDQNModel class."""
    
    def test_init(self):
        """Test CircadianDQNModel initialization."""
        with patch('app.ml.models.energy_optimizer_model.CircadianRhythmModel', MagicMock()) as mock_crm:
            mock_instance = mock_crm.return_value
            mock_instance.trained = False
            
            model = CircadianDQNModel(state_size=16, action_size=3)
            
            assert model.state_size == 16
            assert model.action_size == 3
            assert model.trained == False
            assert model.circadian_importance == 0.4
            assert hasattr(model, 'circadian_model')
            assert isinstance(model.cognitive_demand_categories, dict)
            assert len(model.cognitive_demand_categories) == 4
    
    def test_build_model(self):
        """Test model building with circadian inputs."""
        with patch('app.ml.models.energy_optimizer_model.CircadianRhythmModel', MagicMock()):
            model = CircadianDQNModel(state_size=16, action_size=3)
            tf_model = model._build_model()
            
            assert isinstance(tf_model, tf.keras.Model)
            
            # Check if model has the expected structure (two inputs)
            assert len(tf_model.inputs) == 2
            
            # Check the input shapes - handle both TensorFlow 1.x and 2.x formats
            # In TF 1.x, input shape is accessed via shape.as_list()
            # In TF 2.x, the shape might be a tuple directly
            task_shape = getattr(tf_model.inputs[0].shape, 'as_list', lambda: tf_model.inputs[0].shape)()
            circ_shape = getattr(tf_model.inputs[1].shape, 'as_list', lambda: tf_model.inputs[1].shape)()
            
            # Check dimensions - handle both list and tuple formats
            assert task_shape[0] is None or task_shape[0] == -1  # Batch dimension
            assert task_shape[1] == 12  # Task features
            
            assert circ_shape[0] is None or circ_shape[0] == -1  # Batch dimension
            assert circ_shape[1] == 4   # Circadian features
            
            # Check output - handle both formats for TF 1.x and 2.x
            output_shape = getattr(tf_model.outputs[0].shape, 'as_list', lambda: tf_model.outputs[0].shape)()
            assert output_shape[0] is None or output_shape[0] == -1  # Batch dimension
            assert output_shape[1] == 3  # Action size
    
    def test_get_action(self):
        """Test action selection with circadian features."""
        with patch('app.ml.models.energy_optimizer_model.CircadianRhythmModel', MagicMock()):
            model = CircadianDQNModel(state_size=16, action_size=3)
            
            # Mock the predict method to return specific values
            model.main_model.predict = Mock(return_value=np.array([[1.0, 2.0, 0.5]]))
            
            # Create a state with both task and circadian components
            state = np.concatenate([np.ones(12), np.zeros(4)])
            
            # Test without exploration
            model.epsilon = 0.0
            action = model.get_action(state, explore=False)
            
            # Should choose action 1 (highest Q-value)
            assert action == 1
            
            # Check that the predict method was called with split inputs
            model.main_model.predict.assert_called_once()
            args, kwargs = model.main_model.predict.call_args
            assert len(args[0]) == 2  # two inputs (task and circadian)
            assert args[0][0].shape == (1, 12)  # task features
            assert args[0][1].shape == (1, 4)   # circadian features
    
    @patch('tensorflow.keras.Model.fit')
    @patch('tensorflow.keras.Model.predict')
    def test_train(self, mock_predict, mock_fit):
        """Test training with circadian features."""
        with patch('app.ml.models.energy_optimizer_model.CircadianRhythmModel', MagicMock()):
            # Setup mock returns for the two predict calls
            mock_predict.side_effect = [
                np.array([[1.0, 2.0, 0.5]]),  # current_q for states
                np.array([[1.5, 0.5, 1.0]])   # next_q for next_states
            ]
            mock_fit.return_value = MagicMock(history={'loss': [0.25]})
            
            model = CircadianDQNModel(state_size=16, action_size=3)
            
            # Add experiences to memory
            task_features = np.ones(12)
            circadian_features = np.zeros(4)
            state = np.concatenate([task_features, circadian_features])
            
            next_task_features = np.ones(12) * 2
            next_circadian_features = np.ones(4) * 0.5
            next_state = np.concatenate([next_task_features, next_circadian_features])
            
            model.memory.add(state, 1, 1.0, next_state, False)
            
            # Train the model
            result = model.train(batch_size=1)
            
            # Check return value
            assert 'loss' in result
            assert result['loss'] == 0.25
            
            # Check predict and fit calls
            assert mock_predict.call_count == 2
            assert mock_fit.call_count == 1
    
    def test_create_state_with_circadian_features(self):
        """Test creating state vectors with circadian features."""
        with patch('app.ml.models.energy_optimizer_model.CircadianRhythmModel') as mock_crm_class:
            # Create a mock for the CircadianRhythmModel instance
            mock_crm = Mock()
            mock_crm.trained = False
            mock_crm_class.return_value = mock_crm
            
            model = CircadianDQNModel(state_size=16, action_size=3)
            
            # Test with a timestamp and task state
            task_state = np.ones(12)
            timestamp = datetime(2025, 3, 15, 10, 30)  # 10:30 AM
            user_data = {
                "sleep_time": time(23, 0),
                "wake_time": time(7, 0),
                "sleep_quality": 0.8,
                "sleep_duration": 8.0,
                "medications": []
            }
            
            # Call the method
            state = model.create_state_with_circadian_features(
                task_state=task_state,
                timestamp=timestamp,
                user_data=user_data
            )
            
            # Check that the state has the correct shape
            assert state.shape == (16,)
            
            # First 12 elements should be task_state
            assert np.array_equal(state[:12], task_state)
            
            # Last 4 elements should be circadian features
            # Check that the circadian features include sine and cosine of hour
            hour = 10.5  # 10:30 AM
            hour_sin = np.sin(2 * np.pi * hour / 24)
            hour_cos = np.cos(2 * np.pi * hour / 24)
            
            assert np.isclose(state[12], hour_sin)
            assert np.isclose(state[13], hour_cos)
            
            # The energy level should be between 0 and 1
            assert 0 <= state[14] <= 1
    
    def test_calculate_circadian_reward(self):
        """Test calculation of circadian rewards."""
        with patch('app.ml.models.energy_optimizer_model.CircadianRhythmModel', MagicMock()):
            model = CircadianDQNModel(state_size=16, action_size=3)
            
            # Test focus-intensive task with matching energy
            reward = model.calculate_circadian_reward(
                task_type="focus_intensive",
                energy_level=7.0,  # Matches the energy threshold for focus_intensive
                completion_status=True,
                task_duration=60.0
            )
            
            # Should get a high positive reward
            assert reward > 0
            
            # Test focus-intensive task with mismatched energy
            reward_low_energy = model.calculate_circadian_reward(
                task_type="focus_intensive",
                energy_level=3.0,  # Much lower than the energy threshold
                completion_status=True,
                task_duration=60.0
            )
            
            # Should get a lower reward due to energy mismatch
            assert reward > reward_low_energy
            
            # Test completion status effect
            reward_not_completed = model.calculate_circadian_reward(
                task_type="focus_intensive",
                energy_level=7.0,
                completion_status=False,
                task_duration=60.0
            )
            
            # Should get a negative reward for not completing
            assert reward_not_completed < 0
            
            # Test duration effect
            reward_short_task = model.calculate_circadian_reward(
                task_type="focus_intensive",
                energy_level=7.0,
                completion_status=True,
                task_duration=30.0
            )
            
            # Shorter task should give lower reward
            assert reward > reward_short_task
    
    def test_combine_rewards(self):
        """Test combining base and circadian rewards."""
        with patch('app.ml.models.energy_optimizer_model.CircadianRhythmModel', MagicMock()):
            model = CircadianDQNModel(state_size=16, action_size=3, circadian_importance=0.4)
            
            combined = model.combine_rewards(base_reward=1.0, circadian_reward=2.0)
            
            # Combined reward should be a weighted sum
            # (1-0.4)*1.0 + 0.4*2.0 = 0.6 + 0.8 = 1.4
            assert np.isclose(combined, 1.4)
            
            # Test with different circadian importance
            model.circadian_importance = 0.7
            combined = model.combine_rewards(base_reward=1.0, circadian_reward=2.0)
            
            # (1-0.7)*1.0 + 0.7*2.0 = 0.3 + 1.4 = 1.7
            assert np.isclose(combined, 1.7)
    
    def test_save_load(self):
        """Test saving and loading the model."""
        with patch('app.ml.models.energy_optimizer_model.CircadianRhythmModel') as mock_crm_class:
            # Mock the CircadianRhythmModel
            mock_crm = Mock()
            mock_crm.trained = False
            mock_crm_class.return_value = mock_crm
            
            # Create a temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:
                model_path = os.path.join(temp_dir, "test_model")
                
                # Create and save a model
                model1 = CircadianDQNModel(
                    state_size=16, 
                    action_size=3,
                    circadian_importance=0.5
                )
                model1.trained = True
                
                with patch.object(mock_crm, 'save') as mock_save:
                    model1.save(model_path)
                
                # Check if files were created - supporting both new .keras and old .h5 formats
                assert os.path.exists(f"{model_path}_main.keras") or os.path.exists(f"{model_path}_main.h5")
                assert os.path.exists(f"{model_path}_target.keras") or os.path.exists(f"{model_path}_target.h5")
                assert os.path.exists(f"{model_path}_params.json")
                
                # Check parameters file content
                with open(f"{model_path}_params.json", "r") as f:
                    params = json.load(f)
                    assert params["state_size"] == 16
                    assert params["action_size"] == 3
                    assert params["circadian_importance"] == 0.5
                    assert params["trained"] == True
                
                # Mock the load method for CircadianRhythmModel
                with patch('app.ml.models.adhd17_reinforcement_model.models.load_model') as mock_load_model, \
                     patch('app.ml.models.adhd17_reinforcement_model.os.path.exists') as mock_exists:
                    
                    # Set up the mock to return True only for specific paths
                    def side_effect(path):
                        if path.endswith("_main.keras"):
                            return True
                        if path.endswith("_target.keras"):
                            return True
                        if path.endswith("_params.json"):
                            return True
                        return False
                    
                    mock_exists.side_effect = side_effect
                    
                    mock_load_model.return_value = tf.keras.Sequential([
                        tf.keras.layers.Dense(3, input_shape=(16,))
                    ])
                    
                    # Load the model
                    model2 = CircadianDQNModel.load(model_path)
                    
                    # Check if parameters were loaded correctly
                    assert model2.state_size == 16
                    assert model2.action_size == 3
                    assert model2.circadian_importance == 0.5
                    assert model2.trained == True
                    assert isinstance(model2.main_model, tf.keras.Model)
                    assert isinstance(model2.target_model, tf.keras.Model)


class TestTaskCognitiveProfile:
    """Test suite for the TaskCognitiveProfile class."""
    
    def test_categorize_task(self):
        """Test task categorization logic."""
        # Focus-intensive task
        task = {
            "focus_required": 8,
            "executive_function_load": 7,
            "creative_required": 3,
            "complexity": 6
        }
        category = TaskCognitiveProfile.categorize_task(task)
        assert category == TaskCognitiveProfile.FOCUS_INTENSIVE
        
        # Creative task
        task = {
            "focus_required": 5,
            "executive_function_load": 5,
            "creative_required": 8,
            "complexity": 6
        }
        category = TaskCognitiveProfile.categorize_task(task)
        assert category == TaskCognitiveProfile.CREATIVE
        
        # Administrative task
        task = {
            "focus_required": 3,
            "executive_function_load": 4,
            "creative_required": 2,
            "complexity": 2
        }
        category = TaskCognitiveProfile.categorize_task(task)
        assert category == TaskCognitiveProfile.ADMINISTRATIVE
        
        # Routine task (default)
        task = {
            "focus_required": 5,
            "executive_function_load": 5,
            "creative_required": 5,
            "complexity": 5
        }
        category = TaskCognitiveProfile.categorize_task(task)
        assert category == TaskCognitiveProfile.ROUTINE
    
    def test_get_energy_requirements(self):
        """Test energy requirements for different task categories."""
        focus_energy = TaskCognitiveProfile.get_energy_requirements(TaskCognitiveProfile.FOCUS_INTENSIVE)
        creative_energy = TaskCognitiveProfile.get_energy_requirements(TaskCognitiveProfile.CREATIVE)
        routine_energy = TaskCognitiveProfile.get_energy_requirements(TaskCognitiveProfile.ROUTINE)
        admin_energy = TaskCognitiveProfile.get_energy_requirements(TaskCognitiveProfile.ADMINISTRATIVE)
        
        # Focus-intensive tasks should require the most energy
        assert focus_energy > creative_energy > routine_energy > admin_energy
        
        # Test with invalid category (should return default)
        unknown_energy = TaskCognitiveProfile.get_energy_requirements("unknown")
        assert unknown_energy == 5.0
    
    def test_calculate_temporal_suitability(self):
        """Test temporal suitability calculation."""
        # Setup user circadian profile
        user_profile = {
            "focus_intensive_preferred_hours": [9, 10, 11],
            "creative_preferred_hours": [14, 15, 16],
            "routine_preferred_hours": [12, 13, 17],
            "administrative_preferred_hours": [8, 18, 19]
        }
        
        # Test focus-intensive task at optimal time and energy
        suitability_optimal = TaskCognitiveProfile.calculate_temporal_suitability(
            task_category=TaskCognitiveProfile.FOCUS_INTENSIVE,
            current_energy=8.0,  # Optimal for focus_intensive
            current_hour=10.0,   # In preferred hours
            user_circadian_profile=user_profile
        )
        
        # Test focus-intensive task at sub-optimal time but optimal energy
        suitability_wrong_time = TaskCognitiveProfile.calculate_temporal_suitability(
            task_category=TaskCognitiveProfile.FOCUS_INTENSIVE,
            current_energy=8.0,  # Optimal for focus_intensive
            current_hour=15.0,   # Not in preferred hours
            user_circadian_profile=user_profile
        )
        
        # Test focus-intensive task at optimal time but sub-optimal energy
        suitability_wrong_energy = TaskCognitiveProfile.calculate_temporal_suitability(
            task_category=TaskCognitiveProfile.FOCUS_INTENSIVE,
            current_energy=4.0,  # Not optimal for focus_intensive
            current_hour=10.0,   # In preferred hours
            user_circadian_profile=user_profile
        )
        
        # Check that optimal conditions give the highest suitability
        assert suitability_optimal > suitability_wrong_time
        assert suitability_optimal > suitability_wrong_energy
        
        # Test with empty user profile (should use default preferences)
        suitability_default = TaskCognitiveProfile.calculate_temporal_suitability(
            task_category=TaskCognitiveProfile.FOCUS_INTENSIVE,
            current_energy=8.0,
            current_hour=10.0,
            user_circadian_profile={}
        )
        
        # Should still be high since default preferences for focus_intensive include morning hours
        assert suitability_default > 0.5


if __name__ == "__main__":
    pytest.main(["-xvs", __file__]) 