"""Pomodoro schemas."""

from datetime import datetime
from typing import Any, Dict, Optional, List
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.models.enums_model import PomodoroStatus, BreakType


class SessionStatusSchema(BaseModel):
    """Schema for session status."""

    status: str
    time_remaining: int
    current_session: int
    total_sessions: int
    break_type: Optional[str] = None
    cycles_completed: int
    next_break_duration: Optional[int] = None
    is_long_break_due: bool = False

    model_config = ConfigDict(from_attributes=True)


class SessionAnalyticsSchema(BaseModel):
    """Schema for session analytics."""

    total_sessions: int
    completed_sessions: int
    total_focus_time: int
    average_productivity: float
    productivity_trend: str
    distraction_trend: str
    completion_rate: float

    model_config = ConfigDict(from_attributes=True)


class PomodoroSchema(BaseModel):
    """Base schema for pomodoro sessions."""

    id: Optional[UUID] = None
    user_id: Optional[UUID] = None
    duration: int = Field(default=25, ge=10, le=60, description="Focus time duration in minutes")
    break_duration: int = Field(default=5, ge=3, le=30, description="Break time duration in minutes")
    cycles: int = Field(default=4, ge=1, le=10, description="Number of Pomodoro rounds")
    current_cycle: int = Field(default=1)
    status: PomodoroStatus = Field(default=PomodoroStatus.PENDING)
    meta_data: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("duration")
    def validate_duration(cls, v: int) -> int:
        """Validate duration is within reasonable limits."""
        if not 10 <= v <= 60:
            raise ValueError("Duration must be between 10 and 60 minutes")
        return v

    @model_validator(mode="after")
    def validate_cycles_and_times(self) -> "PomodoroSchema":
        """Validate cycles and time relationships."""
        if self.current_cycle > self.cycles:
            raise ValueError("Current cycle cannot be greater than total cycles")
        if self.break_duration >= self.duration:
            raise ValueError("Break duration must be less than focus duration")
        return self


class PomodoroCreateSchema(PomodoroSchema):
    """Schema for creating pomodoro sessions."""

    user_id: UUID
    task_id: Optional[UUID] = Field(None, description="Associated task ID")
    start_time: datetime = Field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    notes: Optional[str] = None


class PomodoroUpdateSchema(BaseModel):
    """Schema for updating pomodoro sessions."""

    duration: Optional[int] = Field(None, ge=10, le=60, description="Focus time duration")
    break_duration: Optional[int] = Field(None, ge=3, le=30, description="Break time duration")
    cycles: Optional[int] = Field(None, ge=1, le=10, description="Number of rounds")
    current_cycle: Optional[int] = None
    status: Optional[PomodoroStatus] = None
    productivity_score: Optional[int] = Field(
        None, description="Session productivity score", ge=1, le=10
    )
    focus_level: Optional[int] = Field(None, description="Session focus level", ge=1, le=10)
    notes: Optional[str] = Field(None, description="Session notes")

    @field_validator("productivity_score", "focus_level")
    def validate_scores(cls, v: Optional[int], info: Dict[str, Any]) -> Optional[int]:
        if v is not None and (not 1 <= v <= 10):
            raise ValueError(f"{info.field_name} must be between 1 and 10")
        return v

    @field_validator("status")
    def validate_status(cls, v: Optional[PomodoroStatus]) -> Optional[PomodoroStatus]:
        if v is not None:
            valid_statuses = [status for status in PomodoroStatus]
            if v not in valid_statuses:
                raise ValueError(f"Status must be one of {[s.value for s in valid_statuses]}")
        return v


class PomodoroResponseSchema(PomodoroSchema):
    """Schema for pomodoro session responses."""

    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    completed_cycles: Optional[int] = Field(None, ge=0)
    total_focus_time: Optional[int] = Field(None, ge=0)
    success_rate: Optional[float] = Field(None, ge=0, le=1)
    productivity_score: Optional[int] = Field(None, description="Session productivity score")
    focus_level: Optional[int] = Field(None, description="Session focus level")
    notes: Optional[str] = Field(None, description="Session notes")

    model_config = ConfigDict(from_attributes=True)


class PomodoroStatsSchema(BaseModel):
    """Schema for Pomodoro session statistics."""

    total_sessions: int = Field(..., description="Total number of Pomodoro sessions")
    total_duration: int = Field(..., description="Total duration of all sessions in minutes")
    average_duration: float = Field(..., description="Average session duration in minutes")
    completion_rate: float = Field(..., description="Percentage of completed sessions")


class PomodoroSettingsSchema(BaseModel):
    """Schema for customizing default Pomodoro settings."""

    default_duration: Optional[int] = Field(None, ge=10, le=60, description="Default focus time in minutes")
    default_break_duration: Optional[int] = Field(None, ge=3, le=30, description="Default break time in minutes")
    default_cycles: Optional[int] = Field(None, ge=1, le=10, description="Default number of rounds")
    long_break_interval: Optional[int] = Field(None, ge=2, le=6, description="Number of cycles before long break")
    long_break_duration: Optional[int] = Field(None, ge=10, le=45, description="Long break duration in minutes")

    model_config = ConfigDict(from_attributes=True)


class PomodoroCustomizationSchema(BaseModel):
    """Schema for temporary session customization."""

    duration: int = Field(..., ge=10, le=60, description="Customized focus time")
    break_duration: int = Field(..., ge=3, le=30, description="Customized break time")
    cycles: int = Field(..., ge=1, le=10, description="Customized number of rounds")
    message: str = Field(..., description="Customization confirmation message")

    model_config = ConfigDict(from_attributes=True)


__all__ = [
    "PomodoroStatus",
    "PomodoroSchema",
    "PomodoroCreateSchema",
    "PomodoroUpdateSchema",
    "PomodoroResponseSchema",
    "PomodoroStatsSchema",
    "PomodoroSettingsSchema",
    "PomodoroCustomizationSchema",
    "SessionStatusSchema",
    "SessionAnalyticsSchema",
]
