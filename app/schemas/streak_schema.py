# Generated from streak_model.py

from typing import Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Mapped
from app.schemas.user_schema import UserSchema
from app.schemas.base_schema import BaseSchema


class StreakSchema(BaseSchema):
    """ """

    id: Optional[Mapped[UUID]] = None
    user_id: Optional[Mapped[UUID]] = None
    streak_type: Optional[Mapped[str]] = None
    current_streak: Optional[Mapped[int]] = None
    longest_streak: Optional[Mapped[int]] = None
    last_activity: Optional[Mapped[datetime]] = None
    created_at: Optional[Mapped[datetime]] = None
    updated_at: Optional[Mapped[datetime]] = None
    user: Optional[Mapped[UserSchema]] = None

    class Config:
        arbitrary_types_allowed = True
