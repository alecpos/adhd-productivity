"""Gamification schema module."""
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict

from app.schemas.base_schema import BaseSchema


class AchievementBase(BaseSchema):
    """Base model for achievements."""
    name: str
    description: Optional[str] = None
    points: int
    category: str


class AchievementCreate(AchievementBase):
    """Request model for creating an achievement."""
    user_id: UUID


class Achievement(AchievementBase):
    """Response model for achievement data."""
    id: UUID
    user_id: UUID
    earned_at: datetime


class BadgeBase(BaseSchema):
    """Base model for badges."""
    name: str
    category: str
    level: int
    description: Optional[str] = None


class BadgeCreate(BadgeBase):
    """Request model for creating a badge."""
    user_id: UUID


class Badge(BadgeBase):
    """Response model for badge data."""
    id: UUID
    user_id: UUID
    earned_at: datetime


class Points(BaseSchema):
    """Base model for points."""
    total_points: int = Field(ge=0)
    level: int = Field(ge=1)


class UpdatePointsRequest(BaseSchema):
    """Request model for updating points."""
    points: int = Field(..., description="Points to add or subtract")


class PointsResponse(BaseSchema):
    """Response model for points data."""
    total_points: int
    level: int
    message: str


class StreakResponse(BaseSchema):
    """Response model for streak-related operations."""
    success: bool
    message: str
    data: Dict[str, Any]


class LeaderboardResponse(BaseSchema):
    """Response model for leaderboard-related operations."""
    success: bool
    message: str
    data: Dict[str, Any]


class AddUserRequest(BaseSchema):
    """Request model for adding a user to a leaderboard."""
    group_name: str
    user_id: UUID


class UserDashboard(BaseSchema):
    """Response model for user dashboard data."""
    streaks: Dict[str, Any]
    leaderboard: Dict[str, Any]
    points: Dict[str, Any]
    level: int
