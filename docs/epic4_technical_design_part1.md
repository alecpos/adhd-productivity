# Epic 4: Technical Design Document - Part 1
# Dynamic Schedule Rebalancing with Circadian Rhythm Optimization

## Document Information

- **Status**: Draft
- **Version**: 1.0
- **Last Updated**: 2023-09-15
- **Author(s)**: ADHD Calendar Team

## Introduction

This technical design document describes the implementation details for Epic 4: Dynamic Schedule Rebalancing, with a particular focus on the Circadian Rhythm Optimization functionality. This epic addresses key challenges faced by users with ADHD in maintaining an effective schedule aligned with their natural energy patterns.

### Purpose

The Dynamic Schedule Rebalancing system aims to:

1. Detect and model users' individual circadian rhythm patterns
2. Categorize tasks based on cognitive demands
3. Match tasks to optimal time periods based on energy levels
4. Dynamically adjust schedules when disruptions occur
5. Continuously learn and improve from user feedback

### Target Users

The primary users of this system are individuals with ADHD who:
- Experience variable energy and focus levels throughout the day
- Struggle with executive function needed for effective scheduling
- Find traditional scheduling approaches too rigid or ineffective
- Need help aligning task types with optimal cognitive states

### Key Technical Challenges

The implementation must address several technical challenges:

1. **Personalization**: Each user has unique circadian patterns requiring individualized models
2. **Limited Training Data**: Initial predictions must be reasonable even with limited user data
3. **Noisy Feedback**: User-reported energy levels may be inconsistent or subjective
4. **Real-time Adaptation**: Schedule adjustments must happen quickly when plans change
5. **Privacy Concerns**: Sensitive data about user patterns must be handled securely

## System Architecture

### High-Level Architecture

The Dynamic Schedule Rebalancing system is implemented as a set of interrelated services that work together to analyze patterns, predict energy levels, and optimize task scheduling. The architecture follows a service-oriented design with clear API boundaries and data flow patterns.

#### System Components

1. **Circadian Model Service**: Manages the models that predict user energy patterns
2. **Task Profiling Service**: Analyzes and categorizes tasks based on cognitive demands
3. **Schedule Optimization Service**: Allocates tasks to time slots based on predictions
4. **Feedback Collection Service**: Gathers and processes user feedback on energy and task completion
5. **Model Training Pipeline**: Continuously improves models based on collected data

#### Key Interfaces

1. **Client API Gateway**: REST-based interface for client applications
2. **Internal Service Communication**: gRPC-based service-to-service communication
3. **Event Bus**: Kafka streams for event-driven processes
4. **Data Storage**: PostgreSQL for relational data, MongoDB for document storage, Redis for caching

### Detailed Component Architecture

#### 1. Circadian Model Service

The Circadian Model Service is responsible for generating and managing user-specific energy prediction models.

**Key Components**:

- **CircadianProfileManager**: Maintains user circadian profiles
- **EnergyPatternPredictor**: Generates hourly energy level predictions
- **CircadianModelTrainer**: Trains and updates user-specific models
- **PatternDetectionEngine**: Identifies recurring patterns in user data

**Dependencies**:
- MongoDB for storing model parameters
- Redis for caching energy predictions
- TensorFlow Serving for model inference

**API Endpoints**:
- `GET /circadian/energy-curve`: Retrieve energy predictions for a time period
- `POST /circadian/report-energy`: Record user-reported energy levels
- `GET /circadian/model-status`: Get information about model quality

**Internal Methods**:
- `predictUserEnergy(userId, timestamp)`: Predict energy level at a specific time
- `detectOptimalWindows(userId, date, activityType)`: Find optimal time windows
- `updateModelWithFeedback(userId, feedbackData)`: Update model parameters

#### 2. Task Profiling Service

The Task Profiling Service analyzes tasks to determine their cognitive demands and optimal scheduling characteristics.

**Key Components**:
- **CognitiveProfiler**: Analyzes task metadata and descriptions
- **NLPAnalyzer**: Extracts insights from task descriptions using NLP
- **TaskCategoryManager**: Maintains taxonomy of task categories
- **UserPreferenceIntegrator**: Incorporates user preferences into recommendations

**Dependencies**:
- PostgreSQL for task data
- SpaCy for NLP processing
- scikit-learn for classification models

**API Endpoints**:
- `POST /tasks/analyze-cognitive-demands`: Analyze cognitive demands of a task
- `GET /tasks/cognitive-completion-analytics`: Get analytics about task completion

**Internal Methods**:
- `extractTaskFeatures(taskData)`: Extract feature vectors from task data
- `classifyTaskByDemand(taskFeatures)`: Classify task into cognitive demand categories
- `estimateEnergyRequired(taskId)`: Estimate energy needed for a task
- `predictOptimalTimeOfDay(taskId, userId)`: Predict best time of day for a task

#### 3. Schedule Optimization Service

The Schedule Optimization Service uses reinforcement learning to optimize task allocation based on energy predictions.

**Key Components**:
- **CircadianDQNModel**: Specialized reinforcement learning model
- **ScheduleOptimizer**: Core optimization algorithm
- **ConstraintProcessor**: Handles scheduling constraints and conflicts
- **CalendarIntegrationManager**: Integrates with calendar systems

**Dependencies**:
- TensorFlow for DQN model implementation
- PostgreSQL for schedule data
- Redis for optimization job queue

**API Endpoints**:
- `POST /scheduling/circadian-optimize`: Generate optimized schedule
- `POST /scheduling/apply-circadian-optimization`: Apply optimization to calendar

