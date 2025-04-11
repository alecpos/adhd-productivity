"""Temporal Pattern Recognition Models.

This module contains the core machine learning models for temporal pattern recognition:
1. ProductivityPatternLSTM: LSTM for productivity pattern detection
2. CircadianRhythmModel: Circadian rhythm modeling for task allocation
3. ProductivityCorrelationSystem: Multi-feature correlation for insights
4. MentalHealthFederatedModel: Federated learning for privacy-preserving insights
"""

from typing import Dict, List, Any, Optional, Tuple, Union
import numpy as np
import pandas as pd
from datetime import datetime, timedelta, time
import torch
import torch.nn as nn
import torch.nn.functional as F
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import logging

logger = logging.getLogger(__name__)


class ProductivityPatternLSTM(nn.Module):
    """LSTM model for detecting productivity patterns in time series data."""

    def __init__(
        self,
        input_dim: int = 5,
        hidden_dim: int = 64,
        num_layers: int = 2,
        dropout: float = 0.2,
    ):
        """Initialize the LSTM model.

        Args:
            input_dim: Number of input features
            hidden_dim: Number of hidden units in LSTM
            num_layers: Number of LSTM layers
            dropout: Dropout rate
        """
        super().__init__()
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers

        # LSTM layers
        self.lstm = nn.LSTM(
            input_size=input_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0,
        )

        # Output layer
        self.fc = nn.Linear(hidden_dim, 1)

        # Initialize weights
        self._init_weights()

    def _init_weights(self):
        """Initialize model weights."""
        for name, param in self.named_parameters():
            if "weight" in name:
                nn.init.xavier_uniform_(param)
            elif "bias" in name:
                nn.init.zeros_(param)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass through the model.

        Args:
            x: Input tensor of shape (batch_size, seq_len, input_dim)

        Returns:
            Output tensor of shape (batch_size, seq_len, 1)
        """
        # LSTM forward pass
        lstm_out, _ = self.lstm(x)

        # Apply output layer
        output = self.fc(lstm_out)

        return output

    def predict_patterns(self, X: np.ndarray) -> np.ndarray:
        """Predict productivity patterns for input data.

        Args:
            X: Input data array of shape (n_samples, seq_len, input_dim)

        Returns:
            Predictions array of shape (n_samples, seq_len, 1)
        """
        self.eval()
        with torch.no_grad():
            # Convert to tensor
            X_tensor = torch.FloatTensor(X).to(next(self.parameters()).device)

            # Get predictions
            predictions = self(X_tensor)

            # Convert back to numpy
            return predictions.cpu().numpy()

    def detect_optimal_windows(self, predictions: np.ndarray) -> List[Dict[str, Any]]:
        """Detect optimal time windows for productivity.

        Args:
            predictions: Model predictions array

        Returns:
            List of optimal time windows with metadata
        """
        # Find local maxima in predictions
        peaks = []
        for i in range(1, len(predictions) - 1):
            if predictions[i] > predictions[i - 1] and predictions[i] > predictions[i + 1]:
                peaks.append(
                    {
                        "index": i,
                        "value": float(predictions[i]),
                        "window_size": 2,  # Default window size
                    }
                )

        return peaks

    def detect_productivity_bottlenecks(
        self, time_blocks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Detect productivity bottlenecks in time blocks.

        Args:
            time_blocks: List of time block dictionaries

        Returns:
            List of detected bottlenecks with metadata
        """
        bottlenecks = []
        for block in time_blocks:
            if block.get("productivity_score", 0) < 0.3:  # Threshold for bottleneck
                bottlenecks.append(
                    {
                        "start_time": block["start_time"],
                        "end_time": block["end_time"],
                        "productivity_score": block.get("productivity_score", 0),
                        "suggested_improvements": [
                            "Take a short break",
                            "Switch to a different task",
                            "Review task priority",
                        ],
                    }
                )

        return bottlenecks


