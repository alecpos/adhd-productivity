"""Persistence layer for user entities backed by Supabase."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import status
from supabase import Client

from app.schemas.user_schema import UserCreateSchema, UserResponseSchema, UserUpdateSchema
from app1.core.exceptions import AppError, NotFoundError


class SupabaseUserRepository:
    """Repository responsible for persisting users inside Supabase."""

    def __init__(self, client: Client, table: str) -> None:
        self._client = client
        self._table = table

    def _execute_single(self, query: Any) -> Dict[str, Any]:
        response = query.execute()
        if getattr(response, "error", None):
            raise AppError(detail=str(response.error))
        if not response.data:
            raise NotFoundError("User not found")
        if isinstance(response.data, list):
            return response.data[0]
        return response.data

    def _execute_many(self, query: Any) -> List[Dict[str, Any]]:
        response = query.execute()
        if getattr(response, "error", None):
            raise AppError(detail=str(response.error))
        return response.data or []

    def create_user(self, payload: UserCreateSchema) -> UserResponseSchema:
        user_dict = payload.model_dump(exclude_none=True)
        query = self._client.table(self._table).insert(user_dict).select("*")
        record = self._execute_single(query)
        return UserResponseSchema.model_validate(record)

    def get_user_by_id(self, user_id: UUID) -> UserResponseSchema:
        query = self._client.table(self._table).select("*").eq("id", str(user_id)).limit(1)
        record = self._execute_single(query)
        return UserResponseSchema.model_validate(record)

    def get_user_by_email(self, email: str) -> Optional[UserResponseSchema]:
        query = self._client.table(self._table).select("*").eq("email", email).limit(1)
        try:
            record = self._execute_single(query)
        except NotFoundError:
            return None
        return UserResponseSchema.model_validate(record)

    def list_users(self) -> List[UserResponseSchema]:
        query = self._client.table(self._table).select("*")
        records = self._execute_many(query)
        return [UserResponseSchema.model_validate(record) for record in records]

    def update_user(self, user_id: UUID, payload: UserUpdateSchema) -> UserResponseSchema:
        update_dict = payload.model_dump(exclude_none=True)
        if not update_dict:
            raise AppError(status.HTTP_400_BAD_REQUEST, "No fields provided for update")
        query = (
            self._client.table(self._table)
            .update(update_dict)
            .eq("id", str(user_id))
            .select("*")
            .limit(1)
        )
        record = self._execute_single(query)
        return UserResponseSchema.model_validate(record)

    def delete_user(self, user_id: UUID) -> None:
        query = self._client.table(self._table).delete().eq("id", str(user_id)).limit(1)
        try:
            self._execute_single(query)
        except NotFoundError as exc:
            raise NotFoundError("User not found") from exc


__all__ = ["SupabaseUserRepository"]
