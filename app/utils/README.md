# Utils Directory

This directory contains utility functions and helpers for the ADHD Calendar application.

## Overview

The utils directory provides reusable utility functions, helpers, and common tools that are used throughout the application. These utilities help maintain code consistency, reduce duplication, and simplify common operations.

## Utility Categories

### Date and Time Utilities

- **date_utils.py**: Date manipulation and formatting functions
- **timezone_utils.py**: Timezone handling and conversion utilities
- **duration_utils.py**: Duration calculation and formatting

### String and Text Utilities

- **text_utils.py**: Text processing and formatting functions
- **validation_utils.py**: String validation helpers
- **sanitization_utils.py**: Text sanitization for security

### Security Utilities

- **security_utils.py**: Security-related functions
- **password_utils.py**: Password hashing and verification
- **token_utils.py**: Token generation and validation

### Data Processing Utilities

- **json_utils.py**: JSON processing utilities
- **csv_utils.py**: CSV processing utilities
- **serialization_utils.py**: Data serialization helpers

### ML Utilities

- **ml_utils.py**: Common ML-related utility functions
- **preprocessing_utils.py**: Data preprocessing for ML models
- **evaluation_utils.py**: Model evaluation utilities

### HTTP Utilities

- **http_utils.py**: HTTP request/response utilities
- **pagination_utils.py**: Pagination helpers
- **request_utils.py**: Request handling utilities

## Usage Example

```python
from app.utils.date_utils import format_datetime, get_week_boundaries
from app.utils.pagination_utils import paginate_results

# Using date utilities
start_date, end_date = get_week_boundaries(date.today())
formatted_date = format_datetime(datetime.now(), format="short")

# Using pagination utilities
page = 1
page_size = 20
total_items = 100
paginated_data = paginate_results(
    items=all_items,
    page=page,
    page_size=page_size,
    total_items=total_items
)
```

## Decorator Functions

Utility decorators are provided for common patterns:

```python
from app.utils.decorators import cached, retry, log_execution_time

@cached(ttl=300)  # Cache results for 5 minutes
def expensive_operation(param1, param2):
    # ...implementation

@retry(max_attempts=3, backoff_factor=2)
def external_api_call():
    # ...implementation

@log_execution_time
def performance_sensitive_function():
    # ...implementation
```

## Testing Utilities

Testing helpers are available in `testing_utils.py`:

```python
from app.utils.testing_utils import create_test_user, MockResponse, TestClient

# Create a test user
test_user = create_test_user(is_admin=True)

# Mock HTTP responses
mock_response = MockResponse(status_code=200, json_data={"key": "value"})

# Use test client
with TestClient() as client:
    response = client.get("/api/endpoint")
```

## Development Guidelines

When creating utility functions:

1. Keep functions focused on a single responsibility
2. Document parameters and return values
3. Use descriptive names that indicate the function's purpose
4. Include type hints for better IDE support
5. Write unit tests for all utility functions
6. Consider error handling and edge cases

## Related Documentation

- [Utility Functions Guide](../../docs/utility_functions.md)
- [Date and Time Handling](../../docs/date_time_handling.md)
- [Security Best Practices](../../docs/security_best_practices.md)

# API Utilities

This directory contains utilities for implementing the API design guidelines and standardized error handling in the ADHD Calendar API.

## Overview

These utilities are designed to help developers create API endpoints that follow the API design guidelines and provide consistent error handling. They provide reusable functions and classes for common API tasks like:

- Standardized response formatting
- Error handling
- Validation
- Pagination
- Authentication and authorization

## Utilities

### API Response Utilities (`api_responses.py`)

Provides standardized response formatters for API endpoints.

**Key Features:**

- Consistent response format
- Pagination for collections
- Standardized error responses
- Helpers for common error types

**Example:**

```python
from app.utils.api_responses import create_collection_response, not_found_response

# Return a paginated collection
return create_collection_response(
    items=tasks,
    total=total_count,
    page=page,
    page_size=page_size
)

# Return a not found error
return not_found_response("Task", task_id)
```

