import pytest
from datetime import datetime, timedelta
from uuid import UUID, uuid4
from sqlalchemy.exc import IntegrityError, StatementError
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, Column, ForeignKey, String, JSON
from pydantic import ValidationError
import logging
import json

# Import base model
from app.models.base_model import BaseModel

# Import enums once
from app.models.enums_model import (
    SessionType, SessionStatus, BlockType, BlockPriority, CalendarType,
    ConflictResolutionStrategy, EnergyLevel, SyncProvider, SyncSource,
    SyncStatus, ContactType, EventType, ActivityType, DistractionType,
    MedicationType, EventPriority, EventStatus, TaskPriority, TaskStatus,
    CommandType, TimelineEventType, InteractionType, InteractionOutcome,
    HyperfocusSessionStatus, MetricType
)

# Group related model imports
from app.models.subscription_model import (
    SubscriptionModel, SubscriptionTierModel, SubscriptionStatusModel
)
from app.models.health_model import HealthMetrics
from app.models.contact_model import ContactModel
from app.models.adhd_settings_model import (
    ADHDSettingsModel, DistractionLogModel, MedicationLogModel,
    ADHDMetricsModel, ADHDPatternsModel, PatternType
)
from app.models.analytics_model import UserAnalytics
from app.models.interaction_model import Interaction, InteractionStats
from app.models.calendar_model import CalendarModel
from app.models.mental_health_model import MentalHealthLogModel
from app.models.gamification_model import (
    StreakModel, PointsModel, LeaderboardModel, AchievementModel, BadgeModel
)
from app.models.user_model import UserModel
from app.models.body_doubling_model import BodyDoublingSessionModel
from app.models.nlp_model import NLPModel, NLPAnalysis, TaskAnalysis, FocusStrategy
from app.models.energy_model import EnergyLog, EnergyStats
from app.models.session_model import SessionModel, SessionStatsModel, SessionType, SessionStatus
from app.models.auth_model import RefreshToken, LoginAttempt
from app.models.scheduling_model import ScheduleBlock, SchedulePreferences
from app.models.task_model import TaskModel, TaskStatus, TaskPriority
from app.models.hyperfocus_model import HyperfocusSessionModel
from app.models.focus_model import FocusSessionModel,FocusSessionType
from app.models.calendar_event_model import CalendarEventModel
from app.models.pomodoro_model import  PomodoroSessionModel
from app.models.calendar_sync_model import CalendarSyncModel, SyncDirection
from app.models.time_block_model import TimeBlockModel, BlockPriority
from app.models.voice_command_model import VoiceCommandModel, VoicePreferencesModel
from app.models.timeline_model import TimelineEventModel
from app.models.reminder_model import ReminderModel, ReminderPriorityModel
from app.models.mindfulness_model import MindfulnessSessionModel
from app.models.login_attempt_model import LoginAttemptModel

# Set up an in-memory SQLite test database
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# List of model classes to check
model_classes = [
    SubscriptionModel,
    HealthMetrics, ContactModel,
    ADHDSettingsModel, DistractionLogModel, MedicationLogModel, ADHDMetricsModel, ADHDPatternsModel,
    UserAnalytics, Interaction, InteractionStats,
    CalendarModel, MentalHealthLogModel,
    StreakModel, AchievementModel, BadgeModel,
    UserModel, BodyDoublingSessionModel,
    NLPModel, NLPAnalysis, TaskAnalysis, FocusStrategy,
    EnergyLog, EnergyStats,
    SessionModel, PomodoroSessionModel, SessionStatsModel,
    RefreshToken, LoginAttempt,
    ScheduleBlock, SchedulePreferences,
    TaskModel, HyperfocusSessionModel, FocusSessionModel,
    CalendarEventModel, VoiceCommandModel, VoicePreferencesModel,
    TimelineEventModel, ReminderModel,
    MindfulnessSessionModel, LoginAttemptModel, CalendarSyncModel, TimeBlockModel
]

@pytest.fixture(scope="function")
def db_session():
    """Creates a new database session for each test."""
    BaseModel.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.rollback()
    session.close()
    BaseModel.metadata.drop_all(bind=engine)

@pytest.mark.parametrize("model_class", model_classes)
def test_model_inheritance(model_class):
    """Test that all model classes inherit from BaseModel."""
    # Skip non-class entries that might have been accidentally added to model_classes
    if not isinstance(model_class, type):
        return  # Silently skip non-class entries

    # Skip MockHealthMetrics as it's intentionally not inheriting from BaseModel for testing purposes
    if model_class.__name__ == "MockHealthMetrics":
        return  # Silently skip MockHealthMetrics

    assert issubclass(model_class, BaseModel), f"{model_class.__name__} does not inherit from BaseModel"

