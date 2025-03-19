# Stochastic Time Estimation Engine Services

This document provides comprehensive information about the Stochastic Time Estimation Engine services, which collectively enable accurate and personalized time estimation for individuals with ADHD.

## Table of Contents
- [Overview](#overview)
- [Components](#components)
- [Dependencies](#dependencies)
- [Configuration](#configuration)
- [Deployment](#deployment)
- [Monitoring](#monitoring)
- [Troubleshooting](#troubleshooting)
- [Testing](#testing)
- [Documentation](#documentation)

## Overview

The Stochastic Time Estimation Engine (STE) services are designed to address one of the core challenges faced by individuals with ADHD: accurately estimating how long tasks will take. This system acknowledges the variability and uncertainty in task duration for ADHD individuals, providing realistic estimates that account for personal patterns, context, and task-specific factors.

### Key Challenges Addressed

1. **Time Blindness**: Many people with ADHD struggle with "time blindness," a difficulty perceiving and estimating time intervals accurately.

2. **Contextual Variability**: Task duration can vary significantly based on environmental conditions, physiological state, and mental energy levels.

3. **Task Complexity Underestimation**: Tasks with complex or ambiguous descriptions are often severely underestimated.

4. **Transition Difficulties**: Time required to transition between different types of tasks is rarely accounted for.

### System Objectives

The STE system provides:

- Probabilistic time estimates with realistic confidence intervals
- Personalized predictions based on historical patterns
- Complexity assessment of task descriptions
- Detection of environmental and physiological stressors
- Optimal buffer time calculations for task transitions
- Continuous learning and adaptation based on actual outcomes

## Components

### BayesianDurationPredictor

**Description**: A probabilistic model that provides personalized task duration estimates with confidence intervals based on historical completion data, task attributes, and current context.

**Key Features**:
- Personalized duration predictions with confidence intervals
- Similar task identification for novel tasks
- Continuous learning from actual completion times
- Uncertainty quantification based on data availability

**Input Sources**:
- Task descriptions and categories
- Historical task completion data
- Current user context
- Stressor information

**Output Destinations**:
- Calendar system API for scheduling
- Frontend UI for time estimates
- Notification service for updates
- Analytics service for tracking

**Performance Characteristics**:
- Training Time: ~3 minutes for user model updates
- Prediction Latency: <120ms per prediction
- Accuracy: 80-90% of actual times within confidence interval
- Memory Usage: ~250MB during prediction

### NLPComplexityAnalyzer

**Description**: An NLP model that assesses the complexity, cognitive load, and ambiguity of task descriptions to inform duration predictions.

**Key Features**:
- Cognitive complexity scoring
- Implicit subtask detection
- Ambiguity quantification
- Technical term identification

**Input Sources**:
- Task descriptions
- Task categories/types
- Historical analysis data
- Domain-specific terminology

**Output Destinations**:
- BayesianDurationPredictor (for estimations)
- User interface (for complexity insights)
- Task management system (for subtask suggestions)

**Performance Characteristics**:
- Analysis Time: <200ms per task description
- Accuracy: 85% agreement with human raters
- Resource Usage: ~150MB memory during processing
- Batch Processing: Up to 100 tasks/second

### ContextualStressorDetector

**Description**: A system that identifies and quantifies environmental and physiological factors that may impact task performance and duration.

**Key Features**:
- Real-time stressor detection
- Focus impact assessment
- Recovery time estimation
- Stressor pattern analysis

**Input Sources**:
- Wearable device data (heart rate, HRV, etc.)
- Environmental sensors (noise, light, etc.)
- Self-reported focus levels
- Calendar and schedule information

**Output Destinations**:
- BayesianDurationPredictor (for context adjustment)
- TimeBufferCalculator (for buffer adjustments)
- User interface (for stressor insights)
- Notification service (for environmental suggestions)

**Performance Characteristics**:
- Processing Latency: <150ms for real-time analysis
- Stressor Detection Accuracy: 75-85%
- Battery Impact (Mobile): Low (optimized processing)
- Data Usage: ~20KB per analysis

### TimeBufferCalculator

**Description**: An algorithm that determines optimal time buffers between tasks based on task characteristics, transition difficulty, and current context.

**Key Features**:
- Transition difficulty assessment
- Context-aware buffer calculation
- Historical transition analysis
- Transition activity recommendations

**Input Sources**:
- Task pair information
- User transition history
- Current stressor information
- Schedule constraints

**Output Destinations**:
- Calendar system (for buffer scheduling)
- User interface (for buffer explanation)
- Notification system (for transition reminders)

**Performance Characteristics**:
- Calculation Time: <100ms per buffer
- Accuracy: 70-80% of users report improved transitions
- Storage Requirements: Minimal (<50MB)
- API Calls: ~5 calls per calculation

## Dependencies

### External Services

| Service | Purpose | Access Method | SLA Requirements |
|---------|---------|--------------|-----------------|
| User Profile Service | Access to user preferences and ADHD profile | REST API | 99.9% uptime, <100ms response |
| Calendar Integration | Schedule access and modification | OAuth API | 99.5% uptime, <500ms response |
| Task Management | Task details and history | GraphQL API | 99.5% uptime, <300ms response |
| Notification Service | User alerts and reminders | Message Queue | 99% delivery within 5s |
| Analytics Service | Usage data and performance metrics | REST API | 99% uptime, batch processing |

### Libraries and Frameworks

| Library | Version | Purpose | License |
|---------|---------|---------|---------|
| PyMC3 | 3.11.5 | Bayesian statistical modeling | Apache 2.0 |
| TensorFlow | 2.9.0 | ML model training and inference | Apache 2.0 |
| SpaCy | 3.4.0 | NLP processing | MIT |
| HuggingFace Transformers | 4.21.0 | Language models | Apache 2.0 |
| FastAPI | 0.88.0 | API framework | MIT |
| SQLAlchemy | 1.4.40 | Database ORM | MIT |
| Pandas | 1.5.0 | Data manipulation | BSD |
| Redis-py | 4.3.4 | Caching and rate limiting | MIT |

### Database Requirements

| Database | Purpose | Data Stored | Backup Strategy |
|----------|---------|------------|----------------|
| PostgreSQL (TimescaleDB) | Primary data store | Task history, estimates, complexity, stressors | Daily backups, 30-day retention |
| Redis | Caching and rate limiting | Temporary results, session data | Persistence enabled, 3-day retention |
| Vector DB (Pinecone) | Semantic task similarity | Task embedding vectors | Weekly backups |

## Configuration

### Core Configuration

The STE services use a centralized configuration system based on environment variables with reasonable defaults. Key configuration values include:

| Parameter | Description | Default | Environment Variable |
|-----------|-------------|---------|---------------------|
| `database_url` | PostgreSQL connection string | `postgres://user:pass@localhost:5432/ste` | `STE_DATABASE_URL` |
| `redis_url` | Redis connection string | `redis://localhost:6379/0` | `STE_REDIS_URL` |
| `log_level` | Logging verbosity | `INFO` | `STE_LOG_LEVEL` |
| `api_rate_limit` | API requests per minute | `60` | `STE_API_RATE_LIMIT` |
| `model_cache_size` | ML model cache size | `512MB` | `STE_MODEL_CACHE_SIZE` |
| `worker_concurrency` | Background worker count | `4` | `STE_WORKER_CONCURRENCY` |

### BayesianDurationPredictor Configuration

| Parameter | Description | Default | Environment Variable |
|-----------|-------------|---------|---------------------|
| `prediction_confidence_level` | Confidence interval level | `0.80` | `STE_PREDICTION_CONFIDENCE` |
| `minimum_samples_required` | Min samples for personalization | `5` | `STE_MIN_SAMPLES` |
| `mcmc_samples` | MCMC sample count | `1000` | `STE_MCMC_SAMPLES` |
| `max_similar_tasks` | Similar tasks to consider | `10` | `STE_MAX_SIMILAR_TASKS` |

### NLPComplexityAnalyzer Configuration

| Parameter | Description | Default | Environment Variable |
|-----------|-------------|---------|---------------------|
| `model_size` | NLP model size (small/medium/large) | `medium` | `STE_NLP_MODEL_SIZE` |
| `complexity_factors_count` | Top factors to report | `5` | `STE_COMPLEXITY_FACTORS` |
| `ambiguity_threshold` | Threshold for ambiguity warning | `7.0` | `STE_AMBIGUITY_THRESHOLD` |
| `language_detection_enabled` | Auto-detect input language | `true` | `STE_LANG_DETECTION` |

### ContextualStressorDetector Configuration

| Parameter | Description | Default | Environment Variable |
|-----------|-------------|---------|---------------------|
| `wearable_data_batch_size` | Wearable data points to process | `60` | `STE_WEARABLE_BATCH` |
| `stressor_detection_threshold` | Minimum confidence for detection | `0.65` | `STE_STRESSOR_THRESHOLD` |
| `environment_polling_interval` | Environment check frequency | `300` | `STE_ENV_POLL_INTERVAL` |
| `use_default_stressor_profile` | Fall back to defaults if no data | `true` | `STE_USE_DEFAULT_PROFILE` |

### TimeBufferCalculator Configuration

| Parameter | Description | Default | Environment Variable |
|-----------|-------------|---------|---------------------|
| `minimum_buffer_minutes` | Minimum buffer to recommend | `5` | `STE_MIN_BUFFER` |
| `maximum_buffer_minutes` | Maximum buffer to recommend | `60` | `STE_MAX_BUFFER` |
| `transition_history_window_days` | Days of history to consider | `30` | `STE_TRANSITION_HISTORY` |
| `buffer_granularity_minutes` | Buffer time rounding | `5` | `STE_BUFFER_GRANULARITY` |

## Deployment

### System Requirements

| Resource | Minimum | Recommended | High-Traffic |
|----------|---------|------------|-------------|
| CPU | 2 cores | 4 cores | 8+ cores |
| RAM | 4GB | 8GB | 16GB+ |
| Disk | 20GB SSD | 50GB SSD | 100GB+ SSD |
| Network | 50Mbps | 100Mbps | 1Gbps |

### Container Deployment

The STE services are containerized using Docker and can be deployed with the following commands:

```bash
# Pull the latest images
docker pull adhd-calendar/bayesian-predictor:latest
docker pull adhd-calendar/nlp-analyzer:latest
docker pull adhd-calendar/stressor-detector:latest
docker pull adhd-calendar/buffer-calculator:latest

# Run with configuration
docker run -d --name bayesian-predictor \
  -e STE_DATABASE_URL=postgres://user:pass@db:5432/ste \
  -e STE_REDIS_URL=redis://redis:6379/0 \
  -p 8001:8000 \
  adhd-calendar/bayesian-predictor:latest

# Similar commands for other services...
```

### Kubernetes Deployment

For production environments, Kubernetes deployment is recommended using Helm:

```bash
# Add the repository
helm repo add adhd-calendar https://charts.adhd-calendar.io

# Install the STE chart
helm install ste adhd-calendar/stochastic-time-engine \
  --set database.url=postgres://user:pass@db:5432/ste \
  --set redis.url=redis://redis:6379/0 \
  --set global.environment=production
```

### Scaling Considerations

* **BayesianDurationPredictor**: CPU-bound, scales horizontally with stateless prediction
* **NLPComplexityAnalyzer**: Memory-bound, benefits from vertical scaling for larger models
* **ContextualStressorDetector**: I/O-bound for sensor data, benefits from connection pooling
* **TimeBufferCalculator**: Lightweight, can scale horizontally with minimal resources

## Monitoring

### Health Check Endpoints

Each service exposes a health check endpoint at `/health` which returns:

```json
{
  "status": "healthy",
  "version": "1.2.3",
  "dependencies": {
    "database": "connected",
    "redis": "connected",
    "model_service": "connected"
  },
  "uptime_seconds": 3600
}
```

### Prometheus Metrics

Metrics are exposed at `/metrics` in Prometheus format. Key metrics include:

**Request Metrics**:
- `ste_requests_total{service="bayesian_predictor", endpoint="/predict"}`: Total requests
- `ste_request_duration_seconds{service="bayesian_predictor", endpoint="/predict"}`: Request duration
- `ste_request_errors_total{service="bayesian_predictor", endpoint="/predict", error_type="validation"}`: Errors by type

**Model Metrics**:
- `ste_prediction_confidence{service="bayesian_predictor"}`: Average confidence
- `ste_prediction_error_minutes{service="bayesian_predictor"}`: Average error (vs. actual)
- `ste_model_latency_ms{service="nlp_analyzer", model_size="medium"}`: Model inference time

**Resource Metrics**:
- `ste_database_query_duration_seconds{service="stressor_detector", query_type="insert"}`: DB performance
- `ste_cache_hit_ratio{service="buffer_calculator"}`: Cache efficiency
- `ste_memory_usage_bytes{service="nlp_analyzer"}`: Memory consumption

### Alerting Rules

Recommended Prometheus alerting rules:

```yaml
- alert: STEHighErrorRate
  expr: rate(ste_request_errors_total[5m]) / rate(ste_requests_total[5m]) > 0.05
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "High error rate in STE service"
    description: "Service {{ $labels.service }} has error rate above 5% for 5 minutes"

- alert: STEHighLatency
  expr: histogram_quantile(0.95, rate(ste_request_duration_seconds_bucket[5m])) > 1.0
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "High latency in STE service"
    description: "Service {{ $labels.service }} has P95 latency above 1s for 5 minutes"
```

## Troubleshooting

### Common Issues

#### BayesianDurationPredictor

| Issue | Symptoms | Resolution |
|-------|----------|------------|
| Cold start problem | New users receive generic estimates | Ensure fallback estimation strategy is configured |
| Low confidence intervals | Very wide prediction ranges | Check `minimum_samples_required` setting; may need more data |
| Slow prediction response | API latency >500ms | Check cache settings, review database indexes, optimize MCMC settings |
| Outdated model | Predictions diverging from actuals | Verify model update job is running on schedule |

#### NLPComplexityAnalyzer

| Issue | Symptoms | Resolution |
|-------|----------|------------|
| Memory issues | Service OOM errors | Reduce model size or increase container memory |
| Language detection failure | Analysis failing for non-English | Enable explicit language detection or provide language hint |
| Poor complexity estimates | User feedback indicating mismatches | Check for domain-specific terms in analysis, may need model fine-tuning |
| Slow analysis | High latency on complex descriptions | Consider model quantization or batch processing |

#### ContextualStressorDetector

| Issue | Symptoms | Resolution |
|-------|----------|------------|
| Missing wearable data | No stressor detection | Configure fallback to default profiles |
| False positive stressors | Overestimated impact on focus | Adjust stressor detection threshold |
| Wearable connection issues | Intermittent data | Implement retry logic, cache last known good values |
| High battery consumption | User reports of device drain | Reduce polling frequency, optimize data processing |

#### TimeBufferCalculator

| Issue | Symptoms | Resolution |
|-------|----------|------------|
| Buffer recommendations too small | User reports of rushing | Increase minimum buffer setting |
| Buffer recommendations too large | Excessive idle time in schedule | Review buffer components, adjust maximums |
| Inconsistent recommendations | Buffers vary widely for similar transitions | Check transition history window, might need more data points |
| Integration failure | Buffers not appearing in calendar | Verify calendar service integration and permissions |

### Diagnostic Tools

- **Log Analysis**:
  ```bash
  # View recent errors
  kubectl logs -l app=bayesian-predictor --tail=100 | grep ERROR
  
  # Check specific user issues
  kubectl logs -l app=bayesian-predictor --tail=1000 | grep "user_id=123456"
  ```

- **Database Diagnostics**:
  ```bash
  # Check slow queries
  psql -U user -d ste -c "SELECT * FROM pg_stat_activity WHERE state='active' ORDER BY duration DESC LIMIT 10;"
  ```

- **Performance Testing**:
  ```bash
  # Benchmark API performance
  hey -n 1000 -c 50 -H "Authorization: Bearer $TOKEN" https://api.adhd-calendar.io/ste/v1/predict
  ```

### Recovery Procedures

- **Service Restart**:
  ```bash
  kubectl rollout restart deployment/bayesian-predictor
  ```

- **Database Recovery**:
  ```bash
  # Restore from backup
  pg_restore -U user -d ste ./backups/ste_backup_20230615.dump
  ```

- **Cache Reset**:
  ```bash
  # Flush Redis cache
  redis-cli -h redis.adhd-calendar.io FLUSHDB
  ```

## Testing

### Test Environments

| Environment | Purpose | Access Method | Data |
|-------------|---------|--------------|------|
| Development | Local testing | localhost:8000 | Synthetic data |
| Staging | Integration testing | staging-api.adhd-calendar.io | Anonymized production data |
| Production | Live service | api.adhd-calendar.io | Production data |

### Test Data

Test datasets are available in the `tests/data` directory:

- `test_tasks.json`: 100 diverse task descriptions with actual durations
- `test_contexts.json`: Various user contexts for testing predictions
- `test_stressors.json`: Simulated stressor patterns
- `test_transitions.json`: Task transition examples with actual buffer times

### Automated Tests

| Test Type | Command | Coverage |
|-----------|---------|----------|
| Unit Tests | `python -m pytest tests/unit` | 95% |
| Integration Tests | `python -m pytest tests/integration` | 85% |
| End-to-End Tests | `python -m pytest tests/e2e` | 70% |
| Performance Tests | `python -m pytest tests/performance` | N/A |

### Manual Testing Procedures

1. **Prediction Accuracy Testing**:
   - Create a task with standard description
   - Record predicted duration and confidence interval
   - Complete task and record actual time
   - Verify actual falls within confidence interval

2. **Complexity Analysis Testing**:
   - Submit various task descriptions of known complexity
   - Verify complexity scores align with expected values
   - Test with ambiguous descriptions to check detection

3. **Stressor Impact Testing**:
   - Simulate different stressor combinations
   - Verify appropriate impact on predictions
   - Test with and without wearable data

4. **Buffer Calculation Testing**:
   - Create task sequences with known transition difficulty
   - Verify buffer recommendations are appropriate
   - Test with different user contexts and stressors

## Documentation

### API Documentation

Full API documentation is available at:
- OpenAPI Spec: `/openapi.json`
- Swagger UI: `/docs`
- ReDoc: `/redoc`

### Example Workflows

**Task Duration Prediction**:
1. User creates a new task
2. System analyzes task description for complexity
3. System checks current user context and stressors
4. Bayesian model generates prediction with confidence interval
5. Prediction is displayed to user
6. After completion, actual duration updates the model

**Buffer Time Calculation**:
1. User schedules sequential tasks
2. System analyzes task pair for transition difficulty
3. Current stressors are incorporated into calculation
4. Optimal buffer is determined and recommended
5. User accepts or modifies buffer
6. Buffer is applied to schedule

### Internal Design Documents

- [STE System Architecture](docs/ste_architecture.md)
- [Bayesian Model Design](docs/bayesian_model_design.md)
- [NLP Model Selection](docs/nlp_model_selection.md)
- [Stressor Detection Approach](docs/stressor_detection.md)
- [Buffer Calculation Algorithm](docs/buffer_calculation.md)

### User Guides

- [Interpreting Duration Predictions](docs/user/duration_predictions.md)
- [Understanding Task Complexity](docs/user/task_complexity.md)
- [Managing Stressors for Better Focus](docs/user/managing_stressors.md)
- [Optimizing Task Transitions](docs/user/task_transitions.md) 