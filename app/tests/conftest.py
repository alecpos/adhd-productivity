"""Test configuration module."""

import asyncio
import logging
import sys
import os
from datetime import datetime, time, timedelta, timezone
from typing import (
    Any,
    AsyncGenerator,
    Callable,
    Dict,
    Iterator,
    List,
    TypeVar,
)
from uuid import uuid4, UUID

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from unittest.mock import AsyncMock, MagicMock, patch

from app.core.security import get_password_hash
from app.database import get_db
import app.database as db_module
from app.main import create_app
from app.models.base_model import BaseModel
from app.models.body_doubling_model import (
    ActivityType,
    BodyDoublingSessionModel,
    SessionStatus,
    SessionType,
)
from app.models.gamification_model import AchievementModel, BadgeModel
from app.models.gamification_model import StreakModel, PointsModel, LeaderboardModel
from app.models.time_block_model import BlockPriority, BlockType
from app.models.user_model import UserModel
from app.schemas.schedule_params_schema import EnergyPattern, WorkHours
from app.schemas.schema_manager_schema import DictSchema
from app.schemas.task_schema import (
    TaskSchema,
)
from app.services.auth_service import AuthService
from app.services.body_doubling_service import BodyDoublingService
from app.services.gamification_service import GamificationService
from app.services.hyperfocus_service import HyperfocusService
from app.services.pomodoro_service import PomodoroService
from app.services.task_service import TaskService
from app.services.timeline_service import TimelineService
from app.tests.factories import TestFactory
from app.models.enums_model import BlockPriority
from app.database.base import Base
from app.schemas.body_doubling_schema import CreateBodyDoublingSchema
from app.services.body_doubling.session_manager import SessionManager
from app.services.body_doubling.matching_engine import MatchingEngine
from app.services.body_doubling.analytics_service import AnalyticsService
from app.services.body_doubling.notification_service import NotificationService

# Import from our mock modules
from app.tests.ml.stochastic_time_estimation.mock_pymc import MockTheano
from app.tests.ml.stochastic_time_estimation.mock_models import (
    MockMentalHealthModel,
    MockEnergyModel,
    MockBaseMLModel,
    MockFeatureEngineer
)

T = TypeVar("T")  # Add type variable for generic types

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.debug("Python path: %s", sys.path)
logger.debug("Starting test configuration")
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)
logging.getLogger("sqlalchemy.dialects").setLevel(logging.WARNING)
logging.getLogger("sqlalchemy.orm").setLevel(logging.WARNING)
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# Mock dependencies that cause issues during testing
sys.modules['app.routes'] = MagicMock()
sys.modules['app.routes.body_doubling_routes'] = MagicMock()

@pytest.fixture(scope="session")
def event_loop() -> Iterator[asyncio.AbstractEventLoop]:
    """Create an instance of the default event loop for each test case."""
    # Create a new event loop
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    
    # Set the loop as the current event loop
    asyncio.set_event_loop(loop)
    
    # Yield the loop for the tests to use
    yield loop
    
    # Clean up
    loop.close()
    asyncio.set_event_loop(None)  # Reset the event loop after all tests


