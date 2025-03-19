# Schema Management System Documentation

## Overview
The schema management system provides a centralized way to handle data validation, schema versioning, and schema migrations across the application. It consists of several key components that work together to ensure data consistency and type safety.

## Components

### 1. SchemaFactory
The SchemaFactory is responsible for creating schema instances with proper validation and defaults.

```python
from app.schemas.schema_factory import SchemaFactory

# Create a schema factory instance
factory = SchemaFactory()

# Create a schema with validation
schema = factory.create_schema("user", {
    "name": "John Doe",
    "email": "john@example.com"
})
```

### 2. SchemaRegistry
The SchemaRegistry maintains a registry of all schemas and their validation rules.

```python
from app.schemas.schema_registry import SchemaRegistry

# Create a registry instance
registry = SchemaRegistry()

# Register a schema
registry.register_schema("user", UserSchema)

# Register validation rules
registry.register_validation_rule("user", lambda x: len(x.name) > 3)
```

### 3. SchemaManager
The SchemaManager handles schema validation, migration, and versioning.

```python
from app.schemas.schema_manager import SchemaManager

# Create a manager instance
manager = SchemaManager()

# Validate and migrate data
data = {"name": "John", "old_field": "value"}
validated_data = manager.validate_and_migrate("user", data)
```

## Common Use Cases

### 1. Creating and Validating Schemas
```python
# Define a schema
from app.schemas.base_schemas import BaseSchema
from typing import Optional

class UserSchema(BaseSchema):
    name: str
    email: str
    age: Optional[int] = None

# Create and validate
factory = SchemaFactory()
schema = factory.create_schema("user", {
    "name": "John Doe",
    "email": "john@example.com"
})
```

### 2. Schema Validation Rules
```python
# Register validation rules
registry = SchemaRegistry()
registry.register_validation_rule("user", lambda x: "@" in x.email)
registry.register_validation_rule("user", lambda x: len(x.name) >= 2)

# Validate schema
is_valid = registry.validate_schema("user", user_schema)
```

### 3. Schema Migration
```python
# Migrate schema from old version to new
manager = SchemaManager()
old_data = {
    "name": "John",
    "old_field": "value"
}
migrated_data = manager.migrate_schema("user", old_data, "1.0.0", "2.0.0")
```

### 4. Bulk Operations
```python
# Validate multiple items
data_list = [
    {"name": "User 1", "email": "user1@example.com"},
    {"name": "User 2", "email": "user2@example.com"}
]
validated_list = manager.validate_bulk("user", data_list)
```

## Best Practices

### 1. Schema Definition
- Always inherit from BaseSchema or TimestampedSchema
- Use proper type hints for all fields
- Provide default values where appropriate
- Document schema fields with Field descriptions

```python
from app.schemas.base_schemas import TimestampedSchema
from pydantic import Field

class TaskSchema(TimestampedSchema):
    title: str = Field(..., description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    due_date: datetime = Field(..., description="Task due date")
```

### 2. Validation Rules
- Keep validation rules simple and focused
- Use descriptive names for custom validators
- Handle edge cases appropriately
- Document validation requirements

```python
def validate_task_due_date(task):
    """Ensure task due date is in the future."""
    return task.due_date > datetime.now()

registry.register_validation_rule("task", validate_task_due_date)
```

### 3. Schema Migration
- Document schema changes
- Provide migration paths for all version changes
- Test migrations with sample data
- Handle data type conversions carefully

```python
def migrate_task_v1_to_v2(data):
    """Migrate task schema from v1 to v2."""
    if "priority" not in data:
        data["priority"] = "medium"
    return data

manager.register_migration("task", "1.0.0", "2.0.0", migrate_task_v1_to_v2)
```

## Error Handling

### 1. Validation Errors
```python
try:
    validated_data = manager.validate_and_migrate("user", data)
except ValidationError as e:
    print(f"Validation failed: {e.errors()}")
```

### 2. Migration Errors
```python
try:
    migrated_data = manager.migrate_schema("user", data, "1.0.0", "2.0.0")
except ValueError as e:
    print(f"Migration failed: {str(e)}")
```

## Performance Considerations

### 1. Bulk Operations
- Use bulk validation for large datasets
- Consider pagination for very large datasets
- Monitor validation performance

```python
# Efficient bulk validation
data_list = [{"name": f"User {i}"} for i in range(1000)]
validated_list = manager.validate_bulk("user", data_list)
```

### 2. Caching
- Cache schema instances when possible
- Cache validation results for static data
- Use schema version checking for cache invalidation

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_validated_schema(schema_name, version):
    return manager.get_schema_version(schema_name, version)
```

## Integration with Routes

### 1. Request Validation
```python
@router.post("/users", response_model=APIResponse[UserSchema])
async def create_user(
    data: UserSchema,
    db: AsyncSession = Depends(get_db)
):
    """Create a new user with schema validation."""
    validated_data = manager.validate_and_migrate("user", data.dict())
    # Process validated data...
```

### 2. Response Validation
```python
@router.get("/users/{id}", response_model=APIResponse[UserSchema])
async def get_user(
    id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get user with validated response."""
    user = await service.get_user(id)
    validated_user = manager.validate_and_migrate("user", user)
    return APIResponse(data=validated_user)
```

## Testing

### 1. Schema Tests
```python
def test_user_schema():
    """Test user schema validation."""
    data = {
        "name": "Test User",
        "email": "test@example.com"
    }
    schema = factory.create_schema("user", data)
    assert schema.name == "Test User"
```

### 2. Validation Tests
```python
def test_user_validation():
    """Test user validation rules."""
    user = UserSchema(name="Test", email="invalid")
    with pytest.raises(ValidationError):
        registry.validate_schema("user", user)
```

### 3. Migration Tests
```python
def test_user_migration():
    """Test user schema migration."""
    old_data = {
        "name": "Test",
        "old_field": "value"
    }
    migrated = manager.migrate_schema("user", old_data, "1.0.0", "2.0.0")
    assert "old_field" not in migrated
``` 