"""Analytics schemas module."""

from datetime import datetime
from typing import Dict
from uuid import UUID

from pydantic import BaseModel

from app.schemas.base_schema import BaseResponse


class AnalyticsSchema(BaseModel):
    """Base analytics schema."""

    id: UUID
    user_id: UUID
    tasks_completed: int
    focus_time: float
    productivity_score: float
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class AnalyticsResponseSchema(BaseResponse):
    """Analytics response schema."""

    data: Dict
    message: str = "Analytics retrieved successfully"


class UserInsightsResponseSchema(BaseResponse):
    """User insights response schema."""

    data: Dict
    message: str = "User insights retrieved successfully"
