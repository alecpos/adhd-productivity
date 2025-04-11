"""Calendar sync schemas."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

from app.models.enums_model import (
    SyncSource,
    SyncStatus,
    ConflictResolutionStrategy,
    SyncDirection,
)


class CalendarSyncSchema(BaseModel):
    """Base schema for calendar sync."""

    id: Optional[UUID] = None
    user_id: Optional[UUID] = None
    source: SyncSource = Field(default=SyncSource.LOCAL)
    status: SyncStatus = Field(default=SyncStatus.PENDING)
    direction: SyncDirection = Field(default=SyncDirection.BIDIRECTIONAL)
    conflict_resolution: ConflictResolutionStrategy = Field(
        default=ConflictResolutionStrategy.MANUAL
    )
    meta_data: Dict[str, Any] = Field(default_factory=dict)


class CalendarSyncCreateSchema(CalendarSyncSchema):
    """Schema for creating calendar sync."""

    user_id: UUID


class CalendarSyncUpdateSchema(BaseModel):
    """Schema for updating calendar sync."""

    source: Optional[SyncSource] = None
    status: Optional[SyncStatus] = None
    direction: Optional[SyncDirection] = None
    conflict_resolution: Optional[ConflictResolutionStrategy] = None
    meta_data: Optional[Dict[str, Any]] = None


class CalendarSyncResponseSchema(CalendarSyncSchema):
    """Schema for calendar sync responses."""

    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CalendarSyncListResponseSchema(BaseModel):
    """Schema for list of calendar syncs."""

    syncs: List[CalendarSyncResponseSchema]
    total_count: int


__all__ = [
    "CalendarSyncSchema",
    "CalendarSyncCreateSchema",
    "CalendarSyncUpdateSchema",
    "CalendarSyncResponseSchema",
    "CalendarSyncListResponseSchema",
]
