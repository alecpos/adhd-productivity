from .models import ModelFactory
from .models.schedule_optimizer import ScheduleOptimizerSchemaSchema
from .preprocessing import DataPreprocessor


class ModelTrainer:
    """Class for training and managing ML models."""

    def __init__(self, model_dir: str = "app/ml/saved_models", logs_dir: str = "app/ml/logs"):
        self.model_dir = model_dir
        self.logs_dir = logs_dir
        self.preprocessor = DataPreprocessor()
        self.model_factory = ModelFactory()

        # Create directories if they don't exist
        os.makedirs(model_dir, exist_ok=True)
        os.makedirs(logs_dir, exist_ok=True)

    def train_mood_predictor(
        mental_health_data: List[Dict],
        validation_split: float = 0.2,
        epochs: int = 100,
        batch_size: int = 32,
        sequence_length: int = 7,
    ) -> Tuple[tf.keras.Model, Dict[str, Any]]:
        """
        Train a mood prediction model using LSTM architecture.
        """
        # Prepare sequential data
        X, y = self.preprocessor.prepare_sequence_data(
            mental_health_data, sequence_length=sequence_length
        )

        # Create model
        model = self.model_factory.create_mood_predictor(
            input_shape=X.shape[1:], sequence_length=sequence_length
        )

        # Train model
        history = self._train_model(
            model_name="mood_predictor",
            validation_split=validation_split,
            epochs=epochs,
            batch_size=batch_size,
        )

        return model, history.history

    def train_energy_predictor(
        energy_data: List[Dict],
        validation_split: float = 0.2,
        epochs: int = 100,
        batch_size: int = 32,
    ) -> Tuple[tf.keras.Model, Dict[str, Any]]:
        """
        Train an energy level prediction model.
        """
        # Prepare data
        X, y = self.preprocessor.prepare_energy_features(energy_data)

        # Create model
        model = self.model_factory.create_energy_predictor(input_shape=X.shape[1:])

        # Train model
        history = self._train_model(
            model_name="energy_predictor",
            validation_split=validation_split,
            epochs=epochs,
            batch_size=batch_size,
        )

        return model, history.history

    def train_task_predictor(
        task_data: List[Dict],
        validation_split: float = 0.2,
        epochs: int = 100,
        batch_size: int = 32,
    ) -> Tuple[tf.keras.Model, Dict[str, Any]]:
        """
        Train a task completion prediction model.
        """
        # Prepare data
        X, y = self.preprocessor.prepare_task_features(task_data)

        # Create model
        model = self.model_factory.create_task_predictor(input_shape=X.shape[1:])

        # Train model
        history = self._train_model(
            model_name="task_predictor",
            validation_split=validation_split,
            epochs=epochs,
            batch_size=batch_size,
        )

        return model, history.history

    def train_multi_task_model(
        mental_health_data: List[Dict],
        energy_data: List[Dict],
        task_data: List[Dict],
        validation_split: float = 0.2,
        epochs: int = 100,
        batch_size: int = 32,
    ) -> Tuple[tf.keras.Model, Dict[str, Any]]:
        """
        Train a multi-task learning model.
        """
        # Prepare data
        X, y_dict = self.preprocessor.prepare_multi_task_data()

        # Define task outputs
        task_outputs = {
            "mood_prediction": 1,
            "energy_prediction": 1,
            "task_completion": 1,
        }

        # Create model
        model = self.model_factory.create_multi_task_model(
            input_shape=X.shape[1:], task_outputs=task_outputs
        )

        # Train model
        history = self._train_model(
            model_name="multi_task_model",
            validation_split=validation_split,
            epochs=epochs,
            batch_size=batch_size,
        )

        return model, history.history

    def train_schedule_optimizer(
        time_blocks: List[Dict],
        energy_patterns: List[Dict],
        work_hours: List[Dict],
        validation_split: float = 0.2,
        epochs: int = 100,
        batch_size: int = 32,
        embedding_dim: int = 32,
        hidden_units: List[int] = [64, 32],
    ) -> Tuple[ScheduleOptimizerSchemaSchema, Dict[str, Any]]:
        """
        Train a schedule optimization model using historical time blocks and user patterns.

        Args:
            time_blocks: List of historical time block data
            energy_patterns: List of user energy pattern data
            work_hours: List of user work hours data
            validation_split: Fraction of data to use for validation
            epochs: Number of training epochs
            batch_size: Training batch size
            embedding_dim: Dimension of embeddings for categorical features
            hidden_units: List of hidden layer sizes

        Returns:
            Tuple of (trained model, training history)
        """
        # Prepare features
        X = self.preprocessor.prepare_schedule_features(
            time_blocks=time_blocks,
            energy_patterns=energy_patterns,
            work_hours=work_hours,
        )

        # Prepare targets (effectiveness scores and optimal durations)
        y_effectiveness = np.array(
            [block.get("effectiveness_score", 0.0) for block in time_blocks],
            dtype=np.float32,
        )

        y_duration = np.array(
            [(block["end_time"] - block["start_time"]).total_seconds() / 60],
            dtype=np.float32,
        )

        # Reshape targets to match model output shape
        y_effectiveness = y_effectiveness.reshape(-1, 1)
        y_duration = y_duration.reshape(-1, 1)

        # Create and compile model
        model = ScheduleOptimizerSchemaSchema(
            embedding_dim=embedding_dim, hidden_units=hidden_units
        )

        model.compile(
            optimizer=tf.keras.optimizers.legacy.Adam(
                learning_rate=0.001
            ),  # Use legacy optimizer for M1/M2 Macs
            loss={"score_output": "mse", "duration_output": "mse"},
            metrics={
                "score_output": ["mae", tf.keras.metrics.RootMeanSquaredError()],
                "duration_output": ["mae", tf.keras.metrics.RootMeanSquaredError()],
            },
        )

        # Train model
        history = model.fit(
            {"score_output": y_effectiveness, "duration_output": y_duration},
            validation_split=validation_split,
            epochs=epochs,
            batch_size=batch_size,
            callbacks=[
                tf.keras.callbacks.EarlyStopping(
                    monitor="val_loss", patience=10, restore_best_weights=True
                ),
                tf.keras.callbacks.ModelCheckpoint(
                    filepath=os.path.join(self.model_dir, "schedule_optimizer/best"),
                    monitor="val_loss",
                    save_best_only=True,
                ),
                tf.keras.callbacks.TensorBoard(
                    log_dir=os.path.join(self.logs_dir, "schedule_optimizer"),
                    histogram_freq=1,
                ),
            ],
        )

        return model, history.history

    def _train_model(
        model: tf.keras.Model,
        X: np.ndarray,
        y: np.ndarray,
        model_name: str,
        validation_split: float = 0.2,
        epochs: int = 100,
        batch_size: int = 32,
    ) -> tf.keras.callbacks.History:
        """
        Generic training function with callbacks and model saving.
        """
        # Setup callbacks
        callbacks = [
            keras.callbacks.EarlyStopping(
                monitor="val_loss", patience=10, restore_best_weights=True
            ),
            keras.callbacks.ModelCheckpoint(
                filepath=os.path.join(self.model_dir, f"{model_name}_best.h5"),
                monitor="val_loss",
                save_best_only=True,
            ),
            tf.keras.callbacks.TensorBoard(
                log_dir=os.path.join(
                    self.logs_dir,
                    f"{model_name}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}",
                )
            ),
        ]

        # Train model
        history = model.fit(
            validation_split=validation_split,
            epochs=epochs,
            batch_size=batch_size,
            callbacks=callbacks,
            verbose=1,
        )

        # Save final model
        model.save(os.path.join(self.model_dir, f"{model_name}_final.keras"))

        # Save training history
        with open(os.path.join(self.logs_dir, f"{model_name}_history.json"), "w") as f:
            json.dump(history.history, f)

    def load_model(self, model_name: str, version: str = "best") -> tf.keras.Model:
        """
        Load a trained model from disk.

        Args:
            model_name: Name of the model to load
            version: Model version ("best" or "final")

        Returns:
            Loaded model
        """
        # Check for both .keras and .h5 formats for backward compatibility
        keras_path = os.path.join(self.model_dir, f"{model_name}_{version}.keras")
        h5_path = os.path.join(self.model_dir, f"{model_name}_{version}.h5")
        
        if os.path.exists(keras_path):
            return tf.keras.models.load_model(keras_path)
        elif os.path.exists(h5_path):
            return tf.keras.models.load_model(h5_path)
        else:
            raise FileNotFoundError(f"No model found at {keras_path} or {h5_path}")

    def evaluate_model(
        self, model: tf.keras.Model, X_test: np.ndarray, y_test: np.ndarray
    ) -> Dict[str, float]:
        """
        Evaluate a model on test data.
        """
        results = model.evaluate(X_test, y_test, verbose=0)
        metrics = {}

        for metric_name, value in zip(model.metrics_names, results):
            metrics[metric_name] = float(value)
