"""Core exceptions module."""

from fastapi import HTTPException, status


class BaseAPIException(HTTPException):
    """Base API exception."""

    def __init__(self, status_code: int, detail: str):
        """Initialize the exception."""
        super().__init__(status_code=status_code, detail=detail)


class ServiceError(BaseAPIException):
    """Service layer error."""

    def __init__(self, detail: str = "Service operation failed"):
        """Initialize the exception."""
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)


class ServiceException(Exception):
    """Generic service exception not tied to HTTP status codes."""
    
    def __init__(self, message: str = "Service operation failed"):
        """Initialize the exception with a descriptive message."""
        super().__init__(message)
        self.message = message


class NotFoundException(BaseAPIException):
    """Not found exception."""

    def __init__(self, detail: str = "Resource not found"):
        """Initialize the exception."""
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class UnauthorizedException(BaseAPIException):
    """Unauthorized exception."""

    def __init__(self, detail: str = "Not authorized"):
        """Initialize the exception."""
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class ForbiddenException(BaseAPIException):
    """Forbidden exception."""

    def __init__(self, detail: str = "Access forbidden"):
        """Initialize the exception."""
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class BadRequestException(BaseAPIException):
    """Bad request exception."""

    def __init__(self, detail: str = "Bad request"):
        """Initialize the exception."""
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class ConflictException(BaseAPIException):
    """Conflict exception."""

    def __init__(self, detail: str = "Resource conflict"):
        """Initialize the exception."""
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


class IntegrationError(BaseAPIException):
    """Exception raised when there is an error with external service integration."""

    def __init__(self, detail: str = "Integration error occurred"):
        """Initialize the exception."""
        super().__init__(status_code=status.HTTP_502_BAD_GATEWAY, detail=detail)
