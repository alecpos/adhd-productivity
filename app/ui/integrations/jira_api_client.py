"""
Jira API Client Module

This module provides a client for making requests to the Jira API.
"""

import logging
import traceback
from typing import Dict, Any, List, Optional

from app.ui.project_management_integration import ProjectToolConfig
from app.ui.integrations.jira_authenticator import JiraAuthenticator
from app.ui.integrations.jira_error_handler import JiraErrorHandler

logger = logging.getLogger(__name__)


class JiraApiClient:
    """Client for making requests to the Jira API."""

    def __init__(self, config: ProjectToolConfig, authenticator: JiraAuthenticator):
        """
        Initialize the Jira API client.

        Args:
            config: Configuration for the Jira integration
            authenticator: Authenticator for Jira API
        """
        self.config = config
        self.authenticator = authenticator
        self.error_handler = JiraErrorHandler()

    async def get_issues(self, jql: str) -> List[Dict[str, Any]]:
        """
        Fetch issues from Jira using JQL.

        Args:
            jql: JQL query string

        Returns:
            List of Jira issues
        """
        url = f"{self.config.api_url}/rest/api/3/search"
        params = {"jql": jql}

        try:
            headers = self.authenticator.get_auth_headers()
            response = await self._make_request(url, method="GET", params=params, headers=headers)
            return response.get("issues", [])
        except Exception as e:
            self.error_handler.handle_error(f"Error fetching Jira issues with JQL: {jql}", e)
            raise

    async def get_issue(self, issue_key: str) -> Optional[Dict[str, Any]]:
        """
        Fetch a single issue by key.

        Args:
            issue_key: Jira issue key

        Returns:
            Issue data or None if not found
        """
        url = f"{self.config.api_url}/rest/api/3/issue/{issue_key}"

        try:
            headers = self.authenticator.get_auth_headers()
            return await self._make_request(url, method="GET", headers=headers)
        except Exception as e:
            if hasattr(e, "status") and getattr(e, "status") == 404:
                logger.warning(f"Issue {issue_key} not found")
                return None
            self.error_handler.handle_error(f"Error fetching Jira issue {issue_key}", e)
            raise

    async def create_issue(self, issue_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new issue in Jira.

        Args:
            issue_data: Issue data to create

        Returns:
            Created issue data
        """
        url = f"{self.config.api_url}/rest/api/3/issue"

        try:
            headers = self.authenticator.get_auth_headers()
            return await self._make_request(url, method="POST", json=issue_data, headers=headers)
        except Exception as e:
            self.error_handler.handle_error("Error creating Jira issue", e)
            raise

    async def update_issue(self, issue_key: str, issue_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing issue in Jira.

        Args:
            issue_key: Jira issue key
            issue_data: Updated issue data

        Returns:
            Updated issue data
        """
        url = f"{self.config.api_url}/rest/api/3/issue/{issue_key}"

        try:
            headers = self.authenticator.get_auth_headers()
            return await self._make_request(url, method="PUT", json=issue_data, headers=headers)
        except Exception as e:
            self.error_handler.handle_error(f"Error updating Jira issue {issue_key}", e)
            raise

    async def delete_issue(self, issue_key: str) -> bool:
        """
        Delete an issue in Jira.

        Args:
            issue_key: Jira issue key

        Returns:
            True if successful, raises exception otherwise
        """
        url = f"{self.config.api_url}/rest/api/3/issue/{issue_key}"

        try:
            headers = self.authenticator.get_auth_headers()
            await self._make_request(url, method="DELETE", headers=headers)
            return True
        except Exception as e:
            self.error_handler.handle_error(f"Error deleting Jira issue {issue_key}", e)
            raise

    async def get_projects(self) -> List[Dict[str, Any]]:
        """
        Get available projects from Jira.

        Returns:
            List of Jira projects
        """
        url = f"{self.config.api_url}/rest/api/3/project"

        try:
            headers = self.authenticator.get_auth_headers()
            return await self._make_request(url, method="GET", headers=headers)
        except Exception as e:
            self.error_handler.handle_error("Error fetching Jira projects", e)
            raise

    async def _make_request(self, url, method="GET", params=None, headers=None, json=None):
        """
        Make HTTP request to Jira API.

        Args:
            url: Request URL
            method: HTTP method
            params: URL parameters
            headers: HTTP headers
            json: Request body as JSON

        Returns:
            Response data as dictionary
        """
        logger.debug(f"Making {method} request to {url}")

        # In real implementation we would use aiohttp
        # For example:
        # async with aiohttp.ClientSession() as session:
        #     async with session.request(method, url, params=params, headers=headers, json=json) as response:
        #         response.raise_for_status()
        #         if method == "DELETE":
        #             return None
        #         return await response.json()

        # For this refactoring, we'll use mock data handlers
        request_info = {
            "url": url,
            "method": method,
            "params": params,
            "headers": headers,
            "json": json
        }

        if method == "DELETE":
            return None

        # Get appropriate mock data based on request
        return self._get_mock_response(request_info)

    def _get_mock_response(self, request_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Return mock data based on request information.

        Args:
            request_info: Information about the request

        Returns:
            Mock response data
        """
        url = request_info["url"]
        method = request_info["method"]

        # Handle different request types
        if method == "GET":
            if "search" in url:
                return {"issues": self._get_mock_issues()}
            elif "issue" in url and not "project" in url:
                return self._get_mock_issues()[0]
            elif "project" in url:
                return self._get_mock_projects()
        elif method == "POST":
            return self._create_mock_resource(request_info)
        elif method == "PUT":
            return self._update_mock_resource(request_info)

        # Default response
        return {}

    def _create_mock_resource(self, request_info: Dict[str, Any]) -> Dict[str, Any]:
        """Create and return a mock resource."""
        return {"id": "10001", "key": "PROJ-124"}

    def _update_mock_resource(self, request_info: Dict[str, Any]) -> Dict[str, Any]:
        """Update and return a mock resource."""
        url = request_info["url"]
        key = url.split("/")[-1]
        return {"id": "10001", "key": key}

    def _get_mock_issues(self) -> List[Dict[str, Any]]:
        """Return mock issues for testing."""
        return [
            {
                "id": "10001",
                "key": "PROJ-123",
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
                    "project": {"id": "10000", "key": "PROJ"}
                }
            }
        ]

    def _get_mock_projects(self) -> List[Dict[str, Any]]:
        """Return mock projects for testing."""
        return [
            {"id": "10000", "key": "PROJ1", "name": "Project One"},
            {"id": "10001", "key": "PROJ2", "name": "Project Two"}
        ]
