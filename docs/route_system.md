# Route System Documentation

## Overview

The route system provides a standardized way to handle HTTP requests with proper validation, error handling, and response formatting. It's built on FastAPI and includes features like schema validation, dependency injection, and comprehensive error handling.

## Components

### 1. BaseRouter

The BaseRouter is the foundation of our route system, providing common CRUD operations and standardized response handling.

```python
from app.routes.base_router import BaseRouter
from app.schemas.user_schema import UserSchema
from app.services.user_service import UserService

class UserRouter(BaseRouter[UserSchema, UserService]):
    def __init__(self):
        super().__init__(
            prefix="/users",
            tags=["users"],
            schema_class=UserSchema,
            service_class=UserService
        )
```

### 2. Response Models

Standardized response models ensure consistent API responses.

```python
from app.schemas.base_schemas import APIResponse, ErrorResponse, PaginatedResponse

# Success response
response = APIResponse(
    data=user,
    message="User retrieved successfully"
)

# Error response
error = ErrorResponse(
    message="User not found",
    code="NOT_FOUND",
    details={"id": user_id}
)

# Paginated response
paginated = PaginatedResponse(
    items=users,
    total=total_count,
    page=page,
    size=size
)
```

## Common Use Cases

### 1. Creating a New Router

```python
class TaskRouter(BaseRouter[TaskSchema, TaskService]):
    def __init__(self):
        super().__init__(
            prefix="/tasks",
            tags=["tasks"],
            schema_class=TaskSchema,
            service_class=TaskService
        )
        self._register_custom_routes()

    def _register_custom_routes(self):
        @self.router.get("/overdue")
        async def get_overdue_tasks(
            db: AsyncSession = Depends(get_db)
        ):
            """Get overdue tasks."""
            service = self.service_class(db)
            tasks = await service.get_overdue_tasks()
            return APIResponse(data=tasks)
```

### 2. Error Handling

```python
@router.get("/{id}")
@handle_service_error
async def get_item(
    id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get item by ID with error handling."""
    service = self.service_class(db)
    item = await service.get_by_id(id)
    if not item:
        raise HTTPException(
            status_code=404,
            detail=ErrorResponse(
                message="Item not found",
                code="NOT_FOUND",
                details={"id": id}
            ).dict()
        )
    return APIResponse(data=item)
```

### 3. Pagination

```python
@router.get("/", response_model=PaginatedResponse[TaskSchema])
async def get_all(
    page: int = 1,
    size: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """Get all items with pagination."""
    service = self.service_class(db)
    items = await service.get_all()
    return PaginatedResponse.create(
        items=items,
        total=len(items),
        page=page,
        size=size
    )
```

## Best Practices

### 1. Route Organization

- Group related routes in the same router class
- Use meaningful prefixes and tags
- Keep route handlers focused and concise
- Document route parameters and responses

```python
class UserRouter(BaseRouter[UserSchema, UserService]):
    """Router for user-related operations."""

    def __init__(self):
        super().__init__(
            prefix="/users",
            tags=["users"],
            schema_class=UserSchema,
            service_class=UserService
        )
```

### 2. Error Handling

- Use the handle_service_error decorator
- Provide meaningful error messages
- Include relevant error details
- Use appropriate HTTP status codes

```python
@handle_service_error
async def update_user(
    id: str,
    data: UserUpdateSchema,
    db: AsyncSession = Depends(get_db)
):
    """Update user with proper error handling."""
    try:
        user = await service.update(id, data)
        return APIResponse(data=user)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=ErrorResponse(
                message=str(e),
                code="VALIDATION_ERROR"
            ).dict()
        )
```

### 3. Response Formatting

- Use consistent response models
- Include meaningful messages
- Properly type response models
- Handle nested data structures

```python
@router.get("/profile", response_model=APIResponse[UserProfileSchema])
async def get_profile(
    db: AsyncSession = Depends(get_db)
):
    """Get user profile with proper response formatting."""
    profile = await service.get_profile()
    return APIResponse(
        data=profile,
        message="Profile retrieved successfully"
    )
```

## Advanced Features

### 1. Custom Route Decorators

```python
def require_subscription(func):
    """Decorator to check subscription status."""
    async def wrapper(*args, **kwargs):
        if not await check_subscription():
            raise HTTPException(
                status_code=403,
                detail=ErrorResponse(
                    message="Subscription required",
                    code="SUBSCRIPTION_REQUIRED"
                ).dict()
            )
        return await func(*args, **kwargs)
    return wrapper

@router.post("/premium-feature")
@require_subscription
async def premium_feature(
    db: AsyncSession = Depends(get_db)
):
    """Premium feature endpoint."""
    pass
```

### 2. Request Validation

```python
from pydantic import validator

class CreateUserRequest(BaseModel):
    username: str
    email: str
    password: str

    @validator("password")
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v

@router.post("/users")
async def create_user(
    request: CreateUserRequest,
    db: AsyncSession = Depends(get_db)
):
    """Create user with request validation."""
    pass
```

### 3. Response Caching

```python
from fastapi_cache.decorator import cache

@router.get("/cached-data")
@cache(expire=300)  # Cache for 5 minutes
async def get_cached_data(
    db: AsyncSession = Depends(get_db)
):
    """Endpoint with response caching."""
    data = await service.get_expensive_computation()
    return APIResponse(data=data)
```

## Testing

### 1. Route Tests

```python
def test_create_user():
    """Test user creation route."""
    response = client.post("/users", json={
        "username": "test",
        "email": "test@example.com"
    })
    assert response.status_code == 200
    assert response.json()["message"] == "User created successfully"
```

### 2. Error Handling Tests

```python
def test_error_handling():
    """Test route error handling."""
    response = client.get("/users/nonexistent")
    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "NOT_FOUND"
```

### 3. Pagination Tests

```python
def test_pagination():
    """Test route pagination."""
    response = client.get("/users?page=2&size=10")
    data = response.json()["data"]
    assert len(data["items"]) == 10
    assert data["page"] == 2
    assert data["size"] == 10
```

## Performance Considerations

### 1. Response Size

- Use pagination for large datasets
- Select only needed fields
- Compress responses when appropriate

```python
@router.get("/large-dataset")
async def get_large_dataset(
    page: int = 1,
    size: int = 100,
    fields: List[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Handle large dataset with pagination and field selection."""
    data = await service.get_paginated(page, size, fields)
    return PaginatedResponse.create(
        items=data.items,
        total=data.total,
        page=page,
        size=size
    )
```

### 2. Caching Strategies

- Cache frequently accessed data
- Use appropriate cache expiration
- Implement cache invalidation

```python
@router.get("/cached-endpoint")
@cache(
    expire=300,
    key_builder=lambda f, *args, **kwargs: f"{f.__name__}:{kwargs.get('id')}"
)
async def get_cached_endpoint(
    id: str,
    db: AsyncSession = Depends(get_db)
):
    """Endpoint with custom cache key."""
    pass
```

### 3. Database Optimization

- Use efficient queries
- Implement proper indexes
- Handle N+1 query problems

```python
@router.get("/optimized-query")
async def get_optimized_data(
    db: AsyncSession = Depends(get_db)
):
    """Endpoint with optimized database query."""
    data = await service.get_with_related(
        select_from(Model)
        .options(joinedload(Model.related))
        .filter(Model.active == True)
    )
    return APIResponse(data=data)
```
