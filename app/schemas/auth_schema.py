"""Authentication schemas."""

import re
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserBaseSchema(BaseModel):
    """Base schema for user data."""

    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: str = Field(..., min_length=1, max_length=100)

    model_config = ConfigDict(from_attributes=True)


class UserCreateSchema(UserBaseSchema):
    """Schema for user creation."""

    password: str = Field(..., min_length=8)

    @field_validator("password")
    def validate_password(cls, v):
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError("Password must contain at least one special character")
        return v

    @field_validator("username")
    def validate_username(cls, v):
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError("Username can only contain letters, numbers, underscores, and hyphens")
        return v


class UserResponseSchema(UserBaseSchema):
    """Schema for user response data."""

    id: UUID
    is_active: bool
    is_verified: bool
    preferences: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LoginRequest(BaseModel):
    """Schema for login requests."""

    username: str  # Can be either username or email
    password: str


class Token(BaseModel):
    """Schema for token data."""

    access_token: str
    token_type: str
    user: UserResponseSchema
    refresh_token: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class TokenRefresh(BaseModel):
    """Schema for token refresh requests."""

    refresh_token: str


class UserInToken(BaseModel):
    """Schema for user data stored in token."""

    id: str
    email: str
    username: str
    full_name: str

    model_config = ConfigDict(from_attributes=True)


class TokenData(BaseModel):
    """Schema for token payload data."""

    user_id: str


class TokenResponse(BaseModel):
    """Schema for token response."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponseSchema

    model_config = ConfigDict(from_attributes=True)


class EmailVerificationSchema(BaseModel):
    """Schema for email verification."""

    verification_token: str


class PasswordResetSchema(BaseModel):
    """Schema for password reset requests."""

    email: EmailStr
    new_password: str = Field(..., min_length=8)
    reset_token: str

    @field_validator("new_password")
    def validate_password(cls, v):
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError("Password must contain at least one special character")
        return v


class AccountDeactivationSchema(BaseModel):
    """Schema for account deactivation requests."""

    password: str
    deactivation_reason: Optional[str] = None


class AccountReactivationSchema(BaseModel):
    """Schema for account reactivation requests."""

    email: EmailStr
    password: str


class ChangePasswordSchema(BaseModel):
    """Schema for password change requests."""

    current_password: str
    new_password: str = Field(..., min_length=8)

    @field_validator("new_password")
    def validate_password(cls, v):
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError("Password must contain at least one special character")
        return v


__all__ = [
    "UserBaseSchema",
    "UserCreateSchema",
    "UserResponseSchema",
    "LoginRequest",
    "Token",
    "TokenRefresh",
    "UserInToken",
    "TokenData",
    "TokenResponse",
    "EmailVerificationSchema",
    "PasswordResetSchema",
    "AccountDeactivationSchema",
    "AccountReactivationSchema",
    "ChangePasswordSchema",
]
