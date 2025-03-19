# Exceptions Directory

This directory contains custom exception classes for the ADHD Calendar application.

## Overview

The exceptions directory defines custom exception classes that are used throughout the application to represent specific error conditions. These exceptions help provide clear error messages and appropriate HTTP status codes for API responses.

## Exception Categories

### API Exceptions

- **APIException**: Base class for all API-related exceptions
- **NotFoundException**: Resource not found
- **ValidationException**: Request validation failed
- **AuthenticationException**: Authentication failed
- **AuthorizationException**: User not authorized for action
- **RateLimitException**: Rate limit exceeded

### Database Exceptions

- **DatabaseException**: Base class for database-related exceptions
- **UniqueViolationException**: Unique constraint violated
- **ForeignKeyViolationException**: Foreign key constraint violated
- **IntegrityException**: Database integrity constraint violated

### Service Exceptions

- **ServiceException**: Base class for service-related exceptions
- **ExternalServiceException**: External service or API failure
- **ServiceUnavailableException**: Service temporarily unavailable
- **BusinessRuleException**: Business rule violated

### ML Exceptions

- **MLException**: Base class for ML-related exceptions
- **ModelNotTrainedException**: ML model not trained
- **InferenceException**: Error during model inference
- **DataQualityException**: Data quality issue for ML processing

## Exception Structure

Custom exceptions typically include:

- HTTP status code
- Error code (for client identification)
- Error message
- Additional context or details

## Usage Example

```python
from app.exceptions.api_exceptions import NotFoundException
from app.exceptions.handler import handle_exception

try:
    user = get_user_by_id(user_id)
    if not user:
        raise NotFoundException(
            message=f"User with ID {user_id} not found",
            error_code="USER_NOT_FOUND"
        )
    return user
except Exception as e:
    return handle_exception(e)
```

## Exception Handling

Exceptions are handled centrally through exception handlers:

- FastAPI exception handlers registered in `app/api/dependencies/error_handlers.py`
- Each exception maps to an appropriate HTTP response
- Structured error responses for consistent client handling

## Development Guidelines

When working with exceptions:

1. Create specific exception classes for different error types
2. Include descriptive error messages
3. Add appropriate HTTP status codes
4. Use error codes for programmatic client handling
5. Document exceptions raised by functions and methods

## Related Documentation

- [Error Handling Guide](../../docs/error_handling_guide.md)
- [API Error Responses](../../docs/api_error_responses.md) 