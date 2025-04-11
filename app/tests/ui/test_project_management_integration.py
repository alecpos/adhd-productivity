"""
Test suite for the project management tool integration module.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock, AsyncMock

from app.ui.project_management_integration import (
    ProjectToolType,
    SyncDirection,
    SyncFrequency,
    ProjectToolConfig,
    ExternalTask,
    SyncResult,
    ProjectToolIntegration,
    JiraIntegration,
    ProjectManagementService,
)


class TestProjectToolConfig:
    """Test the ProjectToolConfig model."""

    def test_default_config(self):
        """Test that default configuration values are set correctly."""
        config = ProjectToolConfig(
            tool_type=ProjectToolType.JIRA, api_url="https://jira.example.com", user_id="test_user"
        )

        assert config.tool_type == ProjectToolType.JIRA
        assert config.api_url == "https://jira.example.com"
        assert config.user_id == "test_user"
        assert config.auth_token is None
        assert config.auth_user is None
        assert config.auth_password is None
        assert config.sync_direction == SyncDirection.BIDIRECTIONAL
        assert config.sync_frequency == SyncFrequency.ON_CHANGE
        assert config.workspace_id is None
        assert config.project_ids == []
        assert config.labels_to_sync == []
        assert config.enabled is True
        assert config.last_sync is None

    def test_custom_config(self):
        """Test that custom configuration can be set."""
        config = ProjectToolConfig(
            tool_type=ProjectToolType.GITHUB,
            api_url="https://api.github.com",
            user_id="test_user",
            auth_token="github_token",
            sync_direction=SyncDirection.IMPORT,
            sync_frequency=SyncFrequency.DAILY,
            project_ids=["project1", "project2"],
            labels_to_sync=["bug", "feature"],
            last_sync=datetime(2023, 1, 1),
        )

        assert config.tool_type == ProjectToolType.GITHUB
        assert config.auth_token == "github_token"
        assert config.sync_direction == SyncDirection.IMPORT
        assert config.sync_frequency == SyncFrequency.DAILY
        assert config.project_ids == ["project1", "project2"]
        assert config.labels_to_sync == ["bug", "feature"]
        assert config.last_sync == datetime(2023, 1, 1)


class TestExternalTask:
    """Test the ExternalTask model."""

    def test_minimal_task(self):
        """Test creation of a minimal external task."""
        task = ExternalTask(
            external_id="TASK-123",
            title="Test Task",
            status="in_progress",
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(hours=1),
            tool_type=ProjectToolType.JIRA,
        )

        assert task.external_id == "TASK-123"
        assert task.title == "Test Task"
        assert task.status == "in_progress"
        assert task.description is None
        assert task.is_all_day is False
        assert task.location is None
        assert task.url is None
        assert task.labels == []
        assert task.attendees == []
        assert task.tool_type == ProjectToolType.JIRA

    def test_complete_task(self):
        """Test creation of a fully populated external task."""
        now = datetime.now()
        task = ExternalTask(
            external_id="TASK-456",
            title="Comprehensive Task",
            description="This is a detailed task for testing",
            status="completed",
            start_time=now,
            end_time=now + timedelta(hours=2),
            is_all_day=False,
            location="Conference Room",
            url="https://jira.example.com/browse/TASK-456",
            labels=["bug", "critical"],
            project_id="PROJECT-1",
            attendees=[{"email": "user@example.com", "name": "Test User"}],
            priority="high",
            assignee="John Doe",
            created_date=now - timedelta(days=1),
            updated_date=now - timedelta(hours=1),
            tool_type=ProjectToolType.JIRA,
            additional_data={"story_points": 5},
        )

        assert task.external_id == "TASK-456"
        assert task.title == "Comprehensive Task"
        assert task.description == "This is a detailed task for testing"
        assert task.status == "completed"
        assert task.location == "Conference Room"
        assert task.url == "https://jira.example.com/browse/TASK-456"
        assert task.labels == ["bug", "critical"]
        assert task.project_id == "PROJECT-1"
        assert len(task.attendees) == 1
        assert task.priority == "high"
        assert task.assignee == "John Doe"
        assert task.created_date == now - timedelta(days=1)
        assert task.updated_date == now - timedelta(hours=1)
        assert task.additional_data["story_points"] == 5


class TestJiraIntegration:
    """Test the JiraIntegration class."""

    @pytest.fixture
    def jira_config(self):
        """Create a Jira configuration for testing."""
        return ProjectToolConfig(
            tool_type=ProjectToolType.JIRA,
            api_url="https://jira.example.com",
            user_id="test_user",
            auth_token="test_token",
            project_ids=["TEST"],
        )

    @pytest.fixture
    def jira_integration(self, jira_config):
        """Create a JiraIntegration instance for testing."""
        return JiraIntegration(jira_config)

    def test_init(self, jira_integration, jira_config):
        """Test that the integration initializes correctly."""
        assert jira_integration.config == jira_config
        assert jira_integration.name == "Jira"

    def test_get_auth_headers(self, jira_integration):
        """Test authentication headers generation."""
        headers = jira_integration._get_auth_headers()

        assert headers["Content-Type"] == "application/json"
        assert headers["Authorization"] == "Bearer test_token"

    @pytest.mark.asyncio
    @patch("app.ui.project_management_integration.logger")
    async def test_authenticate_success(self, mock_logger, jira_integration):
        """Test successful authentication."""
        result = await jira_integration.authenticate()

        assert result is True
        mock_logger.info.assert_called_once()

    def test_build_jql_query(self, jira_integration):
        """Test JQL query building with various configurations."""
        # Basic query with project IDs
        jql = jira_integration._build_jql_query()
        assert "(project = TEST)" in jql
        assert "ORDER BY" in jql

        # Add labels to sync
        jira_integration.config.labels_to_sync = ["bug", "feature"]
        jql = jira_integration._build_jql_query()
        assert "(labels = bug OR labels = feature)" in jql

        # Add last sync time
        jira_integration.config.last_sync = datetime(2023, 1, 1, 12, 0)
        jql = jira_integration._build_jql_query()
        assert "updated >= '2023-01-01 12:00'" in jql

    def test_map_status(self, jira_integration):
        """Test Jira status mapping."""
        assert jira_integration.map_status("To Do") == "not_started"
        assert jira_integration.map_status("in progress") == "in_progress"
        assert jira_integration.map_status("DONE") == "completed"
        assert jira_integration.map_status("Blocked") == "blocked"
        assert jira_integration.map_status("Reopened") == "not_started"
        assert jira_integration.map_status("unknown") == "not_started"  # Default

    @pytest.mark.asyncio
    async def test_fetch_tasks(self, jira_integration):
        """Test fetching tasks from Jira."""
        tasks = await jira_integration.fetch_tasks()

        assert len(tasks) > 0
        assert isinstance(tasks[0], ExternalTask)
        assert tasks[0].tool_type == ProjectToolType.JIRA
        assert tasks[0].title == "Implement project sync"

    @pytest.mark.asyncio
    async def test_create_task(self, jira_integration):
        """Test creating a task in Jira."""
        task_data = {
            "title": "New Task",
            "description": "Task description",
            "start_time": datetime.now(),
            "end_time": datetime.now() + timedelta(hours=1),
            "priority": "high",
            "labels": ["bug", "critical"],
        }

        created_task = await jira_integration.create_task(task_data)

        assert isinstance(created_task, ExternalTask)
        assert created_task.title == "New Task"
        assert created_task.description == "Task description"
        assert created_task.priority == "high"
        assert "bug" in created_task.labels
        assert created_task.tool_type == ProjectToolType.JIRA

    @pytest.mark.asyncio
    async def test_update_task(self, jira_integration):
        """Test updating a task in Jira."""
        task_data = {"title": "Updated Task", "status": "completed", "priority": "low"}

        updated_task = await jira_integration.update_task("TASK-123", task_data)

        assert isinstance(updated_task, ExternalTask)
        assert updated_task.title == "Updated Task"
        assert updated_task.status == "completed"
        assert updated_task.priority == "low"

    @pytest.mark.asyncio
    async def test_delete_task(self, jira_integration):
        """Test deleting a task from Jira."""
        result = await jira_integration.delete_task("TASK-123")

        assert result is True

    @pytest.mark.asyncio
    async def test_get_projects(self, jira_integration):
        """Test getting projects from Jira."""
        projects = await jira_integration.get_projects()

        assert len(projects) > 0
        assert "id" in projects[0]
        assert "key" in projects[0]
        assert "name" in projects[0]


class TestProjectManagementService:
    """Test the ProjectManagementService class."""

    @pytest.fixture
    def service(self):
        """Create a ProjectManagementService instance for testing."""
        return ProjectManagementService()

    def test_init(self, service):
        """Test that the service initializes correctly."""
        assert service.integrations == {}
        assert ProjectToolType.JIRA in service.integration_classes

    @pytest.mark.asyncio
    @patch.object(JiraIntegration, "test_connection", new_callable=AsyncMock, return_value=True)
    async def test_register_integration_success(self, mock_test_connection, service):
        """Test successful integration registration."""
        config = ProjectToolConfig(
            tool_type=ProjectToolType.JIRA, api_url="https://jira.example.com", user_id="test_user"
        )

        result = await service.register_integration(config)

        assert result is True
        assert "test_user" in service.integrations
        assert ProjectToolType.JIRA in service.integrations["test_user"]
        assert isinstance(service.integrations["test_user"][ProjectToolType.JIRA], JiraIntegration)

    @pytest.mark.asyncio
    @patch.object(JiraIntegration, "test_connection", new_callable=AsyncMock, return_value=False)
    async def test_register_integration_connection_failure(self, mock_test_connection, service):
        """Test integration registration with connection failure."""
        config = ProjectToolConfig(
            tool_type=ProjectToolType.JIRA, api_url="https://jira.example.com", user_id="test_user"
        )

        result = await service.register_integration(config)

        assert result is False
        assert "test_user" not in service.integrations

    @pytest.mark.asyncio
    async def test_register_integration_unsupported_tool(self, service):
        """Test integration registration with unsupported tool type."""
        # Temporarily remove JIRA from supported integrations
        original_classes = service.integration_classes
        service.integration_classes = {}

        config = ProjectToolConfig(
            tool_type=ProjectToolType.JIRA, api_url="https://jira.example.com", user_id="test_user"
        )

        result = await service.register_integration(config)

        assert result is False

        # Restore original classes
        service.integration_classes = original_classes

    @pytest.mark.asyncio
    @patch.object(JiraIntegration, "test_connection", new_callable=AsyncMock, return_value=True)
    async def test_get_user_integrations(self, mock_test_connection, service):
        """Test getting integrations for a user."""
        # Register an integration
        config = ProjectToolConfig(
            tool_type=ProjectToolType.JIRA, api_url="https://jira.example.com", user_id="test_user"
        )
        await service.register_integration(config)

        # Get user integrations
        integrations = await service.get_user_integrations("test_user")

        assert len(integrations) == 1
        assert integrations[0] == ProjectToolType.JIRA

        # Test with non-existent user
        empty_integrations = await service.get_user_integrations("nonexistent_user")
        assert empty_integrations == []

    @pytest.mark.asyncio
    @patch.object(JiraIntegration, "test_connection", new_callable=AsyncMock, return_value=True)
    async def test_get_integration(self, mock_test_connection, service):
        """Test getting a specific integration for a user."""
        # Register an integration
        config = ProjectToolConfig(
            tool_type=ProjectToolType.JIRA, api_url="https://jira.example.com", user_id="test_user"
        )
        await service.register_integration(config)

        # Get integration
        integration = await service.get_integration("test_user", ProjectToolType.JIRA)

        assert integration is not None
        assert isinstance(integration, JiraIntegration)

        # Test with non-existent integration
        none_integration = await service.get_integration("test_user", ProjectToolType.TRELLO)
        assert none_integration is None

    @pytest.mark.asyncio
    @patch.object(JiraIntegration, "test_connection", new_callable=AsyncMock, return_value=True)
    async def test_remove_integration(self, mock_test_connection, service):
        """Test removing an integration for a user."""
        # Register an integration
        config = ProjectToolConfig(
            tool_type=ProjectToolType.JIRA, api_url="https://jira.example.com", user_id="test_user"
        )
        await service.register_integration(config)

        # Remove integration
        result = await service.remove_integration("test_user", ProjectToolType.JIRA)

        assert result is True
        assert "test_user" not in service.integrations

        # Test with non-existent integration
        false_result = await service.remove_integration("test_user", ProjectToolType.JIRA)
        assert false_result is False

    @pytest.mark.asyncio
    @patch.object(JiraIntegration, "test_connection", new_callable=AsyncMock, return_value=True)
    @patch.object(
        JiraIntegration,
        "fetch_tasks",
        new_callable=AsyncMock,
        return_value=[
            ExternalTask(
                external_id="TASK-123",
                title="Test Task",
                status="in_progress",
                start_time=datetime.now(),
                end_time=datetime.now() + timedelta(hours=1),
                tool_type=ProjectToolType.JIRA,
            )
        ],
    )
    async def test_sync_tasks(self, mock_fetch_tasks, mock_test_connection, service):
        """Test synchronizing tasks for a user."""
        # Register an integration
        config = ProjectToolConfig(
            tool_type=ProjectToolType.JIRA, api_url="https://jira.example.com", user_id="test_user"
        )
        await service.register_integration(config)

        # Sync tasks
        results = await service.sync_tasks("test_user")

        assert len(results) == 1
        assert results[0].success is True
        assert results[0].tool_type == ProjectToolType.JIRA
        assert results[0].tasks_imported == 1

        # Test with specific tool type
        specific_results = await service.sync_tasks("test_user", ProjectToolType.JIRA)
        assert len(specific_results) == 1

        # Test with non-existent user
        empty_results = await service.sync_tasks("nonexistent_user")
        assert empty_results == []

    @pytest.mark.asyncio
    @patch.object(
        JiraIntegration,
        "get_projects",
        new_callable=AsyncMock,
        return_value=[{"id": "10000", "key": "PROJ", "name": "Test Project"}],
    )
    @patch.object(JiraIntegration, "test_connection", new_callable=AsyncMock, return_value=True)
    async def test_get_available_projects(self, mock_test_connection, mock_get_projects, service):
        """Test getting available projects for a tool type."""
        # Register an integration
        config = ProjectToolConfig(
            tool_type=ProjectToolType.JIRA, api_url="https://jira.example.com", user_id="test_user"
        )
        await service.register_integration(config)

        # Get projects
        projects = await service.get_available_projects("test_user", ProjectToolType.JIRA)

        assert len(projects) == 1
        assert projects[0]["key"] == "PROJ"
        assert projects[0]["name"] == "Test Project"

        # Test with non-existent integration
        empty_projects = await service.get_available_projects("test_user", ProjectToolType.TRELLO)
        assert empty_projects == []

    @pytest.mark.asyncio
    @patch.object(JiraIntegration, "create_task", new_callable=AsyncMock)
    @patch.object(JiraIntegration, "test_connection", new_callable=AsyncMock, return_value=True)
    async def test_create_task_in_external_tool(
        self, mock_test_connection, mock_create_task, service
    ):
        """Test creating a task in an external tool."""
        # Set up mock return value
        task = ExternalTask(
            external_id="TASK-123",
            title="New Task",
            status="not_started",
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(hours=1),
            tool_type=ProjectToolType.JIRA,
        )
        mock_create_task.return_value = task

        # Register an integration
        config = ProjectToolConfig(
            tool_type=ProjectToolType.JIRA, api_url="https://jira.example.com", user_id="test_user"
        )
        await service.register_integration(config)

        # Create task
        task_data = {"title": "New Task"}
        created_task = await service.create_task_in_external_tool(
            "test_user", ProjectToolType.JIRA, task_data
        )

        assert created_task is not None
        assert created_task.title == "New Task"
        assert created_task.external_id == "TASK-123"
        mock_create_task.assert_called_once_with(task_data)
