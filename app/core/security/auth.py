from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user_model import User
from app.services.auth_service import AuthService
from app.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
) -> User:
    """Get current user from JWT token"""
    auth_service = AuthService(db)
    return await auth_service.get_current_user(token)


__all__ = ["get_current_user"]
