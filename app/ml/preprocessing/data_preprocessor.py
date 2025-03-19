from sklearn.preprocessing import LabelEncoder, StandardScaler

from app.models.time_block_model import BlockPriority, BlockType
from app.models.enums_model import MetricType
from typing import List, Dict, Tuple
import numpy as np
import pandas as pd
import tensorflow as tf
from datetime import datetime

class DataPreprocessor:
    def __init__(self):
        self.mood_scaler = StandardScaler()
        self.energy_scaler = StandardScaler()
        self.task_scaler = StandardScaler()
        self.activity_encoder = LabelEncoder()
        self.schedule_scaler = StandardScaler()

    def preprocess_mental_health_data(self, data: List[Dict]) -> Tuple[np.ndarray, np.ndarray]:
        """
        Preprocess mental health logs for model training.
        Returns features and targets for mood prediction.
        """
        df = pd.DataFrame(data)
        features = df[
            [
                "mood_score",
                "stress_level",
                "anxiety_level",
                "energy_level",
                "sleep_quality",
            ]
        ].values
        features = self.mood_scaler.fit_transform(features)
        targets = df["mood_score"].shift(-1).dropna().values
        features = features[:-1]
        return (features, targets)

    def preprocess_energy_data(self, data: List[Dict]) -> Tuple[np.ndarray, np.ndarray]:
        """
        Preprocess energy logs for model training.
        Returns features and targets for energy prediction.
        """
        df = pd.DataFrame(data)
        features = df[["energy_level", "sleep_quality", "stress_level", "activity_duration"]].values
        features = self.energy_scaler.fit_transform(features)
        targets = df["energy_level"].shift(-1).dropna().values
        features = features[:-1]
        return (features, targets)

    def preprocess_task_data(self, data: List[Dict]) -> Tuple[np.ndarray, np.ndarray]:
        """
        Preprocess task data for model training.
        Returns features and targets for task success prediction.
        """
        df = pd.DataFrame(data)
        df["activity_encoded"] = self.activity_encoder.fit_transform(df["activity_type"])
        features = np.column_stack(
            [
                df[
                    [
                        "energy_level",
                        "focus_score",
                        "estimated_duration",
                        "priority_level",
                    ]
                ].values,
                df["activity_encoded"].values,
            ]
        )
        features = self.task_scaler.fit_transform(features)
        targets = df["completed_successfully"].astype(int).values
        return (features, targets)

    def prepare_sequence_data(
        self, data: List[Dict], sequence_length: int = 7, prediction_horizon: int = 1
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare sequential data for time series prediction.
        """
        df = pd.DataFrame(data)
        df = df.sort_values("timestamp")
        sequences = []
        targets = []
        for i in range(len(df) - sequence_length - prediction_horizon + 1):
            sequence = df.iloc[i : i + sequence_length]
            target = df.iloc[i + sequence_length + prediction_horizon - 1]
            sequences.append(sequence.values)
            targets.append(target.values)
        return (np.array(sequences), np.array(targets))

    def create_time_features(self, timestamp: datetime) -> Dict[str, float]:
        """
        Create time-based features from timestamp.
        """
        return {
            "hour_sin": np.sin(2 * np.pi * timestamp.hour / 24),
            "hour_cos": np.cos(2 * np.pi * timestamp.hour / 24),
            "day_of_week_sin": np.sin(2 * np.pi * timestamp.weekday() / 7),
            "day_of_week_cos": np.cos(2 * np.pi * timestamp.weekday() / 7),
            "month_sin": np.sin(2 * np.pi * timestamp.month / 12),
            "month_cos": np.cos(2 * np.pi * timestamp.month / 12),
        }

    def prepare_schedule_features(
        self,
        time_blocks: List[Dict],
        energy_patterns: List[Dict],
        work_hours: List[Dict],
    ) -> Dict[str, tf.Tensor]:
        """
        Prepare features for schedule optimization.

        Args:
            time_blocks: List of historical time block data
            energy_patterns: List of user energy pattern data
            work_hours: List of user work hours data

        Returns:
        """
        blocks_df = pd.DataFrame(time_blocks)
        energy_df = pd.DataFrame(energy_patterns)
        hours_df = pd.DataFrame(work_hours)
        block_types = tf.convert_to_tensor(
            [
                list(BlockType).index(BlockType(block.get("block_type", "task")))
                for block in time_blocks
            ],
            dtype=tf.int32,
        )
        priorities = tf.convert_to_tensor(
            [
                list(BlockPriority).index(BlockPriority(block.get("priority", 2)))
                for block in time_blocks
            ],
            dtype=tf.int32,
        )
        time_features = np.array(
            [list(self.create_time_features(block["start_time"]).values()) for block in time_blocks]
        )
        energy_features = np.zeros((len(time_blocks), 48))
        for i, block in enumerate(time_blocks):
            block_date = block["start_time"].date()
            day_pattern = energy_df[energy_df["date"] == block_date].iloc[0]
            for hour in range(24):
                slot_idx = hour * 2
                energy_features[i, slot_idx : slot_idx + 2] = (
                    day_pattern.get(f"hour_{hour}_energy", 5.0) / 10.0
                )
        historical_metrics = np.column_stack(
            [
                blocks_df["completion_rate"].fillna(0.0),
                blocks_df["effectiveness_score"].fillna(0.0),
                blocks_df["focus_level"].fillna(5.0) / 10.0,
                blocks_df["energy_level"].fillna(5.0) / 10.0,
            ]
        )
        time_features = self.schedule_scaler.fit_transform(time_features)
        historical_metrics = self.schedule_scaler.fit_transform(historical_metrics)
        time_features = np.tile(time_features[:, np.newaxis, :], (1, 48, 1))
        return {
            "block_type": block_types,
            "priority": priorities,
            "time_features": tf.convert_to_tensor(time_features, dtype=tf.float32),
            "energy_features": tf.convert_to_tensor(energy_features, dtype=tf.float32),
            "historical_metrics": tf.convert_to_tensor(historical_metrics, dtype=tf.float32),
        }
