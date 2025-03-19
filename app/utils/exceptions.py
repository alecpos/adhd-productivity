"""
Custom Exceptions

This module provides custom exceptions for the ADHD Calendar API.
These exceptions are used to standardize error handling across the application.
"""

from typing import Any, Dict, List, Optional


class BaseAPIException(Exception):
    """Base exception for all API exceptions."""
    
    status_code: int = 500
    error_code: str = "internal_server_error"
    default_message: str = "An internal server error occurred."
    
    def __init__(self, message: Optional[str] = None, **kwargs):
        """
        Initialize the exception.
        
        Args:
            message: The error message. Defaults to the default_message.
            **kwargs: Additional error details.
        """
        self.message = message or self.default_message
        self.details = kwargs
        super().__init__(self.message)


class ResourceNotFoundError(BaseAPIException):
    """Exception raised when a resource is not found."""
    
    status_code: int = 404
    error_code: str = "not_found"
    default_message: str = "The requested resource was not found."
    
    def __init__(
        self, 
        resource: Optional[str] = None, 
        resource_id: Optional[Any] = None, 
        message: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize the exception.
        
        Args:
            resource: The resource type that was not found.
            resource_id: The ID of the resource that was not found.
            message: A custom error message.
            **kwargs: Additional error details.
        """
        if resource and resource_id and not message:
            message = f"The {resource} with ID '{resource_id}' was not found."
        
        super().__init__(message, resource=resource, resource_id=resource_id, **kwargs)


class ForbiddenError(BaseAPIException):
    """Exception raised when a user is not authorized to perform an action."""
    
    status_code: int = 403
    error_code: str = "forbidden"
    default_message: str = "You do not have permission to perform this action."
    
    def __init__(self, message: Optional[str] = None, **kwargs):
        """
        Initialize the exception.
        
        Args:
            message: A custom error message.
            **kwargs: Additional error details.
        """
        super().__init__(message, **kwargs)


class ValidationCustomError(BaseAPIException):
    """Exception raised when request data validation fails."""
    
    status_code: int = 400
    error_code: str = "validation_error"
    default_message: str = "Invalid request parameters."
    
    def __init__(
        self, 
        errors: Dict[str, List[str]],
        message: Optional[str] = None, 
        **kwargs
    ):
        """
        Initialize the exception.
        
        Args:
            errors: A dictionary mapping field names to error messages.
            message: A custom error message.
            **kwargs: Additional error details.
        """
        super().__init__(message, **kwargs)
        self.errors = errors


class ConflictError(BaseAPIException):
    """Exception raised when there is a resource conflict."""
    
    status_code: int = 409
    error_code: str = "conflict"
    default_message: str = "A conflict occurred with an existing resource."
    
    def __init__(self, message: Optional[str] = None, **kwargs):
        """
        Initialize the exception.
        
        Args:
            message: A custom error message.
            **kwargs: Additional error details.
        """
        super().__init__(message, **kwargs)


class RateLimitError(BaseAPIException):
    """Exception raised when a rate limit is exceeded."""
    
    status_code: int = 429
    error_code: str = "rate_limit_exceeded"
    default_message: str = "Rate limit exceeded. Please try again later."
    
    def __init__(
        self, 
        retry_after: int,
        message: Optional[str] = None, 
        **kwargs
    ):
        """
        Initialize the exception.
        
        Args:
            retry_after: The number of seconds to wait before retrying.
            message: A custom error message.
            **kwargs: Additional error details.
        """
        super().__init__(message, **kwargs)
        self.retry_after = retry_after


class UnauthorizedError(BaseAPIException):
    """Exception raised when a user is not authenticated."""
    
    status_code: int = 401
    error_code: str = "unauthorized"
    default_message: str = "Authentication required."
    
    def __init__(self, message: Optional[str] = None, **kwargs):
        """
        Initialize the exception.
        
        Args:
            message: A custom error message.
            **kwargs: Additional error details.
        """
        super().__init__(message, **kwargs)


class PaymentRequiredError(BaseAPIException):
    """Exception raised when payment is required."""
    
    status_code: int = 402
    error_code: str = "payment_required"
    default_message: str = "Payment is required to access this resource."
    
    def __init__(self, message: Optional[str] = None, **kwargs):
        """
        Initialize the exception.
        
        Args:
            message: A custom error message.
            **kwargs: Additional error details.
        """
        super().__init__(message, **kwargs)


class TooManyRequestsError(BaseAPIException):
    """Exception raised when too many requests are made."""
    
    status_code: int = 429
    error_code: str = "too_many_requests"
    default_message: str = "Too many requests. Please try again later."
    
    def __init__(self, message: Optional[str] = None, **kwargs):
        """
        Initialize the exception.
        
        Args:
            message: A custom error message.
            **kwargs: Additional error details.
        """
        super().__init__(message, **kwargs)


class ServiceUnavailableError(BaseAPIException):
    """Exception raised when a service is unavailable."""
    
    status_code: int = 503
    error_code: str = "service_unavailable"
    default_message: str = "The service is currently unavailable. Please try again later."
    
    def __init__(self, message: Optional[str] = None, **kwargs):
        """
        Initialize the exception.
        
        Args:
            message: A custom error message.
            **kwargs: Additional error details.
        """
        super().__init__(message, **kwargs)


# Aliases for backward compatibility
ServiceError = BaseAPIException
NotFoundException = ResourceNotFoundError
AuthenticationError = UnauthorizedError
AuthorizationError = ForbiddenError
InvalidInputException = ValidationCustomError
ValidationError = ValidationCustomError
TimeoutError = ServiceUnavailableError
ExternalServiceError = ServiceUnavailableError
DatabaseError = BaseAPIException
