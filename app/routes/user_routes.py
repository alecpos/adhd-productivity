from fastapi import APIRouter, HTTPException
from uuid import UUID

from app.schemas.user_schema import UserCreateSchema, UserResponseSchema, UserUpdateSchema
from app.services.user_service import UserService

user_router = APIRouter(prefix="/users", tags=["Users"])


@user_router.post("/", response_model=UserResponseSchema)
async def create_user(user: UserCreateSchema):
    return await UserService.create_user(user)


@user_router.get("/{user_id}", response_model=UserResponseSchema)
async def get_user(user_id: UUID):
    user = await UserService.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")


@user_router.put("/{user_id}", response_model=UserResponseSchema)
async def update_user(user_id: UUID, user: UserUpdateSchema):
    return await UserService.update_user(user_id, user)


@user_router.delete("/{user_id}")
async def delete_user(user_id: UUID):
    await UserService.delete_user(user_id)
    return {"detail": "User deleted successfully"}
