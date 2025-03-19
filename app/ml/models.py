class ModelFactoryModel(Base):
    """Factory class for creating different types of neural network models."""

    @staticmethod
    def create_mood_predictor(
        input_shape: Tuple[int, ...], sequence_length: int = 7
    ) -> models.Model:
        """
        Create a mood prediction model using LSTM architecture.
        """
        model = models.Sequential(
            [
                layers.LSTM(
                    64,
                    return_sequences=True,
                    input_shape=(sequence_length, input_shape[-1]),
                ),
                layers.Dropout(0.2),
                layers.LSTM(32),
                layers.Dropout(0.2),
                layers.Dense(16, activation="relu"),
                layers.Dense(1),  # Predict mood score
            ]
        )

        model.compile(optimizer="adam", loss="mse", metrics=["mae"])

    @staticmethod
    def create_energy_predictor(input_shape: Tuple[int, ...]) -> models.Model:
        """
        Create an energy level prediction model.
        """
        model = models.Sequential(
            [
                layers.Dense(128, activation="relu", input_shape=input_shape),
                layers.Dropout(0.3),
                layers.Dense(64, activation="relu"),
                layers.Dropout(0.2),
                layers.Dense(32, activation="relu"),
                layers.Dense(1),  # Predict energy level
            ]
        )

        model.compile(optimizer="adam", loss="mse", metrics=["mae"])

    @staticmethod
    def create_task_predictor(input_shape: Tuple[int, ...]) -> models.Model:
        """
        Create a task completion prediction model.
        """
        model = models.Sequential(
            [
                layers.Dense(64, activation="relu", input_shape=input_shape),
                layers.Dropout(0.2),
                layers.Dense(32, activation="relu"),
                layers.Dropout(0.2),
                layers.Dense(16, activation="relu"),
                layers.Dense(1, activation="sigmoid"),  # Binary classification
            ]
        )

        model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy", "AUC"])

    @staticmethod
    def create_multi_task_model(
        input_shape: Tuple[int, ...], task_outputs: Dict[str, int]
    ) -> models.Model:
        """
        Create a multi-task learning model.
        """
        # Shared layers
        inputs = layers.Input(shape=input_shape)
        shared = layers.Dense(256, activation="relu")(inputs)
        shared = layers.Dropout(0.3)(shared)
        shared = layers.Dense(128, activation="relu")(shared)
        shared = layers.Dropout(0.2)(shared)

        # TaskModelSchemaSchema-specific layers
        outputs = {}
        for task_name, output_dim in task_outputs.items():
            task_layer = layers.Dense(64, activation="relu")(shared)
            task_layer = layers.Dropout(0.2)(task_layer)

            if task_name == "task_completion":
                outputs[task_name] = layers.Dense(
                    output_dim, activation="sigmoid", name=task_name
                )()
            else:
                outputs[task_name] = layers.Dense(output_dim, name=task_name)(task_layer)

        model = models.Model(inputs=inputs, outputs=outputs)

        # Compile with appropriate losses for each task
        losses = {
            "mood_prediction": "mse",
            "energy_prediction": "mse",
            "task_completion": "binary_crossentropy",
        }

        metrics = {
            "mood_prediction": ["mae"],
            "energy_prediction": ["mae"],
            "task_completion": ["accuracy", "AUC"],
        }

        model.compile(optimizer="adam", loss=losses, metrics=metrics)

    @staticmethod
    def create_transformer_predictor(
        input_shape: Tuple[int, ...], num_heads: int = 4, key_dim: int = 64
    ) -> models.Model:
        """
        Create a Transformer-based prediction model for complex temporal patterns.
        """
        inputs = layers.Input(shape=input_shape)

        # Multi-head attention layer
        attention = layers.MultiHeadAttention(num_heads=num_heads, key_dim=key_dim)(inputs, inputs)

        # Add & Normalize
        x = layers.LayerNormalization()(attention + inputs)

        # Feed-forward network
        ffn = layers.Dense(128, activation="relu")(x)
        ffn = layers.Dropout(0.1)(ffn)
        ffn = layers.Dense(input_shape[-1])(ffn)

        # Add & Normalize
        x = layers.LayerNormalization()(ffn + x)

        # Output layers
        x = layers.GlobalAveragePooling1D()(x)
        x = layers.Dense(64, activation="relu")(x)
        outputs = layers.Dense(1)(x)

        model = models.Model(inputs=inputs, outputs=outputs)
        model.compile(optimizer="adam", loss="mse", metrics=["mae"])

    @staticmethod
    def create_activity_recommender(num_activities: int, embedding_dim: int = 32) -> models.Model:
        """
        Create a neural collaborative filtering model for activity recommendations.
        """
        # UserModelSchemaSchema features input
        user_input = layers.Input(
            shape=(10,), name="user_features"
        )  # Adjust shape based on your features
        user_embedding = layers.Dense(embedding_dim, activation="relu")(user_input)

        # Activity embedding
        activity_input = layers.Input(shape=(1,), name="activity_id")
        activity_embedding = layers.Embedding(num_activities, embedding_dim)(activity_input)
        activity_embedding = layers.Flatten()(activity_embedding)

        # Combine embeddings
        concatenated = layers.Concatenate()([user_embedding, activity_embedding])

        # Dense layers
        x = layers.Dense(64, activation="relu")(concatenated)
        x = layers.Dropout(0.2)(x)
        x = layers.Dense(32, activation="relu")(x)
        x = layers.Dropout(0.2)(x)

        # Output layer
        outputs = layers.Dense(1, activation="sigmoid")(x)

        model = models.Model(inputs=[user_input, activity_input], outputs=outputs)

        model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])
