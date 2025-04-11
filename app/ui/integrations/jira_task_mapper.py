"""
JiraTaskMapper module handles mapping between Jira issues and ADHD Calendar tasks.

This module provides functionality to convert Jira issue objects to ADHD Calendar
task objects and vice versa, ensuring proper field mapping and data consistency.
"""

import logging
from typing import Any, Dict, List, Optional

from app.core.integrations.external_task import ExternalTask, ExternalTaskStatus, ExternalTaskPriority
from app.ui.integrations.jira_field_mappers import (
    StatusMapper, PriorityMapper, DateFormatter, FieldExtractor, CustomFieldMapper
)


class JiraTaskMapper:
    """
    Maps between Jira issues and ADHD Calendar tasks.
    
    This class handles the conversion between Jira's issue format and 
    ADHD Calendar's task format, ensuring proper field mapping and data transformation.
    """
    
    def __init__(self, custom_field_mappings: Optional[Dict[str, str]] = None):
        """
        Initialize the JiraTaskMapper with optional custom field mappings.
        
        Args:
            custom_field_mappings: Optional dictionary mapping ADHD Calendar task 
                                  fields to Jira custom fields
        """
        self.logger = logging.getLogger(__name__)
        self.custom_field_mapper = CustomFieldMapper(custom_field_mappings)
    
    def jira_to_external_task(self, jira_issue: Dict[str, Any]) -> ExternalTask:
        """
        Convert a Jira issue to an ExternalTask object.
        
        Args:
            jira_issue: Dictionary containing Jira issue data
            
        Returns:
            ExternalTask object representing the Jira issue
        """
        self.logger.debug(f"Converting Jira issue {jira_issue.get('key')} to external task")
        
        # Extract fields dictionary
        fields = jira_issue.get("fields", {})
        
        # Create external task object
        external_task = ExternalTask(
            id=jira_issue.get("id", ""),
            external_id=jira_issue.get("key", ""),
            title=fields.get("summary", ""),
            description=fields.get("description", ""),
            status=FieldExtractor.extract_status(fields),
            priority=FieldExtractor.extract_priority(fields),
            created_at=DateFormatter.parse_jira_date(fields.get("created")),
            updated_at=DateFormatter.parse_jira_date(fields.get("updated")),
            due_date=DateFormatter.parse_jira_date(fields.get("duedate")),
            assignee=FieldExtractor.extract_assignee(fields),
            project_id=FieldExtractor.extract_project_key(fields),
            project_name=FieldExtractor.extract_project_name(fields),
            labels=fields.get("labels", []),
            url=FieldExtractor.get_issue_url(jira_issue),
            raw_data=jira_issue  # Store original Jira data for reference
        )
        
        # Map custom fields
        external_task.custom_fields = self.custom_field_mapper.map_jira_to_adhd(fields)
        
        return external_task
    
    def external_task_to_jira(self, task: ExternalTask) -> Dict[str, Any]:
        """
        Convert an ExternalTask to a Jira issue format.
        
        Args:
            task: ExternalTask object to convert
            
        Returns:
            Dictionary with Jira issue fields
        """
        self.logger.debug(f"Converting external task '{task.title}' to Jira issue format")
        
        # Create fields dictionary for Jira
        jira_fields = self._create_base_jira_fields(task)
        
        # Add status field if needed
        self._add_status_field_if_needed(task, jira_fields)
        
        # Add priority field if needed
        self._add_priority_field_if_needed(task, jira_fields)
        
        # Add date fields if needed
        self._add_date_fields(task, jira_fields)
        
        # Map custom fields
        if task.custom_fields:
            custom_jira_fields = self.custom_field_mapper.map_adhd_to_jira(task.custom_fields)
            jira_fields.update(custom_jira_fields)
        
        return {"fields": jira_fields}
    
    def _create_base_jira_fields(self, task: ExternalTask) -> Dict[str, Any]:
        """Create the base Jira fields dictionary from task."""
        return {
            "summary": task.title,
            "description": task.description or "",
            "labels": task.labels
        }
    
    def _add_status_field_if_needed(self, task: ExternalTask, jira_fields: Dict[str, Any]) -> None:
        """Add status field to Jira fields if needed."""
        if task.status != ExternalTaskStatus.NOT_STARTED:
            jira_status = StatusMapper.external_to_jira(task.status)
            if jira_status:
                # Note: Changing status in Jira typically requires a transition
                jira_fields["status"] = {"name": jira_status}
    
    def _add_priority_field_if_needed(self, task: ExternalTask, jira_fields: Dict[str, Any]) -> None:
        """Add priority field to Jira fields if needed."""
        if task.priority != ExternalTaskPriority.MEDIUM:
            jira_priority = PriorityMapper.external_to_jira(task.priority)
            if jira_priority:
                jira_fields["priority"] = {"name": jira_priority}
    
    def _add_date_fields(self, task: ExternalTask, jira_fields: Dict[str, Any]) -> None:
        """Add date fields to Jira fields if present in task."""
        if task.due_date:
            jira_fields["duedate"] = DateFormatter.format_date_for_jira(task.due_date)
    
    def map_multiple_issues(self, jira_issues: List[Dict[str, Any]]) -> List[ExternalTask]:
        """
        Convert a list of Jira issues to ExternalTask objects.
        
        Args:
            jira_issues: List of dictionaries containing Jira issue data
            
        Returns:
            List of ExternalTask objects
        """
        self.logger.debug(f"Mapping {len(jira_issues)} Jira issues to external tasks")
        return [self.jira_to_external_task(issue) for issue in jira_issues]
    
    def update_custom_field_mappings(self, mappings: Dict[str, str]) -> None:
        """
        Update custom field mappings.
        
        Args:
            mappings: Dictionary mapping ADHD Calendar task fields to Jira custom fields
        """
        self.custom_field_mapper.update_mappings(mappings)
    
    def get_custom_field_mappings(self) -> Dict[str, str]:
        """
        Get the current custom field mappings.
        
        Returns:
            Dictionary of custom field mappings
        """
        return self.custom_field_mapper.get_mappings() 