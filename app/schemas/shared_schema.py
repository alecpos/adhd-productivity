"""Shared schemas for common functionality."""

from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, TypeVar
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.base_schema import BaseSchema, BaseResponse, PaginatedResponse, TimeRange

T = TypeVar("T")

# Re-export base schemas for backward compatibility
__all__ = ["BaseSchema", "BaseResponse", "PaginatedResponse", "TimeRange"]
