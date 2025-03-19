"""
Example Task Route

This module demonstrates how to implement API routes following the API design guidelines.
This is an example file and is not meant to be used in production.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, Query, status
from uuid import UUID

from app.models.task_model import Task
from app.schemas.task_schemas import (
    TaskCreate, 
    TaskResponse, 
    TaskUpdate, 
    TaskListResponse,
    TaskStats
)
from app.services.task_service import TaskService
from app.utils.auth import get_current_user
from app.utils.api_responses import (
    create_collection_response,
)
from app.utils.route_utils import (
    error_responses,
    id_path_param,
    pagination_params,
    not_found_error,
    forbidden_error,
    validation_error,
)
from app.schemas.user_schemas import UserResponse

# Create router with prefix and tags
router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"],
    responses=error_responses(401),  # Add default 401 response to all routes
)


@router.get(
    "/user/{user_id}", 
    response_model=TaskListResponse,
    summary="Get User Tasks",
    description="Retrieve all tasks for a specific user",
    responses=error_responses(403, 404),
)
async def get_user_tasks(
    user_id: UUID = Depends(id_path_param("user")),
    current_user: UserResponse = Depends(get_current_user),
    pagination: Dict[str, int] = Depends(pagination_params),
    status: Optional[str] = Query(None, description="Filter tasks by status"),
    priority: Optional[str] = Query(None, description="Filter tasks by priority"),
    task_service: TaskService = Depends(),
):
    """
    Retrieve all tasks for a specific user.
    
    Args:
        user_id: The user ID
        current_user: The authenticated user
        pagination: Pagination parameters
        status: Optional filter by task status
        priority: Optional filter by task priority
        task_service: Task service dependency
        
    Returns:
        A paginated list of tasks
        
    Raises:
        403: If the current user doesn't have permission to view the tasks
        404: If the user is not found
    """
    # Check if the current user is authorized to view the tasks
    if user_id != current_user.id and not current_user.is_admin:
        raise forbidden_error("You don't have permission to view this user's tasks")
    
    # Get tasks from the service
    tasks, total = await task_service.get_user_tasks(
        user_id=user_id,
        page=pagination["page"],
        page_size=pagination["page_size"],
        status=status,
        priority=priority,
    )
    
    # Return paginated response
    return create_collection_response(
        items=tasks,
        total=total,
        page=pagination["page"],
        page_size=pagination["page_size"],
    )


@router.post(
    "/",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Task",
    description="Create a new task for the current user",
    responses=error_responses(400),
)
async def create_task(
    task: TaskCreate,
    current_user: UserResponse = Depends(get_current_user),
    task_service: TaskService = Depends(),
):
    """
    Create a new task for the current user.
    
    Args:
        task: The task data
        current_user: The authenticated user
        task_service: Task service dependency
        
    Returns:
        The created task
        
    Raises:
        400: If the task data is invalid
    """
    # Create the task
    return await task_service.create_task(
        task_data=task,
        user_id=current_user.id,
    )


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Get Task",
    description="Retrieve a specific task by ID",
    responses=error_responses(403, 404),
)
async def get_task(
    task_id: UUID = Depends(id_path_param("task")),
    current_user: UserResponse = Depends(get_current_user),
    task_service: TaskService = Depends(),
):
    """
    Retrieve a specific task by ID.
    
    Args:
        task_id: The task ID
        current_user: The authenticated user
        task_service: Task service dependency
        
    Returns:
        The requested task
        
    Raises:
        403: If the current user doesn't have permission to view the task
        404: If the task is not found
    """
    # Get the task
    task = await task_service.get_task(task_id)
    
    # Check if the task exists
    if task is None:
        raise not_found_error("Task", task_id)
    
    # Check if the current user is authorized to view the task
    if task.user_id != current_user.id and not current_user.is_admin:
        raise forbidden_error("You don't have permission to view this task")
    
    return task


@router.put(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Update Task",
    description="Update a specific task by ID",
    responses=error_responses(400, 403, 404),
)
async def update_task(
    task_update: TaskUpdate,
    task_id: UUID = Depends(id_path_param("task")),
    current_user: UserResponse = Depends(get_current_user),
    task_service: TaskService = Depends(),
):
    """
    Update a specific task by ID.
    
    Args:
        task_update: The task update data
        task_id: The task ID
        current_user: The authenticated user
        task_service: Task service dependency
        
    Returns:
        The updated task
        
    Raises:
        400: If the task update data is invalid
        403: If the current user doesn't have permission to update the task
        404: If the task is not found
    """
    # Get the task
    task = await task_service.get_task(task_id)
    
    # Check if the task exists
    if task is None:
        raise not_found_error("Task", task_id)
    
    # Check if the current user is authorized to update the task
    if task.user_id != current_user.id and not current_user.is_admin:
        raise forbidden_error("You don't have permission to update this task")
    
    # Update the task
    return await task_service.update_task(
        task_id=task_id,
        task_update=task_update,
    )


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Task",
    description="Delete a specific task by ID",
    responses=error_responses(403, 404),
)
async def delete_task(
    task_id: UUID = Depends(id_path_param("task")),
    current_user: UserResponse = Depends(get_current_user),
    task_service: TaskService = Depends(),
):
    """
    Delete a specific task by ID.
    
    Args:
        task_id: The task ID
        current_user: The authenticated user
        task_service: Task service dependency
        
    Returns:
        No content (204)
        
    Raises:
        403: If the current user doesn't have permission to delete the task
        404: If the task is not found
    """
    # Get the task
    task = await task_service.get_task(task_id)
    
    # Check if the task exists
    if task is None:
        raise not_found_error("Task", task_id)
    
    # Check if the current user is authorized to delete the task
    if task.user_id != current_user.id and not current_user.is_admin:
        raise forbidden_error("You don't have permission to delete this task")
    
    # Delete the task
    await task_service.delete_task(task_id)
    
    # Return no content (204)
    return None


@router.post(
    "/{task_id}/complete",
    response_model=TaskResponse,
    summary="Complete Task",
    description="Mark a specific task as complete",
    responses=error_responses(403, 404),
)
async def complete_task(
    task_id: UUID = Depends(id_path_param("task")),
    current_user: UserResponse = Depends(get_current_user),
    actual_duration: Optional[int] = Query(None, description="Actual duration in minutes"),
    task_service: TaskService = Depends(),
):
    """
    Mark a specific task as complete.
    
    Args:
        task_id: The task ID
        current_user: The authenticated user
        actual_duration: The actual duration of the task in minutes
        task_service: Task service dependency
        
    Returns:
        The updated task
        
    Raises:
        403: If the current user doesn't have permission to complete the task
        404: If the task is not found
    """
    # Get the task
    task = await task_service.get_task(task_id)
    
    # Check if the task exists
    if task is None:
        raise not_found_error("Task", task_id)
    
    # Check if the current user is authorized to complete the task
    if task.user_id != current_user.id and not current_user.is_admin:
        raise forbidden_error("You don't have permission to complete this task")
    
    # Complete the task
    return await task_service.complete_task(
        task_id=task_id,
        actual_duration=actual_duration,
    )


@router.get(
    "/statistics",
    response_model=TaskStats,
    summary="Get Task Statistics",
    description="Get statistics about tasks for the current user",
)
async def get_task_statistics(
    current_user: UserResponse = Depends(get_current_user),
    task_service: TaskService = Depends(),
):
    """
    Get statistics about tasks for the current user.
    
    Args:
        current_user: The authenticated user
        task_service: Task service dependency
        
    Returns:
        Task statistics
    """
    # Get task statistics
    return await task_service.get_task_statistics(current_user.id) 