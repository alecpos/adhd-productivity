"""Custom exceptions for the application."""


class BaseAppException(Exception):
    """Base exception for all application exceptions."""

    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class InvalidInputException(BaseAppException):
    """Exception raised for invalid input."""

    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message=message, status_code=status_code)


class NotFoundException(BaseAppException):
    """Exception raised when a resource is not found."""

    def __init__(self, message: str = "Resource not found", status_code: int = 404):
        super().__init__(message=message, status_code=status_code)


class UnauthorizedException(BaseAppException):
    """Exception raised when a user is not authorized."""

    def __init__(self, message: str = "Unauthorized", status_code: int = 401):
        super().__init__(message=message, status_code=status_code)


class ServiceError(BaseAppException):
    """Exception raised for service-level errors."""

    def __init__(self, message: str = "Service error", status_code: int = 500):
        super().__init__(message=message, status_code=status_code)
