from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.gamification_schema import (
    BadgeResponseSchema,
    AchievementResponseSchema,
    LeaderboardResponseSchema,
    PointsResponseSchema,
)
from app.database import get_db
from app.models.user_model import User
from app.services.gamification_service import GamificationService
from app.services.auth_service import get_current_user
from fastapi import APIRouter, Depends
from typing import List

router = APIRouter(prefix="/api/gamification", tags=["gamification"])


@router.get("/badges", response_model=List[BadgeResponseSchema])
async def get_user_badges(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all badges for current user."""
    service = GamificationService(db)
    badges = await service.get_user_badges(current_user.id)


@router.get("/achievements", response_model=List[AchievementResponseSchema])
async def get_user_achievements(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all achievements for current user."""
    service = GamificationService(db)
    achievements = await service.get_user_achievements(current_user.id)


@router.get("/leaderboard", response_model=LeaderboardResponseSchema)
async def get_leaderboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get leaderboard rankings."""
    service = GamificationService(db)
    leaderboard = await service.get_leaderboard()


@router.get("/progress", response_model=PointsResponseSchema)
async def get_user_progress(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get current user's progress."""
    service = GamificationService(db)
    progress = await service.get_user_points(current_user.id)
