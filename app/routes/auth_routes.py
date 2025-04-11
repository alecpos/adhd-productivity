"""Authentication routes."""

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.responses import APIResponse
from app.core.security import get_current_user
from app.database import get_db
from app.models.user_model import UserModel
from app.schemas.auth_schema import LoginRequest, TokenRefresh, TokenResponse
from app.schemas.user_schema import UserCreateSchema, UserResponseSchema
from app.services.auth_service import AuthService

auth_router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@auth_router.post(
    "/register",
    response_model=APIResponse[UserResponseSchema],
    status_code=status.HTTP_201_CREATED,
)
async def register(user_data: UserCreateSchema, db: AsyncSession = Depends(get_db)):
    """Register a new user."""
    auth_service = AuthService(db)
    user = await auth_service.register_user(user_data)
    return APIResponse(
        success=True,
        message="User registered successfully",
        data=UserResponseSchema.model_validate(user),
    )


@auth_router.post("/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    """Login to get access token."""
    auth_service = AuthService(db)
    return await auth_service.authenticate_user(form_data.username, form_data.password)


@auth_router.post("/refresh")
async def refresh_token(db: AsyncSession = Depends(get_db)):
    """Refresh access token."""
    auth_service = AuthService(db)
    return await auth_service.refresh_token()


@auth_router.get("/verify", response_model=APIResponse[UserResponseSchema])
async def verify_token(db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)):
    """Verify token and return current user info."""
    user = await get_current_user(token, db)
    return APIResponse(
        success=True,
        message="Token verified successfully",
        data=UserResponseSchema.model_validate(user),
    )


@auth_router.get("/me", response_model=APIResponse[UserResponseSchema])
async def get_current_user_info(
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[UserResponseSchema]:
    """Get current user information."""
    return APIResponse(
        success=True,
        message="User info retrieved successfully",
        data=UserResponseSchema.model_validate(current_user),
    )


@auth_router.post(
    "/reset-password",
    response_model=APIResponse[UserResponseSchema],
    status_code=status.HTTP_201_CREATED,
)
async def reset_password(reset_data: dict, db: AsyncSession = Depends(get_db)):
    """Reset user password."""
    auth_service = AuthService(db)
    user = await auth_service.reset_password(
        email=reset_data["email"],
        new_password=reset_data["new_password"],
        reset_token=reset_data["reset_token"],
    )
    return APIResponse(
        success=True,
        message="Password reset successfully",
        data=UserResponseSchema.model_validate(user),
    )
