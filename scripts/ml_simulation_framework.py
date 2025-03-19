"""
ML Simulation Framework

A comprehensive framework for simulating and testing ML models, data pipelines, 
and end-to-end systems under various conditions.

This framework enables:
- Testing ML models with synthetic and simulated data
- Simulating data drift and quality degradation
- Testing system resilience with error injection
- Measuring performance under simulated load
- Creating reproducible test scenarios for ML systems
"""

import logging
import os
import json
import time
import uuid
import warnings
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Any, Callable, Iterator, Type

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, 
    mean_squared_error, mean_absolute_error, r2_score
)

# Custom exceptions
class SimulationError(Exception):
    """Exception raised for errors in the simulation framework."""
    pass

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ml_simulation")

# -----------------------------------------------------------------------------
# Configuration Management
# -----------------------------------------------------------------------------

class SimulationConfigEncoder(json.JSONEncoder):
    """Custom JSON encoder for simulation configuration objects."""
    
    def default(self, obj):
        if hasattr(obj, 'to_dict'):
            return obj.to_dict()
        if isinstance(obj, Enum):
            return obj.name
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if hasattr(obj, '__dict__'):
            return obj.__dict__
        return super().default(obj)


@dataclass
class SimulationConfig:
    """Base configuration for simulation runs."""
    
    name: str
    description: str = ""
    seed: int = 42
    output_dir: str = "simulation_results"
    log_level: str = "INFO"
    save_artifacts: bool = True
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        os.makedirs(self.output_dir, exist_ok=True)
        
    def to_dict(self) -> Dict:
        """Convert configuration to dictionary."""
        return asdict(self)
    
    def save(self, filepath: Optional[str] = None) -> str:
        """Save configuration to a JSON file."""
        if filepath is None:
            filepath = os.path.join(self.output_dir, f"{self.name}_config.json")
            
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, cls=SimulationConfigEncoder, indent=2)
            
        return filepath
    
    @classmethod
    def load(cls, filepath: str) -> 'SimulationConfig':
        """Load configuration from a JSON file."""
        with open(filepath, 'r') as f:
            config_dict = json.load(f)
            
        return cls(**config_dict)


@dataclass
class ModelSimulationConfig(SimulationConfig):
    """Configuration for model simulation scenarios."""
    
    model_type: str = "classifier"
    epochs: int = 10
    batch_size: int = 32
    learning_rate: float = 0.001
    model_params: Dict = field(default_factory=dict)
    

@dataclass
class DataSimulationConfig(SimulationConfig):
    """Configuration for data simulation scenarios."""
    
    dataset_size: int = 10000
    feature_count: int = 10
    class_count: int = 2
    noise_level: float = 0.1
    missing_data_prob: float = 0.0
    outlier_prob: float = 0.0
    drift_rate: float = 0.0
    temporal_dependency: bool = False
    
    
@dataclass
class PipelineSimulationConfig(SimulationConfig):
    """Configuration for pipeline simulation scenarios."""
    
    stages: List[str] = field(default_factory=list)
    stage_failure_probs: Dict[str, float] = field(default_factory=dict)
    latency_distribution: Dict[str, Dict] = field(default_factory=dict)
    resource_constraints: Dict[str, Any] = field(default_factory=dict)


# -----------------------------------------------------------------------------
# Simulation Environment
# -----------------------------------------------------------------------------

