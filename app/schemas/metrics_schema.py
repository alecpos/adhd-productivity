"""Metrics schemas module."""

from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import ConfigDict, Field

from app.schemas.base_schema import BaseSchema


class RouteMetricsSchema(BaseSchema):
    """Schema for route metrics."""
    route_id: UUID
    path: str
    method: str
    total_requests: int = Field(default=0, ge=0)
    successful_requests: int = Field(default=0, ge=0)
    failed_requests: int = Field(default=0, ge=0)
    average_response_time: float = Field(default=0.0, ge=0.0)
    last_accessed: Optional[datetime] = None
    status_codes: Dict[str, int] = Field(default_factory=dict)
    error_types: Dict[str, int] = Field(default_factory=dict)
    user_agents: Dict[str, int] = Field(default_factory=dict)
    ip_addresses: Dict[str, int] = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)


class RouteMetricsListSchema(BaseSchema):
    """Schema for list of route metrics."""
    metrics: List[RouteMetricsSchema]
    total_routes: int = Field(..., ge=0)

    model_config = ConfigDict(from_attributes=True)


class RouteMetricsUpdateSchema(BaseSchema):
    """Schema for updating route metrics."""
    total_requests: Optional[int] = Field(None, ge=0)
    successful_requests: Optional[int] = Field(None, ge=0)
    failed_requests: Optional[int] = Field(None, ge=0)
    average_response_time: Optional[float] = Field(None, ge=0.0)
    last_accessed: Optional[datetime] = None
    status_codes: Optional[Dict[str, int]] = None
    error_types: Optional[Dict[str, int]] = None
    user_agents: Optional[Dict[str, int]] = None
    ip_addresses: Optional[Dict[str, int]] = None

    model_config = ConfigDict(from_attributes=True) 