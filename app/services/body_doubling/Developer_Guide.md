# Body Doubling Service: Developer Guide

This guide provides detailed information for developers who need to extend or modify the Body Doubling Service.

## Table of Contents

1. [Development Environment Setup](#development-environment-setup)
2. [Architecture Overview](#architecture-overview)
3. [Adding New Features](#adding-new-features)
4. [Extending Components](#extending-components)
5. [Testing Guidelines](#testing-guidelines)
6. [Common Patterns](#common-patterns)
7. [Troubleshooting](#troubleshooting)

## Development Environment Setup

### Prerequisites

- Python 3.9+
- PostgreSQL 13+
- Redis (for caching, optional)

### Local Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/adhd_calendar_backend.git
   cd adhd_calendar_backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

4. Run tests to verify setup:
   ```bash
   ./scripts/run_body_doubling_tests.sh
   ```

## Architecture Overview

The Body Doubling Service follows a component-based architecture with clear separation of concerns:

```
BodyDoublingService (Orchestrator)
├── SessionManager (Session CRUD and lifecycle)
├── MatchingEngine (User matching algorithms)
├── AnalyticsService (Data processing and insights)
└── NotificationService (User notifications)
```

Key design patterns used:

- **Dependency Injection**: Components receive their dependencies rather than creating them
- **Repository Pattern**: Database access is abstracted through repositories
- **Service Layer**: Business logic is contained in service classes
- **Command Query Responsibility Segregation (CQRS)**: Methods are separated into commands (state changes) and queries (data retrieval)

## Adding New Features

When adding new features to the Body Doubling Service, follow these steps:

1. **Identify the Component**: Determine which component should own the feature
2. **Write Tests First**: Create tests that define the expected behavior
3. **Implement the Feature**: Add the necessary code to pass the tests
4. **Update Documentation**: Document the new feature in the appropriate files
5. **Integration Testing**: Ensure the feature works correctly with other components

### Example: Adding a New Session Type

1. Update `models.py` to include the new session type
2. Add validation logic in `session_manager.py`
3. Update matching rules in `matching_engine.py` if needed
4. Add any specialized analytics in `analytics_service.py`
5. Test the new session type functionality

## Extending Components

### Extending the SessionManager

The SessionManager handles session lifecycle. To extend it:

1. Add new methods to the `SessionManager` class in `session_manager.py`
2. Update tests in `test_session_manager.py`

Example of adding a new method:

```python
async def pause_session(self, session_id: UUID, pause_duration: int) -> Session:
    """Temporarily pause an active session.

    Args:
        session_id: The ID of the session to pause
        pause_duration: Pause duration in minutes

    Returns:
        Updated session object

    Raises:
        SessionNotFoundError: If session doesn't exist
        InvalidSessionStateError: If session is not in an active state
    """
    session = await self._get_session_by_id(session_id)

    if session.status != SessionStatus.ACTIVE:
        raise InvalidSessionStateError(f"Cannot pause session with status {session.status}")

    session.status = SessionStatus.PAUSED
    session.metadata["pause_end_time"] = (datetime.now() +
                                         timedelta(minutes=pause_duration)).isoformat()

    await self._db.commit()
    await self._notification_service.notify_session_paused(session)

    return session
```

### Extending the MatchingEngine

To add new matching algorithms:

1. Create a new method in the `MatchingEngine` class
2. Add corresponding tests

Example:

```python
async def match_by_topic_similarity(self, user_id: UUID, topics: List[str]) -> List[MatchResult]:
    """Find matches based on topic similarity.

    Args:
        user_id: The user requesting matches
        topics: List of topics the user is interested in

    Returns:
        List of potential matches with similarity scores
    """
    # Implementation details...
    return matches
```

### Extending the AnalyticsService

To add new analytics capabilities:

1. Add a new method to the `AnalyticsService` class
2. Create corresponding tests

Example:

```python
async def calculate_topic_productivity(self, user_id: UUID) -> Dict[str, float]:
    """Calculate user's productivity score by topic.

    Args:
        user_id: The user to analyze

    Returns:
        Dictionary mapping topics to productivity scores
    """
    # Implementation details...
    return topic_scores
```

## Testing Guidelines

### Unit Tests

Each component should have comprehensive unit tests:

- Test public methods with various input combinations
- Test edge cases and error conditions
- Mock dependencies to isolate the component

Example test for SessionManager:

```python
@pytest.mark.asyncio
async def test_create_session_with_invalid_duration(self, session_manager, user_id):
    # Arrange
    invalid_session_data = {
        "type": "focus",
        "duration": -30,  # Invalid duration
        "topic": "Test topic"
    }

    # Act & Assert
    with pytest.raises(InvalidSessionParameterError):
        await session_manager.create_session(user_id, invalid_session_data)
```

### Integration Tests

Integration tests verify component interactions:

- Test realistic workflows across components
- Use an in-memory database when possible
- Test error propagation between components

Example integration test:

```python
@pytest.mark.asyncio
async def test_match_request_and_accept_flow(self, body_doubling_service, user_1_id, user_2_id):
    # Arrange - Create match request
    match_request = await body_doubling_service.request_match(
        user_id=user_1_id,
        criteria={"topic": "coding"}
    )

    # Act - Accept match
    session = await body_doubling_service.accept_match(
        match_request_id=match_request.id,
        user_id=user_2_id
    )

    # Assert
    assert session is not None
    assert session.participants[0].user_id == user_1_id
    assert session.participants[1].user_id == user_2_id
```

## Common Patterns

### Error Handling

Use domain-specific exceptions in the `exceptions.py` file:

```python
class SessionError(Exception):
    """Base exception for session-related errors."""
    pass

class SessionNotFoundError(SessionError):
    """Raised when a session is not found."""
    pass

class InvalidSessionStateError(SessionError):
    """Raised when an operation is invalid for the current session state."""
    pass
```

Handle exceptions at the component level when possible, propagating only when necessary.

### Async/Await

All database operations and service methods should be asynchronous:

```python
async def get_session(self, session_id: UUID) -> Session:
    try:
        session = await self._session_manager.get_session(session_id)
        return session
    except SessionNotFoundError:
        self._logger.error(f"Session not found: {session_id}")
        raise
```

### Logging

Use structured logging with context:

```python
self._logger.info("Creating new session", extra={
    "user_id": str(user_id),
    "session_type": session_data.get("type"),
    "duration": session_data.get("duration")
})
```

## Troubleshooting

### Common Issues

1. **Database Connection Issues**
   - Check database URL in configuration
   - Verify network connectivity
   - Ensure database server is running

2. **Test Failures**
   - Check for missing migrations
   - Ensure test database is properly configured
   - Look for timing issues in async tests

3. **Performance Problems**
   - Use query logging to identify slow database operations
   - Check for N+1 query issues
   - Verify proper use of async/await

### Debugging

1. Use the debug flag for more detailed logging:
   ```bash
   DEBUG=1 pytest app/tests/services/body_doubling/test_integration.py -v
   ```

2. Use Python's debugger:
   ```python
   import pdb; pdb.set_trace()
   ```

3. For async debugging, use:
   ```python
   import asyncio
   asyncio.get_event_loop().set_debug(True)
   ```

---

*Last updated: November 15, 2023*
