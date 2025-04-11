"""Productivity schemas."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator
from pydantic.config import ConfigDict

from app.models.enums_model import (
    EnergyLevel,
    FocusSessionType,
)


class ProductivitySchema(BaseModel):
    """Base schema for productivity tracking."""

    id: Optional[UUID] = None
    user_id: Optional[UUID] = None
    session_id: Optional[UUID] = None
    energy_level: EnergyLevel = Field(default=EnergyLevel.MODERATE)
    session_type: FocusSessionType = Field(default=FocusSessionType.CUSTOM)
    meta_data: Dict[str, Any] = Field(default_factory=dict)


class ProductivityCreateSchema(ProductivitySchema):
    """Schema for creating productivity records."""

    user_id: UUID


class ProductivityUpdateSchema(BaseModel):
    """Schema for updating productivity records."""

    energy_level: Optional[EnergyLevel] = None
    session_type: Optional[FocusSessionType] = None
    meta_data: Optional[Dict[str, Any]] = None


class ProductivityResponseSchema(ProductivitySchema):
    """Schema for productivity record responses."""

    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProductivityListResponseSchema(BaseModel):
    """Schema for list of productivity records."""

    records: List[ProductivityResponseSchema]
    total_count: int


class ProductivityInsights(BaseModel):
    """Schema for productivity insights data."""

    optimal_focus_times: List[Dict[str, Any]] = Field(default_factory=list)
    energy_patterns: Dict[str, Any] = Field(default_factory=dict)
    recommendations: List[str] = Field(default_factory=list)
    focus_session_stats: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)


# Alias for backward compatibility
ProductivityInsightsSchema = ProductivityInsights


__all__ = [
    "ProductivitySchema",
    "ProductivityCreateSchema",
    "ProductivityUpdateSchema",
    "ProductivityResponseSchema",
    "ProductivityListResponseSchema",
    "ProductivityInsights",
    "ProductivityInsightsSchema",
]
