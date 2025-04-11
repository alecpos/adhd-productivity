# ADHD Calendar: Epic 4 Code Reference

**Version**: 1.0
**Last Updated**: 2025-03-08
**Target Audience**: Developers and maintainers

## Overview

This document provides a comprehensive code reference for the Dynamic Schedule Rebalancing components created in Epic 4. It details the structure, classes, methods, and key implementation details to assist developers in understanding and maintaining the codebase.

## Code Structure

The Epic 4 components are organized into the following directory structure:

```
app/
└── ml/
    ├── models/
    │   ├── adhd17_reinforcement_model.py  # Reinforcement learning for scheduling
    │   ├── energy_optimizer_model.py      # Circadian rhythm optimization
    │   └── model_factory.py               # Factory for model creation
    ├── stochastic_time_estimation/
    │   ├── bayesian_duration_predictor.py # Bayesian task duration prediction
    │   ├── time_buffer_calculator.py      # Task time buffer calculations
    │   ├── contextual_stressor_detector.py # Real-time stress/progress detection
    │   └── nlp_complexity_analyzer.py     # Task complexity analysis
    ├── temporal_pattern_recognition.py    # TPR service integration
    └── tests/
        ├── test_circadian_rhythm.py       # Tests for circadian components
        └── test_reinforcement_learning.py # Tests for RL scheduling
```

## Reinforcement Learning (adhd17_reinforcement_model.py)

### Class: `DQNScheduler`

Base reinforcement learning scheduler that learns optimal task allocation policies.

```python
class DQNScheduler:
    """
    Deep Q-Network based scheduler for optimizing task allocation.

    This class implements a reinforcement learning approach to scheduling
    using a Deep Q-Network. It learns optimal policies for allocating tasks
    to time slots based on task properties and constraints.
    """

    def __init__(self, state_size, action_size, learning_rate=0.001,
                 discount_factor=0.95, exploration_rate=0.1,
                 exploration_decay=0.995, min_exploration_rate=0.01):
        """
        Initialize the DQN Scheduler.

        Args:
            state_size: Size of state representation
            action_size: Number of possible actions
            learning_rate: Learning rate for model updates
            discount_factor: Discount factor for future rewards
            exploration_rate: Initial exploration vs exploitation rate
            exploration_decay: Rate at which exploration decreases
            min_exploration_rate: Minimum exploration rate
        """
```

### Class: `CircadianDQNModel`

Extended Deep Q-Network model that incorporates circadian awareness.

```python
class CircadianDQNModel(DQNScheduler):
    """
    Circadian-aware Deep Q-Network for schedule optimization.

    Extends the DQNScheduler with circadian rhythm awareness, incorporating
    time-of-day and energy level considerations into scheduling decisions.
    """

    def __init__(self, state_size, action_size, learning_rate=0.001,
                 discount_factor=0.95, exploration_rate=0.1):
        """Initialize with standard DQN parameters."""
        super().__init__(state_size, action_size, learning_rate,
                         discount_factor, exploration_rate)
        self.circadian_feature_size = 2  # Time of day and energy level

    def create_state_with_circadian_features(self, tasks, time_of_day, energy_level):
        """
        Create state representation with circadian features.

        Args:
            tasks: List of tasks to be scheduled
            time_of_day: Current hour of day (0-23)
            energy_level: Current energy level (0-10)

        Returns:
            State vector with circadian features
        """

    def calculate_circadian_reward(self, task, scheduled_time, completion_success, energy_level):
        """
        Calculate reward with circadian awareness.

        Args:
            task: The task being scheduled
            scheduled_time: Time slot assigned to task
            completion_success: Whether task was completed successfully
            energy_level: Energy level at scheduled time

        Returns:
            Reward value incorporating circadian factors
        """

    def optimize_schedule(self, tasks, energy_pattern, start_time, end_time):
        """
        Generate an optimized schedule using the trained model.

        Args:
            tasks: List of tasks to schedule
            energy_pattern: Energy levels throughout the day
            start_time: Beginning of scheduling window
            end_time: End of scheduling window

        Returns:
            Optimized schedule as list of task-time assignments
        """
```

