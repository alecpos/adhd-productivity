"""
Route Utilities

This module provides utilities for creating API routes that conform to the
API design guidelines.
"""

from typing import Any, Callable, Dict, List, Optional, Type, Union

from fastapi import Depends, HTTPException, Path, Query, status
from pydantic import BaseModel
from uuid import UUID

from app.utils.api_responses import create_error_response


def error_responses(*status_codes: int) -> Dict[int, Dict[str, Any]]:
    """
    Define standard error responses for FastAPI route documentation.
    
    Args:
        *status_codes: The HTTP status codes to include
        
    Returns:
        A dictionary mapping status codes to response descriptions
    """
    responses = {}
    
    error_descriptions = {
        status.HTTP_400_BAD_REQUEST: {
            "description": "Bad Request - Invalid input data",
            "model": dict  # Using dict as a placeholder for ErrorResponse
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Unauthorized - Authentication required",
            "model": dict
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "Forbidden - Insufficient permissions",
            "model": dict
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Not Found - Resource not found",
            "model": dict
        },
        status.HTTP_409_CONFLICT: {
            "description": "Conflict - Resource conflict",
            "model": dict
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Unprocessable Entity - Validation error",
            "model": dict
        },
        status.HTTP_429_TOO_MANY_REQUESTS: {
            "description": "Too Many Requests - Rate limit exceeded",
            "model": dict
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Internal Server Error - Unexpected server error",
            "model": dict
        }
    }
    
    # If no specific codes are provided, include all
    if not status_codes:
        return error_descriptions
    
    # Include only the specified codes
    for code in status_codes:
        if code in error_descriptions:
            responses[code] = error_descriptions[code]
    
    return responses


def pagination_params(
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(20, ge=1, le=100, description="Number of items per page"),
) -> Dict[str, int]:
    """
    Standard pagination parameters for collection endpoints.
    
    Args:
        page: The page number (1-based)
        page_size: The number of items per page
        
    Returns:
        A dictionary with pagination parameters
    """
    return {"page": page, "page_size": page_size}


def id_path_param(resource_name: str) -> Callable[[UUID], UUID]:
    """
    Create a standard ID path parameter for resource endpoints.
    
    Args:
        resource_name: The name of the resource (e.g., 'task', 'user')
        
    Returns:
        A function that validates the ID parameter
    """
    
    def validate_id(
        id: UUID = Path(..., description=f"The unique identifier of the {resource_name}")
    ) -> UUID:
        return id
    
    return validate_id


def validate_resource_access(
    resource_owner_id: UUID, current_user_id: UUID, is_admin: bool = False
) -> None:
    """
    Validate that the current user has access to a resource.
    
    Args:
        resource_owner_id: The ID of the resource owner
        current_user_id: The ID of the current user
        is_admin: Whether the current user is an admin
        
    Raises:
        HTTPException: If the user does not have access to the resource
    """
    if resource_owner_id != current_user_id and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=create_error_response(
                code="FORBIDDEN",
                message="You do not have permission to access this resource",
                status_code=status.HTTP_403_FORBIDDEN,
            ),
        )


def rate_limit_error(retry_after: int) -> HTTPException:
    """
    Create a rate limit error.
    
    Args:
        retry_after: Seconds until the rate limit resets
        
    Returns:
        An HTTPException with a rate limit error
    """
    return HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail=create_error_response(
            code="RATE_LIMIT_EXCEEDED",
            message=f"Rate limit exceeded. Try again after {retry_after} seconds",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        ),
        headers={"Retry-After": str(retry_after)},
    )


def not_found_error(resource_type: str, resource_id: Any) -> HTTPException:
    """
    Create a not found error.
    
    Args:
        resource_type: The type of resource (e.g., 'task', 'user')
        resource_id: The ID of the resource
        
    Returns:
        An HTTPException with a not found error
    """
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=create_error_response(
            code="NOT_FOUND",
            message=f"{resource_type} with ID '{resource_id}' not found",
            status_code=status.HTTP_404_NOT_FOUND,
        ),
    )


def forbidden_error(message: str = "You do not have permission to perform this action") -> HTTPException:
    """
    Create a forbidden error.
    
    Args:
        message: The error message
        
    Returns:
        An HTTPException with a forbidden error
    """
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=create_error_response(
            code="FORBIDDEN",
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
        ),
    )


def validation_error(errors: Dict[str, List[str]]) -> HTTPException:
    """
    Create a validation error.
    
    Args:
        errors: Field-specific validation errors
        
    Returns:
        An HTTPException with a validation error
    """
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=create_error_response(
            code="VALIDATION_ERROR",
            message="Invalid request parameters",
            details=errors,
            status_code=status.HTTP_400_BAD_REQUEST,
        ),
    )


def conflict_error(message: str) -> HTTPException:
    """
    Create a conflict error.
    
    Args:
        message: The error message
        
    Returns:
        An HTTPException with a conflict error
    """
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=create_error_response(
            code="RESOURCE_CONFLICT",
            message=message,
            status_code=status.HTTP_409_CONFLICT,
        ),
    ) 