### Route Utilities (`route_utils.py`)

Provides utilities for creating API routes that conform to the API design guidelines.

**Key Features:**

- Standardized error responses for route documentation
- Pagination parameters
- ID path parameters
- Resource access validation
- Error creation helpers

**Example:**

```python
from app.utils.route_utils import error_responses, pagination_params, id_path_param

@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    responses=error_responses(403, 404)
)
async def get_task(
    task_id: UUID = Depends(id_path_param("task")),
    pagination: Dict[str, int] = Depends(pagination_params),
    current_user: User = Depends(get_current_user)
):
    # Implementation
```

### Validation Utilities (`validation.py`)

Provides enhanced validation utilities for Pydantic models.

**Key Features:**

- Common validators (email, password, dates, numbers)
- Validator registry for reuse
- Dynamic validator addition to models
- Helpers for creating complex validators

**Example:**

```python
from app.utils.validation import BaseModelWithValidators, validate_dependent_fields

class UserCreate(BaseModelWithValidators):
    email: str
    password: str
    birth_date: Optional[datetime] = None
    phone_number: Optional[str] = None

    # Validators will be automatically added for:
    # - email (email format)
    # - password (strength)
    # - birth_date (past date)
    # - phone_number (format)

    # Additional custom validators can be added:
    _validate_dependent = validate_dependent_fields("birth_date", ["phone_number"])
```

## Using the Utilities in API Routes

The recommended way to implement API routes using these utilities is demonstrated in `app/routes/example_task_route.py`.

**Key Patterns:**

1. **Set up the router with consistent tags and responses:**

```python
router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"],
    responses=error_responses(401)  # Add default 401 response to all routes
)
```

2. **Define endpoints with response models and error responses:**

```python
@router.get(
    "/user/{user_id}",
    response_model=TaskListResponse,
    summary="Get User Tasks",
    description="Retrieve all tasks for a specific user",
    responses=error_responses(403, 404),
)
```

3. **Use dependency injection for common parameters:**

```python
async def get_user_tasks(
    user_id: UUID = Depends(id_path_param("user")),
    current_user: UserResponse = Depends(get_current_user),
    pagination: Dict[str, int] = Depends(pagination_params),
    # ...
)
```

4. **Document endpoints with consistent docstrings:**

```python
"""
Retrieve all tasks for a specific user.

Args:
    user_id: The user ID
    current_user: The authenticated user
    pagination: Pagination parameters

Returns:
    A paginated list of tasks

Raises:
    403: If the current user doesn't have permission to view the tasks
    404: If the user is not found
"""
```

5. **Validate access and handle errors consistently:**

```python
# Check if the current user is authorized to view the tasks
if user_id != current_user.id and not current_user.is_admin:
    raise forbidden_error("You don't have permission to view this user's tasks")
```

6. **Return standardized responses:**

```python
# Return paginated response
return create_collection_response(
    items=tasks,
    total=total,
    page=pagination["page"],
    page_size=pagination["page_size"],
)
```

## Application Setup

Setting up the application with these utilities is demonstrated in `app/example_app.py`.

**Key Steps:**

1. **Create the FastAPI application:**

```python
app = FastAPI(
    title="ADHD Calendar API",
    version="1.0.0",
    # ...
)
```

2. **Set up error handling middleware:**

```python
from app.middleware.error_handler import setup_error_handling

setup_error_handling(app)
```

3. **Include routes:**

```python
app.include_router(task_router, prefix="/api/v1")
```

## Benefits of Using These Utilities

- **Consistency:** All API endpoints will have the same response format, error handling, and documentation
- **Reduced Boilerplate:** Common patterns are encapsulated in reusable functions
- **Better Developer Experience:** Documentation is generated automatically
- **Improved Client Experience:** Clients can rely on consistent behavior
- **Easier Maintenance:** Changes to response format or error handling can be made in one place
