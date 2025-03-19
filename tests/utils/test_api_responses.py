"""
Tests for API response utilities.

This module contains tests for the standardized API response utilities.
"""

import pytest
from fastapi import status
from pydantic import ValidationError, BaseModel, Field

from app.utils.api_responses import (
    create_response,
    create_collection_response,
    create_error_response,
    format_validation_errors,
    not_found_response,
    forbidden_response,
    unauthorized_response,
    validation_error_response,
    conflict_response,
    server_error_response,
    rate_limit_response,
)


def test_create_response():
    """Test create_response function."""
    data = {"key": "value"}
    response = create_response(data)
    
    assert response == data


def test_create_collection_response():
    """Test create_collection_response function."""
    items = [{"id": 1}, {"id": 2}, {"id": 3}]
    total = 10
    page = 1
    page_size = 3
    
    response = create_collection_response(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )
    
    # Check the structure of the response
    assert response.items == items
    assert response.pagination.total == total
    assert response.pagination.page == page
    assert response.pagination.page_size == page_size
    assert response.pagination.pages == 4  # Calculated from total/page_size, rounded up
    assert response.pagination.has_next is True
    assert response.pagination.has_prev is False


def test_create_collection_response_last_page():
    """Test create_collection_response function with last page."""
    items = [{"id": 7}, {"id": 8}, {"id": 9}]
    total = 9
    page = 3
    page_size = 3
    
    response = create_collection_response(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )
    
    # Check the pagination info for last page
    assert response.pagination.pages == 3
    assert response.pagination.has_next is False
    assert response.pagination.has_prev is True


def test_create_error_response():
    """Test create_error_response function."""
    code = "TEST_ERROR"
    message = "Test error message"
    details = {"field1": ["Error 1", "Error 2"]}
    
    response = create_error_response(
        code=code,
        message=message,
        details=details,
        status_code=status.HTTP_400_BAD_REQUEST,
    )
    
    # Check the structure of the response
    assert response["status"] == "error"
    assert response["code"] == code
    assert response["message"] == message
    assert response["details"] == details


def test_format_validation_errors():
    """Test format_validation_errors function."""
    # Create a validation error
    class TestModel(BaseModel):
        name: str = Field(..., min_length=3)
        age: int = Field(..., gt=0)
    
    try:
        TestModel(name="A", age=0)
        pytest.fail("Validation should have failed")
    except ValidationError as e:
        # Format the validation error
        errors = format_validation_errors(e)
        
        # Check the structure of the errors
        assert "name" in errors
        assert "age" in errors
        assert any("shorter than 3" in msg for msg in errors["name"])
        assert any("greater than 0" in msg for msg in errors["age"])


def test_not_found_response():
    """Test not_found_response function."""
    resource_type = "User"
    resource_id = "123"
    
    response = not_found_response(resource_type, resource_id)
    
    # Check the structure of the response
    assert response["status"] == "error"
    assert response["code"] == "NOT_FOUND"
    assert f"{resource_type} with ID '{resource_id}' not found" in response["message"]


def test_forbidden_response():
    """Test forbidden_response function."""
    message = "Custom forbidden message"
    
    response = forbidden_response(message)
    
    # Check the structure of the response
    assert response["status"] == "error"
    assert response["code"] == "FORBIDDEN"
    assert response["message"] == message


def test_unauthorized_response():
    """Test unauthorized_response function."""
    response = unauthorized_response()
    
    # Check the structure of the response
    assert response["status"] == "error"
    assert response["code"] == "UNAUTHORIZED"
    assert "Authentication required" in response["message"]


def test_validation_error_response():
    """Test validation_error_response function."""
    details = {"field1": ["Error 1"], "field2": ["Error 2"]}
    
    response = validation_error_response(details)
    
    # Check the structure of the response
    assert response["status"] == "error"
    assert response["code"] == "VALIDATION_ERROR"
    assert "Invalid request parameters" in response["message"]
    assert response["details"] == details


def test_conflict_response():
    """Test conflict_response function."""
    message = "Resource already exists"
    
    response = conflict_response(message)
    
    # Check the structure of the response
    assert response["status"] == "error"
    assert response["code"] == "RESOURCE_CONFLICT"
    assert response["message"] == message


def test_server_error_response():
    """Test server_error_response function."""
    response = server_error_response()
    
    # Check the structure of the response
    assert response["status"] == "error"
    assert response["code"] == "INTERNAL_ERROR"
    assert "An unexpected error occurred" in response["message"]


def test_rate_limit_response():
    """Test rate_limit_response function."""
    retry_after = 60
    
    response = rate_limit_response(retry_after)
    
    # Check the structure of the response
    assert response["status"] == "error"
    assert response["code"] == "RATE_LIMIT_EXCEEDED"
    assert f"Rate limit exceeded. Try again after {retry_after} seconds" in response["message"] 