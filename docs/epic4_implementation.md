# Epic 4: Implementation Documentation - Dynamic Schedule Rebalancing

This document provides technical implementation details for Epic 4: Dynamic Schedule Rebalancing, with particular focus on the Circadian Rhythm Optimization functionality.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Architecture Diagram](#architecture-diagram)
3. [Data Flow](#data-flow)
4. [Component Details](#component-details)
5. [Data Models](#data-models)
6. [API Endpoints](#api-endpoints)
7. [Integration Points](#integration-points)
8. [Performance Considerations](#performance-considerations)
9. [Security Considerations](#security-considerations)
10. [Error Handling](#error-handling)
11. [Future Enhancements](#future-enhancements)
12. [Implementation Roadmap](#implementation-roadmap)

## Architecture Overview

Epic 4 implements a dynamic schedule rebalancing system that adapts to the user's circadian rhythms, energy levels, and task characteristics. The system consists of four primary components:

1. **CircadianDQNModel**: An extended Deep Q-Network model that incorporates circadian rhythm awareness into the reinforcement learning process for schedule optimization.

2. **DQNScheduler**: The base reinforcement learning scheduler that learns optimal task allocation policies.

3. **CircadianRhythmModel**: Advanced model for detecting and predicting a user's circadian rhythm patterns, energy curves, and optimal work windows.

4. **TemporalPatternRecognitionService**: Integration service that combines temporal pattern recognition with schedule optimization.

This architecture provides a comprehensive solution for dynamically rebalancing schedules based on user-specific circadian patterns, task cognitive demands, and learning from previous scheduling outcomes.

## Architecture Diagram

```
┌───────────────────────────────────────────────────────┐
│                 Client Application                     │
└───────────────────────────┬───────────────────────────┘
                            │
                            ▼
┌───────────────────────────────────────────────────────┐
│                API Gateway / Routing                   │
└────────────────┬──────────────────────┬───────────────┘
                 │                      │
                 ▼                      ▼
┌────────────────────────┐  ┌──────────────────────────┐
│  Scheduling Service     │  │Temporal Pattern          │
│                         │  │Recognition Service       │
└──────────┬─────────────┘  └────────────┬─────────────┘
           │                             │
           │       ┌─────────────────────┘
           │       │
           ▼       ▼
┌────────────────────────────────────────────────────────┐
│                     Models Layer                        │
│  ┌───────────────┐  ┌───────────────┐  ┌────────────┐  │
│  │CircadianDQN   │  │CircadianRhythm│  │DQNScheduler│  │
│  │Model          │  │Model          │  │            │  │
│  └───────────────┘  └───────────────┘  └────────────┘  │
└─────────────────────────┬──────────────────────────────┘
                          │
                          ▼
┌────────────────────────────────────────────────────────┐
│                  Database Layer                         │
│  ┌───────────────┐  ┌───────────────┐  ┌────────────┐  │
│  │User Profiles  │  │Task Data      │  │Schedule Data│  │
│  └───────────────┘  └───────────────┘  └────────────┘  │
└────────────────────────────────────────────────────────┘
```

## Data Flow

### Dynamic Schedule Rebalancing Flow

1. **Data Collection**:
   - User task data and preferences are collected
   - Circadian pattern data (sleep times, energy levels, productive periods)
   - Historical task completion and productivity metrics
   - Current schedule and calendar constraints

2. **Circadian Pattern Detection**:
   - CircadianRhythmModel analyzes temporal data to detect energy patterns
   - User's individual peak productivity windows are identified
   - Energy curves are generated for different times of day

3. **Task Classification**:
   - Tasks are categorized by cognitive demand (focus-intensive, creative, routine, administrative)
   - Energy requirements for each task type are determined
   - Temporal suitability is calculated based on task type and time of day

4. **Schedule Optimization**:
   - CircadianDQNModel applies reinforcement learning to optimize schedule
   - Tasks are matched to time slots based on circadian patterns
   - Optimization considers task priorities, deadlines, and dependencies
   - Model learns from past successes and failures in schedule adherence

5. **Feedback Integration**:
   - User feedback on schedule quality is incorporated
   - Completion rates and task abandonment inform model updates
   - Continuous learning improves personalization over time

## Component Details

### CircadianDQNModel

The CircadianDQNModel extends the base DQNScheduler with circadian rhythm awareness:

- **Extended State Space**: Incorporates time-of-day and energy level features into the state representation
- **Circadian-Aware Reward Function**: Rewards actions that align tasks with appropriate energy levels
- **Temporal Suitability Calculation**: Evaluates how suitable a given time is for a specific task type
- **Energy-Task Matching**: Optimizes allocation of tasks based on energy requirements and current energy levels

Implementation Location: `app/ml/models/adhd17_reinforcement_model.py`

Key methods:
- `create_state_with_circadian_features()`: Augments state representation with circadian data
- `calculate_circadian_reward()`: Computes rewards based on circadian alignment
- `combine_rewards()`: Integrates standard task rewards with circadian rewards

### CircadianRhythmModel

The CircadianRhythmModel predicts user energy patterns throughout the day:

- **Energy Curve Prediction**: Generates hourly energy level predictions (0-10 scale)
- **Harmonic Modeling**: Uses harmonic components to model circadian oscillations
- **Personalization**: Adapts to individual user patterns over time
- **Sleep Data Integration**: Incorporates sleep schedule to improve predictions

Implementation Location: `app/ml/models/energy_optimizer_model.py`

Key methods:
- `predict_energy_levels()`: Generates hourly energy predictions
- `generate_energy_curve()`: Creates a complete energy curve for scheduling
- `detect_optimal_windows()`: Identifies optimal time periods for different task types

### TaskCognitiveProfile

Helper class for categorizing tasks by cognitive demands:

- **Task Categorization**: Classifies tasks into cognitive demand categories
- **Energy Requirements**: Determines energy needed for different task types
- **Temporal Suitability**: Calculates optimal timing for different task categories

Implementation Location: `app/ml/models/adhd17_reinforcement_model.py`

Key methods:
- `categorize_task()`: Determines the cognitive demand category for a task
- `get_energy_requirements()`: Returns energy level needed for a task category
- `calculate_temporal_suitability()`: Computes how suitable a time slot is for a task

### TemporalPatternRecognitionService

Integration service that connects all components:

- **Service Orchestration**: Coordinates interaction between models
- **Data Processing**: Prepares and transforms data for model consumption
- **API Exposure**: Provides unified interface for client applications

Implementation Location: `app/ml/temporal_pattern_recognition.py`

## Data Models

### CircadianCalendarOptimizationRequest

Request schema for calendar optimization:

```python
class CircadianCalendarOptimizationRequest(BaseModel):
    start_date: datetime
    end_date: datetime
    tasks: List[TaskSchema]
    preferences: Optional[UserPreferences] = None
```

### CircadianCalendarOptimizationResponse

Response schema with optimized schedule:

```python
class CircadianCalendarOptimizationResponse(BaseModel):
    schedule: List[OptimizedTimeBlock]
    energy_curve: List[HourlyEnergyLevel]
    message: str
```

### TaskSchema

Task representation with cognitive demand information:

```python
class TaskSchema(BaseModel):
    id: Optional[str]
    title: str
    description: Optional[str]
    duration_minutes: int
    focus_required: Optional[int] = None
    executive_function_load: Optional[int] = None
    creative_required: Optional[int] = None
    complexity: Optional[int] = None
    priority: TaskPriority
    is_flexible: bool = True
    deadline: Optional[datetime] = None
```

## API Endpoints

### /api/scheduling/circadian-optimize

Optimizes schedule using CircadianDQN model:

- **Method**: POST
- **Request Body**: `CircadianCalendarOptimizationRequest`
- **Response**: `CircadianCalendarOptimizationResponse`
- **Description**: Generates an optimized schedule based on circadian patterns and task cognitive demands

Implementation Location: `app/routes/scheduling_routes.py`

### /api/scheduling/apply-circadian-optimization

Applies a generated optimization to the user's calendar:

- **Method**: POST
- **Request Body**: `ApplyCircadianOptimizationRequest`
- **Response**: `ApplyCircadianOptimizationResponse` 
- **Description**: Applies a previously generated schedule optimization to the user's actual calendar

Implementation Location: `app/routes/scheduling_routes.py`

## Integration Points

### Integration with Epic 1 (Temporal Pattern Recognition)

- Utilizes the TemporalPatternRecognitionService from Epic 1
- Leverages CircadianRhythmModel for energy curve predictions
- Incorporates historical productivity data for pattern detection

### Integration with Epic 2 (Task Management)

- Uses task data and metadata from Task Management system
- Implements task classification based on cognitive demands
- Provides optimized scheduling back to Task Management

### Integration with Epic 3 (Notification System)

- Sends notifications about optimal task timing
- Alerts users to schedule rebalancing opportunities
- Delivers feedback requests for continual improvement

## Performance Considerations

- **Model Optimization**: CircadianDQNModel uses efficient tensor operations to ensure fast predictions
- **Batch Processing**: Schedule optimization runs in batch mode to reduce computational load
- **Caching**: Energy curves are cached to avoid redundant calculations
- **Asynchronous Processing**: Long-running optimizations use async processing to avoid blocking

## Security Considerations

- **Privacy Protection**: User circadian data is treated as sensitive information
- **Data Minimization**: Only necessary data is retained for model training
- **Consent Management**: Clear user consent is required for data collection
- **On-Device Processing**: When possible, sensitive calculations occur on the user's device

## Error Handling

- **Graceful Degradation**: Falls back to basic scheduling when advanced features fail
- **Error Logging**: Comprehensive logging of model failures for debugging
- **User Feedback**: Clear error messages provided to users
- **Recovery Mechanisms**: Automatic retry logic for transient failures

## Future Enhancements

- **Advanced Sleep Integration**: Direct integration with sleep tracking devices
- **Medication Timing**: Incorporating medication effects into the circadian model
- **Cross-User Patterns**: Learning from anonymized population-level patterns
- **Environmental Factors**: Accounting for weather, location, and environmental impacts on energy

## Implementation Roadmap

1. **Phase 1**: Core CircadianDQNModel and basic integration (Completed)
2. **Phase 2**: Task cognitive profiling and temporal suitability (Completed)
3. **Phase 3**: Full API endpoints and service integration (Completed)
4. **Phase 4**: User feedback loop and model refinement (In Progress)
5. **Phase 5**: Advanced optimizations and performance tuning (Planned)

## Testing Strategy

- **Unit Tests**: Individual component testing with pytest
- **Integration Tests**: End-to-end workflow testing
- **Simulation Testing**: Model evaluation with simulated user data
- **A/B Testing**: Comparing schedule adherence with and without circadian optimization 