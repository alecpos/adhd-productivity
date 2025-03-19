"""Data preprocessing module."""

from typing import List, Dict, Any, Optional, Tuple
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


class DataPreprocessor:
    """Preprocess data for ML models."""
    
    def __init__(
        self, mental_health_data: List[Dict], 
        energy_data: List[Dict], 
        task_data: List[Dict], 
        calendar_data: List[Dict]
    ):
        """Initialize with various data sources."""
        self.mental_health_data = mental_health_data
        self.energy_data = energy_data
        self.task_data = task_data
        self.calendar_data = calendar_data
        
    def preprocess(self) -> pd.DataFrame:
        """Preprocess all data and return a DataFrame."""
        # Convert data to DataFrames
        mental_health_df = pd.DataFrame(self.mental_health_data) if self.mental_health_data else pd.DataFrame()
        energy_df = pd.DataFrame(self.energy_data) if self.energy_data else pd.DataFrame()
        task_df = pd.DataFrame(self.task_data) if self.task_data else pd.DataFrame()
        calendar_df = pd.DataFrame(self.calendar_data) if self.calendar_data else pd.DataFrame()
        
        # Combine the data sources
        # This is a simple implementation - in a real system, you would do more complex
        # feature engineering and preprocessing
        features_df = self._combine_features(mental_health_df, energy_df, task_df, calendar_df)
        
        return features_df
    
    def _combine_features(
        self, 
        mental_health_df: pd.DataFrame, 
        energy_df: pd.DataFrame, 
        task_df: pd.DataFrame, 
        calendar_df: pd.DataFrame
    ) -> pd.DataFrame:
        """Combine features from different data sources."""
        # This is a placeholder implementation
        # In a real application, you would perform more sophisticated feature engineering
        
        # Create a date range based on the data
        dates = self._get_date_range()
        if not dates:
            return pd.DataFrame()
            
        # Create a base DataFrame with dates
        base_df = pd.DataFrame({"date": dates})
        
        # Add mental health features
        if not mental_health_df.empty and "timestamp" in mental_health_df.columns:
            mental_health_df["date"] = pd.to_datetime(mental_health_df["timestamp"]).dt.date
            mental_health_agg = mental_health_df.groupby("date").agg({
                "mood": "mean",
                "anxiety_level": "mean",
                "focus_level": "mean",
                "energy_level": "mean",
                "stress_level": "mean"
            }).reset_index()
            base_df = pd.merge(base_df, mental_health_agg, on="date", how="left")
        
        # Add energy features
        if not energy_df.empty and "timestamp" in energy_df.columns:
            energy_df["date"] = pd.to_datetime(energy_df["timestamp"]).dt.date
            energy_agg = energy_df.groupby("date").agg({
                "energy_level": "mean",
                "focus_level": "mean"
            }).reset_index()
            # Rename columns to avoid collision with mental health features
            energy_agg = energy_agg.rename(columns={
                "energy_level": "energy_log_level",
                "focus_level": "energy_log_focus"
            })
            base_df = pd.merge(base_df, energy_agg, on="date", how="left")
        
        # Add task features
        if not task_df.empty:
            # Process task data if available
            # Example: count tasks per day, average estimated duration, etc.
            if "due_date" in task_df.columns:
                task_df["date"] = pd.to_datetime(task_df["due_date"]).dt.date
                task_agg = task_df.groupby("date").agg({
                    "id": "count",
                    "estimated_duration": "mean",
                    "priority": "mean",
                    "energy_required": "mean",
                    "focus_required": "mean"
                }).reset_index()
                task_agg = task_agg.rename(columns={
                    "id": "task_count",
                    "estimated_duration": "avg_task_duration",
                    "priority": "avg_task_priority",
                    "energy_required": "avg_task_energy",
                    "focus_required": "avg_task_focus"
                })
                base_df = pd.merge(base_df, task_agg, on="date", how="left")
        
        # Add calendar features
        if not calendar_df.empty:
            # Process calendar data if available
            # Example: count events per day, total duration, etc.
            if "start_time" in calendar_df.columns:
                calendar_df["date"] = pd.to_datetime(calendar_df["start_time"]).dt.date
                calendar_agg = calendar_df.groupby("date").agg({
                    "id": "count",
                }).reset_index()
                calendar_agg = calendar_agg.rename(columns={"id": "event_count"})
                base_df = pd.merge(base_df, calendar_agg, on="date", how="left")
        
        # Fill missing values
        base_df = base_df.fillna(0)
        
        return base_df
    
    def _get_date_range(self) -> List[datetime.date]:
        """Get the date range from the data."""
        dates = []
        
        # Collect dates from mental health data
        if self.mental_health_data:
            for data_entry in self.mental_health_data:
                if "timestamp" in data_entry:
                    dates.append(pd.to_datetime(data_entry["timestamp"]).date())
        
        # Collect dates from energy data
        if self.energy_data:
            for data_entry in self.energy_data:
                if "timestamp" in data_entry:
                    dates.append(pd.to_datetime(data_entry["timestamp"]).date())
        
        # Collect dates from task data
        if self.task_data:
            for data_entry in self.task_data:
                if "due_date" in data_entry and data_entry["due_date"]:
                    dates.append(pd.to_datetime(data_entry["due_date"]).date())
        
        # Collect dates from calendar data
        if self.calendar_data:
            for data_entry in self.calendar_data:
                if "start_time" in data_entry:
                    dates.append(pd.to_datetime(data_entry["start_time"]).date())
        
        if not dates:
            return []
        
        # Create a continuous date range
        min_date = min(dates)
        max_date = max(dates)
        
        return [(min_date + timedelta(days=i)) for i in range((max_date - min_date).days + 1)]
        
    def prepare_mental_health_features(
        self, mental_health_data: List[Dict]
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare mental health features for ML models.
        
        Args:
            mental_health_data: List of mental health data points
            
        Returns:
            Tuple of features and targets as numpy arrays
        """
        if not mental_health_data:
            return np.array([]), np.array([])
        
        features = []
        targets = []
        
        for data_entry in mental_health_data:
            # Extract features
            feature_vector = [
                data_entry.get("anxiety_level", 0),
                data_entry.get("stress_level", 0),
                data_entry.get("sleep_hours", 0),
                data_entry.get("focus_level", 0),
                data_entry.get("energy_level", 0),
            ]
            
            # Extract target (mood score)
            target = data_entry.get("mood_score", 0)
            
            features.append(feature_vector)
            targets.append(target)
        
        return np.array(features), np.array(targets)
    
    def prepare_energy_features(self, energy_data: List[Dict]) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare energy features for ML models.
        
        Args:
            energy_data: List of energy data points
            
        Returns:
            Tuple of features and targets as numpy arrays
        """
        if not energy_data:
            return np.array([]), np.array([])
        
        features = []
        targets = []
        
        for data_entry in energy_data:
            # Extract time-based features
            timestamp = pd.to_datetime(data_entry.get("timestamp"))
            hour = timestamp.hour
            day_of_week = timestamp.dayofweek
            
            # Create feature vector
            feature_vector = [
                hour,
                day_of_week,
                data_entry.get("focus_level", 0),
                data_entry.get("mood_level", 0),
            ]
            
            # Target is energy level
            target = data_entry.get("level", 0)
            
            features.append(feature_vector)
            targets.append(target)
        
        return np.array(features), np.array(targets)
    
    def prepare_task_features(self, task_data: List[Dict]) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare task features for ML models.
        
        Args:
            task_data: List of task data points
            
        Returns:
            Tuple of features and targets as numpy arrays
        """
        if not task_data:
            return np.array([]), np.array([])
        
        features = []
        targets = []
        
        for data_entry in task_data:
            # Extract features
            feature_vector = [
                data_entry.get("priority", 0),
                data_entry.get("difficulty", 0),
                data_entry.get("energy_required", 0),
                data_entry.get("focus_required", 0),
                data_entry.get("estimated_duration", 60),  # Default to 60 minutes
            ]
            
            # Target is completion status (1 for completed, 0 for not)
            target = 1 if data_entry.get("status") == "completed" else 0
            
            features.append(feature_vector)
            targets.append(target)
        
        return np.array(features), np.array(targets)
    
    def prepare_sequence_data(
        self, data: List[Dict], sequence_length: Optional[int] = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare sequential data for recurrent models.
        
        Args:
            data: List of data points in chronological order
            sequence_length: Length of sequences to create
            
        Returns:
            Tuple of sequence data and targets
        """
        if not data or not sequence_length:
            return np.array([]), np.array([])
        
        # Sort data by timestamp
        sorted_data = sorted(data, key=lambda x: x.get("timestamp", ""))
        
        # Create sequences
        sequences = []
        targets = []
        
        for i in range(len(sorted_data) - sequence_length):
            seq = sorted_data[i:i + sequence_length]
            target = sorted_data[i + sequence_length]
            
            # Extract features from sequence
            seq_features = []
            for item in seq:
                features = [
                    item.get("energy_level", 0),
                    item.get("focus_level", 0),
                    item.get("mood_score", 0)
                ]
                seq_features.append(features)
            
            sequences.append(seq_features)
            targets.append(target.get("energy_level", 0))
        
        return np.array(sequences), np.array(targets)

    def _encode_time_features(self, timestamps: List[datetime]) -> np.ndarray:
        """
        Encode temporal features using cyclical encoding.
        """
        hours = np.array([t.hour for t in timestamps])
        days = np.array([t.weekday() for t in timestamps])
        months = np.array([t.month for t in timestamps])

        # Cyclical encoding
        hour_sin = np.sin(2 * np.pi * hours / 24)
        hour_cos = np.cos(2 * np.pi * hours / 24)
        day_sin = np.sin(2 * np.pi * days / 7)
        day_cos = np.cos(2 * np.pi * days / 7)
        month_sin = np.sin(2 * np.pi * months / 12)
        month_cos = np.cos(2 * np.pi * months / 12)

        return np.column_stack([hour_sin, hour_cos, day_sin, day_cos, month_sin, month_cos])

    def _encode_categorical_lists(
        self, categorical_lists: List[List[str]], prefix: str
    ) -> np.ndarray:
        """
        Encode lists of categorical values (e.g., activities, triggers).
        """
        # Flatten lists to get unique values
        unique_values = set()
        for lst in categorical_lists:
            unique_values.update(lst)

        # Create binary encoding
        encoded = np.zeros((len(categorical_lists), len(unique_values)))
        value_to_index = {val: idx for idx, val in enumerate(sorted(unique_values))}

        for i, lst in enumerate(categorical_lists):
            for value in lst:
                if value in value_to_index:
                    encoded[i, value_to_index[value]] = 1

    def prepare_multi_task_data(
        self,
        mental_health_data: List[Dict],
        energy_data: List[Dict],
        task_data: List[Dict],
    ) -> Tuple[np.ndarray, Dict[str, np.ndarray]]:
        """
        Prepare data for multi-task learning.
        """
        # Prepare individual features
        mh_features, mh_targets = self.prepare_mental_health_features(mental_health_data)
        energy_features, energy_targets = self.prepare_energy_features(energy_data)
        task_features, task_targets = self.prepare_task_features(task_data)

        # Ensure all feature sets have the same number of samples
        min_samples = min(len(mh_features), len(energy_features), len(task_features))
        features = np.hstack(
            [
                mh_features[:min_samples],
                energy_features[:min_samples],
                task_features[:min_samples],
            ]
        )

        # Create target dictionary for multi-task learning
        targets = {
            "mood_prediction": mh_targets[:min_samples],
            "energy_prediction": energy_targets[:min_samples],
            "task_completion": task_targets[:min_samples],
        }


class ProductivityPatternPreprocessor:
    """Preprocessor for productivity pattern data."""
    
    def __init__(self, sequence_length: int = 14):
        """Initialize the preprocessor.
        
        Args:
            sequence_length: Length of sequences to use for LSTM models
        """
        self.sequence_length = sequence_length
        
    def preprocess(
        self, 
        time_blocks: pd.DataFrame, 
        mental_health_logs: pd.DataFrame, 
        energy_logs: Optional[pd.DataFrame] = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Preprocess time block data for productivity pattern analysis.
        
        Args:
            time_blocks: DataFrame of time block data
            mental_health_logs: DataFrame of mental health log data
            energy_logs: Optional DataFrame of energy log data
            
        Returns:
            Tuple of features and targets for LSTM model
        """
        if time_blocks.empty:
            return np.array([]), np.array([])
        
        # Sort data by timestamp
        sorted_blocks = time_blocks.sort_values(by="start_time").to_dict('records')
        
        # Extract features
        # For each time block, we extract:
        # - Time features (hour, day of week)
        # - Block type
        # - Energy level
        # - Mental health factors
        # - Duration
        features = []
        targets = []
        
        for block in sorted_blocks:
            start_time = pd.to_datetime(block.get("start_time"))
            hour = start_time.hour / 24.0  # Normalize to 0-1
            day_of_week = start_time.dayofweek / 6.0  # Normalize to 0-1
            
            # Block type (one-hot encoded)
            block_type = block.get("block_type", "task")
            block_type_features = self._one_hot_encode_block_type(block_type)
            
            # Duration in minutes
            duration = block.get("duration", 0) / 240.0  # Normalize assuming max 4 hours
            
            # Effectiveness score (target)
            effectiveness = block.get("effectiveness_score", 0.0)
            
            # Combine features
            feature_vector = [hour, day_of_week, duration] + block_type_features
            
            features.append(feature_vector)
            targets.append(effectiveness)
        
        # Create sequences for LSTM
        sequence_features, sequence_targets = self._create_sequences(
            features, targets, self.sequence_length
        )
        
        return np.array(sequence_features), np.array(sequence_targets)
    
    def _one_hot_encode_block_type(self, block_type: str) -> List[float]:
        """One-hot encode the block type.
        
        Args:
            block_type: Type of time block
            
        Returns:
            One-hot encoded vector
        """
        # Define possible block types
        block_types = [
            "task", "meeting", "focus", "break", "learning", 
            "exercise", "social", "leisure", "chore", "meal"
        ]
        
        # Create one-hot vector
        return [1.0 if bt == block_type else 0.0 for bt in block_types]
    
    def _create_sequences(
        self, features: List[List[float]], targets: List[float], sequence_length: int
    ) -> Tuple[List[List[List[float]]], List[float]]:
        """Create sequences for LSTM model.
        
        Args:
            features: List of feature vectors
            targets: List of target values
            sequence_length: Length of sequences
            
        Returns:
            Tuple of sequence features and targets
        """
        if len(features) <= sequence_length:
            return [], []
        
        sequences = []
        sequence_targets = []
        
        for i in range(len(features) - sequence_length):
            seq = features[i:i + sequence_length]
            target = targets[i + sequence_length]
            
            sequences.append(seq)
            sequence_targets.append(target)
        
        return sequences, sequence_targets
