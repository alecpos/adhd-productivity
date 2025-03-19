# Epic 4: API Reference - Dynamic Schedule Rebalancing

This document provides detailed API reference documentation for the Dynamic Schedule Rebalancing system, focusing on circadian rhythm optimization endpoints.

## Base URL

All API endpoints are relative to the base URL:

```
https://api.adhd-calendar.com/v1
```

## Authentication

All API requests require authentication using a Bearer token:

```
Authorization: Bearer <your_api_token>
```

## Endpoints

### Circadian Schedule Optimization

#### Request Optimization

`POST /scheduling/circadian-optimize`

Generate an optimized schedule based on circadian patterns and task requirements.

**Request Body:**

```json
{
  "start_date": "2023-09-01T00:00:00Z",
  "end_date": "2023-09-07T23:59:59Z",
  "tasks": [
    {
      "id": "task-123",
      "title": "Write project proposal",
      "description": "Create detailed proposal for client project",
      "duration_minutes": 120,
      "focus_required": 8,
      "executive_function_load": 7,
      "creative_required": 6,
      "complexity": 7,
      "priority": "HIGH",
      "is_flexible": true,
      "deadline": "2023-09-05T17:00:00Z"
    },
    ...
  ],
  "preferences": {
    "work_hours": {
      "start": "09:00",
      "end": "17:00"
    },
    "optimization_strength": 0.8,
    "respect_existing_events": true,
    "allow_breaks": true,
    "break_duration_minutes": 15
  }
}
```

**Response:**

```json
{
  "schedule": [
    {
      "task_id": "task-123",
      "title": "Write project proposal",
      "start_time": "2023-09-01T10:30:00Z",
      "end_time": "2023-09-01T12:30:00Z",
      "energy_level": 8.5,
      "match_score": 0.92,
      "match_explanation": "High focus task scheduled during peak energy window"
    },
    ...
  ],
  "energy_curve": [
    {
      "date": "2023-09-01",
      "hourly_levels": [
        { "hour": 0, "level": 2.1 },
        { "hour": 1, "level": 1.5 },
        ...
        { "hour": 23, "level": 3.2 }
      ]
    },
    ...
  ],
  "message": "Schedule optimized successfully with 12 tasks"
}
```

**Status Codes:**

- `200 OK`: Successful request
- `400 Bad Request`: Invalid parameters
- `401 Unauthorized`: Authentication failed
- `403 Forbidden`: Not authorized for this resource
- `500 Internal Server Error`: Server error

#### Apply Optimization

`POST /scheduling/apply-circadian-optimization`

Apply a generated optimization to the user's calendar.

**Request Body:**

```json
{
  "optimization_id": "opt-789",
  "calendar_id": "cal-456",
  "modifications": [
    {
      "task_id": "task-123",
      "action": "SCHEDULE",
      "start_time": "2023-09-01T10:30:00Z",
      "end_time": "2023-09-01T12:30:00Z"
    },
    ...
  ],
  "notify_user": true
}
```

**Response:**

```json
{
  "success": true,
  "applied_changes": 12,
  "failed_changes": 0,
  "calendar_link": "https://calendar.example.com/user/view?date=2023-09-01",
  "message": "Schedule optimization applied successfully"
}
```

**Status Codes:**

- `200 OK`: Successful request
- `400 Bad Request`: Invalid parameters
- `401 Unauthorized`: Authentication failed
- `403 Forbidden`: Not authorized for this resource
- `500 Internal Server Error`: Server error

### Energy Prediction

#### Get Energy Curve

`GET /circadian/energy-curve`

Retrieve the predicted energy curve for a user over a specified period.

**Parameters:**

- `start_date` (required): ISO 8601 start date
- `end_date` (required): ISO 8601 end date
- `resolution` (optional): Temporal resolution ('hourly', 'daily', 'weekly'). Default: 'hourly'

**Response:**

