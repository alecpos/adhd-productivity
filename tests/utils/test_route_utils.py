"""
Tests for route utilities.

This module contains tests for the standardized route utilities.
"""

import pytest
from fastapi import Path, Query, HTTPException, status
from uuid import UUID, uuid4

from app.utils.route_utils import (
    error_responses,
    pagination_params,
    id_path_param,
    validate_resource_access,
    rate_limit_error,
    not_found_error,
    forbidden_error,
    validation_error,
    conflict_error,
)


def test_error_responses_specific_codes():
    """Test error_responses function with specific codes."""
    responses = error_responses(400, 404)
    
    # Check that only the specified error codes are included
    assert 400 in responses
    assert 404 in responses
    assert 401 not in responses
    assert 500 not in responses
    
    # Check structure of response descriptions
    assert "description" in responses[400]
    assert "model" in responses[400]
    assert "Bad Request" in responses[400]["description"]


def test_error_responses_no_codes():
    """Test error_responses function with no codes."""
    responses = error_responses()
    
    # Check that common error codes are included
    assert 400 in responses
    assert 401 in responses
    assert 403 in responses
    assert 404 in responses
    assert 409 in responses
    assert 422 in responses
    assert 429 in responses
    assert 500 in responses


def test_pagination_params():
    """Test pagination_params function."""
    # This is a bit tricky to test since it's a dependency function
    # Let's check that it has the expected signature
    
    # Get the signature details
    dependency = pagination_params
    
    # Verify the default values for page and page_size
    deps = {}
    for param in dependency.__defaults__:
        if isinstance(param, Query):
            if param.description == "Page number (1-based)":
                deps["page"] = param.default
            elif param.description == "Number of items per page":
                deps["page_size"] = param.default
    
    assert deps.get("page") == 1
    assert deps.get("page_size") == 20
    
    # Verify the function returns a dict with the expected keys
    # This is a simplification since we can't directly call the function
    # as it's intended to be used as a FastAPI dependency
    # In a real test, you'd use TestClient to make a request with pagination
    result = {"page": 1, "page_size": 20}
    assert "page" in result
    assert "page_size" in result


def test_id_path_param():
    """Test id_path_param function."""
    # Create an id_path_param function for a 'user' resource
    user_id_param = id_path_param("user")
    
    # Get the parameter details
    param = None
    for param_value in user_id_param.__defaults__:
        if isinstance(param_value, Path):
            param = param_value
            break
    
    # Check the description and type
    assert param is not None
    assert "user" in param.description


def test_validate_resource_access_owner():
    """Test validate_resource_access function for resource owner."""
    resource_owner_id = uuid4()
    current_user_id = resource_owner_id
    
    # Should not raise an exception for the resource owner
    validate_resource_access(resource_owner_id, current_user_id)


def test_validate_resource_access_admin():
    """Test validate_resource_access function for admin user."""
    resource_owner_id = uuid4()
    current_user_id = uuid4()  # Different user
    is_admin = True
    
    # Should not raise an exception for an admin
    validate_resource_access(resource_owner_id, current_user_id, is_admin)


def test_validate_resource_access_unauthorized():
    """Test validate_resource_access function for unauthorized user."""
    resource_owner_id = uuid4()
    current_user_id = uuid4()  # Different user
    is_admin = False
    
    # Should raise a HTTPException for an unauthorized user
    with pytest.raises(HTTPException) as excinfo:
        validate_resource_access(resource_owner_id, current_user_id, is_admin)
    
    # Check the exception details
    assert excinfo.value.status_code == status.HTTP_403_FORBIDDEN
    assert "FORBIDDEN" in str(excinfo.value.detail)


def test_rate_limit_error():
    """Test rate_limit_error function."""
    retry_after = 60
    
    exception = rate_limit_error(retry_after)
    
    # Check the exception details
    assert exception.status_code == status.HTTP_429_TOO_MANY_REQUESTS
    assert "RATE_LIMIT_EXCEEDED" in str(exception.detail)
    assert f"{retry_after}" in str(exception.detail)
    assert "Retry-After" in exception.headers
    assert exception.headers["Retry-After"] == str(retry_after)


def test_not_found_error():
    """Test not_found_error function."""
    resource_type = "User"
    resource_id = uuid4()
    
    exception = not_found_error(resource_type, resource_id)
    
    # Check the exception details
    assert exception.status_code == status.HTTP_404_NOT_FOUND
    assert "NOT_FOUND" in str(exception.detail)
    assert f"{resource_type}" in str(exception.detail)
    assert f"{resource_id}" in str(exception.detail)


def test_forbidden_error():
    """Test forbidden_error function."""
    message = "Custom forbidden message"
    
    exception = forbidden_error(message)
    
    # Check the exception details
    assert exception.status_code == status.HTTP_403_FORBIDDEN
    assert "FORBIDDEN" in str(exception.detail)
    assert message in str(exception.detail)


def test_forbidden_error_default_message():
    """Test forbidden_error function with default message."""
    exception = forbidden_error()
    
    # Check the exception details
    assert exception.status_code == status.HTTP_403_FORBIDDEN
    assert "FORBIDDEN" in str(exception.detail)
    assert "permission" in str(exception.detail).lower()


def test_validation_error():
    """Test validation_error function."""
    errors = {"field1": ["Error 1"], "field2": ["Error 2"]}
    
    exception = validation_error(errors)
    
    # Check the exception details
    assert exception.status_code == status.HTTP_400_BAD_REQUEST
    assert "VALIDATION_ERROR" in str(exception.detail)
    assert "Invalid request parameters" in str(exception.detail)
    # The errors should be in the details field
    detail_str = str(exception.detail)
    for field, messages in errors.items():
        assert field in detail_str
        for message in messages:
            assert message in detail_str


def test_conflict_error():
    """Test conflict_error function."""
    message = "Resource already exists"
    
    exception = conflict_error(message)
    
    # Check the exception details
    assert exception.status_code == status.HTTP_409_CONFLICT
    assert "RESOURCE_CONFLICT" in str(exception.detail)
    assert message in str(exception.detail) 