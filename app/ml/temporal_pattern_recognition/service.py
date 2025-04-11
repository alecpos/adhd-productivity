"""Temporal Pattern Recognition (TPR) Integration Service.

This module integrates all components of EPIC-1: Temporal Pattern Recognition (TPR) Models
to provide a unified interface for temporal pattern analysis and optimization.

Components:
- LSTM infrastructure for productivity pattern detection
- Circadian rhythm modeling for optimal task allocation
- Multi-feature correlation system for productivity insights
- Federated learning infrastructure for privacy-preserving insights
"""

from typing import Dict, List, Any, Optional, Tuple, Union
import numpy as np
import pandas as pd
from datetime import datetime, timedelta, time
import os
import json
import logging
from sqlalchemy.ext.asyncio import AsyncSession
import torch
import torch.nn as nn
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

from app.ml.temporal_pattern_recognition.models import (
    ProductivityPatternLSTM,
    CircadianRhythmModel,
    ProductivityCorrelationSystem,
    MentalHealthFederatedModel,
)

from app.schemas.scheduling_schema import EnergySchedulingPattern, WorkHours
import logging

logger = logging.getLogger(__name__)


class TemporalPatternRecognitionService:
    """Service integrating all EPIC-1 components for temporal pattern recognition.

    This service provides a unified interface to all four EPIC-1 model components:
    1. ProductivityPatternLSTM: LSTM for productivity pattern detection
    2. CircadianRhythmModel: Circadian rhythm modeling for task allocation
    3. ProductivityCorrelationSystem: Multi-feature correlation for insights
    4. MentalHealthFederatedModel: Federated learning for privacy-preserving insights
    """

    def __init__(
        self,
        db: Optional[AsyncSession] = None,
        productivity_pattern_model_path: Optional[str] = None,
        circadian_rhythm_model_path: Optional[str] = None,
        correlation_system_path: Optional[str] = None,
        federated_model_path: Optional[str] = None,
    ):
        """Initialize the TPR service with models.

        Args:
            db: An optional database session for data access
            productivity_pattern_model_path: Path to saved LSTM model
            circadian_rhythm_model_path: Path to saved circadian rhythm model
            correlation_system_path: Path to saved correlation system
            federated_model_path: Path to saved federated learning model
        """
        self.db = db
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Using device: {self.device}")

        # Initialize component models
        # 1. Productivity Pattern LSTM
        if productivity_pattern_model_path and os.path.exists(productivity_pattern_model_path):
            self.productivity_pattern = self._load_model(
                ProductivityPatternLSTM, productivity_pattern_model_path
            )
            logger.info(f"Loaded productivity pattern model from {productivity_pattern_model_path}")
        else:
            self.productivity_pattern = ProductivityPatternLSTM().to(self.device)
            logger.info("Initialized new productivity pattern model")

        # 2. Circadian Rhythm Model
        if circadian_rhythm_model_path and os.path.exists(circadian_rhythm_model_path):
            self.circadian_rhythm = self._load_model(
                CircadianRhythmModel, circadian_rhythm_model_path
            )
            logger.info(f"Loaded circadian rhythm model from {circadian_rhythm_model_path}")
        else:
            self.circadian_rhythm = CircadianRhythmModel().to(self.device)
            logger.info("Initialized new circadian rhythm model")

        # 3. Productivity Correlation System
        if correlation_system_path and os.path.exists(correlation_system_path):
            self.correlation_system = self._load_model(
                ProductivityCorrelationSystem, correlation_system_path
            )
            logger.info(f"Loaded correlation system from {correlation_system_path}")
        else:
            self.correlation_system = ProductivityCorrelationSystem().to(self.device)
            logger.info("Initialized new correlation system")

        # 4. Federated Learning for Mental Health
        if federated_model_path and os.path.exists(federated_model_path):
            self.federated_model = self._load_model(
                MentalHealthFederatedModel, federated_model_path
            )
            logger.info(f"Loaded federated model from {federated_model_path}")
        else:
            self.federated_model = MentalHealthFederatedModel(
                input_dim=10, dp_noise_multiplier=0.1, dp_l2_norm_clip=1.0
            ).to(self.device)
            logger.info("Initialized new federated model")

        self.scaler = StandardScaler()
        self.kmeans = KMeans(n_clusters=3, random_state=42)

        logger.info("Temporal Pattern Recognition Service initialized")

    def _load_model(self, model_class: nn.Module, model_path: str) -> nn.Module:
        """Load a PyTorch model from disk.

        Args:
            model_class: The model class to instantiate
            model_path: Path to the saved model state dict

        Returns:
            Loaded model instance
        """
        try:
            model = model_class()
            model.load_state_dict(torch.load(model_path, map_location=self.device))
            model.to(self.device)
            model.eval()  # Set to evaluation mode
            return model
        except Exception as e:
            logger.error(f"Error loading model from {model_path}: {str(e)}")
            return model_class().to(self.device)

    async def save_models(self, base_path: str = "app/ml/saved_models/") -> Dict[str, str]:
        """Save all models to disk.

        Args:
            base_path: Base path for saving models

        Returns:
            Dictionary mapping model names to their save paths
        """
        os.makedirs(base_path, exist_ok=True)
        saved_paths = {}

        # Save each model
        models = {
            "productivity_pattern": self.productivity_pattern,
            "circadian_rhythm": self.circadian_rhythm,
            "correlation_system": self.correlation_system,
            "federated_model": self.federated_model,
        }

        for name, model in models.items():
            path = os.path.join(base_path, f"{name}.pt")
            torch.save(model.state_dict(), path)
            saved_paths[name] = path
            logger.info(f"Saved {name} model to {path}")

        return saved_paths

    async def analyze_productivity_patterns(
        self,
        user_id: str,
        time_blocks: List[Dict[str, Any]],
        mental_health_logs: List[Dict[str, Any]],
        days_to_predict: int = 7,
    ) -> Dict[str, Any]:
        """Analyze productivity patterns using the LSTM model.

        Args:
            user_id: User ID
            time_blocks: Historical time block data
            mental_health_logs: Mental health log data
            days_to_predict: Number of days to predict patterns for

        Returns:
            Dictionary containing productivity pattern analysis results
        """
        logger.info(f"Analyzing productivity patterns for user {user_id}")

        # Preprocess data for LSTM
        from app.ml.preprocessing.preprocessor import ProductivityPatternPreprocessor

        preprocessor = ProductivityPatternPreprocessor()
        X, y = preprocessor.preprocess(time_blocks, mental_health_logs)

        # Make predictions
        if len(X) > 0:
            predictions = self.productivity_pattern.predict_patterns(X)
            optimal_windows = self.productivity_pattern.detect_optimal_windows(predictions)
            bottlenecks = self.productivity_pattern.detect_productivity_bottlenecks(time_blocks)

            return {
                "optimal_windows": optimal_windows,
                "productivity_bottlenecks": bottlenecks,
                "predictions": predictions.tolist(),
            }
        else:
            logger.warning("Not enough data for productivity pattern analysis")
            return {"optimal_windows": [], "productivity_bottlenecks": [], "predictions": []}

    async def model_circadian_rhythm(
        self, user_id: str, energy_logs: List[Dict[str, Any]], user_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Model user's circadian rhythm for optimal task allocation.

        Args:
            user_id: User ID
            energy_logs: Energy level logs
            user_data: User data including sleep patterns

        Returns:
            Dictionary containing circadian rhythm analysis results
        """
        logger.info(f"Modeling circadian rhythm for user {user_id}")

        # Preprocess energy logs
        X = np.array(
            [[log["energy_level"], log["time_of_day"], log["day_of_week"]] for log in energy_logs]
        )

        # Make predictions
        predictions = self.circadian_rhythm.predict_energy_levels(X)
        optimal_times = self.circadian_rhythm.get_optimal_task_times(predictions)

        return {"energy_predictions": predictions.tolist(), "optimal_task_times": optimal_times}

    async def generate_productivity_insights(
        self,
        user_id: str,
        time_blocks: List[Dict[str, Any]],
        mental_health_logs: List[Dict[str, Any]],
        productivity_metrics: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Generate productivity insights using correlation system.

        Args:
            user_id: User ID
            time_blocks: Time block data
            mental_health_logs: Mental health log data
            productivity_metrics: Productivity metrics data

        Returns:
            Dictionary containing productivity insights
        """
        logger.info(f"Generating productivity insights for user {user_id}")

        # Combine features
        X = np.array(
            [
                [
                    block["productivity_score"],
                    block["task_complexity"],
                    block["time_of_day"],
                    log["stress_level"],
                    log["sleep_quality"],
                    metric["focus_score"],
                    metric["distraction_count"],
                ]
                for block, log, metric in zip(time_blocks, mental_health_logs, productivity_metrics)
            ]
        )

        # Analyze correlations
        correlations = self.correlation_system.analyze_correlations(X)
        feature_importance = self.correlation_system.get_feature_importance(X)

        return {"correlations": correlations, "feature_importance": feature_importance}

    async def run_federated_analysis(
        self,
        user_id: str,
        mental_health_data: Dict[str, Any],
        anonymize: bool = True,
        include_sensitive: bool = False,
    ) -> Dict[str, Any]:
        """Run federated analysis on mental health data.

        Args:
            user_id: User ID
            mental_health_data: Mental health data
            anonymize: Whether to anonymize the data
            include_sensitive: Whether to include sensitive data

        Returns:
            Dictionary containing federated analysis results
        """
        logger.info(f"Running federated analysis for user {user_id}")

        # Prepare data
        X = np.array(
            [
                [
                    data["stress_level"],
                    data["anxiety_score"],
                    data["sleep_quality"],
                    data["mood_score"],
                    data["energy_level"],
                    data["focus_score"],
                    data["social_interaction"],
                    data["physical_activity"],
                ]
                for data in mental_health_data["logs"]
            ]
        )

        # Get insights
        insights = self.federated_model.predict_mental_health_insights(X)

        return {
            "insights": insights,
            "privacy_metrics": {
                "noise_multiplier": self.federated_model.dp_noise_multiplier,
                "l2_norm_clip": self.federated_model.dp_l2_norm_clip,
            },
        }

    async def generate_comprehensive_insights(
        self,
        user_id: str,
        time_blocks: List[Dict[str, Any]],
        mental_health_logs: List[Dict[str, Any]],
        energy_logs: List[Dict[str, Any]],
        productivity_metrics: List[Dict[str, Any]],
        user_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Generate comprehensive insights combining all models.

        Args:
            user_id: User ID
            time_blocks: Time block data
            mental_health_logs: Mental health log data
            energy_logs: Energy level logs
            productivity_metrics: Productivity metrics
            user_data: User data

        Returns:
            Dictionary containing comprehensive insights
        """
        logger.info(f"Generating comprehensive insights for user {user_id}")

        # Run all analyses in parallel
        productivity_results = await self.analyze_productivity_patterns(
            user_id, time_blocks, mental_health_logs
        )
        circadian_results = await self.model_circadian_rhythm(user_id, energy_logs, user_data)
        correlation_results = await self.generate_productivity_insights(
            user_id, time_blocks, mental_health_logs, productivity_metrics
        )
        federated_results = await self.run_federated_analysis(user_id, {"logs": mental_health_logs})

        return {
            "productivity_analysis": productivity_results,
            "circadian_analysis": circadian_results,
            "correlation_analysis": correlation_results,
            "federated_analysis": federated_results,
        }
