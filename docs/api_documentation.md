# API Documentation

This document provides comprehensive documentation for the ADHD Calendar API endpoints.

## API Overview

The ADHD Calendar API is a RESTful API built using FastAPI. It provides endpoints for managing users, tasks, events, and accessing ML-powered features like productivity pattern recognition, time estimation, and commitment detection.

## Base URL

All API endpoints are prefixed with `/api/v1`.

## Authentication

Most API endpoints require authentication. The API uses JWT (JSON Web Token) for authentication.

### Authentication Headers

```
Authorization: Bearer <token>
```

### Getting a Token

```http
POST /api/v1/auth/login
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "yourpassword"
}
```

Response:

```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 3600,
    "user": {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "email": "user@example.com",
        "full_name": "Test User"
    }
}
```

### Token Refresh

To refresh the token before it expires:

```http
POST /api/v1/auth/refresh
Authorization: Bearer <token>
```

## API Endpoints

### Authentication

| Method | Endpoint              | Description                 |
|--------|------------------------|-----------------------------|
| POST   | /auth/register        | Register a new user         |
| POST   | /auth/login           | Login and get token         |
| POST   | /auth/refresh         | Refresh token               |
| POST   | /auth/change-password | Change user password        |
| POST   | /auth/forgot-password | Begin password reset process |
| POST   | /auth/reset-password  | Complete password reset     |

### Users

| Method | Endpoint           | Description                  |
|--------|-------------------|------------------------------|
| GET    | /users/me         | Get current user profile     |
| PATCH  | /users/me         | Update current user profile  |
| GET    | /users/me/settings | Get user settings           |
| PATCH  | /users/me/settings | Update user settings        |

| Method | Endpoint           | Description                  |
|--------|-------------------|------------------------------|
| POST   | /users/           | Create a new user            |
| GET    | /users/{user_id}  | Get user by ID               |
| PUT    | /users/{user_id}  | Update user                  |
| DELETE | /users/{user_id}  | Delete user                  |

### Tasks

| Method | Endpoint             | Description                      | Implementation Status |
|--------|--------------------|----------------------------------|----------------------|
| GET    | /tasks/user/{user_id} | List user's tasks               | ✅ Implemented        |
| POST   | /tasks              | Create a new task                | ✅ Implemented        |
| PUT    | /tasks/{task_id}    | Update a task                    | ✅ Implemented        |
| DELETE | /tasks/{task_id}    | Delete a task                    | ✅ Implemented        |
| POST   | /tasks/{task_id}/complete | Mark a task as complete    | ✅ Implemented        |
| GET    | /tasks/statistics   | Get task statistics              | ✅ Implemented        |
| POST   | /tasks/{task_id}/defer | Defer a task                  | ⚠️ Planned           |
| GET    | /tasks/upcoming     | Get upcoming tasks               | ⚠️ Planned           |
| GET    | /tasks/overdue      | Get overdue tasks                | ⚠️ Planned           |

> Note: Endpoints marked as "Planned" are documented for future implementation but not currently available in the API.

### Calendar Events

| Method | Endpoint                | Description                      | Implementation Status |
|--------|------------------------|----------------------------------|----------------------|
| GET    | /calendar/events                | List user's events               | ✅ Implemented        |
| POST   | /calendar/events                | Create a new event               | ✅ Implemented        |
| GET    | /calendar/events/{event_id}     | Get a specific event             | ✅ Implemented        |
| PUT    | /calendar/events/{event_id}     | Update an event                  | ✅ Implemented        |
| DELETE | /calendar/events/{event_id}     | Delete an event                  | ✅ Implemented        |
| GET    | /calendar/events/upcoming       | Get upcoming events              | ⚠️ Planned           |
| GET    | /calendar/events/day/{date}     | Get events for a specific day    | ⚠️ Planned           |
| GET    | /calendar/events/week/{date}    | Get events for a specific week   | ⚠️ Planned           |
| GET    | /calendar/events/month/{date}   | Get events for a specific month  | ⚠️ Planned           |

> Note: Endpoints marked as "Planned" are documented for future implementation but not currently available in the API.

### Reminders

| Method | Endpoint                  | Description                      |
|--------|--------------------------|----------------------------------|
| GET    | /reminders               | List user's reminders            |
| POST   | /reminders               | Create a new reminder            |
| GET    | /reminders/{reminder_id} | Get a specific reminder          |
| PUT    | /reminders/{reminder_id} | Update a reminder                |
| DELETE | /reminders/{reminder_id} | Delete a reminder                |
| POST   | /reminders/{reminder_id}/snooze | Snooze a reminder        |

### Temporal Pattern Recognition (TPR)