class CircadianRhythmModel(nn.Module):
    """Model for circadian rhythm analysis and task allocation."""

    def __init__(
        self,
        input_dim: int = 3,
        hidden_dim: int = 32,
        num_layers: int = 2,
    ):
        """Initialize the circadian rhythm model.

        Args:
            input_dim: Number of input features
            hidden_dim: Number of hidden units
            num_layers: Number of layers
        """
        super().__init__()

        # MLP layers
        layers = []
        in_dim = input_dim
        for _ in range(num_layers):
            layers.extend([nn.Linear(in_dim, hidden_dim), nn.ReLU(), nn.BatchNorm1d(hidden_dim)])
            in_dim = hidden_dim

        # Output layer
        layers.append(nn.Linear(hidden_dim, 1))

        self.model = nn.Sequential(*layers)

        # Initialize weights
        self._init_weights()

    def _init_weights(self):
        """Initialize model weights."""
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight)
                nn.init.zeros_(m.bias)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass through the model.

        Args:
            x: Input tensor of shape (batch_size, input_dim)

        Returns:
            Output tensor of shape (batch_size, 1)
        """
        return self.model(x)

    def predict_energy_levels(self, X: np.ndarray) -> np.ndarray:
        """Predict energy levels for input data.

        Args:
            X: Input data array of shape (n_samples, input_dim)

        Returns:
            Predictions array of shape (n_samples, 1)
        """
        self.eval()
        with torch.no_grad():
            # Convert to tensor
            X_tensor = torch.FloatTensor(X).to(next(self.parameters()).device)

            # Get predictions
            predictions = self(X_tensor)

            # Convert back to numpy
            return predictions.cpu().numpy()

    def get_optimal_task_times(self, predictions: np.ndarray) -> List[Dict[str, Any]]:
        """Get optimal times for different task types.

        Args:
            predictions: Model predictions array

        Returns:
            List of optimal task times with metadata
        """
        optimal_times = []
        for i, pred in enumerate(predictions):
            if pred > 0.7:  # High energy threshold
                optimal_times.append(
                    {
                        "time_index": i,
                        "energy_level": float(pred),
                        "suggested_tasks": [
                            "Deep work",
                            "Creative tasks",
                            "Complex problem solving",
                        ],
                    }
                )
            elif pred > 0.4:  # Medium energy threshold
                optimal_times.append(
                    {
                        "time_index": i,
                        "energy_level": float(pred),
                        "suggested_tasks": ["Meetings", "Email", "Administrative tasks"],
                    }
                )

        return optimal_times


class ProductivityCorrelationSystem(nn.Module):
    """System for analyzing correlations between productivity factors."""

    def __init__(
        self,
        input_dim: int = 10,
        hidden_dim: int = 64,
        num_layers: int = 3,
    ):
        """Initialize the correlation system.

        Args:
            input_dim: Number of input features
            hidden_dim: Number of hidden units
            num_layers: Number of layers
        """
        super().__init__()

        # MLP layers
        layers = []
        in_dim = input_dim
        for _ in range(num_layers):
            layers.extend([nn.Linear(in_dim, hidden_dim), nn.ReLU(), nn.BatchNorm1d(hidden_dim)])
            in_dim = hidden_dim

        # Output layer
        layers.append(nn.Linear(hidden_dim, input_dim))  # Output same size as input for correlation

        self.model = nn.Sequential(*layers)

        # Initialize weights
        self._init_weights()

    def _init_weights(self):
        """Initialize model weights."""
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight)
                nn.init.zeros_(m.bias)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass through the model.

        Args:
            x: Input tensor of shape (batch_size, input_dim)

        Returns:
            Output tensor of shape (batch_size, input_dim)
        """
        return self.model(x)

    def analyze_correlations(self, X: np.ndarray) -> Dict[str, float]:
        """Analyze correlations between productivity factors.

        Args:
            X: Input data array of shape (n_samples, input_dim)

        Returns:
            Dictionary of correlation scores
        """
        self.eval()
        with torch.no_grad():
            # Convert to tensor
            X_tensor = torch.FloatTensor(X).to(next(self.parameters()).device)

            # Get predictions
            predictions = self(X_tensor)

            # Calculate correlations
            correlations = {}
            for i in range(X.shape[1]):
                for j in range(i + 1, X.shape[1]):
                    corr = torch.corrcoef(torch.stack([predictions[:, i], predictions[:, j]]))[0, 1]
                    correlations[f"feature_{i}_feature_{j}"] = float(corr)

            return correlations

    def get_feature_importance(self, X: np.ndarray) -> List[float]:
        """Get importance scores for each feature.

        Args:
            X: Input data array of shape (n_samples, input_dim)

        Returns:
            List of feature importance scores
        """
        self.eval()
        with torch.no_grad():
            # Convert to tensor
            X_tensor = torch.FloatTensor(X).to(next(self.parameters()).device)

            # Get predictions
            predictions = self(X_tensor)

            # Calculate feature importance using gradient
            X_tensor.requires_grad = True
            predictions = self(X_tensor)
            importance = torch.zeros(X.shape[1])

            for i in range(X.shape[1]):
                grad = torch.autograd.grad(predictions[:, i].sum(), X_tensor, retain_graph=True)[0]
                importance[i] = grad.abs().mean()

            return importance.cpu().numpy().tolist()


