"""Main application module."""

# Import all models first to ensure they are registered with SQLAlchemy
from app.models.base_model import BaseModel
from app.models.user_model import UserModel
from app.models.contact_model import ContactModel
from app.models.task_category_model import TaskCategoryModel
from app.models.task_model import TaskModel
from app.models.reminder_model import ReminderModel
from app.models.calendar_model import CalendarModel
from app.models.calendar_event_model import CalendarEventModel
from app.models.calendar_sync_model import CalendarSyncModel
from app.models.session_model import SessionModel
from app.models.scheduling_model import Interruption, Break, WorkHours, ScheduleBlock, SchedulePreferences, EnergyPattern

from fastapi.exceptions import RequestValidationError
from slowapi.errors import RateLimitExceeded
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.database import create_db_and_tables
from app.routes import api_router as legacy_api_router  # Renamed to avoid conflict
from app.api.api import api_router as new_api_router  # Import our new API router
from app.schemas.base_schema import ErrorDetailSchema as ErrorDetail
from app.utils.exceptions import AuthenticationError, ServiceError
import logging
import sys
from fastapi import FastAPI, APIRouter
from pydantic import ValidationError
from typing import Dict, Any, Optional
from fastapi import status
from app.core.config import settings
# Import the database module
from app.database import create_db_and_tables
from app.middleware.error_handler import setup_error_handling
from app.routes.example_task_route import router as task_router

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format=settings.LOG_FORMAT,
)
logging.getLogger("uvicorn").setLevel(logging.INFO)
logging.getLogger("fastapi").setLevel(logging.INFO)
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Define api_router as an instance of APIRouter
app_router = APIRouter()

# Include both legacy and new API routers
# Example: api_router.include_router(user_router)

def create_error_response_dict(
    code: str, message: str, details: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Create a standardized error response dictionary."""
    return {
        "success": False,
        "error": {"code": code, "message": message, "details": details or {}},
    }


def create_app() -> FastAPI:
    """
    Factory function to create and configure the FastAPI app instance.
    """
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description="API for ADHD Calendar backend with advanced ML features",
        version=settings.APP_VERSION,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
    )

    # Set CORS middleware
    if settings.BACKEND_CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    logger.info("Including the legacy api_router")
    app.include_router(legacy_api_router, prefix=settings.API_V1_STR)
    
    logger.info("Including the new API router")
    app.include_router(new_api_router, prefix=settings.API_V1_STR)

    # Include API routers - commented out as these don't exist in the current structure
    # app.include_router(auth.router)
    # app.include_router(users.router)
    # app.include_router(tasks.router)
    # app.include_router(calendar.router)

    # Include new API routers for BioAuth and Hyperfold - commented out for testing
    # if settings.BIOAUTH_ENABLED:
    #     app.include_router(bioauth.router)
    # app.include_router(hyperfold.router)

    # Set up error handling middleware
    setup_error_handling(app)

    @app.get("/")
    async def root():
        """
        Root endpoint to provide a welcome message.
        """
        logger.info("Root endpoint accessed")
        return {"message": "Welcome to the ADHD CalendarModelSchemaSchema API"}

    @app.get("/api/health", tags=["health"])
    async def health():
        """Health check endpoint."""
        return {"status": "ok"}

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle all unhandled exceptions."""
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal server error",
                "type": str(type(exc).__name__),
            },
        )

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        logger.info(f"Request: {request.method} {request.url}")
        response = await call_next(request)
        logger.info(f"Response: Status {response.status_code}")

    @app.on_event("startup")
    async def startup_event():
        logger.info("Starting up and initializing database schema")
        await create_db_and_tables()
        # await init_db()  # This function doesn't exist
        logger.info("Database initialized")

    @app.on_event("shutdown")
    async def shutdown_event():
        logger.info("Shutting down FastAPI application")

    return app


app = create_app()


def get_app() -> FastAPI:
    return app


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}
