# Schema Management Documentation

## Overview
This document details the schema management system for the ADHD Calendar Backend.

## Schema Architecture

### Base Schemas
All schemas inherit from base schemas that provide common functionality:
- Timestamps
- Validation
- Serialization
- Type checking
- Version management

### Schema Factory
The `SchemaFactory` manages schema creation:
- Schema instantiation
- Validation rules
- Default values
- Type conversion
- Version handling

### Schema Registry
The `SchemaRegistry` manages schema registration:
- Schema registration
- Version tracking
- Validation rules
- Schema relationships
- Migration paths

## Core Schemas

### Task Schema
`TaskSchema` defines task structure:
```python
class TaskSchema(BaseSchema):
    title: str
    description: Optional[str]
    status: TaskStatus
    priority: Priority
    due_date: Optional[datetime]
    tags: List[str]
    dependencies: List[str]
```

### Calendar Schema
`CalendarSchema` defines calendar events:
```python
class CalendarEventSchema(BaseSchema):
    title: str
    description: Optional[str]
    start_time: datetime
    end_time: datetime
    attendees: List[str]
    location: Optional[str]
    recurrence: Optional[RecurrenceRule]
```

### Mental Health Schema
`MentalHealthSchema` defines mental health tracking:
```python
class MoodLogSchema(BaseSchema):
    mood_level: int
    energy_level: int
    notes: Optional[str]
    timestamp: datetime
    tags: List[str]
```

### Focus Schemas

#### Pomodoro Schema
`PomodoroSchema` defines focus sessions:
```python
class PomodoroSessionSchema(BaseSchema):
    duration: int
    break_duration: int
    task_id: Optional[str]
    status: SessionStatus
    start_time: Optional[datetime]
    end_time: Optional[datetime]
```

#### Body Doubling Schema
`BodyDoublingSchema` defines collaborative sessions:
```python
class BodyDoublingSessionSchema(BaseSchema):
    title: str
    description: Optional[str]
    duration: int
    max_participants: int
    environment: Environment
    status: SessionStatus
```

## Schema Validation

### Validation Rules
Define validation rules for schemas:
```python
@validation_rule("task_title")
def validate_task_title(title: str) -> bool:
    return len(title) >= 3 and len(title) <= 100

@validation_rule("mood_level")
def validate_mood_level(level: int) -> bool:
    return 1 <= level <= 10
```

### Custom Validators
Create custom validators for complex validation:
```python
class TaskValidator(BaseValidator):
    def validate_dependencies(self, task: Task) -> bool:
        return all(self.task_exists(dep) for dep in task.dependencies)
```

## Schema Versioning

### Version Management
Handle schema versions:
```python
@schema_version("2.0")
class TaskSchemaV2(TaskSchema):
    priority_score: float
    estimated_duration: int
```

### Migration Paths
Define migration between versions:
```python
@migration_path("1.0", "2.0")
def migrate_task_schema(old: Dict) -> Dict:
    return {
        **old,
        "priority_score": calculate_priority(old["priority"]),
        "estimated_duration": 30
    }
```

## Schema Relationships

### One-to-Many
Define one-to-many relationships:
```python
class UserSchema(BaseSchema):
    tasks: List[TaskSchema]
    calendar_events: List[CalendarEventSchema]
```

### Many-to-Many
Define many-to-many relationships:
```python
class ProjectSchema(BaseSchema):
    members: List[UserSchema]
    tasks: List[TaskSchema]
```

## Schema Utilities

### Type Conversion
Convert between types:
```python
@type_converter
def datetime_to_string(dt: datetime) -> str:
    return dt.isoformat()

@type_converter
def string_to_datetime(s: str) -> datetime:
    return datetime.fromisoformat(s)
```

### Default Values
Define default values:
```python
@default_value("task_status")
def default_task_status() -> str:
    return "pending"

@default_value("created_at")
def default_created_at() -> datetime:
    return datetime.utcnow()
```

## Schema Documentation

### Field Documentation
Document schema fields:
```python
class TaskSchema(BaseSchema):
    """Task schema for managing user tasks."""
    
    title: str = Field(
        description="Task title",
        min_length=3,
        max_length=100
    )
```

### Schema Examples
Provide usage examples:
```python
example_task = {
    "title": "Complete project",
    "description": "Finish the project documentation",
    "priority": "high",
    "due_date": "2024-01-01T00:00:00Z"
}
```

## Best Practices

### Schema Design
1. Use clear, descriptive field names
2. Include proper validation rules
3. Document all fields
4. Handle optional fields properly
5. Use appropriate field types

### Validation
1. Validate at schema level
2. Add business rule validation
3. Handle validation errors gracefully
4. Provide clear error messages
5. Use custom validators when needed

### Versioning
1. Plan for schema evolution
2. Maintain backward compatibility
3. Document breaking changes
4. Provide migration paths
5. Test migrations thoroughly

### Performance
1. Optimize validation rules
2. Use efficient data types
3. Cache validation results
4. Batch operations when possible
5. Monitor schema performance

## Testing

### Schema Tests
```python
def test_task_schema_validation():
    task = TaskSchema(title="Test Task")
    assert task.is_valid()
```

### Migration Tests
```python
def test_schema_migration():
    old_task = TaskSchemaV1(...)
    new_task = migrate_to_v2(old_task)
    assert isinstance(new_task, TaskSchemaV2)
```

### Validation Tests
```python
def test_custom_validation():
    validator = TaskValidator()
    assert validator.validate_dependencies(task)
```

## Error Handling

### Validation Errors
Handle validation errors:
```python
try:
    task = TaskSchema(**data)
except ValidationError as e:
    handle_validation_error(e)
```

### Migration Errors
Handle migration errors:
```python
try:
    new_schema = migrate_schema(old_schema)
except MigrationError as e:
    handle_migration_error(e)
``` 