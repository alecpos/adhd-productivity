"""Main application module."""

# Standard library imports
import logging
import sys
from typing import Dict, Any, Optional

# Third-party imports
from fastapi import FastAPI, APIRouter, status
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

# Local application imports - configuration
from app.core.config import settings

# Local application imports - database
from app.database import create_db_and_tables

# Local application imports - routing
from app.routes import api_router as legacy_api_router
from app.api.api import api_router as new_api_router
from app.routes.example_task_route import router as task_router

# Local application imports - middleware
from app.middleware.error_handler import setup_error_handling

# Local application imports - schemas
from app.schemas.base_schema import ErrorDetailSchema as ErrorDetail

# Local application imports - utilities
from app.utils.exceptions import AuthenticationError, ServiceError

# Configure logging
def configure_logging():
    """Configure application logging."""
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL),
        format=settings.LOG_FORMAT,
    )
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
    return logging.getLogger(__name__)

# Initialize logger
logger = configure_logging()
logger.setLevel(logging.DEBUG)

# Create API router
app_router = APIRouter()

def create_error_response_dict(
    code: str, message: str, details: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Create a standardized error response dictionary."""
    return {
        "success": False,
        "error": {"code": code, "message": message, "details": details or {}},
    }

def setup_cors(app: FastAPI) -> None:
    """Configure CORS middleware for the application."""
    if settings.BACKEND_CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        logger.info("CORS middleware configured")

def setup_routers(app: FastAPI) -> None:
    """Configure API routers for the application."""
    # Add legacy router
    logger.info("Including the legacy api_router")
    app.include_router(legacy_api_router, prefix=settings.API_V1_STR)

    # Add new router
    logger.info("Including the new API router")
    app.include_router(new_api_router, prefix=settings.API_V1_STR)

def setup_middleware(app: FastAPI) -> None:
    """Configure middleware for the application."""
    # Set up error handling middleware
    setup_error_handling(app)

    # Add request logging middleware
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        logger.info(f"Request: {request.method} {request.url}")
        response = await call_next(request)
        logger.info(f"Response: Status {response.status_code}")
        return response

def setup_exception_handlers(app: FastAPI) -> None:
    """Configure exception handlers for the application."""
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

def setup_endpoints(app: FastAPI) -> None:
    """Configure basic endpoints for the application."""
    @app.get("/")
    async def root():
        """Root endpoint to provide a welcome message."""
        logger.info("Root endpoint accessed")
        return {"message": "Welcome to the ADHD Calendar API"}

    @app.get("/api/health", tags=["health"])
    async def health():
        """Health check endpoint."""
        return {"status": "ok"}

    @app.get("/health", tags=["Health"])
    async def health_check():
        """Health check endpoint."""
        return {"status": "ok"}

def setup_event_handlers(app: FastAPI) -> None:
    """Configure event handlers for the application."""
    @app.on_event("startup")
    async def startup_event():
        logger.info("Starting up and initializing database schema")
        await create_db_and_tables()
        logger.info("Database initialized")

    @app.on_event("shutdown")
    async def shutdown_event():
        logger.info("Shutting down FastAPI application")

def create_app() -> FastAPI:
    """
    Factory function to create and configure the FastAPI app instance.
    """
    # Create FastAPI application
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description="API for ADHD Calendar backend with advanced ML features",
        version=settings.APP_VERSION,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
    )

    # Setup application components
    setup_cors(app)
    setup_routers(app)
    setup_middleware(app)
    setup_exception_handlers(app)
    setup_endpoints(app)
    setup_event_handlers(app)

    return app

# Create the application instance
app = create_app()

def get_app() -> FastAPI:
    """Return the application instance for ASGI servers."""
    return app