class SimulationEnvironment(ABC):
    """Base class for all simulation environments."""
    
    def __init__(self, config: SimulationConfig):
        self.config = config
        self.logger = logging.getLogger(f"simulation.{self.__class__.__name__}")
        self.logger.setLevel(config.log_level)
        self.artifacts = {}
        self.metrics = {}
        self.start_time = None
        self.end_time = None
        self.id = str(uuid.uuid4())
        
        # Set random seed for reproducibility
        np.random.seed(config.seed)
        
    def start(self) -> None:
        """Start the simulation environment."""
        self.start_time = datetime.now()
        self.logger.info(f"Starting simulation: {self.config.name}")
        
    def stop(self) -> None:
        """Stop the simulation environment."""
        self.end_time = datetime.now()
        duration = (self.end_time - self.start_time).total_seconds()
        self.logger.info(f"Simulation completed in {duration:.2f} seconds")
        
    def log_metric(self, name: str, value: Any) -> None:
        """Log a metric with the given name and value."""
        self.metrics[name] = value
        self.logger.info(f"Metric '{name}': {value}")
        
    def save_artifact(self, name: str, artifact: Any) -> str:
        """Save an artifact to the output directory."""
        if not self.config.save_artifacts:
            return None
            
        artifacts_dir = os.path.join(self.config.output_dir, "artifacts")
        os.makedirs(artifacts_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(artifacts_dir, f"{name}_{timestamp}")
        
        # Handle different artifact types
        if isinstance(artifact, pd.DataFrame):
            filepath += ".csv"
            artifact.to_csv(filepath, index=False)
        elif isinstance(artifact, np.ndarray):
            filepath += ".npy"
            np.save(filepath, artifact)
        elif isinstance(artifact, plt.Figure):
            filepath += ".png"
            artifact.savefig(filepath)
        elif isinstance(artifact, dict):
            filepath += ".json"
            with open(filepath, 'w') as f:
                json.dump(artifact, f, cls=SimulationConfigEncoder, indent=2)
        else:
            filepath += ".pkl"
            import pickle
            with open(filepath, 'wb') as f:
                pickle.dump(artifact, f)
                
        self.artifacts[name] = filepath
        return filepath
    
    def generate_report(self) -> Dict:
        """Generate a report of the simulation run."""
        report = {
            "id": self.id,
            "config": self.config.to_dict(),
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration": (self.end_time - self.start_time).total_seconds() if self.start_time and self.end_time else None,
            "metrics": self.metrics,
            "artifacts": self.artifacts
        }
        
        report_path = os.path.join(self.config.output_dir, f"{self.config.name}_report.json")
        with open(report_path, 'w') as f:
            json.dump(report, f, cls=SimulationConfigEncoder, indent=2)
            
        return report
    
    @abstractmethod
    def run(self) -> Dict:
        """Run the simulation and return the results."""
        pass


class TabularDataEnvironment(SimulationEnvironment):
    """Simulation environment for tabular data scenarios."""
    
    def __init__(self, config: DataSimulationConfig):
        super().__init__(config)
        self.data = None
        
    def generate_data(self) -> pd.DataFrame:
        """Generate synthetic tabular data based on configuration."""
        config = self.config
        n_samples = config.dataset_size
        n_features = config.feature_count
        n_classes = config.class_count
        
        # Generate features
        X = np.random.randn(n_samples, n_features)
        
        # Add noise
        if config.noise_level > 0:
            X += np.random.normal(0, config.noise_level, (n_samples, n_features))
        
        # Generate target variable
        if n_classes > 0:  # Classification
            y = np.random.randint(0, n_classes, size=n_samples)
            
            # Make features somewhat predictive of classes
            for c in range(n_classes):
                mask = (y == c)
                class_mean = np.random.randn(n_features) * 2
                X[mask] += class_mean
        else:  # Regression
            # Create a regression target with some relationship to features
            coeffs = np.random.randn(n_features)
            y = X.dot(coeffs) + np.random.normal(0, 1, n_samples)
        
        # Convert to DataFrame
        feature_names = [f"feature_{i}" for i in range(n_features)]
        df = pd.DataFrame(X, columns=feature_names)
        df['target'] = y
        
        # Add missing values if specified
        if config.missing_data_prob > 0:
            mask = np.random.random(df.shape) < config.missing_data_prob
            df = df.mask(mask)
        
        # Add outliers if specified
        if config.outlier_prob > 0:
            outlier_mask = np.random.random(n_samples) < config.outlier_prob
            outlier_indices = np.where(outlier_mask)[0]
            for idx in outlier_indices:
                feature_idx = np.random.randint(0, n_features)
                df.iloc[idx, feature_idx] = df.iloc[:, feature_idx].mean() + \
                                           df.iloc[:, feature_idx].std() * np.random.choice([-10, 10])
        
        # Add temporal patterns if specified
        if config.temporal_dependency:
            # Assuming the data has a natural order (e.g., time series)
            df['time_idx'] = np.arange(n_samples)
            # Add some temporal trends
            df['seasonal'] = np.sin(df['time_idx'] * 2 * np.pi / (n_samples / 4))
            df['trend'] = df['time_idx'] / n_samples * 2
            # Make target partially dependent on temporal features
            if n_classes == 0:  # only for regression
                df['target'] += df['seasonal'] + df['trend']
        
        self.data = df
        return df
    
    def add_drift(self, drift_percentage: float = 0.2) -> pd.DataFrame:
        """Add concept drift to a portion of the data."""
        if self.data is None:
            raise ValueError("Data must be generated before adding drift")
        
        drift_samples = int(len(self.data) * drift_percentage)
        if drift_samples == 0:
            return self.data
            
        # Create a copy of the data
        drifted_data = self.data.copy()
        
        # Select random samples to apply drift
        drift_indices = np.random.choice(
            len(drifted_data), drift_samples, replace=False
        )
        
        # Apply different kinds of drift based on target type
        if np.issubdtype(drifted_data['target'].dtype, np.integer):
            # Classification - swap some labels
            unique_labels = drifted_data['target'].unique()
            if len(unique_labels) > 1:
                for idx in drift_indices:
                    current_label = drifted_data.loc[idx, 'target']
                    other_labels = [l for l in unique_labels if l != current_label]
                    drifted_data.loc[idx, 'target'] = np.random.choice(other_labels)
        else:
            # Regression - add systematic shift
            drift_magnitude = drifted_data['target'].std() * self.config.drift_rate
            drifted_data.loc[drift_indices, 'target'] += drift_magnitude
            
        return drifted_data
    
    def generate_train_test_sets(
        self, test_size: float = 0.2, 
        add_drift_to_test: bool = False
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Generate train and test datasets with optional drift in test set."""
        if self.data is None:
            self.generate_data()
            
        # Split the data
        indices = np.arange(len(self.data))
        np.random.shuffle(indices)
        
        split_idx = int(len(indices) * (1 - test_size))
        train_indices = indices[:split_idx]
        test_indices = indices[split_idx:]
        
        train_data = self.data.iloc[train_indices].reset_index(drop=True)
        test_data = self.data.iloc[test_indices].reset_index(drop=True)
        
        # Add drift to test data if specified
        if add_drift_to_test and self.config.drift_rate > 0:
            # Create a new environment just for test data
            test_config = DataSimulationConfig(
                name=f"{self.config.name}_test_drift",
                dataset_size=len(test_data),
                feature_count=self.config.feature_count,
                class_count=self.config.class_count,
                drift_rate=self.config.drift_rate
            )
            test_env = TabularDataEnvironment(test_config)
            test_env.data = test_data
            test_data = test_env.add_drift(drift_percentage=1.0)
        
        return train_data, test_data
    
    def run(self) -> Dict:
        """Run the tabular data simulation."""
        self.start()
        
        # Generate data
        data = self.generate_data()
        self.logger.info(f"Generated dataset with shape {data.shape}")
        
        # Split into train/test with optional drift
        train_data, test_data = self.generate_train_test_sets(
            add_drift_to_test=(self.config.drift_rate > 0)
        )
        
        # Save artifacts
        self.save_artifact("full_dataset", data)
        self.save_artifact("train_dataset", train_data)
        self.save_artifact("test_dataset", test_data)
        
        # Generate basic stats
        self.log_metric("dataset_size", len(data))
        self.log_metric("feature_count", len(data.columns) - 1)  # Exclude target
        self.log_metric("missing_values", data.isna().sum().sum())
        
        # Visualize data distributions
        fig, ax = plt.subplots(figsize=(10, 6))
        data.drop(columns=['target']).boxplot(ax=ax)
        plt.xticks(rotation=90)
        plt.title("Feature Distributions")
        self.save_artifact("feature_distributions", fig)
        plt.close(fig)
        
        self.stop()
        return self.generate_report()


class TimeSeriesEnvironment(SimulationEnvironment):
    """Simulation environment for time series data scenarios."""
    
    def __init__(self, config: DataSimulationConfig):
        super().__init__(config)
        self.data = None
        
    def generate_data(
        self, 
        start_date: str = "2022-01-01",
        freq: str = "D",
        n_series: int = 1
    ) -> pd.DataFrame:
        """Generate synthetic time series data."""
        config = self.config
        n_samples = config.dataset_size
        
        # Create date range
        date_rng = pd.date_range(start=start_date, periods=n_samples, freq=freq)
        
        # Initialize DataFrame
        df = pd.DataFrame(date_rng, columns=['date'])
        
        # Generate multiple time series if needed
        for i in range(n_series):
            series_name = f"series_{i}" if n_series > 1 else "value"
            
            # Base signal - combination of trend, seasonality, and noise
            trend = np.linspace(0, 1, n_samples) * np.random.uniform(0, 5)
            
            # Multiple seasonality components with different frequencies
            season1 = np.sin(np.linspace(0, n_samples/10*2*np.pi, n_samples)) * np.random.uniform(1, 3)
            season2 = np.sin(np.linspace(0, n_samples/100*2*np.pi, n_samples)) * np.random.uniform(0.5, 2)
            
            # Random noise
            noise_level = config.noise_level
            noise = np.random.normal(0, noise_level, n_samples)
            
            # Combine components
            signal = trend + season1 + season2 + noise
            
            # Add the series to the DataFrame
            df[series_name] = signal
            
            # Add outliers if specified
            if config.outlier_prob > 0:
                outlier_mask = np.random.random(n_samples) < config.outlier_prob
                outlier_indices = np.where(outlier_mask)[0]
                for idx in outlier_indices:
                    df.loc[idx, series_name] = signal.mean() + signal.std() * np.random.choice([-10, 10])
            
            # Add missing values if specified
            if config.missing_data_prob > 0:
                missing_mask = np.random.random(n_samples) < config.missing_data_prob
                df.loc[missing_mask, series_name] = np.nan
                
        # If need to create concept drift
        if config.drift_rate > 0:
            # Apply drift gradually after a certain point
            drift_start = int(n_samples * 0.7)  # Start drift at 70% of the series
            drift_factor = np.linspace(0, config.drift_rate * 3, n_samples - drift_start)
            
            for i in range(n_series):
                series_name = f"series_{i}" if n_series > 1 else "value"
                df.loc[drift_start:, series_name] += drift_factor
        
        self.data = df
        return df
    
    def run(self) -> Dict:
        """Run the time series simulation."""
        self.start()
        
        # Generate time series data
        data = self.generate_data(n_series=3)  # Generate 3 related time series
        self.logger.info(f"Generated time series with shape {data.shape}")
        
        # Split into train/test
        train_size = int(len(data) * 0.8)
        train_data = data.iloc[:train_size].reset_index(drop=True)
        test_data = data.iloc[train_size:].reset_index(drop=True)
        
        # Save artifacts
        self.save_artifact("full_timeseries", data)
        self.save_artifact("train_timeseries", train_data)
        self.save_artifact("test_timeseries", test_data)
        
        # Visualize the time series
        fig, ax = plt.subplots(figsize=(12, 6))
        for col in data.columns:
            if col != 'date':
                ax.plot(data['date'], data[col], label=col)
        
        ax.set_title("Simulated Time Series")
        ax.set_xlabel("Date")
        ax.set_ylabel("Value")
        ax.legend()
        self.save_artifact("timeseries_plot", fig)
        plt.close(fig)
        
        self.stop()
        return self.generate_report()


class NLPEnvironment(SimulationEnvironment):
    """Simulation environment for natural language processing scenarios."""
    
    def __init__(self, config: DataSimulationConfig):
        super().__init__(config)
        self.data = None
        
    def generate_data(self, vocab_size: int = 5000) -> pd.DataFrame:
        """Generate synthetic text data for NLP tasks."""
        config = self.config
        n_samples = config.dataset_size
        n_classes = config.class_count
        
        # Create a vocabulary of random words (using random strings for simplicity)
        import string
        import random
        
        def random_word(length=None):
            if length is None:
                length = random.randint(3, 10)
            return ''.join(random.choice(string.ascii_lowercase) for _ in range(length))
        
        vocabulary = [random_word() for _ in range(vocab_size)]
        
        # Generate texts with different characteristics for different classes
        texts = []
        labels = []
        
        for i in range(n_samples):
            if n_classes > 0:
                label = random.randint(0, n_classes - 1)
            else:
                label = None
                
            # Vary text length by class
            if label is not None:
                base_length = 10 + label * 5  # Class 0: ~10 words, Class 1: ~15 words, etc.
            else:
                base_length = 15
                
            length = max(3, int(random.gauss(base_length, base_length / 4)))
            
            # Generate a text by sampling from vocabulary
            # Make certain words more likely depending on the class
            if label is not None:
                # Each class has some "characteristic" words
                class_vocab_start = (label * vocab_size // n_classes) % vocab_size
                class_vocab_end = ((label + 1) * vocab_size // n_classes) % vocab_size
                class_vocabulary = vocabulary[class_vocab_start:class_vocab_end]
                
                # Mix general vocabulary with class-specific vocabulary
                text_words = []
                for _ in range(length):
                    if random.random() < 0.3:  # 30% chance of class-specific word
                        word = random.choice(class_vocabulary)
                    else:
                        word = random.choice(vocabulary)
                    text_words.append(word)
            else:
                text_words = [random.choice(vocabulary) for _ in range(length)]
                
            text = ' '.join(text_words)
            
            # Add noise if specified
            if config.noise_level > 0:
                # Introduce typos, deletions, insertions
                chars = list(text)
                n_errors = int(len(chars) * config.noise_level)
                for _ in range(n_errors):
                    error_type = random.choice(['typo', 'deletion', 'insertion'])
                    pos = random.randint(0, len(chars) - 1)
                    
                    if error_type == 'typo' and chars[pos] != ' ':
                        chars[pos] = random.choice(string.ascii_lowercase)
                    elif error_type == 'deletion':
                        chars.pop(pos)
                    elif error_type == 'insertion':
                        chars.insert(pos, random.choice(string.ascii_lowercase))
                
                text = ''.join(chars)
            
            texts.append(text)
            labels.append(label)
        
        # Create DataFrame
        df = pd.DataFrame({
            'text': texts,
            'target': labels
        })
        
        self.data = df
        return df
    
    def run(self) -> Dict:
        """Run the NLP simulation."""
        self.start()
        
        # Generate NLP data
        data = self.generate_data()
        self.logger.info(f"Generated NLP dataset with {len(data)} samples")
        
        # Split into train/test
        indices = np.random.permutation(len(data))
        train_idx = indices[:int(0.8 * len(indices))]
        test_idx = indices[int(0.8 * len(indices)):]
        
        train_data = data.iloc[train_idx].reset_index(drop=True)
        test_data = data.iloc[test_idx].reset_index(drop=True)
        
        # Save artifacts
        self.save_artifact("nlp_dataset", data)
        self.save_artifact("train_nlp", train_data)
        self.save_artifact("test_nlp", test_data)
        
        # Log metrics
        self.log_metric("dataset_size", len(data))
        self.log_metric("avg_text_length", data['text'].str.len().mean())
        self.log_metric("unique_words", len(set(' '.join(data['text']).split())))
        
        # Visualize text length distribution
        fig, ax = plt.subplots(figsize=(10, 6))
        data['text_length'] = data['text'].str.len()
        sns.histplot(data['text_length'], ax=ax)
        ax.set_title("Text Length Distribution")
        ax.set_xlabel("Length (characters)")
        self.save_artifact("text_length_dist", fig)
        plt.close(fig)
        
        self.stop()
        return self.generate_report()


# -----------------------------------------------------------------------------
# Model Simulation Framework
# -----------------------------------------------------------------------------

class ModelSimulator:
    """Simulates model performance under various conditions."""
    
    def __init__(self, 
                 model_factory: Callable,
                 environment: SimulationEnvironment,
                 config: ModelSimulationConfig):
        self.model_factory = model_factory
        self.environment = environment
        self.config = config
        self.model = None
        self.logger = logging.getLogger(f"model_simulator.{self.__class__.__name__}")
        
    def train_model(self, train_data: pd.DataFrame, target_col: str = 'target') -> Any:
        """Train a model on the given data."""
        X = train_data.drop(columns=[target_col])
        y = train_data[target_col]
        
        self.logger.info(f"Training model with {len(X)} samples")
        model = self.model_factory(**self.config.model_params)
        model.fit(X, y)
        
        self.model = model
        return model
    
    def evaluate_model(self, test_data: pd.DataFrame, target_col: str = 'target') -> Dict[str, float]:
        """Evaluate the model on test data."""
        if self.model is None:
            raise ValueError("Model must be trained before evaluation")
            
        X_test = test_data.drop(columns=[target_col])
        y_test = test_data[target_col]
        
        self.logger.info(f"Evaluating model on {len(X_test)} samples")
        
        # Make predictions
        y_pred = self.model.predict(X_test)
        
        # Calculate metrics based on problem type
        metrics = {}
        
        if self.config.model_type == 'classifier':
            # Classification metrics
            metrics['accuracy'] = accuracy_score(y_test, y_pred)
            metrics['precision'] = precision_score(y_test, y_pred, average='weighted')
            metrics['recall'] = recall_score(y_test, y_pred, average='weighted')
            metrics['f1'] = f1_score(y_test, y_pred, average='weighted')
        else:
            # Regression metrics
            metrics['mse'] = mean_squared_error(y_test, y_pred)
            metrics['mae'] = mean_absolute_error(y_test, y_pred)
            metrics['r2'] = r2_score(y_test, y_pred)
            
        return metrics
    
    def simulate_performance_degradation(
        self, 
        test_data: pd.DataFrame,
        target_col: str = 'target',
        degradation_types: List[str] = ['noise', 'missing', 'drift'],
        severity_levels: List[float] = [0.1, 0.3, 0.5]
    ) -> Dict[str, Dict[str, float]]:
        """Simulate model performance under various degradation scenarios."""
        if self.model is None:
            raise ValueError("Model must be trained before simulation")
            
        results = {}
        
        # Baseline performance (no degradation)
        baseline_metrics = self.evaluate_model(test_data, target_col)
        results['baseline'] = baseline_metrics
        
        X_test = test_data.drop(columns=[target_col])
        y_test = test_data[target_col]
        
        # Simulate different types of degradation
        for deg_type in degradation_types:
            for severity in severity_levels:
                scenario_name = f"{deg_type}_{severity}"
                self.logger.info(f"Simulating {scenario_name} degradation")
                
                # Create degraded test set based on type
                if deg_type == 'noise':
                    # Add noise to features
                    X_degraded = X_test.copy()
                    for col in X_degraded.columns:
                        if np.issubdtype(X_degraded[col].dtype, np.number):
                            noise = np.random.normal(0, X_degraded[col].std() * severity, size=len(X_degraded))
                            X_degraded[col] += noise
                            
                elif deg_type == 'missing':
                    # Introduce missing values
                    X_degraded = X_test.copy()
                    mask = np.random.random(X_degraded.shape) < severity
                    X_degraded = X_degraded.mask(mask)
                    
                    # Simple imputation for evaluation
                    for col in X_degraded.columns:
                        if X_degraded[col].isna().any():
                            if np.issubdtype(X_degraded[col].dtype, np.number):
                                X_degraded[col].fillna(X_degraded[col].mean(), inplace=True)
                            else:
                                X_degraded[col].fillna(X_degraded[col].mode()[0], inplace=True)
                            
                elif deg_type == 'drift':
                    # Concept drift - shift in feature distributions
                    X_degraded = X_test.copy()
                    for col in X_degraded.columns:
                        if np.issubdtype(X_degraded[col].dtype, np.number):
                            # Shift the mean and potentially the variance
                            shift = X_degraded[col].mean() * severity
                            scale = 1 + severity
                            X_degraded[col] = (X_degraded[col] + shift) * scale
                else:
                    continue
                
                # Evaluate on degraded data
                y_pred = self.model.predict(X_degraded)
                
                # Calculate metrics
                metrics = {}
                if self.config.model_type == 'classifier':
                    metrics['accuracy'] = accuracy_score(y_test, y_pred)
                    metrics['precision'] = precision_score(y_test, y_pred, average='weighted')
                    metrics['recall'] = recall_score(y_test, y_pred, average='weighted')
                    metrics['f1'] = f1_score(y_test, y_pred, average='weighted')
                else:
                    metrics['mse'] = mean_squared_error(y_test, y_pred)
                    metrics['mae'] = mean_absolute_error(y_test, y_pred)
                    metrics['r2'] = r2_score(y_test, y_pred)
                
                results[scenario_name] = metrics
        
        return results
    
    def simulate_adversarial_cases(
        self,
        test_data: pd.DataFrame,
        target_col: str = 'target',
        epsilon: float = 0.1
    ) -> Dict[str, float]:
        """Simulate simple adversarial attacks on the model."""
        if self.model is None:
            raise ValueError("Model must be trained before simulation")
            
        X_test = test_data.drop(columns=[target_col])
        y_test = test_data[target_col]
        
        self.logger.info(f"Simulating adversarial examples with epsilon={epsilon}")
        
        # Get baseline predictions
        y_pred_baseline = self.model.predict(X_test)
        baseline_correct = (y_pred_baseline == y_test)
        correct_indices = np.where(baseline_correct)[0]
        
        if len(correct_indices) == 0:
            self.logger.warning("No correct predictions found for adversarial simulation")
            return {}
            
        # Select a subset of correctly classified examples for adversarial generation
        sample_size = min(100, len(correct_indices))
        selected_indices = np.random.choice(correct_indices, sample_size, replace=False)
        
        X_selected = X_test.iloc[selected_indices].copy()
        y_selected = y_test.iloc[selected_indices]
        
        # Simple adversarial perturbation (not targeted, just random perturbation)
        X_adversarial = X_selected.copy()
        
        for col in X_adversarial.columns:
            if np.issubdtype(X_adversarial[col].dtype, np.number):
                # Apply small perturbation scaled by feature standard deviation
                std = X_test[col].std()
                perturbation = np.random.uniform(-epsilon * std, epsilon * std, size=len(X_adversarial))
                X_adversarial[col] += perturbation
        
        # Evaluate on adversarial examples
        y_pred_adversarial = self.model.predict(X_adversarial)
        
        # Calculate adversarial success rate (how often predictions changed)
        changed_predictions = (y_pred_adversarial != y_selected)
        adversarial_success_rate = changed_predictions.mean()
        
        # Calculate metrics on adversarial examples
        if self.config.model_type == 'classifier':
            adv_accuracy = accuracy_score(y_selected, y_pred_adversarial)
            adv_f1 = f1_score(y_selected, y_pred_adversarial, average='weighted')
            
            metrics = {
                'adversarial_success_rate': adversarial_success_rate,
                'adversarial_accuracy': adv_accuracy,
                'adversarial_f1': adv_f1,
                'accuracy_drop': 1.0 - adv_accuracy  # Since we started with 100% accuracy on this subset
            }
        else:
            adv_mse = mean_squared_error(y_selected, y_pred_adversarial)
            baseline_mse = mean_squared_error(y_selected, y_selected)  # Should be 0
            
            metrics = {
                'adversarial_success_rate': adversarial_success_rate,
                'adversarial_mse': adv_mse,
                'mse_increase': adv_mse - baseline_mse
            }
            
        return metrics
    
    def run_simulation(self) -> Dict:
        """Run a complete model simulation workflow."""
        self.logger.info(f"Starting model simulation: {self.config.name}")
        start_time = time.time()
        
        results = {
            "config": self.config.to_dict(),
            "metrics": {},
            "degradation_results": {},
            "adversarial_results": {}
        }
        
        # Generate or get data from environment
        if hasattr(self.environment, 'generate_train_test_sets'):
            train_data, test_data = self.environment.generate_train_test_sets(add_drift_to_test=False)
        else:
            # Assume data is already available in the environment
            train_size = int(0.8 * len(self.environment.data))
            train_data = self.environment.data.iloc[:train_size]
            test_data = self.environment.data.iloc[train_size:]
        
        # Train the model
        self.train_model(train_data)
        
        # Standard evaluation
        evaluation_metrics = self.evaluate_model(test_data)
        results["metrics"] = evaluation_metrics
        
        # Degradation simulation
        degradation_results = self.simulate_performance_degradation(test_data)
        results["degradation_results"] = degradation_results
        
        # Adversarial testing
        if self.config.model_type == 'classifier':
            adversarial_results = self.simulate_adversarial_cases(test_data)
            results["adversarial_results"] = adversarial_results
        
        # Calculate elapsed time
        elapsed_time = time.time() - start_time
        results["elapsed_time"] = elapsed_time
        
        self.logger.info(f"Model simulation completed in {elapsed_time:.2f} seconds")
        return results


# -----------------------------------------------------------------------------
# Data Pipeline Simulation
# -----------------------------------------------------------------------------

class PipelineStage:
    """Base class for a stage in a data pipeline simulation."""
    
    def __init__(self, name: str, failure_prob: float = 0.0, latency_mean: float = 0.1):
        self.name = name
        self.failure_prob = failure_prob
        self.latency_mean = latency_mean
        self.logger = logging.getLogger(f"pipeline.{name}")
        self.metrics = {"calls": 0, "failures": 0, "latency": []}
        
    def process(self, data: Any, context: Dict = None) -> Tuple[Any, Dict]:
        """Process the data through this pipeline stage."""
        if context is None:
            context = {}
            
        self.metrics["calls"] += 1
        
        # Simulate latency
        latency = np.random.exponential(self.latency_mean)
        time.sleep(latency)
        self.metrics["latency"].append(latency)
        
        # Simulate potential failure
        if np.random.random() < self.failure_prob:
            self.metrics["failures"] += 1
        
        return data, context
    
    def get_metrics(self) -> Dict:
        """Get the metrics for this pipeline stage."""
        return {
            "failure_rate": self.metrics["failures"] / max(1, self.metrics["calls"]),
            "avg_latency": np.mean(self.metrics["latency"]),
            "max_latency": max(self.metrics["latency"])
        }


class DataLoadStage(PipelineStage):
    """Pipeline stage for loading data."""
    
    def process(self, data: Any, context: Dict = None) -> Tuple[Any, Dict]:
        """Load data for processing."""
        data, context = super().process(data, context)
        
        self.logger.info(f"Loading data in {self.name}")
        
        # If data is None, create a simple synthetic dataset
        if data is None:
            n_samples = context.get("n_samples", 1000)
            n_features = context.get("n_features", 10)
            
            # Generate random features
            X = np.random.randn(n_samples, n_features)
            
            # Generate random target
            if context.get("task", "classification") == "classification":
                n_classes = context.get("n_classes", 2)
                y = np.random.randint(0, n_classes, size=n_samples)
            else:
                y = np.random.randn(n_samples)
                
            data = {
                "X": X,
                "y": y,
                "feature_names": [f"feature_{i}" for i in range(n_features)]
            }
            
            self.logger.info(f"Generated synthetic dataset with {n_samples} samples and {n_features} features")
        
        # Record data loading time in context
        context["data_loaded_at"] = datetime.now().isoformat()
        
        return data, context


class DataPreprocessStage(PipelineStage):
    """Pipeline stage for preprocessing data."""
    
    def process(self, data: Any, context: Dict = None) -> Tuple[Any, Dict]:
        """Preprocess data for modeling."""
        data, context = super().process(data, context)
        
        self.logger.info(f"Preprocessing data in {self.name}")
        
        # Check if we have data to preprocess
        if data is None or "X" not in data:
            raise SimulationError("No data available for preprocessing")
        
        X = data["X"]
        y = data["y"]
        
        # Apply simple preprocessing steps
        
        # 1. Handle missing values (if any)
        if isinstance(X, np.ndarray) and np.isnan(X).any():
            # Simple imputation with mean
            col_mean = np.nanmean(X, axis=0)
            inds = np.where(np.isnan(X))
            X[inds] = np.take(col_mean, inds[1])
            
        # 2. Standardize features (zero mean, unit variance)
        if context.get("standardize", True):
            mean = np.mean(X, axis=0)
            std = np.std(X, axis=0)
            std[std == 0] = 1  # Prevent division by zero
            X = (X - mean) / std
            
            # Store normalization params for later use
            data["preprocessing"] = {
                "mean": mean,
                "std": std
            }
        
        # Update the data
        data["X"] = X
        data["y"] = y
        
        # Record preprocessing time in context
        context["preprocessed_at"] = datetime.now().isoformat()
        
        return data, context


class ModelTrainStage(PipelineStage):
    """Pipeline stage for training a model."""
    
    def __init__(self, name: str, failure_prob: float = 0.0, latency_mean: float = 0.1, model_factory: Callable = None, model_params: Dict = None):
        super().__init__(name, failure_prob, latency_mean)
        self.model_factory = model_factory
        self.model_params = model_params or {}
    
    def process(self, data: Any, context: Dict = None) -> Tuple[Any, Dict]:
        """Train a model on the given data."""
        data, context = super().process(data, context)
        
        self.logger.info(f"Training model in {self.name}")
        
        # Extract data components
        X = data["X"]
        y = data["y"]
        
        # Allow model factory to be provided in context
        model_factory = self.model_factory or context.get("model_factory")
        if model_factory is None:
            # Default to a simple sklearn-like API 
            class DummyModel:
                def __init__(self, **kwargs):
                    self.coef_ = None
                
                def fit(self, X, y):
                    # Simulate training time based on data size
                    time.sleep(0.001 * X.shape[0] * X.shape[1])
                    # Simulate learning some coefficients
                    self.coef_ = np.random.randn(X.shape[1])
                    return self
                
                def predict(self, X):
                    if isinstance(y, np.ndarray) and np.issubdtype(y.dtype, np.integer):
                        # Classification
                        return np.random.randint(0, np.max(y) + 1, size=X.shape[0])
                    else:
                        # Regression
                        return X.dot(self.coef_)
            
            model_factory = DummyModel
            
        # Create and train the model
        model_params = {**self.model_params, **context.get("model_params", {})}
        model = model_factory(**model_params)
        
        # Simulate training
        model.fit(X, y)
        
        # Update the data with the trained model
        data["model"] = model
        
        context["trained_at"] = datetime.now().isoformat()
        return data, context


class ModelEvaluationStage(PipelineStage):
    """Pipeline stage for evaluating a model."""
    
    def process(self, data: Any, context: Dict = None) -> Tuple[Any, Dict]:
        """Evaluate a trained model."""
        data, context = super().process(data, context)
        
        self.logger.info(f"Evaluating model in {self.name}")
        
        # Extract model and data
        model = data.get("model")
        if model is None:
            raise SimulationError("No model found in data for evaluation")
            
        X = data["X"]
        y = data["y"]
        
        # Simulate train/test split if not already done
        if "X_test" not in data:
            # Use a simple 80/20 split
            split_idx = int(0.8 * len(X))
            indices = np.random.permutation(len(X))
            
            train_idx, test_idx = indices[:split_idx], indices[split_idx:]
            X_train, X_test = X[train_idx], X[test_idx]
            y_train, y_test = y[train_idx], y[test_idx]
            
            data["X_train"], data["X_test"] = X_train, X_test
            data["y_train"], data["y_test"] = y_train, y_test
        else:
            X_test = data["X_test"]
            y_test = data["y_test"]
        
        # Make predictions
        y_pred = model.predict(X_test)
        
        # Calculate metrics
        metrics = {}
        if isinstance(y, np.ndarray) and np.issubdtype(y.dtype, np.integer):
            # Classification metrics
            metrics["accuracy"] = accuracy_score(y_test, y_pred)
            try:
                metrics["precision"] = precision_score(y_test, y_pred, average='weighted')
                metrics["recall"] = recall_score(y_test, y_pred, average='weighted')
                metrics["f1"] = f1_score(y_test, y_pred, average='weighted')
            except Exception as e:
                self.logger.warning(f"Could not calculate all classification metrics: {str(e)}")
        else:
            # Regression metrics
            metrics["mse"] = mean_squared_error(y_test, y_pred)
            metrics["mae"] = mean_absolute_error(y_test, y_pred)
            metrics["r2"] = r2_score(y_test, y_pred)
        
        # Store evaluation results
        data["evaluation_metrics"] = metrics
        context["evaluated_at"] = datetime.now().isoformat()
        
        return data, context


class ModelPredictionStage(PipelineStage):
    """Pipeline stage for making predictions with a model."""
    
    def process(self, data: Any, context: Dict = None) -> Tuple[Any, Dict]:
        """Make predictions with a trained model."""
        data, context = super().process(data, context)
        
        self.logger.info(f"Making predictions in {self.name}")
        
        # Extract model and data
        model = data.get("model")
        if model is None:
            raise SimulationError("No model found in data for prediction")
            
        # Check if we have prediction data
        X_pred = data.get("X_pred")
        if X_pred is None:
            # Use test data if available, otherwise use training data
            X_pred = data.get("X_test", data.get("X"))
            
        # Make predictions
        y_pred = model.predict(X_pred)
        
        # Store predictions
        data["predictions"] = y_pred
        context["predicted_at"] = datetime.now().isoformat()
        
        return data, context


class PipelineSimulator:
    """Simulates a complete ML pipeline with multiple stages."""
    
    def __init__(self, config: PipelineSimulationConfig, stages: List[PipelineStage] = None):
        self.config = config
        self.stages = stages or []
        self.logger = logging.getLogger("pipeline_simulator")
        self.metrics = {}
        
    def add_stage(self, stage: PipelineStage) -> None:
        """Add a stage to the pipeline."""
        self.stages.append(stage)
        
    def run(self, initial_data: Any = None, context: Dict = None) -> Tuple[Any, Dict]:
        """Run the complete pipeline simulation."""
        if context is None:
            context = {}
            
        data = initial_data
        context["pipeline_started"] = datetime.now().isoformat()
        
        self.logger.info(f"Starting pipeline simulation with {len(self.stages)} stages")
        
        # Process each stage
        for i, stage in enumerate(self.stages):
            stage_name = stage.name
            self.logger.info(f"Running stage {i+1}/{len(self.stages)}: {stage_name}")
            
            try:
                data, context = stage.process(data, context)
                self.logger.info(f"Stage {stage_name} completed successfully")
            except SimulationError as e:
                self.logger.error(f"Stage {stage_name} failed: {str(e)}")
                context["pipeline_error"] = str(e)
                context["failed_stage"] = stage_name
                break
            except Exception as e:
                self.logger.error(f"Unexpected error in stage {stage_name}: {str(e)}")
                context["pipeline_error"] = str(e)
                context["failed_stage"] = stage_name
                break
                
        # Calculate pipeline metrics
        self.metrics = {
            "pipeline_success": "pipeline_error" not in context,
            "stages_completed": i + 1 if "pipeline_error" not in context else i,
            "total_stages": len(self.stages),
            "stage_metrics": {stage.name: stage.get_metrics() for stage in self.stages}
        }
        
        context["pipeline_metrics"] = self.metrics
        context["pipeline_completed"] = datetime.now().isoformat()
        
        return data, context


# -----------------------------------------------------------------------------
# End-to-End System Testing
# -----------------------------------------------------------------------------

class MLSystemSimulator:
    """Simulates an end-to-end ML system with data, training, and serving components."""
    
    def __init__(self, config: SimulationConfig):
        self.config = config
        self.logger = logging.getLogger("ml_system_simulator")
        self.pipeline_simulator = None
        self.environment = None
        self.model_simulator = None
        
    def configure_data_environment(self, environment_type: str = "tabular", **kwargs) -> SimulationEnvironment:
        """Configure the data environment for the simulation."""
        config_dict = {
            "name": f"{self.config.name}_data_env",
            "description": f"Data environment for {self.config.name}",
            "seed": self.config.seed,
            "output_dir": os.path.join(self.config.output_dir, "data_environment"),
            **kwargs
        }
        
        data_config = DataSimulationConfig(**config_dict)
        
        if environment_type.lower() == "tabular":
            self.environment = TabularDataEnvironment(data_config)
        elif environment_type.lower() == "timeseries":
            self.environment = TimeSeriesEnvironment(data_config)
        elif environment_type.lower() == "nlp":
            self.environment = NLPEnvironment(data_config)
        else:
            raise ValueError(f"Unknown environment type: {environment_type}")
            
        return self.environment
    
    def configure_model_simulator(self, model_factory: Callable, **kwargs) -> ModelSimulator:
        """Configure the model simulator for the simulation."""
        if self.environment is None:
            raise ValueError("Data environment must be configured before model simulator")
            
        config_dict = {
            "name": f"{self.config.name}_model_sim",
            "description": f"Model simulator for {self.config.name}",
            "seed": self.config.seed,
            "output_dir": os.path.join(self.config.output_dir, "model_simulator"),
            **kwargs
        }
        
        model_config = ModelSimulationConfig(**config_dict)
        self.model_simulator = ModelSimulator(model_factory, self.environment, model_config)
        
        return self.model_simulator
    
    def configure_pipeline_simulator(self, stage_configs: List[Dict] = None) -> PipelineSimulator:
        """Configure the pipeline simulator with specified stages."""
        config_dict = {
            "name": f"{self.config.name}_pipeline_sim",
            "description": f"Pipeline simulator for {self.config.name}",
            "seed": self.config.seed,
            "output_dir": os.path.join(self.config.output_dir, "pipeline_simulator"),
            "stages": [cfg.get("name", f"stage_{i}") for i, cfg in enumerate(stage_configs or [])]
        }
        
        pipeline_config = PipelineSimulationConfig(**config_dict)
        
        # Create pipeline stages based on configurations
        stages = []
        if stage_configs:
            for cfg in stage_configs:
                stage_type = cfg.pop("type", "base")
                stage_name = cfg.pop("name", f"stage_{len(stages)}")
                
                if stage_type == "data_load":
                    stages.append(DataLoadStage(stage_name, **cfg))
                elif stage_type == "preprocess":
                    stages.append(DataPreprocessStage(stage_name, **cfg))
                elif stage_type == "train":
                    stages.append(ModelTrainStage(stage_name, **cfg))
                elif stage_type == "evaluate":
                    stages.append(ModelEvaluationStage(stage_name, **cfg))
                elif stage_type == "predict":
                    stages.append(ModelPredictionStage(stage_name, **cfg))
                else:
                    stages.append(PipelineStage(stage_name, **cfg))
        
        self.pipeline_simulator = PipelineSimulator(pipeline_config, stages)
        return self.pipeline_simulator
    
    def run_end_to_end_simulation(self) -> Dict:
        """Run a complete end-to-end ML system simulation."""
        results = {
            "config": self.config.to_dict(),
            "timestamp": datetime.now().isoformat(),
            "components": {}
        }
        
        # 1. Generate data if environment is configured
        if self.environment:
            self.logger.info("Running data environment simulation")
            env_results = self.environment.run()
            results["components"]["data_environment"] = env_results
            
        # 2. Run model simulation if configured
        if self.model_simulator:
            self.logger.info("Running model simulation")
            model_results = self.model_simulator.run_simulation()
            results["components"]["model_simulator"] = model_results
            
        # 3. Run pipeline simulation if configured
        if self.pipeline_simulator:
            self.logger.info("Running pipeline simulation")
            
            # Initialize with data from environment if available
            initial_data = None
            if self.environment and hasattr(self.environment, 'data') and self.environment.data is not None:
                # Convert DataFrame to the format expected by pipeline
                df = self.environment.data
                X = df.drop(columns=['target']).values
                y = df['target'].values
                
                initial_data = {
                    "X": X,
                    "y": y,
                    "feature_names": df.drop(columns=['target']).columns.tolist()
                }
                
            # Run the pipeline
            final_data, context = self.pipeline_simulator.run(initial_data)
            
            # Collect results
            pipeline_results = {
                "pipeline_metrics": self.pipeline_simulator.metrics,
                "context": context
            }
            
            if "evaluation_metrics" in final_data:
                pipeline_results["evaluation_metrics"] = final_data["evaluation_metrics"]
                
            results["components"]["pipeline_simulator"] = pipeline_results
            
        # Generate overall success/failure status
        results["success"] = all(
            comp.get("success", True) 
            for comp in results["components"].values()
        )
        
        return results


# -----------------------------------------------------------------------------
# Reporting and Visualization
# -----------------------------------------------------------------------------

class SimulationReporter:
    """Generates reports and visualizations for simulation results."""
    
    def __init__(self, output_dir: str = "simulation_reports"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.logger = logging.getLogger("simulation_reporter")
        
    def generate_model_performance_report(self, model_results: Dict) -> Dict:
        """Generate a report on model performance across degradation scenarios."""
        report = {
            "baseline_metrics": model_results.get("metrics", {}),
            "degradation_impact": {},
            "adversarial_impact": model_results.get("adversarial_results", {})
        }
        
        # Calculate impact of each degradation scenario
        baseline = report["baseline_metrics"]
        for scenario, metrics in model_results.get("degradation_results", {}).items():
            if scenario == "baseline":
                continue
                
            # Calculate relative changes for each metric
            impact = {}
            for metric, value in metrics.items():
                if metric in baseline and baseline[metric] != 0:
                    rel_change = (value - baseline[metric]) / baseline[metric]
                    impact[f"{metric}_change"] = rel_change
                    
            report["degradation_impact"][scenario] = impact
            
        # Generate visualizations
        self._visualize_model_degradation(model_results)
        
        return report
    
    def _visualize_model_degradation(self, model_results: Dict) -> None:
        """Create visualizations for model degradation scenarios."""
        degradation_results = model_results.get("degradation_results", {})
        if not degradation_results:
            return
            
        # Extract degradation types and metrics
        scenarios = list(degradation_results.keys())
        if "baseline" in scenarios:
            scenarios.remove("baseline")
            
        if not scenarios:
            return
            
        # Get metric names from first scenario
        first_scenario = next(iter(degradation_results.values()))
        metrics = list(first_scenario.keys())
        
        # Prepare data for plotting
        for metric in metrics:
            # Create figure
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Group by degradation type
            degradation_types = set(s.split('_')[0] for s in scenarios)
            
            for deg_type in degradation_types:
                # Get scenarios of this type
                type_scenarios = [s for s in scenarios if s.startswith(deg_type)]
                
                # Sort by severity
                type_scenarios.sort(key=lambda s: float(s.split('_')[1]))
                
                # Extract severity levels and corresponding metric values
                severities = [float(s.split('_')[1]) for s in type_scenarios]
                values = [degradation_results[s][metric] for s in type_scenarios]
                
                # Plot this degradation type
                ax.plot(severities, values, marker='o', label=deg_type)
                
            # Add baseline as horizontal line
            if "baseline" in degradation_results and metric in degradation_results["baseline"]:
                baseline_value = degradation_results["baseline"][metric]
                ax.axhline(y=baseline_value, color='r', linestyle='--', label='baseline')
                
            # Add labels and legend
            ax.set_xlabel("Degradation Severity")
            ax.set_ylabel(metric)
            ax.set_title(f"Impact of Data Degradation on {metric}")
            ax.legend()
            
            # Save figure
            filepath = os.path.join(self.output_dir, f"degradation_impact_{metric}.png")
            fig.savefig(filepath)
            plt.close(fig)
    
    def generate_pipeline_report(self, pipeline_results: Dict) -> Dict:
        """Generate a report on pipeline performance."""
        pipeline_metrics = pipeline_results.get("pipeline_metrics", {})
        
        report = {
            "success_rate": pipeline_metrics.get("pipeline_success", False),
            "stages_completed": pipeline_metrics.get("stages_completed", 0),
            "total_stages": pipeline_metrics.get("total_stages", 0),
            "completion_rate": pipeline_metrics.get("stages_completed", 0) / 
                               max(1, pipeline_metrics.get("total_stages", 1)),
            "stage_metrics": {}
        }
        
        # Process stage metrics
        for stage_name, metrics in pipeline_metrics.get("stage_metrics", {}).items():
            report["stage_metrics"][stage_name] = {
                "failure_rate": metrics.get("failure_rate", 0),
                "avg_latency": metrics.get("avg_latency", 0),
                "max_latency": metrics.get("max_latency", 0)
            }
            
        # Visualize pipeline performance
        self._visualize_pipeline_performance(pipeline_results)
        
        return report
    
    def _visualize_pipeline_performance(self, pipeline_results: Dict) -> None:
        """Create visualizations for pipeline performance."""
        pipeline_metrics = pipeline_results.get("pipeline_metrics", {})
        stage_metrics = pipeline_metrics.get("stage_metrics", {})
        
        if not stage_metrics:
            return
            
        # Create latency visualization
        fig, ax = plt.subplots(figsize=(12, 6))
        
        stages = list(stage_metrics.keys())
        avg_latencies = [metrics.get("avg_latency", 0) for metrics in stage_metrics.values()]
        max_latencies = [metrics.get("max_latency", 0) for metrics in stage_metrics.values()]
        
        x = np.arange(len(stages))
        width = 0.35
        
        ax.bar(x - width/2, avg_latencies, width, label='Average Latency')
        ax.bar(x + width/2, max_latencies, width, label='Max Latency')
        
        ax.set_xlabel('Pipeline Stage')
        ax.set_ylabel('Latency (seconds)')
        ax.set_title('Pipeline Stage Latencies')
        ax.set_xticks(x)
        ax.set_xticklabels(stages, rotation=45, ha='right')
        ax.legend()
        
        fig.tight_layout()
        filepath = os.path.join(self.output_dir, "pipeline_latencies.png")
        fig.savefig(filepath)
        plt.close(fig)
        
        # Create failure rate visualization
        fig, ax = plt.subplots(figsize=(12, 6))
        
        failure_rates = [metrics.get("failure_rate", 0) for metrics in stage_metrics.values()]
        
        ax.bar(x, failure_rates)
        
        ax.set_xlabel('Pipeline Stage')
        ax.set_ylabel('Failure Rate')
        ax.set_title('Pipeline Stage Failure Rates')
        ax.set_xticks(x)
        ax.set_xticklabels(stages, rotation=45, ha='right')
        
        fig.tight_layout()
        filepath = os.path.join(self.output_dir, "pipeline_failure_rates.png")
        fig.savefig(filepath)
        plt.close(fig)
        
    def generate_system_report(self, system_results: Dict) -> Dict:
        """Generate a comprehensive report on the full ML system simulation."""
        report = {
            "system_name": system_results.get("config", {}).get("name", "Unknown"),
            "timestamp": system_results.get("timestamp", datetime.now().isoformat()),
            "success": system_results.get("success", False),
            "components": {}
        }
        
        # Process each component's results
        components = system_results.get("components", {})
        
        # Data environment report
        if "data_environment" in components:
            data_env = components["data_environment"]
            report["components"]["data_environment"] = {
                "metrics": data_env.get("metrics", {}),
                "artifacts": data_env.get("artifacts", {})
            }
            
        # Model simulator report
        if "model_simulator" in components:
            model_sim = components["model_simulator"]
            model_report = self.generate_model_performance_report(model_sim)
            report["components"]["model_simulator"] = model_report
            
        # Pipeline simulator report
        if "pipeline_simulator" in components:
            pipeline_sim = components["pipeline_simulator"]
            pipeline_report = self.generate_pipeline_report(pipeline_sim)
            report["components"]["pipeline_simulator"] = pipeline_report
            
        # Save the report
        report_path = os.path.join(self.output_dir, f"{report['system_name']}_report.json")
        with open(report_path, 'w') as f:
            json.dump(report, f, cls=SimulationConfigEncoder, indent=2)
            
        return report


# -----------------------------------------------------------------------------
# Integration Components
# -----------------------------------------------------------------------------

class CIIntegration:
    """Integration with CI/CD workflows for ML simulation."""
    
    def __init__(self, config_path: str = "ci_simulation_config.json"):
        self.config_path = config_path
        self.logger = logging.getLogger("ci_integration")
        
    def load_config(self) -> SimulationConfig:
        """Load simulation configuration from CI config file."""
        try:
            return SimulationConfig.load(self.config_path)
        except Exception as e:
            self.logger.error(f"Failed to load CI configuration: {str(e)}")
            # Return default config
            return SimulationConfig(name="ci_default_simulation")
            
    def run_ci_simulation(self) -> Dict:
        """Run the simulation as part of CI process."""
        config = self.load_config()
        
        # Create system simulator
        simulator = MLSystemSimulator(config)
        
        # Configure components based on CI config
        simulator.configure_data_environment()
        
        # Use a dummy model for CI
        def dummy_model_factory(**kwargs):
            class DummyModel:
                def fit(self, X, y):
                    return self
                def predict(self, X):
                    return np.zeros(len(X))
            return DummyModel()
            
        simulator.configure_model_simulator(dummy_model_factory)
        
        # Run the simulation
        results = simulator.run_end_to_end_simulation()
        
        # Determine pass/fail status based on results
        ci_status = "passed" if results.get("success", False) else "failed"
        self.logger.info(f"CI simulation {ci_status}")
        
        return {
            "ci_status": ci_status,
            "results": results
        }


class PreCommitHook:
    """Pre-commit hook for running lightweight model simulations."""
    
    def __init__(self, config_path: str = "precommit_simulation_config.json"):
        self.config_path = config_path
        self.logger = logging.getLogger("precommit_hook")
        
    def run_precommit_check(self, changed_files: List[str]) -> Dict:
        """Run pre-commit check based on changed files."""
        # Determine what kinds of checks to run based on changed files
        run_model_check = any(f.endswith(".py") and "model" in f for f in changed_files)
        run_pipeline_check = any(f.endswith(".py") and "pipeline" in f for f in changed_files)
        
        results = {
            "changed_files": changed_files,
            "checks_run": [],
            "passed": True
        }
        
        if run_model_check:
            self.logger.info("Running model robustness check")
            model_result = self._run_quick_model_check()
            results["checks_run"].append("model_robustness")
            results["model_check"] = model_result
            results["passed"] &= model_result["passed"]
            
        if run_pipeline_check:
            self.logger.info("Running pipeline simulation check")
            pipeline_result = self._run_quick_pipeline_check()
            results["checks_run"].append("pipeline_simulation")
            results["pipeline_check"] = pipeline_result
            results["passed"] &= pipeline_result["passed"]
            
        return results
    
    def _run_quick_model_check(self) -> Dict:
        """Run a quick model robustness check."""
        # Create a simple environment with a small dataset
        config = DataSimulationConfig(
            name="precommit_model_check",
            dataset_size=500,  # Small dataset for speed
            feature_count=5
        )
        
        env = TabularDataEnvironment(config)
        env.generate_data()
        
        # Create a simple model simulator
        model_config = ModelSimulationConfig(
            name="precommit_model",
            model_type="classifier"
        )
        
        # Dummy model factory
        def dummy_model_factory(**kwargs):
            class DummyModel:
                def fit(self, X, y):
                    return self
                def predict(self, X):
                    return np.zeros(len(X))
            return DummyModel()
        
        simulator = ModelSimulator(dummy_model_factory, env, model_config)
        
        # Run limited degradation tests
        train_data, test_data = env.generate_train_test_sets()
        simulator.train_model(train_data)
        
        degradation_results = simulator.simulate_performance_degradation(
            test_data,
            degradation_types=['noise'],
            severity_levels=[0.5]
        )
        
        # Check if degradation is acceptable
        if 'noise_0.5' in degradation_results:
            baseline_acc = degradation_results.get('baseline', {}).get('accuracy', 1.0)
            degraded_acc = degradation_results.get('noise_0.5', {}).get('accuracy', 0.0)
            
            # Define passing threshold
            passed = (degraded_acc >= baseline_acc * 0.7)  # Allow 30% degradation
            
            return {
                "passed": passed,
                "baseline_accuracy": baseline_acc,
                "degraded_accuracy": degraded_acc,
                "acceptable_threshold": baseline_acc * 0.7
            }
        
        return {"passed": False, "error": "Failed to compute degradation metrics"}
    
    def _run_quick_pipeline_check(self) -> Dict:
        """Run a quick pipeline simulation check."""
        # Create a simple pipeline configuration
        config = PipelineSimulationConfig(
            name="precommit_pipeline_check",
            stages=["load", "preprocess", "train"]
        )
        
        # Create simple pipeline stages
        stages = [
            DataLoadStage("load", failure_prob=0.0),
            DataPreprocessStage("preprocess", failure_prob=0.1),
            ModelTrainStage("train", failure_prob=0.1)
        ]
        
        simulator = PipelineSimulator(config, stages)
        
        # Run the pipeline
        _, context = simulator.run()
        
        # Check if pipeline completed successfully
        passed = "pipeline_error" not in context
        
        return {
            "passed": passed,
            "pipeline_completed": simulator.metrics.get("stages_completed", 0),
            "total_stages": simulator.metrics.get("total_stages", 0),
            "error": context.get("pipeline_error")
        }


# -----------------------------------------------------------------------------
# Example usage
# -----------------------------------------------------------------------------

def run_example_simulation():
    """Run an example simulation to demonstrate the framework."""
    # Create configuration
    config = SimulationConfig(
        name="example_simulation",
        description="Example simulation to demonstrate the framework"
    )
    
    # Create system simulator
    system = MLSystemSimulator(config)
    
    # Configure data environment
    env = system.configure_data_environment(
        environment_type="tabular",
        dataset_size=5000,
        feature_count=10,
        noise_level=0.1,
        drift_rate=0.2
    )
    
    # Configure model simulator
    from sklearn.ensemble import RandomForestClassifier
    
    model_sim = system.configure_model_simulator(
        model_factory=RandomForestClassifier,
        model_type="classifier",
        model_params={"n_estimators": 100, "max_depth": 5}
    )
    
    # Configure pipeline simulator
    pipeline_stages = [
        {"type": "data_load", "name": "load_data", "failure_prob": 0.0},
        {"type": "preprocess", "name": "preprocess", "failure_prob": 0.1},
        {"type": "train", "name": "train_model", "failure_prob": 0.1},
        {"type": "evaluate", "name": "evaluate_model", "failure_prob": 0.0}
    ]
    
    pipeline_sim = system.configure_pipeline_simulator(pipeline_stages)
    
    # Run end-to-end simulation
    results = system.run_end_to_end_simulation()
    
    # Generate report
    reporter = SimulationReporter()
    report = reporter.generate_system_report(results)
    
    print(f"Simulation completed. Report saved to: {reporter.output_dir}")
    return report


if __name__ == "__main__":
    run_example_simulation()
