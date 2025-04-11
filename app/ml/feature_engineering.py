from typing import Dict, List, Any, Tuple
import numpy as np
import pandas as pd
from sklearn.preprocessing import OneHotEncoder, StandardScaler


class FeatureEngineer:
    """Handles feature engineering for ML models."""

    def __init__(self):
        self.scaler = StandardScaler()
        self.categorical_encoder = OneHotEncoder(sparse_output=False, handle_unknown="ignore")

    def prepare_features(
        self, user_data: Dict[str, List[Dict[str, Any]]]
    ) -> Tuple[Dict[str, np.ndarray], Dict[str, np.ndarray]]:
        """
        Prepare features and targets from collected user data.
        Returns a tuple of (features, targets).
        """
        # Convert data to DataFrames
        mental_health_df = pd.DataFrame(user_data["mental_health"])
        energy_df = pd.DataFrame(user_data["energy"])
        tasks_df = pd.DataFrame(user_data["tasks"])

        # Prepare features for each data type
        mental_health_features, mental_health_targets = self._prepare_mental_health_features(
            mental_health_df
        )
        energy_features, energy_targets = self._prepare_energy_features(energy_df)
        task_features, task_targets = self._prepare_task_features(tasks_df)

        features = {
            "mental_health": mental_health_features,
            "energy": energy_features,
            "tasks": task_features,
        }

        targets = {
            "mental_health": mental_health_targets,
            "energy": energy_targets,
            "tasks": task_targets,
        }

        return features, targets

    def _prepare_mental_health_features(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare features and targets for mental health prediction."""
        if df.empty:
            return np.array([]), np.array([])

        # Extract numerical features
        numerical_features = df[
            [
                "mood_score",
                "stress_level",
                "anxiety_level",
                "energy_level",
                "sleep_quality",
            ]
        ].values

        # Scale numerical features
        scaled_features = self.scaler.fit_transform(numerical_features)

        # Extract time features
        time_features = self._extract_time_features(df["timestamp"])

        # Encode activity log
        activity_features = self._encode_activity_log(df["activity_log"])

        # Combine all features
        features = np.hstack([scaled_features, time_features, activity_features])

        # Use mood score as target
        targets = df["mood_score"].values

        return features, targets

    def _prepare_energy_features(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare features and targets for energy prediction."""
        if df.empty:
            return np.array([]), np.array([])

        # Extract numerical features
        numerical_features = df[["energy_level", "focus_level", "motivation_level"]].values

        # Scale numerical features
        scaled_features = self.scaler.fit_transform(numerical_features)

        # Extract time features
        time_features = self._extract_time_features(df["timestamp"])

        # Combine all features
        features = np.hstack([scaled_features, time_features])

        # Use energy level as target
        targets = df["energy_level"].values

        return features, targets

    def _prepare_task_features(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare features and targets for task success prediction."""
        if df.empty:
            return np.array([]), np.array([])

        # Encode categorical features
        priority_encoded = self._encode_categorical(df["priority"])
        status_encoded = self._encode_categorical(df["status"])

        # Extract time features from due date
        time_features = self._extract_time_features(df["due_date"])

        # Calculate time until due date
        time_until_due = self._calculate_time_until_due(df["due_date"])

        # Combine all features
        features = np.hstack(
            [
                priority_encoded,
                status_encoded,
                time_features,
                time_until_due.values.reshape(-1, 1),
            ]
        )

        # Use task completion status as target (1 for completed, 0 for not completed)
        targets = (df["status"] == "completed").astype(int).values

        return features, targets

    def _extract_time_features(self, timestamps: pd.Series) -> np.ndarray:
        """Extract cyclical time features from timestamps."""
        # Convert to datetime if needed
        if timestamps.dtype != "datetime64[ns]":
            timestamps = pd.to_datetime(timestamps)

        # Extract components
        hour = timestamps.dt.hour
        day = timestamps.dt.day
        month = timestamps.dt.month
        day_of_week = timestamps.dt.dayofweek

        # Create cyclical features
        hour_sin = np.sin(2 * np.pi * hour / 24)
        hour_cos = np.cos(2 * np.pi * hour / 24)
        day_sin = np.sin(2 * np.pi * day / 31)
        day_cos = np.cos(2 * np.pi * day / 31)
        month_sin = np.sin(2 * np.pi * month / 12)
        month_cos = np.cos(2 * np.pi * month / 12)
        dow_sin = np.sin(2 * np.pi * day_of_week / 7)
        dow_cos = np.cos(2 * np.pi * day_of_week / 7)

        return np.column_stack(
            [
                hour_sin,
                hour_cos,
                day_sin,
                day_cos,
                month_sin,
                month_cos,
                dow_sin,
                dow_cos,
            ]
        )

    def _encode_activity_log(self, activity_logs: pd.Series) -> np.ndarray:
        """Encode activity logs into binary features."""
        # Get unique activities
        all_activities = set()
        for activities in activity_logs:
            if isinstance(activities, list):
                all_activities.update(activities)

        # Create binary features for each activity
        activity_features = np.zeros((len(activity_logs), len(all_activities)))
        for i, activities in enumerate(activity_logs):
            if isinstance(activities, list):
                for j, activity in enumerate(all_activities):
                    if activity in activities:
                        activity_features[i, j] = 1

        return activity_features

    def _encode_categorical(self, column: pd.Series) -> np.ndarray:
        """Encode categorical variables using one-hot encoding."""
        # Reshape to 2D array as required by OneHotEncoder
        values = column.values.reshape(-1, 1)
        return self.categorical_encoder.fit_transform(values)

    def _calculate_time_until_due(self, due_dates: pd.Series) -> np.ndarray:
        """Calculate time until due date in days."""
        # Convert to datetime if needed
        if due_dates.dtype != "datetime64[ns]":
            due_dates = pd.to_datetime(due_dates)

        # Calculate time difference in days
        now = pd.Timestamp.now()
        return (due_dates - now).dt.total_seconds() / (24 * 3600)
