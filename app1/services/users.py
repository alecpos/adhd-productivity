"""User domain services for the Supabase-backed application."""

from __future__ import annotations

from uuid import UUID

from app.schemas.user_schema import UserCreateSchema, UserResponseSchema, UserUpdateSchema
from app1.core.exceptions import ConflictError, NotFoundError
from app1.domain.users.repository import SupabaseUserRepository


class UserService:
    """High level user orchestration that wraps the Supabase repository."""

    def __init__(self, repository: SupabaseUserRepository) -> None:
        self._repository = repository

    def register_user(self, payload: UserCreateSchema) -> UserResponseSchema:
        existing = self._repository.get_user_by_email(payload.email)
        if existing:
            raise ConflictError("A user with this email already exists")
        return self._repository.create_user(payload)

    def get_user(self, user_id: UUID) -> UserResponseSchema:
        return self._repository.get_user_by_id(user_id)

    def update_user(self, user_id: UUID, payload: UserUpdateSchema) -> UserResponseSchema:
        self._repository.get_user_by_id(user_id)
        return self._repository.update_user(user_id, payload)

    def delete_user(self, user_id: UUID) -> None:
        try:
            self._repository.delete_user(user_id)
        except NotFoundError as exc:
            raise NotFoundError("User not found") from exc

    def list_users(self) -> list[UserResponseSchema]:
        return self._repository.list_users()


__all__ = ["UserService"]