### Class: `TaskCognitiveProfile`

Helper class for categorizing tasks by cognitive demands.

```python
class TaskCognitiveProfile:
    """
    Analyzes and categorizes tasks based on cognitive demands.

    This class helps classify tasks into different cognitive categories
    and determine their energy requirements and optimal timing.
    """

    CATEGORIES = [
        'focus_intensive',
        'creative',
        'routine',
        'administrative',
        'learning'
    ]

    def categorize_task(self, task):
        """
        Determine the cognitive demand category for a task.

        Args:
            task: Task to categorize

        Returns:
            Category label from CATEGORIES
        """

    def get_energy_requirements(self, task_category):
        """
        Returns energy level needed for a task category.

        Args:
            task_category: Category from CATEGORIES

        Returns:
            Required energy level (0-10)
        """

    def calculate_temporal_suitability(self, task_category, time_of_day, energy_level):
        """
        Compute how suitable a time slot is for a task.

        Args:
            task_category: Category from CATEGORIES
            time_of_day: Hour of day (0-23)
            energy_level: Current energy level (0-10)

        Returns:
            Suitability score (0-1)
        """
```

## Circadian Rhythm Model (energy_optimizer_model.py)

### Class: `CircadianRhythmModel`

Model for detecting and predicting user energy patterns throughout the day.

```python
class CircadianRhythmModel:
    """
    Predicts user energy patterns based on circadian rhythms.

    This model analyzes historical user data to detect circadian patterns
    and predict energy levels throughout the day for optimal scheduling.
    """

    def __init__(self, use_harmonic_model=True):
        """
        Initialize the circadian rhythm model.

        Args:
            use_harmonic_model: Whether to use harmonic modeling
        """
        self.use_harmonic_model = use_harmonic_model
        self.model = self._create_model()

    def train(self, sleep_data, productivity_data):
        """
        Train the model with user data.

        Args:
            sleep_data: Historical sleep timing data
            productivity_data: Historical productivity metrics

        Returns:
            Training history
        """

    def predict_energy_levels(self, user_id, date):
        """
        Predict hourly energy levels for a specific day.

        Args:
            user_id: User identifier
            date: Target date for prediction

        Returns:
            Dictionary of hourly energy levels (0-10)
        """

    def generate_energy_curve(self, user_id, date, resolution_minutes=60):
        """
        Create a complete energy curve for scheduling.

        Args:
            user_id: User identifier
            date: Target date
            resolution_minutes: Time resolution in minutes

        Returns:
            List of energy levels at specified resolution
        """

    def detect_optimal_windows(self, user_id, date, task_categories):
        """
        Identify optimal time periods for different task types.

        Args:
            user_id: User identifier
            date: Target date
            task_categories: List of task categories to find windows for

        Returns:
            Dictionary mapping categories to optimal time windows
        """
```

## Stochastic Time Estimation

### Class: `BayesianDurationPredictor` (bayesian_duration_predictor.py)

Predicts task duration with uncertainty using Bayesian methods.

```python
class BayesianDurationPredictor:
    """
    Predicts task duration with uncertainty using Bayesian inference.

    This class implements Bayesian prediction for task duration, accounting
    for uncertainty and providing confidence intervals.
    """

    def __init__(self, prior_strength=10):
        """
        Initialize the Bayesian predictor.

        Args:
            prior_strength: Strength of prior beliefs
        """
        self.prior_strength = prior_strength
        self.model = self._create_model()

    def predict_duration(self, task_title, task_description, user_id, task_category=None):
        """
        Predict duration for a task with uncertainty.

        Args:
            task_title: Title of the task
            task_description: Description of the task
            user_id: User identifier
            task_category: Optional category of the task

        Returns:
            DurationPrediction object with mean and uncertainty
        """

    def update_model(self, task_id, actual_duration):
        """
        Update model with actual completion time.

        Args:
            task_id: Task identifier
            actual_duration: Actual time taken to complete

        Returns:
            Updated model parameters
        """
```

### Class: `TimeBufferCalculator` (time_buffer_calculator.py)

Calculates appropriate time buffers based on task characteristics and uncertainty.

