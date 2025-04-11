# Epic 2: Implementation Documentation - Stochastic Time Estimation Engine

This document provides technical implementation details for Epic 2: Stochastic Time Estimation Engine.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Architecture Diagram](#architecture-diagram)
3. [Data Flow](#data-flow)
4. [Component Details](#component-details)
5. [Data Models](#data-models)
6. [Database Migrations](#database-migrations)
7. [Integration Points](#integration-points)
8. [Performance Considerations](#performance-considerations)
9. [Security Considerations](#security-considerations)
10. [Error Handling](#error-handling)
11. [Future Enhancements](#future-enhancements)
12. [Implementation Roadmap](#implementation-roadmap)

## Architecture Overview

Epic 2 implements a stochastic time estimation engine to help ADHD users more accurately estimate task durations, accounting for variability in focus, environmental factors, and task complexity. It consists of four primary components:

1. **BayesianDurationPredictor**: A probabilistic model that provides realistic task duration estimates with confidence intervals, based on historical data and contextual factors.

2. **NLPComplexityAnalyzer**: A natural language processing model that analyzes task descriptions to determine cognitive complexity, ambiguity, and required effort.

3. **ContextualStressorDetector**: A real-time monitoring system that identifies environmental and physiological stressors likely to impact productivity and focus.

4. **TimeBufferCalculator**: An algorithm that determines optimal time buffers between tasks, accounting for transition difficulties and cognitive load.

The components work together to provide comprehensive time estimation that adapts to the user's unique ADHD profile, current context, and task-specific factors, reducing the anxiety and pressure associated with unrealistic time expectations.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                          Client Applications                         │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       API Gateway / Load Balancer                    │
└───────────┬──────────────────┬───────────────────┬──────────────────┘
            │                  │                   │
            ▼                  ▼                   ▼
┌────────────────────┐ ┌────────────────┐ ┌────────────────────┐
│Bayesian Duration   │ │NLP Complexity   │ │Contextual Stressor │
│Predictor Service   │ │Analyzer Service │ │Detector Service    │
└─────────┬──────────┘ └────────┬───────┘ └──────────┬─────────┘
          │                     │                    │
          │                     ▼                    │
          │         ┌────────────────────────┐      │
          └────────►│Time Estimation Database◄──────┘
                    └────────────┬───────────┘
                                 │
                                 ▼
                   ┌─────────────────────────────┐
                   │Time Buffer Calculator       │
                   │Service                      │
                   └──────────┬──────────────────┘
                              │
                              ▼
                   ┌─────────────────────────┐
                   │Calendar & Task          │
                   │Integration Service      │
                   └─────────────────────────┘
```

## Data Flow

### Task Duration Prediction Flow

1. **Input Collection**:
   - User creates or selects a task requiring time estimation
   - System collects task description, category, and current context
   - Historical completion data for similar tasks is retrieved

2. **Complexity Analysis**:
   - NLP model processes task description
   - Task complexity metrics are calculated
   - Cognitive load and sub-task estimation is performed

3. **Contextual Adjustment**:
   - Current user state and environment are analyzed
   - Stressor impact is calculated
   - Focus capacity adjustments are applied

4. **Duration Calculation**:
   - Bayesian model generates duration distribution
   - Confidence intervals are calculated
   - Final prediction is presented with explanation

### Buffer Calculation Flow

1. **Transition Analysis**:
   - Previous and next task context is collected
   - Cognitive load difference is calculated
   - Historical transition time data is analyzed

2. **Stressor Incorporation**:
   - Current stressors are detected and quantified
   - Stressor impact on transitions is calculated
   - Recovery time requirements are estimated

3. **Buffer Optimization**:
   - Optimal buffer time is calculated
   - Buffer components are itemized
   - Recommendations are generated

4. **Schedule Integration**:
   - Buffer is applied to calendar or task list
   - Visual indicators show buffer purpose
   - User feedback is collected for future refinement

### Learning and Adaptation Flow

1. **Outcome Collection**:
   - Actual task completion times are recorded
   - User feedback on estimation accuracy is collected
   - Contextual factors during task execution are logged

2. **Model Update**:
   - Bayesian model parameters are updated
   - NLP feature weights are adjusted
   - Buffer calculations are refined

3. **Pattern Recognition**:
   - Long-term patterns in estimation accuracy are identified
   - User-specific adjustment factors are calculated
   - Systematic biases are detected and corrected

## Component Details

### BayesianDurationPredictor

**Purpose**: Provides probabilistic task duration estimates based on historical data, task characteristics, and current context.

**Implementation Location**: `app/ml/stochastic_time_estimation/bayesian_predictor.py`

**Key Methods**:
- `predict_duration(task_data, user_context, user_id)`: Generates duration prediction with confidence intervals
- `update_model(task_id, actual_duration, completion_context)`: Updates model with actual completion data
- `get_similar_tasks(task_description, user_id)`: Finds similar historical tasks for reference
- `generate_duration_distribution(task_data)`: Creates probability distribution of possible durations

**Dependencies**:
- PyMC3 for Bayesian statistical modeling
- Pandas for data manipulation
- SQLAlchemy for database interactions
- Scipy for statistical calculations

**Algorithm Details**:
- Hierarchical Bayesian model with task-type and user-specific priors
- Multi-factor regression for context adjustment
- Monte Carlo simulation for uncertainty estimation
- Thompson sampling for exploration vs. exploitation balance

**Error Handling**:
- Fallback to category averages when personal data is insufficient
- Graceful degradation with explicit confidence reduction
- Outlier detection and handling for data quality
- Progressive disclosure of details based on confidence

**Performance Optimizations**:
- Pre-computed priors for common task types
- Cached MCMC traces for faster incremental updates
- Vectorized operations for batch predictions
- Asynchronous model updates

### NLPComplexityAnalyzer

**Purpose**: Analyzes task descriptions to determine complexity, cognitive load, and effort requirements.

**Implementation Location**: `app/ml/stochastic_time_estimation/nlp_analyzer.py`

**Key Methods**:
- `analyze_complexity(task_description, task_type)`: Calculates overall task complexity
- `extract_requirements(task_description)`: Identifies explicit and implicit requirements
- `estimate_cognitive_load(task_description)`: Estimates cognitive demand of the task
- `detect_ambiguity(task_description)`: Quantifies clarity and specificity of the description

**Dependencies**:
- SpaCy for NLP processing
- HuggingFace Transformers for language models
- NLTK for text analysis
- Scikit-learn for feature extraction

**Algorithm Details**:
- Fine-tuned BERT model for domain-specific complexity analysis
- Named entity recognition for technical concept identification
- Dependency parsing for structural complexity assessment
- Text statistics for readability and clarity metrics

**Error Handling**:
- Confidence scores for all predictions
- Fallback to simpler analysis for very short descriptions
- Language detection and non-English handling
- Invalid input protection with meaningful errors

**Performance Optimizations**:
- Model quantization for faster inference
- Batch processing for multiple tasks
- Feature caching for similar descriptions
- On-demand loading of heavy NLP models

### ContextualStressorDetector

**Purpose**: Identifies and quantifies environmental and physiological factors that may impact task performance.

**Implementation Location**: `app/ml/stochastic_time_estimation/stressor_detector.py`

**Key Methods**:
- `detect_current_stressors(user_id, wearable_data, environment_data)`: Identifies active stressors
- `calculate_focus_impact(stressors, user_profile)`: Estimates impact on focus and productivity
- `generate_recovery_suggestions(stressors, user_preferences)`: Provides personalized recovery strategies
- `track_stressor_patterns(user_id, timeframe)`: Analyzes patterns in stressor occurrence

**Dependencies**:
- TensorFlow for stressor impact models
- Pandas for time-series analysis
- Scikit-learn for pattern detection
- SQLAlchemy for database interactions

**Algorithm Details**:
- Multivariate anomaly detection for stressor identification
- Personalized stress sensitivity profiles
- Time-series pattern recognition for recurring stressors
- Recommendation system for evidence-based recovery strategies

**Error Handling**:
- Default stressor profiles when wearable data is unavailable
- Confidence ratings for all detected stressors
- Explicit assumptions when filling missing data
- Graceful handling of sensor disconnections

**Performance Optimizations**:
- Incremental analysis of streaming sensor data
- Edge computing options for privacy and latency
- Feature importance-based computation prioritization
- Adaptive polling frequency based on context

### TimeBufferCalculator

**Purpose**: Calculates optimal transition time between tasks based on cognitive load, task types, and user state.

**Implementation Location**: `app/ml/stochastic_time_estimation/buffer_calculator.py`

**Key Methods**:
- `calculate_optimal_buffer(user_id, task_duration, task_context)`: Determines appropriate buffer time
- `analyze_transition_difficulty(previous_task, next_task)`: Assesses cognitive switching cost
- `get_transition_statistics(user_id, transition_type)`: Provides historical transition data
- `suggest_transition_activities(buffer_time, transition_type)`: Recommends activities for transition periods

**Dependencies**:
- NumPy for numerical operations
- Pandas for data analysis
- Scikit-learn for machine learning components
- SQLAlchemy for database interactions

**Algorithm Details**:
- Regression model for base buffer prediction
- Task similarity matrix for transition difficulty
- Decision trees for context-specific adjustments
- Reinforcement learning for personalized buffer optimization

**Error Handling**:
- Minimum buffer enforcement for all transitions
- Clear confidence indicators for recommendations
- Fallback to type-based averages when personal data is insufficient
- Explainable recommendations with factor breakdown

**Performance Optimizations**:
- Pre-computed transition matrices for common task pairs
- Cached user profiles for frequent calculations
- Asynchronous updates to transition statistics
- Progressive computation depth based on available time

## Data Models

### TaskDurationEstimate

**Purpose**: Stores information about task duration estimates and actual outcomes.

**Implementation Location**: `app/models/task_duration_estimate.py`

**Fields**:
- `id` (UUID): Primary key
- `user_id` (UUID): Foreign key to User table
- `task_id` (UUID): Foreign key to Task table
- `task_description` (Text): Description of the task
- `task_type` (String): Category of task
- `estimated_duration_minutes` (Integer): Predicted duration
- `confidence_lower_bound` (Integer): Lower bound of confidence interval
- `confidence_upper_bound` (Integer): Upper bound of confidence interval
- `actual_duration_minutes` (Integer): Actual time taken (null until completed)
- `estimation_factors` (JSON): Factors that influenced the estimate
- `context_at_estimation` (JSON): User context when estimate was made
- `context_at_completion` (JSON): User context when task was completed
- `created_at` (DateTime): Record creation timestamp
- `updated_at` (DateTime): Record update timestamp

**Indexes**:
- Index on (`user_id`, `created_at`)
- Index on (`user_id`, `task_type`)
- Index on (`task_id`)

**Relationships**:
- Many-to-one with User
- Many-to-one with Task
- One-to-many with TimeBuffer

### TaskComplexityAnalysis

**Purpose**: Stores the results of complexity analysis for tasks.

**Implementation Location**: `app/models/task_complexity.py`

**Fields**:
- `id` (UUID): Primary key
- `task_id` (UUID): Foreign key to Task table
- `complexity_score` (Float): Overall complexity rating (0-100)
- `cognitive_load` (Float): Estimated cognitive demand (0-10)
- `ambiguity_index` (Float): Measure of task clarity (0-10)
- `estimated_subtasks` (Integer): Number of implicit subtasks
- `language_features` (JSON): Linguistic characteristics of description
- `technical_terms` (Array): Domain-specific terms identified
- `complexity_factors` (JSON): Factors contributing to complexity
- `created_at` (DateTime): Record creation timestamp
- `analyzer_version` (String): Version of the analyzer used

**Indexes**:
- Primary index on `id`
- Index on `task_id`
- Index on (`task_id`, `created_at`)

**Relationships**:
- One-to-one with Task
- Many-to-one with TaskDurationEstimate

### UserStressorRecord

**Purpose**: Tracks detected stressors and their impact on the user.

**Implementation Location**: `app/models/user_stressor.py`

**Fields**:
- `id` (UUID): Primary key
- `user_id` (UUID): Foreign key to User table
- `timestamp` (DateTime): When stressor was detected
- `stressor_type` (String): Category of stressor
- `stressor_details` (JSON): Specific details about the stressor
- `intensity` (Float): Measured intensity (0-10)
- `duration_minutes` (Integer): How long stressor was active
- `focus_impact` (Float): Estimated impact on focus (0-10)
- `cognitive_impact` (Float): Estimated impact on cognition (0-10)
- `detection_confidence` (Float): Confidence in detection (0-1)
- `wearable_metrics` (JSON): Raw metrics from wearable devices
- `environmental_metrics` (JSON): Environmental measurements
- `created_at` (DateTime): Record creation timestamp

**Indexes**:
- Index on (`user_id`, `timestamp`)
- Index on (`user_id`, `stressor_type`)
- Index on (`timestamp`) (for time-series analysis)

**Relationships**:
- Many-to-one with User
- Many-to-many with TaskExecution

### TimeBuffer

**Purpose**: Stores information about calculated time buffers between tasks.

**Implementation Location**: `app/models/time_buffer.py`

**Fields**:
- `id` (UUID): Primary key
- `user_id` (UUID): Foreign key to User table
- `prev_task_id` (UUID): Foreign key to Task table (previous task)
- `next_task_id` (UUID): Foreign key to Task table (next task)
- `recommended_buffer_minutes` (Integer): Calculated optimal buffer
- `actual_buffer_minutes` (Integer): Actual buffer used (if known)
- `buffer_components` (JSON): Breakdown of buffer components
- `transition_difficulty` (Float): Estimated transition difficulty (0-10)
- `context_factors` (JSON): Contextual factors during calculation
- `user_override` (Boolean): Whether user manually adjusted the buffer
- `created_at` (DateTime): Record creation timestamp
- `updated_at` (DateTime): Record update timestamp

**Indexes**:
- Index on (`user_id`, `created_at`)
- Index on (`prev_task_id`, `next_task_id`)
- Index on (`user_id`, `transition_difficulty`)

**Relationships**:
- Many-to-one with User
- Many-to-one with Task (prev_task)
- Many-to-one with Task (next_task)
- Many-to-one with TaskDurationEstimate

## Database Migrations

Database migrations for Epic 2 are managed using Alembic and can be found in the following locations:

### Initial Schema Migrations

- `migrations/versions/20230501_create_task_duration_estimate.py`: Creates TaskDurationEstimate table
- `migrations/versions/20230502_create_task_complexity_analysis.py`: Creates TaskComplexityAnalysis table
- `migrations/versions/20230503_create_user_stressor_record.py`: Creates UserStressorRecord table
- `migrations/versions/20230504_create_time_buffer.py`: Creates TimeBuffer table

### Schema Updates

- `migrations/versions/20230601_add_confidence_metrics.py`: Adds confidence metrics to duration estimates
- `migrations/versions/20230615_add_stressor_impact_fields.py`: Adds impact metrics to stressor records
- `migrations/versions/20230620_add_buffer_components.py`: Adds detailed component breakdown to buffers

### Index Optimizations

- `migrations/versions/20230701_optimize_task_duration_index.py`: Adds performance-oriented indexes
- `migrations/versions/20230715_add_stressor_time_series_index.py`: Adds time-series optimized index

### Migration Commands

To apply migrations:
```
alembic upgrade head
```

To generate a new migration:
```
alembic revision -m "description_of_change"
```

## Integration Points

### Database Integration

- **PostgreSQL with TimescaleDB**: Primary data store
  - Connection configured in `config/database.py`
  - Time-series optimizations for stressor data
  - JSONB columns for flexible storage of context data

### Machine Learning Infrastructure

- **Model Serving**: TensorFlow Serving
  - REST API for model prediction endpoints
  - Batch prediction support for efficiency
  - Model versioning for controlled rollout

- **Model Training**: Kubernetes-based training jobs
  - Scheduled retraining pipelines
  - Performance monitoring and alerting
  - Data validation and integrity checks

### Task Management Integration

- **Task API**: Retrieves task information
  - Task properties and metadata
  - User-specific task history
  - Task dependencies and relationships
  - Implemented in `app/integrations/task_manager.py`

### Calendar Integration

- **Calendar Provider API**:
  - Event scheduling and modification
  - Free/busy time queries
  - Buffer visualization
  - Implemented in `app/integrations/calendar_provider.py`

### Wearable Device Integration

- **Wearable Data API**:
  - Real-time physiological metrics
  - Activity and sleep data
  - Multiple device support (Fitbit, Apple Watch, etc.)
  - Implemented in `app/integrations/wearable_provider.py`

### Environment Monitoring

- **Environment Sensor API**:
  - Noise level monitoring
  - Light and temperature data
  - Location context
  - Optional smart home integration
  - Implemented in `app/integrations/environment_monitor.py`

## Performance Considerations

### Model Optimization

1. **Bayesian Model Efficiency**:
   - Variational inference for faster computation
   - Incremental posterior updates rather than full recomputation
   - Cached MCMC traces for common scenarios
   - Performance: Average prediction time < 150ms

2. **NLP Model Performance**:
   - Distilled BERT models for reduced latency
   - Quantized model weights for memory efficiency
   - Feature caching for repeated analysis
   - Performance: Average analysis time < 200ms for typical descriptions

### Data Management

1. **Time-Series Optimization**:
   - TimescaleDB hypertables for stressor data
   - Automatic partitioning by time
   - Efficient downsampling for historical data
   - Retention policies for data lifecycle management

2. **Query Performance**:
   - Materialized views for common analysis patterns
   - Partial indexes based on access patterns
   - Execution plan optimization for complex queries
   - Average query response time < 50ms for common operations

### Scaling Strategy

1. **Horizontal Scaling**:
   - Stateless API services for linear scaling
   - Redis-based distributed caching
   - Load balancing with sticky sessions for batch operations
   - Designed to handle 500+ requests/second per node

2. **Resource Management**:
   - Automatic scaling based on request queue depth
   - GPU acceleration for batch predictions where available
   - Prioritization of interactive vs. background operations
   - Resource quotas to prevent service degradation

## Security Considerations

### Data Protection

1. **Personal Data Handling**:
   - End-to-end encryption for sensitive data
   - Data minimization principles applied
   - Anonymization for non-essential identifiers
   - Retention periods aligned with purpose

2. **Storage Security**:
   - Encrypted database at rest
   - Secure backup strategy with encryption
   - Strict access controls at database level
   - Regular security audits

### Authentication and Authorization

1. **API Security**:
   - OAuth 2.0 with OpenID Connect
   - JWTs with appropriate expiration
   - Role-based access control
   - Detailed audit logging of sensitive operations

2. **Internal Service Authentication**:
   - Mutual TLS for service-to-service communication
   - Service account management
   - Principle of least privilege for service accounts
   - Automated credential rotation

### Privacy Considerations

1. **User Control**:
   - Granular permissions for data collection
   - Transparent data usage explanations
   - Easy opt-out mechanisms
   - Data export and deletion capabilities

2. **Sensor Data**:
   - Local processing when possible
   - Aggregate metrics over raw data
   - Clear indicators when sensing is active
   - Minimized data retention for raw signals

## Error Handling

### Service Error Handling

1. **Prediction Failures**:
   - Graceful degradation to simpler models
   - Clear confidence indicators on all predictions
   - Fallback to historical averages
   - User notification for significant degradation

2. **Integration Failures**:
   - Circuit breakers for dependent services
   - Partial results with explicit incompleteness indicators
   - Cached recent responses for temporary outages
   - Asynchronous retry mechanisms

### Client-Facing Error Handling

1. **Error Responses**:
   - Consistent JSON error format
   - HTTP status codes matched to error types
   - Human-readable error messages
   - Machine-readable error codes for automation

2. **Validation Errors**:
   - Field-level validation messages
   - Suggested corrections when possible
   - Clear minimum requirements
   - Contextual help references

## Future Enhancements

### Model Improvements

1. **Advanced Prediction Models**:
   - Transformer-based sequence models for task dependencies
   - Reinforcement learning for continuous improvement
   - Multi-task learning across time estimation components
   - Personalized error correction models

2. **Contextual Awareness**:
   - Fine-grained location-based context detection
   - Integration with digital activity monitoring
   - Social context awareness (collaborators, meetings)
   - Proactive stressor prediction

### Technical Enhancements

1. **Real-time Capabilities**:
   - Streaming analytics for continuous monitoring
   - WebSocket APIs for live updates
   - Progressive computation with incremental results
   - Edge computing for privacy-sensitive operations

2. **Integration Enhancements**:
   - GraphQL API for flexible data access
   - Expanded calendar system integrations
   - Advanced wearable device support
   - Smart home integration for environment control

### User Experience Improvements

1. **Explainable AI**:
   - Natural language explanations of estimates
   - Visual breakdown of factors affecting duration
   - Interactive "what-if" analysis
   - Confidence visualization techniques

2. **Personalization**:
   - Learning user terminology and task patterns
   - Adapting to individual ADHD presentation
   - Time-of-day and day-of-week specialization
   - Medication effectiveness integration

## Implementation Roadmap

### Phase 1: Foundation (Completed)

| Feature | Description | Timeline | Status |
|---------|-------------|----------|--------|
| Basic Bayesian Model | Core duration prediction capability | Weeks 1-4 | Completed |
| Simple NLP Analysis | Basic complexity assessment | Weeks 2-5 | Completed |
| Initial Stressor Detection | Fundamental stressor identification | Weeks 3-6 | Completed |
| Basic Buffer Calculation | Minimum viable buffer calculation | Weeks 4-7 | Completed |

### Phase 2: Enhancement (Completed)

| Feature | Description | Timeline | Status |
|---------|-------------|----------|--------|
| Advanced Bayesian Features | Hierarchical modeling, advanced priors | Weeks 8-11 | Completed |
| Enhanced NLP Capabilities | BERT-based analysis, technical term detection | Weeks 9-12 | Completed |
| Multi-source Stressor Detection | Wearable integration, environment detection | Weeks 10-13 | Completed |
| Context-aware Buffer Calculation | Transition difficulty modeling | Weeks 11-14 | Completed |

### Phase 3: Integration (In Progress)

| Feature | Description | Timeline | Status |
|---------|-------------|----------|--------|
| Unified Prediction Pipeline | End-to-end estimation workflow | Weeks 15-18 | In Progress |
| Calendar System Integration | Buffer visualization, schedule optimization | Weeks 16-19 | In Progress |
| Feedback Loop Implementation | Continuous learning from outcomes | Weeks 17-20 | In Progress |
| Mobile Experience | On-device components, notifications | Weeks 18-21 | Planned |

### Phase 4: Advanced Features (Planned)

| Feature | Description | Timeline | Status |
|---------|-------------|----------|--------|
| Explainable Predictions | Natural language explanations, confidence visualization | Weeks 22-25 | Planned |
| Social Context Awareness | Meeting impact, collaboration factors | Weeks 23-26 | Planned |
| Proactive Recommendations | Preventative stressor management | Weeks 24-27 | Planned |
| Personalized Optimization | Individual ADHD presentation adaptation | Weeks 25-28 | Planned |
