"""Task schemas."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import Field

from app.models.enums_model import BlockType, BlockPriority, TaskStatus
from app.schemas.base_schema import BaseSchema
from app.schemas.shared_components_schema import (
    Break,
    EnvironmentalFactors,
    Interruption,
    SessionAnalytics
)
from app.utils.validation import (
    BaseModelWithValidators,
    validate_dependent_fields,
    validate_at_least_one_field_present
)


class TaskSchema(BaseModelWithValidators):
    """Base task model."""

    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=500)
    due_date: Optional[datetime] = None
    estimated_duration: int = Field(..., ge=1)  # minutes
    priority: BlockPriority = Field(default=BlockPriority.MEDIUM)
    status: TaskStatus = Field(default=TaskStatus.TODO)
    block_type: BlockType = Field(default=BlockType.TASK)
    
    # Task requirements
    energy_requirement: Optional[int] = Field(None, ge=1, le=10)
    focus_requirement: Optional[int] = Field(None, ge=1, le=10)
    environmental_requirements: Optional[EnvironmentalFactors] = None
    
    # Scheduling preferences
    preferred_time: Optional[datetime] = None
    is_flexible: bool = True
    buffer_before: Optional[int] = Field(None, ge=0)  # minutes
    buffer_after: Optional[int] = Field(None, ge=0)  # minutes
    
    # Progress tracking
    progress: Optional[float] = Field(None, ge=0, le=1)
    completed_subtasks: Optional[List[str]] = None
    time_spent: Optional[int] = Field(None, ge=0)  # minutes
    completion_date: Optional[datetime] = None
    
    # Performance tracking
    analytics: Optional[SessionAnalytics] = None
    breaks: Optional[List[Break]] = None
    interruptions: Optional[List[Interruption]] = None
    
    # Additional metadata
    parent_task_id: Optional[UUID] = None
    subtask_ids: Optional[List[UUID]] = None
    dependencies: Optional[List[UUID]] = None
    tags: Optional[List[str]] = None
    location: Optional[str] = None
    meta_data: Optional[Dict[str, Any]] = None
    
    # Validation: If status is "COMPLETED", completion_date should be present
    _validate_completion = validate_dependent_fields(
        "status", 
        ["completion_date"], 
        check_value=TaskStatus.COMPLETED
    )
    
    # Validation: If breaks are specified, analytics should also be present
    _validate_analytics = validate_dependent_fields(
        "breaks", 
        ["analytics"]
    )
    
    # Validation: Either preferred_time or is_flexible must be provided
    _validate_scheduling = validate_at_least_one_field_present(
        ["preferred_time", "is_flexible"]
    )


class TaskCreate(TaskSchema):
    """Schema for creating tasks."""

    calendar_event_id: Optional[UUID] = None


class TaskUpdate(BaseModelWithValidators):
    """Schema for updating tasks.
    
    Unlike TaskCreate, all fields are optional for updates.
    """

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=500)
    due_date: Optional[datetime] = None
    estimated_duration: Optional[int] = Field(None, ge=1)  # minutes
    priority: Optional[BlockPriority] = None
    status: Optional[TaskStatus] = None
    block_type: Optional[BlockType] = None
    
    # Task requirements
    energy_requirement: Optional[int] = Field(None, ge=1, le=10)
    focus_requirement: Optional[int] = Field(None, ge=1, le=10)
    environmental_requirements: Optional[EnvironmentalFactors] = None
    
    # Scheduling preferences
    preferred_time: Optional[datetime] = None
    is_flexible: Optional[bool] = None
    buffer_before: Optional[int] = Field(None, ge=0)  # minutes
    buffer_after: Optional[int] = Field(None, ge=0)  # minutes
    
    # Progress tracking
    progress: Optional[float] = Field(None, ge=0, le=1)
    completed_subtasks: Optional[List[str]] = None
    time_spent: Optional[int] = Field(None, ge=0)  # minutes
    completion_date: Optional[datetime] = None
    
    # Performance tracking
    analytics: Optional[SessionAnalytics] = None
    breaks: Optional[List[Break]] = None
    interruptions: Optional[List[Interruption]] = None
    
    # Additional metadata
    parent_task_id: Optional[UUID] = None
    subtask_ids: Optional[List[UUID]] = None
    dependencies: Optional[List[UUID]] = None
    tags: Optional[List[str]] = None
    location: Optional[str] = None
    meta_data: Optional[Dict[str, Any]] = None
    calendar_event_id: Optional[UUID] = None
    
    # Validation: If status is updated to "COMPLETED", completion_date should be present
    _validate_completion = validate_dependent_fields(
        "status", 
        ["completion_date"], 
        check_value=TaskStatus.COMPLETED
    )
    
    # Validation: If breaks are specified, analytics should also be present
    _validate_analytics = validate_dependent_fields(
        "breaks", 
        ["analytics"]
    )


class TaskResponse(TaskSchema):
    """Schema for task responses."""

    id: UUID
    user_id: UUID
    calendar_event_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime


class TaskStatsSchema(BaseModelWithValidators):
    """Task statistics model."""

    total_tasks: int
    completed_tasks: int
    overdue_tasks: int
    average_completion_time: float = Field(..., ge=0)  # minutes
    completion_rate: float = Field(..., ge=0, le=1)
    average_energy_level: Optional[float] = Field(None, ge=1, le=10)
    average_focus_level: Optional[float] = Field(None, ge=1, le=10)
    task_distribution: Dict[TaskStatus, int]
    priority_distribution: Dict[BlockPriority, int]
    optimal_completion_times: List[Dict[str, Any]]
    common_interruptions: List[Dict[str, int]]
    period_start: datetime
    period_end: datetime
    meta_data: Optional[Dict[str, Any]] = None


class TaskListResponse(BaseModelWithValidators):
    """Schema for task list responses."""

    tasks: List[TaskResponse]
    total: int
    page: int = Field(..., ge=1)
    page_size: int = Field(..., ge=1, le=100)
    stats: Optional[TaskStatsSchema] = None


__all__ = [
    "TaskSchema",
    "TaskCreate",
    "TaskUpdate",
    "TaskResponse",
    "TaskStatsSchema",
    "TaskListResponse"
]
