"""Mental health schemas."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class MentalHealthLogBaseSchema(BaseModel):
    """Base schema for mental health logs"""

    user_id: UUID
    mood_score: int = Field(..., ge=1, le=10, description="Mood score from 1-10")
    stress_level: int = Field(..., ge=1, le=10, description="Stress level from 1-10")
    anxiety_level: int = Field(..., ge=1, le=10, description="Anxiety level from 1-10")
    notes: Optional[str] = Field(None, description="Additional notes or context")
    energy_level: Optional[int] = Field(None, ge=1, le=10, description="Energy level from 1-10")
    sleep_quality: Optional[int] = Field(None, ge=1, le=10, description="Sleep quality from 1-10")
    activity_log: Optional[List[str]] = Field(None, description="List of activities during this period")

    model_config = ConfigDict(from_attributes=True)

    @field_validator("mood_score", "stress_level", "anxiety_level", "energy_level", "sleep_quality")
    def validate_scores(cls, v: Optional[int], info: Dict[str, Any]) -> Optional[int]:
        if v is not None and not 1 <= v <= 10:
            raise ValueError(f"{info.field_name} must be between 1 and 10")
        return v


class MentalHealthLogCreateSchema(MentalHealthLogBaseSchema):
    """Schema for creating a mental health log"""

    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When this log was created")


class MentalHealthLogUpdateSchema(BaseModel):
    """Schema for updating a mental health log"""

    mood_score: Optional[int] = Field(None, ge=1, le=10, description="Updated mood score")
    stress_level: Optional[int] = Field(None, ge=1, le=10, description="Updated stress level")
    anxiety_level: Optional[int] = Field(None, ge=1, le=10, description="Updated anxiety level")
    notes: Optional[str] = Field(None, description="Updated notes")
    energy_level: Optional[int] = Field(None, ge=1, le=10, description="Updated energy level")
    sleep_quality: Optional[int] = Field(None, ge=1, le=10, description="Updated sleep quality")
    activity_log: Optional[List[str]] = Field(None, description="Updated activity log")

    model_config = ConfigDict(from_attributes=True)

    @field_validator("mood_score", "stress_level", "anxiety_level", "energy_level", "sleep_quality")
    def validate_scores(cls, v: Optional[int], info: Dict[str, Any]) -> Optional[int]:
        if v is not None and not 1 <= v <= 10:
            raise ValueError(f"{info.field_name} must be between 1 and 10")
        return v


class MentalHealthLogResponseSchema(MentalHealthLogBaseSchema):
    """Schema for mental health log response"""

    id: UUID
    created_at: datetime
    updated_at: datetime
    sentiment_score: Optional[float] = Field(None, description="Analyzed sentiment score")


class MentalHealthStatsSchema(BaseModel):
    """Schema for mental health statistics."""

    user_id: UUID
    total_logs: int = Field(..., description="Total number of logs")
    average_mood: float = Field(..., description="Average mood score")
    average_stress: float = Field(..., description="Average stress level")
    average_anxiety: float = Field(..., description="Average anxiety level")
    average_energy: Optional[float] = Field(None, description="Average energy level")
    average_sleep: Optional[float] = Field(None, description="Average sleep quality")
    most_common_activities: List[str] = Field(default_factory=list, description="Most frequent activities")
    last_log_date: Optional[datetime] = Field(None, description="Date of the last log")
    streak_days: Optional[int] = Field(None, description="Current streak of consecutive days with logs")
    improvement_areas: List[str] = Field(default_factory=list, description="Areas needing improvement")
    progress_indicators: Dict[str, Any] = Field(default_factory=dict, description="Progress indicators")

    model_config = ConfigDict(from_attributes=True)


class MentalHealthInsightsSchema(BaseModel):
    """Schema for mental health insights"""

    mood_average: float = Field(..., description="Average mood score over the period")
    stress_average: float = Field(..., description="Average stress level over the period")
    anxiety_average: float = Field(..., description="Average anxiety level over the period")
    energy_average: Optional[float] = Field(None, description="Average energy level over the period")
    sleep_quality_average: Optional[float] = Field(None, description="Average sleep quality over the period")
    common_activities: Optional[List[str]] = Field(None, description="Most common activities logged")
    recommendations: List[str] = Field(..., description="Personalized recommendations")
    stress_indicators: List[str] = Field(..., description="Identified stress indicators")

    model_config = ConfigDict(from_attributes=True)


class MentalHealthTrendsSchema(BaseModel):
    """Schema for mental health trends"""

    period: str = Field(..., description="Time period for the trends")
    mood_trend: List[Dict[str, Any]] = Field(..., description="Mood score trends")
    stress_trend: List[Dict[str, Any]] = Field(..., description="Stress level trends")
    anxiety_trend: List[Dict[str, Any]] = Field(..., description="Anxiety level trends")
    energy_trend: Optional[List[Dict[str, Any]]] = Field(None, description="Energy level trends")
    correlations: Optional[List[Dict[str, Any]]] = Field(None, description="Identified correlations")

    model_config = ConfigDict(from_attributes=True)


class ActivityCorrelationSchema(BaseModel):
    """Schema for activity correlations"""

    activity: str = Field(..., description="Activity name")
    mood_correlation: float = Field(..., description="Correlation with mood")
    stress_correlation: float = Field(..., description="Correlation with stress")
    anxiety_correlation: float = Field(..., description="Correlation with anxiety")
    energy_correlation: Optional[float] = Field(None, description="Correlation with energy")
    sample_size: int = Field(..., description="Number of samples used")
    last_updated: datetime = Field(..., description="When correlation was last computed")

    model_config = ConfigDict(from_attributes=True)


__all__ = [
    "MentalHealthLogBaseSchema",
    "MentalHealthLogCreateSchema",
    "MentalHealthLogUpdateSchema",
    "MentalHealthLogResponseSchema",
    "MentalHealthStatsSchema",
    "MentalHealthInsightsSchema",
    "MentalHealthTrendsSchema",
    "ActivityCorrelationSchema",
]