| Method | Endpoint                | Description                      | Implementation Status |
|--------|------------------------|----------------------------------|----------------------|
| GET    | /analytics/productivity | Get productivity metrics         | ✅ Implemented (analytics_routes.py) |
| GET    | /analytics/focus-patterns | Get focus patterns            | ✅ Implemented (analytics_routes.py) |
| GET    | /analytics/trends      | Get productivity trends          | ✅ Implemented (analytics_routes.py) |
| GET    | /productivity/patterns | Get user's productivity patterns | ⚠️ Planned           |
| GET    | /productivity/insights | Get productivity insights        | ⚠️ Planned           |
| GET    | /productivity/recommendations | Get time-based recommendations | ⚠️ Planned           |

**Note:** Some TPR functionality is implemented in analytics_routes.py, but with different endpoints than originally documented. The endpoints with `/productivity` prefix are planned for future implementation.

### Time Management & Estimation

| Method | Endpoint                | Description                      | Implementation Status |
|--------|------------------------|----------------------------------|----------------------|
| GET    | /time-management/analytics | Get time analytics           | ✅ Implemented (time_management_routes.py) |
| POST   | /time-management/optimize | Optimize schedule             | ✅ Implemented (time_management_routes.py) |
| GET    | /time-management/suggestions | Get block suggestions      | ✅ Implemented (time_management_routes.py) |
| POST   | /tasks/{task_id}/estimate | Get time estimate for a task    | ⚠️ Planned           |
| POST   | /tasks/sequence/estimate | Get time estimates for task sequence | ⚠️ Planned           |
| POST   | /time-estimation/estimate | Estimate time for a task       | ⚠️ Planned           |
| GET    | /time-estimation/history | Get time estimation history     | ⚠️ Planned           |
| GET    | /time-estimation/accuracy | Get time estimation accuracy   | ⚠️ Planned           |
| POST   | /time-estimation/feedback | Provide feedback on estimate   | ⚠️ Planned           |

**Note:** Some time management functionality is implemented in time_management_routes.py, but dedicated time estimation endpoints are planned for future implementation.

### Commitments

| Method | Endpoint                      | Description                           | Implementation Status |
|--------|------------------------------|---------------------------------------|----------------------|
| GET    | /commitments                 | List user's commitments               | ⚠️ Planned           |
| POST   | /commitments                 | Create a new commitment               | ⚠️ Planned           |
| GET    | /commitments/{commitment_id} | Get a specific commitment             | ⚠️ Planned           |
| PUT    | /commitments/{commitment_id} | Update a commitment                   | ⚠️ Planned           |
| DELETE | /commitments/{commitment_id} | Delete a commitment                   | ⚠️ Planned           |
| POST   | /commitments/detect          | Detect commitments from text          | ⚠️ Planned           |

**Note:** While there is a commitment model defined in the database schema, the API routes for commitments are not currently implemented. The "Transformer-based Commitment Detection" functionality mentioned in the ML README is planned for future implementation.

### Schedule Optimization

| Method | Endpoint                      | Description                           | Implementation Status |
|--------|------------------------------|---------------------------------------|----------------------|
| POST   | /blocks                      | Schedule blocks for a user            | ✅ Implemented        |
| GET    | /stats                       | Get schedule statistics               | ✅ Implemented        |
| POST   | /optimize                    | Generate optimized schedule           | ✅ Implemented        |
| GET    | /optimizer                   | Get schedule optimizer service        | ✅ Implemented        |
| GET    | /schedule                    | Get user's current schedule           | ⚠️ Planned           |
| GET    | /schedule/day/{date}         | Get schedule for a specific day       | ⚠️ Planned           |
| GET    | /schedule/week/{date}        | Get schedule for a specific week      | ⚠️ Planned           |
| POST   | /schedule/apply              | Apply an optimized schedule           | ⚠️ Planned           |

> Note: The schedule optimization API is implemented in `block_scheduler_routes.py` rather than `schedule_routes.py`. Endpoints marked as "Planned" are documented for future implementation but not currently available in the API.

### Circadian Rhythm Optimization

| Method | Endpoint                      | Description                           | Implementation Status |
|--------|------------------------------|---------------------------------------|----------------------|
| POST   | /circadian-optimize          | Optimize schedule with circadian awareness | ✅ Implemented in scheduling_routes.py |
| POST   | /circadian-optimize-calendar | Optimize calendar events with circadian rhythm | ✅ Implemented in scheduling_routes.py |
| POST   | /apply-circadian-optimization | Apply circadian optimization results | ✅ Implemented in scheduling_routes.py |

> Note: These endpoints are implemented in `scheduling_routes.py` rather than in a dedicated `circadian_routes.py` file.

## Request and Response Examples

### Create a Task

Request:

