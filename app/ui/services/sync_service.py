"""
Sync Service Module

This module provides synchronization services for project management tool integrations,
handling the import and export of tasks between ADHD Calendar and external tools.
"""

import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

from app.ui.project_management_integration import (
    ProjectToolIntegration,
    SyncResult,
    ExternalTask,
)
from app.ui.services.sync_task_manager import SyncTaskManager


class SyncService:
    """
    Service for synchronizing tasks between ADHD Calendar and external project management tools.

    Provides high-level methods for performing sync operations, handling errors,
    and maintaining statistics.
    """

    def __init__(self):
        """Initialize the SyncService with its dependencies."""
        self.logger = logging.getLogger(__name__)
        self.task_manager = SyncTaskManager()

    async def sync_tasks(
        self, user_id: str, integration: ProjectToolIntegration,
        import_tasks: bool = True, export_tasks: bool = True
    ) -> SyncResult:
        """
        Synchronize tasks between ADHD Calendar and an external project management tool.

        Args:
            user_id: User ID to sync tasks for
            integration: Integration instance for the external tool
            import_tasks: Whether to import tasks from external tool
            export_tasks: Whether to export tasks to external tool

        Returns:
            SyncResult containing statistics and errors
        """
        # Initialize result
        result = SyncResult()
        result.start_time = datetime.now()

        try:
            self.logger.info(f"Starting sync for user {user_id} with {integration.name}")

            # Authenticate with the external tool
            authenticated = await integration.authenticate()
            if not authenticated:
                error_msg = f"Failed to authenticate with {integration.name}"
                self.logger.error(error_msg)
                result.errors.append(error_msg)
                return self._finalize_result(result)

            # Import tasks if enabled
            if import_tasks:
                await self._perform_import(user_id, integration, result)

            # Export tasks if enabled
            if export_tasks:
                await self._perform_export(user_id, integration, result)

        except Exception as e:
            error_msg = f"Error during sync operation: {str(e)}"
            self.logger.error(error_msg)
            result.errors.append(error_msg)

        return self._finalize_result(result)

    async def _perform_import(
        self, user_id: str, integration: ProjectToolIntegration, result: SyncResult
    ) -> None:
        """
        Perform task import operation.

        Args:
            user_id: User ID
            integration: Integration instance
            result: SyncResult to update
        """
        self.logger.info(f"Importing tasks from {integration.name} for user {user_id}")
        try:
            await self.task_manager.import_tasks(user_id, integration, result)
        except Exception as e:
            error_msg = f"Error during import operation: {str(e)}"
            self.logger.error(error_msg)
            result.errors.append(error_msg)

    async def _perform_export(
        self, user_id: str, integration: ProjectToolIntegration, result: SyncResult
    ) -> None:
        """
        Perform task export operation.

        Args:
            user_id: User ID
            integration: Integration instance
            result: SyncResult to update
        """
        self.logger.info(f"Exporting tasks to {integration.name} for user {user_id}")
        try:
            await self.task_manager.export_tasks(user_id, integration, result)
        except Exception as e:
            error_msg = f"Error during export operation: {str(e)}"
            self.logger.error(error_msg)
            result.errors.append(error_msg)

    def _finalize_result(self, result: SyncResult) -> SyncResult:
        """
        Finalize sync result by adding end time and logging stats.

        Args:
            result: SyncResult to finalize

        Returns:
            Finalized SyncResult
        """
        result.end_time = datetime.now()
        result.duration_seconds = (result.end_time - result.start_time).total_seconds()

        # Log statistics
        stats = (
            f"Sync completed in {result.duration_seconds:.2f}s. "
            f"Imported: {result.tasks_imported}, "
            f"Exported: {result.tasks_exported}, "
            f"Updated: {result.tasks_updated}, "
            f"Errors: {len(result.errors)}"
        )

        if result.errors:
            self.logger.warning(stats)
        else:
            self.logger.info(stats)

        return result


# Function interfaces for backward compatibility
async def import_tasks(
    user_id: str, integration: ProjectToolIntegration, result: SyncResult
) -> None:
    """
    Legacy function for importing tasks. Uses SyncService internally.

    Args:
        user_id: User ID
        integration: Integration instance for the external tool
        result: SyncResult object to update with results
    """
    service = SyncService()
    await service._perform_import(user_id, integration, result)


async def export_tasks(
    user_id: str, integration: ProjectToolIntegration, result: SyncResult
) -> None:
    """
    Legacy function for exporting tasks. Uses SyncService internally.

    Args:
        user_id: User ID
        integration: Integration instance for the external tool
        result: SyncResult object to update with results
    """
    service = SyncService()
    await service._perform_export(user_id, integration, result)
