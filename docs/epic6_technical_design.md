# Epic 6: User Experience and Interface Optimization - Technical Design

## Overview

This document details the technical design of Epic 6, which focuses on enhancing the user experience and interface optimization for neurodiverse users, particularly those with ADHD. The epic encompasses four major components: adaptive gamification, project management tool integration, neurodiverse-optimized UI, and calendar integration.

## System Architecture

### High-Level Architecture

Epic 6 builds on the existing ADHD Calendar architecture with a focus on the presentation and integration layers:

```
┌─────────────────────────────────────────────────────────────────────┐
│                       Frontend Application                           │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────────────┐
│                        API Gateway Layer                             │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────────────┐
│                        Core Application                              │
├─────────────────┬─────────────┬─────────────────┬───────────────────┤
│   Gamification  │  Project    │  Accessibility  │     Calendar      │
│     Engine      │  Management │    Services     │   Integration     │
├─────────────────┴─────────────┴─────────────────┴───────────────────┤
│                        Integration Layer                             │
├─────────────────┬─────────────┬─────────────────┬───────────────────┤
│   Jira, Trello  │   Google    │    Apple        │     Outlook       │
│     Asana       │  Calendar   │   Calendar      │     Calendar      │
└─────────────────┴─────────────┴─────────────────┴───────────────────┘
```

### Component Relationships

The four main components interconnect as follows:

1. The **Adaptive Gamification Engine** integrates with user data from ML models to personalize motivation strategies
2. The **Project Management Integration** connects with task management systems and external PM tools
3. The **Neurodiverse UI Optimization** provides configuration for all UI elements across the application
4. The **Calendar Integration** system connects with the core calendar functionality and external calendar services

## Detailed Component Design

### 1. Adaptive Gamification Engine

#### Class Diagram

```
┌───────────────────────┐       ┌─────────────────────────┐
│ AdaptiveGamification  │◄──────┤   UserMotivationProfile │
│       Engine          │       └─────────────────────────┘
└───────────┬───────────┘                  ▲
            │                              │
            ▼                              │
┌───────────────────────┐       ┌─────────────────────────┐
│  GamificationAction   │─ ─ ─ ─│     GamificationMechanic│
└───────────────────────┘       └─────────────────────────┘
            │                              ▲
            ▼                              │
┌───────────────────────┐       ┌─────────────────────────┐
│   RewardStrategy      │─ ─ ─ ─│      MotivatorType      │
└───────────────────────┘       └─────────────────────────┘
```

#### Data Structures

```python
class MotivatorType(str, Enum):
    ACHIEVEMENT = "achievement"
    SOCIAL = "social"
    IMMERSION = "immersion"
    CREATIVITY = "creativity"
    MASTERY = "mastery"
    AUTONOMY = "autonomy"
    PURPOSE = "purpose"

class RewardStrategy(str, Enum):
    FIXED = "fixed"
    VARIABLE = "variable"
    PROGRESSIVE = "progressive"
    COMPETITIVE = "competitive"
    COOPERATIVE = "cooperative"
    MILESTONE = "milestone"

class GamificationMechanic(str, Enum):
    POINTS = "points"
    BADGES = "badges"
    LEVELS = "levels"
    CHALLENGES = "challenges"
    LEADERBOARDS = "leaderboards"
    PROGRESS_BARS = "progress_bars"
    REWARDS = "rewards"
    STREAKS = "streaks"
    SOCIAL_RECOGNITION = "social_recognition"
    STORYTELLING = "storytelling"

class UserMotivationProfile(BaseModel):
    user_id: str
    primary_motivators: List[MotivatorType]
    secondary_motivators: List[MotivatorType]
    effective_mechanics: List[GamificationMechanic]
    reward_preferences: List[RewardStrategy]
    engagement_patterns: Dict[str, float]
    last_updated: datetime
```

#### Key Methods

The `AdaptiveGamificationEngine` class implements:

- `get_user_motivation_profile(user_id)`: Retrieves or creates a user's motivation profile
- `update_user_motivation_profile(user_id, profile_data)`: Updates a profile based on new inputs
- `get_optimal_mechanics(user_id, context)`: Determines the best gamification mechanics for a given context
- `get_recommended_actions(user_id, count)`: Generates specific gamification actions for the user
- `track_effectiveness(user_id, action_name, engagement_score)`: Tracks how well an action motivated the user

