"""API dependencies for authentication."""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jwt import PyJWTError

from app.database import get_db
from app.core.config import settings
from app.services.auth_service import AuthService
from app.schemas.user_schema import UserResponseSchema

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> UserResponseSchema:
    """Get the current authenticated user.

    Args:
        token: The JWT token for authentication
        db: The database session

    Returns:
        The authenticated user

    Raises:
        HTTPException: If authentication fails
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        auth_service = AuthService(db)
        user = await auth_service.get_current_user(token)
        if user is None:
            raise credentials_exception
        return UserResponseSchema.model_validate(user)
    except PyJWTError:
        raise credentials_exception
