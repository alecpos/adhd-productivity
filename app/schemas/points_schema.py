# Generated from points_model.py

from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class PointsSchema(BaseModel):
    """Points schema for tracking user points and levels."""

    id: Optional[UUID] = None
    user_id: Optional[UUID] = None
    total_points: Optional[int] = None
    level: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)
