# Epic 4: Integration Guide - Dynamic Schedule Rebalancing

## Overview

This integration guide provides practical instructions for incorporating the Dynamic Schedule Rebalancing components from Epic 4 into your application. These components enable adaptive scheduling based on users' circadian rhythms, energy patterns, cognitive demands, and learning from past scheduling outcomes.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start Guide](#quick-start-guide)
3. [CircadianDQNModel Integration](#circardiandqnmodel-integration)
4. [CircadianRhythmModel Integration](#circadianrhythmmodel-integration)
5. [Opportunity Cost Calculator Integration](#opportunity-cost-calculator-integration)
6. [Real-time Progress Monitoring Integration](#real-time-progress-monitoring-integration)
7. [Using Components Together](#using-components-together)
8. [Frontend Integration](#frontend-integration)
9. [Testing Your Integration](#testing-your-integration)
10. [Performance Considerations](#performance-considerations)
11. [Troubleshooting](#troubleshooting)

## Prerequisites

Before integrating Epic 4 components, ensure you have:

- Python 3.9+
- Required packages installed (see `requirements-ml.txt`)
- Access to the ADHD Calendar API
- Basic understanding of reinforcement learning concepts
- User data collection mechanism (for energy patterns and task completion metrics)

```bash
# Install required dependencies
pip install -r requirements-ml.txt
```

## Quick Start Guide

Here's how to quickly integrate Dynamic Schedule Rebalancing into your application:

```python
from app.ml.models.adhd17_reinforcement_model import CircadianDQNModel
from app.ml.models.energy_optimizer_model import CircadianRhythmModel
from app.ml.stochastic_time_estimation.bayesian_duration_predictor import BayesianDurationPredictor
from app.ml.temporal_pattern_recognition import TemporalPatternRecognitionService

# Initialize the TPR service
tpr_service = TemporalPatternRecognitionService()

# Get an optimized schedule for a user
user_id = "user123"
start_date = datetime.now()
end_date = start_date + timedelta(days=7)
tasks = get_user_tasks(user_id)  # Your function to fetch tasks
optimized_schedule = tpr_service.optimize_schedule_with_circadian(
    user_id=user_id,
    start_date=start_date,
    end_date=end_date,
    tasks=tasks
)

# Apply the optimized schedule to the user's calendar
apply_result = tpr_service.apply_circadian_optimization(
    user_id=user_id,
    optimization_id=optimized_schedule.id
)
```

## CircadianDQNModel Integration

The CircadianDQNModel extends the basic DQN reinforcement learning model with circadian rhythm awareness.

### Basic Integration

```python
from app.ml.models.adhd17_reinforcement_model import CircadianDQNModel

# Initialize the model
model = CircadianDQNModel(
    state_size=24,  # Features in state representation
    action_size=5,  # Number of possible actions
    learning_rate=0.001,
    discount_factor=0.95,
    exploration_rate=0.1
)

# Train the model with user data
model.train(training_data, epochs=100)

# Generate schedule recommendations
state = create_current_state()  # Your function to create state representation
action = model.predict_action(state)
```

### Advanced Usage

```python
# Create a state with circadian features
energy_levels = get_user_energy_levels(user_id)  # Your function
state = model.create_state_with_circadian_features(
    tasks=tasks,
    time_of_day=current_hour,
    energy_level=energy_levels[current_hour]
)

# Calculate reward with circadian awareness
reward = model.calculate_circadian_reward(
    task=task,
    scheduled_time=scheduled_time,
    completion_success=True,
    energy_level=energy_level
)
```

## CircadianRhythmModel Integration

The CircadianRhythmModel predicts user energy patterns throughout the day.

### Basic Integration

```python
from app.ml.models.energy_optimizer_model import CircadianRhythmModel

# Initialize the model
model = CircadianRhythmModel()

# Train with user data
sleep_data = get_user_sleep_data(user_id)  # Your function
productivity_data = get_user_productivity_data(user_id)  # Your function
model.train(sleep_data, productivity_data)

# Get predicted energy levels
energy_levels = model.predict_energy_levels(user_id, date=today)
```

### Advanced Usage

```python
# Generate a complete energy curve
energy_curve = model.generate_energy_curve(
    user_id=user_id,
    date=today,
    resolution_minutes=30  # Get energy levels every 30 minutes
)

# Find optimal windows for different task types
optimal_windows = model.detect_optimal_windows(
    user_id=user_id,
    date=today,
    task_categories=["focus_intensive", "creative", "routine"]
)
```

## Opportunity Cost Calculator Integration

The Opportunity Cost Calculator helps estimate the true cost of task decisions.

### Basic Integration

```python
from app.ml.stochastic_time_estimation.bayesian_duration_predictor import BayesianDurationPredictor
from app.ml.stochastic_time_estimation.time_buffer_calculator import TimeBufferCalculator

# Initialize components
predictor = BayesianDurationPredictor()
buffer_calculator = TimeBufferCalculator()

# Predict task duration with uncertainty
task = get_task(task_id)  # Your function
duration_prediction = predictor.predict_duration(
    task_title=task.title,
    task_description=task.description,
    user_id=user_id,
    task_category=task.category
)

# Calculate appropriate time buffer
buffer = buffer_calculator.calculate_buffer(
    base_duration=duration_prediction.mean,
    uncertainty=duration_prediction.uncertainty,
    user_reliability=0.8,  # 0-1 scale
    task_importance=task.priority.value
)
```

## Real-time Progress Monitoring Integration

Integrate progress monitoring to track and adapt to task execution in real-time.

### Basic Integration

```python
from app.ml.stochastic_time_estimation.contextual_stressor_detector import ContextualStressorDetector

# Initialize detector
detector = ContextualStressorDetector()

# During task execution, monitor progress
stressors = detector.detect_stressors(
    user_id=user_id,
    task_id=task_id,
    progress_percentage=0.5,  # 50% complete
    time_elapsed_ratio=0.7  # 70% of allocated time used
)

# Take action based on detected stressors
if stressors:
    recommend_interventions(stressors)  # Your function
```

## Using Components Together

Here's how to integrate all Epic 4 components into a complete workflow:

```python
# 1. Get user's energy pattern for the day
energy_pattern = circadian_model.predict_energy_levels(user_id, today)

# 2. Get task list and their cognitive demands
tasks = get_user_tasks(user_id)
for task in tasks:
    # Add cognitive profile to tasks
    task.cognitive_profile = cognitive_profiler.categorize_task(task)
    
    # Predict realistic durations with uncertainty
    task.duration_prediction = duration_predictor.predict_duration(task)
    
    # Calculate time buffer
    task.time_buffer = buffer_calculator.calculate_buffer(
        task.duration_prediction.mean,
        task.duration_prediction.uncertainty,
        user_reliability,
        task.priority.value
    )

# 3. Use CircadianDQN to optimize schedule
optimized_schedule = circadian_dqn_model.optimize_schedule(
    tasks=tasks,
    energy_pattern=energy_pattern,
    start_time=day_start,
    end_time=day_end
)

# 4. Set up real-time monitoring for scheduled tasks
for scheduled_task in optimized_schedule:
    monitor.register_task_for_monitoring(
        task_id=scheduled_task.task_id,
        scheduled_start=scheduled_task.start_time,
        scheduled_end=scheduled_task.end_time,
        monitoring_interval=5  # minutes
    )
```

## Frontend Integration

To integrate Epic 4 visualizations in frontend applications:

```typescript
import { CircadianChart } from 'components/Charts/CircadianChart';
import { ScheduleComparisonView } from 'components/Schedule/ScheduleComparisonView';
import { ProgressMonitor } from 'components/Progress/ProgressMonitor';

// Display user's energy curve
const EnergyPatternView = () => {
  const [energyData, setEnergyData] = useState([]);
  
  useEffect(() => {
    // Fetch energy data from API
    api.getEnergyPattern(userId).then(data => {
      setEnergyData(data);
    });
  }, [userId]);
  
  return <CircadianChart data={energyData} />;
};

// Display optimized schedule comparison
const ScheduleOptimizer = () => {
  const [originalSchedule, setOriginalSchedule] = useState([]);
  const [optimizedSchedule, setOptimizedSchedule] = useState([]);
  
  const handleOptimize = async () => {
    const result = await api.optimizeSchedule(userId, selectedDate);
    setOptimizedSchedule(result.optimizedSchedule);
  };
  
  return (
    <>
      <ScheduleComparisonView 
        original={originalSchedule} 
        optimized={optimizedSchedule}
      />
      <Button onPress={handleOptimize}>Optimize Schedule</Button>
    </>
  );
};
```

## Testing Your Integration

Comprehensive testing is essential for reliable schedule optimization:

```python
# Unit test for CircadianDQNModel
def test_circadian_dqn_model():
    model = CircadianDQNModel(state_size=24, action_size=5)
    state = create_test_state()
    action = model.predict_action(state)
    assert 0 <= action < 5, "Action should be within range"

# Integration test for complete workflow
def test_schedule_optimization_workflow():
    # Set up test user and tasks
    user_id = create_test_user()
    tasks = create_test_tasks()
    
    # Run optimization
    tpr_service = TemporalPatternRecognitionService()
    result = tpr_service.optimize_schedule_with_circadian(
        user_id=user_id,
        tasks=tasks,
        start_date=today,
        end_date=today + timedelta(days=1)
    )
    
    # Verify results
    assert len(result.schedule) == len(tasks), "All tasks should be scheduled"
    
    # Check energy alignment
    energy_model = CircadianRhythmModel()
    energy_levels = energy_model.predict_energy_levels(user_id, today)
    
    for task_block in result.schedule:
        hour = task_block.start_time.hour
        task = next(t for t in tasks if t.id == task_block.task_id)
        
        if task.focus_required > 7:  # High focus task
            assert energy_levels[hour] > 6, "High focus tasks should be in high energy periods"
```

## Performance Considerations

- For large-scale deployments:
  - Use batch prediction for multiple users
  - Cache energy predictions for recurring patterns
  - Limit reinforcement learning steps for real-time responsiveness
  - Consider serverless functions for progress monitoring

- Resource utilization:
  ```python
  # Configure model for performance
  optimized_model = CircadianDQNModel(
      state_size=24,
      action_size=5,
      use_reduced_network=True,  # Use smaller network
      batch_size=32,             # Optimize batch size
      use_cached_predictions=True  # Enable prediction caching
  )
  ```

## Troubleshooting

Common issues and solutions:

1. **Poor schedule quality**:
   - Ensure sufficient historical data for accurate circadian rhythm detection
   - Check task categorization accuracy
   - Validate energy pattern predictions against user feedback

2. **Slow optimization performance**:
   - Reduce state space complexity
   - Use pre-computed energy patterns
   - Implement parallel processing for independent calculations

3. **Integration failures**:
   - Verify API endpoint URLs and authentication
   - Check data format consistency
   - Ensure all required models are properly initialized

For additional support, contact the Epic 4 development team or refer to the technical design documentation.