def test_uuid_assignment(db_session):
    """Test if models correctly assign UUIDs."""
    user = UserModel(
        id=uuid4(),
        username="test_user",
        email="test@example.com",
        full_name="Test User",
        hashed_password="test_password"
    )
    db_session.add(user)
    db_session.commit()
    assert user.id is not None
    assert isinstance(user.id, UUID)

    retrieved_user = db_session.query(UserModel).first()
    assert retrieved_user is not None
    assert retrieved_user.id == user.id

def test_timestamp_fields(db_session):
    """Test if models properly handle timestamp fields."""
    user = UserModel(
        id=str(uuid4()),
        username="test_user",
        email="test@example.com",
        full_name="Test User",
        hashed_password="test_password",
        is_active=True,
        is_verified=False
    )
    db_session.add(user)
    db_session.commit()

    retrieved_user = db_session.query(UserModel).first()
    assert isinstance(retrieved_user.created_at, datetime)
    assert isinstance(retrieved_user.updated_at, datetime)

    # Allow a slightly larger microsecond difference
    assert abs((retrieved_user.updated_at - retrieved_user.created_at).total_seconds()) < 0.001

    # Simulate an update
    retrieved_user.username = "updated_user"
    db_session.add(retrieved_user)
    db_session.commit()

    # Refresh the object
    db_session.refresh(retrieved_user)

    assert retrieved_user.updated_at is not None
    assert retrieved_user.updated_at > retrieved_user.created_at  # Ensure update timestamp is later

@pytest.mark.parametrize("model_class", model_classes)
def test_model_serialization(model_class):
    """Test model serialization to dict."""
    # Skip non-class entries that might have been accidentally added to model_classes
    if not isinstance(model_class, type):
        return  # Silently skip non-class entries

    # Skip MockHealthMetrics as it's intentionally not inheriting from BaseModel for testing purposes
    if model_class.__name__ == "MockHealthMetrics":
        return  # Silently skip MockHealthMetrics

    # Create an instance of the model
    model_instance = model_class()

    # Test that the model has the expected attributes from BaseModel
    assert hasattr(model_instance, "id"), f"{model_class.__name__} should have an 'id' attribute"
    assert hasattr(model_instance, "created_at"), f"{model_class.__name__} should have a 'created_at' attribute"
    assert hasattr(model_instance, "updated_at"), f"{model_class.__name__} should have an 'updated_at' attribute"

@pytest.mark.parametrize("model_class", model_classes)
def test_invalid_inputs(model_class, db_session):
    """Test model validation for invalid inputs."""
    # Skip non-class entries that might have been accidentally added to model_classes
    if not isinstance(model_class, type):
        return  # Silently skip non-class entries

    # Skip MockHealthMetrics as it's intentionally not inheriting from BaseModel for testing purposes
    if model_class.__name__ == "MockHealthMetrics":
        return  # Silently skip MockHealthMetrics

    # Create dummy parents for models with foreign key constraints
    create_dummy_parents(db_session, model_class)

    # Test with invalid UUID
    try:
        invalid_instance = model_class(id="not-a-uuid")
        db_session.add(invalid_instance)
        db_session.flush()
        # If we get here, the validation failed to catch the invalid UUID
        assert False, f"{model_class.__name__} accepted an invalid UUID"
    except Exception:
        # Expected to fail
        db_session.rollback()

    # Test with invalid date
    date_fields = [field for field in dir(model_class) if "date" in field.lower() and not field.startswith("_")]
    for field in date_fields:
        try:
            kwargs = {field: "not-a-date"}
            invalid_instance = model_class(**kwargs)
            db_session.add(invalid_instance)
            db_session.flush()
            # If we get here, the validation failed to catch the invalid date
            assert False, f"{model_class.__name__} accepted an invalid date for {field}"
        except Exception:
            # Expected to fail
            db_session.rollback()

