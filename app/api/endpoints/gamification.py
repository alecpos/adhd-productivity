"""
API endpoints for the adaptive gamification engine.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, List, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.database import get_db
from app.models.user_model import UserModel
from enum import Enum
from pydantic import BaseModel
from datetime import datetime
from typing import Dict, List, Optional, Union

class MotivatorType(str, Enum):
    ACHIEVEMENT = "achievement"
    SOCIAL = "social"
    IMMERSION = "immersion"
    CREATIVITY = "creativity"
    MASTERY = "mastery"
    AUTONOMY = "autonomy"
    PURPOSE = "purpose"

class RewardStrategy(str, Enum):
    FIXED = "fixed"
    VARIABLE = "variable"
    PROGRESSIVE = "progressive"
    COMPETITIVE = "competitive"
    COOPERATIVE = "cooperative"
    MILESTONE = "milestone"

class GamificationMechanic(str, Enum):
    POINTS = "points"
    BADGES = "badges"
    LEVELS = "levels"
    CHALLENGES = "challenges"
    LEADERBOARDS = "leaderboards"
    PROGRESS_BARS = "progress_bars"
    REWARDS = "rewards"
    STREAKS = "streaks"
    SOCIAL_RECOGNITION = "social_recognition"
    STORYTELLING = "storytelling"

class UserMotivationProfile(BaseModel):
    user_id: str
    primary_motivators: List[MotivatorType]
    secondary_motivators: List[MotivatorType]
    effective_mechanics: List[GamificationMechanic]
    reward_preferences: List[RewardStrategy]
    engagement_patterns: Dict[str, float]
    last_updated: datetime

class GamificationAction(BaseModel):
    name: str
    description: str
    mechanic: GamificationMechanic
    reward_strategy: RewardStrategy
    target_motivator: MotivatorType
    difficulty: float
    engagement_score: float
    
class AdaptiveGamificationEngine:
    async def get_user_motivation_profile(self, user_id: str) -> UserMotivationProfile:
        return UserMotivationProfile(
            user_id=user_id,
            primary_motivators=[MotivatorType.ACHIEVEMENT, MotivatorType.MASTERY],
            secondary_motivators=[MotivatorType.SOCIAL],
            effective_mechanics=[GamificationMechanic.CHALLENGES, GamificationMechanic.BADGES],
            reward_preferences=[RewardStrategy.PROGRESSIVE],
            engagement_patterns={"morning": 0.8, "evening": 0.5},
            last_updated=datetime.now()
        )
        
    async def update_user_motivation_profile(self, user_id: str, profile_data: Dict[str, Any]) -> UserMotivationProfile:
        profile = await self.get_user_motivation_profile(user_id)
        return profile
        
    async def get_optimal_mechanics(self, user_id: str, context: Optional[Dict[str, Any]] = None) -> List[GamificationMechanic]:
        return [GamificationMechanic.CHALLENGES, GamificationMechanic.BADGES]
        
    async def get_recommended_actions(self, user_id: str, count: int = 3) -> List[GamificationAction]:
        return [
            GamificationAction(
                name="Complete Daily Streak",
                description="Finish your daily tasks to maintain your streak",
                mechanic=GamificationMechanic.STREAKS,
                reward_strategy=RewardStrategy.PROGRESSIVE,
                target_motivator=MotivatorType.ACHIEVEMENT,
                difficulty=0.3,
                engagement_score=0.8
            )
        ]
        
    async def track_effectiveness(self, user_id: str, action_name: str, engagement_score: float) -> Dict[str, Any]:
        return {"success": True, "updated_profile": True}

from app.services.gamification_service import GamificationService, get_gamification_service
from app.services.user_insights_service import UserInsightsService, get_user_insights_service

router = APIRouter(
    prefix="/gamification",
    tags=["Gamification", "Motivation"]
)

# Create a dependency for the gamification engine that doesn't expose DB session
gamification_engine = None  # Global instance used by endpoints

def init_gamification_engine(
    gamification_service: GamificationService = Depends(get_gamification_service),
    user_insights_service: UserInsightsService = Depends(get_user_insights_service)
):
    """Initialize the global gamification engine instance."""
    global gamification_engine
    if gamification_engine is None:
        gamification_engine = AdaptiveGamificationEngine(
            gamification_service=gamification_service,
            user_insights_service=user_insights_service
        )
    return gamification_engine

@router.get("/profile", response_model=UserMotivationProfile)
async def get_user_motivation_profile(
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get the user's motivation profile.
    
    This endpoint returns the user's motivation profile, which includes their
    preferences for different motivation types, reward preferences, and the
    effectiveness of various game mechanics for this specific user.
    """
    try:
        # Initialize the engine if needed
        engine = init_gamification_engine(
            get_gamification_service(db),
            get_user_insights_service(db)
        )
        profile = await engine.get_user_profile(str(current_user.id))
        return profile
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve motivation profile: {str(e)}")

