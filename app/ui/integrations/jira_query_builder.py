"""
Jira Query Builder Module

This module builds JQL (Jira Query Language) queries for fetching issues.
"""

import logging
from typing import List
from datetime import datetime

from app.ui.project_management_integration import ProjectToolConfig

logger = logging.getLogger(__name__)


class JiraQueryBuilder:
    """Builds JQL (Jira Query Language) queries."""

    def build_jql_query(self, config: ProjectToolConfig) -> str:
        """
        Build a JQL query based on the configuration.

        Args:
            config: The integration configuration

        Returns:
            JQL query string
        """
        jql_parts = []

        # Filter by project if specified
        if config.project_ids:
            project_clause = self._build_project_clause(config.project_ids)
            jql_parts.append(project_clause)

        # Filter by labels if specified
        if config.labels_to_sync:
            label_clause = self._build_label_clause(config.labels_to_sync)
            jql_parts.append(label_clause)

        # Limit to recent updates if not initial sync
        if config.last_sync:
            updated_clause = self._build_updated_clause(config.last_sync)
            jql_parts.append(updated_clause)

        # Combine all parts with AND operator
        jql = " AND ".join(jql_parts) if jql_parts else ""

        # Add default ordering
        jql = self._add_ordering(jql)

        logger.debug(f"Built JQL query: {jql}")
        return jql

    def _build_project_clause(self, project_ids: List[str]) -> str:
        """
        Build a JQL clause to filter by projects.

        Args:
            project_ids: List of project IDs or keys

        Returns:
            JQL clause for filtering by projects
        """
        # Handle single project case more efficiently
        if len(project_ids) == 1:
            return f"project = {project_ids[0]}"

        project_clause = " OR ".join([f"project = {pid}" for pid in project_ids])
        return f"({project_clause})"

    def _build_label_clause(self, labels: List[str]) -> str:
        """
        Build a JQL clause to filter by labels.

        Args:
            labels: List of label strings

        Returns:
            JQL clause for filtering by labels
        """
        # Handle single label case more efficiently
        if len(labels) == 1:
            return f"labels = {labels[0]}"

        label_clause = " OR ".join([f"labels = {label}" for label in labels])
        return f"({label_clause})"

    def _build_updated_clause(self, last_sync: datetime) -> str:
        """
        Build a JQL clause to filter by update date.

        Args:
            last_sync: Datetime of the last synchronization

        Returns:
            JQL clause for filtering by update date
        """
        # Format with timezone info
        last_sync_str = last_sync.strftime("%Y-%m-%d %H:%M")
        return f"updated >= '{last_sync_str}'"

    def _add_ordering(self, jql: str) -> str:
        """
        Add ordering to the JQL query.

        Args:
            jql: Existing JQL query string

        Returns:
            JQL query with ordering added
        """
        if jql:
            return f"{jql} ORDER BY updated DESC"
        else:
            return "ORDER BY updated DESC"

    def build_single_issue_query(self, issue_key: str) -> str:
        """
        Build a JQL query to fetch a single issue by key.

        Args:
            issue_key: The Jira issue key

        Returns:
            JQL query for a single issue
        """
        return f"key = {issue_key}"

    def build_status_change_query(self, project_ids: List[str], status: str, days: int = 7) -> str:
        """
        Build a JQL query to find issues with status changes.

        Args:
            project_ids: List of project IDs or keys
            status: The status to filter for
            days: Number of days to look back

        Returns:
            JQL query for finding status changes
        """
        project_clause = self._build_project_clause(project_ids)
        return (
            f"{project_clause} AND status = '{status}' AND "
            f"statusChanged >= -{days}d ORDER BY statusChanged DESC"
        )
