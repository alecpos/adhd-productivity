# Epic 2: API Documentation - Stochastic Time Estimation Engine

This document provides a comprehensive reference for the APIs exposed by the Epic 2 components.

## Table of Contents

1. [BayesianDurationPredictor API](#bayesiandurationpredictor-api)
2. [NLPComplexityAnalyzer API](#nlpcomplexityanalyzer-api)
3. [ContextualStressorDetector API](#contextualstressordetector-api)
4. [TimeBufferCalculator API](#timebuffercalculator-api)
5. [Error Handling](#error-handling)
6. [Authentication and Authorization](#authentication-and-authorization)
7. [Rate Limiting](#rate-limiting)
8. [API Versioning](#api-versioning)
9. [SDKs and Client Libraries](#sdks-and-client-libraries)

## BayesianDurationPredictor API

Base URL: `/api/v1/time-estimation/bayesian-predictor`

### `predict_task_duration(task_description: str, user_id: str, task_type: str = None, context_factors: Dict = None) -> Dict`

Predicts the duration of a task based on historical data and contextual factors.

#### Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `task_description` | string | Yes | Description of the task to estimate |
| `user_id` | string | Yes | Unique identifier of the user |
| `task_type` | string | No | Category of task (e.g., "coding", "writing", "meeting") |
| `context_factors` | object | No | Additional factors affecting duration estimation |

##### Context Factors Object

| Field | Type | Description |
|-------|------|-------------|
| `energy_level` | number | Current energy level (0-10) |
| `focus_level` | number | Current focus capacity (0-10) |
| `environment` | string | Working environment (e.g., "home", "office", "coffee shop") |
| `interruption_likelihood` | number | Expected interruption frequency (0-10) |
| `time_of_day` | string | Time when task will be performed (ISO format) |

#### Response

| Field | Type | Description |
|-------|------|-------------|
| `expected_duration_minutes` | number | Predicted task duration in minutes |
| `confidence_interval` | object | Statistical confidence interval for the prediction |
| `histogram` | array | Distribution of possible durations |
| `factors_impact` | array | Impact of different factors on the prediction |
| `similar_tasks` | array | Similar historical tasks used for prediction |

##### Confidence Interval Object

| Field | Type | Description |
|-------|------|-------------|
| `lower_bound_minutes` | number | Lower bound of 95% confidence interval |
| `upper_bound_minutes` | number | Upper bound of 95% confidence interval |

#### Request Example

```json
POST /api/v1/time-estimation/bayesian-predictor/predict_task_duration
Content-Type: application/json

{
  "task_description": "Write a detailed project proposal for the client",
  "user_id": "user_123",
  "task_type": "writing",
  "context_factors": {
    "energy_level": 8,
    "focus_level": 7,
    "environment": "home",
    "interruption_likelihood": 3,
    "time_of_day": "2023-07-15T09:30:00Z"
  }
}
```

#### Response Example

```json
HTTP/1.1 200 OK
Content-Type: application/json

{
  "expected_duration_minutes": 95,
  "confidence_interval": {
    "lower_bound_minutes": 75,
    "upper_bound_minutes": 120
  },
  "histogram": [
    {"duration_minutes": 60, "probability": 0.05},
    {"duration_minutes": 75, "probability": 0.15},
    {"duration_minutes": 90, "probability": 0.45},
    {"duration_minutes": 105, "probability": 0.25},
    {"duration_minutes": 120, "probability": 0.10}
  ],
  "factors_impact": [
    {"factor": "task_complexity", "impact_percentage": 40},
    {"factor": "focus_level", "impact_percentage": 25},
    {"factor": "similar_tasks_history", "impact_percentage": 20},
    {"factor": "environment", "impact_percentage": 10},
    {"factor": "time_of_day", "impact_percentage": 5}
  ],
  "similar_tasks": [
    {"description": "Write client proposal for XYZ Corp", "actual_duration_minutes": 85},
    {"description": "Create detailed project outline for team", "actual_duration_minutes": 65}
  ]
}
```

### `update_with_actual_duration(task_id: str, actual_duration_minutes: int, completion_factors: Dict = None) -> Dict`

Updates the prediction model with actual task completion data.

#### Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `task_id` | string | Yes | Unique identifier of the task |
| `actual_duration_minutes` | integer | Yes | Actual time taken to complete the task |
| `completion_factors` | object | No | Factors affecting the task during completion |

##### Completion Factors Object

| Field | Type | Description |
|-------|------|-------------|
| `interruption_count` | integer | Number of interruptions experienced |
| `perceived_difficulty` | number | User-reported difficulty (0-10) |
| `focus_quality` | number | User-reported focus quality (0-10) |
| `notes` | string | User notes about factors affecting duration |

#### Response

| Field | Type | Description |
|-------|------|-------------|
| `model_updated` | boolean | Whether the model was successfully updated |
| `accuracy_improvement` | number | Improvement in model accuracy after update |
| `learning_insights` | array | Insights gained from this data point |

#### Request Example

```json
POST /api/v1/time-estimation/bayesian-predictor/update_with_actual_duration
Content-Type: application/json

{
  "task_id": "task_456",
  "actual_duration_minutes": 110,
  "completion_factors": {
    "interruption_count": 4,
    "perceived_difficulty": 7,
    "focus_quality": 6,
    "notes": "Had a few unexpected calls during the task"
  }
}
```

#### Response Example

```json
HTTP/1.1 200 OK
Content-Type: application/json

{
  "model_updated": true,
  "accuracy_improvement": 0.05,
  "learning_insights": [
    "Interruptions increased your task duration by approximately 15%",
    "Writing tasks consistently take longer when performed after 3 PM",
    "Your estimation accuracy improves for tasks with detailed descriptions"
  ]
}
```

## NLPComplexityAnalyzer API

Base URL: `/api/v1/time-estimation/nlp-analyzer`

### `analyze_task_complexity(task_description: str, task_type: str = None) -> Dict`

Analyzes the complexity of a task based on its description using NLP.

#### Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `task_description` | string | Yes | Description of the task to analyze |
| `task_type` | string | No | Category of the task to provide context |

#### Response

| Field | Type | Description |
|-------|------|-------------|
| `complexity_score` | number | Overall complexity score (0-100) |
| `cognitive_load` | number | Estimated cognitive load (0-10) |
| `ambiguity_index` | number | Measure of ambiguity in the description (0-10) |
| `subtask_count` | integer | Estimated number of implicit subtasks |
| `key_complexity_factors` | array | Factors contributing to complexity |
| `language_features` | object | Linguistic features affecting complexity |

##### Language Features Object

| Field | Type | Description |
|-------|------|-------------|
| `sentence_complexity` | number | Complexity of sentence structure (0-10) |
| `vocabulary_level` | number | Level of vocabulary used (0-10) |
| `technical_terms_count` | integer | Number of technical or domain-specific terms |
| `action_verb_clarity` | number | Clarity of action verbs (0-10) |

#### Request Example

```json
POST /api/v1/time-estimation/nlp-analyzer/analyze_task_complexity
Content-Type: application/json

{
  "task_description": "Refactor the authentication module to use OAuth2 and implement proper error handling with comprehensive logging",
  "task_type": "coding"
}
```

#### Response Example

```json
HTTP/1.1 200 OK
Content-Type: application/json

{
  "complexity_score": 78,
  "cognitive_load": 8.2,
  "ambiguity_index": 2.1,
  "subtask_count": 4,
  "key_complexity_factors": [
    "Multiple technical components (refactoring, OAuth2, error handling, logging)",
    "Integration complexity between components",
    "Security-critical implementation",
    "Requires systematic testing approach"
  ],
  "language_features": {
    "sentence_complexity": 7.4,
    "vocabulary_level": 8.2,
    "technical_terms_count": 5,
    "action_verb_clarity": 6.8
  }
}
```

### `extract_task_requirements(task_description: str) -> Dict`

Extracts specific requirements and constraints from a task description.

#### Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `task_description` | string | Yes | Description of the task to analyze |

#### Response

| Field | Type | Description |
|-------|------|-------------|
| `identified_requirements` | array | List of explicit requirements |
| `implied_requirements` | array | List of implied requirements |
| `dependencies` | array | External dependencies identified |
| `constraints` | array | Constraints or limitations identified |
| `skills_required` | array | Skills likely needed for the task |

#### Request Example

```json
POST /api/v1/time-estimation/nlp-analyzer/extract_task_requirements
Content-Type: application/json

{
  "task_description": "Create a responsive dashboard that displays real-time analytics from our API. It should update automatically every 5 minutes and support both light and dark themes."
}
```

#### Response Example

```json
HTTP/1.1 200 OK
Content-Type: application/json

{
  "identified_requirements": [
    "Create a responsive dashboard",
    "Display real-time analytics",
    "Update automatically every 5 minutes",
    "Support light and dark themes"
  ],
  "implied_requirements": [
    "Fetch data from API",
    "Implement refresh mechanism",
    "Create theme switching functionality",
    "Ensure mobile compatibility"
  ],
  "dependencies": [
    "Access to analytics API",
    "Frontend framework",
    "Data visualization libraries"
  ],
  "constraints": [
    "Must refresh data every 5 minutes",
    "Must work across device sizes"
  ],
  "skills_required": [
    "Frontend development",
    "API integration",
    "UI/UX design",
    "Data visualization"
  ]
}
```

## ContextualStressorDetector API

Base URL: `/api/v1/time-estimation/stressor-detector`

### `detect_current_stressors(user_id: str, wearable_data: Dict = None, environment_data: Dict = None) -> Dict`

Detects current stressors that may affect task completion time.

#### Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `user_id` | string | Yes | Unique identifier of the user |
| `wearable_data` | object | No | Data from wearable devices |
| `environment_data` | object | No | Data about the current environment |

##### Wearable Data Object

| Field | Type | Description |
|-------|------|-------------|
| `heart_rate` | number | Current heart rate in BPM |
| `heart_rate_variability` | number | HRV measurement |
| `sleep_quality` | number | Last night's sleep quality (0-10) |
| `steps_today` | integer | Steps taken today |
| `activity_level` | number | Recent activity level (0-10) |

##### Environment Data Object

| Field | Type | Description |
|-------|------|-------------|
| `noise_level` | number | Ambient noise level (dB) |
| `temperature` | number | Ambient temperature (°C) |
| `people_present` | integer | Number of people in vicinity |
| `location_type` | string | Type of location (home, office, public) |
| `weather_condition` | string | Current weather condition |

#### Response

| Field | Type | Description |
|-------|------|-------------|
| `stress_level` | number | Overall stress level (0-10) |
| `identified_stressors` | array | List of detected stressors |
| `cognitive_impact` | number | Estimated impact on cognitive performance (0-10) |
| `focus_impact` | number | Estimated impact on focus (0-10) |
| `recovery_suggestions` | array | Suggestions to reduce stress impact |

#### Request Example

```json
POST /api/v1/time-estimation/stressor-detector/detect_current_stressors
Content-Type: application/json

{
  "user_id": "user_789",
  "wearable_data": {
    "heart_rate": 85,
    "heart_rate_variability": 45,
    "sleep_quality": 6.2,
    "steps_today": 3500,
    "activity_level": 4.2
  },
  "environment_data": {
    "noise_level": 65,
    "temperature": 26,
    "people_present": 8,
    "location_type": "office",
    "weather_condition": "cloudy"
  }
}
```

#### Response Example

```json
HTTP/1.1 200 OK
Content-Type: application/json

{
  "stress_level": 7.2,
  "identified_stressors": [
    {"stressor": "elevated_heart_rate", "severity": 6, "duration": "1.5 hours"},
    {"stressor": "lower_than_optimal_sleep", "severity": 7, "duration": "persistent"},
    {"stressor": "high_ambient_noise", "severity": 5, "duration": "current"}
  ],
  "cognitive_impact": 6.8,
  "focus_impact": 7.5,
  "recovery_suggestions": [
    "Take a 10-minute walk outside",
    "Use noise-canceling headphones for next hour",
    "Hydrate and have a small protein-rich snack",
    "Try 5 minutes of deep breathing before starting focused work"
  ]
}
```

### `get_stressor_history(user_id: str, start_date: str, end_date: str) -> Dict`

Retrieves historical stressor data for analysis and pattern recognition.

#### Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `user_id` | string | Yes | Unique identifier of the user |
| `start_date` | string | Yes | Start date for the history (ISO format) |
| `end_date` | string | Yes | End date for the history (ISO format) |

#### Response

| Field | Type | Description |
|-------|------|-------------|
| `average_stress_level` | number | Average stress level during period |
| `stress_trend` | string | Trend of stress levels (increasing, decreasing, stable) |
| `common_stressors` | array | Most common stressors during period |
| `peak_stress_times` | array | Times with highest stress levels |
| `stress_patterns` | array | Identified patterns in stress data |

#### Request Example

```json
GET /api/v1/time-estimation/stressor-detector/get_stressor_history?user_id=user_789&start_date=2023-06-01T00:00:00Z&end_date=2023-06-30T23:59:59Z
```

#### Response Example

```json
HTTP/1.1 200 OK
Content-Type: application/json

{
  "average_stress_level": 5.4,
  "stress_trend": "decreasing",
  "common_stressors": [
    {"stressor": "inadequate_sleep", "frequency": 12, "average_impact": 7.2},
    {"stressor": "high_meeting_load", "frequency": 8, "average_impact": 6.5},
    {"stressor": "deadline_pressure", "frequency": 5, "average_impact": 8.1}
  ],
  "peak_stress_times": [
    {"date": "2023-06-15", "time": "14:00-16:00", "level": 8.7, "context": "Project deadline"},
    {"date": "2023-06-22", "time": "09:00-11:00", "level": 7.9, "context": "Client presentation"}
  ],
  "stress_patterns": [
    {"pattern": "elevated_midweek", "description": "Stress levels consistently higher Tuesday-Thursday"},
    {"pattern": "morning_recovery", "description": "Stress levels typically lower before 9:30 AM"},
    {"pattern": "sleep_correlation", "description": "Poor sleep strongly correlates with next-day stress"}
  ]
}
```

## TimeBufferCalculator API

Base URL: `/api/v1/time-estimation/buffer-calculator`

### `calculate_optimal_buffer(user_id: str, task_duration_minutes: int, task_context: Dict) -> Dict`

Calculates the optimal time buffer to add to a task based on various factors.

#### Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `user_id` | string | Yes | Unique identifier of the user |
| `task_duration_minutes` | integer | Yes | Estimated duration of the task in minutes |
| `task_context` | object | Yes | Contextual information about the task |

##### Task Context Object

| Field | Type | Description |
|-------|------|-------------|
| `task_importance` | number | Importance of the task (0-10) |
| `transition_difficulty` | number | Difficulty of transitioning to this task (0-10) |
| `scheduling_flexibility` | number | Flexibility in scheduling (0-10) |
| `preceding_task_type` | string | Type of task preceding this one |
| `following_task_type` | string | Type of task following this one |
| `time_of_day` | string | When the task is scheduled (ISO format) |

#### Response

| Field | Type | Description |
|-------|------|-------------|
| `recommended_buffer_minutes` | integer | Recommended buffer time in minutes |
| `buffer_breakdown` | object | Breakdown of buffer components |
| `confidence_level` | number | Confidence in the recommendation (0-10) |
| `adjustment_factors` | array | Factors that influenced the buffer calculation |

##### Buffer Breakdown Object

| Field | Type | Description |
|-------|------|-------------|
| `transition_time` | integer | Time needed for task transition |
| `uncertainty_margin` | integer | Additional time for uncertainty |
| `recovery_time` | integer | Time allocated for mental recovery |
| `context_switching` | integer | Time for context switching |

#### Request Example

```json
POST /api/v1/time-estimation/buffer-calculator/calculate_optimal_buffer
Content-Type: application/json

{
  "user_id": "user_456",
  "task_duration_minutes": 60,
  "task_context": {
    "task_importance": 8,
    "transition_difficulty": 7,
    "scheduling_flexibility": 3,
    "preceding_task_type": "meeting",
    "following_task_type": "deep_work",
    "time_of_day": "2023-07-15T14:00:00Z"
  }
}
```

#### Response Example

```json
HTTP/1.1 200 OK
Content-Type: application/json

{
  "recommended_buffer_minutes": 18,
  "buffer_breakdown": {
    "transition_time": 8,
    "uncertainty_margin": 6,
    "recovery_time": 4,
    "context_switching": 0
  },
  "confidence_level": 8.5,
  "adjustment_factors": [
    {"factor": "post_meeting_recovery", "impact_minutes": 5},
    {"factor": "transition_to_deep_work", "impact_minutes": 8},
    {"factor": "afternoon_energy_dip", "impact_minutes": 3},
    {"factor": "task_importance", "impact_minutes": 2}
  ]
}
```

### `get_transition_statistics(user_id: str, transition_type: str = null) -> Dict`

Retrieves statistics about transition times between different types of tasks.

#### Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `user_id` | string | Yes | Unique identifier of the user |
| `transition_type` | string | No | Specific transition type (e.g. "meeting_to_deep_work") |

#### Response

| Field | Type | Description |
|-------|------|-------------|
| `average_transition_times` | array | Average transition times between task types |
| `transition_time_factors` | array | Factors affecting transition times |
| `optimal_task_sequences` | array | Sequences of tasks that minimize transition times |
| `high_friction_transitions` | array | Transitions with highest time costs |

#### Request Example

```json
GET /api/v1/time-estimation/buffer-calculator/get_transition_statistics?user_id=user_456
```

#### Response Example

```json
HTTP/1.1 200 OK
Content-Type: application/json

{
  "average_transition_times": [
    {"from": "meeting", "to": "deep_work", "average_minutes": 12.5},
    {"from": "deep_work", "to": "meeting", "average_minutes": 5.2},
    {"from": "email", "to": "deep_work", "average_minutes": 8.7},
    {"from": "deep_work", "to": "email", "average_minutes": 3.1}
  ],
  "transition_time_factors": [
    {"factor": "cognitive_load_difference", "impact_percentage": 45},
    {"factor": "interruption_during_transition", "impact_percentage": 30},
    {"factor": "task_similarity", "impact_percentage": 15},
    {"factor": "time_of_day", "impact_percentage": 10}
  ],
  "optimal_task_sequences": [
    ["email", "planning", "deep_work", "review"],
    ["meeting", "follow_up", "deep_work"],
    ["learning", "application", "documentation"]
  ],
  "high_friction_transitions": [
    {"from": "meeting", "to": "deep_work", "average_minutes": 12.5, "reduction_strategies": ["Take 5-minute break", "Review notes before starting"]},
    {"from": "multiple_meetings", "to": "creative_work", "average_minutes": 18.2, "reduction_strategies": ["Buffer with low-cognitive task", "Change physical environment"]}
  ]
}
```

## Error Handling

All APIs use consistent error formats and status codes:

### Error Response Format

```json
{
  "error": {
    "code": "error_code",
    "message": "Human-readable error message",
    "details": {
      "field_name": "Specific error about this field",
      ...
    }
  },
  "request_id": "unique_request_identifier"
}
```

### Common Error Codes

| HTTP Status | Error Code | Description |
|-------------|------------|-------------|
| 400 | `invalid_request` | The request was malformed or contained invalid parameters |
| 401 | `unauthorized` | Authentication is required or failed |
| 403 | `forbidden` | The authenticated user doesn't have permission for this operation |
| 404 | `not_found` | The requested resource was not found |
| 409 | `conflict` | The request conflicts with the current state of the resource |
| 422 | `validation_failed` | The input failed validation checks |
| 429 | `rate_limit_exceeded` | The rate limit for the API has been exceeded |
| 500 | `internal_error` | An internal server error occurred |
| 503 | `service_unavailable` | The service is temporarily unavailable |

### Error Examples

#### Invalid Request

```json
HTTP/1.1 400 Bad Request
Content-Type: application/json

{
  "error": {
    "code": "invalid_request",
    "message": "Invalid parameters provided",
    "details": {
      "task_duration_minutes": "Must be a positive integer"
    }
  },
  "request_id": "req_7f6a5d4e3c2b1a"
}
```

#### Insufficient Data

```json
HTTP/1.1 422 Unprocessable Entity
Content-Type: application/json

{
  "error": {
    "code": "insufficient_data",
    "message": "Not enough historical data to make accurate predictions",
    "details": {
      "min_required_tasks": 5,
      "current_task_count": 2
    }
  },
  "request_id": "req_2c3d4e5f6g7h8i"
}
```

## Authentication and Authorization

### Authentication Methods

#### JWT Bearer Token

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

- Tokens expire after 24 hours
- Requests with expired tokens return 401 Unauthorized
- Refresh tokens can be obtained from `/api/v1/auth/refresh`

#### API Key

```
X-API-Key: api_key_f7d6e5c4b3a2
```

- Used for service-to-service communication
- Different rate limits than user authentication
- Set up and manage API keys through the developer portal

### Authorization Model

The API uses role-based access control (RBAC) with the following roles:

| Role | Description |
|------|-------------|
| `user` | Standard user with access to own data |
| `admin` | Administrative access to multiple users' data |
| `service` | System service account for internal operations |

### User Identity

All APIs that require user identification accept one of:

- `user_id`: Direct user identifier
- `me`: Special value to indicate the currently authenticated user

Example:

```
GET /api/v1/time-estimation/buffer-calculator/get_transition_statistics?user_id=me
```

## Rate Limiting

### Default Rate Limits

| API | Authenticated | Unauthenticated |
|-----|--------------|----------------|
| BayesianDurationPredictor | 100 requests/minute | 10 requests/minute |
| NLPComplexityAnalyzer | 60 requests/minute | 5 requests/minute |
| ContextualStressorDetector | 100 requests/minute | 10 requests/minute |
| TimeBufferCalculator | 100 requests/minute | 10 requests/minute |

### Rate Limit Headers

Rate limit information is included in response headers:

```
X-Rate-Limit-Limit: 100
X-Rate-Limit-Remaining: 95
X-Rate-Limit-Reset: 1626369985
```

### Handling Rate Limits

When a rate limit is exceeded, the API responds with:

```json
HTTP/1.1 429 Too Many Requests
Content-Type: application/json
Retry-After: 30

{
  "error": {
    "code": "rate_limit_exceeded",
    "message": "Rate limit exceeded. Please retry after 30 seconds.",
    "details": {
      "limit": 100,
      "reset_seconds": 30
    }
  },
  "request_id": "req_9i8h7g6f5e4d3c"
}
```

### Rate Limit Extensions

Enterprise customers may request increased rate limits through:

- Developer Portal: [https://developer.adhdcalendar.com/rate-limits](https://developer.adhdcalendar.com/rate-limits)
- Email: api-support@adhdcalendar.com

## API Versioning

### Version Specification

Versions are specified in the URL path:

```
/api/v1/time-estimation/...  # version 1
/api/v2/time-estimation/...  # version 2
```

### API Lifecycle

| Status | Description | Support Period |
|--------|-------------|---------------|
| `current` | Latest stable version | Until superseded + 1 year |
| `deprecated` | Still supported but may be removed in future | 6 months after deprecation notice |
| `sunset` | No longer supported | Not available |

### Migration Guides

Migration guides between versions are available at:

[https://developer.adhdcalendar.com/docs/migration/time-estimation/v1-to-v2](https://developer.adhdcalendar.com/docs/migration/time-estimation/v1-to-v2)

## SDKs and Client Libraries

### Available SDKs

| Language | Repository | Features |
|----------|------------|----------|
| Python | [GitHub](https://github.com/adhdcalendar/python-client) | Full API coverage, async support |
| JavaScript | [GitHub](https://github.com/adhdcalendar/js-client) | Browser and Node.js support |
| Java | [GitHub](https://github.com/adhdcalendar/java-client) | Android compatible |
| Swift | [GitHub](https://github.com/adhdcalendar/swift-client) | iOS/macOS native |
| C# | [GitHub](https://github.com/adhdcalendar/dotnet-client) | .NET Standard 2.0+ |

### Example Usage (Python)

```python
from adhdcalendar import TimeEstimationClient

# Initialize client
client = TimeEstimationClient(api_key="your_api_key")

# Predict task duration
prediction = client.bayesian_predictor.predict_task_duration(
    task_description="Create wireframes for the new mobile app",
    user_id="user_123",
    task_type="design",
    context_factors={
        "energy_level": 7,
        "focus_level": 8,
        "environment": "office",
        "interruption_likelihood": 4
    }
)

# Access prediction results
print(f"Expected duration: {prediction.expected_duration_minutes} minutes")
print(f"Confidence interval: {prediction.confidence_interval.lower_bound_minutes} - {prediction.confidence_interval.upper_bound_minutes} minutes")

# Get buffer recommendation
buffer = client.buffer_calculator.calculate_optimal_buffer(
    user_id="user_123",
    task_duration_minutes=prediction.expected_duration_minutes,
    task_context={
        "task_importance": 8,
        "transition_difficulty": 6,
        "scheduling_flexibility": 4,
        "preceding_task_type": "meeting",
        "following_task_type": "break",
        "time_of_day": "2023-07-15T14:00:00Z"
    }
)

print(f"Recommended buffer: {buffer.recommended_buffer_minutes} minutes")
```
