"""
Jira Integration Module

This module provides integration with Atlassian Jira, allowing users to sync
and manage their tasks between ADHD Calendar and Jira.
"""

import logging
import traceback
from typing import Dict, List, Any, Optional

from app.ui.project_management_integration import (
    ProjectToolIntegration,
    ProjectToolConfig,
    ExternalTask,
    ProjectToolType,
)

from app.ui.integrations.jira_authenticator import JiraAuthenticator
from app.ui.integrations.jira_task_mapper import JiraTaskMapper
from app.ui.integrations.jira_query_builder import JiraQueryBuilder
from app.ui.integrations.resilient_jira_api_client import ResilientJiraApiClient
from app.ui.integrations.jira_error_handler import JiraErrorHandler

logger = logging.getLogger(__name__)


class JiraIntegration(ProjectToolIntegration):
    """Integration with Atlassian Jira."""

    def __init__(self, config: ProjectToolConfig):
        """
        Initialize the Jira integration.

        Args:
            config: Configuration for the Jira integration
        """
        super().__init__(config)
        self.authenticator = JiraAuthenticator(config)
        self.api_client = ResilientJiraApiClient(config, self.authenticator)
        self.query_builder = JiraQueryBuilder()
        self.task_mapper = JiraTaskMapper()
        self.error_handler = JiraErrorHandler()

    async def authenticate(self) -> bool:
        """
        Authenticate with Jira using the provided credentials.

        Returns:
            True if authentication successful, False otherwise
        """
        return await self.authenticator.authenticate()

    async def fetch_tasks(self) -> List[ExternalTask]:
        """
        Fetch issues from Jira and convert them to ExternalTask objects.

        Returns:
            List of ExternalTask objects
        """
        try:
            # Build JQL query
            jql = self.query_builder.build_jql_query(self.config)
            logger.info(f"Fetching Jira issues with query: {jql}")

            # Fetch issues using API client
            issues = await self.api_client.get_issues(jql)
            logger.info(f"Retrieved {len(issues)} issues from Jira")

            # Map issues to ExternalTask objects
            return [
                self.task_mapper.jira_to_external_task(issue, self.config.api_url)
                for issue in issues
            ]

        except Exception as e:
            self.error_handler.handle_error("Error fetching Jira tasks", e)
            return []

    async def create_task(self, task: Dict[str, Any]) -> ExternalTask:
        """
        Create a new issue in Jira.

        Args:
            task: Task data to create

        Returns:
            ExternalTask representing the created Jira issue
        """
        try:
            # Add project information if not present
            if not task.get("project_key") and self.config.project_ids:
                task["project_key"] = self.config.project_ids[0]

            # Convert to Jira format
            issue_data = self.task_mapper.internal_to_jira_issue(task)

            # Create using API client
            result = await self.api_client.create_issue(issue_data)
            logger.info(f"Created Jira issue {result.get('key')}")

            # Return as ExternalTask
            return self._create_external_task_from_result(result, task)

        except Exception as e:
            self.error_handler.handle_error("Error creating Jira task", e)
            raise

    async def update_task(self, external_id: str, task_data: Dict[str, Any]) -> ExternalTask:
        """
        Update an existing issue in Jira.

        Args:
            external_id: Jira issue key
            task_data: Updated task data

        Returns:
            ExternalTask representing the updated Jira issue
        """
        try:
            # Convert to Jira format
            issue_data = self.task_mapper.internal_to_jira_issue(task_data)

            # Update using API client
            result = await self.api_client.update_issue(external_id, issue_data)
            logger.info(f"Updated Jira issue {external_id}")

            # Return as ExternalTask
            return self._create_external_task_from_result(result, task_data)

        except Exception as e:
            self.error_handler.handle_error(f"Error updating Jira task {external_id}", e)
            raise

    async def delete_task(self, external_id: str) -> bool:
        """
        Delete a task in Jira.

        Args:
            external_id: Jira issue key

        Returns:
            True if successful, False otherwise
        """
        try:
            result = await self.api_client.delete_issue(external_id)
            logger.info(f"Deleted Jira issue {external_id}")
            return result
        except Exception as e:
            self.error_handler.handle_error(f"Error deleting Jira task {external_id}", e)
            return False

    async def get_projects(self) -> List[Dict[str, Any]]:
        """
        Get available projects from Jira.

        Returns:
            List of Jira projects
        """
        try:
            projects = await self.api_client.get_projects()
            logger.info(f"Retrieved {len(projects)} projects from Jira")
            return projects
        except Exception as e:
            self.error_handler.handle_error("Error fetching Jira projects", e)
            return []

    async def get_task_details(self, external_id: str) -> Optional[ExternalTask]:
        """
        Get detailed information about a specific task.

        Args:
            external_id: Jira issue key

        Returns:
            ExternalTask or None if not found
        """
        try:
            issue = await self.api_client.get_issue(external_id)
            if not issue:
                return None

            return self.task_mapper.jira_to_external_task(issue, self.config.api_url)
        except Exception as e:
            self.error_handler.handle_error(f"Error fetching Jira task {external_id}", e)
            return None

    def _create_external_task_from_result(self, result: Dict[str, Any], task_data: Dict[str, Any]) -> ExternalTask:
        """
        Create an ExternalTask from Jira API result and task data.

        Args:
            result: Result from Jira API
            task_data: Original task data

        Returns:
            ExternalTask representing the Jira issue
        """
        # Get project ID from config if not in task data
        project_id = task_data.get("project_key")
        if not project_id and self.config.project_ids:
            project_id = self.config.project_ids[0]

        return ExternalTask(
            external_id=result["key"],
            title=task_data["title"],
            description=task_data.get("description"),
            status=task_data.get("status", "not_started"),
            due_date=task_data.get("due_date"),
            created_date=None,  # Will be set by Jira
            updated_date=None,  # Will be set by Jira
            priority=task_data.get("priority"),
            labels=task_data.get("labels", []),
            project_id=project_id,
            url=f"{self.config.api_url}/browse/{result['key']}",
            tool_type=ProjectToolType.JIRA,
            additional_data={"key": result["key"]}
        )

    def get_health_metrics(self) -> Dict[str, Any]:
        """
        Get health metrics for the integration.

        Returns:
            Dictionary of health metrics
        """
        return {
            "client_metrics": self.api_client.get_health_metrics(),
            "config": {
                "api_url": self.config.api_url,
                "project_ids": self.config.project_ids,
                "last_sync": self.config.last_sync.isoformat() if self.config.last_sync else None,
            }
        }
