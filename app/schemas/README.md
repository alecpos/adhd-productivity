# Schemas Directory

This directory contains request and response data schemas for the ADHD Calendar application.

## Overview

The schemas directory defines Pydantic models that represent the shape of data for API requests and responses. These schemas provide validation, serialization, and documentation for the application's data structures.

## Schema Categories

### User Schemas

- **UserCreate**: Schema for creating a new user
- **UserUpdate**: Schema for updating user information
- **UserResponse**: Schema for user data in responses
- **UserProfileResponse**: Schema for user profile data

### Authentication Schemas

- **Token**: Schema for authentication tokens
- **TokenPayload**: Schema for token payload data
- **LoginRequest**: Schema for login requests
- **RegisterRequest**: Schema for registration requests

### Task Schemas

- **TaskCreate**: Schema for creating a new task
- **TaskUpdate**: Schema for updating task information
- **TaskResponse**: Schema for task data in responses
- **TaskListResponse**: Schema for paginated task lists

### Calendar Schemas

- **EventCreate**: Schema for creating a calendar event
- **EventUpdate**: Schema for updating event information
- **EventResponse**: Schema for event data in responses
- **ScheduleResponse**: Schema for schedule data

### ML-Related Schemas

- **ProductivityPatternResponse**: Schema for productivity pattern data
- **TimeEstimationRequest**: Schema for time estimation requests
- **TimeEstimationResponse**: Schema for time estimation results
- **CommitmentResponse**: Schema for detected commitments

## Schema Structure

Schemas typically include:

- Field definitions with types
- Validation rules (min/max values, regex patterns, etc.)
- Default values
- Example values for documentation
- Config options for model behavior

## Schema Inheritance

Schemas often use inheritance for shared fields:

- Base models define common fields
- Specialized models inherit and extend base models
- Response models often include base fields plus system-generated fields

## Example Schema

```python
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID

class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    due_date: Optional[datetime] = None
    estimated_duration: Optional[int] = Field(None, ge=1, description="Duration in minutes")
    priority: str = Field("medium", regex="^(low|medium|high|urgent)$")
    
    @validator("title")
    def title_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError("Title must not be empty")
        return v

class TaskCreate(TaskBase):
    tags: Optional[List[str]] = []

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    due_date: Optional[datetime] = None
    estimated_duration: Optional[int] = Field(None, ge=1)
    priority: Optional[str] = Field(None, regex="^(low|medium|high|urgent)$")
    is_completed: Optional[bool] = None

class TaskResponse(TaskBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    is_completed: bool
    user_id: UUID
    
    class Config:
        orm_mode = True
```

## Usage Example

```python
from fastapi import APIRouter, Depends
from app.schemas.task import TaskCreate, TaskResponse
from app.services.task_service import TaskService

router = APIRouter()

@router.post("/tasks/", response_model=TaskResponse)
async def create_task(
    task_data: TaskCreate,  # Request body validated against TaskCreate schema
    task_service: TaskService = Depends()
):
    # TaskCreate schema validates the incoming data
    task = await task_service.create_task(task_data)
    # TaskResponse schema formats the response
    return task
```

## Development Guidelines

When creating or modifying schemas:

1. Use appropriate field types for accurate validation
2. Add validation rules to ensure data integrity
3. Include descriptive field descriptions for documentation
4. Use consistent naming conventions across schemas
5. Keep schemas focused on specific data requirements

## Related Documentation

- [Pydantic Documentation](https://docs.pydantic.dev/)
- [API Schema Design](../../docs/api_schema_design.md)
- [Validation Patterns](../../docs/validation_patterns.md) 