# Integration Components Refactoring Plan - Part 2: Sync Service (continued)

## Phase 3: Creating Centralized Error Handler (1 day)

### 3.1 Create `SyncErrorHandler` Class

```python
class SyncErrorHandler:
    """Centralized error handling for sync operations."""
    
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
    
    def handle_sync_error(self, exception, result, message):
        """Handle and log a sync operation error."""
        error_msg = f"{message}: {str(exception)}"
        self.logger.error(error_msg)
        result.errors.append(error_msg)
        
        # Add stack trace for debugging in development
        self.logger.debug(f"Stack trace: {traceback.format_exc()}")
        
        # Categorize errors for better reporting
        self._categorize_error(exception, result)
        
        return error_msg
    
    def _categorize_error(self, exception, result):
        """Categorize errors for better tracking and reporting."""
        if isinstance(exception, ConnectionError):
            result.details.setdefault("error_categories", {}).setdefault("connection", 0)
            result.details["error_categories"]["connection"] += 1
        elif isinstance(exception, TimeoutError):
            result.details.setdefault("error_categories", {}).setdefault("timeout", 0)
            result.details["error_categories"]["timeout"] += 1
        elif isinstance(exception, ValueError):
            result.details.setdefault("error_categories", {}).setdefault("validation", 0)
            result.details["error_categories"]["validation"] += 1
        else:
            result.details.setdefault("error_categories", {}).setdefault("other", 0)
            result.details["error_categories"]["other"] += 1
```

## Phase 4: Refactoring Main Sync Functions (2 days)

### 4.1 Create `SyncService` Class

```python
class SyncService:
    """Service for handling synchronization between ADHD Calendar and external tools."""
    
    def __init__(self):
        self.import_handler = TaskImportHandler()
        self.export_handler = TaskExportHandler()
        self.error_handler = SyncErrorHandler()
    
    async def sync_tasks(self, user_id: str, integration: ProjectToolIntegration) -> SyncResult:
        """
        Synchronize tasks between ADHD Calendar and an external tool.
        
        Args:
            user_id: User ID
            integration: Integration instance for the external tool
            
        Returns:
            SyncResult containing the results of the sync operation
        """
        result = SyncResult(
            success=True,
            tool_type=integration.config.tool_type
        )
        
        if not await self._verify_connection(integration, result):
            return result
        
        try:
            # Process based on sync direction
            await self._process_by_sync_direction(user_id, integration, result)
            
            # Update last sync time
            integration.config.last_sync = datetime.utcnow()
            logging.info(f"Completed sync for {integration.name} for user {user_id}")
            
        except Exception as e:
            self.error_handler.handle_sync_error(e, result, f"Unexpected error during sync for {integration.name}")
            result.success = False
        
        return result
    
    async def _verify_connection(self, integration, result):
        """Verify the connection to the external service."""
        try:
            if not await integration.test_connection():
                result.success = False
                result.errors.append("Failed to connect to the external service")
                return False
            return True
        except Exception as e:
            self.error_handler.handle_sync_error(e, result, "Connection test failed")
            result.success = False
            return False
    
    async def _process_by_sync_direction(self, user_id, integration, result):
        """Process sync based on the configured direction."""
        sync_direction = integration.config.sync_direction
        
        if sync_direction in [SyncDirection.IMPORT, SyncDirection.BIDIRECTIONAL]:
            await self.import_handler.import_tasks(user_id, integration, result)
        
        if sync_direction in [SyncDirection.EXPORT, SyncDirection.BIDIRECTIONAL]:
            await self.export_handler.export_tasks(user_id, integration, result)
```

### 4.2 Refactor Public Functions to Use New Service

```python
# Simple facade functions for backwards compatibility
async def import_tasks(user_id: str, integration: ProjectToolIntegration, result: SyncResult) -> None:
    """Import tasks from external tool to ADHD Calendar."""
    handler = TaskImportHandler()
    await handler.import_tasks(user_id, integration, result)

async def export_tasks(user_id: str, integration: ProjectToolIntegration, result: SyncResult) -> None:
    """Export tasks from ADHD Calendar to external tool."""
    handler = TaskExportHandler()
    await handler.export_tasks(user_id, integration, result)

async def sync_tasks(user_id: str, integration: ProjectToolIntegration) -> SyncResult:
    """Synchronize tasks between ADHD Calendar and an external tool."""
    service = SyncService()
    return await service.sync_tasks(user_id, integration)
```

## Phase 5: Implementing Functional Enhancements (1 day)

### 5.1 Improve Task Matching with Functional Approach

```python
def find_tasks_to_import(external_tasks, existing_tasks):
    """Find tasks that need to be imported (not in our system yet)."""
    existing_ids = {task.get("external_id") for task in existing_tasks}
    return list(filter(lambda task: task.external_id not in existing_ids, external_tasks))

def find_tasks_to_update(external_tasks, existing_tasks):
    """Find tasks that need to be updated (already in our system but changed)."""
    # Create a lookup dictionary for faster matching
    existing_dict = {task.get("external_id"): task for task in existing_tasks if task.get("external_id")}
    
    # Use list comprehension for cleaner filtering
    return [
        (existing_dict[ext_task.external_id], ext_task)
        for ext_task in external_tasks
        if ext_task.external_id in existing_dict
        and existing_dict[ext_task.external_id].get("updated_date") < ext_task.updated_date
    ]
```

### 5.2 Add Batch Processing for Better Performance

```python
async def process_batch(tasks, process_func, *args, batch_size=10):
    """Process tasks in batches for better performance."""
    for i in range(0, len(tasks), batch_size):
        batch = tasks[i:i+batch_size]
        await asyncio.gather(*[process_func(task, *args) for task in batch])
```

## Phase 6: Testing and Validation (1 day)

### 6.1 Unit Testing
- Test each handler class independently
- Test error handling with mock exceptions
- Verify task identification logic

### 6.2 Integration Testing
- Test end-to-end sync process
- Verify correct behavior for different sync directions
- Test different error scenarios

## Phase 7: Documentation and Cleanup (1 day)

### 7.1 Update Documentation
- Document the new class structure
- Create sequence diagrams for the sync process
- Document error handling patterns

### 7.2 Cleanup
- Remove duplicated code
- Ensure consistent error handling
- Verify logging consistency

## Implementation Timeline

- Days 1-2: Preparation and test creation
- Days 3-4: Implement handler classes 
- Day 5: Implement error handler
- Days 6-7: Refactor main sync functions
- Day 8: Functional enhancements
- Day 9: Testing and validation
- Day 10: Documentation and cleanup 