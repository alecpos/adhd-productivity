"""
Tests for task routes.

This module contains tests for the task API routes, focusing on ensuring
they return proper standardized responses and handle errors correctly.
"""

import pytest
from fastapi.testclient import TestClient
from uuid import UUID, uuid4
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta

from app.main import create_application
from app.models.enums_model import TaskStatus, BlockPriority, BlockType
from app.schemas.task_schema import TaskResponse, TaskStatsSchema


@pytest.fixture
def mock_task_id():
    return str(uuid4())


@pytest.fixture
def mock_user_id():
    return str(uuid4())


@pytest.fixture
def mock_task(mock_task_id, mock_user_id):
    """Generate a mock task."""
    return {
        "id": mock_task_id,
        "user_id": mock_user_id,
        "title": "Test Task",
        "description": "Task description for testing",
        "due_date": (datetime.now() + timedelta(days=1)).isoformat(),
        "estimated_duration": 60,  # minutes
        "priority": BlockPriority.MEDIUM.value,
        "status": TaskStatus.TODO.value,
        "block_type": BlockType.TASK.value,
        "energy_requirement": 5,
        "focus_requirement": 7,
        "preferred_time": None,
        "is_flexible": True,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "calendar_event_id": None
    }


@pytest.fixture
def mock_stats(mock_user_id):
    """Generate mock task statistics."""
    return {
        "total_tasks": 10,
        "completed_tasks": 5,
        "overdue_tasks": 2,
        "average_completion_time": 45.5,  # minutes
        "completion_rate": 0.5,
        "average_energy_level": 6.5,
        "average_focus_level": 7.2,
        "task_distribution": {status.value: 2 for status in TaskStatus},
        "priority_distribution": {priority.value: 3 for priority in BlockPriority},
        "optimal_completion_times": [
            {"hour": 9, "count": 3},
            {"hour": 14, "count": 5}
        ],
        "common_interruptions": [
            {"type": "phone", "count": 3},
            {"type": "email", "count": 4}
        ],
        "period_start": (datetime.now() - timedelta(days=30)).isoformat(),
        "period_end": datetime.now().isoformat()
    }


@pytest.fixture
def mock_auth_headers(mock_user_id):
    """Generate mock authentication headers."""
    return {"Authorization": f"Bearer test_token_{mock_user_id}"}


@pytest.fixture
def task_service_mock():
    """Create a mock TaskService."""
    with patch("app.routes.task_routes.TaskService") as mock:
        service_instance = MagicMock()
        mock.return_value = service_instance
        yield service_instance


@pytest.fixture
def test_client(task_service_mock):
    """Create a test client with mocked dependencies."""
    # Patch the get_current_user dependency
    with patch("app.routes.task_routes.get_current_user") as mock_current_user:
        mock_current_user.return_value = MagicMock(id=UUID("11111111-1111-1111-1111-111111111111"))

        # Create the test client
        app = create_application()
        client = TestClient(app)
        yield client


# Helper functions for assertions
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
    assert data["page"] == expected_page
    assert data["page_size"] == expected_page_size
    assert data["total"] == expected_total
    return data["items"]


# Tests for GET /tasks
def test_get_user_tasks(test_client, mock_auth_headers, task_service_mock, mock_task):
    """Test getting all tasks for a user."""
    # Arrange
    mock_tasks = [mock_task for _ in range(5)]
    task_service_mock.get_user_tasks_paginated.return_value = (mock_tasks, len(mock_tasks))
    task_service_mock.get_task_statistics.return_value = {}

    # Act
    response = test_client.get("/api/v1/tasks", headers=mock_auth_headers)

    # Assert
    items = assert_paginated_response(response, 1, 20, 5)
    assert len(items) == 5
    assert items[0]["title"] == mock_task["title"]


# Test for GET /tasks/{task_id}
def test_get_task(test_client, mock_auth_headers, task_service_mock, mock_task, mock_task_id):
    """Test getting a specific task."""
    # Arrange
    task_service_mock.get_task.return_value = mock_task

    # Act
    response = test_client.get(f"/api/v1/tasks/{mock_task_id}", headers=mock_auth_headers)

    # Assert
    task = assert_successful_response(response)
    assert task["id"] == mock_task_id
    assert task["title"] == mock_task["title"]