class MentalHealthFederatedModel(nn.Module):
    """Federated learning model for mental health insights."""

    def __init__(
        self,
        input_dim: int = 8,
        hidden_dim: int = 32,
        num_layers: int = 2,
        dp_noise_multiplier: float = 0.1,
        dp_l2_norm_clip: float = 1.0,
    ):
        """Initialize the federated learning model.

        Args:
            input_dim: Number of input features
            hidden_dim: Number of hidden units
            num_layers: Number of layers
            dp_noise_multiplier: Differential privacy noise multiplier
            dp_l2_norm_clip: L2 norm clipping for differential privacy
        """
        super().__init__()

        self.dp_noise_multiplier = dp_noise_multiplier
        self.dp_l2_norm_clip = dp_l2_norm_clip

        # MLP layers
        layers = []
        in_dim = input_dim
        for _ in range(num_layers):
            layers.extend([nn.Linear(in_dim, hidden_dim), nn.ReLU(), nn.BatchNorm1d(hidden_dim)])
            in_dim = hidden_dim

        # Output layer
        layers.append(nn.Linear(hidden_dim, 1))

        self.model = nn.Sequential(*layers)

        # Initialize weights
        self._init_weights()

    def _init_weights(self):
        """Initialize model weights."""
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight)
                nn.init.zeros_(m.bias)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass through the model.

        Args:
            x: Input tensor of shape (batch_size, input_dim)

        Returns:
            Output tensor of shape (batch_size, 1)
        """
        return self.model(x)

    def _apply_differential_privacy(self, gradients: List[torch.Tensor]) -> List[torch.Tensor]:
        """Apply differential privacy to gradients.

        Args:
            gradients: List of gradient tensors

        Returns:
            List of privatized gradient tensors
        """
        # Clip gradients
        clipped_gradients = []
        for grad in gradients:
            grad_norm = grad.norm(2)
            if grad_norm > self.dp_l2_norm_clip:
                grad = grad * (self.dp_l2_norm_clip / grad_norm)
            clipped_gradients.append(grad)

        # Add noise
        noisy_gradients = []
        for grad in clipped_gradients:
            noise = torch.randn_like(grad) * self.dp_noise_multiplier
            noisy_gradients.append(grad + noise)

        return noisy_gradients

    def federated_update(self, client_updates: List[Dict[str, torch.Tensor]]) -> None:
        """Update model using federated learning.

        Args:
            client_updates: List of client model updates
        """
        # Average client updates
        avg_update = {}
        for key in client_updates[0].keys():
            avg_update[key] = torch.stack([update[key] for update in client_updates]).mean(0)

        # Apply differential privacy
        gradients = list(avg_update.values())
        privatized_gradients = self._apply_differential_privacy(gradients)

        # Update model parameters
        with torch.no_grad():
            for (name, param), grad in zip(self.named_parameters(), privatized_gradients):
                param.add_(grad)

    def predict_mental_health_insights(self, X: np.ndarray) -> Dict[str, float]:
        """Predict mental health insights.

        Args:
            X: Input data array of shape (n_samples, input_dim)

        Returns:
            Dictionary of mental health insights
        """
        self.eval()
        with torch.no_grad():
            # Convert to tensor
            X_tensor = torch.FloatTensor(X).to(next(self.parameters()).device)

            # Get predictions
            predictions = self(X_tensor)

            # Calculate insights
            insights = {
                "stress_level": float(predictions.mean()),
                "anxiety_score": float(predictions.std()),
                "overall_wellbeing": float(1 - predictions.mean()),  # Inverse of stress
            }

            return insights
