"""
Sync Task Manager Module

This module provides a dedicated manager for handling synchronization operations
between ADHD Calendar and external project management tools.
"""

import logging
from typing import Dict, List, Any, Tuple, Optional, Set

from app.ui.project_management_integration import (
    ProjectToolIntegration,
    SyncResult,
    ExternalTask,
)


class SyncTaskManager:
    """
    Manages synchronization of tasks between ADHD Calendar and external tools.

    Provides methods for importing tasks from external tools and exporting tasks
    to external tools with improved error handling and logging.
    """

    def __init__(self):
        """Initialize the SyncTaskManager."""
        self.logger = logging.getLogger(__name__)

    async def import_tasks(
        self, user_id: str, integration: ProjectToolIntegration, result: SyncResult
    ) -> None:
        """
        Import tasks from external tool to ADHD Calendar.

        Args:
            user_id: User ID
            integration: Integration instance for the external tool
            result: SyncResult object to update with results
        """
        try:
            # Fetch tasks from external tool
            external_tasks = await integration.fetch_tasks()

            # In a real implementation, we would get existing tasks from the database
            # existing_tasks = await self._get_existing_tasks(user_id, integration.config.tool_type)
            existing_tasks = []  # Mock empty list for this example

            # Identify tasks to import and update
            tasks_to_import, tasks_to_update = self._identify_import_tasks(
                external_tasks, existing_tasks
            )

            # Process imports
            await self._process_imports(tasks_to_import, user_id, integration, result)

            # Process updates
            await self._process_import_updates(tasks_to_update, user_id, integration, result)

        except Exception as e:
            error_msg = f"Error during import from {integration.name}: {str(e)}"
            self.logger.error(error_msg)
            result.errors.append(error_msg)

    async def export_tasks(
        self, user_id: str, integration: ProjectToolIntegration, result: SyncResult
    ) -> None:
        """
        Export tasks from ADHD Calendar to external tool.

        Args:
            user_id: User ID
            integration: Integration instance for the external tool
            result: SyncResult object to update with results
        """
        try:
            # In a real implementation, we would get local tasks from the database
            # local_tasks = await self._get_local_tasks_for_export(user_id, integration.config)
            local_tasks = []  # Mock empty list for this example

            # Fetch existing tasks from external tool for comparison
            external_tasks = await integration.fetch_tasks()

            # Identify tasks to export and update
            tasks_to_export, tasks_to_update = self._identify_export_tasks(
                local_tasks, external_tasks
            )

            # Process exports
            await self._process_exports(tasks_to_export, user_id, integration, result)

            # Process updates
            await self._process_export_updates(tasks_to_update, user_id, integration, result)

        except Exception as e:
            error_msg = f"Error during export to {integration.name}: {str(e)}"
            self.logger.error(error_msg)
            result.errors.append(error_msg)

    def _identify_import_tasks(
        self, external_tasks: List[ExternalTask], existing_tasks: List[Dict[str, Any]]
    ) -> Tuple[List[ExternalTask], List[Tuple[Dict[str, Any], ExternalTask]]]:
        """
        Identify tasks to import and update during import process.

        Args:
            external_tasks: List of tasks from external tool
            existing_tasks: List of existing tasks in ADHD Calendar

        Returns:
            Tuple containing (tasks_to_import, tasks_to_update)
        """
        tasks_to_import = []
        tasks_to_update = []

        # Create a map for quicker lookup
        existing_task_map = {t.get("external_id"): t for t in existing_tasks}

        for ext_task in external_tasks:
            if ext_task.external_id not in existing_task_map:
                # Task doesn't exist locally, so import it
                tasks_to_import.append(ext_task)
            else:
                # Task exists, check if it needs updating
                local_task = existing_task_map[ext_task.external_id]
                if local_task.get("updated_date") < ext_task.updated_at:
                    tasks_to_update.append((local_task, ext_task))

        return tasks_to_import, tasks_to_update

    def _identify_export_tasks(
        self, local_tasks: List[Dict[str, Any]], external_tasks: List[ExternalTask]
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Identify tasks to export and update during export process.

        Args:
            local_tasks: List of tasks from ADHD Calendar
            external_tasks: List of existing tasks in external tool

        Returns:
            Tuple containing (tasks_to_export, tasks_to_update)
        """
        tasks_to_export = []
        tasks_to_update = []

        # Create a map for quicker lookup and extract external IDs
        external_id_to_task = {t.external_id: t for t in external_tasks}

        for task in local_tasks:
            external_id = task.get("external_id")
            if not external_id or external_id not in external_id_to_task:
                # Task doesn't exist externally, so export it
                tasks_to_export.append(task)
            else:
                # Task exists, check if it needs updating
                ext_task = external_id_to_task[external_id]
                if task.get("updated_date") > ext_task.updated_at:
                    tasks_to_update.append(task)

        return tasks_to_export, tasks_to_update

    async def _process_imports(
        self, tasks: List[ExternalTask], user_id: str,
        integration: ProjectToolIntegration, result: SyncResult
    ) -> None:
        """
        Process task imports.

        Args:
            tasks: List of tasks to import
            user_id: User ID
            integration: Integration instance
            result: SyncResult to update
        """
        for ext_task in tasks:
            try:
                # In a real implementation, we would save to database
                # await self._create_local_task(user_id, ext_task)
                result.tasks_imported += 1
                self.logger.info(f"Imported task {ext_task.external_id} from {integration.name}")
            except Exception as e:
                self._handle_task_error(
                    f"Error importing task {ext_task.external_id}: {str(e)}",
                    result
                )

    async def _process_import_updates(
        self, task_pairs: List[Tuple[Dict[str, Any], ExternalTask]],
        user_id: str, integration: ProjectToolIntegration, result: SyncResult
    ) -> None:
        """
        Process task updates during import.

        Args:
            task_pairs: List of (local_task, external_task) pairs
            user_id: User ID
            integration: Integration instance
            result: SyncResult to update
        """
        for local_task, ext_task in task_pairs:
            try:
                # In a real implementation, we would update in database
                # await self._update_local_task(local_task["id"], ext_task)
                result.tasks_updated += 1
                self.logger.info(f"Updated task {ext_task.external_id} from {integration.name}")
            except Exception as e:
                self._handle_task_error(
                    f"Error updating task {ext_task.external_id}: {str(e)}",
                    result
                )

    async def _process_exports(
        self, tasks: List[Dict[str, Any]], user_id: str,
        integration: ProjectToolIntegration, result: SyncResult
    ) -> None:
        """
        Process task exports.

        Args:
            tasks: List of tasks to export
            user_id: User ID
            integration: Integration instance
            result: SyncResult to update
        """
        for task in tasks:
            try:
                # In a real implementation, we would create in external system
                # ext_task = await integration.create_task(task)
                # await self._update_local_task_external_id(task["id"], ext_task.external_id)
                result.tasks_exported += 1
                self.logger.info(f"Exported task {task.get('id')} to {integration.name}")
            except Exception as e:
                self._handle_task_error(
                    f"Error exporting task {task.get('id')}: {str(e)}",
                    result
                )

    async def _process_export_updates(
        self, tasks: List[Dict[str, Any]], user_id: str,
        integration: ProjectToolIntegration, result: SyncResult
    ) -> None:
        """
        Process task updates during export.

        Args:
            tasks: List of tasks to update
            user_id: User ID
            integration: Integration instance
            result: SyncResult to update
        """
        for task in tasks:
            try:
                # In a real implementation, we would update in external system
                # await integration.update_task(task["external_id"], task)
                result.tasks_updated += 1
                self.logger.info(f"Updated task {task.get('id')} in {integration.name}")
            except Exception as e:
                self._handle_task_error(
                    f"Error updating external task {task.get('external_id')}: {str(e)}",
                    result
                )

    def _handle_task_error(self, error_msg: str, result: SyncResult) -> None:
        """
        Handle task processing error.

        Args:
            error_msg: Error message
            result: SyncResult to update
        """
        self.logger.error(error_msg)
        result.errors.append(error_msg)
