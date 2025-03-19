# API Documentation

## Overview

This document provides comprehensive documentation for the ADHD Calendar Backend API.

## Base URL

```
https://api.adhdcalendar.com/v1
```

## Authentication

All API requests require authentication using JWT tokens.

### Headers

```
Authorization: Bearer <token>
```

## Common Response Format

All endpoints return responses in the following format:

```json
{
  "status": "success" | "error",
  "data": <response_data>,
  "message": "Optional message",
  "metadata": {
    "version": "1.0",
    "timestamp": "2024-01-01T00:00:00Z"
  }
}
```

## Endpoints

### Task Management

#### GET /tasks

Get all tasks for the authenticated user.

**Query Parameters:**


- `priority`: Filter by priority
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 20)

**Response:**
```json
{
  "status": "success",
  "data": {
    "tasks": [
      {
        "id": "task_id",
        "title": "Task title",
        "description": "Task description",
        "status": "pending",
        "priority": "high",
        "due_date": "2024-01-01T00:00:00Z"
      }
    ],
    "pagination": {
      "total": 100,
      "page": 1,
      "limit": 20
    }
  }
}
```

### Calendar Management

#### POST /calendar/events

Create a new calendar event.

**Request Body:**
```json
{
  "title": "Event title",
  "description": "Event description",
  "start_time": "2024-01-01T09:00:00Z",
  "end_time": "2024-01-01T10:00:00Z",
  "attendees": ["user@example.com"],
  "location": "Optional location"
}
```

### Focus Sessions

#### POST /focus/pomodoro

Start a new pomodoro session.

**Request Body:**
```json
{
  "duration": 25,
  "task_id": "optional_task_id",
  "break_duration": 5
}
```

### Mental Health Tracking

#### POST /mental-health/mood

Log a mood entry.

**Request Body:**
```json
{
  "mood_level": 7,
  "notes": "Feeling productive",
  "energy_level": 8,
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### Body Doubling

#### POST /body-doubling/sessions

Create a new body doubling session.

**Request Body:**
```json
{
  "title": "Study Session",
  "description": "Group study for exam",
  "duration": 60,
  "max_participants": 4,
  "environment": "quiet"
}
```

### Analytics

#### GET /analytics/productivity

Get productivity analytics.

**Query Parameters:**
- `start_date`: Start date for analysis
- `end_date`: End date for analysis
- `metrics`: Comma-separated list of metrics

### User Management

#### PUT /users/preferences

Update user preferences.

**Request Body:**
```json
{
  "timezone": "UTC",
  "notification_preferences": {
    "email": true,
    "push": true
  },
  "default_focus_duration": 25
}
```

## Error Codes

- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 429: Too Many Requests
- 500: Internal Server Error

## Rate Limiting

- 1000 requests per hour per user
- Rate limit headers included in responses

## Versioning

- API version included in URL
- Breaking changes increment major version
- Backward compatibility maintained within versions

## WebSocket Events

Real-time updates available through WebSocket connection:
```
wss://api.adhdcalendar.com/v1/ws
```

### Event Types

- task.updated
- calendar.event.created
- focus.session.started
- body.doubling.participant.joined

## SDK Examples

### Python

```python
from adhd_calendar import Client

client = Client(api_key="your_api_key")
tasks = client.tasks.list(status="pending")
```

### JavaScript

```javascript
import { ADHDCalendar } from 'adhd-calendar';

const client = new ADHDCalendar('your_api_key');
const tasks = await client.tasks.list({ status: 'pending' });
```

## Best Practices

1. Use appropriate HTTP methods
2. Include proper error handling
3. Implement rate limiting
4. Use pagination for large datasets
5. Validate input data
6. Handle timezone differences
7. Implement proper security measures
8. Use proper status codes
9. Include comprehensive error messages
10. Maintain backward compatibility 