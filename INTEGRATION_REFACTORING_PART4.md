# Integration Components Refactoring Plan - Part 4: Jira Integration (continued)

## Phase 3: Refactoring the Main Integration Class (2 days)

### 3.1 Refactor `JiraIntegration` Class

```python
class JiraIntegration(ProjectToolIntegration):
    """Integration with Atlassian Jira."""
    
    def __init__(self, config: ProjectToolConfig):
        super().__init__(config)
        self.authenticator = JiraAuthenticator(config)
        self.api_client = JiraApiClient(config, self.authenticator)
        self.query_builder = JiraQueryBuilder()
        self.task_mapper = JiraTaskMapper()
    
    async def authenticate(self) -> bool:
        """Authenticate with Jira using the provided credentials."""
        return await self.authenticator.authenticate()
    
    async def fetch_tasks(self) -> List[ExternalTask]:
        """Fetch issues from Jira."""
        try:
            # Build JQL query
            jql = self.query_builder.build_jql_query(self.config)
            
            # Fetch issues using API client
            issues = await self.api_client.get_issues(jql)
            
            # Map to external tasks
            return [self.task_mapper.jira_to_external_task(issue) for issue in issues]
            
        except Exception as e:
            self._handle_error("Error fetching Jira tasks", e)
            return []
    
    async def create_task(self, task: Dict[str, Any]) -> ExternalTask:
        """Create a new issue in Jira."""
        try:
            # Convert to Jira format
            issue_data = self.task_mapper.internal_to_jira_issue(task)
            
            # Create using API client
            result = await self.api_client.create_issue(issue_data)
            
            # Create external task from result
            return self._create_external_task_from_result(result, task)
            
        except Exception as e:
            self._handle_error("Error creating Jira task", e)
            raise
    
    async def update_task(self, external_id: str, task_data: Dict[str, Any]) -> ExternalTask:
        """Update an existing issue in Jira."""
        try:
            # Convert to Jira format
            issue_data = self.task_mapper.internal_to_jira_issue(task_data)
            
            # Update using API client
            result = await self.api_client.update_issue(external_id, issue_data)
            
            # Create external task from result
            return self._create_external_task_from_result(result, task_data)
            
        except Exception as e:
            self._handle_error("Error updating Jira task", e)
            raise
    
    async def delete_task(self, external_id: str) -> bool:
        """Delete a task in Jira."""
        try:
            return await self.api_client.delete_issue(external_id)
        except Exception as e:
            self._handle_error("Error deleting Jira task", e)
            raise
    
    async def get_projects(self) -> List[Dict[str, Any]]:
        """Get available projects from Jira."""
        try:
            return await self.api_client.get_projects()
        except Exception as e:
            self._handle_error("Error fetching Jira projects", e)
            return []
    
    def _create_external_task_from_result(self, result: Dict[str, Any], task_data: Dict[str, Any]) -> ExternalTask:
        """Create an ExternalTask from Jira API result and task data."""
        return ExternalTask(
            external_id=result["key"],
            title=task_data["title"],
            description=task_data.get("description"),
            status=task_data.get("status", "not_started"),
            due_date=task_data.get("due_date"),
            created_date=datetime.utcnow(),
            updated_date=datetime.utcnow(),
            priority=task_data.get("priority"),
            labels=task_data.get("labels", []),
            project_id=task_data.get("project_key", self.config.project_ids[0] if self.config.project_ids else None),
            url=f"{self.config.api_url}/browse/{result['key']}",
            tool_type=ProjectToolType.JIRA,
            additional_data={"key": result["key"]}
        )
    
    def _handle_error(self, message: str, exception: Exception) -> None:
        """Handle error in Jira integration."""
        error_msg = f"{message}: {str(exception)}"
        logging.error(error_msg)
        if hasattr(exception, "__traceback__"):
            logging.debug(f"Stack trace: {traceback.format_exception(type(exception), exception, exception.__traceback__)}")
```

## Phase 4: Error Handling and Resilience (1 day)

### 4.1 Create `JiraErrorHandler` Class

