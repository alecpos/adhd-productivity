from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.models.gamification_model import (
    AchievementModel,
    BadgeModel,
)
from app.models.body_doubling_model import (
    ActivityType,
    BodyDoublingSessionModel,
    SessionStatus,
    SessionType,
)
from app.models.gamification_model import StreakModel, PointsModel, LeaderboardModel
from app.models.task_model import TaskModel
from app.models.user_model import UserModel
from app.services.auth_service import AuthService


class TestFactory:
    """Factory for creating test data."""

    def __init__(self, db_session: AsyncSession, auth_service: AuthService):
        """Initialize the factory."""
        self.db = db_session
        self.auth_service = auth_service

    async def create_user(
        self,
        email: Optional[str] = None,
        username: Optional[str] = None,
        password: str = "test_password",
        is_active: bool = True,
        is_verified: bool = False,
    ) -> UserModel:
        """Create a test user."""
        if not email:
            email = f"test_{uuid4()}@example.com"
        if not username:
            username = f"test_user_{uuid4()}"

        user = UserModel(
            email=email,
            username=username,
            hashed_password=get_password_hash(password),
            is_active=is_active,
            is_verified=is_verified,
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def create_task(
        self,
        user_id: UUID,
        title: str = "Test Task",
        description: Optional[str] = None,
        priority: str = "medium",
        due_date: Optional[datetime] = None,
    ) -> TaskModel:
        """Create a test task."""
        task = TaskModel(
            id=uuid4(),
            user_id=user_id,
            title=title,
            description=description or "Test task description",
            priority=priority,
            due_date=due_date or datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.db.add(task)
        await self.db.commit()
        await self.db.refresh(task)
        return task

    async def create_badge(
        self,
        user_id: UUID,
        name: str = "Test Badge",
        category: str = "focus_master",
        level: int = 1,
    ) -> BadgeModel:
        """Create a test badge."""
        badge = BadgeModel(
            id=uuid4(),
            user_id=user_id,
            name=name,
            category=category,
            level=level,
            awarded_at=datetime.now(timezone.utc),
            meta_data={
                "icon": "test_icon.png",
                "color": "#FF0000",
                "description": "Test badge description",
            },
        )
        self.db.add(badge)
        await self.db.commit()
        await self.db.refresh(badge)
        return badge

    async def create_streak(
        self,
        user_id: UUID,
        current_streak: int = 5,
        longest_streak: int = 10,
        streak_type: str = "daily",
    ) -> StreakModel:
        """Create a test streak."""
        streak = StreakModel(
            user_id=user_id,
            current_streak=current_streak,
            longest_streak=longest_streak,
            streak_type=streak_type,
            last_activity=datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.db.add(streak)
        await self.db.commit()
        await self.db.refresh(streak)
        return streak

    async def create_points(
        self,
        user_id: UUID,
        total_points: int = 100,
        level: int = 2,
    ) -> PointsModel:
        """Create test points."""
        points = PointsModel(
            user_id=user_id,
            total_points=total_points,
            level=level,
        )
        self.db.add(points)
        await self.db.commit()
        await self.db.refresh(points)
        return points

    async def create_body_doubling_session(
        self,
        user_id: UUID,
        session_type: SessionType = SessionType.ONE_ON_ONE,
        status: SessionStatus = SessionStatus.ACTIVE,
        activity_type: ActivityType = ActivityType.WORK,
    ) -> BodyDoublingSessionModel:
        """Create a test body doubling session."""
        session = BodyDoublingSessionModel(
            user_id=user_id,
            task_id=None,
            partner_id=None,
            session_type=session_type,
            status=status,
            activity_type=activity_type,
            environment={"noise_level": "quiet", "lighting": "good"},
            notes="Test session",
            start_time=datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        return session

    async def create_achievement(
        self,
        user_id: UUID,
        name: str = "Test Achievement",
        category: str = "focus",
        points: int = 50,
    ) -> AchievementModel:
        """Create a test achievement."""
        achievement = AchievementModel(
            id=uuid4(),
            user_id=user_id,
            name=name,
            category=category,
            points=points,
            unlocked_at=datetime.now(timezone.utc),
            meta_data={
                "icon": "test_icon.png",
                "color": "#FF0000",
                "description": "Test achievement description",
            },
        )
        self.db.add(achievement)
        await self.db.commit()
        await self.db.refresh(achievement)
        return achievement

    async def create_leaderboard_entry(
        self,
        user_id: UUID,
        category: str = "global",
        rank: int = 1,
        score: float = 100.0,
    ) -> LeaderboardModel:
        """Create a test leaderboard entry."""
        entry = LeaderboardModel(
            user_id=user_id,
            category=category,
            rank=rank,
            score=score,
        )
        self.db.add(entry)
        await self.db.commit()
        await self.db.refresh(entry)
        return entry