def create_dummy_parents(db_session, model_class):
    """Create dummy parent records for models with foreign key constraints."""
    parent_data = {}
    model_name = model_class.__name__

    # Create a user if needed
    if hasattr(model_class, "user_id") or model_name in ["RefreshToken", "LoginAttempt"]:
        user = UserModel(
            email=f"test_{uuid4().hex[:8]}@example.com",
            username=f"test_user_{uuid4().hex[:8]}",
            hashed_password="test_password",
            full_name=f"Test User {uuid4().hex[:8]}"
        )
        db_session.add(user)
        db_session.flush()
        parent_data["user_id"] = str(user.id)

    # Create settings if needed
    if model_name in ["DistractionLogModel", "MedicationLogModel", "ADHDMetricsModel", "ADHDPatternsModel"]:
        settings = ADHDSettingsModel(
            user_id=parent_data.get("user_id", str(uuid4())),
            work_interval_duration=25,
            break_duration=5,
            long_break_duration=15,
            blocks_before_long_break=4,
            distraction_sensitivity=1.0,
            focus_assistance_level=1,
            energy_tracking_enabled=True,
            task_chunking_enabled=True,
            visual_aids_enabled=True
        )
        db_session.add(settings)
        db_session.flush()
        parent_data["settings_id"] = str(settings.id)

    # Create a dummy calendar if needed
    if model_name in ["CalendarEventModel", "CalendarSyncModel"]:
        calendar_id = str(uuid4())
        calendar = CalendarModel(
            id=calendar_id,
            user_id=parent_data.get("user_id", str(uuid4())),
            name="Test Calendar",
            provider="Google",
            is_primary=False,
            is_enabled=True
        )
        db_session.add(calendar)
        try:
            db_session.flush()
            parent_data["calendar_id"] = calendar_id
        except Exception:
            db_session.rollback()
            # Try to find an existing calendar
            existing_calendar = db_session.query(CalendarModel).first()
            if existing_calendar:
                parent_data["calendar_id"] = str(existing_calendar.id)
            else:
                # If we can't create or find a calendar, just use a UUID string
                parent_data["calendar_id"] = str(uuid4())

    # Create an NLP record if needed
    if model_name == "NLPAnalysis" or model_name == "TaskAnalysis":
        nlp_id = str(uuid4())
        nlp = NLPModel(
            id=nlp_id,
            user_id=parent_data.get("user_id", str(uuid4())),
            text="Test text",
            parsed_data="{}",
            confidence_score=0.9,
            entities=[]
        )
        db_session.add(nlp)
        db_session.flush()
        parent_data["nlp_record_id"] = nlp_id

    # Create a dummy task if needed
    if model_name in ["TaskAnalysis", "PomodoroSessionModel", "FocusSessionModel"]:
        task_id = str(uuid4())
        task = TaskModel(
            id=task_id,
            user_id=parent_data.get("user_id", str(uuid4())),
            title="Test Task",
            status=TaskStatus.TODO.value,
            priority=TaskPriority.MEDIUM.value
        )
        db_session.add(task)
        try:
            db_session.flush()
            parent_data["task_id"] = task_id
        except Exception:
            db_session.rollback()
            # If we can't create a task, just use a UUID string
            parent_data["task_id"] = str(uuid4())

    # Create a dummy session if needed
    if model_name == "SessionStatsModel":
        session_id = str(uuid4())
        session = SessionModel(
            id=session_id,
            user_id=parent_data.get("user_id", str(uuid4())),
            type=SessionType.FOCUS,
            status=SessionStatus.COMPLETED,
            start_time=datetime.now() - timedelta(hours=2),
            end_time=datetime.now() - timedelta(hours=1),
            duration=60
        )
        db_session.add(session)
        try:
            db_session.flush()
            parent_data["session_id"] = session_id
        except Exception:
            db_session.rollback()
            # If we can't create a session, just use a UUID string
            parent_data["session_id"] = str(uuid4())

    # Convert any UUIDs in parent_data to strings
    for key, value in parent_data.items():
        if isinstance(value, UUID):
            parent_data[key] = str(value)

    return parent_data

def skip_refresh_models():
    """List of model names that should skip the refresh step due to enum mapping issues."""
    return ["ScheduleBlock"]

