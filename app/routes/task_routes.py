"""
Task routes for the ADHD Calendar API.

This module contains all API routes related to tasks, including CRUD operations
and task-specific functionalities like task completion and statistics.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.user_model import UserModel
from app.services.auth_service import get_current_user
from fastapi import APIRouter, Depends, Query, Path, HTTPException
from typing import List, Optional
from uuid import UUID
import logging

from app.schemas.task_schema import (
    TaskResponse,
    TaskCreate,
    TaskUpdate,
    TaskStatsSchema,
    TaskListResponse
)
from app.services.task_service import TaskService
from app.utils.api_responses import (
    create_response,
    create_collection_response,
    not_found_response,
    forbidden_response
)
from app.utils.route_utils import (
    error_responses,
    pagination_params,
    id_path_param,
    validate_resource_access,
    not_found_error,
    forbidden_error
)
from app.utils.exceptions import ResourceNotFoundError
from app.models.enums_model import TaskState

logger = logging.getLogger(__name__)
task_router = APIRouter(prefix="/tasks", tags=["tasks"])


@task_router.get(
    "",
    response_model=TaskListResponse,
    summary="Get all tasks for the current user",
    description="Retrieve all tasks belonging to the currently authenticated user with pagination.",
    responses=error_responses()
)
async def get_user_tasks(
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    status: Optional[TaskState] = Query(None, description="Filter tasks by status"),
    priority: Optional[str] = Query(None, description="Filter tasks by priority"),
    due_before: Optional[str] = Query(None, description="Filter tasks due before this date (ISO format)"),
    due_after: Optional[str] = Query(None, description="Filter tasks due after this date (ISO format)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Number of items per page"),
):
    """
    Get all tasks for the authenticated user with pagination and filtering.

    Args:
        current_user: The authenticated user
        db: Database session
        status: Optional status filter
        priority: Optional priority filter
        due_before: Optional due date upper bound filter
        due_after: Optional due date lower bound filter
        page: Page number (1-indexed)
        page_size: Number of items per page

    Returns:
        A paginated list of tasks with optional statistics
    """
    logger.info(f"Fetching tasks for user_id: {current_user.id} with filters")

    try:
        task_service = TaskService(db)

        # Build filters dictionary
        filters = {}
        if status:
            filters["status"] = status.value
        if priority:
            filters["priority"] = priority
        if due_before:
            filters["due_before"] = due_before
        if due_after:
            filters["due_after"] = due_after

        tasks, total = await task_service.get_user_tasks_paginated(
            str(current_user.id),
            page=page,
            page_size=page_size,
            filters=filters
        )

        # Get basic stats
        stats = None
        if page == 1:  # Only include stats on first page
            stats = await task_service.get_task_statistics(str(current_user.id))

        logger.info(f"Successfully fetched {len(tasks)} tasks for user {current_user.id}")

        return create_collection_response(
            items=tasks,
            total=total,
            page=page,
            page_size=page_size,
            wrapper_class=TaskListResponse,
            extra={"stats": stats}
        )

    except Exception as e:
        logger.error(f"Error fetching tasks for user {current_user.id}: {str(e)}", exc_info=True)
        raise


@task_router.get(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Get a specific task",
    description="Retrieve a specific task by its ID. The user must be the owner of the task.",
    responses=error_responses(403, 404)
)
async def get_task(
    task_id: UUID = id_path_param("task"),
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get a specific task by ID.

    Args:
        task_id: The ID of the task to retrieve
        current_user: The authenticated user
        db: Database session

    Returns:
        The requested task

    Raises:
        ResourceNotFoundError: If the task doesn't exist
        ForbiddenError: If the user doesn't own the task
    """
    logger.info(f"Fetching task {task_id} for user {current_user.id}")

    try:
        task_service = TaskService(db)
        task = await task_service.get_task(str(task_id))

        if task is None:
            logger.warning(f"Task {task_id} not found")
            raise not_found_error("task", task_id)

        # Validate that the user has access to this task
        validate_resource_access(task, current_user.id, "user_id")

        logger.info(f"Successfully fetched task {task_id}")
        return create_response(task)

    except ResourceNotFoundError:
        return not_found_response("task", task_id)
    except Exception as e:
        logger.error(f"Error fetching task {task_id}: {str(e)}", exc_info=True)
        raise


