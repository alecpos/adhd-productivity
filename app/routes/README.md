# Routes Directory

This directory contains route definitions for the ADHD Calendar backend API.

## Overview

The routes directory defines the API routes and endpoints for the application. It maps URL paths to handler functions that process requests and return responses. Routes are organized by resource type and functionality.

## Route Organization

Routes are organized into modules by resource or functionality:

- **user_routes.py**: User management routes
- **auth_routes.py**: Authentication routes
- **task_routes.py**: Task management routes
- **calendar_routes.py**: Calendar management routes
- **ml_routes.py**: Machine learning functionality routes
- **admin_routes.py**: Administrative routes

## Route Structure

Each route module typically:

1. Creates a router instance
2. Defines routes with path, HTTP method, and handler function
3. Specifies response models
4. Includes dependencies like authentication
5. Documents endpoints with descriptions and examples

## API Versioning

API routes are versioned using URL prefixes:

- `/api/v1/...` - Version 1 endpoints
- `/api/v2/...` - Version 2 endpoints (when applicable)

## Authentication and Permissions

Routes use dependencies for authentication and permission checks:

- JWT authentication through dependencies
- Role-based access control
- Resource ownership verification

## Example Route Definition

```python
from fastapi import APIRouter, Depends, HTTPException
from app.schemas.task import TaskCreate, TaskResponse
from app.services.task_service import TaskService
from app.api.dependencies.auth import get_current_user

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("/", response_model=TaskResponse)
async def create_task(
    task_data: TaskCreate,
    current_user = Depends(get_current_user),
    task_service: TaskService = Depends()
):
    """
    Create a new task for the current user.
    """
    return await task_service.create_task(current_user.id, task_data)

@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    current_user = Depends(get_current_user),
    task_service: TaskService = Depends()
):
    """
    Get a specific task by ID.
    """
    task = await task_service.get_task(task_id)
    if task.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this task")
    return task
```

## Documentation

Routes are automatically documented using FastAPI's built-in OpenAPI integration. Each route includes:

- Path parameters
- Query parameters
- Request body schema
- Response models
- Authorization requirements
- Description and examples

## Development Guidelines

When creating new routes:

1. Follow RESTful principles for resource naming and methods
2. Use appropriate response models and status codes
3. Include authentication and permission checks
4. Document endpoints with clear descriptions
5. Add appropriate error handling
6. Include pagination for list endpoints

## Related Documentation

- [API Design Guidelines](../../docs/api_design_guidelines.md)
- [Authentication Guide](../../docs/authentication.md)
- [API Documentation](../../docs/api_documentation.md)
