"""
Jira Field Mappers Module

This module provides specialized mapper classes for handling the translation
between Jira fields and ADHD Calendar fields, including status, priority, 
date formatting, and field extraction.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.core.integrations.external_task import ExternalTask, ExternalTaskStatus, ExternalTaskPriority


class StatusMapper:
    """Handles mapping between Jira statuses and ExternalTaskStatus."""
    
    # Mapping from Jira issue status to ExternalTaskStatus
    STATUS_MAP = {
        "To Do": ExternalTaskStatus.NOT_STARTED,
        "Backlog": ExternalTaskStatus.NOT_STARTED,
        "Open": ExternalTaskStatus.NOT_STARTED,
        "In Progress": ExternalTaskStatus.IN_PROGRESS,
        "Under Review": ExternalTaskStatus.IN_PROGRESS,
        "Done": ExternalTaskStatus.COMPLETED,
        "Closed": ExternalTaskStatus.COMPLETED,
        "Resolved": ExternalTaskStatus.COMPLETED,
        "Blocked": ExternalTaskStatus.BLOCKED
    }
    
    # Reverse mapping for status (ExternalTaskStatus to Jira status)
    REVERSE_STATUS_MAP = {
        ExternalTaskStatus.NOT_STARTED: "To Do",
        ExternalTaskStatus.IN_PROGRESS: "In Progress",
        ExternalTaskStatus.COMPLETED: "Done",
        ExternalTaskStatus.BLOCKED: "Blocked"
    }
    
    @classmethod
    def jira_to_external(cls, jira_status: Optional[str]) -> ExternalTaskStatus:
        """
        Map Jira status to ExternalTaskStatus.
        
        Args:
            jira_status: Jira status string
            
        Returns:
            Mapped ExternalTaskStatus
        """
        if not jira_status:
            return ExternalTaskStatus.NOT_STARTED
            
        return cls.STATUS_MAP.get(jira_status, ExternalTaskStatus.NOT_STARTED)
    
    @classmethod
    def external_to_jira(cls, status: ExternalTaskStatus) -> str:
        """
        Map ExternalTaskStatus to Jira status.
        
        Args:
            status: ExternalTaskStatus enum value
            
        Returns:
            Mapped Jira status string
        """
        return cls.REVERSE_STATUS_MAP.get(status, "To Do")


class PriorityMapper:
    """Handles mapping between Jira priorities and ExternalTaskPriority."""
    
    # Mapping from Jira issue priority to ExternalTaskPriority
    PRIORITY_MAP = {
        "Highest": ExternalTaskPriority.CRITICAL,
        "High": ExternalTaskPriority.HIGH,
        "Medium": ExternalTaskPriority.MEDIUM,
        "Low": ExternalTaskPriority.LOW,
        "Lowest": ExternalTaskPriority.TRIVIAL
    }
    
    # Reverse mapping for priority (ExternalTaskPriority to Jira priority)
    REVERSE_PRIORITY_MAP = {
        ExternalTaskPriority.CRITICAL: "Highest",
        ExternalTaskPriority.HIGH: "High",
        ExternalTaskPriority.MEDIUM: "Medium",
        ExternalTaskPriority.LOW: "Low",
        ExternalTaskPriority.TRIVIAL: "Lowest"
    }
    
    @classmethod
    def jira_to_external(cls, jira_priority: Optional[str]) -> ExternalTaskPriority:
        """
        Map Jira priority to ExternalTaskPriority.
        
        Args:
            jira_priority: Jira priority string
            
        Returns:
            Mapped ExternalTaskPriority
        """
        if not jira_priority:
            return ExternalTaskPriority.MEDIUM
            
        return cls.PRIORITY_MAP.get(jira_priority, ExternalTaskPriority.MEDIUM)
    
    @classmethod
    def external_to_jira(cls, priority: ExternalTaskPriority) -> str:
        """
        Map ExternalTaskPriority to Jira priority.
        
        Args:
            priority: ExternalTaskPriority enum value
            
        Returns:
            Mapped Jira priority string
        """
        return cls.REVERSE_PRIORITY_MAP.get(priority, "Medium")


class DateFormatter:
    """Handles date formatting between Jira and ADHD Calendar."""
    
    @staticmethod
    def parse_jira_date(date_str: Optional[str]) -> Optional[datetime]:
        """
        Parse date string from Jira format to datetime.
        
        Args:
            date_str: Jira date string
            
        Returns:
            Parsed datetime or None if parsing fails
        """
        if not date_str:
            return None
            
        try:
            # Jira uses ISO format (2023-01-01T12:00:00.000+0000)
            # or simple date format (2023-01-01)
            if "T" in date_str:
                # Try to parse as ISO datetime
                return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            else:
                # Try to parse as simple date
                return datetime.strptime(date_str, "%Y-%m-%d")
        except (ValueError, TypeError):
            logging.getLogger(__name__).warning(f"Failed to parse Jira date: {date_str}")
            return None
    
    @staticmethod
    def format_date_for_jira(date_value: Optional[datetime]) -> Optional[str]:
        """
        Format datetime to Jira date format.
        
        Args:
            date_value: Datetime to format
            
        Returns:
            Formatted date string or None
        """
        if not date_value:
            return None
            
        try:
            return date_value.strftime("%Y-%m-%d")
        except (ValueError, TypeError):
            logging.getLogger(__name__).warning(f"Failed to format date for Jira: {date_value}")
            return None


class FieldExtractor:
    """Extracts and formats fields from Jira issues."""
    
    @staticmethod
    def extract_status(fields: Dict[str, Any]) -> ExternalTaskStatus:
        """Extract and map status from Jira fields."""
        status_obj = fields.get("status", {})
        jira_status = status_obj.get("name") if status_obj else None
        return StatusMapper.jira_to_external(jira_status)
    
    @staticmethod
    def extract_priority(fields: Dict[str, Any]) -> ExternalTaskPriority:
        """Extract and map priority from Jira fields."""
        priority_obj = fields.get("priority", {})
        jira_priority = priority_obj.get("name") if priority_obj else None
        return PriorityMapper.jira_to_external(jira_priority)
    
    @staticmethod
    def extract_assignee(fields: Dict[str, Any]) -> Optional[str]:
        """Extract assignee from Jira fields."""
        assignee_obj = fields.get("assignee", {})
        if not assignee_obj:
            return None
        return assignee_obj.get("displayName") or assignee_obj.get("name")
    
    @staticmethod
    def extract_project_key(fields: Dict[str, Any]) -> str:
        """Extract project key from Jira fields."""
        project_obj = fields.get("project", {})
        return project_obj.get("key", "") if project_obj else ""
    
    @staticmethod
    def extract_project_name(fields: Dict[str, Any]) -> str:
        """Extract project name from Jira fields."""
        project_obj = fields.get("project", {})
        return project_obj.get("name", "") if project_obj else ""
    
    @staticmethod
    def get_issue_url(jira_issue: Dict[str, Any]) -> str:
        """Generate a URL for viewing the Jira issue."""
        # Extract the Jira base URL and issue key
        browse_url = jira_issue.get("self", "")
        key = jira_issue.get("key", "")
        
        # If both are available, construct the browsable URL
        if browse_url and key:
            base_url = browse_url.split("/rest/")[0]
            return f"{base_url}/browse/{key}"
        
        return ""


class CustomFieldMapper:
    """Handles mapping of custom fields between Jira and ADHD Calendar."""
    
    def __init__(self, field_mappings: Optional[Dict[str, str]] = None):
        """
        Initialize the CustomFieldMapper with optional mappings.
        
        Args:
            field_mappings: Dictionary mapping ADHD Calendar fields to Jira fields
        """
        self.logger = logging.getLogger(__name__)
        self.field_mappings = field_mappings or {}
    
    def map_jira_to_adhd(self, jira_fields: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map Jira custom fields to ADHD Calendar custom fields.
        
        Args:
            jira_fields: Dictionary of Jira fields
            
        Returns:
            Dictionary of mapped ADHD Calendar custom fields
        """
        custom_fields = {}
        
        for adhd_field, jira_field in self.field_mappings.items():
            if jira_field in jira_fields:
                custom_fields[adhd_field] = jira_fields[jira_field]
        
        return custom_fields
    
    def map_adhd_to_jira(self, adhd_fields: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map ADHD Calendar custom fields to Jira custom fields.
        
        Args:
            adhd_fields: Dictionary of ADHD Calendar custom fields
            
        Returns:
            Dictionary of mapped Jira fields
        """
        jira_fields = {}
        
        for adhd_field, jira_field in self.field_mappings.items():
            if adhd_field in adhd_fields:
                jira_fields[jira_field] = adhd_fields[adhd_field]
        
        return jira_fields
    
    def update_mappings(self, new_mappings: Dict[str, str]) -> None:
        """
        Update the field mappings with new entries.
        
        Args:
            new_mappings: Dictionary of new field mappings
        """
        self.logger.info(f"Updating custom field mappings with {len(new_mappings)} entries")
        self.field_mappings.update(new_mappings)
    
    def get_mappings(self) -> Dict[str, str]:
        """
        Get a copy of the current field mappings.
        
        Returns:
            Dictionary of field mappings
        """
        return self.field_mappings.copy()
    
    def clear_mappings(self) -> None:
        """Clear all field mappings."""
        self.logger.info("Clearing all custom field mappings")
        self.field_mappings.clear() 