# Jira Integration Components

This directory contains the refactored Jira integration components for the ADHD Calendar application.

## Architecture Overview

The Jira integration has been refactored using a component-based architecture to reduce complexity and improve maintainability. The main components are:

1. **JiraIntegration** - Main integration class that implements the `ProjectToolIntegration` interface
2. **JiraAuthenticator** - Handles authentication with Jira APIs
3. **JiraTaskMapper** - Maps between Jira issues and ADHD Calendar tasks
4. **JiraQueryBuilder** - Builds JQL (Jira Query Language) queries
5. **JiraApiClient** - Basic client for making requests to the Jira API
6. **ResilientJiraApiClient** - Enhanced client with retry and circuit breaker patterns
7. **JiraErrorHandler** - Specialized error handling for Jira API interactions

## Component Relationships

```
┌───────────────────┐
│  JiraIntegration  │
└─────────┬─────────┘
          │
          │ uses
          ▼
┌─────────────────────┐     ┌───────────────────┐
│ ResilientJiraApiClient│────▶ JiraErrorHandler │
└──────────┬──────────┘     └───────────────────┘
           │
           │ extends
           ▼
┌───────────────────┐     ┌─────────────────┐     ┌───────────────────┐
│   JiraApiClient   │────▶│JiraAuthenticator│     │  JiraTaskMapper   │
└──────────┬────────┘     └─────────────────┘     └──────────┬────────┘
           │                                                  │
           │ uses                                             │ uses
           ▼                                                  ▼
┌───────────────────┐                           ┌───────────────────────┐
│ JiraQueryBuilder  │─────────────────────────▶│   JiraFieldMappers    │
└───────────────────┘                           └───────────────────────┘
```

## Key Improvements

1. **Reduced Nested Depth**: The original implementation had nested depths up to 14, which has been reduced to a maximum of 3-4 levels.

2. **Improved Error Handling**: Implemented specialized error handling with error categorization and detailed logging.

3. **Resilience Patterns**: Added retry mechanism with exponential backoff and circuit breaker pattern to prevent cascading failures.

4. **Separation of Concerns**: Each component has a single responsibility, making the code more maintainable.

5. **Improved Testability**: Components can be tested in isolation with mocks.

## Additional Refactoring Improvements

The integration components have been further improved in a subsequent refactoring effort:

1. **Enhanced Field Mapping**: Moved field mapping logic to specialized mapper classes (StatusMapper, PriorityMapper, DateFormatter, etc.)

2. **Reduced Class Size**: Split large classes into smaller, more cohesive components:
   - `JiraTaskMapper` now uses specialized field mappers
   - `JiraAuthenticator` has streamlined authentication logic
   - `JiraErrorHandler` uses a more declarative approach for error classification

3. **Declarative Patterns**: Replaced complex conditional logic with more declarative patterns:
   - Dictionary-based mappings
   - Function mapping strategy patterns
   - Specialized helper classes

4. **Reduced Cyclomatic Complexity**:
   - Simplified complex methods by extracting specialized helper methods
   - Reduced deeply nested conditionals
   - Improved error handling logic

5. **Improved Token Management**: Added more sophisticated token management in the authenticator:
   - Token refresh handling
   - Better error processing for auth-related issues
   - Enhanced status reporting

## Usage Example

```python
# Create a Jira integration with project configuration
integration = JiraIntegration(config)

# Authenticate with Jira
authenticated = await integration.authenticate()

# Fetch tasks from Jira
tasks = await integration.fetch_tasks()

# Create a new task in Jira
task_data = {
    "title": "New Task",
    "description": "This is a new task",
    "status": "not_started",
    "priority": "high"
}
created_task = await integration.create_task(task_data)

# Update an existing task
updated_task = await integration.update_task("PROJ-123", task_data)

# Delete a task
success = await integration.delete_task("PROJ-123")
```

## Health Monitoring

The `ResilientJiraApiClient` provides health metrics through the `get_health_metrics()` method, which returns information about:

- Circuit breaker status
- API call rate
- Error statistics by category

This can be useful for monitoring the integration's health and diagnosing issues.

## Field Mappers

The field mapper components handle conversion between Jira and ADHD Calendar data formats:

1. **StatusMapper**: Maps between Jira issue statuses and `ExternalTaskStatus` enum values
2. **PriorityMapper**: Maps between Jira priorities and `ExternalTaskPriority` enum values  
3. **DateFormatter**: Handles date format conversions between systems
4. **FieldExtractor**: Extracts and formats fields from Jira issues
5. **CustomFieldMapper**: Manages mappings for custom fields

Example:
```python
# Map Jira status to ExternalTaskStatus
status = StatusMapper.jira_to_external("In Progress")  # Returns ExternalTaskStatus.IN_PROGRESS

# Convert date format
date = DateFormatter.parse_jira_date("2023-05-15T10:30:45.000+0000")

# Extract fields from Jira issue
assignee = FieldExtractor.extract_assignee(issue_fields)
```

## Future Improvements

1. **Enhanced Rate Limiting**: Implement more sophisticated rate limiting based on Jira API response headers.
2. **Caching**: Add caching for frequently accessed data like projects and issue types.
3. **Webhook Support**: Add support for Jira webhooks to receive real-time updates.
4. **Transition Support**: Improve status transition handling using Jira's transition API.
5. **Metrics Collection**: Add more detailed metrics collection for performance monitoring.

## Testing

Each component has a corresponding test file in the `tests` directory. Run the tests using pytest:

```bash
pytest app/ui/integrations/tests/
``` 