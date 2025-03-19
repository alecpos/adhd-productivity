"""Calendar schemas module."""

from datetime import datetime, time
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.base_schema import BaseSchema, TimestampedSchema


class CalendarType(str, Enum):
    """Calendar type enum."""
    PERSONAL = "personal"
    WORK = "work"
    SHARED = "shared"


class EventType(str, Enum):
    """Event type enum."""
    MEETING = "meeting"
    TASK = "task"
    REMINDER = "reminder"
    APPOINTMENT = "appointment"
    BREAK = "break"
    OTHER = "other"


class EventPriority(str, Enum):
    """Event priority enum."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class EventStatus(str, Enum):
    """Event status enum."""
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class RecurrencePattern(str, Enum):
    """Event recurrence patterns."""
    DAILY = "daily"
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"
    CUSTOM = "custom"


class CalendarSchema(BaseSchema):
    """Base schema for calendar."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    type: CalendarType = Field(default=CalendarType.PERSONAL)
    color_code: Optional[str] = Field(None, pattern="^#[0-9a-fA-F]{6}$")
    is_default: bool = False

    model_config = ConfigDict(from_attributes=True)


class WorkingHoursSchema(BaseSchema):
    """Schema for working hours."""
    start: time
    end: time
    time_zone: str = "UTC"

    model_config = ConfigDict(from_attributes=True)


class CalendarEventSchema(TimestampedSchema):
    """Base schema for calendar events."""
    id: UUID
    user_id: UUID
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    start_time: datetime
    end_time: datetime
    event_type: EventType = EventType.OTHER
    priority: EventPriority = EventPriority.MEDIUM
    status: EventStatus = EventStatus.SCHEDULED
    location: Optional[str] = Field(None, max_length=200)
    is_recurring: bool = False
    recurrence_pattern: Optional[RecurrencePattern] = None
    calendar_type: CalendarType = CalendarType.PERSONAL
    metadata: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)


class CalendarEventCreateSchema(BaseSchema):
    """Schema for creating calendar events."""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    start_time: datetime
    end_time: datetime
    event_type: EventType = EventType.OTHER
    priority: EventPriority = EventPriority.MEDIUM
    location: Optional[str] = Field(None, max_length=200)
    is_recurring: bool = False
    recurrence_pattern: Optional[RecurrencePattern] = None
    calendar_type: CalendarType = CalendarType.PERSONAL
    metadata: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)


class CalendarEventUpdateSchema(BaseSchema):
    """Schema for updating calendar events."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    event_type: Optional[EventType] = None
    priority: Optional[EventPriority] = None
    status: Optional[EventStatus] = None
    location: Optional[str] = Field(None, max_length=200)
    is_recurring: Optional[bool] = None
    recurrence_pattern: Optional[RecurrencePattern] = None
    calendar_type: Optional[CalendarType] = None
    metadata: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)


class CalendarEventResponseSchema(BaseSchema):
    """Schema for calendar event responses."""
    success: bool
    message: str
    data: CalendarEventSchema

    model_config = ConfigDict(from_attributes=True)


class CalendarEventListResponseSchema(BaseSchema):
    """Schema for calendar event list responses."""
    success: bool
    message: str
    data: List[CalendarEventSchema]

    model_config = ConfigDict(from_attributes=True)


class CalendarStatsSchema(BaseSchema):
    """Schema for calendar statistics."""
    total_events: int
    upcoming_events: int
    events_this_week: int
    events_this_month: int
    most_common_type: EventType
    busiest_day: str
    average_duration: float


class CalendarSettingsSchema(BaseSchema):
    """Schema for calendar settings."""
    default_view: str = "week"
    start_of_week: int = Field(0, ge=0, le=6)  # 0 = Sunday, 6 = Saturday
    working_hours: WorkingHoursSchema
    default_event_duration: int = Field(60, ge=1)  # minutes
    default_reminder_time: int = Field(15, ge=0)  # minutes
    time_zone: str = "UTC"
    display_weekends: bool = True
    default_calendar_color: str = Field("#4A90E2", pattern="^#[0-9a-fA-F]{6}$")


__all__ = [
    "CalendarType",
    "EventType",
    "EventPriority",
    "EventStatus",
    "RecurrencePattern",
    "CalendarSchema",
    "WorkingHoursSchema",
    "CalendarEventSchema",
    "CalendarEventCreateSchema",
    "CalendarEventUpdateSchema",
    "CalendarEventResponseSchema",
    "CalendarEventListResponseSchema",
    "CalendarStatsSchema",
    "CalendarSettingsSchema",
]