### 2. Project Management Tool Integration

#### Class Diagram

```
┌───────────────────────────┐     ┌────────────────────────────┐
│ProjectManagementService   │◄────┤ProjectToolConfig           │
└─────────────┬─────────────┘     └────────────────────────────┘
              │                                   ▲
              │                                   │
              ▼                                   │
┌───────────────────────────┐     ┌────────────────────────────┐
│ProjectManagementIntegration│     │ExternalTask                │
└─────────────┬─────────────┘     └────────────────────────────┘
              │
              │
        ┌─────┴───────┐
        │             │
        ▼             ▼
┌───────────────┐  ┌───────────────┐
│JiraIntegration│  │TrelloInteg... │
└───────────────┘  └───────────────┘
```

#### Data Structures

```python
class ProjectToolConfig(BaseModel):
    tool_id: str
    api_url: str
    username: Optional[str] = None
    api_key: Optional[str] = None
    oauth_token: Optional[str] = None
    default_project: Optional[str] = None
    sync_frequency: int = 60  # minutes
    two_way_sync: bool = True
    last_sync: Optional[datetime] = None

class ExternalTask(BaseModel):
    external_id: str
    title: str
    description: Optional[str] = None
    status: str
    priority: Optional[str] = None
    due_date: Optional[datetime] = None
    assigned_to: Optional[str] = None
    project: Optional[str] = None
    url: Optional[str] = None
    labels: List[str] = []
    last_updated: Optional[datetime] = None
```

#### Interface Definition

The abstract `ProjectManagementIntegration` class defines:

```python
class ProjectManagementIntegration(ABC):
    @abstractmethod
    async def authenticate(self, credentials: Dict[str, Any]) -> bool:
        """Authenticate with the external tool"""
        pass

    @abstractmethod
    async def fetch_tasks(self, since: Optional[datetime] = None) -> List[ExternalTask]:
        """Fetch tasks from the external tool"""
        pass

    @abstractmethod
    async def create_task(self, task_data: Dict[str, Any]) -> ExternalTask:
        """Create a new task in the external tool"""
        pass

    @abstractmethod
    async def update_task(self, external_id: str, task_data: Dict[str, Any]) -> ExternalTask:
        """Update an existing task in the external tool"""
        pass

    @abstractmethod
    async def delete_task(self, external_id: str) -> bool:
        """Delete a task in the external tool"""
        pass

    @abstractmethod
    async def get_projects(self) -> List[Dict[str, Any]]:
        """Get available projects from the external tool"""
        pass
```

### 3. Neurodiverse-Optimized UI

#### Class Diagram

```
┌───────────────────────────┐      ┌────────────────────────────┐
│  AccessibilityService     │◄─────┤ AccessibilityPreferences   │
└─────────────┬─────────────┘      └────────────────────────────┘
              │
              │
              ▼
┌───────────────────────────┐      ┌────────────────────────────┐
│ UIAdaptationStrategy      │◄─────┤ ColorScheme                │
└───────────────────────────┘      └────────────────────────────┘
```

#### Data Structures

```python
class AccessibilityPreferences(BaseModel):
    user_id: str
    color_mode: str = "default"  # default, high-contrast, reduced-blue, etc.
    text_size: float = 1.0  # Scale factor for text
    reduce_motion: bool = False
    reduce_transparency: bool = False
    reduce_distractions: bool = False
    highlight_focus: bool = True
    reading_guide: bool = False
    custom_fonts: bool = False
    font_family: Optional[str] = None
    spacing_scale: float = 1.0
    use_audio_cues: bool = False
    use_visual_cues: bool = True
    last_updated: datetime = Field(default_factory=datetime.now)
```

#### Key Methods

The `AccessibilityService` implements:

- `get_user_preferences(user_id)`: Retrieves or creates user UI preferences
- `update_user_preferences(user_id, preferences)`: Updates UI preferences
- `get_theme_css(user_id, context)`: Generates CSS variables for the UI based on preferences
- `get_wcag_compliance_report()`: Analyzes current settings for accessibility compliance
- `generate_adhd_optimized_ui_settings(context)`: Creates tailored settings for ADHD users

### 4. Calendar Integration System

#### Class Diagram

