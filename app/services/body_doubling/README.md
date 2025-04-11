# Body Doubling Service

## Overview

The Body Doubling Service provides virtual accountability partners for ADHD Calendar users. Body doubling is a technique where individuals with ADHD work alongside another person to improve focus and task completion.

## Service Components

This service is organized into several specialized components:

- **BodyDoublingService**: Main service orchestration and API entry point
- **SessionManager**: Handles session creation, retrieval, and lifecycle management
- **MatchingEngine**: Manages user matching algorithms and compatibility
- **AnalyticsService**: Processes session data for insights and recommendations
- **NotificationService**: Manages user notifications for session events

## Directory Structure

```
app/services/body_doubling/
├── __init__.py                 # Package initialization
├── README.md                   # This file
├── body_doubling_service.py    # Main service orchestration
├── session_manager.py          # Session management component
├── matching_engine.py          # User matching component
├── analytics_service.py        # Analytics processing component
├── notification_service.py     # Notification management component
├── models.py                   # Data models and schemas
├── exceptions.py               # Domain-specific exceptions
├── Refactoring_Summary.md      # Documentation of refactoring process
├── Testing_Strategy.md         # Testing approach and guidelines
└── Future_Improvements.md      # Planned enhancements and roadmap
```

## Usage Examples

### Creating a New Session

```python
from app.services.body_doubling import BodyDoublingService

# Initialize the service
body_doubling_service = BodyDoublingService(db_session)

# Create a new body doubling session
session = await body_doubling_service.create_session(
    user_id=user_id,
    session_type="focus",
    duration=60,  # minutes
    topic="Coding project",
    preferences={
        "communication_mode": "video",
        "experience_level": "beginner"
    }
)
```

### Finding a Match

```python
# Request a match with specific criteria
match_request = await body_doubling_service.request_match(
    user_id=user_id,
    criteria={
        "session_type": "focus",
        "duration": {"min": 30, "max": 90},
        "topics": ["coding", "writing", "studying"]
    }
)

# Check for match status
match_status = await body_doubling_service.check_match_status(match_request.id)
```

### Joining a Session

```python
# Join an existing session
await body_doubling_service.join_session(
    session_id=session.id,
    user_id=participant_id
)
```

## Testing

Tests for this service are located in `app/tests/services/body_doubling/`.

Run all tests with:

```bash
./scripts/run_body_doubling_tests.sh
```

## Documentation

- **Refactoring_Summary.md**: Details about the service refactoring process and improvements
- **Testing_Strategy.md**: Guidelines for testing different components of the service
- **Future_Improvements.md**: Roadmap for future enhancements to the service

## Contributing

When contributing to this service:

1. Ensure all new features have corresponding tests
2. Follow the component-based architecture pattern
3. Document all public interfaces
4. Run the test suite before submitting changes

## Component Responsibilities

### BodyDoublingService

- Provides the main API for client applications
- Orchestrates interactions between specialized components
- Handles high-level error management
- Provides transaction management

### SessionManager

- Creates and retrieves body doubling sessions
- Manages session state transitions
- Handles participant management
- Enforces session policies and constraints

### MatchingEngine

- Implements user matching algorithms
- Manages matching criteria and preferences
- Provides compatibility scoring
- Handles match request queueing

### AnalyticsService

- Processes session data for insights
- Generates user activity reports
- Provides recommendation data
- Tracks effectiveness metrics

### NotificationService

- Sends session event notifications
- Manages notification preferences
- Handles delivery to multiple channels
- Provides notification templates 