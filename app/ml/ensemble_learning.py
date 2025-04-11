from sklearn.decomposition import PCA
from sklearn.impute import KNNImputer
from sklearn.preprocessing import StandardScaler

from .models import ModelFactory
from .preprocessing import DataPreprocessor

import numpy as np
from typing import List, Dict, Any
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score

# Set a fixed random seed for reproducibility
RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)


class EnsembleModel:
    def __init__(self, n_estimators: int = 100, max_depth: int = 10):
        self.rf_model = RandomForestClassifier(
            n_estimators=n_estimators, max_depth=max_depth, random_state=RANDOM_SEED
        )
        self.gb_model = GradientBoostingClassifier(
            n_estimators=n_estimators, max_depth=max_depth, random_state=RANDOM_SEED
        )


class EnsembleLearner:
    """
    and handles missing data intelligently.
    """

    def __init__(self):
        self.model_factory = ModelFactory()
        self.preprocessor = DataPreprocessor()
        self.knn_imputer = KNNImputer(n_neighbors=5)
        self.scaler = StandardScaler()
        self.pca = PCA(n_components=0.95)  # Preserve 95% of variance

    def create_meta_model(
        self, input_shape: Tuple[int, ...], num_base_models: int = 3
    ) -> models.Model:
        """
        Create a meta-model that combines predictions from base models.
        """
        inputs = layers.Input(shape=(num_base_models,))
        x = layers.Dense(32, activation="relu")(inputs)
        x = layers.Dropout(0.2)(x)
        x = layers.Dense(16, activation="relu")(x)
        outputs = layers.Dense(1, activation="sigmoid")(x)

        model = models.Model(inputs=inputs, outputs=outputs)
        model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])

    async def handle_missing_data(self, data: pd.DataFrame, strategy: str = "knn") -> pd.DataFrame:
        """
        Handle missing data using various imputation strategies.
        """
        if strategy == "knn":
            # KNN imputation
            return pd.DataFrame(
                self.knn_imputer.fit_transform(data),
                columns=data.columns,
                index=data.index,
            )
        elif strategy == "mean":
            # Mean imputation
            return data.fillna(data.mean())
        elif strategy == "forward":
            # Forward fill for time series
            return data.fillna(method="ffill")
        elif strategy == "backward":
            # Backward fill for time series
            return data.fillna(method="bfill")
        else:
            raise ValueError(f"Unknown imputation strategy: {strategy}")

    def reduce_dimensionality(
        self, features: np.ndarray, n_components: Optional[int] = None
    ) -> np.ndarray:
        """
        Reduce feature dimensionality while preserving important information.
        """
        if n_components:
            self.pca.n_components = n_components

        # Scale features before PCA
        scaled_features = self.scaler.fit_transform(features)

        # Apply PCA
        reduced_features = self.pca.fit_transform(scaled_features)

    async def create_ensemble_prediction(
        self,
        mental_health_data: List[Dict],
        energy_data: List[Dict],
        task_data: List[Dict],
    ) -> Dict[str, Any]:
        """
        Create ensemble predictions by combining multiple models.
        """
        # Prepare data
        mh_features, _ = self.preprocessor.prepare_mental_health_features(mental_health_data)
        energy_features, _ = self.preprocessor.prepare_energy_features(energy_data)
        task_features, _ = self.preprocessor.prepare_task_features(task_data)

        # Handle missing data
        df = pd.DataFrame(np.hstack([mh_features, energy_features, task_features]))
        clean_data = await self.handle_missing_data(df)

        # Reduce dimensionality
        reduced_features = self.reduce_dimensionality(clean_data.values)

        # Get predictions from base models
        mood_pred = self.model_factory.create_mood_predictor(
            input_shape=reduced_features.shape[1:]
        ).predict(reduced_features)

        energy_pred = self.model_factory.create_energy_predictor(
            input_shape=reduced_features.shape[1:]
        ).predict(reduced_features)

        task_pred = self.model_factory.create_task_predictor(
            input_shape=reduced_features.shape[1:]
        ).predict(reduced_features)

        # Combine predictions using meta-model
        meta_features = np.column_stack([mood_pred, energy_pred, task_pred])

        meta_model = self.create_meta_model(input_shape=(3,))
        final_prediction = meta_model.predict(meta_features)

        return {
            "ensemble_score": float(final_prediction[0]),
            "component_predictions": {
                "mood": float(mood_pred[0]),
                "energy": float(energy_pred[0]),
                "task": float(task_pred[0]),
            },
            "feature_importance": self._calculate_feature_importance(clean_data),
            "timestamp": datetime.now().isoformat(),
        }

    def _calculate_feature_importance(self, data: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate feature importance using PCA components.
        """
        # Get feature importance from PCA components
        components = self.pca.components_
        importance = np.abs(components).sum(axis=0)

        # Normalize importance scores
        importance = importance / importance.sum()

        return {f"feature_{i}": float(score) for i, score in enumerate(importance)}


class ModelPipeline:
    """
    Pipeline for sequentially linking multiple models.
    """

    def __init__(self):
        self.models = []
        self.preprocessors = []

    def add_stage(self, model: models.Model, preprocessor: Optional[Any] = None):
        """
        Add a model and its preprocessor to the pipeline.
        """
        self.models.append(model)
        self.preprocessors.append(preprocessor or (lambda x: x))

    async def predict(self, initial_input: Any) -> List[Any]:
        """
        Run prediction through the entire pipeline.
        """
        current_output = initial_input
        all_outputs = []

        for model, preprocessor in zip(self.models, self.preprocessors):
            # Preprocess current input
            processed_input = preprocessor(current_output)

            # Get prediction
            current_output = model.predict(processed_input)
            all_outputs.append(current_output)


class ReinforcementOptimizer:
    """
    Reinforcement learning system for optimizing decisions based on model outputs.
    """

    def __init__(self, state_size: int, action_size: int):
        self.state_size = state_size
        self.action_size = action_size
        self.model = self._build_model()

    def _build_model(self) -> models.Model:
        """
        Build a simple DQN model for reinforcement learning.
        """
        model = models.Sequential(
            [
                layers.Dense(64, activation="relu", input_shape=(self.state_size,)),
                layers.Dropout(0.2),
                layers.Dense(32, activation="relu"),
                layers.Dense(self.action_size, activation="linear"),
            ]
        )

        model.compile(optimizer="adam", loss="mse")

    def get_action(self, state: np.ndarray) -> int:
        """
        Get the optimal action for a given state.
        """
        q_values = self.model.predict(state.reshape(1, -1))
        return np.argmax(q_values[0])

    def update(
        state: np.ndarray,
        action: int,
        reward: float,
        next_state: np.ndarray,
        learning_rate: float = 0.1,
    ):
        """
        Update the model based on received reward.
        """
        current_q = self.model.predict(state.reshape(1, -1))[0]
        next_q = self.model.predict(next_state.reshape(1, -1))[0]

        # Q-learning update
        current_q[action] = (1 - learning_rate) * current_q[action] + learning_rate * (
            reward + 0.95 * np.max(next_q)
        )

        # Train model
        self.model.fit(state.reshape(1, -1), current_q.reshape(1, -1), verbose=0)
