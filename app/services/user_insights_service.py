"""User insights service."""

import logging
import numpy as np
import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from uuid import UUID
from tensorflow import keras
from scipy import stats

from app.models.user_model import UserModel
from app.schemas.user_schema import UserResponseSchema, UserCreateSchema
from app.services.base_service import BaseService
from app.services.mental_health_service import MentalHealthService
from app.schemas.mental_health_schema import MentalHealthLogResponseSchema

logger = logging.getLogger(__name__)


class UserInsightsService(BaseService[UserModel, UserResponseSchema, UserCreateSchema]):
    """Service for analyzing user patterns and building comprehensive user models."""

    def __init__(self, db: AsyncSession):
        super().__init__(db=db, model=UserModel, schema=UserResponseSchema)
        self.mental_health_service = MentalHealthService(db)
        self.mood_predictor = self._build_mood_predictor()
        self.activity_recommender = self._build_activity_recommender()
        self.scaler = StandardScaler()

    def _build_mood_predictor(self) -> keras.models.Sequential:
        """Build and compile the mood prediction model."""
        model = keras.models.Sequential(
            [
                keras.layers.Dense(64, activation="relu", input_shape=(10,)),
                keras.layers.Dropout(0.2),
                keras.layers.Dense(32, activation="relu"),
                keras.layers.Dropout(0.2),
                keras.layers.Dense(16, activation="relu"),
                keras.layers.Dense(1),
            ]
        )
        model.compile(optimizer="adam", loss="mse", metrics=["mae"])

    def _build_activity_recommender(self) -> keras.models.Sequential:
        """Build and compile the activity recommendation model."""
        model = keras.models.Sequential(
            [
                keras.layers.Dense(32, activation="relu", input_shape=(8,)),
                keras.layers.Dropout(0.2),
                keras.layers.Dense(16, activation="relu"),
                keras.layers.Dense(8, activation="softmax"),
            ]
        )
        model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])

    async def _prepare_features(
        self, mental_health_stats: Dict[str, Any], mental_health_trends: Dict[str, Any]
    ) -> np.ndarray:
        """Prepare features for ML models."""
        features = []
        features.extend(
            [
                mental_health_stats["mood_average"],
                mental_health_stats["stress_level_average"],
                mental_health_stats["anxiety_level_average"],
                mental_health_stats["energy_level_average"],
                mental_health_stats["sleep_quality_average"],
            ]
        )
        hour = datetime.now().hour
        day_of_week = datetime.now().weekday()
        features.extend(
            [
                np.sin(2 * np.pi * hour / 24),
                np.cos(2 * np.pi * hour / 24),
                np.sin(2 * np.pi * day_of_week / 7),
                np.cos(2 * np.pi * day_of_week / 7),
            ]
        )
        features = np.array(features).reshape(1, -1)
        return self.scaler.fit_transform(features)

    async def _analyze_patterns(
        self, stats: Dict[str, Any], trends: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze patterns and correlations in user data using ML models."""
        try:
            features = await self._prepare_features(stats, trends)
            activity_impact = {}
            for activity in stats["most_common_activities"]:
                activity_dates = self._get_activity_dates(trends, activity)
                mood_impact = self._calculate_mood_impact(trends, activity_dates)
                energy_impact = self._calculate_energy_impact(trends, activity_dates)
                stress_reduction = self._calculate_stress_reduction(trends, activity_dates)
                activity_impact[activity] = {
                    "mood_impact": float(mood_impact),
                    "energy_impact": float(energy_impact),
                    "stress_reduction": float(stress_reduction),
                }
            optimal_times = self._analyze_optimal_times(trends)
            stress_triggers = self._analyze_stress_triggers(trends, stats["most_common_triggers"])
            mood_boosters = self._predict_mood_boosters(features, stats["most_common_activities"])
            energy_patterns = self._analyze_energy_patterns(trends)
            sleep_impact = self._analyze_sleep_impact(trends)
            recommendations = self._generate_recommendations(
                features, activity_impact, optimal_times, energy_patterns
            )
            return {
                "activity_impact": activity_impact,
                "optimal_times": optimal_times,
                "stress_triggers": stress_triggers,
                "mood_boosters": mood_boosters,
                "energy_patterns": energy_patterns,
                "sleep_impact": sleep_impact,
                "suggested_activities": recommendations["activities"],
                "recommended_strategies": recommendations["strategies"],
                "schedule_recommendations": recommendations["schedule"],
                "improvement_areas": self._identify_improvement_areas(stats, trends),
                "achieved_goals": self._identify_achieved_goals(stats, trends),
            }
        except Exception as e:
            logger.error(f"Error in pattern analysis: {str(e)}", exc_info=True)

    def _get_activity_dates(self, trends: Dict[str, Any], activity: str) -> List[datetime]:
        """Get dates when an activity occurred."""
        activity_dates = []
        for trend in trends["mood_trends"]:
            if activity in trend.get("activities", []):
                activity_dates.append(trend["date"])

    def _calculate_mood_impact(
        self, trends: Dict[str, Any], activity_dates: List[datetime]
    ) -> float:
        """Calculate the impact of an activity on mood using statistical analysis."""
        activity_moods = []
        non_activity_moods = []
        for trend in trends["mood_trends"]:
            if trend["date"] in activity_dates:
                activity_moods.append(trend["value"])
            else:
                non_activity_moods.append(trend["value"])
        if not activity_moods or not non_activity_moods:
            return 0.0
        t_stat, p_value = stats.ttest_ind(activity_moods, non_activity_moods)
        effect_size = (np.mean(activity_moods) - np.mean(non_activity_moods)) / np.sqrt(
            (
                (len(activity_moods) - 1) * np.std(activity_moods) ** 2
                + (len(non_activity_moods) - 1) * np.std(non_activity_moods) ** 2
            )
            / (len(activity_moods) + len(non_activity_moods) - 2)
        )
        return effect_size if p_value < 0.05 else 0.0

    def _calculate_energy_impact(
        self, trends: Dict[str, Any], activity_dates: List[datetime]
    ) -> float:
        """Calculate the impact of an activity on energy levels."""
        return self._calculate_mood_impact(trends, activity_dates)

    def _calculate_stress_reduction(
        self, trends: Dict[str, Any], activity_dates: List[datetime]
    ) -> float:
        """Calculate the stress reduction effect of an activity."""
        return -self._calculate_mood_impact(trends, activity_dates)

    def _analyze_optimal_times(self, trends: Dict[str, Any]) -> Dict[str, List[int]]:
        """Analyze optimal times for activities using time series analysis."""
        energy_by_hour = {i: [] for i in range(24)}
        focus_by_hour = {i: [] for i in range(24)}
        stress_by_hour = {i: [] for i in range(24)}
        for trend in trends["energy_trends"]:
            hour = trend["date"].hour
            energy_by_hour[hour].append(trend["value"])
        for trend in trends.get("focus_trends", []):
            hour = trend["date"].hour
            focus_by_hour[hour].append(trend["value"])
        for trend in trends.get("stress_trends", []):
            hour = trend["date"].hour
            stress_by_hour[hour].append(trend["value"])
        return {
            "high_energy": self._get_peak_hours(energy_by_hour),
            "high_focus": self._get_peak_hours(focus_by_hour),
            "low_stress": self._get_peak_hours(stress_by_hour, inverse=True),
        }

    def _get_peak_hours(
        self, values_by_hour: Dict[int, List[float]], inverse: bool = False
    ) -> List[int]:
        """Get hours with peak values (or minimum values if inverse=True)."""
        hour_averages = {
            hour: np.mean(values) if values else 0 for hour, values in values_by_hour.items()
        }
        threshold = np.percentile(list(hour_averages.values()), 25 if inverse else 75)
        return [
            hour
            for hour, avg in hour_averages.items()
            if (avg <= threshold if inverse else avg >= threshold)
        ]

    def _analyze_stress_triggers(
        self, trends: Dict[str, Any], triggers: List[str]
    ) -> List[Dict[str, Any]]:
        """Analyze stress triggers using correlation analysis."""
        trigger_analysis = []
        for trigger in triggers:
            trigger_dates = set()
            for trend in trends.get("stress_trends", []):
                if trigger in trend.get("triggers", []):
                    trigger_dates.add(trend["date"])
            impact_level = self._calculate_trigger_impact(trends, trigger_dates)
            frequency = len(trigger_dates) / len(trends.get("stress_trends", []))
            trigger_analysis.append(
                {
                    "trigger": trigger,
                    "impact_level": float(impact_level),
                    "frequency": float(frequency),
                }
            )

    def _predict_mood_boosters(self, features: np.ndarray, activities: List[str]) -> List[str]:
        """Predict activities that are likely to boost mood."""
        activity_scores = self.activity_recommender.predict(features)[0]
        top_indices = np.argsort(activity_scores)[-3:]
        return [activities[i] for i in top_indices if i < len(activities)]

    def _analyze_energy_patterns(self, trends: Dict[str, Any]) -> Dict[str, List[int]]:
        """Analyze energy patterns using time series decomposition."""
        if not trends.get("energy_trends"):
            return {"peak_hours": [], "low_periods": []}
        energy_series = pd.Series(
            [t["value"] for t in trends["energy_trends"]],
            index=[t["date"] for t in trends["energy_trends"]],
        )
        decomposition = stats.tsa.seasonal_decompose(
            energy_series, period=24, extrapolate_trend="freq"
        )
        seasonal = decomposition.seasonal
        peak_hours = seasonal[seasonal > seasonal.mean()].index.hour.tolist()
        low_periods = seasonal[seasonal < seasonal.mean()].index.hour.tolist()
        return {"peak_hours": peak_hours, "low_periods": low_periods}

    def _analyze_sleep_impact(self, trends: Dict[str, Any]) -> Dict[str, float]:
        """Analyze the impact of sleep on daily performance."""
        sleep_quality = []
        next_day_performance = []
        for i in range(len(trends.get("sleep_trends", [])) - 1):
            sleep_trend = trends["sleep_trends"][i]
            next_day = trends["energy_trends"][i + 1]
            sleep_quality.append(sleep_trend["value"])
            next_day_performance.append(next_day["value"])
        if not sleep_quality or not next_day_performance:
            return {"quality_correlation": 0.0, "optimal_duration": 7.0}
        correlation = np.corrcoef(sleep_quality, next_day_performance)[0, 1]
        sleep_durations = [t.get("duration", 0) for t in trends.get("sleep_trends", [])]
        performance_by_duration = {}
        for duration, performance in zip(sleep_durations, next_day_performance):
            if duration not in performance_by_duration:
                performance_by_duration[duration] = []
            performance_by_duration[duration].append(performance)
        optimal_duration = max(
            performance_by_duration.items(), key=lambda x: np.mean(x[1]) if x[1] else 0
        )[0]
        return {
            "quality_correlation": float(correlation),
            "optimal_duration": float(optimal_duration),
        }

    def _generate_recommendations(
        self,
        features: np.ndarray,
        activity_impact: Dict[str, Dict[str, float]],
        optimal_times: Dict[str, List[int]],
        energy_patterns: Dict[str, List[int]],
    ) -> Dict[str, List[str]]:
        """Generate personalized recommendations using ML models."""
        activity_probs = self.activity_recommender.predict(features)[0]
        suggested_activities = [
            activity
            for activity, impact in activity_impact.items()
            if impact["mood_impact"] > 0 or impact["energy_impact"] > 0
        ]
        strategies = [
            strategy
            for strategy, impact in activity_impact.items()
            if impact["stress_reduction"] > 0
        ]
        schedule = []
        for hour in range(24):
            if hour in optimal_times["high_energy"]:
                schedule.append(f"Schedule high-energy tasks around {hour:02d}:00")
            elif hour in optimal_times["high_focus"]:
                schedule.append(f"Schedule focused work around {hour:02d}:00")
            elif hour in optimal_times["low_stress"]:
                schedule.append(f"Schedule relaxing activities around {hour:02d}:00")
        return {
            "activities": suggested_activities[:5],
            "strategies": strategies[:3],
            "schedule": schedule[:5],
        }

    def _identify_improvement_areas(
        self, stats: Dict[str, Any], trends: Dict[str, Any]
    ) -> List[str]:
        """Identify areas where the user can improve."""
        improvements = []
        if stats["mood_average"] < 6:
            improvements.append("Mood management")
        if stats["stress_level_average"] > 6:
            improvements.append("Stress reduction")
        if stats["sleep_quality_average"] < 6:
            improvements.append("Sleep quality")
        if stats["energy_level_average"] < 6:
            improvements.append("Energy management")

    def _identify_achieved_goals(self, stats: Dict[str, Any], trends: Dict[str, Any]) -> List[str]:
        """Identify goals that the user has achieved."""
        achievements = []
        if stats["mood_average"] > 7:
            achievements.append("Maintained positive mood")
        if stats["stress_level_average"] < 4:
            achievements.append("Managed stress effectively")
        if stats["sleep_quality_average"] > 7:
            achievements.append("Achieved good sleep quality")
        if stats["streak"] > 7:
            achievements.append(f"Maintained a {stats['streak']}-day streak")


def get_user_insights_service(db: AsyncSession) -> UserInsightsService:
    """Get an instance of the user insights service."""
    return UserInsightsService(db)
