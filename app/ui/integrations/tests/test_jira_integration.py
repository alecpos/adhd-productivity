"""
Tests for the Jira Integration component.
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock

from app.ui.project_management_integration import (
    ProjectToolConfig,
    ProjectToolType,
    SyncDirection,
    SyncFrequency,
    ExternalTask
)
from app.ui.integrations.jira_integration import JiraIntegration


@pytest.fixture
def jira_config():
    """Fixture providing a sample Jira configuration."""
    return ProjectToolConfig(
        tool_type=ProjectToolType.JIRA,
        api_url="https://example.atlassian.net",
        auth_token="fake-token",
        sync_direction=SyncDirection.BIDIRECTIONAL,
        sync_frequency=SyncFrequency.ON_CHANGE,
        project_ids=["PROJ"],
        labels_to_sync=["adhd-calendar"],
        enabled=True,
        user_id="test-user-1"
    )


@pytest.fixture
def mock_jira_issue():
    """Fixture providing a sample Jira issue response."""
    return {
        "id": "10001",
        "key": "PROJ-123",
        "fields": {
            "summary": "Test Issue",
            "description": "This is a test issue",
            "status": {"name": "In Progress"},
            "duedate": "2023-12-31",
            "created": "2023-01-01T10:00:00.000Z",
            "updated": "2023-01-15T14:30:00.000Z",
            "priority": {"name": "High"},
            "assignee": {"displayName": "Test User"},
            "labels": ["adhd-calendar", "test"],
            "project": {"id": "PROJ", "key": "PROJ"}
        }
    }


@pytest.mark.asyncio
async def test_jira_authenticate_success(jira_config):
    """Test successful authentication with Jira."""
    integration = JiraIntegration(jira_config)
    
    # Patch the authenticate method to return True
    with patch.object(integration, '_get_auth_headers', return_value={}), \
         patch('app.ui.integrations.jira_integration.logging'):
        result = await integration.authenticate()
        assert result is True


@pytest.mark.asyncio
async def test_jira_authenticate_failure(jira_config):
    """Test failed authentication with Jira."""
    integration = JiraIntegration(jira_config)
    
    # Patch the authenticate method to raise an exception
    with patch.object(integration, '_get_auth_headers', side_effect=Exception("Auth failed")), \
         patch('app.ui.integrations.jira_integration.logging'):
        result = await integration.authenticate()
        assert result is False


@pytest.mark.asyncio
async def test_fetch_tasks(jira_config, mock_jira_issue):
    """Test fetching tasks from Jira."""
    integration = JiraIntegration(jira_config)
    
    # Mock the necessary methods
    with patch.object(integration, '_build_jql_query', return_value="project = PROJ"), \
         patch.object(integration, '_make_api_call', new_callable=AsyncMock) as mock_api_call, \
         patch('app.ui.integrations.jira_integration.logging'):
        
        # Setup mock return value
        mock_api_call.return_value = {"issues": [mock_jira_issue]}
        
        # Call the method
        tasks = await integration.fetch_tasks()
        
        # Assertions
        assert len(tasks) == 1
        task = tasks[0]
        assert task.external_id == "PROJ-123"
        assert task.title == "Test Issue"
        assert task.status == "in_progress"
        assert task.priority == "high"
        assert "adhd-calendar" in task.labels
        assert task.tool_type == ProjectToolType.JIRA


@pytest.mark.asyncio
async def test_create_task(jira_config):
    """Test creating a task in Jira."""
    integration = JiraIntegration(jira_config)
    
    # Test task data
    task_data = {
        "title": "New Task",
        "description": "This is a new task",
        "status": "not_started",
        "due_date": datetime(2023, 12, 31),
        "priority": "high",
        "labels": ["adhd-calendar", "test"]
    }
    
    # Mock responses
    with patch.object(integration, '_make_api_call', new_callable=AsyncMock) as mock_api_call, \
         patch('app.ui.integrations.jira_integration.logging'):
        
        # Setup mock return value
        mock_api_call.return_value = {"id": "10002", "key": "PROJ-124"}
        
        # Call the method
        result = await integration.create_task(task_data)
        
        # Assertions
        assert result.external_id == "PROJ-124"
        assert result.title == "New Task"
        assert result.status == "not_started"
        assert result.priority == "high"
        assert "adhd-calendar" in result.labels
        assert result.tool_type == ProjectToolType.JIRA


@pytest.mark.asyncio
async def test_update_task(jira_config):
    """Test updating a task in Jira."""
    integration = JiraIntegration(jira_config)
    
    # Test task data
    task_data = {
        "title": "Updated Task",
        "description": "This task has been updated",
        "status": "in_progress",
        "due_date": datetime(2023, 12, 31),
        "priority": "critical",
        "labels": ["adhd-calendar", "test", "updated"]
    }
    
    # Mock responses
    with patch.object(integration, '_make_api_call', new_callable=AsyncMock) as mock_api_call, \
         patch('app.ui.integrations.jira_integration.logging'):
        
        # Setup mock return value
        mock_api_call.return_value = {"id": "10001", "key": "PROJ-123"}
        
        # Call the method
        result = await integration.update_task("PROJ-123", task_data)
        
        # Assertions
        assert result.external_id == "PROJ-123"
        assert result.title == "Updated Task"
        assert result.status == "in_progress"
        assert result.priority == "critical"
        assert "updated" in result.labels
        assert result.tool_type == ProjectToolType.JIRA


@pytest.mark.asyncio
async def test_delete_task(jira_config):
    """Test deleting a task in Jira."""
    integration = JiraIntegration(jira_config)
    
    # Mock responses
    with patch.object(integration, '_make_api_call', new_callable=AsyncMock) as mock_api_call, \
         patch('app.ui.integrations.jira_integration.logging'):
        
        # Setup mock return value
        mock_api_call.return_value = {}
        
        # Call the method
        result = await integration.delete_task("PROJ-123")
        
        # Assertions
        assert result is True
        mock_api_call.assert_called_once()


@pytest.mark.asyncio
async def test_get_projects(jira_config):
    """Test fetching projects from Jira."""
    integration = JiraIntegration(jira_config)
    
    # Mock responses
    with patch.object(integration, '_make_api_call', new_callable=AsyncMock) as mock_api_call, \
         patch('app.ui.integrations.jira_integration.logging'):
        
        # Setup mock return value
        mock_api_call.return_value = [
            {"id": "10000", "key": "PROJ1", "name": "Project One"},
            {"id": "10001", "key": "PROJ2", "name": "Project Two"}
        ]
        
        # Call the method
        projects = await integration.get_projects()
        
        # Assertions
        assert len(projects) == 2
        assert projects[0]["key"] == "PROJ1"
        assert projects[1]["name"] == "Project Two"


@pytest.mark.asyncio
async def test_error_handling(jira_config):
    """Test error handling in Jira integration."""
    integration = JiraIntegration(jira_config)
    
    # Mock responses
    with patch.object(integration, '_make_api_call', new_callable=AsyncMock) as mock_api_call, \
         patch('app.ui.integrations.jira_integration.logging') as mock_logging:
        
        # Setup mock to raise exception
        mock_api_call.side_effect = Exception("API error")
        
        # Call the method and test it doesn't raise
        tasks = await integration.fetch_tasks()
        
        # Assertions
        assert tasks == []
        assert mock_logging.error.called 