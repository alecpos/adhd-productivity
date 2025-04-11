from datetime import datetime, timedelta
from typing import List, Dict, Any
from dateutil.rrule import rrule, DAILY, WEEKLY, MONTHLY, YEARLY

def get_recurring_dates(
    start_date: datetime,
    recurrence_pattern: Dict[str, Any],
    range_start: datetime,
    range_end: datetime
) -> List[datetime]:
    """Generate recurring dates based on pattern."""
    freq_map = {
        "daily": DAILY,
        "weekly": WEEKLY,
        "monthly": MONTHLY,
        "yearly": YEARLY
    }

    freq = freq_map.get(recurrence_pattern.get("frequency", "").lower())
    if not freq:
        return []

    interval = recurrence_pattern.get("interval", 1)

    dates = list(rrule(
        freq=freq,
        interval=interval,
        dtstart=start_date,
        until=range_end
    ))

    # Filter dates within the range
    return [d for d in dates if range_start <= d <= range_end]

def calculate_duration(start_time: datetime, end_time: datetime) -> int:
    """Calculate duration in minutes between two datetimes."""
    return int((end_time - start_time).total_seconds() / 60)

def add_buffer_time(duration: int, complexity: int = 1) -> int:
    """Add buffer time based on task complexity."""
    buffer_factor = 1 + (complexity * 0.2)  # 20% per complexity level
    return int(duration * buffer_factor)

def get_next_available_slot(
    start_time: datetime,
    duration: int,
    existing_events: List[Dict[str, datetime]]
) -> datetime:
    """Find next available time slot."""
    current_time = start_time
    while True:
        end_time = current_time + timedelta(minutes=duration)
        conflicts = [
            event for event in existing_events
            if (event["start_time"] < end_time and event["end_time"] > current_time)
        ]

        if not conflicts:
            return current_time

        # Move to the end of the latest conflicting event
        current_time = max(event["end_time"] for event in conflicts)
