"""Tests for the DQN Scheduler model from ADHD-17."""

import os
import numpy as np
import pytest
import tensorflow as tf
from unittest.mock import patch, MagicMock
import tempfile
import json

from app.ml.models.adhd17_reinforcement_model import DQNScheduler, ReplayBuffer

class TestReplayBuffer:
    """Test suite for the ReplayBuffer class."""
    
    def test_init(self):
        """Test ReplayBuffer initialization."""
        buffer = ReplayBuffer(capacity=100)
        assert len(buffer) == 0
        assert buffer.buffer.maxlen == 100
    
    def test_add(self):
        """Test adding experiences to the buffer."""
        buffer = ReplayBuffer(capacity=2)
        buffer.add(np.array([1, 2]), 0, 1.0, np.array([2, 3]), False)
        assert len(buffer) == 1
        
        buffer.add(np.array([3, 4]), 1, 0.5, np.array([4, 5]), True)
        assert len(buffer) == 2
        
        # Test that the buffer maintains its capacity
        buffer.add(np.array([5, 6]), 2, 0.0, np.array([6, 7]), False)
        assert len(buffer) == 2
        
        # The first experience should have been removed
        assert buffer.buffer[0][0][0] == 3
    
    def test_sample(self):
        """Test sampling from the buffer."""
        buffer = ReplayBuffer(capacity=3)
        buffer.add(np.array([1, 2]), 0, 1.0, np.array([2, 3]), False)
        buffer.add(np.array([3, 4]), 1, 0.5, np.array([4, 5]), True)
        buffer.add(np.array([5, 6]), 2, 0.0, np.array([6, 7]), False)
        
        # Test sampling one experience
        samples = buffer.sample(1)
        assert len(samples) == 1
        assert len(samples[0]) == 5  # state, action, reward, next_state, done
        
        # Test sampling all experiences
        samples = buffer.sample(3)
        assert len(samples) == 3
        
        # Test sampling more than available (should return all available)
        samples = buffer.sample(5)
        assert len(samples) == 3

