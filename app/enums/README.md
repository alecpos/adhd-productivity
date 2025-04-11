# Enums Directory

This directory contains enumeration classes used throughout the ADHD Calendar application.

## Overview

The enums directory defines enumeration classes that represent fixed sets of values used across the application. Using enumerations helps maintain consistency, type safety, and code clarity by avoiding magic strings and numbers.

## Key Enumerations

### User-Related Enums

- **UserRole**: Defines user roles (e.g., USER, ADMIN, THERAPIST)
- **UserStatus**: Defines user account statuses (e.g., ACTIVE, SUSPENDED, DELETED)
- **AuthProvider**: Authentication providers (e.g., EMAIL, GOOGLE, APPLE)

### Task-Related Enums

- **TaskStatus**: Task statuses (e.g., PENDING, IN_PROGRESS, COMPLETED)
- **TaskPriority**: Task priority levels (e.g., LOW, MEDIUM, HIGH, URGENT)
- **TaskType**: Task types based on cognitive requirements (e.g., DEEP_FOCUS, QUICK_TASK)

### ML-Related Enums

- **ProductivityLevel**: Productivity levels (e.g., LOW, MEDIUM, HIGH)
- **CircadianPhase**: Circadian rhythm phases (e.g., MORNING_PEAK, AFTERNOON_DIP)
- **ReminderType**: Types of reminders (e.g., STANDARD, CONTEXTUAL, ADAPTIVE)

### System Enums

- **ErrorCode**: Error codes for API responses
- **ResourceType**: Types of resources in the system
- **PermissionLevel**: Permission levels for access control

## Implementation Pattern

Enums are implemented using Python's Enum class:

```python
from enum import Enum, auto

class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELED = "canceled"
    DEFERRED = "deferred"
```

## Usage Example

```python
from app.enums.task_enums import TaskStatus, TaskPriority

def create_new_task(description: str, priority: TaskPriority):
    return {
        "description": description,
        "priority": priority,
        "status": TaskStatus.PENDING
    }

# Using the enum
task = create_new_task("Complete project proposal", TaskPriority.HIGH)
```

## Development Guidelines

When working with enumerations:

1. Use string-based enums for database and API compatibility
2. Include descriptive docstrings for each enum and value
3. Keep enum definitions focused and cohesive
4. Consider backwards compatibility when modifying enums
5. Include methods for conversion between enum values and display values

## Related Documentation

- [Enum Usage Patterns](../../docs/enum_usage_patterns.md)
- [API Data Types](../../docs/api_data_types.md)
