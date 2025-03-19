"""
API Response Utilities

This module provides standardized response formatters for the ADHD Calendar API.
It ensures consistent response structure across all API endpoints.
"""

from typing import Any, Dict, Generic, List, Optional, TypeVar, Union
from fastapi import status
from pydantic import BaseModel, Field, RootModel

T = TypeVar('T')


class PaginationMetadata(BaseModel):
    """Metadata for paginated response."""
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number (1-based)")
    page_size: int = Field(..., description="Number of items per page")
    pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_prev: bool = Field(..., description="Whether there is a previous page")


class CollectionResponse(BaseModel, Generic[T]):
    """Standard response for collections."""
    items: List[T] = Field(..., description="Collection of items")
    pagination: PaginationMetadata = Field(..., description="Pagination metadata")


# Use RootModel instead of __root__ field for field-specific errors
class ErrorDetails(RootModel[Dict[str, List[str]]]):
    """Details for field-specific errors.
    
    Maps field names to lists of error messages.
    """
    model_config = {
        "json_schema_extra": {
            "description": "Field-specific error messages, keyed by field name"
        }
    }


class ErrorResponse(BaseModel):
    """Standard error response."""
    status: str = Field("error", description="Status indicator, always 'error' for errors")
    code: str = Field(..., description="Error code for programmatic handling")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, List[str]]] = Field(
        {},
        description="Field-specific error details"
    )


def create_response(data: Any) -> Dict[str, Any]:
    """
    Create a standard success response.
    
    Args:
        data: The response data
        
    Returns:
        A formatted success response
    """
    return data


def create_collection_response(
    items: List[Any],
    total: int,
    page: int,
    page_size: int
) -> CollectionResponse:
    """
    Create a standard collection response with pagination.
    
    Args:
        items: The collection items
        total: Total number of items across all pages
        page: Current page number (1-based)
        page_size: Number of items per page
        
    Returns:
        A formatted collection response with pagination metadata
    """
    pages = (total + page_size - 1) // page_size if page_size > 0 else 0
    
    pagination = PaginationMetadata(
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
        has_next=page < pages,
        has_prev=page > 1
    )
    
    return CollectionResponse(
        items=items,
        pagination=pagination
    )


def create_error_response(
    code: str,
    message: str,
    details: Optional[Dict[str, List[str]]] = None,
    status_code: int = status.HTTP_400_BAD_REQUEST
) -> Dict[str, Union[str, Dict[str, List[str]]]]:
    """
    Create a standard error response.
    
    Args:
        code: Error code for programmatic handling
        message: Human-readable error message
        details: Field-specific error details
        status_code: HTTP status code (not included in response)
        
    Returns:
        A formatted error response
    """
    return ErrorResponse(
        code=code,
        message=message,
        details=details or {}
    ).dict()


def format_validation_errors(validation_error: Any) -> Dict[str, List[str]]:
    """
    Format Pydantic ValidationError into a field-specific error dict.
    
    Args:
        validation_error: Pydantic ValidationError
        
    Returns:
        Dict with field names as keys and lists of error messages as values
    """
    errors: Dict[str, List[str]] = {}
    
    for error in validation_error.errors():
        location = error["loc"]
        field_name = location[-1] if len(location) > 0 else "non_field_error"
        
        if isinstance(field_name, int):
            # Handle array validation errors
            field_name = f"{location[-2]}[{field_name}]"
        
        if field_name not in errors:
            errors[field_name] = []
            
        errors[field_name].append(error["msg"])
    
    return errors


# Predefined responses for common scenarios
def not_found_response(resource_type: str, resource_id: Any) -> Dict[str, Any]:
    """Create a standard not found error response."""
    return create_error_response(
        code="NOT_FOUND",
        message=f"{resource_type} with ID '{resource_id}' not found",
        status_code=status.HTTP_404_NOT_FOUND
    )


def forbidden_response(message: str = "You do not have permission to perform this action") -> Dict[str, Any]:
    """Create a standard forbidden error response."""
    return create_error_response(
        code="FORBIDDEN",
        message=message,
        status_code=status.HTTP_403_FORBIDDEN
    )


def unauthorized_response(message: str = "Authentication required") -> Dict[str, Any]:
    """Create a standard unauthorized error response."""
    return create_error_response(
        code="UNAUTHORIZED",
        message=message,
        status_code=status.HTTP_401_UNAUTHORIZED
    )


def validation_error_response(details: Dict[str, List[str]]) -> Dict[str, Any]:
    """Create a standard validation error response."""
    return create_error_response(
        code="VALIDATION_ERROR",
        message="Invalid request parameters",
        details=details,
        status_code=status.HTTP_400_BAD_REQUEST
    )


def conflict_response(message: str) -> Dict[str, Any]:
    """Create a standard conflict error response."""
    return create_error_response(
        code="RESOURCE_CONFLICT",
        message=message,
        status_code=status.HTTP_409_CONFLICT
    )


def server_error_response(message: str = "An unexpected error occurred") -> Dict[str, Any]:
    """Create a standard server error response."""
    return create_error_response(
        code="INTERNAL_ERROR",
        message=message,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )


def rate_limit_response(retry_after: int) -> Dict[str, Any]:
    """Create a standard rate limit error response."""
    return create_error_response(
        code="RATE_LIMIT_EXCEEDED",
        message=f"Rate limit exceeded. Try again after {retry_after} seconds",
        status_code=status.HTTP_429_TOO_MANY_REQUESTS
    ) 