@router.patch("/profile", response_model=UserMotivationProfile)
async def update_user_motivation_profile(
    profile_updates: Dict[str, Any],
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update the user's motivation profile.
    
    This endpoint allows updating specific aspects of the user's motivation profile,
    such as their preferences for different motivation types or game mechanics.
    """
    try:
        # Initialize the engine if needed
        engine = init_gamification_engine(
            get_gamification_service(db),
            get_user_insights_service(db)
        )
        # The behavior update structure is used to modify the profile
        updated_profile = await engine.update_profile_from_behavior(
            str(current_user.id), profile_updates
        )
        return updated_profile
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update motivation profile: {str(e)}")

@router.post("/actions", response_model=List[Dict[str, Any]])
async def get_gamification_actions(
    context: Dict[str, Any],
    count: int = Query(1, ge=1, le=5),
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get recommended gamification actions based on the current context.
    
    This endpoint suggests the most effective gamification actions for the current
    user based on their motivation profile and the provided context (e.g., task
    difficulty, importance, current energy level).
    """
    try:
        # Initialize the engine if needed
        engine = init_gamification_engine(
            get_gamification_service(db),
            get_user_insights_service(db)
        )
        actions = await engine.get_gamification_actions(
            str(current_user.id), context, count
        )
        return [action.dict() for action in actions]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get gamification actions: {str(e)}")

@router.get("/mechanics", response_model=List[GamificationMechanic])
async def get_optimal_mechanics(
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = Query(3, ge=1, le=10),
    task_type: Optional[str] = None,
    difficulty: Optional[float] = None,
    importance: Optional[float] = None,
    energy_level: Optional[float] = None,
    current_hour: Optional[int] = None,
):
    """
    Get the optimal game mechanics for the current user.
    
    This endpoint returns the game mechanics that are most effective for the
    current user, based on their motivation profile and the provided context.
    """
    context = {
        "task_type": task_type,
        "difficulty": difficulty,
        "importance": importance,
        "energy_level": energy_level,
        "current_hour": current_hour,
    }
    # Filter out None values
    context = {k: v for k, v in context.items() if v is not None}
    
    try:
        # Initialize the engine if needed
        engine = init_gamification_engine(
            get_gamification_service(db),
            get_user_insights_service(db)
        )
        mechanics = await engine.get_optimal_mechanics(
            str(current_user.id), context, limit
        )
        return mechanics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get optimal game mechanics: {str(e)}")

@router.post("/effectiveness/{action_id}", response_model=Dict[str, Any])
async def track_gamification_effectiveness(
    action_id: str,
    engagement_metrics: Dict[str, Any],
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Track the effectiveness of a gamification action.
    
    This endpoint allows tracking how effective a specific gamification action was
    based on the user's engagement with it. This data is used to improve future
    recommendations.
    """
    try:
        # Initialize the engine if needed
        engine = init_gamification_engine(
            get_gamification_service(db),
            get_user_insights_service(db)
        )
        await engine.track_gamification_effectiveness(
            str(current_user.id), action_id, engagement_metrics
        )
        return {"success": True, "message": "Effectiveness tracking recorded"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to track gamification effectiveness: {str(e)}") 