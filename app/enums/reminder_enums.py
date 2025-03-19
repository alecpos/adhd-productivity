"""Reminder enums module."""

from enum import Enum

class ReminderType(Enum):
    """Reminder type enum."""
    MENTAL_HEALTH_CHECK = "mental_health_check"
    TASK_DUE = "task_due"
    FOCUS_SESSION = "focus_session"
    BREAK_TIME = "break_time"
    MEDICATION = "medication"
    WATER = "water"
    EXERCISE = "exercise"
    CUSTOM = "custom"

class ReminderFrequency(Enum):
    """Reminder frequency enum."""
    ONCE = "once"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"

class ReminderType(Enum):
    MENTAL_HEALTH_CHECK = "mental_health_check"
    COPING_STRATEGY = "coping_strategy"
    MEDICATION = "medication"
    CUSTOM = "custom"


class ReminderFrequency(Enum):
    NEVER = "never"
    DAILY = "daily"
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"