@pytest_asyncio.fixture(scope="session")
async def db_engine():
    """Create a test database engine."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=True)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture(scope="session")
def db_session_factory(db_engine: AsyncEngine) -> Any:
    """Create session factory."""
    return sessionmaker(
        bind=db_engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
    )


@pytest_asyncio.fixture
async def db_session(db_session_factory) -> AsyncSession:
    """Create a test database session."""
    async with db_session_factory() as session:
        try:
            yield session
            await session.rollback()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client."""
    app = create_app()

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        """Override the get_db dependency for testing."""
        try:
            yield db_session
        except Exception:
            await db_session.rollback()
            raise
        finally:
            await db_session.close()

    app.dependency_overrides[get_db] = override_get_db  # type: ignore[reportInvalidTypeForm]

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
        follow_redirects=True,
    ) as client:
        try:
            yield client
        finally:
            app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def test_user(db_session: AsyncSession) -> UserModel:
    """Create a test user."""
    logger.debug("Creating test user")
    user_id = uuid4()
    user = UserModel(
        id=user_id,
        email=f"test_{user_id}@example.com",
        username=f"test_user_{user_id}",
        full_name="Test User",
        hashed_password=get_password_hash("test_password"),
        is_active=True,
        is_verified=False,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
async def auth_headers(test_user, db_session: AsyncSession) -> DictSchema:
    """Create authentication headers."""
    auth_service = AuthService(db_session)
    access_token = auth_service.create_access_token({"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture(scope="function")
async def body_doubling_service(db_session: AsyncSession) -> BodyDoublingService:
    """Create a body doubling service instance."""
    session_manager = SessionManager(db_session)
    matching_engine = MatchingEngine(session_manager=session_manager)
    analytics_service = AnalyticsService(session_manager=session_manager)
    notification_service = NotificationService(session_manager=session_manager)
    
    return BodyDoublingService(
        session_manager=session_manager,
        matching_engine=matching_engine,
        analytics_service=analytics_service,
        notification_service=notification_service
    )


@pytest.fixture(scope="function")
async def timeline_service(db_session: AsyncSession) -> TimelineService:
    """Create a timeline service instance."""
    return TimelineService(db_session)


@pytest.fixture(scope="function")
async def gamification_service(db_session: AsyncSession) -> GamificationService:
    """Create a gamification service instance."""
    logger.debug("Creating gamification service")
    return GamificationService(db_session)


@pytest.fixture(scope="function")
async def pomodoro_service(db_session: AsyncSession) -> PomodoroService:
    """Create a pomodoro service instance."""
    return PomodoroService(db_session)


@pytest.fixture(scope="function")
async def hyperfocus_service(db_session: AsyncSession) -> HyperfocusService:
    """Create a hyperfocus service instance."""
    return HyperfocusService(db_session)


@pytest.fixture(scope="function")
async def task_service(db_session: AsyncSession) -> TaskService:
    """Create a task service instance."""
    return TaskService(db_session)


@pytest_asyncio.fixture(scope="function")
async def test_streak(test_user: UserModel, db_session: AsyncSession) -> StreakModel:
    """Create a test streak."""
    logger.debug("Creating test streak")
    now = datetime.now(tz=timezone.utc)
    streak = StreakModel(
        user_id=test_user.id,
        current_streak=5,
        longest_streak=10,
        streak_type="daily",
        last_activity=now,
        created_at=now,
        updated_at=now,
    )
    db_session.add(streak)
    await db_session.commit()
    await db_session.refresh(streak)


@pytest_asyncio.fixture(scope="function")
async def test_leaderboard(
    test_user: UserModel, db_session: AsyncSession
) -> LeaderboardModel:
    """Create a test leaderboard entry."""
    logger.debug("Creating test leaderboard entry")
    leaderboard = LeaderboardModel(user_id=test_user.id, category="global", rank=1, score=100.0)
    db_session.add(leaderboard)
    await db_session.commit()
    await db_session.refresh(leaderboard)


@pytest.fixture(scope="function")
async def active_session(test_user, db_session: AsyncSession):
    """Create an active body doubling session."""
    logger.debug("Creating active body doubling session")
    session = BodyDoublingSessionModel(
        user_id=test_user.id,
        task_id=None,
        partner_id=None,
        session_type=SessionType.ONE_ON_ONE,
        status=SessionStatus.ACTIVE,
        activity_type=ActivityType.WORK,
        environment={"noise_level": "quiet", "lighting": "good"},
        notes="Working on Python backend",
        start_time=datetime.utcnow(),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db_session.add(session)
    await db_session.commit()
    await db_session.refresh(session)
    logger.debug("Active session created: %s", session)


@pytest.fixture(scope="function")
async def test_factory(db_session: AsyncSession):
    """Create a test factory for creating test data."""
    auth_service = AuthService(db_session)
    return TestFactory(db_session, auth_service)


@pytest_asyncio.fixture(scope="function")
async def test_points(test_user: UserModel, db_session: AsyncSession) -> PointsModel:
    """Create test points for a user."""
    logger.debug("Creating test points")
    points = PointsModel(user_id=test_user.id, total_points=100, level=2)
    db_session.add(points)
    await db_session.commit()
    await db_session.refresh(points)


@pytest_asyncio.fixture(scope="function")
async def test_badge(test_user: UserModel, db_session: AsyncSession) -> BadgeModel:
    """Create a test badge."""
    badge = BadgeModel(
        id=uuid4(),
        user_id=test_user.id,
        name="Test Badge",
        description="A test badge",
        category="focus_master",
        level=1,
        earned_at=datetime.now(timezone.utc),
        meta_data={"icon_url": "test_icon.png"},
    )
    db_session.add(badge)
    await db_session.commit()
    await db_session.refresh(badge)


@pytest_asyncio.fixture(scope="function")
async def test_achievement(
    test_user: UserModel, db_session: AsyncSession
) -> AchievementModel:
    """Create a test achievement."""
    achievement = AchievementModel(
        id=uuid4(),
        user_id=test_user.id,
        name="Test Achievement",
        description="A test achievement",
        category="focus",
        points=50,
        earned_at=datetime.now(timezone.utc),
        meta_data={"progress": 50, "completed": False},
    )
    db_session.add(achievement)
    await db_session.commit()
    await db_session.refresh(achievement)


@pytest_asyncio.fixture(scope="function")
async def multiple_badges(test_user: UserModel, db_session: AsyncSession) -> List[BadgeModel]:
    """Create multiple test badges."""
    badges = [
        BadgeModel(
            id=uuid4(),
            user_id=test_user.id,
            name=f"Test Badge {i}",
            description=f"Test Badge {i} Description",
            category=["focus_master", "task_champion", "streak_king"][i % 3],
            level=i + 1,
            earned_at=datetime.now(timezone.utc) - timedelta(days=i),
            meta_data={"icon_url": f"test_icon_{i}.png"},
        )
        for i in range(5)
    ]
    for badge in badges:
        db_session.add(badge)
    await db_session.commit()
    for badge in badges:
        await db_session.refresh(badge)


@pytest_asyncio.fixture(scope="function")
async def multiple_achievements(
    test_user: UserModel, db_session: AsyncSession
) -> List[AchievementModel]:
    """Create multiple test achievements."""
    achievements = [
        AchievementModel(
            id=uuid4(),
            user_id=test_user.id,
            name=f"Test Achievement {i}",
            description=f"Test Achievement {i} Description",
            category=["focus", "tasks", "streaks"][i % 3],
            points=i * 50,
            earned_at=datetime.now(timezone.utc) - timedelta(days=i),
            meta_data={"progress": i * 20, "completed": i % 2 == 0},
        )
        for i in range(5)
    ]
    for achievement in achievements:
        db_session.add(achievement)
    await db_session.commit()
    for achievement in achievements:
        await db_session.refresh(achievement)


@pytest.fixture
def sample_work_hours() -> WorkHours:
    """Create sample work hours for testing."""
    return WorkHours(
        start=time(9, 0).strftime("%H:%M"),
        end=time(17, 0).strftime("%H:%M"),
        breaks=[
            {
                "start": time(12, 0).strftime("%H:%M"),
                "end": time(13, 0).strftime("%H:%M"),
            }
        ],
    )


@pytest.fixture
def sample_energy_pattern() -> EnergyPattern:
    """Create sample energy pattern for testing."""
    return EnergyPattern(
        pattern_type="morning",
        peak_hours=[
            {
                "start": time(9, 0).strftime("%H:%M"),
                "end": time(11, 0).strftime("%H:%M"),
            }
        ],
        low_energy_periods=[
            {
                "start": time(14, 0).strftime("%H:%M"),
                "end": time(16, 0).strftime("%H:%M"),
            }
        ],
    )


@pytest.fixture
def task_to_block_dict() -> Callable[[TaskSchema], Dict[str, Any]]:
    """Create a function to convert TaskSchema to TimeBlockModel dictionary."""

    def converter(task: TaskSchema) -> Dict[str, Any]:
        current_time = datetime.now(timezone.utc)
        start_time = current_time.replace(hour=9, minute=0)
        duration = min(task.estimated_duration or 60, 240)
        end_time = start_time + timedelta(minutes=duration)
        return {
            "title": task.title,
            "description": task.description or "",
            "start_time": start_time,
            "end_time": end_time,
            "duration": duration,
            "block_type": BlockType.TASK,
            "priority": (
                BlockPriority.HIGH
                if task.priority == BlockPriority.HIGH
                else BlockPriority.MEDIUM
            ),
            "energy_level": min(task.energy_required or 5, 10),
            "focus_level": min(task.energy_required or 5, 10),
            "effectiveness_score": 1.0,
            "is_flexible": True,
            "buffer_before": 0,
            "buffer_after": 0,
        }

    return converter


@pytest.fixture
async def mock_optimizer_service(monkeypatch):
    """Mock the optimizer service for testing."""

    class MockOptimizerService:
        async def optimize_schedule(self, *args, **kwargs):
            return {"blocks": [], "score": 0.95, "duration": 480}

        async def get_stats(self, *args, **kwargs):
            return {"total_optimizations": 10, "average_score": 0.85}

    mock_service = MockOptimizerService()
    monkeypatch.setattr(
        "app.services.optimizer_service.OptimizerService",
        lambda *args, **kwargs: mock_service,
    )


@pytest.fixture
def valid_token() -> str:
    return "valid.test.token"


@pytest.fixture
def expired_token() -> str:
    return "expired.test.token"


@pytest.fixture(scope="session", autouse=True)
def patch_imports():
    """
    Patch imports to use mocks instead of real modules.
    """
    # Mock PyMC3 and its dependencies
    sys.modules['pymc3'] = MagicMock()
    sys.modules['theano'] = MockTheano()
    sys.modules['theano.tensor'] = MagicMock()
    
    # Patch app.models.mental_health_model to include MentalHealthModel
    mental_health_module = MagicMock()
    mental_health_module.MentalHealthModel = MockMentalHealthModel
    sys.modules['app.models.mental_health_model'] = mental_health_module
    
    # Patch app.models.energy_model
    energy_module = MagicMock()
    energy_module.EnergyModel = MockEnergyModel
    sys.modules['app.models.energy_model'] = energy_module
    
    # Patch ML base models
    ml_models_module = MagicMock()
    ml_models_module.BaseMLModel = MockBaseMLModel
    sys.modules['app.ml.models'] = ml_models_module
    
    # Patch feature engineering
    feature_eng_module = MagicMock()
    feature_eng_module.FeatureEngineer = MockFeatureEngineer
    sys.modules['app.ml.feature_engineering'] = feature_eng_module
    
    # Patch numpy bool
    try:
        import numpy as np
        if not hasattr(np, 'bool_'):
            np.bool_ = bool
    except ImportError:
        pass
    
    yield
    
    # Clean up after tests complete
    for module in [
        'pymc3', 'theano', 'theano.tensor', 
        'app.models.mental_health_model', 'app.models.energy_model',
        'app.ml.models', 'app.ml.feature_engineering'
    ]:
        if module in sys.modules:
            del sys.modules[module]


@pytest.fixture
def mock_db():
    """Mock database session."""
    class MockDB:
        def __init__(self):
            self.data = {}
            self.settings = {}

        async def query(self, model_class):
            return self.data.get(model_class.__name__, [])

        async def commit(self):
            pass

        async def close(self):
            pass

        async def add(self, obj):
            model_name = obj.__class__.__name__
            if model_name not in self.data:
                self.data[model_name] = []
            self.data[model_name].append(obj)

    return MockDB()


def run_async_test(coroutine):
    """Run an async test within an event loop.
    
    This function ensures that async test functions are properly awaited when run
    outside of pytest's automatic asyncio handling.
    
    Args:
        coroutine: The async function to run
        
    Returns:
        The result of the awaited coroutine
    """
    # Get the current policy
    policy = asyncio.get_event_loop_policy()
    
    try:
        # Try to get the current event loop
        loop = asyncio.get_event_loop()
    except RuntimeError:
        # If there's no event loop in the current thread, create one
        loop = policy.new_event_loop()
        asyncio.set_event_loop(loop)
    
    if loop.is_running():
        # If the loop is already running (e.g., in an async environment),
        # use run_coroutine_threadsafe
        future = asyncio.run_coroutine_threadsafe(coroutine, loop)
        return future.result()
    else:
        # Otherwise, use run_until_complete
        return loop.run_until_complete(coroutine)


@pytest.fixture
def sample_session_data():
    """Create sample session data for testing."""
    return CreateBodyDoublingSchema(
        user_id=UUID("11111111-1111-1111-1111-111111111111"),
        host_id=UUID("11111111-1111-1111-1111-111111111111"),
        session_type=SessionType.ONE_ON_ONE,
        activity_type=ActivityType.WORK,
        planned_duration=30,
        description=None,
        energy_level=None,
        environment_data=None,
    )


@pytest.fixture
def user_1_id():
    """Create a test user ID."""
    return UUID("11111111-1111-1111-1111-111111111111")


@pytest.fixture
def user_2_id():
    """Create another test user ID."""
    return UUID("22222222-2222-2222-2222-222222222222")
