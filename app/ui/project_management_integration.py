"""
Project Management Tool Integration System (ADHD-30)

This module provides integration with popular project management tools,
allowing users to sync and manage their tasks across multiple platforms.
"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Union

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ProjectToolType(str, Enum):
    """Types of supported project management tools."""
    JIRA = "jira"
    TRELLO = "trello"
    ASANA = "asana"
    GITHUB = "github"
    GITLAB = "gitlab"
    MONDAY = "monday"
    NOTION = "notion"
    CLICKUP = "clickup"
    TODOIST = "todoist"
    BASECAMP = "basecamp"
    CUSTOM = "custom"


class SyncDirection(str, Enum):
    """Direction of synchronization between ADHD Calendar and external tools."""
    IMPORT = "import"  # One-way sync from external to local
    EXPORT = "export"  # One-way sync from local to external
    BIDIRECTIONAL = "bidirectional"  # Two-way sync


class SyncFrequency(str, Enum):
    """How often synchronization should occur."""
    MANUAL = "manual"
    HOURLY = "hourly"
    DAILY = "daily"
    ON_CHANGE = "on_change"  # Sync when changes are detected


class ProjectToolConfig(BaseModel):
    """Configuration for a project management tool integration."""
    tool_type: ProjectToolType
    api_url: str
    auth_token: Optional[str] = None
    auth_user: Optional[str] = None
    auth_password: Optional[str] = None
    sync_direction: SyncDirection = SyncDirection.BIDIRECTIONAL
    sync_frequency: SyncFrequency = SyncFrequency.ON_CHANGE
    workspace_id: Optional[str] = None
    project_ids: List[str] = Field(default_factory=list)
    labels_to_sync: List[str] = Field(default_factory=list)
    enabled: bool = True
    last_sync: Optional[datetime] = None
    user_id: str


class ExternalTask(BaseModel):
    """Representation of a task from an external project management tool."""
    external_id: str
    title: str
    description: Optional[str] = None
    status: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    due_date: Optional[datetime] = None
    created_date: Optional[datetime] = None
    updated_date: Optional[datetime] = None
    priority: Optional[str] = None
    assignee: Optional[str] = None
    labels: List[str] = Field(default_factory=list)
    project_id: Optional[str] = None
    url: Optional[str] = None
    parent_id: Optional[str] = None
    tool_type: ProjectToolType
    is_all_day: bool = False
    location: Optional[str] = None
    attendees: List[Dict[str, str]] = Field(default_factory=list)
    additional_data: Dict[str, Any] = Field(default_factory=dict)


class SyncResult(BaseModel):
    """Result of a synchronization operation."""
    success: bool
    tool_type: ProjectToolType
    tasks_imported: int = 0
    tasks_exported: int = 0
    tasks_updated: int = 0
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    details: Dict[str, Any] = Field(default_factory=dict)


class ProjectToolIntegration(ABC):
    """Base abstract class for all project management tool integrations."""
    
    def __init__(self, config: ProjectToolConfig):
        self.config = config
        self.name = config.tool_type.value.capitalize()
    
    @abstractmethod
    async def authenticate(self) -> bool:
        """Authenticate with the external service."""
        pass
    
    @abstractmethod
    async def fetch_tasks(self) -> List[ExternalTask]:
        """Fetch tasks from the external service."""
        pass
    
    @abstractmethod
    async def create_task(self, task: Dict[str, Any]) -> ExternalTask:
        """Create a new task in the external service."""
        pass
    
    @abstractmethod
    async def update_task(self, external_id: str, task_data: Dict[str, Any]) -> ExternalTask:
        """Update an existing task in the external service."""
        pass
    
    @abstractmethod
    async def delete_task(self, external_id: str) -> bool:
        """Delete a task in the external service."""
        pass
    
    @abstractmethod
    async def get_projects(self) -> List[Dict[str, Any]]:
        """Get available projects from the external service."""
        pass
    
    async def test_connection(self) -> bool:
        """Test the connection to the external service."""
        try:
            return await self.authenticate()
        except Exception as e:
            logger.error(f"Connection test failed for {self.name}: {str(e)}")
            return False
    
    def map_priority(self, external_priority: str) -> str:
        """Map external priority to internal priority format."""
        # Default mapping, can be overridden by specific implementations
        priority_map = {
            "highest": "critical",
            "high": "high",
            "medium": "medium",
            "low": "low",
            "lowest": "trivial"
        }
        return priority_map.get(external_priority.lower(), "medium")
    
    def map_status(self, external_status: str) -> str:
        """Map external status to internal status format."""
        # Default mapping, can be overridden by specific implementations
        status_map = {
            "to do": "not_started",
            "in progress": "in_progress",
            "done": "completed",
            "blocked": "blocked"
        }
        return status_map.get(external_status.lower(), "not_started")


class JiraIntegration(ProjectToolIntegration):
    """Integration with Atlassian Jira."""
    
    async def authenticate(self) -> bool:
        """Authenticate with Jira using the provided credentials."""
        try:
            # In a real implementation, we would use a Jira client library
            headers = self._get_auth_headers()
            # Make a test API call to verify credentials
            # For example: requests.get(f"{self.config.api_url}/rest/api/3/myself", headers=headers)
            logger.info(f"Successfully authenticated with Jira at {self.config.api_url}")
            return True
        except Exception as e:
            logger.error(f"Failed to authenticate with Jira: {str(e)}")
            return False
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """Create authentication headers for Jira API requests."""
        headers = {"Content-Type": "application/json"}
        
        if self.config.auth_token:
            headers["Authorization"] = f"Bearer {self.config.auth_token}"
        elif self.config.auth_user and self.config.auth_password:
            # Basic authentication - in production, we'd use a proper base64 encoding
            # import base64
            # auth_str = f"{self.config.auth_user}:{self.config.auth_password}"
            # encoded = base64.b64encode(auth_str.encode()).decode()
            # headers["Authorization"] = f"Basic {encoded}"
            pass
        
        return headers
    
    async def fetch_tasks(self) -> List[ExternalTask]:
        """Fetch issues from Jira."""
        try:
            # Build JQL (Jira Query Language) for fetching relevant issues
            jql = self._build_jql_query()
            
            # In real implementation:
            # response = await make_api_call(f"{self.config.api_url}/rest/api/3/search?jql={jql}")
            # data = response.json()
            
            # Simulate API response for this example
            mock_data = {
                "issues": [
                    {
                        "id": "JRA-123",
                        "key": "JRA-123",
                        "fields": {
                            "summary": "Implement project sync",
                            "description": "Create bidirectional sync with project tools",
                            "status": {"name": "In Progress"},
                            "duedate": "2023-06-30",
                            "created": "2023-05-01T10:00:00.000Z",
                            "updated": "2023-05-15T14:30:00.000Z",
                            "priority": {"name": "High"},
                            "assignee": {"displayName": "John Doe"},
                            "labels": ["adhd-calendar", "integration"],
                            "project": {"id": "10000", "key": "JRA"}
                        }
                    }
                ]
            }
            
            # Map Jira issues to our ExternalTask model
            tasks = []
            for issue in mock_data["issues"]:
                fields = issue["fields"]
                
                task = ExternalTask(
                    external_id=issue["key"],
                    title=fields["summary"],
                    description=fields.get("description"),
                    status=self.map_status(fields["status"]["name"]),
                    due_date=datetime.fromisoformat(fields["duedate"]) if fields.get("duedate") else None,
                    created_date=datetime.fromisoformat(fields["created"].replace("Z", "+00:00")) if fields.get("created") else None,
                    updated_date=datetime.fromisoformat(fields["updated"].replace("Z", "+00:00")) if fields.get("updated") else None,
                    priority=self.map_priority(fields["priority"]["name"]) if fields.get("priority") else None,
                    assignee=fields["assignee"]["displayName"] if fields.get("assignee") else None,
                    labels=fields.get("labels", []),
                    project_id=fields["project"]["id"],
                    url=f"{self.config.api_url}/browse/{issue['key']}",
                    tool_type=ProjectToolType.JIRA,
                    additional_data={"key": issue["key"]}
                )
                tasks.append(task)
            
            return tasks
        except Exception as e:
            logger.error(f"Error fetching Jira tasks: {str(e)}")
            return []
    
    def _build_jql_query(self) -> str:
        """Build a JQL query based on the configuration."""
        jql_parts = []
        
        # Filter by project if specified
        if self.config.project_ids:
            project_clause = " OR ".join([f"project = {pid}" for pid in self.config.project_ids])
            jql_parts.append(f"({project_clause})")
        
        # Filter by labels if specified
        if self.config.labels_to_sync:
            label_clause = " OR ".join([f"labels = {label}" for label in self.config.labels_to_sync])
            jql_parts.append(f"({label_clause})")
        
        # Limit to recent updates if not initial sync
        if self.config.last_sync:
            last_sync_str = self.config.last_sync.strftime("%Y-%m-%d %H:%M")
            jql_parts.append(f"updated >= '{last_sync_str}'")
        
        # Combine all parts
        jql = " AND ".join(jql_parts) if jql_parts else ""
        
        # Default ordering
        if jql:
            jql += " ORDER BY updated DESC"
        else:
            jql = "ORDER BY updated DESC"
        
        return jql
    
    async def create_task(self, task: Dict[str, Any]) -> ExternalTask:
        """Create a new issue in Jira."""
        try:
            # Prepare data for Jira API
            issue_data = {
                "fields": {
                    "project": {"key": task.get("project_key", self.config.project_ids[0])},
                    "summary": task["title"],
                    "description": task.get("description", ""),
                    "issuetype": {"name": "Task"},
                }
            }
            
            # Set optional fields
            if task.get("due_date"):
                issue_data["fields"]["duedate"] = task["due_date"].strftime("%Y-%m-%d")
            
            if task.get("priority"):
                # Map internal priority back to Jira priority
                priority_map = {v: k for k, v in {
                    "Highest": "critical",
                    "High": "high", 
                    "Medium": "medium",
                    "Low": "low",
                    "Lowest": "trivial"
                }.items()}
                issue_data["fields"]["priority"] = {"name": priority_map.get(task["priority"], "Medium")}
            
            if task.get("labels"):
                issue_data["fields"]["labels"] = task["labels"]
            
            # In real implementation:
            # response = await make_api_call(
            #     f"{self.config.api_url}/rest/api/3/issue",
            #     method="POST",
            #     json=issue_data,
            #     headers=self._get_auth_headers()
            # )
            # result = response.json()
            
            # Mock response for this example
            mock_result = {"id": "10001", "key": "JRA-124"}
            
            # Return the created task
            return ExternalTask(
                external_id=mock_result["key"],
                title=task["title"],
                description=task.get("description"),
                status="not_started",  # New tasks typically start as "To Do"
                due_date=task.get("due_date"),
                created_date=datetime.utcnow(),
                updated_date=datetime.utcnow(),
                priority=task.get("priority"),
                labels=task.get("labels", []),
                project_id=task.get("project_key", self.config.project_ids[0]),
                url=f"{self.config.api_url}/browse/{mock_result['key']}",
                tool_type=ProjectToolType.JIRA,
                additional_data={"key": mock_result["key"]}
            )
        except Exception as e:
            logger.error(f"Error creating Jira task: {str(e)}")
            raise
    
    async def update_task(self, external_id: str, task_data: Dict[str, Any]) -> ExternalTask:
        """Update an existing issue in Jira."""
        try:
            # Prepare data for Jira API
            issue_data = {"fields": {}}
            
            # Add fields to update
            if "title" in task_data:
                issue_data["fields"]["summary"] = task_data["title"]
                
            if "description" in task_data:
                issue_data["fields"]["description"] = task_data["description"]
                
            if "status" in task_data:
                # Map internal status to Jira status
                # In a real implementation, this would involve transition IDs
                status_map = {v: k for k, v in {
                    "To Do": "not_started",
                    "In Progress": "in_progress",
                    "Done": "completed",
                    "Blocked": "blocked"
                }.items()}
                jira_status = status_map.get(task_data["status"], "To Do")
                # This is simplified - in reality, we'd need to use the transitions API
                issue_data["fields"]["status"] = {"name": jira_status}
            
            if "due_date" in task_data:
                issue_data["fields"]["duedate"] = task_data["due_date"].strftime("%Y-%m-%d") if task_data["due_date"] else None
            
            if "priority" in task_data:
                priority_map = {v: k for k, v in {
                    "Highest": "critical",
                    "High": "high", 
                    "Medium": "medium",
                    "Low": "low",
                    "Lowest": "trivial"
                }.items()}
                issue_data["fields"]["priority"] = {"name": priority_map.get(task_data["priority"], "Medium")}
            
            if "labels" in task_data:
                issue_data["fields"]["labels"] = task_data["labels"]
            
            # In real implementation:
            # response = await make_api_call(
            #     f"{self.config.api_url}/rest/api/3/issue/{external_id}",
            #     method="PUT",
            #     json=issue_data,
            #     headers=self._get_auth_headers()
            # )
            
            # For this example, just return a mock updated task
            return ExternalTask(
                external_id=external_id,
                title=task_data.get("title", "Updated Task"),
                description=task_data.get("description"),
                status=task_data.get("status", "not_started"),
                due_date=task_data.get("due_date"),
                created_date=datetime.utcnow() - timedelta(days=1),
                updated_date=datetime.utcnow(),
                priority=task_data.get("priority"),
                labels=task_data.get("labels", []),
                project_id=task_data.get("project_id"),
                url=f"{self.config.api_url}/browse/{external_id}",
                tool_type=ProjectToolType.JIRA,
                additional_data={"key": external_id}
            )
        except Exception as e:
            logger.error(f"Error updating Jira task {external_id}: {str(e)}")
            raise
    
    async def delete_task(self, external_id: str) -> bool:
        """Delete an issue in Jira."""
        try:
            # In real implementation:
            # response = await make_api_call(
            #     f"{self.config.api_url}/rest/api/3/issue/{external_id}",
            #     method="DELETE",
            #     headers=self._get_auth_headers()
            # )
            # return response.status_code == 204  # No content = success
            
            # Mock success
            logger.info(f"Deleted Jira issue {external_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting Jira task {external_id}: {str(e)}")
            return False
    
    async def get_projects(self) -> List[Dict[str, Any]]:
        """Get available projects from Jira."""
        try:
            # In real implementation:
            # response = await make_api_call(
            #     f"{self.config.api_url}/rest/api/3/project",
            #     headers=self._get_auth_headers()
            # )
            # return response.json()
            
            # Mock response
            return [
                {"id": "10000", "key": "JRA", "name": "Jira Core"},
                {"id": "10001", "key": "ADHD", "name": "ADHD Calendar"}
            ]
        except Exception as e:
            logger.error(f"Error fetching Jira projects: {str(e)}")
            return []
    
    def map_status(self, external_status: str) -> str:
        """Map Jira status to internal status format."""
        status_map = {
            "to do": "not_started",
            "in progress": "in_progress",
            "done": "completed",
            "blocked": "blocked",
            "reopened": "not_started",
            "resolved": "completed",
            "closed": "completed"
        }
        return status_map.get(external_status.lower(), "not_started") 


class ProjectManagementService:
    """
    Service for coordinating multiple project management tool integrations.
    Handles synchronization, mapping, and integration management.
    """
    
    def __init__(self):
        self.integrations: Dict[str, Dict[ProjectToolType, ProjectToolIntegration]] = {}
        self._load_integration_classes()
    
    def _load_integration_classes(self):
        """Load available integration classes."""
        self.integration_classes = {
            ProjectToolType.JIRA: JiraIntegration,
            # Add other integrations as they are implemented
            # ProjectToolType.TRELLO: TrelloIntegration,
            # ProjectToolType.ASANA: AsanaIntegration,
            # ProjectToolType.GITHUB: GitHubIntegration,
        }
    
    async def register_integration(self, config: ProjectToolConfig) -> bool:
        """Register and initialize a new tool integration for a user."""
        try:
            # Check if we have an implementation for this tool type
            if config.tool_type not in self.integration_classes:
                logger.error(f"No integration available for {config.tool_type.value}")
                return False
            
            # Create the integration instance
            integration_class = self.integration_classes[config.tool_type]
            integration = integration_class(config)
            
            # Test the connection
            if not await integration.test_connection():
                logger.error(f"Connection test failed for {config.tool_type.value}")
                return False
            
            # Store the integration for the user
            user_id = config.user_id
            if user_id not in self.integrations:
                self.integrations[user_id] = {}
            
            self.integrations[user_id][config.tool_type] = integration
            logger.info(f"Registered {config.tool_type.value} integration for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error registering {config.tool_type.value} integration: {str(e)}")
            return False
    
    async def get_user_integrations(self, user_id: str) -> List[ProjectToolType]:
        """Get all registered integrations for a user."""
        if user_id not in self.integrations:
            return []
        return list(self.integrations[user_id].keys())
    
    async def get_integration(
        self, user_id: str, tool_type: ProjectToolType
    ) -> Optional[ProjectToolIntegration]:
        """Get a specific integration for a user."""
        if user_id not in self.integrations or tool_type not in self.integrations[user_id]:
            return None
        return self.integrations[user_id][tool_type]
    
    async def remove_integration(self, user_id: str, tool_type: ProjectToolType) -> bool:
        """Remove a tool integration for a user."""
        if user_id not in self.integrations or tool_type not in self.integrations[user_id]:
            return False
        
        del self.integrations[user_id][tool_type]
        if not self.integrations[user_id]:
            del self.integrations[user_id]
        
        logger.info(f"Removed {tool_type.value} integration for user {user_id}")
        return True
    
    async def sync_tasks(
        self, user_id: str, tool_type: Optional[ProjectToolType] = None
    ) -> List[SyncResult]:
        """
        Synchronize tasks between ADHD Calendar and external project tools.
        If tool_type is provided, sync only that tool, otherwise sync all.
        """
        results = []
        
        if user_id not in self.integrations:
            logger.warning(f"No integrations registered for user {user_id}")
            return results
        
        tool_types = [tool_type] if tool_type else list(self.integrations[user_id].keys())
        
        for tt in tool_types:
            if tt not in self.integrations[user_id]:
                logger.warning(f"Integration {tt.value} not registered for user {user_id}")
                continue
            
            integration = self.integrations[user_id][tt]
            result = await self._sync_single_tool(user_id, integration)
            results.append(result)
        
        return results
    
    async def _sync_single_tool(
        self, user_id: str, integration: ProjectToolIntegration
    ) -> SyncResult:
        """Synchronize tasks for a single tool integration."""
        result = SyncResult(
            success=False,
            tool_type=integration.config.tool_type
        )
        
        try:
            # Start with empty success
            result.success = True
            
            # Import tasks from external tool if configured
            if integration.config.sync_direction in [SyncDirection.IMPORT, SyncDirection.BIDIRECTIONAL]:
                await self._import_tasks(user_id, integration, result)
            
            # Export tasks to external tool if configured
            if integration.config.sync_direction in [SyncDirection.EXPORT, SyncDirection.BIDIRECTIONAL]:
                await self._export_tasks(user_id, integration, result)
            
            # Update last sync time
            integration.config.last_sync = datetime.utcnow()
            
            # In a real implementation, we would save the updated config
            # await self._save_integration_config(integration.config)
            
            logger.info(
                f"Sync completed for {integration.name}: "
                f"imported {result.tasks_imported}, "
                f"exported {result.tasks_exported}, "
                f"updated {result.tasks_updated}"
            )
        except Exception as e:
            error_msg = f"Error syncing with {integration.name}: {str(e)}"
            logger.error(error_msg)
            result.success = False
            result.errors.append(error_msg)
        
        return result
    
    async def _import_tasks(
        self, user_id: str, integration: ProjectToolIntegration, result: SyncResult
    ):
        """Import tasks from external tool to ADHD Calendar."""
        # Fetch tasks from external tool
        external_tasks = await integration.fetch_tasks()
        
        # In a real implementation, we would get existing tasks from the database
        # existing_tasks = await self._get_existing_tasks(user_id, integration.config.tool_type)
        existing_tasks = []  # Mock empty list for this example
        
        # Find tasks to import (not already in our system)
        tasks_to_import = []
        for ext_task in external_tasks:
            if not any(t.get("external_id") == ext_task.external_id for t in existing_tasks):
                tasks_to_import.append(ext_task)
        
        # Find tasks to update (already in our system but changed)
        tasks_to_update = []
        for ext_task in external_tasks:
            for local_task in existing_tasks:
                if local_task.get("external_id") == ext_task.external_id:
                    if local_task.get("updated_date") < ext_task.updated_date:
                        tasks_to_update.append((local_task, ext_task))
                    break
        
        # Import new tasks
        for ext_task in tasks_to_import:
            # In a real implementation, we would save to database
            # await self._create_local_task(user_id, ext_task)
            result.tasks_imported += 1
        
        # Update existing tasks
        for local_task, ext_task in tasks_to_update:
            # In a real implementation, we would update in database
            # await self._update_local_task(local_task["id"], ext_task)
            result.tasks_updated += 1
    
    async def _export_tasks(
        self, user_id: str, integration: ProjectToolIntegration, result: SyncResult
    ):
        """Export tasks from ADHD Calendar to external tool."""
        # In a real implementation, we would get local tasks from the database
        # local_tasks = await self._get_local_tasks_for_export(user_id, integration.config)
        local_tasks = []  # Mock empty list for this example
        
        # Fetch existing tasks from external tool for comparison
        external_tasks = await integration.fetch_tasks()
        external_ids = [t.external_id for t in external_tasks]
        
        # Find tasks to export (not already in external system)
        tasks_to_export = []
        for task in local_tasks:
            if not task.get("external_id") or task.get("external_id") not in external_ids:
                tasks_to_export.append(task)
        
        # Find tasks to update (already in external system but changed)
        tasks_to_update = []
        for task in local_tasks:
            if task.get("external_id") and task.get("external_id") in external_ids:
                # Find the corresponding external task
                ext_task = next((t for t in external_tasks if t.external_id == task.get("external_id")), None)
                if ext_task and task.get("updated_date") > ext_task.updated_date:
                    tasks_to_update.append(task)
        
        # Export new tasks
        for task in tasks_to_export:
            try:
                # In a real implementation, we would create in external system and update local reference
                # ext_task = await integration.create_task(task)
                # await self._update_local_task_external_id(task["id"], ext_task.external_id)
                result.tasks_exported += 1
            except Exception as e:
                error_msg = f"Error exporting task {task.get('id')}: {str(e)}"
                logger.error(error_msg)
                result.errors.append(error_msg)
        
        # Update existing tasks
        for task in tasks_to_update:
            try:
                # In a real implementation, we would update in external system
                # await integration.update_task(task["external_id"], task)
                result.tasks_updated += 1
            except Exception as e:
                error_msg = f"Error updating external task {task.get('external_id')}: {str(e)}"
                logger.error(error_msg)
                result.errors.append(error_msg)
    
    async def get_available_projects(
        self, user_id: str, tool_type: ProjectToolType
    ) -> List[Dict[str, Any]]:
        """Get available projects from an external tool."""
        integration = await self.get_integration(user_id, tool_type)
        if not integration:
            logger.warning(f"Integration {tool_type.value} not found for user {user_id}")
            return []
        
        return await integration.get_projects()
    
    async def create_task_in_external_tool(
        self, user_id: str, tool_type: ProjectToolType, task_data: Dict[str, Any]
    ) -> Optional[ExternalTask]:
        """Create a task directly in an external tool."""
        integration = await self.get_integration(user_id, tool_type)
        if not integration:
            logger.warning(f"Integration {tool_type.value} not found for user {user_id}")
            return None
        
        try:
            return await integration.create_task(task_data)
        except Exception as e:
            logger.error(f"Error creating task in {tool_type.value}: {str(e)}")
            return None
    
    async def update_task_in_external_tool(
        self, user_id: str, tool_type: ProjectToolType, external_id: str, task_data: Dict[str, Any]
    ) -> Optional[ExternalTask]:
        """Update a task directly in an external tool."""
        integration = await self.get_integration(user_id, tool_type)
        if not integration:
            logger.warning(f"Integration {tool_type.value} not found for user {user_id}")
            return None
        
        try:
            return await integration.update_task(external_id, task_data)
        except Exception as e:
            logger.error(f"Error updating task {external_id} in {tool_type.value}: {str(e)}")
            return None
    
    async def get_sync_status(self, user_id: str) -> Dict[ProjectToolType, Dict[str, Any]]:
        """Get synchronization status for all user integrations."""
        status = {}
        
        if user_id not in self.integrations:
            return status
        
        for tool_type, integration in self.integrations[user_id].items():
            status[tool_type] = {
                "last_sync": integration.config.last_sync,
                "sync_direction": integration.config.sync_direction.value,
                "sync_frequency": integration.config.sync_frequency.value,
                "enabled": integration.config.enabled
            }
        
        return status 