```python
class TimeBufferCalculator:
    """
    Calculates appropriate time buffers for tasks.

    This class determines how much buffer time to add to task estimates
    based on prediction uncertainty, task importance, and user reliability.
    """

    def calculate_buffer(self, base_duration, uncertainty, user_reliability, task_importance):
        """
        Calculate time buffer for a task.

        Args:
            base_duration: Base duration estimate in minutes
            uncertainty: Prediction uncertainty (standard deviation)
            user_reliability: User's historical reliability (0-1)
            task_importance: Importance of the task (1-5)

        Returns:
            Buffer time in minutes
        """

    def calculate_opportunity_cost(self, task1, task2, available_time):
        """
        Calculate opportunity cost between two tasks.

        Args:
            task1: First task to compare
            task2: Second task to compare
            available_time: Available time in minutes

        Returns:
            Opportunity cost metric
        """
```

### Class: `ContextualStressorDetector` (contextual_stressor_detector.py)

Detects progress issues and stressors during task execution.

```python
class ContextualStressorDetector:
    """
    Detects potential stressors and progress issues during task execution.

    This class analyzes task progress and contextual factors to identify
    stressors that might impact task completion.
    """

    def detect_stressors(self, user_id, task_id, progress_percentage, time_elapsed_ratio):
        """
        Detect stressors based on task progress.

        Args:
            user_id: User identifier
            task_id: Task identifier
            progress_percentage: Percentage of task completed
            time_elapsed_ratio: Ratio of time used vs allocated

        Returns:
            List of detected stressors with confidence scores
        """

    def recommend_interventions(self, detected_stressors):
        """
        Recommend interventions for detected stressors.

        Args:
            detected_stressors: List of detected stressors

        Returns:
            List of recommended interventions
        """
```

## Service Integration

### Class: `TemporalPatternRecognitionService` (temporal_pattern_recognition.py)

Integration service that connects all components.

```python
class TemporalPatternRecognitionService:
    """
    Service that integrates temporal pattern recognition with scheduling.

    This service coordinates the interaction between different components
    to provide a unified interface for schedule optimization.
    """

    def __init__(self):
        """Initialize service components."""
        self.circadian_model = CircadianRhythmModel()
        self.dqn_scheduler = CircadianDQNModel(state_size=30, action_size=24)
        self.duration_predictor = BayesianDurationPredictor()
        self.buffer_calculator = TimeBufferCalculator()
        self.cognitive_profiler = TaskCognitiveProfile()

    def optimize_schedule_with_circadian(self, user_id, tasks, start_date, end_date):
        """
        Generate optimized schedule using circadian patterns.

        Args:
            user_id: User identifier
            tasks: List of tasks to schedule
            start_date: Start of scheduling period
            end_date: End of scheduling period

        Returns:
            CircadianCalendarOptimizationResponse
        """

    def apply_circadian_optimization(self, user_id, optimization_id):
        """
        Apply a generated optimization to the user's calendar.

        Args:
            user_id: User identifier
            optimization_id: ID of previously generated optimization

        Returns:
            ApplyCircadianOptimizationResponse
        """

    def monitor_progress(self, user_id, task_id):
        """
        Set up real-time progress monitoring for a task.

        Args:
            user_id: User identifier
            task_id: Task to monitor

        Returns:
            MonitoringConfiguration
        """
```

## Performance Considerations

- The CircadianDQNModel uses model compression techniques to reduce inference time
- Caching is implemented for energy patterns to avoid redundant calculations
- The bayesian duration predictor uses approximate inference for faster predictions
- The system supports batch processing of multiple schedule optimizations

## Security Considerations

- User circadian data is treated as sensitive information
- Energy patterns are anonymized before any cross-user learning
- All models support local inference to minimize data transfer
- User consent is required before collecting any temporal pattern data

## Testing

Test cases for Epic 4 components are located in `app/ml/tests/`:

- `test_circadian_rhythm.py`: Tests for the CircadianRhythmModel
- `test_reinforcement_learning.py`: Tests for DQNScheduler and CircadianDQNModel
- `test_stochastic_estimation.py`: Tests for duration prediction components
- `test_integration.py`: End-to-end tests for the TemporalPatternRecognitionService
