from .preprocessing import DataPreprocessor
from .training import ModelTrainer


class PredictionService:
    """Service for making predictions using trained models."""

    def __init__(self):
        self.preprocessor = DataPreprocessor()
        self.trainer = ModelTrainer()
        self.models = {}
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

    def _generate_comprehensive_insights(
        mood_pred: float,
        energy_pred: float,
        task_completion_pred: float,
        current_state: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """
        Generate comprehensive insights based on predictions.
        """
        insights = {
            "overall_state": self._assess_overall_state(),
            "mood_analysis": {
                "prediction": mood_pred,
                "trend": (
                    "improving"
                    if current_state and mood_pred > current_state.get("mood_score", 0)
                    else "declining"
                ),
                "factors": self._identify_mood_factors(current_state) if current_state else [],
            },
            "energy_analysis": {
                "prediction": energy_pred,
                "optimal_task_types": self._suggest_task_types(energy_pred),
                "recommended_breaks": self._calculate_break_recommendations(energy_pred),
            },
            "productivity_potential": {
                "score": task_completion_pred,
                "limiting_factors": self._identify_limiting_factors(),
                "optimization_suggestions": self._generate_optimization_suggestions(),
            },
        }

    def _assess_overall_state(
        self, mood_pred: float, energy_pred: float, task_completion_pred: float
    ) -> str:
        """
        Assess overall state based on predictions.
        """
        average_score = (mood_pred + energy_pred + task_completion_pred * 10) / 3

        if average_score >= 7.5:
            return "optimal"
        elif average_score >= 6:
            return "good"
        elif average_score >= 4:
            return "moderate"
        else:
            return "challenging"

    def _identify_mood_factors(self, current_state: Dict) -> List[str]:
        """
        Identify factors affecting mood.
        """
        factors = []

        if current_state.get("stress_level", 0) > 6:
            factors.append("high stress levels")
        if current_state.get("sleep_quality", 0) < 6:
            factors.append("poor sleep quality")
        if current_state.get("anxiety_level", 0) > 6:
            factors.append("elevated anxiety")

    def _suggest_task_types(self, energy_pred: float) -> List[str]:
        """
        Suggest appropriate task types based on predicted energy.
        """
        if energy_pred >= 7:
            return ["high-focus tasks", "complex problem-solving", "creative work"]
        elif energy_pred >= 5:
            return ["moderate-focus tasks", "routine work", "administrative tasks"]
        else:
            return ["low-energy tasks", "planning", "organization"]

    def _calculate_break_recommendations(self, energy_pred: float) -> Dict[str, Any]:
        """
        Calculate break recommendations based on energy prediction.
        """
        if energy_pred < 4:
            return {
                "frequency": "every 25 minutes",
                "duration": "10-15 minutes",
                "type": "active breaks",
            }
        elif energy_pred < 7:
            return {
                "frequency": "every 45 minutes",
                "duration": "5-10 minutes",
                "type": "mixed breaks",
            }
        else:
            return {
                "frequency": "every 60 minutes",
                "duration": "5 minutes",
                "type": "quick breaks",
            }

    def _identify_limiting_factors(
        self, mood_pred: float, energy_pred: float, task_completion_pred: float
    ) -> List[str]:
        """
        Identify factors limiting productivity.
        """
        factors = []

        if mood_pred < 5:
            factors.append("low mood")
        if energy_pred < 5:
            factors.append("low energy")
        if task_completion_pred < 0.4:
            factors.append("task complexity or overwhelm")

    def _generate_optimization_suggestions(
        self, mood_pred: float, energy_pred: float, task_completion_pred: float
    ) -> List[str]:
        """
        Generate suggestions for optimization.
        """
        suggestions = []

        if mood_pred < 5:
            suggestions.extend(
                [
                    "Take a short walk or get some fresh air",
                    "Practice a quick mindfulness exercise",
                    "Connect with a supportive person",
                ]
            )

        if energy_pred < 5:
            suggestions.extend(
                [
                    "Take a power nap (15-20 minutes)",
                    "Have a healthy snack",
                    "Do some light stretching or exercise",
                ]
            )

        if task_completion_pred < 0.4:
            suggestions.extend(
                [
                    "Break down tasks into smaller, manageable pieces",
                    "Start with the easiest subtask",
                    "Set a timer for focused work sessions",
                ]
            )

    def _generate_recommendations(self, insights: Dict[str, Any]) -> List[str]:
        """
        Generate actionable recommendations based on insights.
        """
        recommendations = []

        # Add recommendations based on overall state
        if insights["overall_state"] == "challenging":
            recommendations.extend(
                [
                    "Consider taking a break to recharge",
                    "Focus on self-care activities",
                    "Adjust your schedule to match your energy levels",
                ]
            )

        # Add mood-based recommendations
        if insights["mood_analysis"]["trend"] == "declining":
            recommendations.extend(
                [
                    "Schedule a mood-boosting activity",
                    "Practice stress-reduction techniques",
                    "Consider talking to a supportive person",
                ]
            )

        # Add energy-based recommendations
        recommendations.extend(
            [
                f"Focus on {task_type}"
                for task_type in insights["energy_analysis"]["optimal_task_types"][:2]
            ]
        )

        # Add productivity recommendations
        recommendations.extend(insights["productivity_potential"]["optimization_suggestions"])

        return recommendations[:5]  # Return top 5 recommendations