class TestDQNScheduler:
    """Test suite for the DQNScheduler class."""
    
    def test_init(self):
        """Test DQNScheduler initialization."""
        dqn = DQNScheduler(state_size=8, action_size=3)
        
        assert dqn.state_size == 8
        assert dqn.action_size == 3
        assert dqn.trained == False
        assert isinstance(dqn.main_model, tf.keras.Model)
        assert isinstance(dqn.target_model, tf.keras.Model)
        assert isinstance(dqn.memory, ReplayBuffer)
    
    def test_build_model(self):
        """Test model building."""
        dqn = DQNScheduler(state_size=8, action_size=3)
        model = dqn._build_model()
        
        assert isinstance(model, tf.keras.Model)
        
        # Get input shape - compatible with different TensorFlow versions
        # For TensorFlow 2.x, layer.input_shape may not be available
        # Check the model input shape instead
        input_shape = model.input_shape
        output_shape = model.output_shape
        
        # Input shape should match state_size
        assert input_shape[0] is None or input_shape[0] == -1  # Batch dimension
        assert input_shape[1] == 8  # state_size
        
        # Output shape should match action_size
        assert output_shape[0] is None or output_shape[0] == -1  # Batch dimension
        assert output_shape[1] == 3  # action_size
    
    def test_update_target_network(self):
        """Test updating target network weights."""
        dqn = DQNScheduler(state_size=8, action_size=3)
        
        # Modify main model weights
        weights = dqn.main_model.get_weights()
        weights[0] = weights[0] + 1.0  # Change the first weight tensor
        dqn.main_model.set_weights(weights)
        
        # Before update, the weights should be different
        main_weights = dqn.main_model.get_weights()
        target_weights = dqn.target_model.get_weights()
        
        # Check at least one weight tensor is different
        weights_different = False
        for m_w, t_w in zip(main_weights, target_weights):
            if not np.array_equal(m_w, t_w):
                weights_different = True
                break
        
        assert weights_different
        
        # After update, the weights should be the same
        dqn.update_target_network()
        main_weights = dqn.main_model.get_weights()
        target_weights = dqn.target_model.get_weights()
        
        for m_w, t_w in zip(main_weights, target_weights):
            assert np.array_equal(m_w, t_w)
    
    def test_get_action_exploration(self):
        """Test action selection with exploration."""
        dqn = DQNScheduler(state_size=8, action_size=3)
        dqn.epsilon = 1.0  # Always explore
        
        state = np.zeros(8)
        
        # With exploration enabled and epsilon=1.0, should return random actions
        actions = [dqn.get_action(state) for _ in range(20)]
        
        # With 20 samples, we should see at least 2 different actions
        assert len(set(actions)) >= 2
    
    def test_get_action_exploitation(self):
        """Test action selection with exploitation."""
        dqn = DQNScheduler(state_size=8, action_size=3)
        dqn.epsilon = 0.0  # Never explore
        
        # Create a predictable Q-value output
        def mock_predict(state_input, **kwargs):
            return np.array([[1.0, 2.0, 0.5]])
        
        # Replace the predict method with our mock
        dqn.main_model.predict = mock_predict
        
        state = np.zeros(8)
        action = dqn.get_action(state)
        
        # Should choose action 1 (highest Q-value)
        assert action == 1
    
    @patch('tensorflow.keras.Model.fit')
    @patch('tensorflow.keras.Model.predict')
    def test_train(self, mock_predict, mock_fit):
        """Test training the DQN model."""
        # Setup mock returns
        mock_predict.side_effect = [
            np.array([[1.0, 2.0, 0.5]]),  # current_q for states
            np.array([[1.5, 0.5, 1.0]])   # next_q for next_states
        ]
        mock_fit.return_value = MagicMock(history={'loss': [0.25]})
        
        dqn = DQNScheduler(state_size=8, action_size=3)
        
        # Add some experiences to memory
        dqn.memory.add(np.zeros(8), 1, 1.0, np.ones(8), False)
        
        # Train the model
        result = dqn.train(batch_size=1)
        
        # Check return value
        assert 'loss' in result
        assert result['loss'] == 0.25
        
        # Check if model.fit was called with correct shapes
        args, kwargs = mock_fit.call_args
        assert args[0].shape == (1, 8)  # states
        assert args[1].shape == (1, 3)  # target q-values
    
    def test_remember(self):
        """Test storing experiences in memory."""
        dqn = DQNScheduler(state_size=8, action_size=3)
        
        # Initial buffer should be empty
        assert len(dqn.memory) == 0
        
        # Store an experience
        dqn.remember(np.zeros(8), 1, 1.0, np.ones(8), False)
        
        # Buffer should now have one experience
        assert len(dqn.memory) == 1
    
    @patch('app.ml.models.adhd17_reinforcement_model.models.load_model')
    def test_save_load(self, mock_load_model):
        """Test saving and loading the model."""
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            model_path = os.path.join(temp_dir, "test_model")
            
            # Create and save a model
            dqn1 = DQNScheduler(state_size=8, action_size=3)
            dqn1.trained = True
            dqn1.save(model_path)
            
            # Check if files were created - supporting both new .keras and old .h5 formats
            assert os.path.exists(f"{model_path}_main.keras") or os.path.exists(f"{model_path}_main.h5")
            assert os.path.exists(f"{model_path}_target.keras") or os.path.exists(f"{model_path}_target.h5")
            assert os.path.exists(f"{model_path}_params.json")
            
            # Check parameters file content
            with open(f"{model_path}_params.json", "r") as f:
                params = json.load(f)
                assert params["state_size"] == 8
                assert params["action_size"] == 3
                assert params["trained"] == True
            
            # Mock the load_model function to return a simple model
            mock_load_model.return_value = tf.keras.Sequential([
                tf.keras.layers.Dense(3, input_shape=(8,))
            ])
            
            # Load the model
            dqn2 = DQNScheduler.load(model_path)
            
            # Check if parameters were loaded correctly
            assert dqn2.state_size == 8
            assert dqn2.action_size == 3
            assert dqn2.trained == True
            assert isinstance(dqn2.main_model, tf.keras.Model)
            assert isinstance(dqn2.target_model, tf.keras.Model)
            
            # Verify that load_model was called twice (once for main, once for target)
            assert mock_load_model.call_count == 2


if __name__ == "__main__":
    pytest.main(["-xvs", __file__]) 