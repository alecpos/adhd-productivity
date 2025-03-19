"""
Tests for error handler middleware.

This module contains tests for error handler middleware to ensure it correctly
handles various exception types and returns appropriate standardized responses.
"""

import pytest
from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.testclient import TestClient
from pydantic import BaseModel, ValidationError, validator
from typing import Dict, Any

from app.middleware.error_handler import setup_error_handling
from app.utils.exceptions import (
    ResourceNotFoundError,
    ForbiddenError,
    ValidationCustomError,
    ConflictError, 
    RateLimitError
)


def create_test_app() -> FastAPI:
    """Create a FastAPI test application with error handling middleware."""
    app = FastAPI()
    setup_error_handling(app)
    
    @app.get("/test-internal-error")
    async def test_internal_error():
        """Test route that raises a generic exception."""
        raise Exception("Test internal server error")
    
    @app.get("/test-http-exception")
    async def test_http_exception():
        """Test route that raises a FastAPI HTTPException."""
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Test bad request error"
        )
    
    @app.get("/test-not-found")
    async def test_not_found():
        """Test route that raises a ResourceNotFoundError."""
        raise ResourceNotFoundError(resource="item", resource_id="123")
    
    @app.get("/test-forbidden")
    async def test_forbidden():
        """Test route that raises a ForbiddenError."""
        raise ForbiddenError(message="You don't have permission")
    
    @app.get("/test-validation-error")
    async def test_validation_error():
        """Test route that raises a ValidationCustomError."""
        raise ValidationCustomError(errors={
            "field1": ["Value is required"],
            "field2": ["Invalid format"]
        })
    
    @app.get("/test-conflict")
    async def test_conflict():
        """Test route that raises a ConflictError."""
        raise ConflictError(message="Resource already exists")
    
    @app.get("/test-rate-limit")
    async def test_rate_limit():
        """Test route that raises a RateLimitError."""
        raise RateLimitError(
            message="Rate limit exceeded",
            retry_after=60
        )
    
    # Define a model for Pydantic validation error testing
    class TestModel(BaseModel):
        name: str
        age: int
        
        @validator('age')
        def age_must_be_positive(cls, v):
            if v <= 0:
                raise ValueError('Age must be positive')
            return v
    
    @app.get("/test-pydantic-validation")
    async def test_pydantic_validation(request: Request):
        """Test route that triggers a Pydantic validation error."""
        # Manually parse the request to trigger a validation error
        # In a real scenario, this would happen automatically with request body parsing
        TestModel(name="", age=-1)
        return {"status": "This should not be reached"}
    
    return app


@pytest.fixture
def test_client():
    """Create a test client for the FastAPI application."""
    app = create_test_app()
    client = TestClient(app)
    return client


def check_error_response_structure(response_json: Dict[str, Any]):
    """Check that the error response has the correct structure."""
    assert "error" in response_json
    assert "code" in response_json["error"]
    assert "message" in response_json["error"]
    assert "timestamp" in response_json


def test_handle_internal_error(test_client):
    """Test handling of internal server errors."""
    response = test_client.get("/test-internal-error")
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    
    response_json = response.json()
    check_error_response_structure(response_json)
    assert response_json["error"]["code"] == "internal_server_error"
    assert "internal server error" in response_json["error"]["message"].lower()


def test_handle_http_exception(test_client):
    """Test handling of FastAPI HTTPExceptions."""
    response = test_client.get("/test-http-exception")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    response_json = response.json()
    check_error_response_structure(response_json)
    assert response_json["error"]["code"] == "bad_request"
    assert "test bad request error" in response_json["error"]["message"].lower()


def test_handle_not_found(test_client):
    """Test handling of ResourceNotFoundErrors."""
    response = test_client.get("/test-not-found")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    
    response_json = response.json()
    check_error_response_structure(response_json)
    assert response_json["error"]["code"] == "not_found"
    assert "item" in response_json["error"]["message"].lower()
    assert "123" in response_json["error"]["message"]


def test_handle_forbidden(test_client):
    """Test handling of ForbiddenErrors."""
    response = test_client.get("/test-forbidden")
    assert response.status_code == status.HTTP_403_FORBIDDEN
    
    response_json = response.json()
    check_error_response_structure(response_json)
    assert response_json["error"]["code"] == "forbidden"
    assert "permission" in response_json["error"]["message"].lower()


def test_handle_validation_error(test_client):
    """Test handling of ValidationCustomErrors."""
    response = test_client.get("/test-validation-error")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    response_json = response.json()
    check_error_response_structure(response_json)
    assert response_json["error"]["code"] == "validation_error"
    assert "field1" in response_json["error"]["details"]
    assert "field2" in response_json["error"]["details"]
    assert "Value is required" in response_json["error"]["details"]["field1"]


def test_handle_conflict(test_client):
    """Test handling of ConflictErrors."""
    response = test_client.get("/test-conflict")
    assert response.status_code == status.HTTP_409_CONFLICT
    
    response_json = response.json()
    check_error_response_structure(response_json)
    assert response_json["error"]["code"] == "conflict"
    assert "already exists" in response_json["error"]["message"].lower()


def test_handle_rate_limit(test_client):
    """Test handling of RateLimitErrors."""
    response = test_client.get("/test-rate-limit")
    assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
    
    response_json = response.json()
    check_error_response_structure(response_json)
    assert response_json["error"]["code"] == "rate_limit_exceeded"
    assert "rate limit exceeded" in response_json["error"]["message"].lower()
    assert "retry_after" in response_json["error"]
    assert response_json["error"]["retry_after"] == 60
    
    # Check that the Retry-After header is set
    assert "Retry-After" in response.headers
    assert response.headers["Retry-After"] == "60"


def test_handle_404_not_found(test_client):
    """Test handling of 404 not found for non-existent routes."""
    response = test_client.get("/non-existent-route")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    
    response_json = response.json()
    check_error_response_structure(response_json)
    assert response_json["error"]["code"] == "not_found"
    assert "route" in response_json["error"]["message"].lower()


def test_method_not_allowed(test_client):
    """Test handling of method not allowed errors."""
    response = test_client.post("/test-internal-error")  # POST not allowed
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    
    response_json = response.json()
    check_error_response_structure(response_json)
    assert response_json["error"]["code"] == "method_not_allowed"
    assert "method" in response_json["error"]["message"].lower() 