```
┌───────────────────────────┐       ┌────────────────────────────┐
│ CalendarIntegrationService│◄──────┤ CalendarIntegrationConfig  │
└─────────────┬─────────────┘       └────────────────────────────┘
              │                                    ▲
              │                                    │
              ▼                                    │
┌───────────────────────────┐       ┌────────────────────────────┐
│ CalendarIntegration       │       │ ExternalEvent              │
└─────────────┬─────────────┘       └────────────────────────────┘
              │
              │
       ┌──────┴──────┐
       │             │
       ▼             ▼
┌──────────────┐ ┌───────────────┐
│GoogleCalendar│ │AppleCalendar  │
│Integration   │ │Integration    │
└──────────────┘ └───────────────┘
```

#### Data Structures

```python
class CalendarIntegrationConfig(BaseModel):
    calendar_id: str
    platform: str  # google, apple, outlook, etc.
    user_id: str
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_expiry: Optional[datetime] = None
    sync_frequency: int = 30  # minutes
    two_way_sync: bool = True
    default_reminders: List[int] = [10, 30]  # minutes before
    include_details: bool = True
    color_coding: bool = True
    last_sync: Optional[datetime] = None

class ExternalEvent(BaseModel):
    external_id: str
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    location: Optional[str] = None
    is_all_day: bool = False
    reminders: List[int] = []  # minutes before
    attendees: List[Dict[str, str]] = []
    recurrence: Optional[str] = None
    status: str = "confirmed"  # confirmed, tentative, cancelled
    url: Optional[str] = None
    color: Optional[str] = None
    calendar_id: str
    last_updated: Optional[datetime] = None
```

#### Interface Definition

The abstract `CalendarIntegration` class defines:

```python
class CalendarIntegration(ABC):
    @abstractmethod
    async def authenticate(self, auth_code: str = None, refresh_token: str = None) -> bool:
        """Authenticate with the calendar service"""
        pass

    @abstractmethod
    async def fetch_events(self, start_date: datetime, end_date: datetime) -> List[ExternalEvent]:
        """Fetch events from the calendar"""
        pass

    @abstractmethod
    async def create_event(self, event_data: Dict[str, Any]) -> ExternalEvent:
        """Create a new event in the calendar"""
        pass

    @abstractmethod
    async def update_event(self, external_id: str, event_data: Dict[str, Any]) -> ExternalEvent:
        """Update an existing event in the calendar"""
        pass

    @abstractmethod
    async def delete_event(self, external_id: str) -> bool:
        """Delete an event from the calendar"""
        pass

    @abstractmethod
    async def get_calendars(self) -> List[Dict[str, Any]]:
        """Get available calendars from the service"""
        pass
```

## Implementation Strategy

### Development Phases

1. **Base Infrastructure**: Establish base interfaces and data models (Weeks 1-2)
2. **Core Functionality**: Implement key services and minimal integrations (Weeks 3-5)
3. **Advanced Features**: Add personalization, learning algorithms, and additional integrations (Weeks 6-8)

### Technology Stack

- **Core**: FastAPI, Pydantic, SQLAlchemy
- **Integration**: OAuth2, REST API clients, Webhook handlers
- **UI Components**: CSS variable system, Theme management, WCAG compliance tools
- **Testing**: Pytest, Mock services, Integration test harnesses

## API Contracts

### Adaptive Gamification API

```
POST /api/gamification/profile
GET /api/gamification/profile
PATCH /api/gamification/profile
GET /api/gamification/mechanics
POST /api/gamification/actions
POST /api/gamification/effectiveness/{action_id}
```

### Project Management API

```
POST /api/project-tools/register
GET /api/project-tools
DELETE /api/project-tools/{tool_id}
POST /api/project-tools/sync
GET /api/project-tools/{tool_id}/projects
POST /api/project-tools/{tool_id}/tasks
PUT /api/project-tools/{tool_id}/tasks/{task_id}
DELETE /api/project-tools/{tool_id}/tasks/{task_id}
```

### Accessibility API

```
GET /api/accessibility/preferences
PATCH /api/accessibility/preferences
GET /api/accessibility/theme.css
GET /api/accessibility/wcag-report
GET /api/accessibility/focus-assist-styles
GET /api/accessibility/adhd-optimized-settings
```

### Calendar Integration API

```
POST /api/calendars/register
GET /api/calendars
DELETE /api/calendars/{calendar_id}
POST /api/calendars/sync
GET /api/calendars/{calendar_id}/available
POST /api/calendars/{calendar_id}/events
PUT /api/calendars/{calendar_id}/events/{event_id}
DELETE /api/calendars/{calendar_id}/events/{event_id}
```

