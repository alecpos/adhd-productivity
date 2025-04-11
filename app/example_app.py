"""
Example Application Entry Point

This module demonstrates how to set up a FastAPI application with middleware,
routes, and configuration following the API design guidelines.
This is an example file and is not meant to be used in production.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.middleware.error_handler import setup_error_handling
from app.routes.example_task_route import router as task_router

def create_application() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns:
        The configured FastAPI application
    """
    # Create FastAPI app
    app = FastAPI(
        title="ADHD Calendar API",
        description="API for managing ADHD-friendly calendar and task management",
        version="1.0.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
    )

    # Set up CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "https://adhdcalendar.com"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Set up error handling middleware
    setup_error_handling(app)

    # Include routes with prefix
    app.include_router(task_router, prefix="/api/v1")

    # Add a simple health check endpoint
    @app.get("/health", tags=["Health"])
    async def health_check():
        return {"status": "ok"}

    return app


# This would be used in a real application
# app = create_application()

# Example usage
"""
To use this code:

1. Create a file named 'app.py' with this content:

from app.example_app import create_application

app = create_application()

2. Run the application with uvicorn:

uvicorn app:app --reload

3. Access the API docs at:

http://localhost:8000/api/docs
"""
