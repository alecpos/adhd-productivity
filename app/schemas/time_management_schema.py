"""Time management schemas."""

from datetime import datetime, time
from enum import Enum, IntEnum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import Field

from app.models.enums_model import BlockType, BlockPriority
from app.schemas.base_schema import BaseSchema
from app.schemas.shared_components_schema import (
    Break,
    EnvironmentalFactors,
    Interruption,
    SessionAnalytics
)


class WorkHoursSchema(BaseSchema):
    """Work hours configuration."""

    start: time = Field(default=time(9, 0))  # 9 AM default
    end: time = Field(default=time(17, 0))  # 5 PM default
    breaks: List[Dict[str, time]] = Field(default_factory=list)


class PomodoroStatus(str, Enum):
    """Pomodoro status enum."""

    ACTIVE = "active"
    ON_BREAK = "on_break"
    COMPLETED = "completed"
    INTERRUPTED = "interrupted"
    CANCELLED = "cancelled"


class BreakType(str, Enum):
    """Break type enum."""

    SHORT = "short"
    LONG = "long"
    FLEXIBLE = "flexible"
    EMERGENCY = "emergency"


class TimeManagementBlockBase(BaseSchema):
    """Base time management block model with extended tracking."""

    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=500)
    start_time: datetime
    end_time: datetime
    block_type: BlockType
    priority: BlockPriority = Field(default=BlockPriority.MEDIUM)

    # Flexibility settings
    is_break: bool = False
    is_flexible: bool = True
    buffer_before: Optional[int] = Field(None, ge=0)  # minutes
    buffer_after: Optional[int] = Field(None, ge=0)  # minutes

    # Performance metrics
    energy_level: Optional[int] = Field(None, ge=1, le=10)
    focus_level: Optional[int] = Field(None, ge=1, le=10)
    mental_health_score: Optional[int] = Field(None, ge=1, le=10)
    completion_rate: Optional[float] = Field(None, ge=0, le=1)
    effectiveness_score: Optional[float] = Field(None, ge=0, le=1)

    # Time tracking
    actual_start_time: Optional[datetime] = None
    actual_end_time: Optional[datetime] = None
    total_focus_time: Optional[int] = Field(None, ge=0)  # minutes
    total_break_time: Optional[int] = Field(None, ge=0)  # minutes

    # Additional tracking
    interruptions: Optional[List[Interruption]] = None
    break_intervals: Optional[List[Break]] = None
    environment_data: Optional[EnvironmentalFactors] = None
    location: Optional[str] = None
    tags: Optional[List[str]] = None
    meta_data: Optional[Dict[str, Any]] = None


class TimeManagementBlockCreate(TimeManagementBlockBase):
    """Schema for creating time management blocks."""

    task_id: Optional[UUID] = None
    calendar_event_id: Optional[UUID] = None


class TimeManagementBlockUpdate(TimeManagementBlockBase):
    """Schema for updating time management blocks."""

    pass


class TimeManagementBlockResponse(TimeManagementBlockBase):
    """Schema for time management block responses."""

    id: UUID
    user_id: UUID
    task_id: Optional[UUID]
    calendar_event_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime


class PomodoroSessionBase(BaseSchema):
    """Base pomodoro session model."""

    # Basic session info
    start_time: datetime
    end_time: Optional[datetime] = None
    status: PomodoroStatus = Field(default=PomodoroStatus.ACTIVE)

    # Time settings
    work_duration: int = Field(default=25, ge=1)  # minutes
    short_break_duration: int = Field(default=5, ge=1)  # minutes
    long_break_duration: int = Field(default=15, ge=1)  # minutes
    sessions_until_long_break: int = Field(default=4, ge=1)

    # Session tracking
    completed_sessions: int = Field(default=0, ge=0)
    completed: bool = False
    current_session: int = Field(default=1, ge=1)

    # Performance metrics
    analytics: Optional[SessionAnalytics] = None

    # Break tracking
    breaks_taken: Optional[List[Break]] = None
    total_break_time: Optional[int] = Field(None, ge=0)
    break_adherence: Optional[float] = Field(None, ge=0, le=1)
    current_break_type: Optional[BreakType] = None

    # Additional tracking
    interruptions: Optional[List[Interruption]] = None
    task_progress: Optional[float] = Field(None, ge=0, le=1)
    completed_subtasks: Optional[List[str]] = None
    environment_data: Optional[EnvironmentalFactors] = None
    location: Optional[str] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None
    meta_data: Optional[Dict[str, Any]] = None


class PomodoroSessionCreate(PomodoroSessionBase):
    """Schema for creating pomodoro sessions."""

    task_id: Optional[UUID] = None


class PomodoroSessionUpdate(PomodoroSessionBase):
    """Schema for updating pomodoro sessions."""

    pass


class PomodoroSessionResponse(PomodoroSessionBase):
    """Schema for pomodoro session responses."""

    id: UUID
    user_id: UUID
    task_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime


class TimeManagementStats(BaseSchema):
    """Time management statistics model."""

    total_blocks: int
    total_focus_time: int  # minutes
    total_break_time: int  # minutes
    average_effectiveness: float
    block_type_distribution: Dict[BlockType, int]
    optimal_focus_periods: List[Dict[str, Any]]
    optimal_break_patterns: List[Dict[str, Any]]
    productivity_by_time: Dict[str, float]
    interruption_patterns: List[Dict[str, Any]]
    environment_correlations: Dict[str, float]
    updated_at: datetime


class TimeManagementTrends(BaseSchema):
    """Time management trends model."""

    focus_trends: List[Dict[str, Any]]
    effectiveness_trends: List[Dict[str, Any]]
    break_pattern_trends: List[Dict[str, Any]]
    interruption_trends: List[Dict[str, Any]]
    energy_level_trends: List[Dict[str, Any]]
    period_start: datetime
    period_end: datetime
    updated_at: datetime


__all__ = [
    "WorkHoursSchema",
    "PomodoroStatus",
    "BreakType",
    "TimeManagementBlockBase",
    "TimeManagementBlockCreate",
    "TimeManagementBlockUpdate",
    "TimeManagementBlockResponse",
    "PomodoroSessionBase",
    "PomodoroSessionCreate",
    "PomodoroSessionUpdate",
    "PomodoroSessionResponse",
    "TimeManagementStats",
    "TimeManagementTrends",
]
