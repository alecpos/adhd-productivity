"""Health schemas for system health monitoring."""

from typing import Dict, Any, Optional
from datetime import datetime

from app.schemas.base_schema import BaseSchema


class HealthMetricsSchema(BaseSchema):
    """Schema for health metrics data."""
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    uptime: float
    last_check: datetime


class HealthCheckSchema(BaseSchema):
    """Schema for health check data."""
    status: str
    timestamp: datetime
    details: Dict[str, Any]
    message: Optional[str] = None
