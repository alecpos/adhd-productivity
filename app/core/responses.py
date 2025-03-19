"""Core responses module."""

from typing import Any, Dict, Generic, List, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    """API response model."""

    status: str = "success"
    message: str
    data: Optional[T] = None
    meta: Optional[Dict[str, Any]] = None


class ErrorResponse(BaseModel):
    """Error response model."""

    message: str
    code: str
    details: Optional[Dict[str, Any]] = None


class PaginatedResponse(APIResponse[List[T]], Generic[T]):
    """Paginated API response model."""

    page: int
    page_size: int
    total: int
    has_more: bool
