# SQLAlchemy Models Documentation

This document provides information about the SQLAlchemy models used in the ADHD Calendar application and best practices for working with them.

## Overview

SQLAlchemy is an Object-Relational Mapping (ORM) library for Python that provides a set of high-level API for interacting with relational databases. In the ADHD Calendar application, we use SQLAlchemy models to:

- Define database schema
- Perform database operations
- Validate data
- Enforce relationships between entities

## Model Structure

### Base Model

All models inherit from a common base model that provides shared functionality:

```python
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, DateTime
from datetime import datetime
import uuid

Base = declarative_base()

class BaseModel(Base):
    __abstract__ = True
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Common methods for all models
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
```

### Model Example

Here's an example of a typical model definition:

```python
from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, Enum, JSON, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import enum

class TaskStatus(enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELED = "canceled"
    DEFERRED = "deferred"

class TaskPriority(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class Task(BaseModel):
    __tablename__ = "tasks"
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    priority = Column(Enum(TaskPriority), default=TaskPriority.MEDIUM, nullable=False)
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING, nullable=False)
    due_date = Column(DateTime, nullable=True)
    estimated_duration = Column(Integer, nullable=True)  # in minutes
    actual_duration = Column(Integer, nullable=True)  # in minutes
    tags = Column(JSON, default=list, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="tasks")
    reminders = relationship("Reminder", back_populates="task", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Task id={self.id} title='{self.title}' status={self.status}>"
```

## Key Model Components

### Common Fields

Most models include:

- **id**: Primary key, usually a UUID
- **created_at**: Timestamp when the record was created
- **updated_at**: Timestamp when the record was last updated

### Relationships

SQLAlchemy relationships are defined using the `relationship()` function:

```python
# One-to-many relationship
tasks = relationship("Task", back_populates="user", cascade="all, delete-orphan")

# Many-to-one relationship
user = relationship("User", back_populates="tasks")

# One-to-one relationship
profile = relationship("UserProfile", uselist=False, back_populates="user", cascade="all, delete-orphan")
```

Common relationship options:
- `back_populates`: Links relationships on both sides
- `cascade`: Controls how operations cascade to related objects
- `uselist`: When set to False, creates a one-to-one relationship
- `lazy`: Controls how the relationship loads (`'select'`, `'joined'`, `'subquery'`, etc.)

### Data Types

Common SQLAlchemy data types used in the application:

- **String**: For character strings with optional length limit
- **Text**: For large text fields without length limit
- **Integer**: For whole numbers
- **Float**: For decimal numbers
- **Boolean**: For true/false values
- **DateTime**: For timestamps and dates
- **Enum**: For fields with a fixed set of values
- **JSON**: For structured JSON data
- **UUID**: For UUID primary keys

### Constraints

Models use constraints to enforce data integrity:

```python
# Primary key
id = Column(UUID, primary_key=True, default=uuid.uuid4)

# Foreign key with cascade delete
user_id = Column(UUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

# Unique constraint
email = Column(String(255), unique=True, nullable=False)

# Check constraint
age = Column(Integer, CheckConstraint("age >= 0"), nullable=True)

# Not null constraint
name = Column(String(255), nullable=False)

# Default value
is_active = Column(Boolean, default=True, nullable=False)
```

## Best Practices

### Model Organization

1. **Logical Grouping**: Group related models in the same file
2. **Imports at Top**: Keep imports at the top of the file
3. **Enum Definitions First**: Define enums before the models that use them
4. **Clear Class Hierarchy**: Use inheritance appropriately

### Relationship Management

1. **Consistent Naming**: Use consistent names for relationships
2. **Two-Way Relationships**: Use `back_populates` to establish two-way relationships
3. **Cascading Operations**: Set appropriate cascade options
4. **Avoid Circular Imports**: Use string references to break circular imports

```python
# Avoid circular imports by using string references
relationship("User", back_populates="tasks")
```

### Query Optimization

1. **Eager Loading**: Use eager loading for related objects that will be accessed
2. **Selective Loading**: Load only the columns you need
3. **Efficient Filtering**: Apply filters at the database level, not in Python
4. **Pagination**: Use pagination for large result sets

```python
# Eager loading with joined loading
query = session.query(Task).options(
    joinedload(Task.user),
    joinedload(Task.reminders)
).filter(Task.status == TaskStatus.PENDING)

# Selective loading
query = session.query(Task.id, Task.title, Task.due_date)

# Efficient filtering
query = session.query(Task).filter(
    Task.user_id == user_id,
    Task.due_date <= datetime.utcnow()
)

# Pagination
query = session.query(Task).offset(page * page_size).limit(page_size)
```

### Data Validation

1. **Model-Level Validation**: Implement validation logic in models
2. **Constraints**: Use database constraints to enforce data rules
3. **Custom Validators**: Implement custom validators when needed

### Testing

1. **Isolation**: Use separate test databases
2. **Fixtures**: Create fixtures for common test data
3. **Transactions**: Use transaction rollbacks to clean up after tests

## Common Operations

### Creating Objects

```python
# Create a new user
user = User(email="user@example.com", password_hash="hashed_password")
session.add(user)
session.commit()

# Create a related object
task = Task(
    user=user,
    title="Complete documentation",
    description="Write SQLAlchemy models documentation",
    priority=TaskPriority.HIGH
)
session.add(task)
session.commit()
```

### Querying Objects

```python
# Get by ID
user = session.query(User).get(user_id)

# Filter by conditions
pending_tasks = session.query(Task).filter(
    Task.status == TaskStatus.PENDING,
    Task.due_date <= datetime.utcnow()
).all()

# Join relationships
user_with_tasks = session.query(User).join(User.tasks).filter(
    Task.status == TaskStatus.PENDING
).first()

# Order by
oldest_tasks = session.query(Task).order_by(Task.created_at.asc()).all()
```

### Updating Objects

```python
# Update a single object
task = session.query(Task).get(task_id)
task.status = TaskStatus.COMPLETED
task.actual_duration = 60
session.commit()

# Bulk update
session.query(Task).filter(
    Task.due_date < datetime.utcnow(),
    Task.status == TaskStatus.PENDING
).update({"status": TaskStatus.OVERDUE})
session.commit()
```

### Deleting Objects

```python
# Delete a single object
task = session.query(Task).get(task_id)
session.delete(task)
session.commit()

# Bulk delete
session.query(Task).filter(Task.status == TaskStatus.CANCELED).delete()
session.commit()
```

## Related Resources

- [Database Schema Documentation](./database_schema.md)
- [Alembic Migration Guide](./alembic_guide.md)
- [SQLAlchemy Official Documentation](https://docs.sqlalchemy.org/en/14/) 