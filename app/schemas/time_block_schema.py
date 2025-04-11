"""Time block schemas."""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.enums_model import BlockType, TaskPriority


class TimeBlock(BaseModel):
    """Base schema for time blocks."""

    id: Optional[UUID] = None
    user_id: Optional[UUID] = None
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    type: BlockType = Field(default=BlockType.TASK)
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM)
    meta_data: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("end_time")
    @classmethod
    def validate_end_time(cls, v: datetime, info: Any) -> datetime:
        """Validate end time is after start time."""
        if info.data.get("start_time") and v <= info.data["start_time"]:
            raise ValueError("End time must be after start time")
        return v


class TimeBlockCreate(TimeBlock):
    """Schema for creating time blocks."""

    user_id: UUID
    start_time: datetime
    end_time: datetime


class TimeBlockUpdate(BaseModel):
    """Schema for updating time blocks."""

    title: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    type: Optional[BlockType] = None
    priority: Optional[TaskPriority] = None
    meta_data: Optional[Dict[str, Any]] = None

    @field_validator("end_time")
    @classmethod
    def validate_end_time(cls, v: Optional[datetime], info: Any) -> Optional[datetime]:
        """Validate end time is after start time if both are provided."""
        if v is not None and info.data.get("start_time") and v <= info.data["start_time"]:
            raise ValueError("End time must be after start time")
        return v


class TimeBlockResponse(TimeBlock):
    """Schema for time block responses."""

    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TimeBlockListResponse(BaseModel):
    """Schema for list of time blocks."""

    blocks: List[TimeBlockResponse]
    total_count: int


class TimePreferences(BaseModel):
    """Schema for user time management preferences."""

    user_id: UUID
    preferred_start_time: Optional[datetime] = None
    preferred_end_time: Optional[datetime] = None
    preferred_break_intervals: List[timedelta] = Field(default_factory=list)
    preferred_focus_duration: timedelta = Field(default=timedelta(minutes=50))
    allow_notifications: bool = True
    preferred_task_types: List[str] = Field(default_factory=list)

    @field_validator("preferred_end_time")
    @classmethod
    def validate_preferred_end_time(cls, v: Optional[datetime], info: Any) -> Optional[datetime]:
        """Validate preferred end time is after preferred start time if both are provided."""
        if (
            v is not None
            and info.data.get("preferred_start_time")
            and v <= info.data["preferred_start_time"]
        ):
            raise ValueError("Preferred end time must be after preferred start time")
        return v


class TimeAnalytics(BaseModel):
    """Schema for analyzing time block usage."""

    user_id: UUID
    total_blocks: int
    total_time_spent: timedelta
    avg_time_per_block: Optional[timedelta] = None
    most_common_block_type: Optional[str] = None
    priority_distribution: Dict[str, int] = Field(default_factory=dict)
    active_days: List[str] = Field(default_factory=list)  # List of active days in a week
    productivity_score: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)


__all__ = [
    "TimeBlock",
    "TimeBlockCreate",
    "TimeBlockUpdate",
    "TimeBlockResponse",
    "TimeBlockListResponse",
    "TimePreferences",
    "TimeAnalytics",
]
