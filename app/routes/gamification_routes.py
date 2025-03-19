from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.models.user_model import UserModel
from app.services.auth_service import get_current_user
from app.services.gamification_service import GamificationService
from app.schemas.gamification_schema import (
    Badge,
    Achievement,
    LeaderboardResponse,
    PointsResponse,
)

router = APIRouter(prefix="/api/gamification", tags=["gamification"])


@router.get("/badges", response_model=List[Badge])
async def get_user_badges(
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Get all badges for current user."""
    service = GamificationService(db)
    badges = await service.get_user_badges(current_user.id)
    return badges


@router.get("/achievements", response_model=List[Achievement])
async def get_user_achievements(
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Get all achievements for current user."""
    service = GamificationService(db)
    achievements = await service.get_user_achievements(current_user.id)
    return achievements


@router.get("/leaderboard", response_model=LeaderboardResponse)
async def get_leaderboard(
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Get leaderboard rankings."""
    service = GamificationService(db)
    leaderboard = await service.get_leaderboard()
    return leaderboard


@router.get("/progress", response_model=PointsResponse)
async def get_user_progress(
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Get current user's progress."""
    service = GamificationService(db)
    progress = await service.get_user_points(current_user.id)
    return progress
