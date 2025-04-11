"""Schema package initialization."""

from app.schemas.analytics_schema import (
    AnalyticsSchema,
    AnalyticsResponseSchema,
    UserInsightsResponseSchema,
)
from app.schemas.auth_schema import Token, TokenData, TokenResponse
from app.schemas.body_doubling_schema import (
    BodyDoublingSchema,
    CreateBodyDoublingSchema,
    UpdateBodyDoublingSchema,
    BodyDoublingResponseSchema,
    BodyDoublingListSchema,
    InteractionSchema,
)
from app.schemas.calendar_event_schema import EventSchema
from app.schemas.calendar_schema import CalendarSchema
from app.schemas.mental_health_schema import (
    MentalHealthLogCreateSchema,
    MentalHealthLogResponseSchema,
    MentalHealthLogUpdateSchema,
)
from app.schemas.pomodoro_schema import (
    PomodoroCreateSchema,
    PomodoroResponseSchema,
    PomodoroUpdateSchema,
)
from app.schemas.task_schema import (
    TaskSchema,
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskListResponse,
    TaskStatsSchema,
)
from app.schemas.user_schema import (
    UserCreateSchema,
    UserResponseSchema,
    UserSchema,
    UserUpdateSchema,
)

__all__ = [
    "AnalyticsSchema",
    "AnalyticsResponseSchema",
    "UserInsightsResponseSchema",
    "UserSchema",
    "UserCreateSchema",
    "UserUpdateSchema",
    "UserResponseSchema",
    "TaskSchema",
    "TaskCreate",
    "TaskUpdate",
    "TaskResponse",
    "TaskListResponse",
    "TaskStatsSchema",
    "PomodoroCreateSchema",
    "PomodoroResponseSchema",
    "PomodoroUpdateSchema",
    "MentalHealthLogCreateSchema",
    "MentalHealthLogResponseSchema",
    "MentalHealthLogUpdateSchema",
    "CalendarSchema",
    "EventSchema",
    "BodyDoublingSchema",
    "CreateBodyDoublingSchema",
    "UpdateBodyDoublingSchema",
    "BodyDoublingResponseSchema",
    "BodyDoublingListSchema",
    "InteractionSchema",
    "Token",
    "TokenData",
    "TokenResponse",
]
