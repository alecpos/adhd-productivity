"""User related HTTP routes."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, status
from supabase import Client

from app.schemas.user_schema import UserCreateSchema, UserResponseSchema, UserUpdateSchema
from app1.api.dependencies import get_app_settings, supabase_client
from app1.core.config import Settings
from app1.domain.users.repository import SupabaseUserRepository
from app1.services.users import UserService

router = APIRouter(prefix="/users", tags=["users"])


def get_user_service(
    client: Client = Depends(supabase_client),
    settings: Settings = Depends(get_app_settings),
) -> UserService:
    repository = SupabaseUserRepository(client, settings.supabase_users_table)
    return UserService(repository)


@router.post("/", response_model=UserResponseSchema, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreateSchema, service: UserService = Depends(get_user_service)) -> UserResponseSchema:
    return service.register_user(payload)


@router.get("/", response_model=list[UserResponseSchema])
def list_users(service: UserService = Depends(get_user_service)) -> list[UserResponseSchema]:
    return service.list_users()


@router.get("/{user_id}", response_model=UserResponseSchema)
def get_user(user_id: UUID, service: UserService = Depends(get_user_service)) -> UserResponseSchema:
    return service.get_user(user_id)


@router.patch("/{user_id}", response_model=UserResponseSchema)
def update_user(
    user_id: UUID,
    payload: UserUpdateSchema,
    service: UserService = Depends(get_user_service),
) -> UserResponseSchema:
    return service.update_user(user_id, payload)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: UUID, service: UserService = Depends(get_user_service)) -> None:
    service.delete_user(user_id)
    return None


__all__ = ["router"]
