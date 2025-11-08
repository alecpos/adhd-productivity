"""Task management endpoints for the Supabase powered stack."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, status
from supabase import Client

from app.schemas.task_schema import TaskCreate, TaskResponse, TaskUpdate
from app1.api.dependencies import get_app_settings, supabase_client
from app1.core.config import Settings
from app1.domain.tasks.repository import SupabaseTaskRepository
from app1.services.tasks import TaskService

router = APIRouter(prefix="/tasks", tags=["tasks"])


def get_task_service(
    client: Client = Depends(supabase_client),
    settings: Settings = Depends(get_app_settings),
) -> TaskService:
    repository = SupabaseTaskRepository(client, settings.supabase_tasks_table)
    return TaskService(repository)


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate, service: TaskService = Depends(get_task_service)) -> TaskResponse:
    return service.create_task(payload)


@router.get("/user/{user_id}", response_model=list[TaskResponse])
def list_tasks(user_id: UUID, service: TaskService = Depends(get_task_service)) -> list[TaskResponse]:
    return service.list_tasks(user_id)


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: UUID, service: TaskService = Depends(get_task_service)) -> TaskResponse:
    return service.get_task(task_id)


@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: UUID,
    payload: TaskUpdate,
    service: TaskService = Depends(get_task_service),
) -> TaskResponse:
    return service.update_task(task_id, payload)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: UUID, service: TaskService = Depends(get_task_service)) -> None:
    service.delete_task(task_id)
    return None


__all__ = ["router"]
