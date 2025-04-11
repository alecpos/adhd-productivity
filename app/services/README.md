# Services Directory

This directory contains the business logic services for the ADHD Calendar application.

## Overview

The services directory houses the core business logic of the application, separated from the API layer and database models. Services implement the application's use cases and orchestrate interactions between different components.

## Core Services

### ML-Related Services

- **TPRService**: Manages temporal pattern recognition functionality
- **TimeEstimationService**: Provides time estimation for tasks based on the ML models
- **ForgetfulnessService**: Handles commitment detection and reminder functionality
- **CircadianService**: Manages energy pattern predictions and circadian rhythm modeling

### User and Authentication Services

- **UserService**: Manages user accounts and profiles
- **AuthService**: Handles authentication and authorization

### Calendar and Task Services

- **CalendarService**: Manages calendar events and schedules
- **TaskService**: Handles task creation, updating, and completion
- **ScheduleOptimizationService**: Optimizes task scheduling based on ML insights

### Integration Services

- **ExternalCalendarService**: Integrates with external calendar providers
- **NotificationService**: Manages user notifications across platforms

## Design Principles

Services in this directory follow these principles:

1. **Separation of Concerns**: Each service has a specific responsibility
2. **Dependency Injection**: Services receive their dependencies via constructor parameters
3. **Domain-Driven Design**: Services implement domain logic based on business requirements
4. **Testing**: All services have corresponding test files in the `app/tests/services` directory

## Usage Example

```python
# Example of using services together
from app.services.tpr_service import TPRService
from app.services.time_estimation_service import TimeEstimationService
from app.services.task_service import TaskService

# Initialize services
tpr_service = TPRService()
time_service = TimeEstimationService()
task_service = TaskService()

# Use services to create an optimized task
optimal_time = tpr_service.get_optimal_time(user_id, task_type)
duration_estimate = time_service.estimate_duration(user_id, task_description, task_type)
task = task_service.create_task(
    user_id=user_id,
    description=task_description,
    scheduled_time=optimal_time,
    estimated_duration=duration_estimate.mean_minutes
)
```

## Development Guidelines

When creating or modifying services:
1. Keep services focused on a specific domain or functionality
2. Implement comprehensive error handling
3. Add appropriate logging for debugging and monitoring
4. Write unit tests for all service methods
5. Document public methods with docstrings

## Documentation

- [Services Architecture](../../docs/services_architecture.md)
- [Integration Patterns](../../docs/integration_patterns.md)
