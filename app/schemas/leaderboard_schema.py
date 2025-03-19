# Generated from leaderboard_model.py

from app.schemas.base_schema import BaseSchema
from app.schemas.user_schema import UserSchema
from sqlalchemy.orm import Mapped
from datetime import datetime
from uuid import UUID
from typing import Optional

class LeaderboardSchema(BaseSchema):
    """ """

    id: Optional[Mapped[UUID]] = None
    user_id: Optional[Mapped[UUID]] = None
    category: Optional[Mapped[str]] = None
    score: Optional[Mapped[float]] = None
    rank: Optional[Mapped[int]] = None
    timestamp: Optional[Mapped[datetime]] = None
    user: Optional[Mapped[UserSchema]] = None

    class Config:
        arbitrary_types_allowed = True