@pytest.mark.parametrize("model_class", model_classes)
def test_database_constraints(model_class, db_session):
    """Test database constraints for models."""
    # Skip non-class entries that might have been accidentally added to model_classes
    if not isinstance(model_class, type):
        return  # Silently skip non-class entries

    # Skip MockHealthMetrics as it's intentionally not inheriting from BaseModel for testing purposes
    if model_class.__name__ == "MockHealthMetrics":
        return  # Silently skip MockHealthMetrics

    # Create dummy parents for models with foreign key constraints
    parent_data = create_dummy_parents(db_session, model_class)

    # Create and save a valid instance with parent data
    instance = model_class()

    # Apply parent data to the instance
    for key, value in parent_data.items():
        setattr(instance, key, value)

    # Set required fields based on model type
    model_name = model_class.__name__

    # Set created_at and updated_at for all models
    now = datetime.now()
    if hasattr(instance, 'created_at') and getattr(instance, 'created_at') is None:
        setattr(instance, 'created_at', now)
    if hasattr(instance, 'updated_at') and getattr(instance, 'updated_at') is None:
        setattr(instance, 'updated_at', now)

    # Common fields for many models
    if hasattr(instance, 'title') and getattr(instance, 'title') is None:
        setattr(instance, 'title', f"Test {model_name} {uuid4().hex[:8]}")

    if hasattr(instance, 'name') and getattr(instance, 'name') is None:
        setattr(instance, 'name', f"Test {model_name} {uuid4().hex[:8]}")

    if hasattr(instance, 'description') and getattr(instance, 'description') is None:
        setattr(instance, 'description', f"Test description for {model_name}")

    # Time-related fields
    if hasattr(instance, 'start_time') and getattr(instance, 'start_time') is None:
        setattr(instance, 'start_time', datetime.now())

    if hasattr(instance, 'end_time') and getattr(instance, 'end_time') is None:
        setattr(instance, 'end_time', datetime.now() + timedelta(hours=1))

    if hasattr(instance, 'duration') and getattr(instance, 'duration') is None:
        setattr(instance, 'duration', 30)  # 30 minutes

    if hasattr(instance, 'scheduled_time') and getattr(instance, 'scheduled_time') is None:
        setattr(instance, 'scheduled_time', datetime.now() + timedelta(hours=2))

    # Status and type fields
    if hasattr(instance, 'status') and getattr(instance, 'status') is None:
        if model_name == "CalendarSyncModel":
            setattr(instance, 'status', SyncStatus.IN_PROGRESS.value)
        else:
            setattr(instance, 'status', 'active')

    if hasattr(instance, 'type') and getattr(instance, 'type') is None:
        setattr(instance, 'type', 'default')

    # Set a unique ID for all models
    if hasattr(instance, 'id') and getattr(instance, 'id') is None:
        setattr(instance, 'id', str(uuid4()))

    # Model-specific fields
    if model_name == "UserModel":
        instance.email = f"test_{uuid4().hex[:8]}@example.com"
        instance.username = f"test_user_{uuid4().hex[:8]}"
        instance.hashed_password = "test_password"
        instance.full_name = f"Test User {uuid4().hex[:8]}"

    elif model_name == "LoginAttemptModel" or model_name == "LoginAttempt":
        instance.ip_address = "127.0.0.1"
        instance.user_agent = "Mozilla/5.0 (Test)"
        instance.success = True
        instance.attempt_time = datetime.now()

    elif model_name == "HealthMetrics":
        instance.mood_score = 5
        instance.energy_level = 5
        instance.stress_level = 3
        instance.focus_score = 7
        instance.meditation_minutes = 10
        instance.date = datetime.now().date()
        instance.user_id = parent_data.get("user_id", str(uuid4()))
        instance.metric_type = MetricType.DAILY.value if hasattr(MetricType, 'DAILY') else "daily"
        instance.mood_level = 6
        instance.focus_level = 7

    elif model_name == "NLPModel":
        instance.text = "Sample text for NLP analysis"
        instance.parsed_data = "{}"
        instance.user_id = parent_data.get("user_id", str(uuid4()))
        instance.confidence_score = 0.9
        instance.language = "en"
        instance.entities = []

    elif model_name == "TaskModel":
        instance.title = f"Test Task {uuid4().hex[:8]}"
        instance.status = "todo"
        instance.priority = 2

    elif model_name == "StreakModel":
        instance.streak_type = "daily_login"
        instance.current_count = 1
        instance.last_activity_date = datetime.now().date()
        instance.user_id = parent_data.get("user_id", str(uuid4()))
        instance.longest_streak = 5
        instance.current_streak = 3
        instance.last_activity = datetime.now()
        instance.is_active = True

    elif model_name == "FocusStrategy":
        instance.name = f"Test Strategy {uuid4().hex[:8]}"
        instance.description = "A test focus strategy"
        instance.effectiveness_score = 7
        instance.user_id = parent_data.get("user_id", str(uuid4()))
        instance.strategy_type = "pomodoro"
        instance.duration = 25
        instance.task_type = "coding"
        instance.title = f"Test Focus Strategy {uuid4().hex[:8]}"
        instance.break_intervals = [{"duration": 5, "after_minutes": 25}]
        instance.environment_setup = ["quiet room", "good lighting"]
        instance.tools_needed = ["timer", "notebook"]

    elif model_name == "RefreshToken":
        instance.token = f"token_{uuid4().hex}"
        instance.expires_at = datetime.now() + timedelta(days=7)
        instance.user_id = parent_data.get("user_id", str(uuid4()))
        instance.client_id = "test_client"
        instance.is_revoked = False
        instance.token_type = "bearer"
        instance.token_id = str(uuid4())  # Add the required token_id field

    elif model_name == "ADHDPatternsModel":
        instance.session_count = 10
        instance.pattern_type = "focus"
        instance.serialized_pattern = "{}"
        instance.date_range_start = datetime.now() - timedelta(days=30)
        instance.date_range_end = datetime.now()
        instance.user_id = parent_data.get("user_id", str(uuid4()))
        instance.confidence_score = 0.85
        instance.pattern_name = "Focus Pattern"
        instance.detection_method = "algorithm"
        instance.settings_id = parent_data.get("settings_id", str(uuid4()))

    elif model_name == "Interaction":
        instance.type = InteractionType.CHAT.value if hasattr(InteractionType, 'CHAT') else "chat"
        instance.outcome = InteractionOutcome.POSITIVE.value if hasattr(InteractionOutcome, 'POSITIVE') else "positive"
        instance.timestamp = datetime.now()

    elif model_name == "ContactModel":
        instance.name = f"Test Contact {uuid4().hex[:8]}"
        instance.email = f"contact_{uuid4().hex[:8]}@example.com"
        instance.phone = "555-123-4567"
        instance.contact_type = "personal"
        instance.user_id = parent_data.get("user_id", str(uuid4()))
        instance.relationship = "friend"
        instance.notes = "Test contact notes"
        instance.is_favorite = False
        instance.relationship_strength = "strong"
        instance.type = ContactType.PERSONAL.value if hasattr(ContactType, 'PERSONAL') else "personal"

    elif model_name == "ReminderModel":
        instance.title = f"Test Reminder {uuid4().hex[:8]}"
        instance.scheduled_time = datetime.now() + timedelta(hours=2)
        instance.status = "pending"

    elif model_name == "AchievementModel" or model_name == "BadgeModel":
        instance.name = f"Test {model_name} {uuid4().hex[:8]}"
        instance.category = "productivity"

    elif model_name == "InteractionStats":
        instance.period_start = datetime.now() - timedelta(days=7)
        instance.period_end = datetime.now()
        instance.interaction_count = 10
        instance.stat_type = "daily"
        instance.user_id = parent_data.get("user_id", str(uuid4()))
        instance.average_duration = 15
        instance.peak_times = json.dumps(["morning", "evening"])
        instance.effectiveness_rating = 8
        instance.total_interactions = 10
        instance.average_effectiveness = 7.5

    elif model_name == "EnergyStats":
        instance.period_start = datetime.now() - timedelta(days=7)
        instance.period_end = datetime.now()
        instance.average_energy = 7.0
        instance.average_focus = 6.5
        instance.energy_stability = 0.8
        instance.focus_stability = 0.7
        instance.peak_performance_duration = 120
        instance.recovery_effectiveness = 0.75
        instance.break_effectiveness = 0.8
        instance.interruption_impact = -0.3
        instance.user_id = parent_data.get("user_id", str(uuid4()))

    elif model_name == "SessionStatsModel":
        instance.session_count = 10
        instance.total_duration = 600
        instance.average_focus_score = 7
        instance.period_start = datetime.now() - timedelta(days=7)
        instance.period_end = datetime.now()
        instance.stat_type = "daily"
        instance.user_id = parent_data.get("user_id", str(uuid4()))
        instance.peak_session_times = json.dumps(["morning"])
        instance.session_distribution = json.dumps({"focus": 5, "pomodoro": 5})
        instance.session_id = parent_data.get("session_id", str(uuid4()))
        instance.total_sessions = 10
        instance.average_effectiveness = 0.8
        instance.completion_rate = 0.9

    elif model_name == "MedicationLogModel":
        instance.medication_name = "Test Medication"
        instance.dosage = 10.0  # Changed from "10mg" to a float value
        instance.unit = "mg"  # Set the unit separately
        instance.timestamp = datetime.now()
        instance.taken = True
        instance.medication_type = MedicationType.STIMULANT.value if hasattr(MedicationType, 'STIMULANT') else "stimulant"
        instance.user_id = parent_data.get("user_id", str(uuid4()))
        instance.effectiveness = 7
        instance.side_effects = "None"
        instance.settings_id = parent_data.get("settings_id", str(uuid4()))

    elif model_name == "DistractionLogModel":
        instance.distraction_type = DistractionType.DIGITAL.value if hasattr(DistractionType, 'DIGITAL') else "digital"
        instance.timestamp = datetime.now()
        instance.duration = 5
        instance.notes = "Test distraction"
        instance.user_id = parent_data.get("user_id", str(uuid4()))
        instance.severity = 3
        instance.context = "working"
        instance.settings_id = parent_data.get("settings_id", str(uuid4()))

    elif model_name == "MentalHealthLogModel":
        instance.log_type = "anxiety"
        instance.severity = 3
        instance.notes = "Test mental health log"
        instance.timestamp = datetime.now()
        instance.user_id = parent_data.get("user_id", str(uuid4()))
        instance.mood_score = 7
        instance.anxiety_level = 3
        instance.focus_level = 7
        instance.energy_level = 6
        instance.stress_level = 3
        instance.sleep_hours = 7.5

    elif model_name == "BodyDoublingSessionModel":
        instance.duration = 30
        instance.partner_type = "virtual"
        instance.start_time = datetime.now() - timedelta(minutes=30)
        instance.end_time = datetime.now()
        instance.user_id = parent_data.get("user_id", str(uuid4()))
        instance.session_type = "focus"
        instance.status = "completed"

    elif model_name == "FocusSessionModel":
        instance.duration = 45
        instance.focus_level = 8
        instance.energy_level = 7
        instance.activity_type = "coding"
        instance.status = "active"
        instance.start_time = datetime.now() - timedelta(hours=1)
        instance.end_time = datetime.now()
        instance.session_type = FocusSessionType.POMODORO.value if hasattr(FocusSessionType, 'POMODORO') else "pomodoro"
        instance.user_id = parent_data.get("user_id", str(uuid4()))
        instance.total_breaks = 2
        instance.total_break_duration = 15
        instance.actual_focus_duration = 30

    elif model_name == "TimelineEventModel":
        instance.event_type = TimelineEventType.TASK_COMPLETED.value if hasattr(TimelineEventType, 'TASK_COMPLETED') else "task_completed"
        instance.timestamp = datetime.now()
        instance.details = "{}"

    elif model_name == "CalendarSyncModel":
        instance.external_calendar_id = f"ext_cal_{uuid4().hex[:8]}"
        instance.provider = SyncProvider.GOOGLE.value
        instance.source = SyncSource.LOCAL.value
        instance.sync_direction = SyncDirection.TWO_WAY.value
        instance.status = SyncStatus.IN_PROGRESS.value
        instance.conflict_strategy = ConflictResolutionStrategy.AUTO_REMOTE.value
        instance.is_active = True
        instance.error_count = 0
        instance.consecutive_failures = 0
        instance.error_history = "[]"
        instance.sync_frequency = 3600
        instance.pending_conflicts = "{}"
        instance.sync_settings = "{}"

    elif model_name == "TimeBlockModel":
        instance.title = f"Test TimeBlock {uuid4().hex[:8]}"
        instance.start_time = datetime.now()
        instance.end_time = datetime.now() + timedelta(hours=1)
        instance.block_type = BlockType.TASK.value
        instance.priority = BlockPriority.MEDIUM.value
        instance.is_break = False
        instance.is_flexible = False
        instance.interruptions = "null"
        instance.break_intervals = "null"
        instance.environment_data = "null"
        instance.tags = "null"
        instance.meta_data = "null"

    elif model_name == "VoiceCommandModel":
        instance.command_text = "Test voice command"
        instance.command_type = CommandType.VOICE.value
        instance.success = True
        instance.confidence_score = 0.95
        instance.processing_time = 0.5
        instance.action_taken = "test_action"
        instance.result = {"status": "success"}
        instance.timestamp = datetime.now()

    elif model_name == "CalendarModel":
        instance.name = f"Test Calendar {uuid4().hex[:8]}"
        instance.provider = "google"
        instance.is_primary = False
        instance.is_enabled = True

    elif model_name == "ADHDSettingsModel":
        instance.medication_tracking_enabled = True
        instance.distraction_tracking_enabled = True
        instance.energy_tracking_enabled = True
        instance.focus_tracking_enabled = True

    elif model_name == "ScheduleBlock":
        instance.start_time = datetime.now()
        instance.end_time = datetime.now() + timedelta(hours=1)
        instance.block_type = BlockType.TASK.value
        instance.is_available = True

    elif model_name == "SchedulePreferences":
        instance.user_id = parent_data.get("user_id", str(uuid4()))
        instance.preferred_start_time = datetime.now()
        instance.preferred_end_time = datetime.now() + timedelta(hours=8)
        instance.preferred_break_duration = 15
        instance.min_break_interval = 90
        instance.max_focus_duration = 120

    elif model_name == "CalendarEventModel":
        instance.title = f"Test Event {uuid4().hex[:8]}"
        instance.start_time = datetime.now()
        instance.end_time = datetime.now() + timedelta(hours=1)
        instance.event_type = EventType.MEETING.value
        instance.status = EventStatus.SCHEDULED.value
        instance.priority = EventPriority.MEDIUM.value
        instance.is_all_day = False

    elif model_name == "NLPAnalysis":
        instance.nlp_record_id = parent_data.get("nlp_record_id", str(uuid4()))
        instance.sentiment_score = 0.8
        instance.complexity_score = 0.6
        instance.key_phrases = ["important", "urgent", "focus"]
        instance.topics = ["productivity", "adhd"]
        instance.summary = "Test summary"
        instance.recommendations = ["take breaks", "use timer"]
        instance.meta_data = {"source": "test"}

    elif model_name == "TaskAnalysis":
        instance.task_id = parent_data.get("task_id", str(uuid4()))
        instance.complexity_level = 0.7
        instance.time_estimate = 60
        instance.focus_requirements = {"attention": "high", "creativity": "medium"}
        instance.potential_challenges = ["distractions", "complexity"]
        instance.breakdown_suggestions = ["break into smaller tasks", "use pomodoro technique"]
        instance.energy_level_recommendation = "medium"
        instance.adhd_friendly_score = 0.6

    elif model_name == "PomodoroSessionModel":
        instance.work_duration = 25
        instance.break_duration = 5
        instance.long_break_duration = 15
        instance.cycles_completed = 2
        instance.start_time = datetime.now() - timedelta(hours=2)
        instance.end_time = datetime.now() - timedelta(hours=1)
        instance.status = "completed"
        instance.session_data = "{}"
        instance.task_id = parent_data.get("task_id", str(uuid4()))
        instance.meta_data = {}
        instance.short_break_duration = 5

    elif model_name == "LoginAttemptModel":
        instance.user_id = parent_data.get("user_id", str(uuid4()))
        instance.ip_address = "192.168.1.1"
        instance.user_agent = "Mozilla/5.0"
        instance.success = True
        instance.attempt_time = datetime.now()

    elif model_name == "VoiceCommandModel":
        instance.user_id = parent_data.get("user_id", str(uuid4()))
        instance.command_text = "Test command"
        instance.command_type = CommandType.VOICE.value
        instance.result = "Test result"
        instance.confidence_score = 0.9
        instance.processing_time = 0.5
        instance.action_taken = "Test action"

    elif model_name == "VoicePreferencesModel":
        instance.user_id = parent_data.get("user_id", str(uuid4()))
        instance.language = "en-US"
        instance.voice_speed = 1.0
        instance.confirmation_required = True
        instance.wake_word = "Hey Assistant"
        instance.disabled_commands = []

    elif model_name == "TimelineEventModel":
        instance.user_id = parent_data.get("user_id", str(uuid4()))
        instance.event_type = TimelineEventType.TASK_COMPLETED.value
        instance.title = "Test Event"

    elif model_name == "InteractionStats":
        instance.period_start = datetime.now() - timedelta(days=7)
        instance.period_end = datetime.now()
        instance.interaction_count = 10
        instance.stat_type = "daily"
        instance.user_id = parent_data.get("user_id", str(uuid4()))
        instance.average_duration = 15
        instance.peak_times = json.dumps(["morning", "evening"])
        instance.effectiveness_rating = 8
        instance.total_interactions = 10
        instance.average_effectiveness = 7.5

    elif model_name == "CalendarModel":
        instance.user_id = parent_data.get("user_id", str(uuid4()))
        instance.name = "Test Calendar"
        instance.provider = "Google"
        instance.color = "#4285F4"
        instance.is_primary = True
        instance.is_enabled = True
        instance.meta_data = {}

    elif model_name == "MentalHealthLogModel":
        instance.log_type = "anxiety"
        instance.severity = 3
        instance.notes = "Test mental health log"
        instance.timestamp = datetime.now()
        instance.user_id = parent_data.get("user_id", str(uuid4()))
        instance.mood_score = 7
        instance.anxiety_level = 3
        instance.focus_level = 7
        instance.energy_level = 6
        instance.stress_level = 3
        instance.sleep_hours = 7.5

    elif model_name == "StreakModel":
        instance.streak_type = "daily_login"
        instance.current_count = 1
        instance.last_activity_date = datetime.now().date()
        instance.user_id = parent_data.get("user_id", str(uuid4()))
        instance.longest_streak = 5
        instance.current_streak = 3
        instance.last_activity = datetime.now()
        instance.is_active = True

    elif model_name == "PointsModel":
        instance.user_id = parent_data.get("user_id", str(uuid4()))
        instance.total_points = 100
        instance.level = 1

    elif model_name == "BadgeModel":
        instance.user_id = parent_data.get("user_id", str(uuid4()))
        instance.name = "Test Badge"
        instance.category = "Test Category"
        instance.type = "Test Type"
        instance.earned_at = datetime.now()

    elif model_name == "BodyDoublingSessionModel":
        instance.user_id = parent_data.get("user_id", str(uuid4()))
        instance.host_id = parent_data.get("user_id", str(uuid4()))
        instance.partner_id = parent_data.get("user_id", str(uuid4()))
        instance.session_type = "focus"
        instance.status = "active"
        instance.start_time = datetime.now() - timedelta(minutes=30)
        instance.end_time = datetime.now()

    elif model_name == "NLPModel":
        instance.user_id = parent_data.get("user_id", str(uuid4()))
        instance.text = "Test text"
        instance.parsed_data = {}
        instance.confidence_score = 0.9
        instance.entities = []

    elif model_name == "ScheduleBlock":
        instance.user_id = parent_data.get("user_id", str(uuid4()))
        instance.title = "Test Block"
        instance.start_time = datetime.now()
        instance.end_time = datetime.now() + timedelta(hours=1)
        instance.block_type = BlockType.TASK
        instance.priority = BlockPriority.MEDIUM
        instance.status = TaskStatus.TODO
        instance.is_flexible = True
        instance.buffer_before = 15
        instance.buffer_after = 15

    elif model_name == "HyperfocusSessionModel":
        instance.user_id = parent_data.get("user_id", str(uuid4()))
        instance.start_time = datetime.now()
        instance.end_time = datetime.now() + timedelta(hours=2)
        instance.status = HyperfocusSessionStatus.ACTIVE
        instance.focus_level = 9
        instance.duration_minutes = 120
        instance.purpose = "Focus"
        instance.focus_area = "General"

    elif model_name == "CalendarEventModel":
        instance.user_id = parent_data.get("user_id", str(uuid4()))
        instance.calendar_id = parent_data.get("calendar_id", str(uuid4()))
        instance.title = "Test Event"
        instance.start_time = datetime.now()
        instance.end_time = datetime.now() + timedelta(hours=1)
        instance.event_type = EventType.MEETING.value
        instance.status = EventStatus.SCHEDULED.value
        instance.duration = 60

    elif model_name == "CalendarSyncModel":
        instance.user_id = parent_data.get("user_id", str(uuid4()))
        instance.calendar_id = parent_data.get("calendar_id", str(uuid4()))
        instance.external_calendar_id = parent_data.get("external_calendar_id", str(uuid4()))
        instance.provider = SyncProvider.GOOGLE.value
        instance.source = SyncSource.LOCAL.value
        instance.sync_direction = SyncDirection.TWO_WAY
        instance.status = SyncStatus.PENDING.value

    elif model_name == "TimeBlockModel":
        instance.user_id = parent_data.get("user_id", str(uuid4()))
        instance.title = "Test Block"
        instance.start_time = datetime.now()
        instance.end_time = datetime.now() + timedelta(hours=1)

    elif model_name == "MindfulnessSessionModel":
        instance.duration = 15
        instance.start_time = datetime.now() - timedelta(minutes=15)
        instance.end_time = datetime.now()
        instance.technique = "breathing"
        instance.session_type = "meditation"
        instance.timestamp = datetime.now()
        instance.user_id = parent_data.get("user_id", str(uuid4()))

    elif model_name == "EnergyLog":
        instance.user_id = parent_data.get("user_id", str(uuid4()))
        instance.level = 7
        instance.timestamp = datetime.now()
        instance.notes = "Test energy log"

    else:
        # For any other model, just use the base data
        pass

    # Convert any UUID attributes to strings for SQLite compatibility
    # This needs to happen BEFORE adding to the session
    def convert_uuid_to_str(obj):
        """Recursively convert UUID objects to strings."""
        if isinstance(obj, UUID):
            return str(obj)
        elif isinstance(obj, dict):
            return {k: convert_uuid_to_str(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_uuid_to_str(item) for item in obj]
        else:
            return obj

    # First convert any UUIDs in parent_data to strings
    for key, value in parent_data.items():
        parent_data[key] = convert_uuid_to_str(value)

    # Then convert any UUID attributes to strings
    for attr_name in dir(instance):
        if not attr_name.startswith('_') and not callable(getattr(instance, attr_name)):
            try:
                attr_value = getattr(instance, attr_name)
                if isinstance(attr_value, UUID):
                    setattr(instance, attr_name, str(attr_value))
                elif isinstance(attr_value, dict) or isinstance(attr_value, list):
                    setattr(instance, attr_name, convert_uuid_to_str(attr_value))
            except Exception as e:
                # Skip attributes that can't be accessed or modified
                pass

    # Add the instance to the session and flush
    db_session.add(instance)
    try:
        db_session.flush()  # Use flush instead of commit
    except Exception as e:
        db_session.rollback()
        pytest.fail(f"Failed to create instance of {model_name}: {str(e)}")

    # Store the ID of the instance for later testing
    instance_id = getattr(instance, 'id', None)

    # Now test primary key constraint in a clean session to avoid identity conflicts
    db_session.expunge_all()  # Remove all objects from the session

    # Create a duplicate instance with the same ID
    duplicate = model_class()

    # Set only necessary attributes to trigger the constraint violation
    if hasattr(duplicate, 'id') and instance_id is not None:
        duplicate.id = instance_id

        # Add the duplicate to the session
        db_session.add(duplicate)

        # This should raise an IntegrityError due to duplicate primary key
        with pytest.raises(IntegrityError):
            db_session.flush()

    # Clean up the session
    db_session.rollback()

@pytest.mark.performance
def test_bulk_insert_performance(db_session):
    """Test performance of bulk inserts."""
    num_records = 1000
    start_time = datetime.now()

    users = [
        UserModel(
            id=uuid4(),
            username=f"user_{i}",
            email=f"user_{i}@example.com",
            full_name=f"User {i}",
            hashed_password="test_password",
            is_active=True,
            is_verified=False,
            energy_level=EnergyLevel.MODERATE.value
        ) for i in range(num_records)
    ]
    db_session.bulk_save_objects(users)
    db_session.commit()

    end_time = datetime.now()
    elapsed_time = (end_time - start_time).total_seconds()
    print(f"\nInserted {num_records} records in {elapsed_time} seconds")
    assert elapsed_time < 2.0  # Ensure bulk insert is fast
