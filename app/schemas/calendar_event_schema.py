"""Calendar event schemas."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.enums_model import (
    EventType,
    EventPriority,
    EventStatus,
    RecurrenceType,
)


class EventSchema(BaseModel):
    """Base schema for calendar events."""

    id: Optional[UUID] = None
    user_id: Optional[UUID] = None
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    type: EventType = Field(default=EventType.OTHER)
    priority: EventPriority = Field(default=EventPriority.MEDIUM)
    status: EventStatus = Field(default=EventStatus.PENDING)
    recurrence_type: Optional[RecurrenceType] = None
    meta_data: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("end_time")
    @classmethod
    def validate_end_time(cls, v: datetime, info: Any) -> datetime:
        """Validate end time is after start time."""
        start_time = info.data.get("start_time")
        if start_time and v <= start_time:
            raise ValueError("End time must be after start time")
        return v


class EventCreateSchema(EventSchema):
    """Schema for creating calendar events."""

    user_id: UUID
    start_time: datetime
    end_time: datetime


class EventUpdateSchema(BaseModel):
    """Schema for updating calendar events."""

    title: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    type: Optional[EventType] = None
    priority: Optional[EventPriority] = None
    status: Optional[EventStatus] = None
    recurrence_type: Optional[RecurrenceType] = None
    meta_data: Optional[Dict[str, Any]] = None

    @field_validator("end_time")
    @classmethod
    def validate_end_time(cls, v: Optional[datetime], info: Any) -> Optional[datetime]:
        """Validate end time is after start time if both are provided."""
        if v is not None and info.data.get("start_time") and v <= info.data["start_time"]:
            raise ValueError("End time must be after start time")
        return v


class EventResponseSchema(EventSchema):
    """Schema for calendar event responses."""

    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EventListResponseSchema(BaseModel):
    """Schema for list of calendar events."""

    events: List[EventResponseSchema]
    total_count: int


__all__ = [
    "EventSchema",
    "EventCreateSchema",
    "EventUpdateSchema",
    "EventResponseSchema",
    "EventListResponseSchema",
]
