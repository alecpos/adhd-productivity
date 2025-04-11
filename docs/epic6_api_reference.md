# ADHD Calendar: Epic 6 API Reference

**Version**: 1.0
**Last Updated**: 2025-03-15
**Target Audience**: Developers integrating with UX components

## Overview

This document provides detailed API specifications for the User Experience and Interface Optimization components created in Epic 6. These APIs enable developers to integrate adaptive gamification, project management tools, accessibility features, and calendar systems into the ADHD Calendar platform.

## Table of Contents

1. [Adaptive Gamification API](#adaptive-gamification-api)
2. [Project Management Integration API](#project-management-integration-api)
3. [Accessibility API](#accessibility-api)
4. [Calendar Integration API](#calendar-integration-api)
5. [Common Data Types](#common-data-types)
6. [Error Handling](#error-handling)
7. [Rate Limits](#rate-limits)

## Adaptive Gamification API

The Adaptive Gamification API provides methods for personalizing motivation mechanisms based on user preferences and behavior patterns.

### User Motivation Profile

#### `GET /api/gamification/profile`

Retrieves the current user's motivation profile.

**Parameters**:
- None (uses authenticated user context)

**Returns**:
- `UserMotivationProfile` object

**Example Response**:
```json
{
  "user_id": "u123456",
  "primary_motivators": ["achievement", "mastery"],
  "secondary_motivators": ["social", "autonomy"],
  "effective_mechanics": ["badges", "progress_bars", "streaks"],
  "reward_preferences": ["progressive", "milestone"],
  "engagement_patterns": {
    "morning_responsiveness": 0.85,
    "afternoon_responsiveness": 0.62,
    "evening_responsiveness": 0.74,
    "challenges_completed_rate": 0.68,
    "badge_engagement_score": 0.92
  },
  "last_updated": "2025-03-15T14:30:15Z"
}
```

#### `PATCH /api/gamification/profile`

Updates specific fields in the user's motivation profile.

**Request Body**:
- Partial `UserMotivationProfile` object with fields to update

**Returns**:
- Updated `UserMotivationProfile` object

**Example Request**:
```json
{
  "primary_motivators": ["achievement", "creativity"],
  "reward_preferences": ["variable", "milestone"]
}
```

### Gamification Mechanics

#### `GET /api/gamification/mechanics`

Retrieves optimal gamification mechanics for the current context.

**Query Parameters**:
- `limit`: Number of mechanics to retrieve (default: 3, max: 10)
- `task_type`: Optional task type to contextualize recommendations
- `difficulty`: Optional task difficulty level (0.0-1.0)
- `importance`: Optional task importance level (0.0-1.0)
- `energy_level`: Optional user energy level (0.0-1.0)
- `current_hour`: Optional hour of day (0-23)

**Returns**:
- Array of `GamificationMechanic` enumeration values

**Example Response**:
```json
[
  "streaks",
  "badges",
  "progress_bars"
]
```

### Gamification Actions

#### `POST /api/gamification/actions`

Recommends gamification actions based on user profile and context.

**Request Body**:
```json
{
  "context": {
    "task_type": "focus",
    "difficulty": 0.7,
    "importance": 0.8,
    "energy_level": 0.6
  },
  "count": 2
}
```

**Returns**:
- Array of recommended gamification action objects

**Example Response**:
```json
[
  {
    "name": "streak_milestone",
    "description": "You're on a 5-day streak! Keep going to reach your weekly goal.",
    "mechanic": "streaks",
    "reward_strategy": "milestone",
    "target_motivator": "achievement",
    "difficulty": 0.6,
    "engagement_score": 0.85
  },
  {
    "name": "level_progress",
    "description": "You're making great progress! Just 2 more tasks to level up.",
    "mechanic": "levels",
    "reward_strategy": "progressive",
    "target_motivator": "mastery",
    "difficulty": 0.5,
    "engagement_score": 0.75
  }
]
```

#### `POST /api/gamification/effectiveness/{action_id}`

Records user engagement with a specific gamification action.

**Path Parameters**:
- `action_id`: ID of the gamification action

**Request Body**:
```json
{
  "engagement_metrics": {
    "engagement_score": 0.85,
    "interaction_type": "clicked",
    "task_completed": true,
    "time_spent": 120
  }
}
```

**Returns**:
- Success confirmation and updated effectiveness data

## Project Management Integration API

The Project Management Integration API provides methods for connecting and synchronizing with external project management tools.

### Tool Configuration

#### `GET /api/project-tools`

Retrieves the list of connected project management tools.

**Parameters**:
- None (uses authenticated user context)

**Returns**:
- Array of `ProjectToolConfig` objects

**Example Response**:
```json
[
  {
    "tool_id": "jira-workspace-1",
    "name": "Work Jira",
    "api_url": "https://company.atlassian.net",
    "username": "user@company.com",
    "default_project": "ADHD",
    "sync_frequency": 30,
    "two_way_sync": true,
    "last_sync": "2025-03-15T12:30:00Z",
    "status": "active"
  },
  {
    "tool_id": "trello-personal",
    "name": "Personal Trello",
    "api_url": "https://api.trello.com/1",
    "default_project": "Personal Projects",
    "sync_frequency": 60,
    "two_way_sync": true,
    "last_sync": "2025-03-15T12:15:00Z",
    "status": "active"
  }
]
```

#### `POST /api/project-tools/register`

Registers a new project management tool connection.

**Request Body**:
```json
{
  "platform": "jira",
  "name": "Work Jira",
  "api_url": "https://company.atlassian.net",
  "auth_method": "oauth2",
  "default_project": "ADHD",
  "sync_frequency": 30,
  "two_way_sync": true
}
```

**Returns**:
- `ProjectToolConfig` object with auth URL for OAuth flow

#### `DELETE /api/project-tools/{tool_id}`

Disconnects and removes a project management tool.

**Path Parameters**:
- `tool_id`: ID of the tool to remove

**Returns**:
- Success confirmation

### Task Synchronization

#### `POST /api/project-tools/sync`

Manually triggers synchronization with all connected tools.

**Parameters**:
- `full_sync` (query): Boolean to force a full sync (default: false)

**Returns**:
- Sync status object with counts of added/updated/removed tasks

**Example Response**:
```json
{
  "sync_id": "sync123456",
  "start_time": "2025-03-15T15:30:00Z",
  "end_time": "2025-03-15T15:30:45Z",
  "status": "completed",
  "tools_synced": 2,
  "tools_failed": 0,
  "tasks_added": 5,
  "tasks_updated": 12,
  "tasks_removed": 2,
  "conflicts": 1,
  "conflict_resolution": "automatic",
  "details": [
    {
      "tool_id": "jira-workspace-1",
      "tasks_added": 3,
      "tasks_updated": 8,
      "tasks_removed": 1
    },
    {
      "tool_id": "trello-personal",
      "tasks_added": 2,
      "tasks_updated": 4,
      "tasks_removed": 1
    }
  ]
}
```

#### `GET /api/project-tools/{tool_id}/projects`

Retrieves available projects from the external project management tool.

**Path Parameters**:
- `tool_id`: ID of the tool

**Returns**:
- Array of project objects

**Example Response**:
```json
[
  {
    "id": "ADHD",
    "name": "ADHD Calendar Application",
    "description": "Development of the ADHD Calendar Application",
    "url": "https://company.atlassian.net/browse/ADHD"
  },
  {
    "id": "MOBILE",
    "name": "Mobile Applications",
    "description": "Mobile application development",
    "url": "https://company.atlassian.net/browse/MOBILE"
  }
]
```

#### `GET /api/project-tools/{tool_id}/tasks`

Retrieves tasks from the external project management tool.

**Path Parameters**:
- `tool_id`: ID of the tool

**Query Parameters**:
- `project` (optional): Project ID to filter by
- `status` (optional): Status to filter by
- `since` (optional): Timestamp to get only tasks updated since

**Returns**:
- Array of `ExternalTask` objects

**Example Response**:
```json
[
  {
    "external_id": "ADHD-123",
    "title": "Implement gamification API",
    "description": "Create endpoints for the adaptive gamification system",
    "status": "in_progress",
    "priority": "high",
    "due_date": "2025-03-20T23:59:59Z",
    "assigned_to": "user@company.com",
    "project": "ADHD",
    "url": "https://company.atlassian.net/browse/ADHD-123",
    "labels": ["backend", "api", "epic6"],
    "last_updated": "2025-03-14T09:15:30Z"
  },
  {
    "external_id": "ADHD-124",
    "title": "Design gamification UI components",
    "description": "Create UI components for displaying badges and rewards",
    "status": "to_do",
    "priority": "medium",
    "due_date": "2025-03-22T23:59:59Z",
    "assigned_to": "designer@company.com",
    "project": "ADHD",
    "url": "https://company.atlassian.net/browse/ADHD-124",
    "labels": ["frontend", "ui", "epic6"],
    "last_updated": "2025-03-13T16:42:12Z"
  }
]
```

#### `POST /api/project-tools/{tool_id}/tasks`

Creates a new task in the external project management tool.

**Path Parameters**:
- `tool_id`: ID of the tool

**Request Body**:
```json
{
  "title": "Implement streak tracking",
  "description": "Create a system to track and display user task streaks",
  "status": "to_do",
  "priority": "medium",
  "due_date": "2025-03-25T23:59:59Z",
  "project": "ADHD",
  "labels": ["backend", "gamification"]
}
```

**Returns**:
- Created `ExternalTask` object with external_id

#### `PUT /api/project-tools/{tool_id}/tasks/{task_id}`

Updates an existing task in the external project management tool.

**Path Parameters**:
- `tool_id`: ID of the tool
- `task_id`: External ID of the task

**Request Body**:
```json
{
  "status": "in_progress",
  "priority": "high",
  "due_date": "2025-03-23T23:59:59Z"
}
```

**Returns**:
- Updated `ExternalTask` object

## Accessibility API

The Accessibility API provides methods for customizing the user interface for neurodivergent users.

### User Preferences

#### `GET /api/accessibility/preferences`

Retrieves the current user's accessibility preferences.

**Parameters**:
- None (uses authenticated user context)

**Returns**:
- `AccessibilityPreferences` object

**Example Response**:
```json
{
  "user_id": "u123456",
  "color_mode": "reduced-blue",
  "text_size": 1.2,
  "reduce_motion": true,
  "reduce_transparency": true,
  "reduce_distractions": true,
  "highlight_focus": true,
  "reading_guide": false,
  "custom_fonts": true,
  "font_family": "OpenDyslexic",
  "spacing_scale": 1.15,
  "use_audio_cues": false,
  "use_visual_cues": true,
  "last_updated": "2025-03-14T10:15:00Z"
}
```

#### `PATCH /api/accessibility/preferences`

Updates specific accessibility preferences.

**Request Body**:
- Partial `AccessibilityPreferences` object with fields to update

**Returns**:
- Updated `AccessibilityPreferences` object

**Example Request**:
```json
{
  "color_mode": "high-contrast",
  "reduce_distractions": true,
  "font_family": "OpenDyslexic"
}
```

### UI Adaptation

#### `GET /api/accessibility/theme.css`

Generates a CSS stylesheet based on the user's accessibility preferences.

**Query Parameters**:
- `context` (optional): Application context ('calendar', 'tasks', 'focus')

**Returns**:
- CSS stylesheet as text/css

**Example Response**:
```css
:root {
  --adhd-primary-color: #0056b3;
  --adhd-secondary-color: #6c757d;
  --adhd-text-color: #333333;
  --adhd-background-color: #f8f9fa;
  --adhd-focus-color: #ffcc00;
  --adhd-font-size-base: 18px;
  --adhd-line-height: 1.6;
  --adhd-spacing-scale: 1.15;
  --adhd-animation-speed: 0;
  --adhd-border-radius: 8px;
}

body {
  font-family: 'OpenDyslexic', sans-serif;
  font-size: var(--adhd-font-size-base);
  line-height: var(--adhd-line-height);
  color: var(--adhd-text-color);
  background-color: var(--adhd-background-color);
}

/* Additional CSS rules for high contrast and reduced distractions */
```

#### `GET /api/accessibility/wcag-report`

Analyzes the current accessibility settings for WCAG compliance.

**Parameters**:
- None (uses authenticated user context)

**Returns**:
- Compliance report with suggestions for improvements

**Example Response**:
```json
{
  "overall_compliance": "AA",
  "color_contrast": {
    "status": "pass",
    "ratio": 7.2,
    "minimum_required": 4.5
  },
  "text_size": {
    "status": "pass",
    "current": "18px"
  },
  "keyboard_navigation": {
    "status": "pass"
  },
  "screen_reader_compatibility": {
    "status": "warning",
    "issues": ["Some charts missing alt text"]
  },
  "suggestions": [
    "Add alt text to all visualizations",
    "Ensure all interactive elements have accessible names"
  ]
}
```

#### `GET /api/accessibility/focus-assist-styles`

Generates a CSS stylesheet specifically for focus assistance.

**Query Parameters**:
- `energy_level` (optional): Current energy level (0.0-1.0)
- `time_of_day` (optional): Current hour (0-23)

**Returns**:
- CSS stylesheet as text/css focused on attention management

#### `GET /api/accessibility/adhd-optimized-settings`

Provides recommended accessibility settings for ADHD users.

**Query Parameters**:
- `adhd_type`: ADHD subtype ('inattentive', 'hyperactive', 'combined')
- `energy_level`: Current energy level (0.0-1.0)
- `context`: Application context ('work', 'study', 'leisure')

**Returns**:
- `AccessibilityPreferences` object with recommended settings

## Calendar Integration API

The Calendar Integration API provides methods for connecting and synchronizing with external calendar systems.

### Calendar Configuration

#### `GET /api/calendars`

Retrieves the list of connected calendars.

**Parameters**:
- None (uses authenticated user context)

**Returns**:
- Array of `CalendarIntegrationConfig` objects

**Example Response**:
```json
[
  {
    "calendar_id": "google-work",
    "platform": "google",
    "name": "Work Calendar",
    "sync_frequency": 15,
    "two_way_sync": true,
    "default_reminders": [10, 30],
    "include_details": true,
    "color_coding": true,
    "last_sync": "2025-03-15T14:30:00Z",
    "status": "active"
  },
  {
    "calendar_id": "apple-personal",
    "platform": "apple",
    "name": "Personal Calendar",
    "sync_frequency": 30,
    "two_way_sync": true,
    "default_reminders": [15, 60],
    "include_details": true,
    "color_coding": true,
    "last_sync": "2025-03-15T14:15:00Z",
    "status": "active"
  }
]
```

#### `POST /api/calendars/register`

Registers a new calendar connection.

**Request Body**:
```json
{
  "platform": "google",
  "name": "Work Calendar",
  "sync_frequency": 15,
  "two_way_sync": true,
  "default_reminders": [10, 30],
  "include_details": true,
  "color_coding": true
}
```

**Returns**:
- `CalendarIntegrationConfig` object with auth URL for OAuth flow

#### `DELETE /api/calendars/{calendar_id}`

Disconnects and removes a calendar.

**Path Parameters**:
- `calendar_id`: ID of the calendar to remove

**Returns**:
- Success confirmation

### Calendar Event Management

#### `POST /api/calendars/{calendar_id}/sync`

Manually triggers synchronization with the specified calendar.

**Path Parameters**:
- `calendar_id`: ID of the calendar to synchronize

**Query Parameters**:
- `full_sync` (optional): Boolean to force a full sync (default: false)
- `start_date` (optional): Start date for sync range
- `end_date` (optional): End date for sync range

**Returns**:
- Sync status object with counts of added/updated/removed events

**Example Response**:
```json
{
  "sync_id": "sync789012",
  "start_time": "2025-03-15T15:45:00Z",
  "end_time": "2025-03-15T15:45:30Z",
  "status": "completed",
  "events_added": 3,
  "events_updated": 7,
  "events_removed": 1,
  "conflicts": 0,
  "next_scheduled_sync": "2025-03-15T16:00:00Z"
}
```

#### `GET /api/calendars/{calendar_id}/available`

Retrieves the list of available calendars from the external platform.

**Path Parameters**:
- `calendar_id`: ID of the calendar connection

**Returns**:
- Array of available calendar objects from the external platform

**Example Response**:
```json
[
  {
    "id": "primary",
    "name": "Primary Calendar",
    "description": "Main calendar",
    "color": "#4285F4",
    "access_role": "owner"
  },
  {
    "id": "work_calendar@group.calendar.google.com",
    "name": "Work Calendar",
    "description": "Company-wide work calendar",
    "color": "#0B8043",
    "access_role": "reader"
  }
]
```

#### `GET /api/calendars/{calendar_id}/events`

Retrieves events from the external calendar.

**Path Parameters**:
- `calendar_id`: ID of the calendar

**Query Parameters**:
- `start_date` (required): Start date to filter by
- `end_date` (required): End date to filter by

**Returns**:
- Array of `ExternalEvent` objects

**Example Response**:
```json
[
  {
    "external_id": "event123456",
    "title": "Team Stand-up",
    "description": "Daily team stand-up meeting",
    "start_time": "2025-03-16T10:00:00Z",
    "end_time": "2025-03-16T10:15:00Z",
    "location": "Zoom Meeting",
    "is_all_day": false,
    "reminders": [10],
    "attendees": [
      {"email": "user@company.com", "name": "User Name", "status": "accepted"},
      {"email": "colleague@company.com", "name": "Colleague Name", "status": "accepted"}
    ],
    "recurrence": "RRULE:FREQ=DAILY;BYDAY=MO,TU,WE,TH,FR",
    "status": "confirmed",
    "url": "https://zoom.us/meeting/123456",
    "color": "#4285F4",
    "calendar_id": "google-work",
    "last_updated": "2025-03-10T09:00:00Z"
  },
  {
    "external_id": "event123457",
    "title": "Project Review",
    "description": "Review progress on ADHD Calendar project",
    "start_time": "2025-03-16T14:00:00Z",
    "end_time": "2025-03-16T15:00:00Z",
    "location": "Conference Room A",
    "is_all_day": false,
    "reminders": [10, 30],
    "attendees": [
      {"email": "user@company.com", "name": "User Name", "status": "accepted"},
      {"email": "manager@company.com", "name": "Manager Name", "status": "accepted"},
      {"email": "stakeholder@company.com", "name": "Stakeholder Name", "status": "tentative"}
    ],
    "recurrence": null,
    "status": "confirmed",
    "url": null,
    "color": "#0B8043",
    "calendar_id": "google-work",
    "last_updated": "2025-03-14T13:30:00Z"
  }
]
```

#### `POST /api/calendars/{calendar_id}/events`

Creates a new event in the external calendar.

**Path Parameters**:
- `calendar_id`: ID of the calendar

**Request Body**:
```json
{
  "title": "Focus Block",
  "description": "Uninterrupted time for deep work",
  "start_time": "2025-03-17T09:00:00Z",
  "end_time": "2025-03-17T11:00:00Z",
  "is_all_day": false,
  "location": "Office",
  "reminders": [10, 30],
  "attendees": [],
  "status": "confirmed",
  "color": "#A142F4"
}
```

**Returns**:
- Created `ExternalEvent` object with external_id

#### `PUT /api/calendars/{calendar_id}/events/{event_id}`

Updates an existing event in the external calendar.

**Path Parameters**:
- `calendar_id`: ID of the calendar
- `event_id`: External ID of the event

**Request Body**:
```json
{
  "title": "Extended Focus Block",
  "start_time": "2025-03-17T09:00:00Z",
  "end_time": "2025-03-17T12:00:00Z",
  "reminders": [15, 45]
}
```

**Returns**:
- Updated `ExternalEvent` object

#### `DELETE /api/calendars/{calendar_id}/events/{event_id}`

Deletes an event from the external calendar.

**Path Parameters**:
- `calendar_id`: ID of the calendar
- `event_id`: External ID of the event

**Returns**:
- Success confirmation

## Common Data Types

### `UserMotivationProfile`

Object representing a user's gamification preferences and patterns.

**Properties**:
- `user_id`: String identifier for the user
- `primary_motivators`: Array of MotivatorType strings
- `secondary_motivators`: Array of MotivatorType strings
- `effective_mechanics`: Array of GamificationMechanic strings
- `reward_preferences`: Array of RewardStrategy strings
- `engagement_patterns`: Dictionary mapping pattern names to float values
- `last_updated`: Timestamp of last profile update

### `GamificationAction`

Object representing a specific gamification action to present to the user.

**Properties**:
- `name`: String name of the action
- `description`: String description of the action
- `mechanic`: GamificationMechanic string
- `reward_strategy`: RewardStrategy string
- `target_motivator`: MotivatorType string
- `difficulty`: Float difficulty level (0.0-1.0)
- `engagement_score`: Float historical engagement score (0.0-1.0)

### `MotivatorType`

Enumeration of motivator types:
- `achievement`: Motivated by accomplishing goals and challenges
- `social`: Motivated by social connection and interaction
- `immersion`: Motivated by deep engagement and flow states
- `creativity`: Motivated by creative expression and innovation
- `mastery`: Motivated by skill improvement and expertise
- `autonomy`: Motivated by independence and self-direction
- `purpose`: Motivated by meaningful impact and contribution

### `RewardStrategy`

Enumeration of reward strategies:
- `fixed`: Consistent, predictable rewards
- `variable`: Randomized or unpredictable rewards
- `progressive`: Increasing rewards for continued engagement
- `competitive`: Rewards based on comparison with others
- `cooperative`: Rewards based on group achievement
- `milestone`: Rewards at specific achievement milestones

### `GamificationMechanic`

Enumeration of gamification mechanics:
- `points`: Numerical points for accomplishments
- `badges`: Visual representations of achievements
- `levels`: Progressive stages of accomplishment
- `challenges`: Specific goals to accomplish
- `leaderboards`: Competitive rankings
- `progress_bars`: Visual progress indicators
- `rewards`: Tangible or virtual rewards
- `streaks`: Consecutive completion tracking
- `social_recognition`: Public acknowledgment of achievements
- `storytelling`: Narrative-based gamification

### `ProjectToolConfig`

Object representing a connection to an external project management tool.

**Properties**:
- `tool_id`: String identifier for the tool connection
- `name`: String name for the connection
- `api_url`: String URL of the API endpoint
- `username`: Optional string username
- `api_key`: Optional string API key (masked)
- `oauth_token`: Optional string OAuth token (masked)
- `default_project`: Optional string project identifier
- `sync_frequency`: Integer minutes between syncs
- `two_way_sync`: Boolean indicating if changes sync both ways
- `last_sync`: Timestamp of last synchronization
- `status`: String status of the connection

### `ExternalTask`

Object representing a task from an external project management tool.

**Properties**:
- `external_id`: String identifier in the external system
- `title`: String title of the task
- `description`: Optional string description
- `status`: String status
- `priority`: Optional string priority
- `due_date`: Optional timestamp
- `assigned_to`: Optional string assignee
- `project`: Optional string project identifier
- `url`: Optional string URL to view in external system
- `labels`: Array of string labels
- `last_updated`: Optional timestamp of last update

### `AccessibilityPreferences`

Object representing a user's accessibility settings.

**Properties**:
- `user_id`: String identifier for the user
- `color_mode`: String indicating color scheme
- `text_size`: Float scale factor for text
- `reduce_motion`: Boolean to minimize animations
- `reduce_transparency`: Boolean to minimize transparency effects
- `reduce_distractions`: Boolean to minimize distracting elements
- `highlight_focus`: Boolean to highlight focused elements
- `reading_guide`: Boolean to enable reading guide
- `custom_fonts`: Boolean to enable custom fonts
- `font_family`: Optional string font family
- `spacing_scale`: Float scale factor for spacing
- `use_audio_cues`: Boolean to enable audio cues
- `use_visual_cues`: Boolean to enable visual cues
- `last_updated`: Timestamp of last update

### `CalendarIntegrationConfig`

Object representing a connection to an external calendar system.

**Properties**:
- `calendar_id`: String identifier for the calendar connection
- `platform`: String indicating the calendar platform
- `name`: String name for the connection
- `user_id`: String identifier for the user
- `access_token`: Optional string access token (masked)
- `refresh_token`: Optional string refresh token (masked)
- `token_expiry`: Optional timestamp when token expires
- `sync_frequency`: Integer minutes between syncs
- `two_way_sync`: Boolean indicating if changes sync both ways
- `default_reminders`: Array of integer minutes before event
- `include_details`: Boolean to include event details
- `color_coding`: Boolean to enable color coding
- `last_sync`: Timestamp of last synchronization
- `status`: String status of the connection

### `ExternalEvent`

Object representing an event from an external calendar.

**Properties**:
- `external_id`: String identifier in the external system
- `title`: String title of the event
- `description`: Optional string description
- `start_time`: Timestamp of event start
- `end_time`: Timestamp of event end
- `location`: Optional string location
- `is_all_day`: Boolean indicating all-day event
- `reminders`: Array of integer minutes before event
- `attendees`: Array of attendee objects
- `recurrence`: Optional string recurrence rule
- `status`: String status of the event
- `url`: Optional string URL
- `color`: Optional string color
- `calendar_id`: String identifier of the calendar
- `last_updated`: Optional timestamp of last update

## Error Handling

All API endpoints use consistent error handling with the following response structure:

```json
{
  "error": {
    "code": "tool_connection_failed",
    "message": "Failed to connect to external tool",
    "details": "Connection timed out after 30 seconds",
    "target": "jira-workspace-1",
    "status": 503
  }
}
```

Common error codes include:

- `invalid_request`: The request was malformed or had invalid parameters
- `authentication_failed`: Authentication with external service failed
- `authorization_failed`: User lacks permissions for the requested operation
- `resource_not_found`: The requested resource doesn't exist
- `sync_conflict`: Changes conflict with external system
- `rate_limit_exceeded`: API rate limit has been exceeded
- `service_unavailable`: External service is temporarily unavailable

## Rate Limits

- **Gamification APIs**: 120 requests per minute
- **Project Management APIs**: 60 requests per minute
- **Accessibility APIs**: 120 requests per minute
- **Calendar APIs**: 60 requests per minute

For higher limits, please contact the platform team.
