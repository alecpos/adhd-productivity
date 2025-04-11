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

# Import integrations
from app.ui.integrations.jira_integration import JiraIntegration

logger = logging.getLogger(__name__)


# Enums
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


# Models
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


# Base integration class
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


# Import service components
from app.ui.services.sync_service import (
    import_tasks,
    export_tasks
)


class ProjectManagementService:
    """Service to manage project management tool integrations."""
    
    def __init__(self):
        """Initialize the project management service."""
        self.integrations = {}
        self._load_integration_classes()
    
    def _load_integration_classes(self):
        """Load the available integration classes."""
        self.integration_classes = {
            ProjectToolType.JIRA: JiraIntegration,
            # Add other integrations here as they are implemented
        }
    
    async def register_integration(self, config: ProjectToolConfig) -> bool:
        """
        Register a new project management tool integration for a user.
        
        Args:
            config: Configuration for the integration
            
        Returns:
            True if registration successful, False otherwise
        """
        try:
            # Create the integration instance
            integration_class = self.integration_classes.get(config.tool_type)
            if not integration_class:
                logger.error(f"Unsupported tool type: {config.tool_type}")
                return False
            
            integration = integration_class(config)
            
            # Test connection
            if not await integration.test_connection():
                logger.error(f"Failed to connect to {config.tool_type} for user {config.user_id}")
                return False
            
            # Store the integration
            user_id = config.user_id
            if user_id not in self.integrations:
                self.integrations[user_id] = {}
            
            self.integrations[user_id][config.tool_type] = integration
            logger.info(f"Successfully registered {config.tool_type} integration for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error registering integration: {str(e)}")
            return False
    
    async def get_user_integrations(self, user_id: str) -> List[ProjectToolType]:
        """Get list of integration types registered for a user."""
        return list(self.integrations.get(user_id, {}).keys())
    
    async def get_integration(
        self, user_id: str, tool_type: ProjectToolType
    ) -> Optional[ProjectToolIntegration]:
        """Get a specific integration for a user."""
        return self.integrations.get(user_id, {}).get(tool_type)
    
    async def remove_integration(self, user_id: str, tool_type: ProjectToolType) -> bool:
        """Remove an integration for a user."""
        try:
            if user_id in self.integrations and tool_type in self.integrations[user_id]:
                del self.integrations[user_id][tool_type]
                if not self.integrations[user_id]:
                    del self.integrations[user_id]
                logger.info(f"Removed {tool_type} integration for user {user_id}")
                return True
            logger.warning(f"Integration {tool_type} not found for user {user_id}")
            return False
        except Exception as e:
            logger.error(f"Error removing integration: {str(e)}")
            return False
    
    async def sync_tasks(
        self, user_id: str, tool_type: Optional[ProjectToolType] = None
    ) -> List[SyncResult]:
        """
        Synchronize tasks between local and external project management tools.
        
        Args:
            user_id: User ID
            tool_type: Optional tool type to sync (if None, sync all tools)
            
        Returns:
            List of sync results
        """
        results = []
        user_integrations = self.integrations.get(user_id, {})
        
        if not user_integrations:
            logger.warning(f"No integrations found for user {user_id}")
            return results
        
        if tool_type:
            integration = user_integrations.get(tool_type)
            if integration:
                result = await self._sync_single_tool(user_id, integration)
                results.append(result)
        else:
            for integration in user_integrations.values():
                result = await self._sync_single_tool(user_id, integration)
                results.append(result)
        
        return results
    
    async def _sync_single_tool(
        self, user_id: str, integration: ProjectToolIntegration
    ) -> SyncResult:
        """Synchronize tasks for a single tool."""
        result = SyncResult(
            success=True,
            tool_type=integration.config.tool_type
        )
        
        # Check connection
        if not await integration.test_connection():
            result.success = False
            result.errors.append("Failed to connect to the external service")
            return result
        
        try:
            # Process based on sync direction
            sync_direction = integration.config.sync_direction
            
            if sync_direction in [SyncDirection.IMPORT, SyncDirection.BIDIRECTIONAL]:
                await import_tasks(user_id, integration, result)
            
            if sync_direction in [SyncDirection.EXPORT, SyncDirection.BIDIRECTIONAL]:
                await export_tasks(user_id, integration, result)
            
            # Update last sync time
            integration.config.last_sync = datetime.utcnow()
            logger.info(f"Completed sync for {integration.name} for user {user_id}")
            
        except Exception as e:
            result.success = False
            result.errors.append(f"Sync error: {str(e)}")
            logger.error(f"Error during sync for {integration.name}: {str(e)}")
        
        return result
    
    async def get_available_projects(
        self, user_id: str, tool_type: ProjectToolType
    ) -> List[Dict[str, Any]]:
        """Get available projects from an external tool."""
        integration = await self.get_integration(user_id, tool_type)
        if not integration:
            logger.warning(f"Integration {tool_type} not found for user {user_id}")
            return []
        
        try:
            return await integration.get_projects()
        except Exception as e:
            logger.error(f"Error fetching projects: {str(e)}")
            return []
    
    async def create_task_in_external_tool(
        self, user_id: str, tool_type: ProjectToolType, task_data: Dict[str, Any]
    ) -> Optional[ExternalTask]:
        """Create a task in an external tool."""
        integration = await self.get_integration(user_id, tool_type)
        if not integration:
            logger.warning(f"Integration {tool_type} not found for user {user_id}")
            return None
        
        try:
            return await integration.create_task(task_data)
        except Exception as e:
            logger.error(f"Error creating task: {str(e)}")
            return None
    
    async def update_task_in_external_tool(
        self, user_id: str, tool_type: ProjectToolType, external_id: str, task_data: Dict[str, Any]
    ) -> Optional[ExternalTask]:
        """Update a task in an external tool."""
        integration = await self.get_integration(user_id, tool_type)
        if not integration:
            logger.warning(f"Integration {tool_type} not found for user {user_id}")
            return None
        
        try:
            return await integration.update_task(external_id, task_data)
        except Exception as e:
            logger.error(f"Error updating task: {str(e)}")
            return None
    
    async def get_sync_status(self, user_id: str) -> Dict[ProjectToolType, Dict[str, Any]]:
        """Get synchronization status for all user integrations."""
        status = {}
        user_integrations = self.integrations.get(user_id, {})
        
        for tool_type, integration in user_integrations.items():
            status[tool_type] = {
                "name": integration.name,
                "last_sync": integration.config.last_sync,
                "sync_frequency": integration.config.sync_frequency,
                "sync_direction": integration.config.sync_direction,
                "enabled": integration.config.enabled
            }
        
        return status 