```python
class JiraErrorHandler:
    """Specialized error handling for Jira API interactions."""
    
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
    
    def handle_error(self, message: str, exception: Exception, reraise: bool = False) -> None:
        """Handle Jira API errors with proper logging and classification."""
        error_msg = f"{message}: {str(exception)}"
        self.logger.error(error_msg)
        
        # Log detailed stack trace in debug mode
        self.logger.debug(f"Stack trace: {traceback.format_exc()}")
        
        # Classify errors
        if isinstance(exception, aiohttp.ClientResponseError):
            self._handle_response_error(exception)
        elif isinstance(exception, aiohttp.ClientConnectionError):
            self._handle_connection_error(exception)
        elif isinstance(exception, aiohttp.ClientTimeout):
            self._handle_timeout_error(exception)
        elif isinstance(exception, json.JSONDecodeError):
            self._handle_json_error(exception)
        else:
            self._handle_generic_error(exception)
        
        if reraise:
            raise exception
    
    def _handle_response_error(self, exception: aiohttp.ClientResponseError) -> None:
        """Handle HTTP response errors."""
        status = exception.status
        if status == 401:
            self.logger.error("Authentication failed. Please check credentials.")
        elif status == 403:
            self.logger.error("Permission denied. User lacks necessary permissions.")
        elif status == 404:
            self.logger.error("Resource not found. Please check IDs and paths.")
        elif status == 429:
            self.logger.error("Rate limit exceeded. Implement backoff and retry logic.")
        elif status >= 500:
            self.logger.error("Jira server error. Please try again later.")
    
    def _handle_connection_error(self, exception: aiohttp.ClientConnectionError) -> None:
        """Handle connection errors."""
        self.logger.error("Connection error. Please check network and Jira server status.")
    
    def _handle_timeout_error(self, exception: aiohttp.ClientTimeout) -> None:
        """Handle timeout errors."""
        self.logger.error("Request timed out. Jira server might be overloaded.")
    
    def _handle_json_error(self, exception: json.JSONDecodeError) -> None:
        """Handle JSON parsing errors."""
        self.logger.error(f"Invalid JSON response: {str(exception)}")
    
    def _handle_generic_error(self, exception: Exception) -> None:
        """Handle other types of errors."""
        self.logger.error(f"Unexpected error: {str(exception)}")
```

## Phase 5: Enhanced API Client with Resilience (1 day)

### 5.1 Create Resilient API Client

```python
class ResilientJiraApiClient(JiraApiClient):
    """Jira API client with retry and circuit breaker patterns."""
    
    def __init__(self, config: ProjectToolConfig, authenticator: JiraAuthenticator):
        super().__init__(config, authenticator)
        self.error_handler = JiraErrorHandler()
        self.retry_count = 3
        self.backoff_factor = 1.5
        self.circuit_breaker_failures = 0
        self.circuit_breaker_threshold = 5
        self.circuit_open_until = None
    
    async def _make_request(self, url, method="GET", params=None, headers=None, json=None):
        """Make HTTP request to Jira API with retry and circuit breaker patterns."""
        # Check if circuit breaker is open
        if self._is_circuit_open():
            raise Exception("Circuit breaker open, Jira API temporarily disabled")
        
        # Try the request with exponential backoff
        attempt = 0
        last_exception = None
        
        while attempt < self.retry_count:
            try:
                # In real implementation:
                # async with aiohttp.ClientSession() as session:
                #     async with session.request(method, url, params=params, headers=headers, json=json) as response:
                #         response.raise_for_status()
                #         if method != "DELETE":
                #             return await response.json()
                #         return True
                
                # Reset circuit breaker counter on success
                self.circuit_breaker_failures = 0
                return {}  # Mock response for this example
                
            except aiohttp.ClientResponseError as e:
                # Don't retry for 4xx errors except 429 (rate limit)
                if e.status >= 400 and e.status < 500 and e.status != 429:
                    self._increment_circuit_breaker()
                    self.error_handler.handle_error(f"HTTP error {e.status}", e, reraise=False)
                    raise
                
                last_exception = e
                
            except (aiohttp.ClientConnectionError, aiohttp.ClientTimeout) as e:
                last_exception = e
                self._increment_circuit_breaker()
                
            # Exponential backoff
            await asyncio.sleep(self.backoff_factor ** attempt)
            attempt += 1
        
        # If we got here, all retries failed
        self.error_handler.handle_error("All retries failed", last_exception, reraise=True)
    
    def _is_circuit_open(self):
        """Check if circuit breaker is open."""
        if self.circuit_open_until and datetime.utcnow() < self.circuit_open_until:
            return True
        # Reset if the circuit was open but now the timeout has passed
        if self.circuit_open_until:
            self.circuit_open_until = None
            self.circuit_breaker_failures = 0
        return False
    
    def _increment_circuit_breaker(self):
        """Increment the circuit breaker failure counter and open if threshold exceeded."""
        self.circuit_breaker_failures += 1
        if self.circuit_breaker_failures >= self.circuit_breaker_threshold:
            # Open the circuit for 1 minute
            self.circuit_open_until = datetime.utcnow() + timedelta(minutes=1)
            logging.warning("Circuit breaker opened for Jira API due to repeated failures")
```

## Phase 6: Integration and Testing (2 days)

### 6.1 Unit Testing 
- Test each component in isolation
- Create comprehensive mocks for Jira API responses
- Test error handling pathways

### 6.2 Integration Testing
- Test the entire integration end-to-end
- Verify proper data mapping between systems
- Test rate limiting and error recovery

## Phase 7: Documentation and Cleanup (1 day)

### 7.1 Update Documentation
- Create architectural diagrams showing components 
- Document error handling strategies
- Document mapping rules between systems

### 7.2 Code Cleanup
- Remove redundant code
- Ensure consistent error handling
- Add comprehensive docstrings

## Implementation Timeline

- Days 1-2: Preparation and test creation
- Days 3-5: Component extraction
- Days 6-7: Refactor main integration class
- Day 8: Enhance error handling
- Day 9: Implement resilient API client
- Days 10-11: Integration and testing
- Day 12: Documentation and cleanup 