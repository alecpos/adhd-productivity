# Integration Components Refactoring Plan - Part 1: Sync Service

## Current Issues in `app/ui/services/sync_service.py`

- High nested depth (12)
- Complex error handling
- Duplicated code between import and export functions
- Limited separation of concerns
- High cyclomatic complexity (14.0)

## Refactoring Goals

1. Reduce cyclomatic complexity by at least 40%
2. Limit maximum nesting depth to 3-4 levels
3. Eliminate code duplication
4. Improve error handling
5. Maintain all existing functionality

## Phase 1: Preparation (2 days)

### 1.1 Create Comprehensive Test Suite
- Develop unit tests for `import_tasks` and `export_tasks` functions
- Create mock integration objects for testing
- Test error handling scenarios

### 1.2 Set Up Metrics Tracking
- Establish baseline complexity metrics
- Document current error handling patterns

## Phase 2: Class Extraction (2 days)

### 2.1 Create `TaskImportHandler` Class
```python
class TaskImportHandler:
    """Handles the import of tasks from external tools."""

    async def import_tasks(self, user_id: str, integration: ProjectToolIntegration, result: SyncResult) -> None:
        """Import tasks from external tool to ADHD Calendar."""
        try:
            external_tasks = await integration.fetch_tasks()
            existing_tasks = await self._get_existing_tasks(user_id, integration.config.tool_type)

            tasks_to_import = self._find_tasks_to_import(external_tasks, existing_tasks)
            tasks_to_update = self._find_tasks_to_update(external_tasks, existing_tasks)

            await self._process_new_tasks(user_id, tasks_to_import, integration, result)
            await self._process_updated_tasks(user_id, tasks_to_update, integration, result)

        except Exception as e:
            self._handle_error(e, result, f"Error in import process for {integration.name}")

    def _find_tasks_to_import(self, external_tasks, existing_tasks):
        """Find tasks that need to be imported (not in our system yet)."""
        existing_ids = {task.get("external_id") for task in existing_tasks}
        return [task for task in external_tasks if task.external_id not in existing_ids]

    def _find_tasks_to_update(self, external_tasks, existing_tasks):
        """Find tasks that need to be updated (already in our system but changed)."""
        update_pairs = []

        # Create a lookup dictionary for faster matching
        existing_dict = {task.get("external_id"): task for task in existing_tasks}

        for ext_task in external_tasks:
            if ext_task.external_id in existing_dict:
                local_task = existing_dict[ext_task.external_id]
                if local_task.get("updated_date") < ext_task.updated_date:
                    update_pairs.append((local_task, ext_task))

        return update_pairs

    async def _process_new_tasks(self, user_id, tasks_to_import, integration, result):
        """Process and save new tasks to import."""
        for ext_task in tasks_to_import:
            try:
                # await create_local_task(user_id, ext_task)
                result.tasks_imported += 1
                logging.info(f"Imported task {ext_task.external_id} from {integration.name}")
            except Exception as e:
                self._handle_error(e, result, f"Error importing task {ext_task.external_id}")

    async def _process_updated_tasks(self, user_id, tasks_to_update, integration, result):
        """Process and update existing tasks."""
        for local_task, ext_task in tasks_to_update:
            try:
                # await update_local_task(local_task["id"], ext_task)
                result.tasks_updated += 1
                logging.info(f"Updated task {ext_task.external_id} from {integration.name}")
            except Exception as e:
                self._handle_error(e, result, f"Error updating task {ext_task.external_id}")

    async def _get_existing_tasks(self, user_id, tool_type):
        """Get existing tasks from the database for comparison."""
        # In a real implementation, we would get existing tasks from the database
        # return await get_existing_tasks(user_id, tool_type)
        return []  # Mock empty list for this example

    def _handle_error(self, exception, result, message):
        """Handle and log errors during the import process."""
        error_msg = f"{message}: {str(exception)}"
        logging.error(error_msg)
        result.errors.append(error_msg)
```

### 2.2 Create `TaskExportHandler` Class
```python
class TaskExportHandler:
    """Handles the export of tasks to external tools."""

    async def export_tasks(self, user_id: str, integration: ProjectToolIntegration, result: SyncResult) -> None:
        """Export tasks from ADHD Calendar to external tool."""
        try:
            local_tasks = await self._get_local_tasks(user_id, integration.config)
            external_tasks = await integration.fetch_tasks()

            tasks_to_export = self._find_tasks_to_export(local_tasks, external_tasks)
            tasks_to_update = self._find_tasks_to_update(local_tasks, external_tasks)

            await self._process_new_exports(tasks_to_export, integration, result)
            await self._process_external_updates(tasks_to_update, integration, result)

        except Exception as e:
            self._handle_error(e, result, f"Error in export process for {integration.name}")

    def _find_tasks_to_export(self, local_tasks, external_tasks):
        """Find tasks that need to be exported (not in external system yet)."""
        external_ids = {task.external_id for task in external_tasks}
        return [
            task for task in local_tasks
            if not task.get("external_id") or task.get("external_id") not in external_ids
        ]

    def _find_tasks_to_update(self, local_tasks, external_tasks):
        """Find tasks that need to be updated in the external system."""
        # Create external task lookup dictionary
        external_dict = {task.external_id: task for task in external_tasks}

        return [
            task for task in local_tasks
            if task.get("external_id") and task.get("external_id") in external_dict
            and task.get("updated_date") > external_dict[task.get("external_id")].updated_date
        ]

    async def _process_new_exports(self, tasks_to_export, integration, result):
        """Process and create new tasks in the external system."""
        for task in tasks_to_export:
            try:
                # ext_task = await integration.create_task(task)
                # await update_local_task_external_id(task["id"], ext_task.external_id)
                result.tasks_exported += 1
                logging.info(f"Exported task {task.get('id')} to {integration.name}")
            except Exception as e:
                self._handle_error(e, result, f"Error exporting task {task.get('id')}")

    async def _process_external_updates(self, tasks_to_update, integration, result):
        """Process and update tasks in the external system."""
        for task in tasks_to_update:
            try:
                # await integration.update_task(task["external_id"], task)
                result.tasks_updated += 1
                logging.info(f"Updated task {task.get('id')} in {integration.name}")
            except Exception as e:
                self._handle_error(e, result, f"Error updating external task {task.get('external_id')}")

    async def _get_local_tasks(self, user_id, integration_config):
        """Get local tasks from the database for export."""
        # In a real implementation, we would get local tasks from the database
        # return await get_local_tasks_for_export(user_id, integration_config)
        return []  # Mock empty list for this example

    def _handle_error(self, exception, result, message):
        """Handle and log errors during the export process."""
        error_msg = f"{message}: {str(exception)}"
        logging.error(error_msg)
        result.errors.append(error_msg)
```
