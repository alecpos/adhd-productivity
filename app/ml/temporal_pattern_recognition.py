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
import tensorflow as tf

from app.ml.models import (
    ProductivityPatternLSTM,
    CircadianRhythmModel,
    EnergyOptimizer,
    ProductivityCorrelationSystem,
    EnsembleLearnerModel,
    MentalHealthFederatedModel,
    PrivacyBudget
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
        
        # Initialize component models
        # 1. Productivity Pattern LSTM
        if productivity_pattern_model_path and os.path.exists(productivity_pattern_model_path):
            self.productivity_pattern = self._load_model(
                ProductivityPatternLSTM, productivity_pattern_model_path
            )
            logger.info(f"Loaded productivity pattern model from {productivity_pattern_model_path}")
        else:
            self.productivity_pattern = ProductivityPatternLSTM()
            logger.info("Initialized new productivity pattern model")
            
        # 2. Circadian Rhythm Model
        if circadian_rhythm_model_path and os.path.exists(circadian_rhythm_model_path):
            self.circadian_rhythm = self._load_model(
                CircadianRhythmModel, circadian_rhythm_model_path
            )
            logger.info(f"Loaded circadian rhythm model from {circadian_rhythm_model_path}")
        else:
            self.circadian_rhythm = CircadianRhythmModel()
            logger.info("Initialized new circadian rhythm model")
            
        # 3. Productivity Correlation System
        if correlation_system_path and os.path.exists(correlation_system_path):
            self.correlation_system = self._load_model(
                ProductivityCorrelationSystem, correlation_system_path
            )
            logger.info(f"Loaded correlation system from {correlation_system_path}")
        else:
            self.correlation_system = ProductivityCorrelationSystem()
            logger.info("Initialized new correlation system")
            
        # 4. Federated Learning for Mental Health
        if federated_model_path and os.path.exists(federated_model_path):
            self.federated_model = self._load_model(
                MentalHealthFederatedModel, federated_model_path
            )
            logger.info(f"Loaded federated model from {federated_model_path}")
        else:
            self.federated_model = MentalHealthFederatedModel(
                input_dim=10,
                dp_noise_multiplier=0.1,
                dp_l2_norm_clip=1.0
            )
            logger.info("Initialized new federated model")
        
        self.energy_optimizer = EnergyOptimizer(db)
        self.ensemble_learner = EnsembleLearnerModel()
        self.privacy_budget = PrivacyBudget()
        
        logger.info("Temporal Pattern Recognition Service initialized")
    
    async def analyze_productivity_patterns(
        self,
        user_id: str,
        time_blocks: List[Dict[str, Any]],
        mental_health_logs: List[Dict[str, Any]],
        days_to_predict: int = 7
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
            
            # Analyze flexible blocks
            flexible_indices = [i for i, block in enumerate(time_blocks) if block.get('is_flexible', False)]
            flexible_recommendations = self.productivity_pattern.analyze_flexible_blocks(
                flexible_indices, predictions
            )
            
            return {
                "optimal_windows": optimal_windows,
                "productivity_bottlenecks": bottlenecks,
                "flexible_block_recommendations": flexible_recommendations,
                "predictions": {k: v.tolist() for k, v in predictions.items()}
            }
        else:
            logger.warning("Not enough data for productivity pattern analysis")
            return {
                "optimal_windows": [],
                "productivity_bottlenecks": [],
                "flexible_block_recommendations": [],
                "predictions": {}
            }
    
    async def model_circadian_rhythm(
        self,
        user_id: str,
        energy_logs: List[Dict[str, Any]],
        user_data: Dict[str, Any]
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
        
        # Train or update circadian rhythm model
        training_result = self.circadian_rhythm.train(energy_logs, user_data)
        
        # Generate daily energy curve predictions
        energy_curve = self.circadian_rhythm.predict_daily_curve(user_data)
        
        return {
            "energy_curve": energy_curve,
            "training_metrics": training_result,
            "rhythm_features": {
                "peak_times": [
                    time.strftime("%H:%M") for time, level in energy_curve["hourly_predictions"]
                    if level > 7.0  # High energy threshold
                ],
                "low_times": [
                    time.strftime("%H:%M") for time, level in energy_curve["hourly_predictions"]
                    if level < 4.0  # Low energy threshold
                ]
            }
        }
    
    async def optimize_schedule_with_energy(
        self,
        user_id: str,
        tasks: List[Dict[str, Any]],
        energy_pattern: Optional[EnergySchedulingPattern] = None,
        user_data: Optional[Dict[str, Any]] = None,
        work_hours: Optional[WorkHours] = None
    ) -> List[Dict[str, Any]]:
        """Optimize schedule based on circadian rhythm and energy levels.
        
        Args:
            user_id: User ID
            tasks: Tasks to schedule
            energy_pattern: Energy scheduling pattern
            user_data: User data
            work_hours: Work hours constraints
            
        Returns:
            Optimized schedule as list of time blocks
        """
        logger.info(f"Optimizing schedule with energy data for user {user_id}")
        
        # If no energy pattern provided, generate from circadian model
        if not energy_pattern and user_data:
            energy_curve = self.circadian_rhythm.predict_daily_curve(user_data)
            energy_pattern = EnergySchedulingPattern(
                hourly_energy_levels={
                    int(time.split(":")[0]): level 
                    for time, level in energy_curve["hourly_predictions"]
                }
            )
        
        # Use energy optimizer to create optimized schedule
        optimized_schedule = self.energy_optimizer.optimize_schedule(
            tasks, energy_pattern, user_data, work_hours
        )
        
        return optimized_schedule
    
    async def generate_productivity_insights(
        self,
        user_id: str,
        time_blocks: List[Dict[str, Any]],
        mental_health_logs: List[Dict[str, Any]],
        productivity_metrics: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate productivity insights using the correlation system.
        
        Args:
            user_id: User ID
            time_blocks: Time block data
            mental_health_logs: Mental health log data
            productivity_metrics: Productivity metric data
            
        Returns:
            Dictionary containing productivity insights
        """
        logger.info(f"Generating productivity insights for user {user_id}")
        
        # Train correlation system
        training_result = self.correlation_system.train(
            time_blocks, mental_health_logs, productivity_metrics
        )
        
        # Get correlation insights
        correlation_insights = self.correlation_system.get_correlation_insights()
        
        # Get visualizations
        correlation_viz = self.correlation_system.visualize_correlations()
        pattern_viz = self.correlation_system.visualize_patterns()
        
        # Generate user-specific recommendations
        current_features = {
            "energy_level": sum(block.get("energy_level", 5) for block in time_blocks[-5:]) / 5 
            if time_blocks else 5,
            "focus_level": sum(block.get("focus_level", 5) for block in time_blocks[-5:]) / 5 
            if time_blocks else 5,
            "stress_level": sum(log.get("stress_level", 5) for log in mental_health_logs[-5:]) / 5 
            if mental_health_logs else 5,
            "sleep_quality": sum(log.get("sleep_quality", 5) for log in mental_health_logs[-5:]) / 5 
            if mental_health_logs else 5,
            "sleep_hours": sum(log.get("sleep_hours", 7) for log in mental_health_logs[-5:]) / 5 
            if mental_health_logs else 7,
        }
        
        productivity_insights = self.correlation_system.get_productivity_insights(current_features)
        
        return {
            "correlation_insights": correlation_insights,
            "productivity_insights": productivity_insights,
            "visualizations": {
                "correlations": correlation_viz,
                "patterns": pattern_viz
            },
            "training_metrics": training_result
        }
    
    async def run_federated_analysis(
        self,
        user_id: str,
        mental_health_data: Dict[str, Any],
        anonymize: bool = True,
        include_sensitive: bool = False
    ) -> Dict[str, Any]:
        """Run federated learning analysis on mental health data.
        
        This method performs privacy-preserving analysis on mental health data
        using federated learning techniques.
        
        Args:
            user_id: User identifier
            mental_health_data: Dictionary of mental health metrics and logs
            anonymize: Whether to anonymize the user ID
            include_sensitive: Whether to include sensitive information
            
        Returns:
            Dictionary with federated learning insights
        """
        logger.info(f"Running federated analysis for user {user_id}")
        
        # Anonymize user ID if requested
        client_id = user_id
        if anonymize:
            client_id = self.federated_model.anonymize_client_id(user_id)
            logger.info(f"Anonymized user ID for federated analysis")
        
        # Preprocess mental health data
        try:
            preprocessed_data = self.federated_model.preprocess_mental_health_data(
                mental_health_data,
                include_sensitive=include_sensitive
            )
            logger.info(f"Preprocessed mental health data for federated analysis")
        except Exception as e:
            logger.error(f"Error preprocessing mental health data: {str(e)}")
            return {"error": "Failed to preprocess mental health data", "details": str(e)}
        
        # Check if we can execute federated query within privacy budget
        privacy_check = self.federated_model.privacy_budget.check_query(
            epsilon=0.1,
            delta=1e-5,
            query_description=f"Federated analysis for user {client_id}"
        )
        
        if not privacy_check:
            logger.warning(f"Privacy budget exceeded for user {client_id}")
            return {
                "status": "privacy_limited",
                "message": "Analysis limited due to privacy budget constraints",
                "insights": {}
            }
        
        # Run federated analysis
        try:
            # Simulate federated analysis
            analysis_results = self.federated_model.run_federated_analysis(
                client_id=client_id,
                client_data=preprocessed_data
            )
            
            # Process results
            insights = self._process_federated_results(analysis_results)
            logger.info(f"Completed federated analysis for user {client_id}")
            
            return {
                "status": "success",
                "client_id": client_id,
                "is_anonymized": anonymize,
                "insights": insights
            }
            
        except Exception as e:
            logger.error(f"Error in federated analysis: {str(e)}")
            return {"error": "Failed to complete federated analysis", "details": str(e)}
    
    def _process_federated_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Process raw federated learning results into useful insights.
        
        Args:
            results: Raw results from federated analysis
            
        Returns:
            Processed insights from federated analysis
        """
        insights = {}
        
        # Extract mental health correlations
        if "correlations" in results:
            insights["correlations"] = {
                k: round(float(v), 2) for k, v in results["correlations"].items()
            }
        
        # Extract risk assessments
        if "risk_factors" in results:
            insights["risk_factors"] = results["risk_factors"]
        
        # Extract recommendations
        if "recommendations" in results:
            insights["recommendations"] = results["recommendations"]
        
        # Add federated statistics
        if "participant_stats" in results:
            insights["federated_stats"] = {
                "participant_count": results["participant_stats"].get("count", 0),
                "privacy_guarantee": results["participant_stats"].get("privacy_level", "medium"),
                "confidence": results["participant_stats"].get("confidence", 0.7),
            }
        
        return insights
    
    async def generate_comprehensive_insights(
        self,
        user_id: str,
        time_blocks: List[Dict[str, Any]],
        mental_health_logs: List[Dict[str, Any]],
        energy_logs: List[Dict[str, Any]],
        productivity_metrics: List[Dict[str, Any]],
        user_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate comprehensive insights using all EPIC-1 models.
        
        Args:
            user_id: User ID
            time_blocks: Time block data
            mental_health_logs: Mental health log data
            energy_logs: Energy log data
            productivity_metrics: Productivity metric data
            user_data: User data including sleep patterns
            
        Returns:
            Dictionary containing comprehensive insights from all models
        """
        logger.info(f"Generating comprehensive insights for user {user_id}")
        
        # Run all analysis components in parallel
        import asyncio
        productivity_patterns_task = asyncio.create_task(
            self.analyze_productivity_patterns(user_id, time_blocks, mental_health_logs)
        )
        
        circadian_rhythm_task = asyncio.create_task(
            self.model_circadian_rhythm(user_id, energy_logs, user_data)
        )
        
        productivity_insights_task = asyncio.create_task(
            self.generate_productivity_insights(
                user_id, time_blocks, mental_health_logs, productivity_metrics
            )
        )
        
        # For federated analysis, we need to prepare mental health data
        mh_data = {
            "mood_scores": [log.get("mood_score", 5) for log in mental_health_logs if "mood_score" in log],
            "stress_levels": [log.get("stress_level", 5) for log in mental_health_logs if "stress_level" in log],
            "sleep_quality": [log.get("sleep_quality", 5) for log in mental_health_logs if "sleep_quality" in log],
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id
        }
        
        federated_analysis_task = asyncio.create_task(
            self.run_federated_analysis(user_id, mh_data)
        )
        
        # Gather all results
        productivity_patterns = await productivity_patterns_task
        circadian_rhythm = await circadian_rhythm_task
        productivity_insights = await productivity_insights_task
        federated_analysis = await federated_analysis_task
        
        # Combine all insights
        combined_insights = {
            "productivity_patterns": productivity_patterns,
            "circadian_rhythm": circadian_rhythm,
            "productivity_insights": productivity_insights,
            "federated_analysis": federated_analysis,
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id
        }
        
        # Generate task scheduling recommendations
        tasks_to_schedule = [
            {
                "id": f"task_{i}",
                "title": block.get("title", "Untitled Task"),
                "description": block.get("description", ""),
                "duration": block.get("duration", 60),  # minutes
                "energy_required": block.get("energy_level", 5),
                "focus_required": block.get("focus_level", 5),
                "priority": self._convert_priority_to_numeric(block.get("priority", "medium")),
                "deadline": block.get("deadline", None),
                "is_flexible": block.get("is_flexible", True)
            }
            for i, block in enumerate(time_blocks[-10:]) if block.get("block_type") == "task"
        ]
        
        # Create energy pattern from circadian rhythm
        hourly_values = {
            int(time.split(":")[0]): level 
            for time, level in circadian_rhythm["energy_curve"]["hourly_predictions"]
        }
        
        # Calculate average energy level from the hourly predictions or use default
        avg_energy = round(sum(hourly_values.values()) / len(hourly_values)) if hourly_values else 5
        
        # Calculate peak and trough hours based on energy levels
        peak_hours = [hour for hour, level in hourly_values.items() if level >= 7]
        trough_hours = [hour for hour, level in hourly_values.items() if level <= 4]
        
        energy_pattern = EnergySchedulingPattern(
            hourly_energy_levels=hourly_values,
            time_of_day=time(9, 0),  # Default to 9:00 AM
            average_energy=avg_energy, 
            average_focus=avg_energy,  # Use same value for focus as energy for simplicity
            peak_hours=peak_hours,
            trough_hours=trough_hours
        )
        
        # Get work hours from user data
        work_hours = WorkHours(
            start_time=time(user_data.get("work_start_hour", 9), 0),  # 9:00 AM default
            end_time=time(user_data.get("work_end_hour", 17), 0)  # 5:00 PM default
        )
        
        # Optimize schedule with energy data
        optimized_schedule = await self.optimize_schedule_with_energy(
            user_id, tasks_to_schedule, energy_pattern, user_data, work_hours
        )
        
        combined_insights["schedule_recommendations"] = optimized_schedule
        
        return combined_insights
    
    async def save_models(self, base_path: str = "app/ml/saved_models/") -> Dict[str, str]:
        """Save all models to disk.
        
        Args:
            base_path: Base path to save models
            
        Returns:
            Dictionary mapping model names to save paths
        """
        import os
        os.makedirs(base_path, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        paths = {}
        
        # Save productivity pattern LSTM
        pp_path = os.path.join(base_path, f"productivity_pattern_{timestamp}.h5")
        self.productivity_pattern.save(pp_path)
        paths["productivity_pattern"] = pp_path
        
        # Save circadian rhythm model
        cr_path = os.path.join(base_path, f"circadian_rhythm_{timestamp}.h5")
        self.circadian_rhythm.save(cr_path)
        paths["circadian_rhythm"] = cr_path
        
        # Save correlation system
        cs_path = os.path.join(base_path, f"correlation_system_{timestamp}.pkl")
        self.correlation_system.save(cs_path)
        paths["correlation_system"] = cs_path
        
        # Save federated model
        fm_path = os.path.join(base_path, f"federated_model_{timestamp}.h5")
        self.federated_model.save(fm_path)
        paths["federated_model"] = fm_path
        
        logger.info(f"All models saved to {base_path}")
        return paths 

    def _convert_priority_to_numeric(self, priority_str: str) -> int:
        """Convert priority string to numeric value.
        
        Args:
            priority_str: Priority as string ('high', 'medium', 'low')
            
        Returns:
            int: Numeric priority (3 for high, 2 for medium, 1 for low)
        """
        priority_map = {
            "high": 3,
            "medium": 2,
            "low": 1
        }
        return priority_map.get(priority_str.lower(), 2)  # Default to medium (2) if not recognized 

    async def optimize_schedule_with_circadian_dqn(
        self,
        user_id: str,
        tasks: List[Dict[str, Any]],
        user_data: Dict[str, Any],
        current_state: Optional[np.ndarray] = None,
        model_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Optimize schedule using circadian-aware DQN model from ADHD-18.
        
        This method implements the ADHD-18 story: CircadianDQN-based schedule
        optimization that integrates circadian rhythm awareness.
        
        Args:
            user_id: User ID
            tasks: List of tasks to schedule
            user_data: User data including sleep patterns and preferences
            current_state: Current state if continuing a session
            model_path: Path to a saved CircadianDQN model
            
        Returns:
            Optimized schedule with circadian rhythm considerations
        """
        logger.info(f"Optimizing schedule with circadian DQN for user {user_id}")
        
        # Create or load CircadianDQN model
        from app.ml.models.model_factory_model import ModelFactory
        
        # Get or create circadian rhythm model path
        circadian_model_path = None
        if self.circadian_rhythm.trained:
            # Use temporary path to save the model
            import tempfile
            import os
            
            temp_dir = tempfile.gettempdir()
            circadian_model_path = os.path.join(temp_dir, f"circadian_model_{user_id}")
            self.circadian_rhythm.save(circadian_model_path)
        
        # Create or load CircadianDQN model
        if model_path and os.path.exists(f"{model_path}_main.h5"):
            from app.ml.models.adhd17_reinforcement_model import CircadianDQNModel
            dqn_model = CircadianDQNModel.load(model_path)
            logger.info(f"Loaded CircadianDQN model from {model_path}")
        else:
            dqn_model = ModelFactory.create_circadian_dqn(
                circadian_model_path=circadian_model_path
            )
            logger.info("Created new CircadianDQN model")
        
        # Process tasks to include cognitive demand profiles
        from app.ml.models.adhd17_reinforcement_model import TaskCognitiveProfile
        
        processed_tasks = []
        for task in tasks:
            # Categorize task by cognitive demand
            cognitive_category = TaskCognitiveProfile.categorize_task(task)
            
            # Add category to task data
            task_with_category = task.copy()
            task_with_category['cognitive_category'] = cognitive_category
            
            # Get optimal energy requirements
            task_with_category['optimal_energy'] = TaskCognitiveProfile.get_energy_requirements(cognitive_category)
            
            processed_tasks.append(task_with_category)
        
        # Generate schedule options with temporal suitability scores
        schedule_options = []
        
        # Get current timestamp or use provided
        current_timestamp = datetime.now()
        
        # Get hourly energy predictions for the day
        daily_energy_curve = {}
        if self.circadian_rhythm.trained:
            try:
                prediction_result = self.circadian_rhythm.predict_daily_curve(
                    user_data=user_data,
                    resolution_minutes=30
                )
                
                for point in prediction_result.get('curve_data', []):
                    hour = point.get('hour')
                    if hour is not None:
                        daily_energy_curve[hour] = point.get('energy_level', 5.0)
            except Exception as e:
                logger.error(f"Error predicting energy curve: {str(e)}")
                # Use default curve if prediction fails
                for hour in range(24):
                    # Simple default curve
                    if 8 <= hour < 12:  # Morning peak
                        daily_energy_curve[hour] = 7.5
                    elif 14 <= hour < 17:  # Afternoon peak
                        daily_energy_curve[hour] = 6.5
                    elif 20 <= hour < 23:  # Evening decline
                        daily_energy_curve[hour] = 4.0
                    else:  # Early morning/late night
                        daily_energy_curve[hour] = 3.0
        else:
            # Use default curve if model not trained
            for hour in range(24):
                # Simple default curve
                if 8 <= hour < 12:  # Morning peak
                    daily_energy_curve[hour] = 7.5
                elif 14 <= hour < 17:  # Afternoon peak
                    daily_energy_curve[hour] = 6.5
                elif 20 <= hour < 23:  # Evening decline
                    daily_energy_curve[hour] = 4.0
                else:  # Early morning/late night
                    daily_energy_curve[hour] = 3.0
        
        # For each task, calculate temporal suitability for each hour
        for task in processed_tasks:
            task_category = task.get('cognitive_category')
            task_suitability = {}
            
            # Calculate suitability score for each hour
            for hour in range(24):
                # Get energy level for this hour
                energy_level = daily_energy_curve.get(hour, 5.0)
                
                # Calculate temporal suitability
                suitability = TaskCognitiveProfile.calculate_temporal_suitability(
                    task_category=task_category,
                    current_energy=energy_level,
                    current_hour=hour,
                    user_circadian_profile=user_data.get('circadian_profile', {})
                )
                
                task_suitability[hour] = suitability
            
            # Add suitability scores to task
            task_with_suitability = task.copy()
            task_with_suitability['hourly_suitability'] = task_suitability
            
            # Find optimal hours (top 3)
            optimal_hours = sorted(
                task_suitability.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:3]
            
            task_with_suitability['optimal_hours'] = [
                {'hour': h, 'suitability': s} 
                for h, s in optimal_hours
            ]
            
            schedule_options.append(task_with_suitability)
        
        # TODO: In a full implementation, we would use the DQN model to
        # find the optimal schedule by:
        # 1. Converting tasks to state representations
        # 2. Using the model to select optimal actions (task ordering/timing)
        # 3. Evaluating the schedule with the reward function
        
        # For now, use a simple greedy algorithm based on suitability scores
        from collections import defaultdict
        
        # Initialize schedule with empty slots
        hourly_schedule = defaultdict(list)
        
        # Sort tasks by priority (if available) then by flexibility (less flexible first)
        sorted_tasks = sorted(
            schedule_options,
            key=lambda t: (
                -float(t.get('priority', 5)),
                t.get('is_flexible', True)
            )
        )
        
        # Place tasks in their optimal hours if available
        for task in sorted_tasks:
            task_duration = task.get('estimated_duration', 60) / 60.0  # Convert to hours
            optimal_hours = task.get('optimal_hours', [])
            
            # Try to place task in one of its optimal hours
            placed = False
            
            for hour_info in optimal_hours:
                hour = hour_info.get('hour')
                
                # Check if hour is within work hours (default 8am-6pm)
                if not (8 <= hour < 18):
                    continue
                    
                # Check if the slot is available
                if len(hourly_schedule[hour]) < 1:  # Assuming max 1 task per hour for simplicity
                    hourly_schedule[hour].append(task)
                    placed = True
                    break
            
            # If couldn't place in optimal hours, find any available slot
            if not placed:
                for hour in range(8, 18):  # Default work hours
                    if len(hourly_schedule[hour]) < 1:
                        hourly_schedule[hour].append(task)
                        placed = True
                        break
        
        # Convert hourly schedule to list format
        final_schedule = []
        for hour, tasks in sorted(hourly_schedule.items()):
            for task in tasks:
                # Create a datetime for this hour
                task_time = current_timestamp.replace(
                    hour=int(hour),
                    minute=0,
                    second=0,
                    microsecond=0
                )
                
                duration_minutes = task.get('estimated_duration', 60)
                
                schedule_item = {
                    'task_id': task.get('id', ''),
                    'title': task.get('title', ''),
                    'description': task.get('description', ''),
                    'start_time': task_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'duration_minutes': duration_minutes,
                    'end_time': (task_time + timedelta(minutes=duration_minutes)).strftime('%Y-%m-%d %H:%M:%S'),
                    'cognitive_category': task.get('cognitive_category', ''),
                    'energy_level': daily_energy_curve.get(hour, 5.0),
                    'suitability_score': task.get('hourly_suitability', {}).get(hour, 0.5),
                    'priority': task.get('priority', 5)
                }
                
                final_schedule.append(schedule_item)
        
        # Sort by start time
        final_schedule = sorted(
            final_schedule,
            key=lambda x: x.get('start_time', '')
        )
        
        # Save model for future use
        if not model_path:
            import tempfile
            import os
            
            temp_dir = tempfile.gettempdir()
            model_path = os.path.join(temp_dir, f"circadian_dqn_{user_id}")
            
        try:
            dqn_model.save(model_path)
            logger.info(f"Saved CircadianDQN model to {model_path}")
        except Exception as e:
            logger.error(f"Error saving CircadianDQN model: {str(e)}")
        
        # Return the optimized schedule
        return {
            "schedule": final_schedule,
            "energy_curve": daily_energy_curve,
            "model_path": model_path
        } 

    def _load_model(self, model_class, model_path):
        """Helper method to load a model from disk.
        
        Args:
            model_class: The class of the model to load
            model_path: Path to the saved model
            
        Returns:
            An instance of the model loaded from disk
        """
        try:
            if hasattr(model_class, 'load'):
                return model_class.load(model_path)
            else:
                logger.warning(f"Model class {model_class.__name__} does not have a load method")
                return model_class()
        except Exception as e:
            logger.error(f"Error loading model from {model_path}: {str(e)}")
            return model_class() 