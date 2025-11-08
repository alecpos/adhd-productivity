"""Task service orchestrating Supabase-backed repositories with schema validation."""

from __future__ import annotations

from uuid import UUID

from app.schemas.task_schema import TaskCreate, TaskResponse, TaskUpdate
from app1.domain.tasks.repository import SupabaseTaskRepository


class TaskService:
    """Provide task centric use-cases on top of Supabase persistence."""

    def __init__(self, repository: SupabaseTaskRepository) -> None:
        self._repository = repository

    def create_task(self, payload: TaskCreate) -> TaskResponse:
        return self._repository.create_task(payload)

    def list_tasks(self, user_id: UUID) -> list[TaskResponse]:
        return self._repository.list_tasks_for_user(user_id)

    def get_task(self, task_id: UUID) -> TaskResponse:
        return self._repository.get_task(task_id)

    def update_task(self, task_id: UUID, payload: TaskUpdate) -> TaskResponse:
        return self._repository.update_task(task_id, payload)

    def delete_task(self, task_id: UUID) -> None:
        self._repository.delete_task(task_id)


__all__ = ["TaskService"]
