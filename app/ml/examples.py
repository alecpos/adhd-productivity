from .ensemble_learning import EnsembleLearner, ModelPipeline, ReinforcementOptimizer
from .models import ModelFactory
from .preprocessing import DataPreprocessor
from .visualization import InsightVisualizer
from .prediction_service import PredictionService


async def ensemble_learning_example(
    mental_health_data: List[Dict], energy_data: List[Dict], task_data: List[Dict]
) -> Dict[str, Any]:
    """
    Example of using the ensemble learning system.
    """
    # Initialize components
    ensemble = EnsembleLearner()
    visualizer = InsightVisualizer()

    # Get ensemble predictions
    predictions = await ensemble.create_ensemble_prediction(
        mental_health_data=mental_health_data, energy_data=energy_data, task_data=task_data
    )

    # Create visualizations
    dashboard = visualizer.create_productivity_dashboard(mental_health_data, energy_data, task_data)

    return {"predictions": predictions, "visualizations": dashboard}


async def pipeline_example(initial_data: Any) -> List[Any]:
    """
    Example of using the model pipeline.
    """
    # Initialize components
    pipeline = ModelPipeline()
    model_factory = ModelFactory()
    preprocessor = DataPreprocessor()

    # Create models
    mood_predictor = model_factory.create_mood_predictor(input_shape=(10,))
    energy_predictor = model_factory.create_energy_predictor(input_shape=(8,))
    task_predictor = model_factory.create_task_predictor(input_shape=(12,))

    # Add models to pipeline
    pipeline.add_stage(mood_predictor, preprocessor.prepare_mental_health_features)
    pipeline.add_stage(energy_predictor, preprocessor.prepare_energy_features)
    pipeline.add_stage(task_predictor, preprocessor.prepare_task_features)

    # Get sequential predictions
    results = await pipeline.predict(initial_data)


async def reinforcement_learning_example(
    state_size: int = 10, action_size: int = 5
) -> Dict[str, Any]:
    """
    Example of using reinforcement learning for optimization.
    """
    # Initialize optimizer
    optimizer = ReinforcementOptimizer(state_size=state_size, action_size=action_size)

    # Example state
    current_state = np.random.normal(size=state_size)

    # Get optimal action
    action = optimizer.get_action(current_state)

    # Simulate environment interaction
    reward = np.random.random()  # In real use, this would be actual feedback
    next_state = np.random.normal(size=state_size)  # In real use, this would be the new state

    # Update model based on reward
    optimizer.update(state=current_state, action=action, reward=reward, next_state=next_state)

    return {"action_taken": int(action), "reward_received": float(reward)}


async def comprehensive_analysis_example(
    mental_health_data: List[Dict], energy_data: List[Dict], task_data: List[Dict]
) -> Dict[str, Any]:
    """
    Example of performing comprehensive analysis using all components.
    """
    # Initialize all components
    ensemble = EnsembleLearner()
    visualizer = InsightVisualizer()
    pipeline = ModelPipeline()
    optimizer = ReinforcementOptimizer(state_size=10, action_size=5)

    # Get ensemble predictions
    predictions = await ensemble.create_ensemble_prediction(
        mental_health_data=mental_health_data, energy_data=energy_data, task_data=task_data
    )

    # Create visualizations
    dashboard = visualizer.create_productivity_dashboard(mental_health_data, energy_data, task_data)

    # Extract current state from predictions
    current_state = np.array(
        [
            predictions["component_predictions"]["mood"],
            predictions["component_predictions"]["energy"],
            predictions["component_predictions"]["task"],
            predictions["ensemble_score"],
        ]
    )

    # Get optimization recommendation
    action = optimizer.get_action(current_state)

    # Combine all insights
    return {
        "predictions": predictions,
        "visualizations": dashboard,
        "recommended_action": int(action),
        "timestamp": datetime.now().isoformat(),
    }


# Example usage data
def create_example_data(
    num_days: int = 30,
) -> Tuple[List[Dict], List[Dict], List[Dict]]:
    """
    Create example data for testing the ML components.
    """
    base_time = datetime.now() - timedelta(days=num_days)

    mental_health_data = [
        {
            "timestamp": base_time + timedelta(days=i),
            "mood_score": np.random.normal(7, 1),
            "stress_level": np.random.normal(5, 2),
            "anxiety_level": np.random.normal(4, 2),
            "energy_level": np.random.normal(6, 1),
            "sleep_quality": np.random.normal(7, 1),
            "activity_log": ["exercise", "meditation"] if np.random.random() > 0.5 else ["reading"],
            "triggers": ["work", "social"] if np.random.random() > 0.7 else [],
        }
        for i in range(num_days)
    ]

    energy_data = [
        {
            "timestamp": base_time + timedelta(days=i),
            "energy_level": np.random.normal(6, 1),
            "focus_level": np.random.normal(7, 1),
            "duration": np.random.normal(60, 15),
            "activities": ["work", "study"] if np.random.random() > 0.5 else ["exercise"],
        }
        for i in range(num_days)
    ]

    task_data = [
        {
            "timestamp": base_time + timedelta(days=i),
            "time_spent": np.random.normal(45, 15),
            "difficulty_rating": np.random.randint(1, 11),
            "focus_level": np.random.normal(7, 1),
            "breaks_taken": np.random.randint(0, 5),
            "interruptions": np.random.randint(0, 8),
            "priority_level": np.random.randint(1, 4),
            "category": np.random.choice(["work", "study", "personal"]),
            "completed": np.random.random() > 0.3,
        }
        for i in range(num_days)
    ]


async def run_ensemble_example():
    """Example of using ensemble learning."""
    learner = EnsembleLearner()

    # Example data
    mental_health_data = [
        {"mood": 0.8, "stress": 0.2, "timestamp": "2023-01-01T10:00:00"},
        {"mood": 0.7, "stress": 0.3, "timestamp": "2023-01-01T11:00:00"},
    ]

    energy_data = [
        {"energy_level": 0.9, "activity": 0.5, "timestamp": "2023-01-01T10:00:00"},
        {"energy_level": 0.8, "activity": 0.6, "timestamp": "2023-01-01T11:00:00"},
    ]

    task_data = [
        {"complexity": 0.7, "duration": 30, "timestamp": "2023-01-01T10:00:00"},
        {"complexity": 0.6, "duration": 45, "timestamp": "2023-01-01T11:00:00"},
    ]

    # Create ensemble prediction with all required arguments
    prediction = await learner.create_ensemble_prediction(
        mental_health_data=mental_health_data, energy_data=energy_data, task_data=task_data
    )

    return prediction


async def run_prediction_example():
    """Example of using prediction service."""
    service = PredictionService()

    # Example data
    mental_health_data = [
        {"mood": 0.8, "stress": 0.2, "timestamp": "2023-01-01T10:00:00"},
        {"mood": 0.7, "stress": 0.3, "timestamp": "2023-01-01T11:00:00"},
    ]

    energy_data = [
        {"energy_level": 0.9, "activity": 0.5, "timestamp": "2023-01-01T10:00:00"},
        {"energy_level": 0.8, "activity": 0.6, "timestamp": "2023-01-01T11:00:00"},
    ]

    task_data = [
        {"complexity": 0.7, "duration": 30, "timestamp": "2023-01-01T10:00:00"},
        {"complexity": 0.6, "duration": 45, "timestamp": "2023-01-01T11:00:00"},
    ]

    # Create ensemble prediction with all required arguments
    prediction = await service.create_ensemble_prediction(
        mental_health_data=mental_health_data, energy_data=energy_data, task_data=task_data
    )

    return prediction
