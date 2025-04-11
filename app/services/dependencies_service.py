"""Authentication dependencies module."""

from typing import AsyncGenerator, Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.auth_service import AuthService
from app.models.user_model import UserModel

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> UserModel:
    """Get the current authenticated user."""
    auth_service = AuthService(db)
    return await auth_service.get_current_user(token)
