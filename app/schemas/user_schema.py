"""User schemas."""

import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr


class User(BaseModel):
    email: EmailStr
    username: str
    full_name: str


class UserCreateSchema(User):
    password: str


class UserUpdateSchema(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None


class UserResponseSchema(User):
    id: UUID
    is_active: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True


# Removed alias: UserSchema = UserResponseSchema
# Instead, we set UserSchema to be User
UserSchema = User
