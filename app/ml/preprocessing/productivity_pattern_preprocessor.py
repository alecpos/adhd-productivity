"""Specialized preprocessor for productivity pattern detection."""

from typing import Dict, List, Tuple, Any, Optional
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sklearn.preprocessing import StandardScaler, OneHotEncoder

from app.models.time_block_model import BlockType, BlockPriority


class ProductivityPatternPreprocessor:
    """Preprocessor for time block and mental health data for productivity pattern analysis.

    This preprocessor creates sequence data from time blocks and mental health logs
    to feed into LSTM models for productivity pattern detection.
    """

    def __init__(self):
        """Initialize the preprocessor with required scalers and encoders."""
        self.feature_scaler = StandardScaler()
        self.block_type_encoder = OneHotEncoder(sparse=False)
        self.priority_encoder = OneHotEncoder(sparse=False)
        self.day_of_week_encoder = OneHotEncoder(sparse=False)
        self.time_of_day_encoder = OneHotEncoder(sparse=False)

        # Pre-fit block type encoder with all possible types
        self.block_type_encoder.fit([[bt.value] for bt in BlockType])

        # Pre-fit priority encoder with all possible priorities
        self.priority_encoder.fit([[p.value] for p in BlockPriority])

        # Pre-fit day of week encoder
        self.day_of_week_encoder.fit([[i] for i in range(7)])

        # Pre-fit time of day encoder
        self.time_of_day_encoder.fit([[i] for i in range(24)])

    def prepare_time_block_features(self, time_blocks: List[Dict[str, Any]]) -> pd.DataFrame:
        """Extract features from time blocks for productivity analysis.

        Args:
            time_blocks: List of time block data dictionaries

        Returns:
            DataFrame with extracted features
        """
        if not time_blocks:
            return pd.DataFrame()

        # Convert to DataFrame for easier manipulation
        df = pd.DataFrame(time_blocks)

        # Sort by start time
        if "start_time" in df.columns:
            df = df.sort_values("start_time")

        # Extract time features (hour of day, day of week)
        if "start_time" in df.columns:
            df["hour_of_day"] = df["start_time"].apply(lambda x: x.hour)
            df["day_of_week"] = df["start_time"].apply(lambda x: x.weekday())

            # Convert to cyclical features for time
            df["hour_sin"] = np.sin(2 * np.pi * df["hour_of_day"] / 24)
            df["hour_cos"] = np.cos(2 * np.pi * df["hour_of_day"] / 24)
            df["day_sin"] = np.sin(2 * np.pi * df["day_of_week"] / 7)
            df["day_cos"] = np.cos(2 * np.pi * df["day_of_week"] / 7)

        # One-hot encode categorical variables
        if "block_type" in df.columns:
            block_types = self.block_type_encoder.transform(df["block_type"].values.reshape(-1, 1))

            # Add block type columns
            for i, bt in enumerate(BlockType):
                df[f"block_type_{bt.value}"] = block_types[:, i]

        if "priority" in df.columns:
            priorities = self.priority_encoder.transform(df["priority"].values.reshape(-1, 1))

            # Add priority columns
            for i, p in enumerate(BlockPriority):
                df[f"priority_{p.value}"] = priorities[:, i]

        # Calculate durations
        if "start_time" in df.columns and "end_time" in df.columns:
            df["planned_duration"] = df.apply(
                lambda x: (x["end_time"] - x["start_time"]).total_seconds() / 60, axis=1
            )

        if "actual_start_time" in df.columns and "actual_end_time" in df.columns:
            df["actual_duration"] = df.apply(
                lambda x: (
                    (x["actual_end_time"] - x["actual_start_time"]).total_seconds() / 60
                    if pd.notna(x["actual_start_time"]) and pd.notna(x["actual_end_time"])
                    else np.nan
                ),
                axis=1,
            )

            # Calculate duration accuracy
            df["duration_accuracy"] = df.apply(
                lambda x: (
                    x["planned_duration"] / x["actual_duration"]
                    if pd.notna(x["actual_duration"]) and x["actual_duration"] > 0
                    else np.nan
                ),
                axis=1,
            )

        # Get relevant numeric features for scaling
        numeric_features = [
            "energy_level",
            "focus_level",
            "mental_health_score",
            "completion_rate",
            "effectiveness_score",
            "total_focus_time",
            "interruption_count",
            "planned_duration",
        ]

        numeric_columns = [col for col in numeric_features if col in df.columns]

        if numeric_columns:
            # Fill missing values
            df[numeric_columns] = df[numeric_columns].fillna(0)

            # Scale numeric features
            df[numeric_columns] = self.feature_scaler.fit_transform(df[numeric_columns])

        return df

    def prepare_mental_health_features(
        self, mental_health_logs: List[Dict[str, Any]]
    ) -> pd.DataFrame:
        """Extract features from mental health logs.

        Args:
            mental_health_logs: List of mental health log dictionaries

        Returns:
            DataFrame with extracted features
        """
        if not mental_health_logs:
            return pd.DataFrame()

        # Convert to DataFrame
        df = pd.DataFrame(mental_health_logs)

        # Sort by timestamp
        if "timestamp" in df.columns:
            df = df.sort_values("timestamp")

        # Extract time features
        if "timestamp" in df.columns:
            df["hour_of_day"] = df["timestamp"].apply(lambda x: x.hour)
            df["day_of_week"] = df["timestamp"].apply(lambda x: x.weekday())

            # Convert to cyclical features
            df["hour_sin"] = np.sin(2 * np.pi * df["hour_of_day"] / 24)
            df["hour_cos"] = np.cos(2 * np.pi * df["hour_of_day"] / 24)
            df["day_sin"] = np.sin(2 * np.pi * df["day_of_week"] / 7)
            df["day_cos"] = np.cos(2 * np.pi * df["day_of_week"] / 7)

        # Get relevant numeric features for scaling
        numeric_features = [
            "mood_score",
            "stress_level",
            "anxiety_level",
            "anxiety_score",
            "energy_level",
            "focus_level",
            "sleep_hours",
            "sleep_quality",
        ]

        numeric_columns = [col for col in numeric_features if col in df.columns]

        if numeric_columns:
            # Fill missing values
            df[numeric_columns] = df[numeric_columns].fillna(0)

            # Scale numeric features
            df[numeric_columns] = self.feature_scaler.fit_transform(df[numeric_columns])

        return df

    def create_hourly_sequences(
        self,
        time_blocks_df: pd.DataFrame,
        mental_health_df: pd.DataFrame,
        sequence_length: int = 14,
        prediction_horizon: int = 1,
        resample_freq: str = "H",
    ) -> Tuple[np.ndarray, Dict[str, np.ndarray]]:
        """Create hourly sequence data for LSTM model.

        Args:
            time_blocks_df: DataFrame with time block features
            mental_health_df: DataFrame with mental health features
            sequence_length: Number of time periods to include in sequence
            prediction_horizon: Number of periods ahead to predict
            resample_freq: Frequency to resample data ('H' for hourly)

        Returns:
            Tuple of input sequences and target dictionaries
        """
        # Merge and resample data to hourly intervals
        if "start_time" in time_blocks_df.columns:
            time_blocks_df = time_blocks_df.set_index("start_time")

        if "timestamp" in mental_health_df.columns:
            mental_health_df = mental_health_df.set_index("timestamp")

        # Get common columns to avoid duplicates
        common_cols = set(time_blocks_df.columns) & set(mental_health_df.columns)
        mental_health_cols = [col for col in mental_health_df.columns if col not in common_cols]

        # Create merged dataframe
        if not time_blocks_df.empty and not mental_health_df.empty:
            # Resample both dataframes to hourly and merge
            time_blocks_hourly = time_blocks_df.resample(resample_freq).mean()
            mental_health_hourly = (
                mental_health_df[mental_health_cols].resample(resample_freq).mean()
            )
            merged_df = pd.concat([time_blocks_hourly, mental_health_hourly], axis=1)
        elif not time_blocks_df.empty:
            merged_df = time_blocks_df.resample(resample_freq).mean()
        elif not mental_health_df.empty:
            merged_df = mental_health_df.resample(resample_freq).mean()
        else:
            return np.array([]), {}

        # Forward fill missing values within the resample
        merged_df = merged_df.fillna(method="ffill")

        # Create sequences
        sequences = []
        completion_targets = []
        focus_targets = []
        energy_targets = []
        optimal_time_targets = []

        # Build sequences with a sliding window
        for i in range(len(merged_df) - sequence_length - prediction_horizon + 1):
            # Input sequence
            seq = merged_df.iloc[i : i + sequence_length].values
            sequences.append(seq)

            # Target values (from the period after the sequence)
            target_idx = i + sequence_length + prediction_horizon - 1

            # 1. Completion rate (binary success/failure)
            completion_rate = merged_df.iloc[target_idx].get("completion_rate", 0)
            completion_targets.append(1 if completion_rate >= 0.5 else 0)

            # 2. Focus level prediction
            focus_level = merged_df.iloc[target_idx].get("focus_level", 0)
            focus_targets.append(focus_level)

            # 3. Energy level prediction
            energy_level = merged_df.iloc[target_idx].get("energy_level", 0)
            energy_targets.append(energy_level)

            # 4. Optimal time (which hour of day is most productive)
            # We'll create a one-hot encoded vector for the 24 hours of the day
            hour = merged_df.index[target_idx].hour
            optimal_time = np.zeros(24)
            optimal_time[hour] = 1
            optimal_time_targets.append(optimal_time)

        # Convert lists to numpy arrays
        X = np.array(sequences)
        y_completion = np.array(completion_targets).reshape(-1, 1)
        y_focus = np.array(focus_targets).reshape(-1, 1)
        y_energy = np.array(energy_targets).reshape(-1, 1)
        y_optimal_time = np.array(optimal_time_targets)

        # Return input sequences and targets as a dictionary
        y_dict = {
            "completion_rate": y_completion,
            "focus_level": y_focus,
            "energy_level": y_energy,
            "optimal_time": y_optimal_time,
        }

        return X, y_dict

    def get_flexible_block_indices(self, time_blocks: List[Dict[str, Any]]) -> List[int]:
        """Get indices of flexible time blocks for sliding window analysis.

        Args:
            time_blocks: List of time block dictionaries

        Returns:
            List of indices for flexible blocks
        """
        indices = []
        for i, block in enumerate(time_blocks):
            if block.get("is_flexible", False):
                indices.append(i)
        return indices