```json
{
  "user_id": "user-345",
  "model_version": "2.3.0",
  "confidence_score": 0.85,
  "energy_data": [
    {
      "date": "2023-09-01",
      "hourly_levels": [
        {
          "timestamp": "2023-09-01T00:00:00Z",
          "energy_level": 2.1,
          "focus_capacity": 1.8,
          "creative_capacity": 3.2,
          "executive_function_capacity": 1.5
        },
        ...
      ]
    },
    ...
  ],
  "optimal_windows": [
    {
      "date": "2023-09-01",
      "windows": [
        {
          "type": "FOCUS",
          "start": "2023-09-01T10:00:00Z",
          "end": "2023-09-01T12:30:00Z",
          "strength": 0.92
        },
        {
          "type": "CREATIVE",
          "start": "2023-09-01T15:00:00Z",
          "end": "2023-09-01T17:00:00Z",
          "strength": 0.87
        },
        ...
      ]
    },
    ...
  ]
}
```

**Status Codes:**

- `200 OK`: Successful request
- `400 Bad Request`: Invalid parameters
- `401 Unauthorized`: Authentication failed
- `403 Forbidden`: Not authorized for this resource
- `500 Internal Server Error`: Server error

#### Report Energy Level

`POST /circadian/report-energy`

Submit user-reported energy levels to improve model accuracy.

**Request Body:**

```json
{
  "timestamp": "2023-09-01T14:30:00Z",
  "energy_level": 7,
  "focus_level": 8,
  "mood": "PRODUCTIVE",
  "context": {
    "location": "OFFICE",
    "activity": "WORKING",
    "recent_meal": true,
    "recent_exercise": false
  },
  "notes": "Feeling very productive after lunch meeting"
}
```

**Response:**

```json
{
  "success": true,
  "message": "Energy data recorded successfully",
  "data_points_collected_today": 5,
  "prediction_accuracy": {
    "previous": 0.82,
    "current": 0.84,
    "improvement": "+2.4%"
  }
}
```

**Status Codes:**

- `200 OK`: Successful request
- `400 Bad Request`: Invalid parameters
- `401 Unauthorized`: Authentication failed
- `403 Forbidden`: Not authorized for this resource
- `500 Internal Server Error`: Server error

### Task Cognitive Analysis

#### Analyze Task Demands

`POST /tasks/analyze-cognitive-demands`

Analyze the cognitive demands of a task description.

**Request Body:**

```json
{
  "title": "Quarterly financial report",
  "description": "Compile and analyze Q3 financial data, create visualizations, and write executive summary",
  "duration_estimate_minutes": 180,
  "task_type": "WORK",
  "previous_instances": [
    {
      "date": "2023-06-15",
      "duration_actual_minutes": 210,
      "completion_rating": 4,
      "difficulty_rating": 7,
      "energy_drain": 8
    }
  ]
}
```

**Response:**

```json
{
  "analysis": {
    "focus_required": 8,
    "executive_function_load": 7,
    "creative_required": 5,
    "complexity": 7,
    "energy_demand": "HIGH",
    "expected_duration_minutes": 195,
    "confidence": 0.86
  },
  "recommendations": {
    "optimal_time_of_day": "MORNING",
    "suggested_breaks": 2,
    "break_interval_minutes": 45,
    "preparation_steps": [
      "Gather all financial data before starting",
      "Review previous quarter's report structure"
    ]
  }
}
```

**Status Codes:**

- `200 OK`: Successful request
- `400 Bad Request`: Invalid parameters
- `401 Unauthorized`: Authentication failed
- `403 Forbidden`: Not authorized for this resource
- `500 Internal Server Error`: Server error

#### Get Task Completion Analytics

`GET /tasks/cognitive-completion-analytics`

Retrieve analytics about task completion rates correlated with cognitive demands and timing.

**Parameters:**

- `start_date` (required): ISO 8601 start date
- `end_date` (required): ISO 8601 end date
- `task_types` (optional): Filter by task types (comma-separated)
- `grouping` (optional): Group results by ('day', 'time_of_day', 'task_type', 'cognitive_demand'). Default: 'time_of_day'

**Response:**