```http
POST /api/v1/tasks
Authorization: Bearer <token>
Content-Type: application/json

{
    "title": "Complete project proposal",
    "description": "Finish the project proposal document",
    "priority": "high",
    "due_date": "2023-04-15T17:00:00Z",
    "estimated_duration": 120,
    "tags": ["work", "project"]
}
```

Response:

```json
{
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "title": "Complete project proposal",
    "description": "Finish the project proposal document",
    "priority": "high",
    "status": "pending",
    "due_date": "2023-04-15T17:00:00Z",
    "estimated_duration": 120,
    "actual_duration": null,
    "tags": ["work", "project"],
    "created_at": "2023-04-10T14:30:00Z",
    "updated_at": "2023-04-10T14:30:00Z",
    "user_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

### Get Optimal Times for Task

Request:

```http
GET /api/v1/tpr/optimal-times?task_type=deep_focus&date=2023-04-15
Authorization: Bearer <token>
```

Response:

```json
{
    "date": "2023-04-15",
    "task_type": "deep_focus",
    "optimal_times": [
        {
            "start_time": "2023-04-15T09:00:00Z",
            "end_time": "2023-04-15T11:00:00Z",
            "productivity_score": 0.85,
            "confidence": "high"
        },
        {
            "start_time": "2023-04-15T15:00:00Z",
            "end_time": "2023-04-15T17:00:00Z",
            "productivity_score": 0.78,
            "confidence": "medium"
        }
    ]
}
```

### Estimate Time for a Task

Request:

```http
POST /api/v1/time-estimation/estimate
Authorization: Bearer <token>
Content-Type: application/json

{
    "task_description": "Write comprehensive API documentation for the ADHD Calendar app",
    "task_type": "writing",
    "additional_factors": {
        "similar_tasks_completed": true,
        "complexity": "medium"
    }
}
```

Response:

```json
{
    "task_description": "Write comprehensive API documentation for the ADHD Calendar app",
    "task_type": "writing",
    "mean_minutes": 180,
    "min_minutes": 120,
    "max_minutes": 240,
    "confidence_interval_90": [135, 225],
    "factors_considered": {
        "complexity": 0.65,
        "similar_tasks_history": 0.8,
        "user_velocity": 0.7
    },
    "confidence": "medium"
}
```

### Get Task Statistics

Request:

```http
GET /api/v1/tasks/statistics
Authorization: Bearer <token>
```

Response:

```json
{
    "total_tasks": 24,
    "completed_tasks": 18,
    "pending_tasks": 6,
    "overdue_tasks": 2,
    "completion_rate": 0.75,
    "average_completion_time": 120.5
}
```

## Error Handling

The API uses standard HTTP status codes and returns detailed error messages in the response body.

### Error Response Format

```json
{
    "status": "error",
    "code": "ERROR_CODE",
    "message": "A detailed error message",
    "details": {
        "field1": ["Error details related to field1"],
        "field2": ["Error details related to field2"]
    }
}
```

### Common Error Codes

| Status Code | Error Code           | Description                                     |
|-------------|----------------------|-------------------------------------------------|
| 400         | VALIDATION_ERROR     | Invalid request parameters                      |
| 401         | UNAUTHORIZED         | Authentication required                         |
| 403         | FORBIDDEN            | Insufficient permissions                        |
| 404         | NOT_FOUND            | Resource not found                              |
| 409         | CONFLICT             | Resource conflict (e.g., duplicate email)       |
| 422         | UNPROCESSABLE_ENTITY | Valid data but unable to process the request    |
| 429         | TOO_MANY_REQUESTS    | Rate limit exceeded                             |
| 500         | INTERNAL_ERROR       | Server error                                    |

## Pagination

List endpoints support pagination with the following query parameters:

- `page`: Page number (1-based, default: 1)
- `page_size`: Number of items per page (default: 20, max: 100)
- `sort_by`: Field to sort by (depends on the endpoint)
- `sort_order`: Sort order (`asc` or `desc`, default: `asc`)

Paginated responses include the following metadata:

```json
{
    "items": [...],
    "total": 100,
    "page": 1,
    "page_size": 20,
    "pages": 5,
    "has_next": true,
    "has_prev": false
}
```

## Filtering

List endpoints support filtering with query parameters specific to each endpoint. For example:

- `/api/v1/tasks?status=pending&priority=high`
- `/api/v1/events?start_date=2023-04-01&end_date=2023-04-30`

## Rate Limiting

The API implements rate limiting to protect against abuse. Rate limits are applied per user and vary by endpoint.

Rate limit headers are included in the response:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1680278400
```

## Versioning

The API is versioned using URL prefixes (e.g., `/api/v1`). When breaking changes are introduced, a new version will be created.

## Related Resources

- [API Design Guidelines](./api_design_guidelines.md)
- [Authentication Flow](./authentication_flow.md)
- [Error Handling Guide](./error_handling_guide.md) 