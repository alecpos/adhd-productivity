# API Testing Examples

This document provides examples of how to test API endpoints using the standardized utilities implemented for the ADHD Calendar API.

## Introduction

Testing API endpoints is critical for ensuring the reliability and correctness of our API. The examples in this document demonstrate how to test endpoints using:

1. FastAPI TestClient
2. Our standardized response utilities
3. Our error handling middleware
4. Our custom exceptions

## Basic Test Setup

All API tests should follow this basic pattern:

```python
import pytest
from fastapi.testclient import TestClient
from uuid import uuid4

from app.main import create_application
from app.utils.api_responses import create_response


@pytest.fixture
def test_client():
    app = create_application()
    with TestClient(app) as client:
        yield client


def test_some_endpoint(test_client):
    # Arrange
    # Set up test data, authentication, etc.

    # Act
    response = test_client.get("/api/v1/some-endpoint")

    # Assert
    assert response.status_code == 200
    data = response.json()
    # Perform assertions on response data
```

## Example: Testing a GET Endpoint with Success Response

```python
def test_get_task(test_client, mock_user, mock_db_session):
    # Arrange
    task_id = str(uuid4())
    mock_task = {
        "id": task_id,
        "title": "Test Task",
        "description": "Test Description",
        "user_id": mock_user["id"],
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z"
    }

    # Mock the task service to return the mock task
    mock_db_session.query().filter().first.return_value = mock_task

    # Act
    response = test_client.get(f"/api/v1/tasks/{task_id}", headers={"Authorization": f"Bearer {mock_user['token']}"})

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert data["data"]["id"] == task_id
    assert data["data"]["title"] == "Test Task"
    assert "timestamp" in data
```

## Example: Testing Error Responses

```python
def test_get_nonexistent_task(test_client, mock_user):
    # Arrange
    nonexistent_task_id = str(uuid4())

    # Act
    response = test_client.get(f"/api/v1/tasks/{nonexistent_task_id}", headers={"Authorization": f"Bearer {mock_user['token']}"})

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "not_found"
    assert f"task with ID {nonexistent_task_id}" in data["error"]["message"]
    assert "timestamp" in data


def test_unauthorized_access(test_client):
    # Arrange
    task_id = str(uuid4())

    # Act - No authorization header
    response = test_client.get(f"/api/v1/tasks/{task_id}")

    # Assert
    assert response.status_code == 401
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "unauthorized"
    assert "Not authenticated" in data["error"]["message"]


def test_forbidden_access(test_client, mock_user, other_mock_user, mock_db_session):
    # Arrange
    task_id = str(uuid4())
    # Task belongs to other_mock_user
    mock_task = {
        "id": task_id,
        "title": "Test Task",
        "description": "Test Description",
        "user_id": other_mock_user["id"],  # Different user than the one making the request
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z"
    }

    # Mock the task service
    mock_db_session.query().filter().first.return_value = mock_task

    # Act - Authenticated as mock_user trying to access other_mock_user's task
    response = test_client.get(f"/api/v1/tasks/{task_id}", headers={"Authorization": f"Bearer {mock_user['token']}"})

    # Assert
    assert response.status_code == 403
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "forbidden"
    assert "do not have permission" in data["error"]["message"].lower()
```

## Example: Testing Validation Errors

```python
def test_create_task_validation_error(test_client, mock_user):
    # Arrange
    invalid_task = {
        # Missing required 'title' field
        "description": "Test Description",
        "estimated_duration": -5  # Invalid duration (must be positive)
    }

    # Act
    response = test_client.post(
        "/api/v1/tasks",
        json=invalid_task,
        headers={"Authorization": f"Bearer {mock_user['token']}"}
    )

    # Assert
    assert response.status_code == 400
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "validation_error"
    assert "details" in data["error"]
    # Check for specific validation errors
    assert any("title" in field for field in data["error"]["details"])
    assert any("estimated_duration" in field for field in data["error"]["details"])
```