```json
{
  "period": {
    "start": "2023-08-01T00:00:00Z",
    "end": "2023-08-31T23:59:59Z"
  },
  "total_tasks": 156,
  "completion_rate": 0.74,
  "analytics": {
    "by_time_of_day": [
      {
        "time_range": "06:00-09:00",
        "completion_rate": 0.83,
        "task_count": 35,
        "avg_satisfaction": 4.2,
        "avg_focus_required": 7.1
      },
      {
        "time_range": "09:00-12:00",
        "completion_rate": 0.89,
        "task_count": 45,
        "avg_satisfaction": 4.5,
        "avg_focus_required": 7.8
      },
      ...
    ],
    "by_cognitive_demand": [
      {
        "demand_level": "HIGH_FOCUS",
        "completion_rate": 0.72,
        "optimal_time_ranges": [
          { "range": "09:00-12:00", "completion_rate": 0.91 },
          { "range": "16:00-18:00", "completion_rate": 0.76 }
        ]
      },
      ...
    ]
  },
  "recommendations": {
    "high_focus_optimal_windows": [
      { "day": "WEEKDAY", "start": "09:00", "end": "11:30" },
      { "day": "WEEKEND", "start": "10:00", "end": "13:00" }
    ],
    "creative_tasks_optimal_windows": [
      { "day": "WEEKDAY", "start": "14:00", "end": "16:00" },
      { "day": "WEEKEND", "start": "15:00", "end": "18:00" }
    ],
    ...
  }
}
```

**Status Codes:**

- `200 OK`: Successful request
- `400 Bad Request`: Invalid parameters
- `401 Unauthorized`: Authentication failed
- `403 Forbidden`: Not authorized for this resource
- `500 Internal Server Error`: Server error

### Model Management

#### Get Model Status

`GET /circadian/model-status`

Get information about the user's circadian model status and quality.

**Response:**

```json
{
  "model_id": "cm-12345",
  "version": "2.3.1",
  "created_at": "2023-08-15T00:00:00Z",
  "last_updated": "2023-09-01T14:30:00Z",
  "training_data_points": 342,
  "confidence_score": 0.86,
  "prediction_accuracy": 0.83,
  "adaptation_speed": "MEDIUM",
  "data_quality": {
    "coverage": 0.78,
    "consistency": 0.82,
    "recency": 0.94
  },
  "recommendations": {
    "needs_more_data": false,
    "suggested_actions": [
      "Report energy levels more consistently on weekends",
      "Add more data about evening energy patterns"
    ]
  }
}
```

**Status Codes:**

- `200 OK`: Successful request
- `401 Unauthorized`: Authentication failed
- `403 Forbidden`: Not authorized for this resource
- `500 Internal Server Error`: Server error

#### Reset Model

`POST /circadian/reset-model`

Reset the user's circadian model to start fresh training.

**Request Body:**

```json
{
  "reset_type": "FULL",
  "preserve_preferences": true,
  "reason": "LIFESTYLE_CHANGE",
  "notes": "Changed work schedule from day shift to night shift"
}
```

**Response:**

```json
{
  "success": true,
  "message": "Circadian model has been reset successfully",
  "new_model_id": "cm-67890",
  "estimated_training_period_days": 14,
  "next_steps": [
    "Complete the initial questionnaire",
    "Log your energy levels regularly for the next two weeks",
    "Provide feedback on task scheduling accuracy"
  ]
}
```

**Status Codes:**

- `200 OK`: Successful request
- `400 Bad Request`: Invalid parameters
- `401 Unauthorized`: Authentication failed
- `403 Forbidden`: Not authorized for this resource
- `500 Internal Server Error`: Server error

## Data Models

### CircadianCalendarOptimizationRequest

```typescript
interface CircadianCalendarOptimizationRequest {
  start_date: string;  // ISO 8601 format
  end_date: string;    // ISO 8601 format
  tasks: TaskSchema[];
  preferences?: UserPreferences;
}
```

### TaskSchema

```typescript
interface TaskSchema {
  id?: string;
  title: string;
  description?: string;
  duration_minutes: number;
  focus_required?: number;  // 1-10 scale
  executive_function_load?: number;  // 1-10 scale
  creative_required?: number;  // 1-10 scale
  complexity?: number;  // 1-10 scale
  priority: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  is_flexible: boolean;
  deadline?: string;  // ISO 8601 format
}
```

### UserPreferences