## Database Schema Extensions

### Gamification Tables

```sql
CREATE TABLE user_motivation_profiles (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    primary_motivators JSONB,
    secondary_motivators JSONB,
    effective_mechanics JSONB,
    reward_preferences JSONB,
    engagement_patterns JSONB,
    last_updated TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE gamification_actions (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    name TEXT,
    description TEXT,
    mechanic TEXT,
    reward_strategy TEXT,
    target_motivator TEXT,
    difficulty FLOAT,
    engagement_score FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_used TIMESTAMP WITH TIME ZONE
);
```

### Project Management Tables

```sql
CREATE TABLE project_tool_configs (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    tool_id TEXT,
    api_url TEXT,
    username TEXT,
    api_key TEXT,
    oauth_token TEXT,
    default_project TEXT,
    sync_frequency INTEGER,
    two_way_sync BOOLEAN,
    last_sync TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE external_tasks (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    external_id TEXT,
    title TEXT,
    description TEXT,
    status TEXT,
    priority TEXT,
    due_date TIMESTAMP WITH TIME ZONE,
    assigned_to TEXT,
    project TEXT,
    url TEXT,
    labels JSONB,
    last_updated TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Accessibility Tables

```sql
CREATE TABLE accessibility_preferences (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    color_mode TEXT,
    text_size FLOAT,
    reduce_motion BOOLEAN,
    reduce_transparency BOOLEAN,
    reduce_distractions BOOLEAN,
    highlight_focus BOOLEAN,
    reading_guide BOOLEAN,
    custom_fonts BOOLEAN,
    font_family TEXT,
    spacing_scale FLOAT,
    use_audio_cues BOOLEAN,
    use_visual_cues BOOLEAN,
    last_updated TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Calendar Integration Tables

```sql
CREATE TABLE calendar_integration_configs (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    calendar_id TEXT,
    platform TEXT,
    access_token TEXT,
    refresh_token TEXT,
    token_expiry TIMESTAMP WITH TIME ZONE,
    sync_frequency INTEGER,
    two_way_sync BOOLEAN,
    default_reminders JSONB,
    include_details BOOLEAN,
    color_coding BOOLEAN,
    last_sync TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE external_events (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    external_id TEXT,
    title TEXT,
    description TEXT,
    start_time TIMESTAMP WITH TIME ZONE,
    end_time TIMESTAMP WITH TIME ZONE,
    location TEXT,
    is_all_day BOOLEAN,
    reminders JSONB,
    attendees JSONB,
    recurrence TEXT,
    status TEXT,
    url TEXT,
    color TEXT,
    calendar_id TEXT,
    last_updated TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## Security Considerations

1. **OAuth Security**: Using OAuth 2.0 with PKCE for all external service connections
2. **Token Storage**: Secure storage of refresh tokens in encrypted form
3. **Rate Limiting**: Implementing rate limits on synchronization to prevent API abuse
4. **Data Minimization**: Only syncing required data to reduce exposure
5. **Audit Logging**: Tracking all integration activities for security review
6. **Permission Model**: Clear permission model for accessing external services

## Performance Considerations

1. **Async Processing**: All integrations use async processing to prevent blocking
2. **Background Sync**: Calendar and project synchronization runs in the background
3. **Caching**: Gamification and UI settings are cached for performance
4. **Lazy Loading**: UI adaptations load progressively to prioritize critical elements
5. **Selective Sync**: Only syncing changed data to reduce bandwidth and processing
6. **Throttling**: Intelligent throttling of external service requests

## Integration Testing

Each component includes detailed integration tests:

1. **Mock External Services**: Using response mocking for external APIs
2. **Test Data Generation**: Automated test data for various integration scenarios
3. **Error Handling**: Specific tests for error conditions and retries
4. **End-to-End Tests**: Simulated full workflows with multiple components
5. **Performance Testing**: Load testing for synchronization processes

## References

- WCAG 2.2 Guidelines: https://www.w3.org/TR/WCAG22/
- Google Calendar API: https://developers.google.com/calendar
- Jira REST API: https://developer.atlassian.com/cloud/jira/platform/rest/v3/intro/
- Gamification Framework Research: https://doi.org/10.1016/j.chb.2020.106595
