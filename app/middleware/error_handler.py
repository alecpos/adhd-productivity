"""
Error Handling Middleware

This module provides a global error handling middleware for the ADHD Calendar API.
It ensures consistent error responses across all API endpoints.
"""

import traceback
from typing import Callable, Dict, List, Union

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

from app.utils.api_responses import (
    create_error_response,
    format_validation_errors,
)
from app.utils.logging import get_logger

logger = get_logger(__name__)


class ErrorHandlerMiddleware:
    """
    Middleware for handling errors and formatting standardized error responses.
    """

    def __init__(self, app: FastAPI):
        """
        Initialize the middleware.
        
        Args:
            app: The FastAPI application
        """
        self.app = app
        self._setup_exception_handlers()

    def _setup_exception_handlers(self) -> None:
        """Set up exception handlers for common exception types."""
        
        # Handle Pydantic validation errors
        @self.app.exception_handler(RequestValidationError)
        async def validation_exception_handler(
            request: Request, exc: RequestValidationError
        ) -> JSONResponse:
            return self._handle_validation_error(request, exc)

        # Handle SQLAlchemy no result found errors
        @self.app.exception_handler(NoResultFound)
        async def no_result_exception_handler(
            request: Request, exc: NoResultFound
        ) -> JSONResponse:
            return self._handle_not_found_error(request, exc)

        # Handle integrity errors (conflicts)
        @self.app.exception_handler(IntegrityError)
        async def integrity_exception_handler(
            request: Request, exc: IntegrityError
        ) -> JSONResponse:
            return self._handle_integrity_error(request, exc)

        # Handle generic server errors
        @self.app.exception_handler(Exception)
        async def general_exception_handler(
            request: Request, exc: Exception
        ) -> JSONResponse:
            return self._handle_server_error(request, exc)

    def _handle_validation_error(
        self, request: Request, exc: Union[RequestValidationError, ValidationError]
    ) -> JSONResponse:
        """
        Handle validation errors and format a standardized response.
        
        Args:
            request: The request that caused the error
            exc: The validation error
            
        Returns:
            A formatted error response
        """
        # Log the error
        logger.warning(
            f"Validation error for {request.method} {request.url.path}: {exc}"
        )
        
        # Format the errors into field-specific messages
        errors = format_validation_errors(exc)
        
        # Create and return the error response
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=create_error_response(
                code="VALIDATION_ERROR",
                message="Invalid request parameters",
                details=errors,
            ),
        )

    def _handle_not_found_error(
        self, request: Request, exc: NoResultFound
    ) -> JSONResponse:
        """
        Handle not found errors and format a standardized response.
        
        Args:
            request: The request that caused the error
            exc: The not found error
            
        Returns:
            A formatted error response
        """
        # Log the error
        logger.info(
            f"Resource not found for {request.method} {request.url.path}: {exc}"
        )
        
        # Create and return the error response
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=create_error_response(
                code="NOT_FOUND",
                message="The requested resource was not found",
                status_code=status.HTTP_404_NOT_FOUND,
            ),
        )

    def _handle_integrity_error(
        self, request: Request, exc: IntegrityError
    ) -> JSONResponse:
        """
        Handle integrity errors and format a standardized response.
        
        Args:
            request: The request that caused the error
            exc: The integrity error
            
        Returns:
            A formatted error response
        """
        # Log the error
        logger.warning(
            f"Integrity error for {request.method} {request.url.path}: {exc}"
        )
        
        # Create and return the error response
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=create_error_response(
                code="RESOURCE_CONFLICT",
                message="The request conflicts with the current state of the resource",
                status_code=status.HTTP_409_CONFLICT,
            ),
        )

    def _handle_server_error(self, request: Request, exc: Exception) -> JSONResponse:
        """
        Handle generic server errors and format a standardized response.
        
        Args:
            request: The request that caused the error
            exc: The server error
            
        Returns:
            A formatted error response
        """
        # Log the error with traceback
        logger.error(
            f"Unexpected error for {request.method} {request.url.path}: {exc}",
            exc_info=True,
        )
        
        # Get stack trace for logging (not included in the response)
        trace = traceback.format_exc()
        logger.error(trace)
        
        # Create and return the error response
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=create_error_response(
                code="INTERNAL_ERROR",
                message="An unexpected error occurred",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            ),
        )


def setup_error_handling(app: FastAPI) -> None:
    """
    Set up error handling middleware for the FastAPI application.
    
    Args:
        app: The FastAPI application
    """
    ErrorHandlerMiddleware(app) 