**Internal Methods**:
- `generateOptimizedSchedule(userId, tasks, timeRange)`: Create optimal schedule
- `evaluateScheduleQuality(schedule)`: Score schedule based on multiple factors
- `adjustForInterruptions(userId, schedule, newEvents)`: Dynamically adjust schedule

## Core Technical Components

### CircadianDQNModel

The CircadianDQNModel extends traditional Deep Q-Network reinforcement learning to incorporate circadian awareness.

**Key Features**:
- Circadian-aware state representation
- Energy-sensitive reward function
- Time-dependent action evaluation
- Progressive learning rate adjustment

**Implementation Details**:
- **State Space**: Includes task properties, time features, and energy predictions
- **Action Space**: Placement of tasks in time slots, with breaks and buffers
- **Reward Function**: Weighted combination of energy alignment, priority, deadline proximity
- **Training Approach**: Begins with general population data, then personalizes with user data

```python
class CircadianDQNModel:
    def __init__(self, user_id, config):
        self.user_id = user_id
        self.config = config
        self.model = self._build_model()
        self.energy_predictor = EnergyPredictionClient()
        self.target_model = self._build_model()  # Target network for stability
        self.update_target_network()
        
    def _build_model(self):
        model = Sequential()
        model.add(Dense(64, input_dim=self.state_dim, activation='relu'))
        model.add(Dense(64, activation='relu'))
        model.add(Dense(self.action_dim, activation='linear'))
        model.compile(loss='mse', optimizer=Adam(lr=self.config.learning_rate))
        return model
        
    def create_state_with_circadian_features(self, tasks, time_slots, current_schedule):
        """Creates a state representation including circadian features"""
        base_state = self._create_base_state(tasks, time_slots, current_schedule)
        energy_levels = self.energy_predictor.get_levels(self.user_id, time_slots)
        circadian_features = self._extract_circadian_features(energy_levels)
        return np.concatenate([base_state, circadian_features])
        
    def calculate_circadian_reward(self, task, time_slot):
        """Calculates reward component based on circadian alignment"""
        energy_level = self.energy_predictor.get_level(self.user_id, time_slot)
        task_demand = self._get_task_cognitive_demand(task)
        alignment_score = self._calculate_alignment(energy_level, task_demand)
        return self.config.circadian_weight * alignment_score
        
    def combine_rewards(self, circadian_reward, standard_reward):
        """Combines circadian and standard rewards"""
        total_reward = (circadian_reward + 
                       self.config.priority_weight * standard_reward.priority_component +
                       self.config.deadline_weight * standard_reward.deadline_component)
        return total_reward
        
    def update_with_feedback(self, task_id, time_slot, completion_rate, satisfaction):
        """Updates model based on task completion feedback"""
        # Implementation details for incorporating feedback
```

### CircadianRhythmModel

The CircadianRhythmModel predicts a user's energy levels throughout the day using a combination of harmonic analysis and machine learning.

**Key Features**:
- Personalized energy curve prediction
- Multiple energy dimension tracking (focus, creativity, executive function)
- Adaptation to changing user patterns
- Cold-start handling for new users

**Implementation Details**:
- **Base Model**: Population-level defaults by demographic group
- **Personalization Layer**: User-specific adjustments learned from data
- **Temporal Features**: Time of day, day of week, seasonal factors
- **External Factors**: Sleep data, activity data, medication timing

```python
class CircadianRhythmModel:
    def __init__(self, user_id):
        self.user_id = user_id
        self.base_parameters = self._load_base_parameters()
        self.user_parameters = self._load_user_parameters()
        self.harmonic_components = self._initialize_harmonic_components()
        
    def predict_energy_levels(self, timestamp):
        """Predicts energy level at a specific timestamp"""
        base_prediction = self._get_base_prediction(timestamp)
        user_adjustment = self._get_user_adjustment(timestamp)
        context_adjustment = self._get_context_adjustment(timestamp)
        
        return {
            'energy_level': base_prediction.energy + user_adjustment.energy + context_adjustment.energy,
            'focus_capacity': base_prediction.focus + user_adjustment.focus + context_adjustment.focus,
            'creative_capacity': base_prediction.creative + user_adjustment.creative + context_adjustment.creative,
            'executive_function_capacity': base_prediction.ef + user_adjustment.ef + context_adjustment.ef
        }
        
    def generate_energy_curve(self, date, resolution_minutes=60):
        """Generates a complete energy curve for a day"""
        timestamps = self._generate_timestamps(date, resolution_minutes)
        predictions = [self.predict_energy_levels(ts) for ts in timestamps]
        return list(zip(timestamps, predictions))
        
    def detect_optimal_windows(self, date, capacity_type, threshold=0.7):
        """Identifies optimal time windows for a specific capacity type"""
        energy_curve = self.generate_energy_curve(date)
        windows = []
        current_window = None
        
        for timestamp, prediction in energy_curve:
            capacity = prediction[capacity_type]
            
            if capacity >= threshold and current_window is None:
                current_window = {'start': timestamp, 'capacity': capacity}
            elif capacity < threshold and current_window is not None:
                current_window['end'] = timestamp
                current_window['average_capacity'] = self._calculate_window_average(
                    current_window['start'], current_window['end'], capacity_type)
                windows.append(current_window)
                current_window = None
                
        return windows
        
    def update_with_reported_level(self, timestamp, reported_levels):
        """Updates model with user-reported energy levels"""
        # Implementation for incorporating user feedback
``` 