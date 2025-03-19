"""Schedule parameters schema."""

from datetime import time
from typing import Any, Dict, List

from pydantic import BaseModel, Field, validator


class TimeRange(BaseModel):
    """Time range with start and end times."""

    start: str
    end: str

    @validator("start", "end")
    def validate_time_format(cls, v: str) -> str:
        try:
            hour, minute = map(int, v.split(":"))
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                raise ValueError(
                    "Time values must be within valid ranges (hours: 0-23, minutes: 0-59)"
                )
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid time format: {str(e)}")
        return v


class WorkHours(BaseModel):
    """Work hours configuration."""

    start: str = Field(default="09:00")  # 9 AM default
    end: str = Field(default="17:00")  # 5 PM default
    breaks: List[TimeRange] = Field(default_factory=list)

    @validator("start", "end")
    def validate_time_format(cls, v: str) -> str:
        try:
            hour, minute = map(int, v.split(":"))
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                raise ValueError(
                    "Time values must be within valid ranges (hours: 0-23, minutes: 0-59)"
                )
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid time format: {str(e)}")
        return v

    def to_time_objects(self) -> Dict[str, Any]:
        """Convert string times to time objects."""
        start_hour, start_minute = map(int, self.start.split(":"))
        end_hour, end_minute = map(int, self.end.split(":"))

        result = {
            "start": time(hour=start_hour, minute=start_minute),
            "end": time(hour=end_hour, minute=end_minute),
            "breaks": [],
        }

        for break_time in self.breaks:
            break_start_hour, break_start_minute = map(int, break_time.start.split(":"))
            break_end_hour, break_end_minute = map(int, break_time.end.split(":"))
            result["breaks"].append(
                {
                    "start": time(hour=break_start_hour, minute=break_start_minute),
                    "end": time(hour=break_end_hour, minute=break_end_minute),
                }
            )

        return result


class EnergyPattern(BaseModel):
    """Energy pattern configuration."""

    pattern_type: str = "morning"  # morning, afternoon, evening
    peak_hours: List[TimeRange] = Field(default_factory=list)
    low_energy_periods: List[TimeRange] = Field(default_factory=list)


class ScheduleParams(BaseModel):
    """Parameters for schedule generation."""

    tasks: List[Dict[str, Any]]
    work_hours: WorkHours
    energy_pattern: EnergyPattern
    block_duration: int = 30  # minutes
    break_duration: int = 15  # minutes
    focus_duration: int = 45  # minutes
    preferences: Dict[str, Any] = Field(default_factory=dict)
    constraints: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        arbitrary_types_allowed = True 