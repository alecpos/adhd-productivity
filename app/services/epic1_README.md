# Epic 1: Temporal Pattern Recognition (TPR) Models - Service Documentation

## Table of Contents
- [Overview](#overview)
- [Components](#components)
  - [ProductivityPatternLSTM](#productivitypatternlstm)
  - [CircadianRhythmModel](#circadianrhythmmodel)
  - [ProductivityCorrelationSystem](#productivitycorrelationsystem)
  - [MentalHealthFederatedModel](#mentalhealthfederatedmodel)
- [Dependencies](#dependencies)
- [Configuration](#configuration)
- [Deployment](#deployment)
- [Monitoring](#monitoring)
- [Troubleshooting](#troubleshooting)
- [Testing](#testing)
- [Documentation](#documentation)

## Overview

The Temporal Pattern Recognition (TPR) services are designed to help individuals with ADHD understand and leverage their natural productivity patterns. These services analyze historical productivity data to identify optimal working times, energy fluctuations, and factors that impact focus and task completion.

The TPR system addresses several key ADHD-related challenges:
- Difficulty identifying personal productivity patterns
- Inconsistent energy levels throughout the day
- Challenges in understanding factors that affect focus
- Need for privacy-preserving mental health insights

## Components

### ProductivityPatternLSTM

**Purpose**: Analyzes historical task completion data to identify optimal productivity windows and patterns.

**Location**: `app/services/ml/productivity_pattern_lstm/`

**Key Features**:
- Productivity heatmap generation by time of day and day of week
- Optimal window detection for different task types
- Flexibility analysis for scheduled tasks
- Adaptive learning from user feedback

**Performance Characteristics**:
- Training time: ~2 minutes on initial dataset, ~30 seconds for incremental updates
- Prediction latency: <100ms for pattern queries
- Memory usage: ~200MB during training, ~50MB during inference
- Accuracy: 85-92% for predicting optimal windows after 3 weeks of data

**Usage Example**:
```python
from app.services.ml.productivity_pattern_lstm import ProductivityPatternLSTM

# Initialize with user ID
lstm_model = ProductivityPatternLSTM(user_id="user123")

# Get optimal windows for a specific task type
optimal_windows = lstm_model.get_optimal_windows(
    task_type="deep_work",
    day_of_week="monday",
    duration_minutes=90
)

# Get productivity heatmap for the week
weekly_heatmap = lstm_model.generate_productivity_heatmap(
    granularity_minutes=30,
    include_weekends=True
)
```

**Error Handling**:
- Insufficient data: Returns confidence scores with predictions; below threshold, falls back to population averages
- Training failures: Logs detailed error, retains previous model version
- Prediction errors: Returns error code with fallback recommendations

### CircadianRhythmModel

**Purpose**: Models user's natural energy levels throughout the day to optimize task scheduling.

**Location**: `app/services/ml/circadian_rhythm/`

**Key Features**:
- Daily energy curve prediction
- Task-energy matching algorithm
- Sleep impact analysis
- Medication timing optimization

**Performance Characteristics**:
- Model update time: ~1 minute daily
- Prediction latency: <50ms for energy queries
- Memory usage: ~150MB during training, ~30MB during inference
- Accuracy: 75-85% for energy level predictions after 2 weeks of data

**Usage Example**:
```python
from app.services.ml.circadian_rhythm import CircadianRhythmModel

# Initialize with user ID
rhythm_model = CircadianRhythmModel(user_id="user123")

# Get predicted energy levels for a specific time range
energy_levels = rhythm_model.predict_energy_levels(
    start_time="2023-06-01T09:00:00",
    end_time="2023-06-01T17:00:00",
    granularity_minutes=30
)

# Get optimal time for a task requiring high energy
optimal_time = rhythm_model.get_optimal_time_for_task(
    energy_requirement="high",
    duration_minutes=60,
    date="2023-06-01"
)
```

**Error Handling**:
- Missing sleep data: Interpolates from available data with reduced confidence scores
- Anomalous predictions: Applies smoothing algorithms and flags unusual patterns
- Integration failures: Falls back to basic model with clear indication of reduced accuracy

### ProductivityCorrelationSystem

**Purpose**: Identifies correlations between various factors and productivity metrics.

**Location**: `app/services/ml/productivity_correlation/`

**Key Features**:
- Multi-factor correlation analysis
- Insight generation engine
- Pattern clustering
- Experiment suggestion system

**Performance Characteristics**:
- Correlation analysis time: ~3 minutes for full analysis, ~30 seconds for incremental updates
- Query latency: <200ms for correlation queries
- Memory usage: ~300MB during analysis, ~70MB during querying
- Statistical significance: Enforces p<0.05 with multiple testing correction

**Usage Example**:
```python
from app.services.ml.productivity_correlation import ProductivityCorrelationSystem

# Initialize with user ID
correlation_system = ProductivityCorrelationSystem(user_id="user123")

# Get top factors correlated with productivity
top_correlations = correlation_system.get_top_correlations(
    metric="task_completion_rate",
    limit=5,
    min_confidence=0.7
)

# Get actionable insights
insights = correlation_system.generate_insights(
    category="sleep",
    actionable_only=True,
    max_insights=3
)
```

**Error Handling**:
- Insufficient data: Requires minimum thresholds for correlation analysis, returns clear messages
- Spurious correlations: Applies multiple testing correction and confidence intervals
- Processing errors: Logs detailed diagnostics, falls back to partial results with warnings

### MentalHealthFederatedModel

**Purpose**: Provides population-level insights while preserving privacy of sensitive mental health data.

**Location**: `app/services/ml/federated_learning/`

**Key Features**:
- Federated learning infrastructure
- Differential privacy implementation
- Anonymous comparison engine
- Granular privacy controls

**Performance Characteristics**:
- Local model update: ~30 seconds
- Global model update: Runs daily, taking ~20 minutes
- Query latency: <150ms for insight queries
- Privacy guarantee: ε-differential privacy with ε=3.0

**Usage Example**:
```python
from app.services.ml.federated_learning import MentalHealthFederatedModel

# Initialize with user ID
federated_model = MentalHealthFederatedModel(user_id="user123")

# Get anonymous comparisons
comparisons = federated_model.get_anonymous_comparisons(
    metric="productivity_variance",
    demographic_filters={
        "age_range": "25-34",
        "adhd_type": "primarily_inattentive"
    }
)

# Update privacy settings
federated_model.update_privacy_settings(
    contribute_data=True,
    privacy_level="high",
    allowed_categories=["productivity", "sleep"]
)
```

**Error Handling**:
- Privacy budget exceeded: Enforces strict limits with clear user messaging
- Federation failures: Gracefully degrades to local-only mode
- Demographic filter issues: Provides minimum group size guarantees, rejects overly specific queries

## Dependencies

### Database Access
- **PostgreSQL**: Primary data store for user productivity data
  - Connection parameters in `config/database.yml`
  - Required tables: `productivity_sessions`, `energy_levels`, `task_completions`, `user_factors`
- **Redis**: Caching layer for model predictions
  - Connection parameters in `config/redis.yml`
  - Cache TTL: 1 hour for predictions, 24 hours for heatmaps

### External Services
- **Wearable API Gateway**: For sleep and activity data
  - Configuration in `config/integrations/wearables.yml`
  - Supports: Fitbit, Apple Health, Google Fit, Garmin
- **Calendar Integration Service**: For schedule data
  - Configuration in `config/integrations/calendars.yml`
  - Supports: Google Calendar, Outlook, Apple Calendar
- **Notification Service**: For delivering insights
  - Configuration in `config/notifications.yml`
  - Supports: Push, Email, SMS

### Utility Libraries
- **TensorFlow**: For LSTM and neural network models
  - Version: 2.9.0+
  - GPU acceleration configured in `config/tensorflow.yml`
- **PyTorch**: For federated learning models
  - Version: 1.12.0+
  - Configuration in `config/pytorch.yml`
- **Pandas & NumPy**: For data processing
  - Pandas version: 1.4.0+
  - NumPy version: 1.22.0+
- **Scikit-learn**: For correlation analysis
  - Version: 1.1.0+
- **PySyft**: For federated learning and differential privacy
  - Version: 0.5.0+
  - Configuration in `config/federated_learning.yml`

## Configuration

### Core Configuration

All services use environment variables with sensible defaults defined in `.env.example`:

```
# ProductivityPatternLSTM Configuration
LSTM_HIDDEN_LAYERS=2
LSTM_HIDDEN_UNITS=128
LSTM_DROPOUT_RATE=0.2
LSTM_LEARNING_RATE=0.001
LSTM_BATCH_SIZE=32
LSTM_MIN_DATA_POINTS=50

# CircadianRhythmModel Configuration
CIRCADIAN_MODEL_TYPE=bayesian
CIRCADIAN_SMOOTHING_FACTOR=0.3
CIRCADIAN_MIN_DATA_DAYS=5
CIRCADIAN_UPDATE_FREQUENCY_HOURS=24

# ProductivityCorrelationSystem Configuration
CORRELATION_MIN_SAMPLES=20
CORRELATION_SIGNIFICANCE_THRESHOLD=0.05
CORRELATION_MIN_EFFECT_SIZE=0.2
CORRELATION_MAX_FACTORS=50

# MentalHealthFederatedModel Configuration
FEDERATED_PRIVACY_EPSILON=3.0
FEDERATED_MIN_CLIENTS=10
FEDERATED_AGGREGATION_FREQUENCY_HOURS=24
FEDERATED_MIN_LOCAL_EPOCHS=5
```

### Advanced Configuration

Additional configuration files in `config/` directory:

- **Feature Flags**: `config/features.yml` - Controls enabling/disabling specific features
- **Model Hyperparameters**: `config/model_hyperparams/` - Detailed model configurations
- **Integration Settings**: `config/integrations/` - API keys and endpoints for third-party services
- **Privacy Settings**: `config/privacy.yml` - Default privacy settings and limits
- **Logging Configuration**: `config/logging.yml` - Log levels, formats, and destinations

## Deployment

### System Requirements

- **CPU**: 4+ cores recommended (2 minimum)
- **RAM**: 8GB+ recommended (4GB minimum)
- **Disk**: 20GB+ for model storage and caching
- **GPU**: Optional but recommended for training acceleration
- **Network**: Outbound access to wearable and calendar APIs
- **Database**: PostgreSQL 13+ with TimescaleDB extension

### Container Deployment

Docker images are available for all services:

```bash
# Pull the latest images
docker pull adhdcalendar/productivity-pattern-lstm:latest
docker pull adhdcalendar/circadian-rhythm-model:latest
docker pull adhdcalendar/productivity-correlation:latest
docker pull adhdcalendar/mental-health-federated:latest

# Run with environment configuration
docker run -d \
  --name productivity-pattern-lstm \
  --env-file .env \
  -p 8001:8000 \
  -v model-data:/app/models \
  adhdcalendar/productivity-pattern-lstm:latest
```

### Kubernetes Deployment

Helm charts are available in the `deploy/charts/` directory:

```bash
# Deploy all TPR services
helm install tpr-services ./deploy/charts/tpr-services \
  --namespace adhd-calendar \
  --values ./deploy/environments/production.yaml

# Scale specific components
kubectl scale deployment productivity-pattern-lstm --replicas=3 -n adhd-calendar
```

### Scaling Considerations

- **ProductivityPatternLSTM**: CPU-bound during training, memory-bound during inference
  - Horizontal scaling recommended for inference
  - Vertical scaling helpful for training
- **CircadianRhythmModel**: Lightweight, scales horizontally easily
- **ProductivityCorrelationSystem**: Memory-intensive during analysis
  - Consider memory-optimized instances
- **MentalHealthFederatedModel**: Network and CPU intensive during aggregation
  - Schedule aggregation during off-peak hours

### Health Checks

All services expose health endpoints:

- **Readiness**: `/health/ready` - Returns 200 when service is ready to accept requests
- **Liveness**: `/health/live` - Returns 200 when service is running
- **Model Status**: `/health/model` - Returns model version and last update timestamp

## Monitoring

### Health Checks

All services implement the following health check endpoints:

- **GET /health/live**: Basic liveness check
- **GET /health/ready**: Readiness check including dependencies
- **GET /health/model**: Model health and version information

### Metrics

Prometheus metrics are exposed on `/metrics` for all services:

- **Request Metrics**:
  - `tpr_requests_total{service="service_name", endpoint="endpoint_name"}`: Request count
  - `tpr_request_duration_seconds{service="service_name", endpoint="endpoint_name"}`: Request duration
  - `tpr_request_errors_total{service="service_name", endpoint="endpoint_name", error_type="error_type"}`: Error count

- **Model Metrics**:
  - `tpr_model_prediction_count{model="model_name"}`: Prediction count
  - `tpr_model_training_duration_seconds{model="model_name"}`: Training duration
  - `tpr_model_accuracy{model="model_name"}`: Model accuracy metrics
  - `tpr_model_last_update_timestamp{model="model_name"}`: Last model update time

- **Resource Metrics**:
  - `tpr_memory_usage_bytes{service="service_name"}`: Memory usage
  - `tpr_cpu_usage_percent{service="service_name"}`: CPU usage
  - `tpr_disk_usage_bytes{service="service_name"}`: Disk usage for model storage

### Alerting Rules

Recommended Prometheus alerting rules in `monitoring/prometheus/alert_rules.yml`:

```yaml
groups:
- name: TPRServiceAlerts
  rules:
  - alert: TPRServiceDown
    expr: up{job=~"tpr-.*"} == 0
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "TPR service {{ $labels.job }} is down"

  - alert: TPRHighErrorRate
    expr: rate(tpr_request_errors_total[5m]) / rate(tpr_requests_total[5m]) > 0.05
    for: 10m
    labels:
      severity: warning
    annotations:
      summary: "High error rate on {{ $labels.service }} ({{ $labels.endpoint }})"

  - alert: TPRModelUpdateFailure
    expr: time() - tpr_model_last_update_timestamp > 86400
    for: 1h
    labels:
      severity: warning
    annotations:
      summary: "Model {{ $labels.model }} has not been updated in 24 hours"
```

### Logging

All services use structured JSON logging with the following fields:

- `timestamp`: ISO8601 timestamp
- `service`: Service name
- `level`: Log level (INFO, WARN, ERROR, DEBUG)
- `message`: Log message
- `trace_id`: Request trace ID for distributed tracing
- `user_id`: Anonymized user ID (when applicable)
- `component`: Component within the service
- `duration_ms`: Operation duration (when applicable)
- `error`: Error details (when applicable)

Log levels can be configured in `config/logging.yml` and are set to INFO by default.

## Troubleshooting

### Common Issues

#### ProductivityPatternLSTM

| Issue | Symptoms | Resolution |
|-------|----------|------------|
| Insufficient training data | Low confidence scores, fallback to defaults | Ensure user has at least 2 weeks of task completion data |
| Model divergence | Erratic predictions, high loss values | Reset model weights, adjust learning rate, check for data anomalies |
| Memory leaks | Increasing memory usage over time | Restart service, update to latest version with fix |
| Slow predictions | High latency on prediction endpoints | Check Redis cache status, optimize model size, scale horizontally |

#### CircadianRhythmModel

| Issue | Symptoms | Resolution |
|-------|----------|------------|
| Missing sleep data | Gaps in energy predictions | Implement interpolation, prompt user for manual input |
| Inconsistent patterns | Low confidence scores, high variance | Increase smoothing factor, extend data collection period |
| Integration failures | Missing wearable data | Check API credentials, implement fallback to manual input |
| Timezone issues | Shifted predictions after travel | Detect timezone changes, adjust model accordingly |

#### ProductivityCorrelationSystem

| Issue | Symptoms | Resolution |
|-------|----------|------------|
| Spurious correlations | Too many weak correlations | Adjust significance threshold, implement multiple testing correction |
| Analysis timeout | Long-running queries, timeouts | Optimize query patterns, implement incremental analysis |
| Data sparsity | Few significant correlations | Guide users to track more consistent factors |
| High memory usage | OOM errors during analysis | Batch processing, optimize memory usage, scale vertically |

#### MentalHealthFederatedModel

| Issue | Symptoms | Resolution |
|-------|----------|------------|
| Privacy budget exceeded | Rejected contribution requests | Reset budget on schedule, educate users on privacy limits |
| Federation failures | Stuck on "updating global model" | Implement timeout and fallback, check network connectivity |
| Model divergence | Declining accuracy metrics | Implement stronger regularization, check for adversarial contributions |
| Small comparison groups | "Insufficient data" for comparisons | Broaden demographic filters, increase minimum group size |

### Diagnostic Tools

- **Model Inspection**: `/debug/model` endpoint (admin access only)
  - Returns model architecture, weights summary, and recent performance metrics
- **Log Analysis**: Structured logs can be queried in Elasticsearch
  - Example: `service:productivity-pattern-lstm AND level:ERROR`
- **Performance Profiling**: `/debug/profile` endpoint (admin access only)
  - Returns CPU and memory profiling information
- **Dependency Check**: `/health/dependencies` endpoint
  - Returns status of all dependencies with detailed error information

### Recovery Procedures

- **Model Rollback**:
  ```bash
  # Rollback to previous model version
  curl -X POST https://api.adhdcalendar.com/v1/admin/models/rollback \
    -H "Authorization: Bearer ${ADMIN_TOKEN}" \
    -d '{"service": "productivity-pattern-lstm", "version": "previous"}'
  ```

- **Data Reprocessing**:
  ```bash
  # Trigger reprocessing of user data
  curl -X POST https://api.adhdcalendar.com/v1/admin/data/reprocess \
    -H "Authorization: Bearer ${ADMIN_TOKEN}" \
    -d '{"user_id": "user123", "service": "circadian-rhythm-model"}'
  ```

- **Cache Invalidation**:
  ```bash
  # Invalidate prediction cache
  curl -X POST https://api.adhdcalendar.com/v1/admin/cache/invalidate \
    -H "Authorization: Bearer ${ADMIN_TOKEN}" \
    -d '{"service": "productivity-correlation-system"}'
  ```

## Testing

### Test Locations

- **Unit Tests**: `app/tests/ml/temporal_pattern_recognition/unit/`
  - Test individual functions and methods in isolation
- **Integration Tests**: `app/tests/ml/temporal_pattern_recognition/integration/`
  - Test interactions between components
- **End-to-End Tests**: `app/tests/ml/temporal_pattern_recognition/e2e/`
  - Test complete workflows from data ingestion to prediction
- **Performance Tests**: `app/tests/ml/temporal_pattern_recognition/performance/`
  - Benchmark performance under various loads

### Running Tests

```bash
# Run all TPR tests
pytest app/tests/ml/temporal_pattern_recognition/

# Run specific test category
pytest app/tests/ml/temporal_pattern_recognition/unit/

# Run tests for specific component
pytest app/tests/ml/temporal_pattern_recognition/unit/test_productivity_pattern_lstm.py

# Run performance tests
pytest app/tests/ml/temporal_pattern_recognition/performance/ --benchmark
```

### Test Data

- **Synthetic Data**: `app/tests/ml/temporal_pattern_recognition/data/synthetic/`
  - Generated data for reproducible tests
- **Anonymized Data**: `app/tests/ml/temporal_pattern_recognition/data/anonymized/`
  - Real-world anonymized data for realistic testing
- **Edge Cases**: `app/tests/ml/temporal_pattern_recognition/data/edge_cases/`
  - Data designed to test boundary conditions and error handling

## Documentation

- **API Documentation**: `docs/epic1_api.md`
  - Comprehensive API reference for all TPR services
- **Implementation Details**: `docs/epic1_implementation.md`
  - Technical implementation details and architecture
- **User Guide**: `docs/epic1_user_guide.md`
  - End-user documentation for TPR features
- **Integration Guide**: `docs/integration/tpr_integration.md`
  - Guide for integrating with TPR services
- **Model Documentation**: `app/services/ml/model_docs/`
  - Detailed documentation for each ML model