## Example: Testing Pagination

```python
def test_get_tasks_pagination(test_client, mock_user, mock_db_session):
    # Arrange
    # Create mock tasks
    mock_tasks = [{"id": str(uuid4()), "title": f"Task {i}"} for i in range(30)]

    # Mock the task service to return paginated results
    mock_db_session.query().filter().offset().limit().all.return_value = mock_tasks[:10]
    mock_db_session.query().filter().count.return_value = len(mock_tasks)

    # Act
    response = test_client.get(
        "/api/v1/tasks?page=1&page_size=10",
        headers={"Authorization": f"Bearer {mock_user['token']}"}
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "items" in data["data"]
    assert len(data["data"]["items"]) == 10
    assert data["data"]["total"] == 30
    assert data["data"]["page"] == 1
    assert data["data"]["page_size"] == 10
    assert data["data"]["total_pages"] == 3
```

## Testing Utilities

To simplify testing, you can create helper utilities like these:

```python
def assert_successful_response(response, expected_status=200):
    """Assert that a response was successful and has correct structure."""
    assert response.status_code == expected_status
    data = response.json()
    assert "data" in data
    assert "timestamp" in data
    return data["data"]


def assert_error_response(response, expected_status, expected_code):
    """Assert that an error response has correct structure and code."""
    assert response.status_code == expected_status
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == expected_code
    assert "message" in data["error"]
    assert "timestamp" in data
    return data["error"]


def assert_paginated_response(response, expected_page, expected_page_size, expected_total):
    """Assert that a paginated response has correct structure."""
    data = assert_successful_response(response)
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert "total_pages" in data
    assert data["page"] == expected_page
    assert data["page_size"] == expected_page_size
    assert data["total"] == expected_total
    expected_total_pages = (expected_total + expected_page_size - 1) // expected_page_size
    assert data["total_pages"] == expected_total_pages
    return data["items"]
```

## Mocking Authentication

For tests that require authentication, it's useful to create a fixture that mocks the authentication process:

```python
@pytest.fixture
def mock_user():
    """Create a mock authenticated user for testing."""
    return {
        "id": str(uuid4()),
        "email": "test@example.com",
        "token": "mock_token"
    }


@pytest.fixture
def auth_headers(mock_user):
    """Generate authorization headers for the mock user."""
    return {"Authorization": f"Bearer {mock_user['token']}"}


# Then use in tests:
def test_authenticated_endpoint(test_client, auth_headers):
    response = test_client.get("/api/v1/protected-endpoint", headers=auth_headers)
    assert response.status_code == 200
```

## Integration Tests vs. Unit Tests

While the examples above focus on unit testing with mocked dependencies, consider also writing integration tests that use a test database to verify end-to-end functionality:

```python
@pytest.mark.integration
def test_create_and_retrieve_task(test_client, test_db, authenticated_user):
    # Create a task
    task_data = {
        "title": "Integration Test Task",
        "description": "Testing the full task lifecycle",
        "estimated_duration": 30
    }

    create_response = test_client.post(
        "/api/v1/tasks",
        json=task_data,
        headers=authenticated_user["headers"]
    )
    assert create_response.status_code == 201
    created_task = assert_successful_response(create_response, 201)
    task_id = created_task["id"]

    # Retrieve the task
    get_response = test_client.get(
        f"/api/v1/tasks/{task_id}",
        headers=authenticated_user["headers"]
    )
    retrieved_task = assert_successful_response(get_response)

    # Verify task data
    assert retrieved_task["id"] == task_id
    assert retrieved_task["title"] == task_data["title"]
    assert retrieved_task["description"] == task_data["description"]
    assert retrieved_task["estimated_duration"] == task_data["estimated_duration"]
    assert retrieved_task["user_id"] == authenticated_user["id"]
```

## Conclusion

By following these patterns and examples, you can create a comprehensive test suite for your API endpoints that ensures they conform to our standardized response format, handle errors consistently, and meet all functional requirements.
