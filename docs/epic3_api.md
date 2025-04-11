# Epic 3: API Documentation

This document provides a comprehensive reference for the APIs exposed by the Epic 3 components.

## Table of Contents

1. [CommitmentDetectionService API](#commitmentdetectionservice-api)
2. [DialogueSystemService API](#dialoguesystemservice-api)
3. [SmartReminderService API](#smartreminderservice-api)
4. [Error Handling](#error-handling)
5. [Authentication and Authorization](#authentication-and-authorization)
6. [Rate Limiting](#rate-limiting)
7. [API Versioning](#api-versioning)
8. [SDKs and Client Libraries](#sdks-and-client-libraries)

## CommitmentDetectionService API

Base URL: `/api/v1/commitments`

### `detect_commitments(text: str, user_id: str = None, context: Dict = None) -> List[Dict]`

Detects commitments from text input.

**Endpoint**: `POST /api/v1/commitments/detect`

**Parameters**:
- `text` (str, required): Input text to analyze
- `user_id` (str, optional): User identifier for personalized detection
- `context` (Dict, optional): Additional context for improved detection
  - `source` (str, optional): Source of the text (email, chat, journal, etc.)
  - `location` (str, optional): Physical location when text was created
  - `related_entities` (List[str], optional): Related entities mentioned

**Request Example**:
```json
{
  "text": "I need to submit the report by Friday and call John next week.",
  "user_id": "user123",
  "context": {
    "source": "email",
    "related_entities": ["report", "John"]
  }
}
```

**Response**:
- 200 OK: List of detected commitments
- 400 Bad Request: Invalid input
- 401 Unauthorized: Authentication required
- 403 Forbidden: Insufficient permissions
- 500 Internal Server Error: Service error

**Response Example**:
```json
{
  "commitments": [
    {
      "id": "commit_temp_1",
      "text": "submit the report",
      "due_date": "2023-04-07",
      "time_frame": "by Friday",
      "confidence": 0.92,
      "priority": "medium",
      "source": "email"
    },
    {
      "id": "commit_temp_2",
      "text": "call John",
      "due_date": null,
      "time_frame": "next week",
      "confidence": 0.85,
      "priority": "low",
      "source": "email"
    }
  ],
  "metadata": {
    "processing_time_ms": 215,
    "source_text_length": 58
  }
}
```

### `save_commitment(commitment: Dict, user_id: str) -> Dict`

Saves a detected commitment to the database.

**Endpoint**: `POST /api/v1/commitments`

**Parameters**:
- `commitment` (Dict, required): Commitment data to save
  - `text` (str, required): Commitment text
  - `due_date` (str, optional): ISO8601 formatted date
  - `time_frame` (str, optional): Human readable time frame
  - `priority` (str, optional): Priority level (high, medium, low)
  - `source` (str, optional): Source of the commitment
- `user_id` (str, required): User identifier

**Request Example**:
```json
{
  "commitment": {
    "text": "submit the report",
    "due_date": "2023-04-07T17:00:00Z",
    "time_frame": "by Friday",
    "priority": "medium",
    "source": "email"
  },
  "user_id": "user123"
}
```

**Response**:
- 201 Created: Saved commitment with ID
- 400 Bad Request: Invalid input
- 401 Unauthorized: Authentication required
- 403 Forbidden: Insufficient permissions
- 409 Conflict: Duplicate commitment
- 500 Internal Server Error: Service error

**Response Example**:
```json
{
  "id": "commit_abc123",
  "text": "submit the report",
  "due_date": "2023-04-07T17:00:00Z",
  "time_frame": "by Friday",
  "priority": "medium",
  "source": "email",
  "user_id": "user123",
  "status": "pending",
  "created_at": "2023-04-01T10:00:00Z",
  "updated_at": "2023-04-01T10:00:00Z"
}
```

### `get_user_commitments(user_id: str, status: str = None, from_date: datetime = None, to_date: datetime = None) -> List[Dict]`

Retrieves commitments for a specific user.

**Endpoint**: `GET /api/v1/commitments`

**Query Parameters**:
- `user_id` (str, required): User identifier
- `status` (str, optional): Filter by status (pending, completed, cancelled)
- `from_date` (str, optional): ISO8601 formatted start date
- `to_date` (str, optional): ISO8601 formatted end date
- `priority` (str, optional): Filter by priority (high, medium, low)
- `source` (str, optional): Filter by source
- `page` (int, optional): Page number for pagination (default: 1)
- `page_size` (int, optional): Items per page (default: 20, max: 100)

**Request Example**:
```
GET /api/v1/commitments?user_id=user123&status=pending&from_date=2023-04-01T00:00:00Z&to_date=2023-04-30T23:59:59Z&priority=high
```

**Response**:
- 200 OK: List of commitments matching criteria
- 400 Bad Request: Invalid parameters
- 401 Unauthorized: Authentication required
- 403 Forbidden: Insufficient permissions
- 500 Internal Server Error: Service error

**Response Example**:
```json
{
  "commitments": [
    {
      "id": "commit_abc123",
      "text": "submit the report",
      "due_date": "2023-04-07T17:00:00Z",
      "time_frame": "by Friday",
      "priority": "high",
      "source": "email",
      "user_id": "user123",
      "status": "pending",
      "created_at": "2023-04-01T10:00:00Z",
      "updated_at": "2023-04-01T10:00:00Z"
    },
    {
      "id": "commit_def456",
      "text": "prepare presentation",
      "due_date": "2023-04-15T09:00:00Z",
      "time_frame": "before the meeting",
      "priority": "high",
      "source": "chat",
      "user_id": "user123",
      "status": "pending",
      "created_at": "2023-04-02T14:30:00Z",
      "updated_at": "2023-04-02T14:30:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_items": 2,
    "total_pages": 1
  }
}
```

### `update_commitment_status(commitment_id: str, status: str) -> Dict`

Updates the status of a commitment.

**Endpoint**: `PATCH /api/v1/commitments/{commitment_id}`

**URL Parameters**:
- `commitment_id` (str, required): Commitment identifier

**Request Body**:
- `status` (str, required): New status (pending, completed, cancelled)
- `completion_notes` (str, optional): Notes on completion

**Request Example**:
```json
{
  "status": "completed",
  "completion_notes": "Submitted via email to team@example.com"
}
```

**Response**:
- 200 OK: Updated commitment
- 400 Bad Request: Invalid status
- 401 Unauthorized: Authentication required
- 403 Forbidden: Insufficient permissions
- 404 Not Found: Commitment not found
- 500 Internal Server Error: Service error

**Response Example**:
```json
{
  "id": "commit_abc123",
  "text": "submit the report",
  "due_date": "2023-04-07T17:00:00Z",
  "time_frame": "by Friday",
  "priority": "high",
  "source": "email",
  "user_id": "user123",
  "status": "completed",
  "completion_notes": "Submitted via email to team@example.com",
  "created_at": "2023-04-01T10:00:00Z",
  "updated_at": "2023-04-05T15:30:00Z",
  "completed_at": "2023-04-05T15:30:00Z"
}
```

## DialogueSystemService API

Base URL: `/api/v1/dialogue`

### `create_session(user_id: str) -> Dict`

Creates a new dialogue session.

**Endpoint**: `POST /api/v1/dialogue/sessions`

**Parameters**:
- `user_id` (str, required): User identifier
- `initial_context` (Dict, optional): Initial context for the session
  - `location` (str, optional): Current user location
  - `activity` (str, optional): Current user activity
  - `device` (str, optional): User device type

**Request Example**:
```json
{
  "user_id": "user123",
  "initial_context": {
    "location": "office",
    "device": "mobile"
  }
}
```

**Response**:
- 201 Created: Session created successfully
- 400 Bad Request: Invalid input
- 401 Unauthorized: Authentication required
- 403 Forbidden: Insufficient permissions
- 500 Internal Server Error: Service error

**Response Example**:
```json
{
  "session_id": "sess_abc123",
  "user_id": "user123",
  "context": {
    "location": "office",
    "device": "mobile"
  },
  "created_at": "2023-04-01T10:00:00Z",
  "expires_at": "2023-04-01T10:30:00Z"
}
```

### `process_message(session_id: str, message: str, context: Dict = None) -> Dict`

Processes a user message and generates a response.

**Endpoint**: `POST /api/v1/dialogue/sessions/{session_id}/messages`

**URL Parameters**:
- `session_id` (str, required): Session identifier

**Request Body**:
- `message` (str, required): User message
- `context` (Dict, optional): Additional context for response generation
  - `location` (str, optional): Updated location
  - `activity` (str, optional): Current activity
  - `timestamp` (str, optional): Client timestamp

**Request Example**:
```json
{
  "message": "What do I need to do today?",
  "context": {
    "location": "office",
    "timestamp": "2023-04-01T10:05:00Z"
  }
}
```

**Response**:
- 200 OK: Response generated successfully
- 400 Bad Request: Invalid input
- 401 Unauthorized: Authentication required
- 403 Forbidden: Insufficient permissions
- 404 Not Found: Session not found
- 500 Internal Server Error: Service error

**Response Example**:
```json
{
  "text": "You have 3 commitments due today:\n1. Submit the report (due at 5pm)\n2. Call John about the project (anytime today)\n3. Pick up groceries on your way home\n\nWould you like me to prioritize these for you?",
  "detected_commitments": [],
  "suggestions": [
    {
      "text": "Prioritize my commitments",
      "action": "prioritize_commitments"
    },
    {
      "text": "Mark 'Submit the report' as completed",
      "action": "mark_completed",
      "commitment_id": "commit_abc123"
    },
    {
      "text": "Remind me about the report at 4pm",
      "action": "schedule_reminder",
      "commitment_id": "commit_abc123",
      "time": "16:00:00"
    }
  ],
  "updated_context": {
    "location": "office",
    "timestamp": "2023-04-01T10:05:00Z",
    "last_topic": "today_commitments"
  },
  "message_id": "msg_xyz789"
}
```

### `get_session_status(session_id: str) -> Dict`

Retrieves the current status of a dialogue session.

**Endpoint**: `GET /api/v1/dialogue/sessions/{session_id}`

**URL Parameters**:
- `session_id` (str, required): Session identifier

**Response**:
- 200 OK: Session status
- 401 Unauthorized: Authentication required
- 403 Forbidden: Insufficient permissions
- 404 Not Found: Session not found
- 500 Internal Server Error: Service error

**Response Example**:
```json
{
  "session_id": "sess_abc123",
  "user_id": "user123",
  "context": {
    "location": "office",
    "device": "mobile",
    "last_topic": "today_commitments"
  },
  "message_count": 5,
  "created_at": "2023-04-01T10:00:00Z",
  "updated_at": "2023-04-01T10:05:30Z",
  "expires_at": "2023-04-01T10:35:30Z",
  "active": true
}
```

### `end_session(session_id: str) -> bool`

Ends an active dialogue session.

**Endpoint**: `DELETE /api/v1/dialogue/sessions/{session_id}`

**URL Parameters**:
- `session_id` (str, required): Session identifier

**Response**:
- 204 No Content: Session ended successfully
- 401 Unauthorized: Authentication required
- 403 Forbidden: Insufficient permissions
- 404 Not Found: Session not found
- 500 Internal Server Error: Service error

## SmartReminderService API

Base URL: `/api/v1/reminders`

### `get_contextual_reminders(user_id: str, context: Dict) -> List[Dict]`

Gets context-relevant reminders for a user.

**Endpoint**: `GET /api/v1/reminders/contextual`

**Query Parameters**:
- `user_id` (str, required): User identifier

**Request Body**:
- `context` (Dict, required): Current context
  - `location` (str, optional): User's current location
  - `time` (str, optional): ISO8601 formatted current time
  - `activity` (str, optional): Current activity
  - `device` (str, optional): Device in use
  - `focus_mode` (bool, optional): Whether user is in focus mode

**Request Example**:
```json
{
  "context": {
    "location": "office",
    "time": "2023-04-01T09:00:00Z",
    "activity": "working",
    "device": "desktop",
    "focus_mode": false
  }
}
```

**Response**:
- 200 OK: List of relevant reminders
- 400 Bad Request: Invalid context
- 401 Unauthorized: Authentication required
- 403 Forbidden: Insufficient permissions
- 500 Internal Server Error: Service error

**Response Example**:
```json
{
  "reminders": [
    {
      "id": "rem_abc123",
      "commitment_id": "commit_abc123",
      "text": "Submit the quarterly report",
      "priority": "high",
      "relevance_score": 0.95,
      "due_date": "2023-04-01T17:00:00Z",
      "suggested_action": "Open report document",
      "action_data": {
        "document_id": "doc_xyz789",
        "application": "document_editor"
      }
    },
    {
      "id": "rem_def456",
      "commitment_id": "commit_def456",
      "text": "Call John about the project",
      "priority": "medium",
      "relevance_score": 0.75,
      "due_date": "2023-04-01T23:59:59Z",
      "suggested_action": "Place call",
      "action_data": {
        "contact_id": "contact_john",
        "phone": "+1234567890"
      }
    }
  ],
  "metadata": {
    "total_available": 8,
    "filtered_by_context": true,
    "next_batch_after": "2023-04-01T12:00:00Z"
  }
}
```

### `send_commitment_reminder(user_id: str, commitment_id: str, context: Dict = None) -> Dict`

Sends a reminder for a specific commitment.

**Endpoint**: `POST /api/v1/reminders`

**Parameters**:
- `user_id` (str, required): User identifier
- `commitment_id` (str, required): Commitment to remind about
- `context` (Dict, optional): Current context for personalization
  - `location` (str, optional): User's current location
  - `activity` (str, optional): Current activity
  - `importance_override` (str, optional): Override default importance
  - `delivery_channel` (str, optional): Preferred delivery channel

**Request Example**:
```json
{
  "user_id": "user123",
  "commitment_id": "commit_abc123",
  "context": {
    "location": "office",
    "importance_override": "urgent",
    "delivery_channel": "push_notification"
  }
}
```

**Response**:
- 200 OK: Reminder sent successfully
- 400 Bad Request: Invalid input
- 401 Unauthorized: Authentication required
- 403 Forbidden: Insufficient permissions
- 404 Not Found: Commitment not found
- 429 Too Many Requests: Rate limit exceeded
- 500 Internal Server Error: Service error

**Response Example**:
```json
{
  "reminder_id": "rem_abc123",
  "commitment_id": "commit_abc123",
  "status": "delivered",
  "delivery_channel": "push_notification",
  "delivered_at": "2023-04-01T10:15:30Z",
  "notification_id": "notif_xyz789"
}
```

### `update_reminder_status(reminder_id: str, status: str) -> Dict`

Updates the status of a reminder.

**Endpoint**: `PATCH /api/v1/reminders/{reminder_id}`

**URL Parameters**:
- `reminder_id` (str, required): Reminder identifier

**Request Body**:
- `status` (str, required): New status (delivered, dismissed, acted_upon)
- `action_taken` (str, optional): Description of action taken
- `user_feedback` (Dict, optional): User feedback on reminder
  - `relevance` (int, optional): Relevance rating (1-5)
  - `timing` (int, optional): Timing rating (1-5)
  - `comment` (str, optional): User comment

**Request Example**:
```json
{
  "status": "acted_upon",
  "action_taken": "Opened document",
  "user_feedback": {
    "relevance": 5,
    "timing": 4
  }
}
```

**Response**:
- 200 OK: Status updated successfully
- 400 Bad Request: Invalid status
- 401 Unauthorized: Authentication required
- 403 Forbidden: Insufficient permissions
- 404 Not Found: Reminder not found
- 500 Internal Server Error: Service error

**Response Example**:
```json
{
  "id": "rem_abc123",
  "commitment_id": "commit_abc123",
  "status": "acted_upon",
  "action_taken": "Opened document",
  "updated_at": "2023-04-01T10:20:00Z",
  "user_feedback": {
    "relevance": 5,
    "timing": 4
  }
}
```

### `process_smart_reminders(user_id: str) -> Dict`

Processes all pending reminders for a user, prioritizing and delivering as appropriate.

**Endpoint**: `POST /api/v1/reminders/process`

**Parameters**:
- `user_id` (str, required): User identifier
- `context` (Dict, optional): Current user context for better processing
- `delivery_options` (Dict, optional): Delivery preferences
  - `max_notifications` (int, optional): Maximum notifications to send
  - `minimum_priority` (str, optional): Minimum priority to deliver
  - `delivery_channels` (List[str], optional): Preferred channels

**Request Example**:
```json
{
  "user_id": "user123",
  "context": {
    "location": "office",
    "activity": "meeting",
    "focus_mode": true
  },
  "delivery_options": {
    "max_notifications": 2,
    "minimum_priority": "high",
    "delivery_channels": ["in_app", "email"]
  }
}
```

**Response**:
- 200 OK: Processing completed successfully
- 400 Bad Request: Invalid parameters
- 401 Unauthorized: Authentication required
- 403 Forbidden: Insufficient permissions
- 500 Internal Server Error: Service error

**Response Example**:
```json
{
  "processing_summary": {
    "reminders_processed": 12,
    "reminders_sent": 2,
    "reminders_deferred": 8,
    "reminders_merged": 2
  },
  "sent_reminders": [
    {
      "id": "rem_abc123",
      "commitment_id": "commit_abc123",
      "delivery_channel": "in_app",
      "priority": "high"
    },
    {
      "id": "rem_def456",
      "commitment_id": "commit_def456",
      "delivery_channel": "email",
      "priority": "high"
    }
  ],
  "next_processing_recommended_at": "2023-04-01T11:00:00Z"
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
      "field": "due_date",
      "issue": "must be a valid ISO8601 date"
    },
    "request_id": "req_abc123",
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

### Error Handling Best Practices

1. Always check HTTP status codes first
2. Use error codes for programmatic handling
3. Display friendly messages to end users
4. Include request_id in support inquiries
5. Implement exponential backoff for 429 and 503 responses

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
- Role-based permissions:
  - `read:commitments`: View commitments
  - `write:commitments`: Create/edit commitments
  - `read:reminders`: View reminders
  - `write:reminders`: Create/manage reminders
  - `admin:*`: Administrative access

### User Identity

- `user_id` must match the authenticated user or have admin permissions
- Sub-resources inherit parent resource permissions
- Shared resources have explicit access control lists

## Rate Limiting

The APIs implement rate limiting to ensure system stability and prevent abuse.

### Default Rate Limits

| API | Rate Limit | Window | Burst |
|-----|------------|--------|-------|
| CommitmentDetectionService | 60 requests | 1 minute | 10 |
| DialogueSystemService | 100 messages | 1 minute | 20 |
| SmartReminderService | 30 requests | 1 minute | 5 |

### Rate Limit Headers

All responses include rate limit headers:
- `X-RateLimit-Limit`: Maximum requests allowed in time window
- `X-RateLimit-Remaining`: Requests remaining in current window
- `X-RateLimit-Reset`: Unix timestamp when limit resets

### Handling Rate Limits

When a rate limit is exceeded (429 response):
1. Check the `Retry-After` header for wait time in seconds
2. Implement exponential backoff with jitter
3. Consider batching requests when possible

### Rate Limit Extensions

For increased limits, contact support@adhdcalendar.com:
- Enterprise tier: 10x default limits
- Service accounts: Custom limits available

## API Versioning

The APIs follow semantic versioning and maintain backward compatibility within major versions.

### Version Specification

- Version in URL path: `/api/v1/commitments`
- Current version: v1
- Version header option: `X-API-Version: v1`

### Version Lifecycle

- Breaking changes trigger major version increments (v1 → v2)
- Non-breaking additions increment minor version (v1.0 → v1.1)
- Bug fixes increment patch version (v1.0.0 → v1.0.1)
- Version deprecation process:
  1. Announcement 6 months before deprecation
  2. 3-month warning period with upgrade documentation
  3. 3-month grace period with reduced performance
  4. Version decommissioning

### Version Migration

- Migration guides provided for major version upgrades
- Temporary dual-version support during transitions
- Migration assistance available for enterprise customers

## SDKs and Client Libraries

Official client libraries are available for common programming languages:

### Official SDKs

- **Python**: `pip install adhdcalendar-client`
- **JavaScript**: `npm install adhdcalendar-client`
- **Java**: Available via Maven
- **Swift/iOS**: Available via CocoaPods
- **Kotlin/Android**: Available via Gradle

### SDK Features

- Automatic authentication handling
- Request/response serialization
- Error handling and retries
- Rate limit awareness
- Typed interfaces for all APIs

### Usage Example (Python)

```python
from adhdcalendar import ADHDCalendarClient

# Initialize client
client = ADHDCalendarClient(api_key="your_api_key")

# Detect commitments
commitments = client.commitments.detect(
    text="I need to submit the report by Friday.",
    context={"source": "email"}
)

# Process dialogue
response = client.dialogue.process_message(
    session_id="sess_abc123",
    message="What do I need to do today?"
)

# Get contextual reminders
reminders = client.reminders.get_contextual(
    context={"location": "office", "activity": "working"}
)
```