```typescript
interface UserPreferences {
  work_hours?: {
    start: string;  // HH:MM format
    end: string;    // HH:MM format
  };
  weekend_different?: boolean;
  weekend_work_hours?: {
    start: string;  // HH:MM format
    end: string;    // HH:MM format
  };
  optimization_strength?: number;  // 0.0-1.0
  respect_existing_events?: boolean;
  allow_breaks?: boolean;
  break_duration_minutes?: number;
  avoid_switching_costs?: boolean;
  group_similar_tasks?: boolean;
}
```

### CircadianCalendarOptimizationResponse

```typescript
interface CircadianCalendarOptimizationResponse {
  schedule: OptimizedTimeBlock[];
  energy_curve: HourlyEnergyLevel[][];
  message: string;
}
```

### OptimizedTimeBlock

```typescript
interface OptimizedTimeBlock {
  task_id: string;
  title: string;
  start_time: string;  // ISO 8601 format
  end_time: string;    // ISO 8601 format
  energy_level: number;
  match_score: number;
  match_explanation: string;
}
```

### HourlyEnergyLevel

```typescript
interface HourlyEnergyLevel {
  date: string;  // YYYY-MM-DD format
  hourly_levels: {
    hour: number;  // 0-23
    level: number; // 0.0-10.0
  }[];
}
```

## Error Responses

All error responses follow this format:

```json
{
  "error": {
    "code": "INVALID_DATE_RANGE",
    "message": "End date must be after start date",
    "details": {
      "start_date": "2023-09-07T00:00:00Z",
      "end_date": "2023-09-01T23:59:59Z"
    }
  },
  "request_id": "req-abcdef123456"
}
```

### Common Error Codes

- `INVALID_PARAMETERS`: Request parameters are invalid
- `INVALID_DATE_RANGE`: Date range is invalid
- `INSUFFICIENT_DATA`: Not enough data to generate accurate predictions
- `MODEL_NOT_READY`: Circadian model isn't fully trained yet
- `RATE_LIMIT_EXCEEDED`: Too many requests in a short period
- `AUTHENTICATION_FAILED`: Authentication credentials are invalid
- `AUTHORIZATION_FAILED`: User doesn't have permission for this action
- `RESOURCE_NOT_FOUND`: Requested resource doesn't exist
- `INTERNAL_ERROR`: An internal server error occurred

## Rate Limits

- Standard tier: 100 requests per hour
- Premium tier: 500 requests per hour
- Enterprise tier: Customized limits

When rate limits are exceeded, the API returns a `429 Too Many Requests` status code.

## Webhooks

Subscribe to real-time events using webhooks:

### Available Events

- `circadian.model.updated`: Triggered when the user's circadian model is updated
- `schedule.optimization.completed`: Triggered when schedule optimization completes
- `energy.prediction.updated`: Triggered when energy predictions are updated

### Webhook Subscription

`POST /webhooks/subscribe`

**Request Body:**

```json
{
  "url": "https://your-app.com/webhook-handler",
  "events": ["schedule.optimization.completed", "energy.prediction.updated"],
  "secret": "your-webhook-secret"
}
```

**Response:**

```json
{
  "subscription_id": "sub-123456",
  "url": "https://your-app.com/webhook-handler",
  "events": ["schedule.optimization.completed", "energy.prediction.updated"],
  "created_at": "2023-09-01T12:34:56Z",
  "status": "ACTIVE"
}
```

## SDK Support

The Dynamic Schedule Rebalancing API is supported in the following client SDKs:

- JavaScript/TypeScript: [@adhd-calendar/client-js](https://www.npmjs.com/package/@adhd-calendar/client-js)
- Python: [adhd-calendar-python](https://pypi.org/project/adhd-calendar-python/)
- Swift: [ADHDCalendarKit](https://github.com/adhd-calendar/ADHDCalendarKit)
- Kotlin: [adhd-calendar-android](https://github.com/adhd-calendar/adhd-calendar-android)

## Release Notes

### v2.3.1 (Current)

- Added support for medication timing in circadian models
- Improved prediction accuracy for irregular sleep schedules
- Fixed bug in task cognitive demand analysis for complex multi-step tasks
- Added new analytics endpoints for pattern visualization

### v2.3.0

- Introduced the Dynamic Schedule Rebalancing feature
- Added circadian rhythm optimization endpoints
- Implemented cognitive demand analysis for tasks
- Added support for energy level reporting 