@task_router.post(
    "",
    response_model=TaskResponse,
    status_code=201,
    summary="Create a new task",
    description="Create a new task for the authenticated user.",
    responses=error_responses()
)
async def create_task(
    task: TaskCreate,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new task.

    Args:
        task: The task data
        current_user: The authenticated user
        db: Database session

    Returns:
        The created task
    """
    logger.info(f"Creating task for user {current_user.id}")
    logger.debug(f"Task data: {task.dict()}")

    try:
        task_service = TaskService(db)
        created_task = await task_service.create_task(task, str(current_user.id))
        logger.info(f"Successfully created task {created_task.id} for user {current_user.id}")

        return create_response(created_task)

    except Exception as e:
        logger.error(f"Error creating task: {str(e)}", exc_info=True)
        raise


@task_router.put(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Update a task",
    description="Update an existing task. The user must be the owner of the task.",
    responses=error_responses(403, 404)
)
async def update_task(
    task_update: TaskUpdate,
    task_id: UUID = id_path_param("task"),
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update a task.

    Args:
        task_id: The ID of the task to update
        task_update: The task update data
        current_user: The authenticated user
        db: Database session

    Returns:
        The updated task

    Raises:
        ResourceNotFoundError: If the task doesn't exist
        ForbiddenError: If the user doesn't own the task
    """
    logger.info(f"Updating task {task_id} for user {current_user.id}")
    logger.debug(f"Update data: {task_update.dict(exclude_unset=True)}")

    try:
        task_service = TaskService(db)

        # First get the task to check ownership
        task = await task_service.get_task(str(task_id))

        if task is None:
            logger.warning(f"Task {task_id} not found")
            raise not_found_error("task", task_id)

        # Validate that the user has access to this task
        validate_resource_access(task, current_user.id, "user_id")

        # Perform the update
        updated_task = await task_service.update_task(
            str(task_id), task_update, str(current_user.id)
        )

        logger.info(f"Successfully updated task {task_id}")
        return create_response(updated_task)

    except ResourceNotFoundError:
        return not_found_response("task", task_id)
    except Exception as e:
        logger.error(f"Error updating task {task_id}: {str(e)}", exc_info=True)
        raise


@task_router.delete(
    "/{task_id}",
    status_code=204,
    summary="Delete a task",
    description="Delete an existing task. The user must be the owner of the task.",
    responses=error_responses(403, 404)
)
async def delete_task(
    task_id: UUID = id_path_param("task"),
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a task.

    Args:
        task_id: The ID of the task to delete
        current_user: The authenticated user
        db: Database session

    Returns:
        204 No Content on success

    Raises:
        ResourceNotFoundError: If the task doesn't exist
        ForbiddenError: If the user doesn't own the task
    """
    logger.info(f"Deleting task {task_id} for user {current_user.id}")

    try:
        task_service = TaskService(db)

        # First get the task to check ownership
        task = await task_service.get_task(str(task_id))

        if task is None:
            logger.warning(f"Task {task_id} not found")
            raise not_found_error("task", task_id)

        # Validate that the user has access to this task
        validate_resource_access(task, current_user.id, "user_id")

        # Perform the deletion
        await task_service.delete(str(task_id))

        logger.info(f"Successfully deleted task {task_id}")
        return None

    except ResourceNotFoundError:
        return not_found_response("task", task_id)
    except Exception as e:
        logger.error(f"Error deleting task {task_id}: {str(e)}", exc_info=True)
        raise


@task_router.post(
    "/{task_id}/complete",
    response_model=TaskResponse,
    summary="Mark a task as complete",
    description="Mark an existing task as complete. The user must be the owner of the task.",
    responses=error_responses(403, 404)
)
async def complete_task(
    task_id: UUID = id_path_param("task"),
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Mark a task as complete.

    Args:
        task_id: The ID of the task to mark as complete
        current_user: The authenticated user
        db: Database session

    Returns:
        The updated task

    Raises:
        ResourceNotFoundError: If the task doesn't exist
        ForbiddenError: If the user doesn't own the task
    """
    logger.info(f"Completing task {task_id} for user {current_user.id}")

    try:
        task_service = TaskService(db)

        # First get the task to check ownership
        task = await task_service.get_task(str(task_id))

        if task is None:
            logger.warning(f"Task {task_id} not found")
            raise not_found_error("task", task_id)

        # Validate that the user has access to this task
        validate_resource_access(task, current_user.id, "user_id")

        # Mark the task as complete
        completed_task = await task_service.complete_task(str(task_id))

        logger.info(f"Successfully completed task {task_id}")
        return create_response(completed_task)

    except ResourceNotFoundError:
        return not_found_response("task", task_id)
    except Exception as e:
        logger.error(f"Error completing task {task_id}: {str(e)}", exc_info=True)
        raise


@task_router.get(
    "/statistics",
    response_model=TaskStatsSchema,
    summary="Get task statistics",
    description="Get statistics about tasks for the authenticated user.",
    responses=error_responses()
)
async def get_task_statistics(
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    period_start: Optional[str] = Query(None, description="Start date for statistics (ISO format)"),
    period_end: Optional[str] = Query(None, description="End date for statistics (ISO format)"),
):
    """
    Get task statistics for the current user.

    Args:
        current_user: The authenticated user
        db: Database session
        period_start: Optional start date for statistics
        period_end: Optional end date for statistics

    Returns:
        Task statistics for the specified period
    """
    logger.info(f"Fetching task statistics for user {current_user.id}")

    try:
        task_service = TaskService(db)

        # Build filters dictionary
        filters = {}
        if period_start:
            filters["period_start"] = period_start
        if period_end:
            filters["period_end"] = period_end

        stats = await task_service.get_task_statistics(
            str(current_user.id),
            filters=filters
        )

        logger.info(f"Successfully fetched task statistics for user {current_user.id}")
        return create_response(stats)

    except Exception as e:
        logger.error(f"Error fetching task statistics: {str(e)}", exc_info=True)
        raise


__all__ = ["task_router"]
