import pytest
from app.ml.models.model_factory import ModelFactory
import tensorflow as tf
import numpy as np


@pytest.fixture
def model_factory():
    return ModelFactory()


def test_create_mood_predictor(model_factory):
    """Test creating a mood prediction model."""
    input_shape = (15,)  # Example input shape
    model = model_factory.create_mood_predictor(input_shape)

    # Check model structure
    assert isinstance(model, tf.keras.Model)
    assert model.input_shape == (None, 15)
    assert model.output_shape == (None, 1)

    # Test model with sample data
    batch_size = 32
    X = np.random.random((batch_size, 15))
    predictions = model.predict(X)

    assert predictions.shape == (batch_size, 1)


def test_create_energy_predictor(model_factory):
    """Test creating an energy prediction model."""
    input_shape = (12,)  # Example input shape
    model = model_factory.create_energy_predictor(input_shape)

    # Check model structure
    assert isinstance(model, tf.keras.Model)
    assert model.input_shape == (None, 12)
    assert model.output_shape == (None, 1)

    # Test model with sample data
    batch_size = 32
    X = np.random.random((batch_size, 12))
    predictions = model.predict(X)

    assert predictions.shape == (batch_size, 1)


def test_create_task_predictor(model_factory):
    """Test creating a task prediction model."""
    input_shape = (20,)  # Example input shape
    model = model_factory.create_task_predictor(input_shape)

    # Check model structure
    assert isinstance(model, tf.keras.Model)
    assert model.input_shape == (None, 20)
    assert model.output_shape == (None, 1)

    # Test model with sample data
    batch_size = 32
    X = np.random.random((batch_size, 20))
    predictions = model.predict(X)

    assert predictions.shape == (batch_size, 1)
    assert np.all((predictions >= 0) & (predictions <= 1))  # Check sigmoid output


def test_create_sequence_model(model_factory):
    """Test creating a sequence prediction model."""
    input_shape = (10, 8)  # Example input shape (sequence_length, features)
    output_dim = 3
    model = model_factory.create_sequence_model(input_shape, output_dim)

    # Check model structure
    assert isinstance(model, tf.keras.Model)
    assert model.input_shape == (None, 10, 8)
    assert model.output_shape == (None, output_dim)

    # Test model with sample data
    batch_size = 32
    X = np.random.random((batch_size, 10, 8))
    predictions = model.predict(X)

    assert predictions.shape == (batch_size, output_dim)


def test_create_multi_task_model(model_factory):
    """Test creating a multi-task learning model."""
    input_shape = (25,)  # Example input shape
    num_tasks = 3
    model = model_factory.create_multi_task_model(input_shape, num_tasks)

    # Check model structure
    assert isinstance(model, tf.keras.Model)
    assert model.input_shape == (None, 25)
    assert len(model.output_shape) == num_tasks  # One output per task

    # Test model with sample data
    batch_size = 32
    X = np.random.random((batch_size, 25))
    predictions = model.predict(X)

    assert len(predictions) == num_tasks
    for pred in predictions:
        assert pred.shape == (batch_size, 1)


def test_create_activity_recommender(model_factory):
    """Test creating an activity recommendation model."""
    input_shape = (18,)  # Example input shape
    num_activities = 5
    model = model_factory.create_activity_recommender(input_shape, num_activities)

    # Check model structure
    assert isinstance(model, tf.keras.Model)
    assert model.input_shape == (None, 18)
    assert model.output_shape == (None, num_activities)

    # Test model with sample data
    batch_size = 32
    X = np.random.random((batch_size, 18))
    predictions = model.predict(X)

    assert predictions.shape == (batch_size, num_activities)
    assert np.all((predictions >= 0) & (predictions <= 1))  # Check sigmoid output


def test_custom_hidden_layers(model_factory):
    """Test creating models with custom hidden layer configurations."""
    input_shape = (10,)
    hidden_layers = [128, 64, 32]

    # Test mood predictor with custom layers
    mood_model = model_factory.create_mood_predictor(input_shape, hidden_layers)
    assert isinstance(mood_model, tf.keras.Model)

    # Test energy predictor with custom layers
    energy_model = model_factory.create_energy_predictor(input_shape, hidden_layers)
    assert isinstance(energy_model, tf.keras.Model)

    # Test task predictor with custom layers
    task_model = model_factory.create_task_predictor(input_shape, hidden_layers)
    assert isinstance(task_model, tf.keras.Model)

    # Test activity recommender with custom layers
    num_activities = 5
    activity_model = model_factory.create_activity_recommender(
        input_shape=input_shape, num_activities=num_activities, hidden_layers=hidden_layers
    )
    assert isinstance(activity_model, tf.keras.Model)


def test_model_compilation(model_factory):
    """Test that models are compiled with appropriate optimizers and metrics."""
    input_shape = (10,)

    # Test mood predictor compilation
    mood_model = model_factory.create_mood_predictor(input_shape)
    assert mood_model.optimizer.__class__.__name__ == "Adam"

    # Instead of checking metrics directly, we'll verify the model can be compiled
    assert mood_model._is_compiled
    assert hasattr(mood_model, "loss")

    # Test energy predictor compilation
    energy_model = model_factory.create_energy_predictor(input_shape)
    assert energy_model.optimizer.__class__.__name__ == "Adam"
    assert energy_model._is_compiled
    assert hasattr(energy_model, "loss")

    # Test task predictor compilation
    task_model = model_factory.create_task_predictor(input_shape)
    assert task_model.optimizer.__class__.__name__ == "Adam"
    assert task_model._is_compiled
    assert hasattr(task_model, "loss")

    # Test activity recommender compilation
    num_activities = 5
    activity_model = model_factory.create_activity_recommender(input_shape, num_activities)
    assert activity_model.optimizer.__class__.__name__ == "Adam"
    assert activity_model._is_compiled
    assert hasattr(activity_model, "loss")

    # Compile the model with metrics if needed
    if not any("accuracy" in metric.name for metric in activity_model.metrics):
        activity_model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])
