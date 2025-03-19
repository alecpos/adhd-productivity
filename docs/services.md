# Service Layer Documentation

## Overview
This document details the service layer architecture and implementation for the ADHD Calendar Backend.

## Service Architecture

### Base Service
All services inherit from `BaseService` which provides:
- Database session management
- Error handling
- Logging
- Caching
- Event dispatching
- Validation

### Service Factory
The `ServiceFactory` manages service instantiation and dependencies:
- Singleton service instances
- Dependency injection
- Configuration management
- Service lifecycle

## Core Services

### Task Service
`TaskService` manages task-related operations:
- Task CRUD operations
- Task prioritization
- Task scheduling
- Task dependencies
- Progress tracking
- Task analytics

### Calendar Service
`CalendarService` handles calendar functionality:
- Event management
- Schedule optimization
- Conflict resolution
- Calendar sync
- Availability management
- Recurring events

### Mental Health Service
`MentalHealthService` provides mental health tracking:
- Mood logging
- Anxiety tracking
- Coping strategies
- Wellness reports
- Crisis support
- Progress analytics

### Focus Services

#### Pomodoro Service
`PomodoroService` manages focus sessions:
- Session management
- Break handling
- Progress tracking
- Statistics
- Settings management
- Notifications

#### Body Doubling Service
`BodyDoublingService` handles collaborative sessions:
- Session creation
- Participant management
- Real-time interaction
- Progress tracking
- Environment management
- Accountability features

### Analytics Service
`AnalyticsService` provides data analysis:
- Productivity metrics
- Usage statistics
- Trend analysis
- Custom reports
- Data visualization
- Performance insights

## Service Integration

### Event System
Services communicate through events:
```python
@event_handler("task.completed")
async def handle_task_completion(task_id: str):
    await notify_completion(task_id)
    await update_statistics(task_id)
```

### Dependency Management
Services can depend on other services:
```python
class TaskService(BaseService):
    def __init__(self, calendar_service: CalendarService):
        self.calendar_service = calendar_service
```

## Service Patterns

### Repository Pattern
Data access through repositories:
```python
class TaskRepository:
    async def get_by_id(self, task_id: str) -> Task:
        return await self.db.tasks.get(task_id)
```

### Unit of Work
Transaction management:
```python
async with UnitOfWork() as uow:
    task = await uow.tasks.get(task_id)
    task.complete()
    await uow.commit()
```

### Service Layer
Business logic in services:
```python
class TaskService:
    async def complete_task(self, task_id: str):
        task = await self.get_task(task_id)
        await self.validate_completion(task)
        await self.update_task_status(task)
```

## Error Handling

### Service Exceptions
Custom exceptions for different scenarios:
```python
class TaskNotFoundError(ServiceError):
    pass

class InvalidTaskStateError(ServiceError):
    pass
```

### Error Recovery
Graceful error handling:
```python
try:
    await service.process_task(task_id)
except TaskNotFoundError:
    await handle_missing_task(task_id)
except InvalidTaskStateError:
    await handle_invalid_state(task_id)
```

## Caching Strategy

### Cache Decorators
```python
@cached(ttl=300)
async def get_user_tasks(user_id: str) -> List[Task]:
    return await self.task_repo.get_user_tasks(user_id)
```

### Cache Invalidation
```python
async def update_task(self, task_id: str):
    await self.cache.invalidate(f"task:{task_id}")
```

## Validation

### Schema Validation
```python
async def create_task(self, task_data: TaskSchema):
    validated = await self.validate_schema(task_data)
    return await self.task_repo.create(validated)
```

### Business Rules
```python
async def validate_task_completion(self, task: Task):
    if not task.can_complete():
        raise InvalidTaskStateError()
```

## Service Configuration

### Environment Variables
```python
class ServiceConfig:
    DATABASE_URL: str
    REDIS_URL: str
    API_KEY: str
```

### Feature Flags
```python
if self.config.FEATURE_ADVANCED_ANALYTICS:
    await self.process_advanced_metrics()
```

## Monitoring

### Logging
```python
self.logger.info("Processing task", task_id=task.id)
```

### Metrics
```python
await self.metrics.increment("tasks_completed")
```

### Tracing
```python
with self.tracer.span("process_task"):
    await self.process_task_logic()
```

## Testing

### Unit Tests
```python
async def test_task_completion():
    task = await service.complete_task(task_id)
    assert task.status == "completed"
```

### Integration Tests
```python
async def test_task_calendar_integration():
    task = await task_service.create_task(task_data)
    event = await calendar_service.get_task_event(task.id)
    assert event is not None
```

## Best Practices
1. Follow single responsibility principle
2. Use dependency injection
3. Implement proper error handling
4. Add comprehensive logging
5. Use proper validation
6. Implement caching strategy
7. Follow async/await patterns
8. Add proper documentation
9. Include unit tests
10. Monitor performance 