def test_get_nonexistent_task(test_client, mock_auth_headers, task_service_mock, mock_task_id):
    """Test getting a task that doesn't exist."""
    # Arrange
    task_service_mock.get_task.return_value = None

    # Act
    response = test_client.get(f"/api/v1/tasks/{mock_task_id}", headers=mock_auth_headers)

    # Assert
    error = assert_error_response(response, 404, "not_found")
    assert f"task with ID {mock_task_id}" in error["message"]


# Test for POST /tasks
def test_create_task(test_client, mock_auth_headers, task_service_mock, mock_task):
    """Test creating a task."""
    # Arrange
    task_data = {
        "title": "New Task",
        "description": "A new task for testing",
        "estimated_duration": 30,
        "priority": "MEDIUM",
        "preferred_time": None,
        "is_flexible": True
    }
    task_service_mock.create_task.return_value = mock_task

    # Act
    response = test_client.post("/api/v1/tasks", json=task_data, headers=mock_auth_headers)

    # Assert
    task = assert_successful_response(response, 201)
    assert task["title"] == mock_task["title"]
    # Verify service was called with correct parameters
    task_service_mock.create_task.assert_called_once()


# Test for PUT /tasks/{task_id}
def test_update_task(test_client, mock_auth_headers, task_service_mock, mock_task, mock_task_id):
    """Test updating a task."""
    # Arrange
    update_data = {
        "title": "Updated Task",
        "description": "Updated description"
    }
    task_service_mock.get_task.return_value = mock_task
    task_service_mock.update_task.return_value = {**mock_task, **update_data}

    # Act
    response = test_client.put(f"/api/v1/tasks/{mock_task_id}", json=update_data, headers=mock_auth_headers)

    # Assert
    task = assert_successful_response(response)
    assert task["id"] == mock_task_id
    # Verify service was called with correct parameters
    task_service_mock.update_task.assert_called_once()


# Test for DELETE /tasks/{task_id}
def test_delete_task(test_client, mock_auth_headers, task_service_mock, mock_task, mock_task_id):
    """Test deleting a task."""
    # Arrange
    task_service_mock.get_task.return_value = mock_task

    # Act
    response = test_client.delete(f"/api/v1/tasks/{mock_task_id}", headers=mock_auth_headers)

    # Assert
    assert response.status_code == 204
    assert not response.content  # No content for 204 response
    # Verify service was called with correct parameters
    task_service_mock.delete.assert_called_once_with(mock_task_id)


# Test for POST /tasks/{task_id}/complete
def test_complete_task(test_client, mock_auth_headers, task_service_mock, mock_task, mock_task_id):
    """Test marking a task as complete."""
    # Arrange
    completed_task = {**mock_task, "status": TaskStatus.COMPLETED.value}
    task_service_mock.get_task.return_value = mock_task
    task_service_mock.complete_task.return_value = completed_task

    # Act
    response = test_client.post(f"/api/v1/tasks/{mock_task_id}/complete", headers=mock_auth_headers)

    # Assert
    task = assert_successful_response(response)
    assert task["id"] == mock_task_id
    assert task["status"] == TaskStatus.COMPLETED.value
    # Verify service was called with correct parameters
    task_service_mock.complete_task.assert_called_once_with(mock_task_id)


# Test for GET /tasks/statistics
def test_get_task_statistics(test_client, mock_auth_headers, task_service_mock, mock_stats):
    """Test getting task statistics."""
    # Arrange
    task_service_mock.get_task_statistics.return_value = mock_stats

    # Act
    response = test_client.get("/api/v1/tasks/statistics", headers=mock_auth_headers)

    # Assert
    stats = assert_successful_response(response)
    assert stats["total_tasks"] == mock_stats["total_tasks"]
    assert stats["completed_tasks"] == mock_stats["completed_tasks"]
    assert stats["completion_rate"] == mock_stats["completion_rate"]
    # Verify service was called with correct parameters
    task_service_mock.get_task_statistics.assert_called_once()
