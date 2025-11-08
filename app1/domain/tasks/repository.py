"""Supabase repository implementation for task entities."""

from __future__ import annotations

from typing import Any, Dict, List
from uuid import UUID

from supabase import Client

from app.schemas.task_schema import TaskCreate, TaskResponse, TaskUpdate
from app1.core.exceptions import AppError, NotFoundError


class SupabaseTaskRepository:
    """Handles task persistence against Supabase PostgREST endpoints."""

    def __init__(self, client: Client, table: str) -> None:
        self._client = client
        self._table = table

    def _execute_single(self, query: Any) -> Dict[str, Any]:
        response = query.execute()
        if getattr(response, "error", None):
            raise AppError(detail=str(response.error))
        if not response.data:
            raise NotFoundError("Task not found")
        if isinstance(response.data, list):
            return response.data[0]
        return response.data

    def _execute_many(self, query: Any) -> List[Dict[str, Any]]:
        response = query.execute()
        if getattr(response, "error", None):
            raise AppError(detail=str(response.error))
        return response.data or []

    def create_task(self, payload: TaskCreate) -> TaskResponse:
        data = payload.model_dump(exclude_none=True)
        query = self._client.table(self._table).insert(data).select("*")
        record = self._execute_single(query)
        return TaskResponse.model_validate(record)

    def list_tasks_for_user(self, user_id: UUID) -> List[TaskResponse]:
        query = self._client.table(self._table).select("*").eq("user_id", str(user_id))
        records = self._execute_many(query)
        return [TaskResponse.model_validate(record) for record in records]

    def get_task(self, task_id: UUID) -> TaskResponse:
        query = self._client.table(self._table).select("*").eq("id", str(task_id)).limit(1)
        record = self._execute_single(query)
        return TaskResponse.model_validate(record)

    def update_task(self, task_id: UUID, payload: TaskUpdate) -> TaskResponse:
        data = payload.model_dump(exclude_none=True)
        if not data:
            raise AppError(detail="No task fields supplied for update")
        query = (
            self._client.table(self._table)
            .update(data)
            .eq("id", str(task_id))
            .select("*")
            .limit(1)
        )
        record = self._execute_single(query)
        return TaskResponse.model_validate(record)

    def delete_task(self, task_id: UUID) -> None:
        query = self._client.table(self._table).delete().eq("id", str(task_id)).limit(1)
        self._execute_single(query)


__all__ = ["SupabaseTaskRepository"]
