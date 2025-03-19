"""Authentication service module."""

import logging
import secrets
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Tuple
from uuid import UUID

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import NotFoundException, UnauthorizedException
from app.core.responses import APIResponse
from app.database import get_db
from app.models.login_attempt_model import LoginAttemptModel
from app.models.user_model import UserModel
from app.schemas.auth_schema import TokenData, TokenResponse
from app.schemas.user_schema import UserCreateSchema, UserResponseSchema

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

logger = logging.getLogger(__name__)


class AuthService:
    """Authentication service."""

    def __init__(self, db: AsyncSession):
        """Initialize the service."""
        self.db = db
        self.secret_key = settings.SECRET_KEY
        self.algorithm = settings.ALGORITHM
        self.access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
        self.refresh_token_expire_days = settings.REFRESH_TOKEN_EXPIRE_DAYS

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against a hash."""
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Hash a password."""
        return pwd_context.hash(password)

    def create_access_token(
        self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create an access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
        
    def create_expired_token(
        self, data: Dict[str, Any]
    ) -> str:
        """Create an expired token for testing."""
        to_encode = data.copy()
        expire = datetime.utcnow() - timedelta(minutes=1)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    async def decode_token(self, token: str) -> TokenData:
        """Decode a JWT token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            user_id: str = payload.get("sub")
            if user_id is None:
                raise UnauthorizedException("Could not validate credentials")
            token_data = TokenData(user_id=UUID(user_id))
            return token_data
        except jwt.JWTError:
            raise UnauthorizedException("Could not validate credentials")

    async def get_current_user(self, token: str = Depends(oauth2_scheme)) -> UserModel:
        """Get the current user from a token."""
        token_data = await self.decode_token(token)
        query = select(UserModel).where(UserModel.id == token_data.user_id)
        result = await self.db.execute(query)
        user = result.scalar_one_or_none()
        if user is None:
            logger.error(f"User not found for ID: {token_data.user_id}")
            raise UnauthorizedException("Could not validate credentials")
        return user

    def create_refresh_token(
        self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create a refresh token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    async def refresh_access_token(self, refresh_token: str) -> TokenResponse:
        """Refresh an access token using a refresh token."""
        try:
            payload = jwt.decode(refresh_token, self.secret_key, algorithms=[self.algorithm])
            user_id: str = payload.get("sub")
            if user_id is None:
                raise UnauthorizedException("Invalid refresh token")

            query = (
                select(UserModel).where(UserModel.id == UUID(user_id)).with_for_update()
            )
            result = await self.db.execute(query)
            user = result.scalar_one_or_none()

            if not user or not user.refresh_token or user.refresh_token != refresh_token:
                raise UnauthorizedException("Invalid refresh token")

            if user.refresh_token_expires and user.refresh_token_expires < datetime.utcnow():
                raise UnauthorizedException("Refresh token has expired")

            access_token = self.create_access_token({"sub": str(user.id)})
            return TokenResponse(access_token=access_token, token_type="bearer")

        except jwt.JWTError:
            raise UnauthorizedException("Invalid refresh token")

    async def generate_reset_token(self, user_id: UUID) -> Tuple[str, datetime]:
        """Generate a password reset token."""
        token = secrets.token_urlsafe(32)
        expires = datetime.utcnow() + timedelta(hours=24)

        query = select(UserModel).where(UserModel.id == user_id).with_for_update()
        result = await self.db.execute(query)
        user = result.scalar_one_or_none()

        if not user:
            raise NotFoundException("User not found")

        user.reset_token = token
        user.reset_token_expires = expires
        await self.db.commit()
        return token, expires

    async def verify_reset_token(self, email: str, token: str) -> bool:
        """Verify a password reset token."""
        query = select(UserModel).where(
            (UserModel.email == email)
            & (UserModel.reset_token == token)
            & (UserModel.reset_token_expires > datetime.utcnow())
        )
        result = await self.db.execute(query)
        user = result.scalar_one_or_none()
        return bool(user)

    async def create_user(self, user_data: UserCreateSchema) -> UserResponseSchema:
        """Create a new user."""
        # Check if email already exists
        query = select(UserModel).where(UserModel.email == user_data.email)
        result = await self.db.execute(query)
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Email already registered")

        # Check if username already exists
        query = select(UserModel).where(UserModel.username == user_data.username)
        result = await self.db.execute(query)
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Username already taken")

        hashed_password = self.get_password_hash(user_data.password)
        user = UserModel(
            email=user_data.email,
            username=user_data.username,
            full_name=user_data.full_name,
            hashed_password=hashed_password,
            is_active=True,
            is_verified=False,
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return UserResponseSchema.from_orm(user)

    async def authenticate_user(self, username: str, password: str) -> TokenResponse:
        """Authenticate a user and return tokens."""
        query = select(UserModel).where(
            or_(UserModel.username == username, UserModel.email == username)
        )
        result = await self.db.execute(query)
        user = result.scalar_one_or_none()

        if not user:
            raise UnauthorizedException("Incorrect username or password")

        if not self.verify_password(password, user.hashed_password):
            # Log failed attempt
            attempt = LoginAttemptModel(
                user_id=user.id,
                ip_address="0.0.0.0",  # TODO: Get actual IP
                success=False,
                timestamp=datetime.utcnow(),
            )
            self.db.add(attempt)
            await self.db.commit()
            raise UnauthorizedException("Incorrect username or password")

        # Log successful attempt
        attempt = LoginAttemptModel(
            user_id=user.id,
            ip_address="0.0.0.0",  # TODO: Get actual IP
            success=True,
            timestamp=datetime.utcnow(),
        )
        self.db.add(attempt)

        access_token = self.create_access_token({"sub": str(user.id)})
        refresh_token = self.create_refresh_token({"sub": str(user.id)})

        user.refresh_token = refresh_token
        user.refresh_token_expires = datetime.utcnow() + timedelta(
            days=self.refresh_token_expire_days
        )
        await self.db.commit()

        return TokenResponse(
            access_token=access_token, refresh_token=refresh_token, token_type="bearer"
        )

    async def change_password(
        self, user_id: UUID, old_password: str, new_password: str
    ) -> APIResponse[UserResponseSchema]:
        """Change a user's password."""
        query = select(UserModel).where(UserModel.id == user_id).with_for_update()
        result = await self.db.execute(query)
        user = result.scalar_one_or_none()

        if not user:
            raise NotFoundException("User not found")

        if not self.verify_password(old_password, user.hashed_password):
            raise UnauthorizedException("Incorrect password")

        user.hashed_password = self.get_password_hash(new_password)
        user.refresh_token = None  # Invalidate all sessions
        user.refresh_token_expires = None
        await self.db.commit()
        await self.db.refresh(user)

        return APIResponse(
            status="success",
            message="Password changed successfully",
            data=UserResponseSchema.from_orm(user),
        )

    async def reset_password(self, email: str, token: str, new_password: str) -> bool:
        """Reset a user's password using a reset token."""
        query = (
            select(UserModel)
            .where(
                (UserModel.email == email)
                & (UserModel.reset_token == token)
                & (UserModel.reset_token_expires > datetime.utcnow())
            )
            .with_for_update()
        )
        result = await self.db.execute(query)
        user = result.scalar_one_or_none()

        if not user:
            return False

        user.hashed_password = self.get_password_hash(new_password)
        user.reset_token = None
        user.reset_token_expires = None
        user.refresh_token = None  # Invalidate all sessions
        user.refresh_token_expires = None
        await self.db.commit()
        return True

    def create_verification_token(self, data: Dict[str, Any]) -> str:
        """Create an email verification token."""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(hours=24)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    async def verify_email(self, token: str) -> bool:
        """Verify a user's email address."""
        try:
            payload = jwt.encode(token, self.secret_key, algorithms=[self.algorithm])
            email: str = payload.get("email")
            if email is None:
                return False

            query = select(UserModel).where(UserModel.email == email).with_for_update()
            result = await self.db.execute(query)
            user = result.scalar_one_or_none()

            if not user:
                return False

            user.is_verified = True
            await self.db.commit()
            return True

        except jwt.JWTError:
            return False


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> UserModel:
    """Get the current user from a token.
    
    This is a FastAPI dependency that can be used in route handlers to get the authenticated user.
    It uses AuthService internally but presents a simpler interface for route handlers.
    """
    auth_service = AuthService(db)
    return await auth_service.get_current_user(token)
