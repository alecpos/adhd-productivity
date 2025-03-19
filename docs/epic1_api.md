# Epic 1: API Documentation - Temporal Pattern Recognition (TPR) Models

This document provides a comprehensive reference for the APIs exposed by the Epic 1 components.

## Table of Contents

1. [ProductivityPatternLSTM API](#productivitypatternlstm-api)
2. [CircadianRhythmModel API](#circadianrhythmmodel-api)
3. [ProductivityCorrelationSystem API](#productivitycorrelationsystem-api)
4. [MentalHealthFederatedModel API](#mentalhealthfederatedmodel-api)
5. [Error Handling](#error-handling)
6. [Authentication and Authorization](#authentication-and-authorization)
7. [Rate Limiting](#rate-limiting)
8. [API Versioning](#api-versioning)
9. [SDKs and Client Libraries](#sdks-and-client-libraries)

## ProductivityPatternLSTM API

Base URL: `/api/v1/productivity-patterns`

### `detect_optimal_windows(user_id: str, days_ahead: int = 7, min_window_length_minutes: int = 30) -> List[Dict]`

Detects optimal scheduling windows based on historical productivity patterns.

**Endpoint**: `GET /api/v1/productivity-patterns/optimal-windows`

**Parameters**:
- `user_id` (str, required): User identifier
- `days_ahead` (int, optional): Number of days to look ahead
- `min_window_length_minutes` (int, optional): Minimum window length in minutes
- `task_category` (str, optional): Filter by specific task category
- `priority_level` (str, optional): Filter by priority level (high, medium, low)

**Request Example**:
```
GET /api/v1/productivity-patterns/optimal-windows?user_id=user123&days_ahead=5&min_window_length_minutes=45&task_category=coding
```

**Response**:
- 200 OK: List of optimal windows
- 400 Bad Request: Invalid parameters
- 401 Unauthorized: Authentication required
- 403 Forbidden: Insufficient permissions
- 500 Internal Server Error: Service error

**Response Example**:
```json
{
  "optimal_windows": [
    {
      "start_time": "2023-04-01T09:30:00Z",
      "end_time": "2023-04-01T11:30:00Z",
      "confidence_score": 0.92,
      "expected_productivity": "high",
      "task_categories": ["coding", "writing", "analysis"],
      "historical_completion_rate": 0.87
    },
    {
      "start_time": "2023-04-01T15:00:00Z",
      "end_time": "2023-04-01T16:30:00Z",
      "confidence_score": 0.78,
      "expected_productivity": "medium",
      "task_categories": ["emails", "meetings", "planning"],
      "historical_completion_rate": 0.72
    }
  ],
  "metadata": {
    "prediction_based_on_days": 30,
    "model_version": "lstm_v2.3",
    "generated_at": "2023-03-31T18:20:30Z"
  }
}
```

### `analyze_flexible_blocks(user_id: str, time_blocks: List[Dict], flexibility_threshold: float = 0.5) -> Dict`

Analyzes time blocks to identify which ones should be flexible based on historical patterns.

**Endpoint**: `POST /api/v1/productivity-patterns/analyze-flexibility`

**Parameters**:
- `user_id` (str, required): User identifier
- `time_blocks` (List[Dict], required): Time blocks to analyze
  - `id` (str, required): Block identifier
  - `start_time` (str, required): ISO8601 formatted start time
  - `end_time` (str, required): ISO8601 formatted end time
  - `task_category` (str, optional): Category of task
- `flexibility_threshold` (float, optional): Threshold for flexibility determination

**Request Example**:
```json
{
  "user_id": "user123",
  "time_blocks": [
    {
      "id": "block123",
      "start_time": "2023-04-01T09:00:00Z",
      "end_time": "2023-04-01T10:30:00Z",
      "task_category": "coding"
    },
    {
      "id": "block456",
      "start_time": "2023-04-01T13:00:00Z",
      "end_time": "2023-04-01T14:30:00Z",
      "task_category": "meetings"
    }
  ],
  "flexibility_threshold": 0.6
}
```

**Response**:
- 200 OK: Analysis results
- 400 Bad Request: Invalid input
- 401 Unauthorized: Authentication required
- 403 Forbidden: Insufficient permissions
- 500 Internal Server Error: Service error

**Response Example**:
```json
{
  "flexible_blocks": [
    {
      "id": "block123",
      "flexibility_score": 0.85,
      "recommendation": "This block can be rescheduled with minimal impact",
      "alternative_times": [
        {
          "start_time": "2023-04-01T14:30:00Z",
          "end_time": "2023-04-01T16:00:00Z",
          "expected_productivity": "high"
        },
        {
          "start_time": "2023-04-02T09:00:00Z",
          "end_time": "2023-04-02T10:30:00Z",
          "expected_productivity": "high"
        }
      ]
    }
  ],
  "fixed_blocks": [
    {
      "id": "block456",
      "flexibility_score": 0.32,
      "recommendation": "Keep this block fixed to maintain productivity",
      "impact_if_moved": "significant_decrease"
    }
  ],
  "metadata": {
    "analysis_confidence": "high",
    "model_version": "flex_analyzer_v1.2"
  }
}
```

### `get_productivity_metrics(user_id: str, start_date: str, end_date: str) -> Dict`

Retrieves historical productivity metrics and patterns.

**Endpoint**: `GET /api/v1/productivity-patterns/metrics`

**Parameters**:
- `user_id` (str, required): User identifier
- `start_date` (str, required): ISO8601 formatted start date
- `end_date` (str, required): ISO8601 formatted end date
- `metrics` (List[str], optional): Specific metrics to retrieve
- `aggregate_by` (str, optional): Aggregation period (day, week, month)

**Request Example**:
```
GET /api/v1/productivity-patterns/metrics?user_id=user123&start_date=2023-03-01T00:00:00Z&end_date=2023-03-31T23:59:59Z&metrics=completion_rate,focus_score&aggregate_by=week
```

**Response**:
- 200 OK: Productivity metrics
- 400 Bad Request: Invalid parameters
- 401 Unauthorized: Authentication required
- 403 Forbidden: Insufficient permissions
- 500 Internal Server Error: Service error

**Response Example**:
```json
{
  "metrics": {
    "completion_rate": [
      {
        "period": "2023-03-01/2023-03-07",
        "value": 0.78,
        "trend": "stable"
      },
      {
        "period": "2023-03-08/2023-03-14",
        "value": 0.82,
        "trend": "improving"
      },
      {
        "period": "2023-03-15/2023-03-21",
        "value": 0.85,
        "trend": "improving"
      },
      {
        "period": "2023-03-22/2023-03-31",
        "value": 0.81,
        "trend": "slight_decline"
      }
    ],
    "focus_score": [
      {
        "period": "2023-03-01/2023-03-07",
        "value": 72,
        "trend": "stable"
      },
      {
        "period": "2023-03-08/2023-03-14",
        "value": 75,
        "trend": "improving"
      },
      {
        "period": "2023-03-15/2023-03-21",
        "value": 79,
        "trend": "improving"
      },
      {
        "period": "2023-03-22/2023-03-31",
        "value": 76,
        "trend": "slight_decline"
      }
    ]
  },
  "pattern_insights": [
    {
      "insight": "Productivity peaks on Tuesday and Wednesday mornings",
      "confidence": "high",
      "recommendation": "Schedule high-focus tasks during these periods"
    },
    {
      "insight": "Completion rates decline after 3pm",
      "confidence": "medium",
      "recommendation": "Consider scheduling administrative tasks for afternoon periods"
    }
  ],
  "metadata": {
    "data_points": 124,
    "model_version": "lstm_v2.3"
  }
}
```

## CircadianRhythmModel API

Base URL: `/api/v1/circadian-rhythm`

### `predict_daily_curve(user_id: str, date: str = None) -> Dict`

Predicts a user's energy/focus curve for a specific day based on circadian rhythm analysis.

**Endpoint**: `GET /api/v1/circadian-rhythm/daily-curve`

**Parameters**:
- `user_id` (str, required): User identifier
- `date` (str, optional): ISO8601 formatted date (defaults to current day)
- `include_factors` (bool, optional): Include contributing factors

**Request Example**:
```
GET /api/v1/circadian-rhythm/daily-curve?user_id=user123&date=2023-04-01&include_factors=true
```

**Response**:
- 200 OK: Daily energy curve prediction
- 400 Bad Request: Invalid parameters
- 401 Unauthorized: Authentication required
- 403 Forbidden: Insufficient permissions
- 500 Internal Server Error: Service error

**Response Example**:
```json
{
  "date": "2023-04-01",
  "hourly_predictions": [
    {
      "hour": 0,
      "energy_level": 10,
      "focus_capacity": 5,
      "confidence": 0.85
    },
    {
      "hour": 1,
      "energy_level": 5,
      "focus_capacity": 3,
      "confidence": 0.92
    },
    /* ... hours 2-23 ... */
    {
      "hour": 23,
      "energy_level": 15,
      "focus_capacity": 8,
      "confidence": 0.78
    }
  ],
  "peak_periods": [
    {
      "start_hour": 9,
      "end_hour": 11,
      "energy_level": "high",
      "focus_capacity": "high",
      "recommended_activities": ["deep work", "creative tasks", "problem solving"]
    },
    {
      "start_hour": 16,
      "end_hour": 18,
      "energy_level": "medium",
      "focus_capacity": "medium",
      "recommended_activities": ["emails", "planning", "learning"]
    }
  ],
  "contributing_factors": {
    "sleep_pattern": {
      "average_sleep_hours": 7.2,
      "sleep_quality": "good",
      "impact": "positive"
    },
    "medication": {
      "timing": "morning",
      "impact": "positive"
    },
    "physical_activity": {
      "level": "moderate",
      "impact": "positive"
    }
  },
  "metadata": {
    "model_version": "circadian_v3.1",
    "data_points_used": 14,
    "prediction_confidence": "high"
  }
}
```

### `optimize_schedule(user_id: str, tasks: List[Dict], date: str) -> Dict`

Optimizes task scheduling based on circadian rhythm energy levels.

**Endpoint**: `POST /api/v1/circadian-rhythm/optimize-schedule`

**Parameters**:
- `user_id` (str, required): User identifier
- `tasks` (List[Dict], required): Tasks to be scheduled
  - `id` (str, required): Task identifier
  - `name` (str, required): Task name
  - `duration_minutes` (int, required): Expected duration
  - `energy_requirement` (str, optional): Energy requirement (high, medium, low)
  - `focus_requirement` (str, optional): Focus requirement (high, medium, low)
  - `priority` (str, optional): Priority level (high, medium, low)
  - `deadline` (str, optional): ISO8601 formatted deadline
- `date` (str, required): ISO8601 formatted date to schedule for
- `constraints` (Dict, optional): Scheduling constraints
  - `working_hours` (Dict, optional): Working hours constraints
  - `break_preferences` (Dict, optional): Break preferences

**Request Example**:
```json
{
  "user_id": "user123",
  "tasks": [
    {
      "id": "task1",
      "name": "Write project proposal",
      "duration_minutes": 90,
      "energy_requirement": "high",
      "focus_requirement": "high",
      "priority": "high",
      "deadline": "2023-04-01T17:00:00Z"
    },
    {
      "id": "task2",
      "name": "Team meeting",
      "duration_minutes": 60,
      "energy_requirement": "medium",
      "focus_requirement": "medium",
      "priority": "medium",
      "deadline": null
    },
    {
      "id": "task3",
      "name": "Process emails",
      "duration_minutes": 45,
      "energy_requirement": "low",
      "focus_requirement": "low",
      "priority": "low",
      "deadline": null
    }
  ],
  "date": "2023-04-01",
  "constraints": {
    "working_hours": {
      "start": "09:00",
      "end": "17:00"
    },
    "break_preferences": {
      "lunch_duration_minutes": 60,
      "preferred_lunch_time": "12:00"
    }
  }
}
```

**Response**:
- 200 OK: Optimized schedule
- 400 Bad Request: Invalid input
- 401 Unauthorized: Authentication required
- 403 Forbidden: Insufficient permissions
- 500 Internal Server Error: Service error

**Response Example**:
```json
{
  "schedule": [
    {
      "task_id": "task1",
      "start_time": "2023-04-01T09:30:00Z",
      "end_time": "2023-04-01T11:00:00Z",
      "energy_match_score": 0.92,
      "focus_match_score": 0.95,
      "recommendation_confidence": "high"
    },
    {
      "type": "break",
      "name": "Lunch break",
      "start_time": "2023-04-01T12:00:00Z",
      "end_time": "2023-04-01T13:00:00Z"
    },
    {
      "task_id": "task2",
      "start_time": "2023-04-01T13:30:00Z",
      "end_time": "2023-04-01T14:30:00Z",
      "energy_match_score": 0.78,
      "focus_match_score": 0.82,
      "recommendation_confidence": "medium"
    },
    {
      "task_id": "task3",
      "start_time": "2023-04-01T15:00:00Z",
      "end_time": "2023-04-01T15:45:00Z",
      "energy_match_score": 0.85,
      "focus_match_score": 0.80,
      "recommendation_confidence": "high"
    }
  ],
  "optimization_metrics": {
    "energy_efficiency": 0.88,
    "focus_utilization": 0.85,
    "priority_satisfaction": 0.92,
    "schedule_balance": 0.87
  },
  "metadata": {
    "model_version": "energy_optimizer_v2.2",
    "optimization_iterations": 12
  }
}
```

## ProductivityCorrelationSystem API

Base URL: `/api/v1/productivity-correlations`

### `analyze_correlations(user_id: str, time_period: str = "last_30_days") -> Dict`

Analyzes correlations between various factors and productivity/focus.

**Endpoint**: `GET /api/v1/productivity-correlations/analyze`

**Parameters**:
- `user_id` (str, required): User identifier
- `time_period` (str, optional): Time period for analysis
- `factors` (List[str], optional): Specific factors to analyze
- `metrics` (List[str], optional): Target metrics to correlate with

**Request Example**:
```
GET /api/v1/productivity-correlations/analyze?user_id=user123&time_period=last_30_days&factors=sleep_quality,physical_activity,medication_adherence&metrics=task_completion,focus_duration
```

**Response**:
- 200 OK: Correlation analysis results
- 400 Bad Request: Invalid parameters
- 401 Unauthorized: Authentication required
- 403 Forbidden: Insufficient permissions
- 500 Internal Server Error: Service error

**Response Example**:
```json
{
  "correlations": [
    {
      "factor": "sleep_quality",
      "metric": "task_completion",
      "correlation_coefficient": 0.72,
      "significance": "high",
      "direction": "positive",
      "insight": "Higher sleep quality strongly correlates with better task completion rates"
    },
    {
      "factor": "sleep_quality",
      "metric": "focus_duration",
      "correlation_coefficient": 0.68,
      "significance": "high",
      "direction": "positive",
      "insight": "Higher sleep quality correlates with longer periods of focused work"
    },
    {
      "factor": "physical_activity",
      "metric": "task_completion",
      "correlation_coefficient": 0.54,
      "significance": "medium",
      "direction": "positive",
      "insight": "Physical activity shows moderate correlation with task completion"
    },
    {
      "factor": "physical_activity",
      "metric": "focus_duration",
      "correlation_coefficient": 0.61,
      "significance": "medium",
      "direction": "positive",
      "insight": "Regular physical activity correlates with improved focus duration"
    },
    {
      "factor": "medication_adherence",
      "metric": "task_completion",
      "correlation_coefficient": 0.82,
      "significance": "high",
      "direction": "positive",
      "insight": "Consistent medication adherence strongly correlates with task completion"
    },
    {
      "factor": "medication_adherence",
      "metric": "focus_duration",
      "correlation_coefficient": 0.79,
      "significance": "high",
      "direction": "positive",
      "insight": "Medication adherence shows strong positive correlation with focus duration"
    }
  ],
  "recommendations": [
    {
      "title": "Improve sleep quality",
      "description": "Your data shows sleep quality has significant impact on productivity",
      "suggested_actions": [
        "Maintain consistent sleep schedule",
        "Reduce screen time before bed",
        "Consider sleep tracking app integration"
      ],
      "expected_impact": "high"
    },
    {
      "title": "Maintain medication consistency",
      "description": "Medication adherence shows strongest correlation with performance",
      "suggested_actions": [
        "Set up medication reminders",
        "Track medication effects",
        "Discuss timing optimization with healthcare provider"
      ],
      "expected_impact": "high"
    }
  ],
  "metadata": {
    "data_points": 258,
    "analysis_confidence": "high",
    "model_version": "correlation_analyzer_v2.4"
  }
}
```

### `get_productivity_clusters(user_id: str, n_clusters: int = 3) -> Dict`

Identifies distinct clusters/patterns in a user's productivity data.

**Endpoint**: `GET /api/v1/productivity-correlations/clusters`

**Parameters**:
- `user_id` (str, required): User identifier
- `n_clusters` (int, optional): Number of clusters to identify
- `time_period` (str, optional): Time period for analysis
- `include_visualization` (bool, optional): Include visualization data

**Request Example**:
```
GET /api/v1/productivity-correlations/clusters?user_id=user123&n_clusters=4&time_period=last_90_days&include_visualization=true
```

**Response**:
- 200 OK: Cluster analysis results
- 400 Bad Request: Invalid parameters
- 401 Unauthorized: Authentication required
- 403 Forbidden: Insufficient permissions
- 500 Internal Server Error: Service error

**Response Example**:
```json
{
  "clusters": [
    {
      "id": "cluster_1",
      "name": "High Performance Days",
      "size": 21,
      "characteristics": {
        "task_completion": "high (avg: 92%)",
        "focus_duration": "high (avg: 5.2 hours)",
        "energy_level": "high (avg: 85/100)",
        "stress_level": "low (avg: 25/100)"
      },
      "common_factors": [
        "Good sleep (7+ hours)",
        "Morning medication",
        "Physical activity",
        "Low interruptions"
      ],
      "common_weekdays": ["Tuesday", "Wednesday", "Thursday"]
    },
    {
      "id": "cluster_2",
      "name": "Moderate Performance Days",
      "size": 42,
      "characteristics": {
        "task_completion": "medium (avg: 75%)",
        "focus_duration": "medium (avg: 3.8 hours)",
        "energy_level": "medium (avg: 65/100)",
        "stress_level": "medium (avg: 50/100)"
      },
      "common_factors": [
        "Average sleep (6-7 hours)",
        "Regular schedule",
        "Mixed interruption levels"
      ],
      "common_weekdays": ["Monday", "Friday"]
    },
    {
      "id": "cluster_3",
      "name": "Low Performance Days",
      "size": 18,
      "characteristics": {
        "task_completion": "low (avg: 45%)",
        "focus_duration": "low (avg: 2.1 hours)",
        "energy_level": "low (avg: 40/100)",
        "stress_level": "high (avg: 75/100)"
      },
      "common_factors": [
        "Poor sleep (<6 hours)",
        "Missed medication",
        "High interruptions",
        "Multiple meetings"
      ],
      "common_weekdays": ["Monday", "Friday"]
    },
    {
      "id": "cluster_4",
      "name": "Weekend Pattern",
      "size": 24,
      "characteristics": {
        "task_completion": "variable (avg: 65%)",
        "focus_duration": "medium (avg: 3.2 hours)",
        "energy_level": "variable (avg: 60/100)",
        "stress_level": "low (avg: 30/100)"
      },
      "common_factors": [
        "Irregular sleep pattern",
        "Different environment",
        "No scheduled meetings"
      ],
      "common_weekdays": ["Saturday", "Sunday"]
    }
  ],
  "visualization_data": {
    "type": "scatter_plot",
    "x_axis": "energy_level",
    "y_axis": "focus_duration",
    "points": [
      /* Array of data points for visualization - truncated for brevity */
    ],
    "cluster_centroids": [
      {
        "cluster_id": "cluster_1",
        "x": 85,
        "y": 5.2
      },
      {
        "cluster_id": "cluster_2",
        "x": 65,
        "y": 3.8
      },
      {
        "cluster_id": "cluster_3",
        "x": 40,
        "y": 2.1
      },
      {
        "cluster_id": "cluster_4",
        "x": 60,
        "y": 3.2
      }
    ]
  },
  "recommendations": [
    {
      "title": "Capitalize on high performance patterns",
      "description": "Schedule important tasks during your high performance days",
      "suggested_actions": [
        "Schedule deep work on Tuesday-Thursday",
        "Maintain sleep and medication schedule",
        "Block interruptions during peak performance times"
      ]
    },
    {
      "title": "Improve low performance patterns",
      "description": "Address factors leading to low performance days",
      "suggested_actions": [
        "Improve sleep hygiene on Sunday and Thursday nights",
        "Set up medication reminders",
        "Block meeting-free time on Mondays"
      ]
    }
  ],
  "metadata": {
    "clustering_algorithm": "k-means",
    "silhouette_score": 0.72,
    "data_points": 105,
    "model_version": "cluster_analyzer_v1.8"
  }
}
```

## MentalHealthFederatedModel API

Base URL: `/api/v1/mental-health-insights`

### `get_anonymized_insights(user_id: str) -> Dict`

Retrieves privacy-preserving insights about mental health and productivity patterns.

**Endpoint**: `GET /api/v1/mental-health-insights/anonymized`

**Parameters**:
- `user_id` (str, required): User identifier
- `insight_categories` (List[str], optional): Categories of insights to retrieve
- `privacy_level` (str, optional): Privacy level setting

**Request Example**:
```
GET /api/v1/mental-health-insights/anonymized?user_id=user123&insight_categories=mood,sleep,focus&privacy_level=high
```

**Response**:
- 200 OK: Anonymized insights
- 400 Bad Request: Invalid parameters
- 401 Unauthorized: Authentication required
- 403 Forbidden: Insufficient permissions
- 500 Internal Server Error: Service error

**Response Example**:
```json
{
  "insights": [
    {
      "category": "mood",
      "insight": "Your mood pattern shows improvement correlation with consistent sleep schedule",
      "confidence": "high",
      "privacy_impact": "none",
      "population_percentile": 78,
      "actionable_recommendation": "Maintain consistent sleep schedule, especially on weekdays"
    },
    {
      "category": "sleep",
      "insight": "Sleep quality appears to improve with evening exercise",
      "confidence": "medium",
      "privacy_impact": "none",
      "population_percentile": 65,
      "actionable_recommendation": "Consider light physical activity 2-3 hours before bedtime"
    },
    {
      "category": "focus",
      "insight": "Your focus duration is significantly higher in morning hours compared to population average",
      "confidence": "high",
      "privacy_impact": "none",
      "population_percentile": 92,
      "actionable_recommendation": "Schedule high-priority tasks in morning hours to leverage your natural pattern"
    }
  ],
  "aggregated_metrics": {
    "overall_focus_trend": "improving",
    "overall_mood_trend": "stable",
    "overall_sleep_trend": "slightly improving"
  },
  "privacy_statement": {
    "data_processing": "All insights are derived from on-device processing",
    "data_storage": "No raw mental health data is stored on servers",
    "anonymization_level": "high",
    "epsilon_guarantee": 0.1
  },
  "metadata": {
    "model_version": "federated_insights_v1.5",
    "privacy_budget_remaining": 0.87,
    "insight_refresh_available": "2023-04-08T00:00:00Z"
  }
}
```

### `update_privacy_settings(user_id: str, settings: Dict) -> Dict`

Updates privacy settings for mental health data collection and processing.

**Endpoint**: `PATCH /api/v1/mental-health-insights/privacy-settings`

**Parameters**:
- `user_id` (str, required): User identifier
- `settings` (Dict, required): Privacy settings to update
  - `data_sharing_level` (str, optional): Data sharing level
  - `federated_learning_opt_in` (bool, optional): Opt in to federated learning
  - `data_retention_days` (int, optional): Data retention period
  - `anonymization_strength` (str, optional): Anonymization strength

**Request Example**:
```json
{
  "settings": {
    "data_sharing_level": "aggregated_only",
    "federated_learning_opt_in": true,
    "data_retention_days": 60,
    "anonymization_strength": "high"
  }
}
```

**Response**:
- 200 OK: Updated privacy settings
- 400 Bad Request: Invalid settings
- 401 Unauthorized: Authentication required
- 403 Forbidden: Insufficient permissions
- 500 Internal Server Error: Service error

**Response Example**:
```json
{
  "updated_settings": {
    "data_sharing_level": "aggregated_only",
    "federated_learning_opt_in": true,
    "data_retention_days": 60,
    "anonymization_strength": "high"
  },
  "privacy_impact": {
    "insight_quality": "high",
    "available_features": ["anonymized_insights", "population_comparisons", "trend_analysis"],
    "unavailable_features": ["raw_data_export", "third_party_sharing"]
  },
  "next_model_training": "2023-04-05T00:00:00Z",
  "metadata": {
    "settings_updated_at": "2023-04-01T10:15:30Z",
    "settings_effective_from": "2023-04-01T10:15:30Z"
  }
}
```

## Error Handling

All APIs follow consistent error handling patterns:

### Error Response Structure

```json
{
  "error": {
    "error_code": "VALIDATION_ERROR",
    "message": "Invalid parameter value",
    "details": {
      "field": "date",
      "issue": "must be a valid ISO8601 date"
    },
    "request_id": "req_xyz789",
    "timestamp": "2023-04-01T10:25:30Z"
  }
}
```

### Common Error Codes

| HTTP Status | Error Code | Description |
|-------------|------------|-------------|
| 400 | VALIDATION_ERROR | Invalid input parameter |
| 400 | MALFORMED_REQUEST | Request format incorrect |
| 401 | AUTHENTICATION_REQUIRED | Authentication missing |
| 401 | INVALID_CREDENTIALS | Invalid authentication credentials |
| 403 | PERMISSION_DENIED | Insufficient permissions |
| 404 | RESOURCE_NOT_FOUND | Requested resource not found |
| 409 | RESOURCE_CONFLICT | Resource already exists |
| 429 | RATE_LIMIT_EXCEEDED | Too many requests |
| 500 | INTERNAL_ERROR | Internal server error |
| 503 | SERVICE_UNAVAILABLE | Service temporarily unavailable |

## Authentication and Authorization

### Authentication Methods

1. **JWT Bearer Token**
   - Include in Authorization header: `Authorization: Bearer {token}`
   - Tokens expire after 24 hours
   - Refresh tokens available at `/api/v1/auth/refresh`

2. **API Key** (for server-to-server)
   - Include in X-API-Key header: `X-API-Key: {api_key}`
   - Rate limits based on service tier

### Authorization Model

- User-level access control for all APIs
- Resource ownership validation
- Role-based permissions for specific operations

## Rate Limiting

### Default Rate Limits

| API | Rate Limit | Window | Burst |
|-----|------------|--------|-------|
| ProductivityPatternLSTM | 60 requests | 1 minute | 10 |
| CircadianRhythmModel | 30 requests | 1 minute | 5 |
| ProductivityCorrelationSystem | 20 requests | 1 minute | 5 |
| MentalHealthFederatedModel | 10 requests | 1 minute | 3 |

### Rate Limit Headers

All responses include rate limit headers:
- `X-RateLimit-Limit`: Maximum requests allowed in time window
- `X-RateLimit-Remaining`: Requests remaining in current window
- `X-RateLimit-Reset`: Unix timestamp when limit resets

## API Versioning

The APIs follow semantic versioning and maintain backward compatibility within major versions.

### Version Specification

- Version in URL path: `/api/v1/productivity-patterns`
- Current version: v1
- Version header option: `X-API-Version: v1`

## SDKs and Client Libraries

Official client libraries are available for common programming languages:

### Official SDKs

- **Python**: `pip install adhd-calendar-client`
- **JavaScript**: `npm install adhd-calendar-client`
- **Java**: Available via Maven
- **Swift/iOS**: Available via CocoaPods
- **Kotlin/Android**: Available via Gradle

### Usage Example (Python)

```python
from adhd_calendar import ADHDCalendarClient

# Initialize client
client = ADHDCalendarClient(api_key="your_api_key")

# Get optimal windows
windows = client.productivity_patterns.detect_optimal_windows(
    user_id="user123",
    days_ahead=5,
    min_window_length_minutes=45
)

# Predict circadian rhythm
daily_curve = client.circadian_rhythm.predict_daily_curve(
    user_id="user123",
    date="2023-04-01"
)

# Analyze correlations
correlations = client.productivity_correlations.analyze_correlations(
    user_id="user123",
    time_period="last_30_days"
)
``` 