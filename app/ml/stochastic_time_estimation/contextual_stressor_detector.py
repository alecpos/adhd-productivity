"""
Contextual Stressor Detection from Wearable Data (STORY-7)

This module implements a system to detect contextual stressors from HealthModel and wearable data
that may impact task performance and duration estimation. It integrates with the Bayesian duration
prediction network to adjust time estimates based on detected stress levels.

Key components:
1. Wearable data processing (heart rate, HRV, etc.)
2. Environmental stressor detection
3. Stress level classification
4. Dynamic duration adjustment based on stress
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any, Union
from datetime import datetime, timedelta
import logging
import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
from enum import Enum
import math

from app.models.health_model import HealthMetrics
from app.models.user_model import UserModel
from app.models.task_model import TaskModel
from app.ml.models import BaseMLModel

logger = logging.getLogger(__name__)


class StressLevel(Enum):
    """Stress level classification."""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    EXTREME = "extreme"


class StressorType(Enum):
    """Types of detected stressors."""
    PHYSIOLOGICAL = "physiological"  # Heart rate, HRV, etc.
    ENVIRONMENTAL = "environmental"  # Noise, temperature, etc.
    COGNITIVE = "cognitive"  # Mental fatigue, focus, etc.
    EMOTIONAL = "emotional"  # Mood, anxiety, etc.
    SOCIAL = "social"  # Meetings, social pressure, etc.


class ContextualStressorDetector(BaseMLModel):
    """
    System to detect contextual stressors from HealthModel and wearable data.
    
    This model analyzes health metrics and environmental data to:
    - Detect and classify stressors
    - Estimate overall stress levels
    - Provide duration adjustment factors based on stress
    - Track stress patterns over time
    
    It integrates with the BayesianDurationPredictor to improve time estimates.
    """
    
    def __init__(
        self,
        db: Optional[AsyncSession] = None,
        model_path: Optional[str] = None,
        stress_threshold_hr: Optional[Dict[str, float]] = None,
        stress_threshold_hrv: Optional[Dict[str, float]] = None,
        stress_impact_weights: Optional[Dict[StressorType, float]] = None,
        lookback_period: int = 24  # hours
    ):
        """
        Initialize the Contextual Stressor Detector.
        
        Args:
            db: Database session for retrieving health data
            model_path: Path to saved model parameters
            stress_threshold_hr: Heart rate thresholds for stress levels
            stress_threshold_hrv: HRV thresholds for stress levels
            stress_impact_weights: Weights for different stressor types
            lookback_period: How far back to look for stressors, in hours
        """
        super().__init__(model_path=model_path)
        self.db = db
        self.lookback_period = lookback_period
        
        # Default heart rate thresholds (percentages above resting)
        self.stress_threshold_hr = stress_threshold_hr or {
            StressLevel.LOW.value: 0.1,      # 10% above resting
            StressLevel.MODERATE.value: 0.2,  # 20% above resting
            StressLevel.HIGH.value: 0.3,      # 30% above resting
            StressLevel.EXTREME.value: 0.4    # 40% above resting
        }
        
        # Default HRV thresholds (percentages below baseline)
        self.stress_threshold_hrv = stress_threshold_hrv or {
            StressLevel.LOW.value: 0.1,      # 10% below baseline
            StressLevel.MODERATE.value: 0.2,  # 20% below baseline
            StressLevel.HIGH.value: 0.3,      # 30% below baseline
            StressLevel.EXTREME.value: 0.4    # 40% below baseline
        }
        
        # Default stressor type weights
        self.stress_impact_weights = stress_impact_weights or {
            StressorType.PHYSIOLOGICAL.value: 0.3,
            StressorType.ENVIRONMENTAL.value: 0.2,
            StressorType.COGNITIVE.value: 0.2,
            StressorType.EMOTIONAL.value: 0.2,
            StressorType.SOCIAL.value: 0.1
        }
        
        # Environmental thresholds
        self.env_thresholds = {
            "noise_level": {  # in dB
                StressLevel.LOW.value: 60,
                StressLevel.MODERATE.value: 70,
                StressLevel.HIGH.value: 80,
                StressLevel.EXTREME.value: 90
            },
            "temperature": {  # Deviation from comfort zone (20-24°C) in °C
                StressLevel.LOW.value: 2,
                StressLevel.MODERATE.value: 4,
                StressLevel.HIGH.value: 6,
                StressLevel.EXTREME.value: 8
            }
        }
    
    async def detect_current_stress(self, user_id: str) -> Dict[str, Any]:
        """
        Detect current stress levels based on recent health metrics.
        
        Args:
            user_id: ID of the user to analyze
            
        Returns:
            Dictionary with stress analysis including:
            - overall_stress_level: Overall stress level (LOW, MODERATE, HIGH, EXTREME)
            - stress_score: Numerical stress score (0-100)
            - detected_stressors: List of detected stressors and their levels
            - time_impact_factor: Factor to adjust time estimation
            - trend: Trend in stress levels (increasing, decreasing, stable)
        """
        if self.db is None:
            return {
                "error": "No database connection available"
            }
        
        # Get user's resting heart rate as baseline
        user = await self._get_user(user_id)
        if user is None:
            return {
                "error": f"User {user_id} not found"
            }
        
        # Get recent health metrics
        metrics = await self._get_recent_health_metrics(user_id)
        if not metrics:
            return {
                "error": "No recent health metrics available",
                "overall_stress_level": StressLevel.LOW.value,
                "stress_score": 0,
                "detected_stressors": [],
                "time_impact_factor": 1.0,
                "trend": "stable"
            }
        
        # Extract heart rate data
        hr_data = [m for m in metrics if hasattr(m, 'heart_rate') and m.heart_rate is not None]
        
        # Determine resting heart rate (use the lowest 10th percentile from metrics or user default)
        resting_hr = user.resting_heart_rate if hasattr(user, 'resting_heart_rate') and user.resting_heart_rate else 65
        if hr_data:
            hr_values = [m.heart_rate for m in hr_data]
            if hr_values:
                resting_hr = np.percentile(hr_values, 10)
        
        # Process metrics to detect stressors
        stressors = []
        
        # Analyze physiological stressors (heart rate, HRV)
        physiological_stress = self._analyze_physiological_stress(metrics, resting_hr)
        if physiological_stress:
            stressors.append(physiological_stress)
        
        # Analyze environmental stressors
        environmental_stress = self._analyze_environmental_stress(metrics)
        if environmental_stress:
            stressors.append(environmental_stress)
        
        # Analyze cognitive stressors
        cognitive_stress = self._analyze_cognitive_stress(metrics)
        if cognitive_stress:
            stressors.append(cognitive_stress)
        
        # Analyze emotional stressors
        emotional_stress = self._analyze_emotional_stress(metrics)
        if emotional_stress:
            stressors.append(emotional_stress)
        
        # Analyze social stressors
        social_stress = self._analyze_social_stress(metrics, user_id)
        if social_stress:
            stressors.append(social_stress)
        
        # Calculate overall stress score and level
        stress_score, stress_level = self._calculate_overall_stress(stressors)
        
        # Calculate time impact factor
        time_impact_factor = self._calculate_stress_time_impact(stress_score)
        
        # Determine stress trend
        trend = await self._determine_stress_trend(user_id, stress_score)
        
        return {
            "user_id": user_id,
            "overall_stress_level": stress_level,
            "stress_score": stress_score,
            "detected_stressors": stressors,
            "time_impact_factor": time_impact_factor,
            "trend": trend,
            "analysis_timestamp": datetime.now().isoformat()
        }
    
    async def get_task_stress_adjustment(self, task_id: str) -> float:
        """
        Get stress-based time adjustment factor for a specific task.
        
        This is a simplified interface for the Bayesian predictor to use.
        
        Args:
            task_id: ID of the task
            
        Returns:
            Time adjustment factor (usually in range 1.0-2.0)
        """
        # Get the task to find user ID
        task = await self._get_task(task_id)
        if task is None:
            return 1.0  # Default: no adjustment
            
        # Handle dictionary and object access patterns for task
        # Support both object attribute access and dictionary key access
        try:
            user_id = task.user_id if hasattr(task, 'user_id') else task.get('user_id', None)
            if not user_id:
                return 1.0  # Default: no adjustment
                
            # Detect current stress for the user
            stress_analysis = await self.detect_current_stress(user_id)
            if "error" in stress_analysis:
                return 1.0  # Default: no adjustment
            
            # Consider task priority and stress level
            adjustment = stress_analysis.get("time_impact_factor", 1.0)
            
            # Adjust factor based on task difficulty and stress sensitivity
            task_difficulty = 3  # Default to medium difficulty
            if hasattr(task, 'difficulty') and task.difficulty is not None:
                task_difficulty = task.difficulty
            elif isinstance(task, dict) and 'difficulty' in task:
                task_difficulty = task['difficulty']
                
            stress_sensitivity = self._calculate_task_stress_sensitivity(task)
            
            # Higher difficulty with higher stress means even greater impact
            final_adjustment = adjustment * (1 + (task_difficulty / 10) * stress_sensitivity)
            
            # Cap the adjustment to a reasonable range
            return max(1.0, min(final_adjustment, 2.0))
        except Exception as e:
            logger.error(f"Error calculating stress adjustment: {e}")
            return 1.0  # Default: no adjustment
    
    def _analyze_physiological_stress(
        self, 
        metrics: List[HealthMetrics], 
        resting_hr: float
    ) -> Dict[str, Any]:
        """
        Analyze physiological stress indicators (heart rate, HRV, etc.).
        
        Args:
            metrics: List of health metrics
            resting_hr: User's resting heart rate
            
        Returns:
            Dictionary with physiological stress analysis
        """
        # Extract relevant metrics
        hr_metrics = [m for m in metrics if hasattr(m, 'heart_rate') and m.heart_rate is not None]
        hrv_metrics = [m for m in metrics if hasattr(m, 'heart_rate_variability') and m.heart_rate_variability is not None]
        
        if not hr_metrics and not hrv_metrics:
            return None
        
        # Analyze heart rate
        hr_stress_level = StressLevel.LOW.value
        hr_stress_score = 0
        
        if hr_metrics:
            recent_hr = hr_metrics[-1].heart_rate
            hr_elevation = (recent_hr - resting_hr) / resting_hr if resting_hr > 0 else 0
            
            # Determine stress level from heart rate
            for level, threshold in sorted(
                self.stress_threshold_hr.items(), 
                key=lambda x: self.stress_level_to_numeric(x[0])
            ):
                if hr_elevation >= threshold:
                    hr_stress_level = level
            
            # Calculate heart rate stress score (0-100)
            hr_stress_score = min(100, int(hr_elevation * 100 / self.stress_threshold_hr[StressLevel.EXTREME.value]))
        
        # Analyze HRV
        hrv_stress_level = StressLevel.LOW.value
        hrv_stress_score = 0
        
        if hrv_metrics:
            # Calculate baseline HRV (higher values mean lower stress)
            baseline_hrv = np.percentile([m.heart_rate_variability for m in hrv_metrics], 90)
            recent_hrv = hrv_metrics[-1].heart_rate_variability
            hrv_reduction = (baseline_hrv - recent_hrv) / baseline_hrv if baseline_hrv > 0 else 0
            
            # Determine stress level from HRV
            for level, threshold in sorted(
                self.stress_threshold_hrv.items(), 
                key=lambda x: self.stress_level_to_numeric(x[0])
            ):
                if hrv_reduction >= threshold:
                    hrv_stress_level = level
            
            # Calculate HRV stress score (0-100)
            hrv_stress_score = min(100, int(hrv_reduction * 100 / self.stress_threshold_hrv[StressLevel.EXTREME.value]))
        
        # Combine heart rate and HRV indicators
        if hr_metrics and hrv_metrics:
            # Use the higher of the two stress levels
            combined_level = hr_stress_level if self.stress_level_to_numeric(hr_stress_level) > self.stress_level_to_numeric(hrv_stress_level) else hrv_stress_level
            combined_score = max(hr_stress_score, hrv_stress_score)
        elif hr_metrics:
            combined_level = hr_stress_level
            combined_score = hr_stress_score
        else:
            combined_level = hrv_stress_level
            combined_score = hrv_stress_score
        
        return {
            "stressor_type": StressorType.PHYSIOLOGICAL.value,
            "stress_level": combined_level,
            "stress_score": combined_score,
            "details": {
                "heart_rate": {
                    "value": hr_metrics[-1].heart_rate if hr_metrics else None,
                    "stress_level": hr_stress_level if hr_metrics else None
                },
                "hrv": {
                    "value": hrv_metrics[-1].heart_rate_variability if hrv_metrics else None,
                    "stress_level": hrv_stress_level if hrv_metrics else None
                }
            }
        }
    
    def _analyze_environmental_stress(self, metrics: List[HealthMetrics]) -> Dict[str, Any]:
        """
        Analyze environmental stress indicators (noise, temperature, etc.).
        
        Args:
            metrics: List of health metrics
            
        Returns:
            Dictionary with environmental stress analysis
        """
        # Extract metrics with environment data
        env_metrics = [m for m in metrics if hasattr(m, 'environment_data') and m.environment_data]
        
        if not env_metrics:
            return None
        
        # Extract latest environment data
        latest_env = env_metrics[-1].environment_data
        
        if not latest_env:
            return None
        
        stressors = []
        
        # Check noise level
        if 'noise_level' in latest_env:
            noise_level = latest_env['noise_level']
            noise_stress_level = StressLevel.LOW.value
            
            for level, threshold in sorted(
                self.env_thresholds['noise_level'].items(), 
                key=lambda x: self.stress_level_to_numeric(x[0])
            ):
                if noise_level >= threshold:
                    noise_stress_level = level
            
            stressors.append({
                "factor": "noise",
                "value": noise_level,
                "stress_level": noise_stress_level
            })
        
        # Check temperature
        if 'temperature' in latest_env:
            temp = latest_env['temperature']
            temp_stress_level = StressLevel.LOW.value
            
            # Calculate deviation from comfort zone (20-24°C)
            comfort_min, comfort_max = 20, 24
            temp_deviation = 0
            
            if temp < comfort_min:
                temp_deviation = comfort_min - temp
            elif temp > comfort_max:
                temp_deviation = temp - comfort_max
            
            for level, threshold in sorted(
                self.env_thresholds['temperature'].items(), 
                key=lambda x: self.stress_level_to_numeric(x[0])
            ):
                if temp_deviation >= threshold:
                    temp_stress_level = level
            
            stressors.append({
                "factor": "temperature",
                "value": temp,
                "deviation": temp_deviation,
                "stress_level": temp_stress_level
            })
        
        # If no specific environmental stressors found
        if not stressors:
            return None
        
        # Determine overall environmental stress level (take the highest)
        overall_level = max(stressors, key=lambda x: self.stress_level_to_numeric(x["stress_level"]))["stress_level"]
        
        # Calculate overall stress score
        overall_score = 0
        for stressor in stressors:
            factor_score = self.stress_level_to_numeric(stressor["stress_level"]) * 25  # 0-100 scale
            overall_score = max(overall_score, factor_score)
        
        return {
            "stressor_type": StressorType.ENVIRONMENTAL.value,
            "stress_level": overall_level,
            "stress_score": overall_score,
            "details": stressors
        }
    
    def _analyze_cognitive_stress(self, metrics: List[HealthMetrics]) -> Dict[str, Any]:
        """
        Analyze cognitive stress indicators (focus level, mental fatigue, etc.).
        
        Args:
            metrics: List of health metrics
            
        Returns:
            Dictionary with cognitive stress analysis
        """
        # Extract relevant metrics
        focus_metrics = [m for m in metrics if hasattr(m, 'focus_level') and m.focus_level is not None]
        
        if not focus_metrics:
            return None
        
        # Calculate focus/fatigue based stress
        recent_focus = focus_metrics[-1].focus_level
        
        # Focus level is usually 1-10, where higher is better
        # Convert to stress level (low focus = high stress)
        if recent_focus >= 8:  # 8-10
            focus_stress_level = StressLevel.LOW.value
        elif recent_focus >= 6:  # 6-7
            focus_stress_level = StressLevel.MODERATE.value
        elif recent_focus >= 4:  # 4-5
            focus_stress_level = StressLevel.HIGH.value
        else:  # 1-3
            focus_stress_level = StressLevel.EXTREME.value
        
        # Calculate cognitive stress score (0-100)
        cognitive_stress_score = max(0, min(100, int((10 - recent_focus) * 10)))
        
        return {
            "stressor_type": StressorType.COGNITIVE.value,
            "stress_level": focus_stress_level,
            "stress_score": cognitive_stress_score,
            "details": {
                "focus_level": recent_focus
            }
        }
    
    def _analyze_emotional_stress(self, metrics: List[HealthMetrics]) -> Dict[str, Any]:
        """
        Analyze emotional stress indicators (mood, anxiety levels, etc.).
        
        Args:
            metrics: List of health metrics
            
        Returns:
            Dictionary with emotional stress analysis
        """
        # Extract relevant metrics
        mood_metrics = [m for m in metrics if hasattr(m, 'mood_level') and m.mood_level is not None]
        anxiety_metrics = [m for m in metrics if hasattr(m, 'anxiety_level') and m.anxiety_level is not None]
        
        if not mood_metrics and not anxiety_metrics:
            return None
        
        details = {}
        stress_factors = []
        
        # Analyze mood (mood is typically 1-10, where higher is better)
        if mood_metrics:
            recent_mood = mood_metrics[-1].mood_level
            
            # Convert to stress level (low mood = high stress)
            if recent_mood >= 8:  # 8-10
                mood_stress_level = StressLevel.LOW.value
            elif recent_mood >= 6:  # 6-7
                mood_stress_level = StressLevel.MODERATE.value
            elif recent_mood >= 4:  # 4-5
                mood_stress_level = StressLevel.HIGH.value
            else:  # 1-3
                mood_stress_level = StressLevel.EXTREME.value
            
            mood_stress_score = max(0, min(100, int((10 - recent_mood) * 10)))
            details["mood_level"] = recent_mood
            stress_factors.append((mood_stress_level, mood_stress_score))
        
        # Analyze anxiety (anxiety is typically 1-10, where lower is better)
        if anxiety_metrics:
            recent_anxiety = anxiety_metrics[-1].anxiety_level
            
            # Convert to stress level (high anxiety = high stress)
            if recent_anxiety <= 3:  # 1-3
                anxiety_stress_level = StressLevel.LOW.value
            elif recent_anxiety <= 5:  # 4-5
                anxiety_stress_level = StressLevel.MODERATE.value
            elif recent_anxiety <= 7:  # 6-7
                anxiety_stress_level = StressLevel.HIGH.value
            else:  # 8-10
                anxiety_stress_level = StressLevel.EXTREME.value
            
            anxiety_stress_score = max(0, min(100, int(recent_anxiety * 10)))
            details["anxiety_level"] = recent_anxiety
            stress_factors.append((anxiety_stress_level, anxiety_stress_score))
        
        # If no emotional stress factors found
        if not stress_factors:
            return None
        
        # Determine overall emotional stress level (take the highest)
        overall_level = max(stress_factors, key=lambda x: self.stress_level_to_numeric(x[0]))[0]
        
        # Calculate overall emotional stress score (take the highest)
        overall_score = max(stress_factors, key=lambda x: x[1])[1]
        
        return {
            "stressor_type": StressorType.EMOTIONAL.value,
            "stress_level": overall_level,
            "stress_score": overall_score,
            "details": details
        }
    
    def _analyze_social_stress(self, metrics: List[HealthMetrics], user_id: str) -> Dict[str, Any]:
        """
        Analyze social stress indicators (meetings, interactions, etc.).
        
        Args:
            metrics: List of health metrics
            user_id: ID of the user
            
        Returns:
            Dictionary with social stress analysis
        """
        # For now, use a simple implementation based on available metrics
        # In a real implementation, this would analyze calendar events, meeting frequency, etc.
        social_pressure_metrics = [m for m in metrics 
                                 if hasattr(m, 'social_pressure') and m.social_pressure is not None]
        
        if not social_pressure_metrics:
            return None
        
        # Get latest social pressure value
        recent_pressure = social_pressure_metrics[-1].social_pressure
        
        # Social pressure is typically 1-10, where lower is better
        if recent_pressure <= 3:  # 1-3
            social_stress_level = StressLevel.LOW.value
        elif recent_pressure <= 5:  # 4-5
            social_stress_level = StressLevel.MODERATE.value
        elif recent_pressure <= 7:  # 6-7
            social_stress_level = StressLevel.HIGH.value
        else:  # 8-10
            social_stress_level = StressLevel.EXTREME.value
        
        social_stress_score = max(0, min(100, int(recent_pressure * 10)))
        
        return {
            "stressor_type": StressorType.SOCIAL.value,
            "stress_level": social_stress_level,
            "stress_score": social_stress_score,
            "details": {
                "social_pressure": recent_pressure
            }
        }
    
    def _calculate_overall_stress(self, stressors: List[Dict[str, Any]]) -> Tuple[int, str]:
        """
        Calculate overall stress score and level from detected stressors.
        
        Args:
            stressors: List of detected stressors
            
        Returns:
            Tuple of (stress_score, stress_level)
        """
        if not stressors:
            return 0, StressLevel.LOW.value
        
        # Calculate weighted stress score
        weighted_score = 0
        total_weight = 0
        
        for stressor in stressors:
            stressor_type = stressor["stressor_type"]
            stressor_score = stressor["stress_score"]
            
            if stressor_type in self.stress_impact_weights:
                weight = self.stress_impact_weights[stressor_type]
                weighted_score += stressor_score * weight
                total_weight += weight
        
        # Calculate final score (0-100)
        final_score = int(weighted_score / total_weight) if total_weight > 0 else 0
        
        # Determine overall stress level
        if final_score <= 25:
            final_level = StressLevel.LOW.value
        elif final_score <= 50:
            final_level = StressLevel.MODERATE.value
        elif final_score <= 75:
            final_level = StressLevel.HIGH.value
        else:
            final_level = StressLevel.EXTREME.value
        
        return final_score, final_level
    
    def _calculate_stress_time_impact(self, stress_score: int) -> float:
        """
        Calculate time impact factor based on stress score.
        
        Args:
            stress_score: Overall stress score (0-100)
            
        Returns:
            Time impact factor (usually in range 1.0-2.0)
        """
        # Simple linear mapping from stress score to time impact
        # Low stress (0) -> factor of 1.0 (no change)
        # Extreme stress (100) -> factor of 2.0 (double time)
        impact_factor = 1.0 + (stress_score / 100)
        
        return impact_factor
    
    def _calculate_task_stress_sensitivity(self, task: Union[TaskModel, Dict[str, Any]]) -> float:
        """
        Calculate how sensitive a task is to stress.
        
        Args:
            task: Task model instance or dictionary
            
        Returns:
            Stress sensitivity factor (0.0-1.0)
        """
        # Handle dictionary or object access
        try:
            # Default values
            focus_required = 3
            energy_required = 3
            
            # Get focus required from task
            if hasattr(task, 'focus_required') and task.focus_required is not None:
                focus_required = task.focus_required
            elif isinstance(task, dict) and 'focus_required' in task:
                focus_required = task['focus_required']
                
            # Get energy required from task  
            if hasattr(task, 'energy_required') and task.energy_required is not None:
                energy_required = task.energy_required
            elif isinstance(task, dict) and 'energy_required' in task:
                energy_required = task['energy_required']
                
            # Calculate sensitivities
            focus_sensitivity = focus_required / 5  # 0.2-1.0
            energy_sensitivity = energy_required / 5  # 0.2-1.0
            
            # Calculate combined sensitivity
            sensitivity = (focus_sensitivity * 0.6) + (energy_sensitivity * 0.4)
            
            return sensitivity
        except Exception as e:
            logger.error(f"Error calculating stress sensitivity: {e}")
            return 0.5  # Default medium sensitivity
    
    async def _determine_stress_trend(self, user_id: str, current_score: int) -> str:
        """
        Determine trend in stress levels over time.
        
        Args:
            user_id: ID of the user
            current_score: Current stress score
            
        Returns:
            Trend description: "increasing", "decreasing", or "stable"
        """
        # Get historical stress scores (simplified implementation)
        # In a real implementation, this would retrieve saved stress scores from database
        historicaldata = await self._get_historical_stress_data(user_id)
        
        if not historicaldata or len(historicaldata) < 2:
            return "stable"  # Not enough data to determine trend
        
        # Calculate trend from last few measurements
        recent_scores = [data["score"] for data in historicaldata[-3:]]
        recent_scores.append(current_score)
        
        if len(recent_scores) < 2:
            return "stable"
        
        # Simple trend detection
        trend_value = sum(recent_scores[i] - recent_scores[i-1] for i in range(1, len(recent_scores)))
        
        if trend_value > 5:
            return "increasing"
        elif trend_value < -5:
            return "decreasing"
        else:
            return "stable"
    
    async def _get_recent_health_metrics(self, user_id: str) -> List[HealthMetrics]:
        """
        Get recent health metrics for a user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            List of recent health metrics
        """
        if self.db is None:
            return []
        
        # Calculate lookback time
        lookback_time = datetime.now() - timedelta(hours=self.lookback_period)
        
        # Query recent metrics
        stmt = (
            select(HealthMetrics)
            .where(
                and_(
                    HealthMetrics.user_id == user_id,
                    HealthMetrics.timestamp >= lookback_time
                )
            )
            .order_by(HealthMetrics.timestamp)
        )
        
        result = await self.db.execute(stmt)
        metrics = result.scalars().all()
        
        return list(metrics)
    
    async def _get_user(self, user_id: str) -> Optional[UserModel]:
        """
        Get user by ID.
        
        Args:
            user_id: ID of the user
            
        Returns:
            UserModel instance or None if not found
        """
        if self.db is None:
            return None
            
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await self.db.execute(stmt)
        user_row = result.first()
        
        if user_row:
            return user_row[0]
        return None
    
    async def _get_task(self, task_id: str) -> Optional[TaskModel]:
        """
        Get task by ID.
        
        Args:
            task_id: ID of the task
            
        Returns:
            TaskModel instance or None if not found
        """
        if self.db is None:
            return None
            
        stmt = select(TaskModel).where(TaskModel.id == task_id)
        result = await self.db.execute(stmt)
        task_row = result.first()
        
        if task_row:
            return task_row[0]
        return None
    
    async def _get_historical_stress_data(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get historical stress data for a user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            List of historical stress data points
        """
        # This would normally retrieve data from database
        # For this implementation, we'll return a simple mock dataset
        return [
            {"timestamp": datetime.now() - timedelta(hours=24), "score": 30},
            {"timestamp": datetime.now() - timedelta(hours=18), "score": 45},
            {"timestamp": datetime.now() - timedelta(hours=12), "score": 40},
            {"timestamp": datetime.now() - timedelta(hours=6), "score": 35}
        ]
    
    @staticmethod
    def stress_level_to_numeric(level: str) -> int:
        """
        Convert stress level string to numeric value for comparisons.
        
        Args:
            level: Stress level string
            
        Returns:
            Numeric value of stress level
        """
        if level == StressLevel.LOW.value:
            return 1
        elif level == StressLevel.MODERATE.value:
            return 2
        elif level == StressLevel.HIGH.value:
            return 3
        elif level == StressLevel.EXTREME.value:
            return 4
        else:
            return 0
    
    def save(self, filepath: str) -> None:
        """
        Save model parameters to a file.
        
        Args:
            filepath: Path to save model to
        """
        params = {
            "stress_threshold_hr": self.stress_threshold_hr,
            "stress_threshold_hrv": self.stress_threshold_hrv,
            "stress_impact_weights": self.stress_impact_weights,
            "lookback_period": self.lookback_period,
            "env_thresholds": self.env_thresholds
        }
        
        with open(filepath, 'w') as f:
            json.dump(params, f)
    
    @classmethod
    def load(cls, filepath: str) -> 'ContextualStressorDetector':
        """
        Load model parameters from a file.
        
        Args:
            filepath: Path to load model from
            
        Returns:
            Loaded ContextualStressorDetector instance
        """
        try:
            with open(filepath, 'r') as f:
                params = json.load(f)
                
            return cls(
                stress_threshold_hr=params.get("stress_threshold_hr"),
                stress_threshold_hrv=params.get("stress_threshold_hrv"),
                stress_impact_weights=params.get("stress_impact_weights"),
                lookback_period=params.get("lookback_period", 24)
            )
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Error loading model parameters: {e}")
            return cls() 