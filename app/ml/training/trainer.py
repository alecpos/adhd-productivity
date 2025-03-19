"""Model training module."""

from typing import Dict, List, Any, Optional, Tuple, Union, Callable
import numpy as np
import tensorflow as tf
from sklearn.model_selection import train_test_split
from datetime import datetime
import os
import json
import pandas as pd

from ..preprocessing import DataPreprocessor, ProductivityPatternPreprocessor
from ..models.model_factory_model import ModelFactory


class ModelTrainer:
    """Model trainer for ADHD productivity models."""
    
    def __init__(self, model_factory: Optional[ModelFactory] = None):
        """Initialize the trainer with a model factory.
        
        Args:
            model_factory: Factory for creating models
        """
        self.model_factory = model_factory or ModelFactory()
        
    def train_productivity_pattern_model(
        self,
        time_blocks: List[Dict],
        energy_logs: List[Dict],
        mental_health_logs: List[Dict],
        sequence_length: int = 14,
        epochs: int = 50,
        batch_size: int = 32,
        validation_split: float = 0.2,
        early_stopping_patience: int = 5,
        verbose: int = 1
    ) -> Tuple[tf.keras.Model, Dict[str, Any]]:
        """Train a productivity pattern LSTM model.
        
        Args:
            time_blocks: Time block data
            energy_logs: Energy log data
            mental_health_logs: Mental health log data
            sequence_length: Length of sequences for LSTM
            epochs: Number of training epochs
            batch_size: Batch size for training
            validation_split: Portion of data to use for validation
            early_stopping_patience: Patience for early stopping
            verbose: Verbosity level for training
            
        Returns:
            Tuple of trained model and training history
        """
        # Preprocess data
        preprocessor = ProductivityPatternPreprocessor(sequence_length=sequence_length)
        features, targets = preprocessor.preprocess(
            time_blocks=time_blocks,
            energy_logs=energy_logs,
            mental_health_logs=mental_health_logs
        )
        
        if len(features) == 0:
            raise ValueError("No valid data for training")
        
        # Split data
        X_train, X_val, y_train, y_val = train_test_split(
            features, targets, test_size=validation_split, random_state=42
        )
        
        # Create model
        n_features = X_train.shape[2]
        model = self.model_factory.create_productivity_pattern_lstm(
            sequence_length=sequence_length,
            n_features=n_features
        )
        
        # Define callbacks
        callbacks = [
            tf.keras.callbacks.EarlyStopping(
                monitor='val_loss',
                patience=early_stopping_patience,
                restore_best_weights=True
            ),
            tf.keras.callbacks.ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=3,
                min_lr=0.0001
            )
        ]
        
        # Train model
        history = model.fit(
            X_train, y_train,
            epochs=epochs,
            batch_size=batch_size,
            validation_data=(X_val, y_val),
            callbacks=callbacks,
            verbose=verbose
        )
        
        return model, history.history
    
    def train_mental_health_predictor(
        self,
        mental_health_data: List[Dict],
        epochs: int = 50,
        batch_size: int = 32,
        validation_split: float = 0.2,
        verbose: int = 1
    ) -> Tuple[tf.keras.Model, Dict[str, Any]]:
        """Train a mental health prediction model.
        
        Args:
            mental_health_data: Mental health data
            epochs: Number of training epochs
            batch_size: Batch size for training
            validation_split: Portion of data to use for validation
            verbose: Verbosity level for training
            
        Returns:
            Tuple of trained model and training history
        """
        # Preprocess data
        preprocessor = DataPreprocessor(
            mental_health_data=mental_health_data,
            energy_data=[],
            task_data=[],
            calendar_data=[]
        )
        features, targets = preprocessor.prepare_mental_health_features(mental_health_data)
        
        if len(features) == 0:
            raise ValueError("No valid data for training")
        
        # Split data
        X_train, X_val, y_train, y_val = train_test_split(
            features, targets, test_size=validation_split, random_state=42
        )
        
        # Create model
        input_shape = X_train.shape[1:]
        model = self.model_factory.create_mental_health_predictor(input_shape=input_shape)
        
        # Train model
        history = model.fit(
            X_train, y_train,
            epochs=epochs,
            batch_size=batch_size,
            validation_data=(X_val, y_val),
            verbose=verbose
        )
        
        return model, history.history
    
    def train_mood_predictor(
        self,
        mental_health_data: List[Dict],
        epochs: int = 50,
        batch_size: int = 32,
        validation_split: float = 0.2,
        verbose: int = 1
    ) -> Tuple[tf.keras.Model, Dict[str, Any]]:
        """Train a mood prediction model.
        
        Args:
            mental_health_data: Mental health data
            epochs: Number of training epochs
            batch_size: Batch size for training
            validation_split: Portion of data to use for validation
            verbose: Verbosity level for training
            
        Returns:
            Tuple of trained model and training history
        """
        # Preprocess data
        preprocessor = DataPreprocessor(
            mental_health_data=mental_health_data,
            energy_data=[],
            task_data=[],
            calendar_data=[]
        )
        features, targets = preprocessor.prepare_mental_health_features(mental_health_data)
        
        if len(features) == 0:
            raise ValueError("No valid data for training")
        
        # Split data
        X_train, X_val, y_train, y_val = train_test_split(
            features, targets, test_size=validation_split, random_state=42
        )
        
        # Create model
        input_shape = X_train.shape[1:]
        model = self.model_factory.create_mood_predictor(input_shape=input_shape)
        
        # Train model
        history = model.fit(
            X_train, y_train,
            epochs=epochs,
            batch_size=batch_size,
            validation_data=(X_val, y_val),
            verbose=verbose
        )
        
        return model, history.history
    
    def train_energy_predictor(
        self,
        energy_data: List[Dict],
        epochs: int = 50,
        batch_size: int = 32,
        validation_split: float = 0.2,
        verbose: int = 1
    ) -> Tuple[tf.keras.Model, Dict[str, Any]]:
        """Train an energy level prediction model.
        
        Args:
            energy_data: Energy data
            epochs: Number of training epochs
            batch_size: Batch size for training
            validation_split: Portion of data to use for validation
            verbose: Verbosity level for training
            
        Returns:
            Tuple of trained model and training history
        """
        # Preprocess data
        preprocessor = DataPreprocessor(
            mental_health_data=[],
            energy_data=energy_data,
            task_data=[],
            calendar_data=[]
        )
        features, targets = preprocessor.prepare_energy_features(energy_data)
        
        if len(features) == 0:
            raise ValueError("No valid data for training")
        
        # Split data
        X_train, X_val, y_train, y_val = train_test_split(
            features, targets, test_size=validation_split, random_state=42
        )
        
        # Create model
        input_shape = X_train.shape[1:]
        model = self.model_factory.create_energy_predictor(input_shape=input_shape)
        
        # Train model
        history = model.fit(
            X_train, y_train,
            epochs=epochs,
            batch_size=batch_size,
            validation_data=(X_val, y_val),
            verbose=verbose
        )
        
        return model, history.history
    
    def train_task_predictor(
        self,
        task_data: List[Dict],
        epochs: int = 50,
        batch_size: int = 32,
        validation_split: float = 0.2,
        verbose: int = 1
    ) -> Tuple[tf.keras.Model, Dict[str, Any]]:
        """Train a task prediction model.
        
        Args:
            task_data: Task data
            epochs: Number of training epochs
            batch_size: Batch size for training
            validation_split: Portion of data to use for validation
            verbose: Verbosity level for training
            
        Returns:
            Tuple of (trained model, training history)
        """
        # Initialize data preprocessor
        preprocessor = DataPreprocessor(
            mental_health_data=[],
            energy_data=[],
            task_data=task_data,
            calendar_data=[]
        )
        
        # Prepare features and targets
        features, targets = preprocessor.prepare_task_features(task_data)
        
        if len(features) == 0 or len(targets) == 0:
            raise ValueError("No valid data available for training task predictor")
        
        # Convert to numpy arrays
        X = np.array(features)
        y = np.array(targets)
        
        # Create model
        model_factory = ModelFactory()
        model = model_factory.create_task_predictor(input_shape=(X.shape[1],))
        
        # Train model
        history = model.fit(
            X, y,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=validation_split,
            verbose=verbose
        )
        
        # Save model (optional)
        self.save_model(model, "task_predictor")
        
        return model, history.history
    
    def save_model(
        self, 
        model: tf.keras.Model, 
        model_type: str, 
        version: str = None
    ) -> str:
        """Save model to disk.
        
        Args:
            model: Model to save
            model_type: Type of model (e.g., 'productivity', 'energy')
            version: Version string (defaults to timestamp)
            
        Returns:
            Path where model was saved
        """
        if version is None:
            version = datetime.now().strftime("%Y%m%d_%H%M%S")
            
        model_path = f"models/{model_type}_{version}"
        model.save(model_path)
        
        return model_path
    
    def load_model(self, model_path: str) -> tf.keras.Model:
        """Load model from disk.
        
        Args:
            model_path: Path to saved model
            
        Returns:
            Loaded model
        """
        return tf.keras.models.load_model(model_path)
