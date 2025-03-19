"""Tests for the ModelFactory methods related to Epic 4."""

import pytest
from unittest.mock import patch, MagicMock

from app.ml.models.model_factory_model import ModelFactory

class TestModelFactoryEpic4:
    """Test suite for the ModelFactory class methods related to Epic 4."""
    
    @patch('app.ml.models.adhd17_reinforcement_model.CircadianDQNModel')
    def test_create_circadian_dqn(self, mock_cdqn):
        """Test creating a CircadianDQNModel instance."""
        # Setup the mock
        mock_instance = MagicMock()
        mock_cdqn.return_value = mock_instance
        
        # Call the factory method with default parameters
        model = ModelFactory.create_circadian_dqn()
        
        # Check that the constructor was called with default parameters
        mock_cdqn.assert_called_once_with(
            state_size=16,
            action_size=5,
            learning_rate=0.001,
            gamma=0.95,
            epsilon=1.0,
            epsilon_decay=0.995,
            epsilon_min=0.1,
            circadian_importance=0.4,
            circadian_model_path=None
        )
        
        # Check that the method returns the instance
        assert model == mock_instance
        
    @patch('app.ml.models.adhd17_reinforcement_model.CircadianDQNModel')
    def test_create_circadian_dqn_custom_params(self, mock_cdqn):
        """Test creating a CircadianDQNModel instance with custom parameters."""
        # Setup the mock
        mock_instance = MagicMock()
        mock_cdqn.return_value = mock_instance
        
        # Call the factory method with custom parameters
        model = ModelFactory.create_circadian_dqn(
            state_size=24,
            action_size=7,
            learning_rate=0.01,
            gamma=0.9,
            epsilon=0.8,
            epsilon_decay=0.99,
            epsilon_min=0.05,
            circadian_importance=0.6,
            circadian_model_path="/path/to/model"
        )
        
        # Check that the constructor was called with custom parameters
        mock_cdqn.assert_called_once_with(
            state_size=24,
            action_size=7,
            learning_rate=0.01,
            gamma=0.9,
            epsilon=0.8,
            epsilon_decay=0.99,
            epsilon_min=0.05,
            circadian_importance=0.6,
            circadian_model_path="/path/to/model"
        )
        
        # Check that the method returns the instance
        assert model == mock_instance

if __name__ == "__main__":
    pytest.main(["-xvs", __file__]) 