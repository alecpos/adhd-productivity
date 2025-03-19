"""Energy tracking and analysis schemas."""

from datetime import datetime, time
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import Field

from app.schemas.base_schema import BaseSchema
from app.schemas.shared_components_schema import (
    Break,
    EnvironmentalFactors,
    Interruption,
    SessionAnalytics
)


class EnergyLog(BaseSchema):
    """Base energy log model."""

    timestamp: datetime
    energy_level: int = Field(..., ge=1, le=10)
    focus_level: int = Field(..., ge=1, le=10)
    mood: Optional[int] = Field(None, ge=1, le=10)
    stress_level: Optional[int] = Field(None, ge=1, le=10)
    notes: Optional[str] = None
    activity: Optional[str] = None
    environment: Optional[EnvironmentalFactors] = None
    breaks_taken: Optional[List[Break]] = None
    interruptions: Optional[List[Interruption]] = None
    meta_data: Optional[Dict[str, Any]] = None


class EnergyLogCreate(EnergyLog):
    """Schema for creating energy logs."""

    task_id: Optional[UUID] = None
    calendar_event_id: Optional[UUID] = None


class EnergyLogUpdate(EnergyLog):
    """Schema for updating energy logs."""

    pass


class EnergyLogResponse(EnergyLog):
    """Schema for energy log responses."""

    id: UUID
    user_id: UUID
    task_id: Optional[UUID]
    calendar_event_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime


class EnergyLogListResponse(BaseSchema):
    """Schema for energy log list responses."""

    logs: List[EnergyLogResponse]
    total: int
    page: int
    page_size: int
    stats: Optional["EnergyStats"] = None


class EnergyAnalysisPattern(BaseSchema):
    """Energy pattern model for analysis."""

    time_of_day: time
    average_energy: int = Field(..., ge=1, le=10)
    average_focus: int = Field(..., ge=1, le=10)
    common_activities: List[str] = Field(default_factory=list)
    effective_breaks: List[Break] = Field(default_factory=list)
    optimal_recovery_activities: List[str] = Field(default_factory=list)
    environmental_preferences: Optional[EnvironmentalFactors] = None


class PeakHours(BaseSchema):
    """Peak hours model."""

    start_time: time
    end_time: time
    average_energy: float = Field(..., ge=1, le=10)
    average_focus: float = Field(..., ge=1, le=10)
    optimal_activities: List[str] = Field(default_factory=list)
    environmental_factors: Optional[EnvironmentalFactors] = None


class WeeklyTrends(BaseSchema):
    """Weekly energy trends model."""

    day_of_week: int = Field(..., ge=0, le=6)  # 0 = Monday, 6 = Sunday
    peak_hours: List[PeakHours]
    average_energy: float = Field(..., ge=1, le=10)
    average_focus: float = Field(..., ge=1, le=10)
    common_activities: List[str] = Field(default_factory=list)
    optimal_break_patterns: List[Break] = Field(default_factory=list)
    environmental_preferences: Optional[EnvironmentalFactors] = None


class EnergyPatterns(BaseSchema):
    """Schema for energy pattern analysis."""

    daily_patterns: Dict[str, List[Dict[str, Any]]] = Field(
        ...,
        description="Energy patterns by day of week"
    )
    hourly_patterns: Dict[str, List[Dict[str, Any]]] = Field(
        ...,
        description="Energy patterns by hour of day"
    )
    activity_patterns: Dict[str, Dict[str, float]] = Field(
        ...,
        description="Energy levels by activity type"
    )
    peak_hours: List[time] = Field(
        ...,
        description="Hours with highest average energy levels"
    )
    low_hours: List[time] = Field(
        ...,
        description="Hours with lowest average energy levels"
    )
    optimal_break_times: List[Dict[str, Any]] = Field(
        ...,
        description="Suggested break times based on energy patterns"
    )
    focus_correlation: float = Field(
        ...,
        description="Correlation between energy and focus levels",
        ge=-1,
        le=1
    )
    environmental_impacts: Dict[str, float] = Field(
        ...,
        description="Impact of environmental factors on energy levels"
    )
    recommendations: List[str] = Field(
        ...,
        description="Personalized recommendations based on patterns"
    )


class EnergyPatternsSchema(BaseSchema):
    """Schema for energy pattern analysis response."""

    patterns: EnergyPatterns
    analytics: SessionAnalytics
    meta_data: Optional[Dict[str, Any]] = None


class EnergyStats(BaseSchema):
    """Energy statistics model."""

    average_energy: float = Field(..., ge=1, le=10)
    average_focus: float = Field(..., ge=1, le=10)
    energy_stability: float = Field(..., ge=0, le=1)
    focus_stability: float = Field(..., ge=0, le=1)
    peak_performance_duration: int  # minutes
    recovery_effectiveness: float = Field(..., ge=0, le=1)
    break_effectiveness: float = Field(..., ge=0, le=1)
    interruption_impact: float = Field(..., ge=-1, le=0)
    environment_impact_scores: Dict[str, float]
    activity_correlations: Dict[str, float]
    period_start: datetime
    period_end: datetime
    meta_data: Optional[Dict[str, Any]] = None


class EnergyInsights(BaseSchema):
    """Energy insights model."""

    optimal_schedule_recommendations: List[Dict[str, Any]]
    break_pattern_recommendations: List[Dict[str, Any]]
    environment_optimization_tips: List[str]
    activity_scheduling_suggestions: List[Dict[str, Any]]
    focus_improvement_strategies: List[str]
    energy_management_tips: List[str]
    period_start: datetime
    period_end: datetime
    meta_data: Optional[Dict[str, Any]] = None


class EnergyLogCreateSchema(EnergyLogCreate):
    """Alias for EnergyLogCreate for consistent naming."""
    pass


class EnergyLogResponseSchema(EnergyLogResponse):
    """Alias for EnergyLogResponse for consistent naming."""
    pass


__all__ = [
    "EnergyLogBase",
    "EnergyLogCreate",
    "EnergyLogUpdate",
    "EnergyLogResponse",
    "EnergyLogListResponse",
    "EnergyAnalysisPattern",
    "PeakHours",
    "WeeklyTrends",
    "EnergyPatterns",
    "EnergyStats",
    "EnergyInsights",
    "EnergyPatternsSchema",
    "EnergyLogCreateSchema",
    "EnergyLogResponseSchema"
]
