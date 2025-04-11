from .preprocessing import DataPreprocessor
from .training import ModelTrainer
from typing import Dict, List, Any
from app.ml.ensemble_learning import EnsembleLearner
from app.ml.visualization import InsightVisualizer


class PredictionService:
    """Service for making predictions using trained models."""

    def __init__(self):
        self.preprocessor = DataPreprocessor()
        self.trainer = ModelTrainer()
        self.models = {}
        self.ensemble = EnsembleLearner()
        self.visualizer = InsightVisualizer()
        self._load_models()

    def _load_models(self):
        """Load all trained models."""
        try:
            self.models["mood"] = self.trainer.load_model("mood_predictor")
            self.models["energy"] = self.trainer.load_model("energy_predictor")
            self.models["task"] = self.trainer.load_model("task_predictor")
            self.models["multi_task"] = self.trainer.load_model("multi_task_model")
            self.models["activity"] = self.trainer.load_model("activity_recommender")
        except Exception as e:
            print(f"Warning: Not all models could be loaded: {str(e)}")

    async def predict_mood(
        self, mental_health_data: List[Dict], sequence_length: int = 7
    ) -> Dict[str, Any]:
        """
        Predict future mood based on historical mental health data.
        """
        if "mood" not in self.models:
            raise ValueError("Mood prediction model not loaded")

        # Prepare sequential data
        X, _ = self.preprocessor.prepare_sequence_data(
            mental_health_data, sequence_length=sequence_length
        )

        # Make prediction
        prediction = self.models["mood"].predict(X[-1:])  # Predict for the last sequence

        confidence = self._calculate_prediction_confidence(prediction[0])

        return {
            "predicted_mood": float(prediction[0]),
            "confidence": confidence,
            "timestamp": datetime.now().isoformat(),
        }

    async def predict_energy(self, energy_data: List[Dict]) -> Dict[str, Any]:
        """
        Predict future energy levels.
        """
        if "energy" not in self.models:
            raise ValueError("Energy prediction model not loaded")

        # Prepare features
        X, _ = self.preprocessor.prepare_energy_features(energy_data)

        # Make prediction
        prediction = self.models["energy"].predict(X[-1:])  # Predict for the latest data point

        confidence = self._calculate_prediction_confidence(prediction[0])

        return {
            "predicted_energy": float(prediction[0]),
            "confidence": confidence,
            "timestamp": datetime.now().isoformat(),
        }

    async def predict_task_completion(self, task_data: Dict) -> Dict[str, Any]:
        """
        Predict likelihood of task completion.
        """
        if "task" not in self.models:
            raise ValueError("TaskModelSchemaSchema prediction model not loaded")

        # Prepare single task features
        X, _ = self.preprocessor.prepare_task_features([task_data])

        # Make prediction
        prediction = self.models["task"].predict(X)

        completion_probability = float(prediction[0])

        # Generate recommendations based on probability
        recommendations = self._generate_task_recommendations(completion_probability, task_data)

        return {
            "completion_probability": completion_probability,
            "confidence": self._calculate_prediction_confidence(prediction[0]),
            "recommendations": recommendations,
            "timestamp": datetime.now().isoformat(),
        }

    async def recommend_activities(
        self, user_features: np.ndarray, available_activities: List[str], top_k: int = 5
    ) -> Dict[str, Any]:
        """
        Recommend activities based on user state and preferences.
        """
        if "activity" not in self.models:
            raise ValueError("Activity recommendation model not loaded")

        # Prepare activity IDs
        activity_ids = np.arange(len(available_activities))

        # Repeat user features for each activity
        user_features_repeated = np.tile(user_features, (len(activity_ids), 1))

        # Make predictions for all activities
        predictions = self.models["activity"].predict(
            {"user_features": user_features_repeated, "activity_id": activity_ids}
        )

        # Get top k activities
        top_indices = np.argsort(predictions.flatten())[-top_k:][::-1]

        recommendations = []
        for idx in top_indices:
            recommendations.append(
                {
                    "activity": available_activities[idx],
                    "score": float(predictions[idx]),
                    "confidence": self._calculate_prediction_confidence(predictions[idx]),
                }
            )

        return {
            "recommendations": recommendations,
            "timestamp": datetime.now().isoformat(),
        }

    async def get_comprehensive_insights(
        self,
        mental_health_data: List[Dict],
        energy_data: List[Dict],
        task_data: List[Dict],
    ) -> Dict[str, Any]:
        """
        Generate comprehensive insights using multi-task model.
        """
        if "multi_task" not in self.models:
            raise ValueError("Multi-task model not loaded")

        # Prepare data
        X, _ = self.preprocessor.prepare_multi_task_data(mental_health_data, energy_data, task_data)

        # Make predictions
        predictions = self.models["multi_task"].predict(X[-1:])  # Predict for latest data point

        # Extract predictions for each task
        mood_pred = float(predictions["mood_prediction"][0])
        energy_pred = float(predictions["energy_prediction"][0])
        task_completion_pred = float(predictions["task_completion"][0])

        # Generate insights
        insights = self._generate_comprehensive_insights(
            mental_health_data[-1] if mental_health_data else None,
        )

        return {
            "predictions": {
                "mood": mood_pred,
                "energy": energy_pred,
                "task_completion_probability": task_completion_pred,
            },
            "insights": insights,
            "recommendations": self._generate_recommendations(insights),
            "timestamp": datetime.now().isoformat(),
        }

    def _calculate_prediction_confidence(self, prediction: float) -> float:
        """
        Calculate confidence score for a prediction.
        """
        # Simple confidence calculation based on distance from extreme values
        if isinstance(prediction, np.ndarray):
            prediction = prediction.item()

        # For binary predictions (0-1)
        if 0 <= prediction <= 1:
            return 1 - 2 * abs(0.5 - prediction)

        # For scale predictions (e.g., 1-10)
        return 1 - abs(5.5 - prediction) / 5.5

    def _generate_task_recommendations(
        self, completion_probability: float, task_data: Dict
    ) -> List[str]:
        """
        Generate recommendations to improve task completion probability.
        """
        recommendations = []

        if completion_probability < 0.4:
            recommendations.extend(
                [
                    "Consider breaking the task into smaller subtasks",
                    "Schedule the task during your peak energy hours",
                    "Set up a body doubling session for accountability",
                ]
            )
        elif completion_probability < 0.7:
            recommendations.extend(
                [
                    "Use the Pomodoro technique to maintain focus",
                    "Remove potential distractions before starting",
                    "Take regular breaks to maintain energy",
                ]
            )

        if task_data.get("difficulty_rating", 5) > 7:
            recommendations.append("Consider seeking help or resources to reduce task complexity")

    async def _generate_comprehensive_insights(
        self,
        predictions: Dict[str, Any],
        user_id: str
    ) -> Dict[str, Any]:
        """
        Generate comprehensive insights from predictions.

        Args:
            predictions: Dictionary containing prediction results
            user_id: ID of the user for whom insights are being generated

        Returns:
            Dictionary containing comprehensive insights
        """
        # Generate insights based on predictions
        insights = {
            "user_id": user_id,
            "productivity_score": predictions.get("ensemble_score", 0.0),
            "component_scores": predictions.get("component_predictions", {}),
            "feature_importance": predictions.get("feature_importance", {}),
            "recommendations": self._generate_recommendations(predictions)
        }

        return insights

    def _generate_recommendations(self, predictions: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on predictions."""
        recommendations = []

        # Add recommendations based on component scores
        component_scores = predictions.get("component_predictions", {})
        if component_scores.get("mood", 0.0) < 0.5:
            recommendations.append("Consider taking a short break to improve mood")
        if component_scores.get("energy", 0.0) < 0.5:
            recommendations.append("Try a quick physical activity to boost energy")

        return recommendations
