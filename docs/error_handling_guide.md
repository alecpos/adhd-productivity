# Error Handling Guide

## Overview

This document outlines the error handling approach for the ADHD Calendar API. Consistent error handling ensures that clients can reliably interpret and respond to errors.

## Error Response Structure

All API error responses follow this structure:

```json
{
    "status": "error",
    "code": "ERROR_CODE",
    "message": "A human-readable error message",
    "details": {
        "field1": ["Error details related to field1"],
        "field2": ["Error details related to field2"]
    }
}
```

### Fields

- **status**: Always "error" for error responses
- **code**: A unique error code for programmatic handling
- **message**: A human-readable description of the error
- **details**: Object containing field-specific errors (for validation errors)

## HTTP Status Codes

The API uses standard HTTP status codes to indicate the success or failure of a request:

### Success Codes

- **200 OK**: The request was successful
- **201 Created**: A new resource was successfully created
- **204 No Content**: The request was successful but there's no content to return

### Client Error Codes

- **400 Bad Request**: Invalid request parameters
- **401 Unauthorized**: Authentication required or failed
- **403 Forbidden**: Authentication succeeded but the user doesn't have permission
- **404 Not Found**: The requested resource was not found
- **409 Conflict**: The request conflicts with the current state (e.g., duplicate resource)
- **422 Unprocessable Entity**: The server understood the request but can't process it
- **429 Too Many Requests**: Rate limit exceeded

### Server Error Codes

- **500 Internal Server Error**: An unexpected error occurred on the server
- **502 Bad Gateway**: The server received an invalid response from an upstream server
- **503 Service Unavailable**: The server is temporarily unavailable
- **504 Gateway Timeout**: The server timed out waiting for an upstream service

## Error Codes

The API uses the following error codes for programmatic handling:

### Authentication Errors

- **UNAUTHORIZED**: User is not authenticated
- **INVALID_CREDENTIALS**: Provided credentials are incorrect
- **TOKEN_EXPIRED**: Authentication token has expired
- **TOKEN_INVALID**: Authentication token is invalid

### Authorization Errors

- **FORBIDDEN**: User doesn't have permission for the requested resource
- **INSUFFICIENT_PERMISSIONS**: User lacks specific permissions required
- **RESOURCE_OWNER_MISMATCH**: User is not the owner of the requested resource

### Validation Errors

- **VALIDATION_ERROR**: Request data failed validation
- **MISSING_REQUIRED_FIELD**: A required field is missing
- **INVALID_FORMAT**: Field format is invalid
- **INVALID_VALUE**: Field value is invalid
- **CONSTRAINT_VIOLATION**: A database constraint was violated

### Resource Errors

- **NOT_FOUND**: The requested resource was not found
- **RESOURCE_EXISTS**: Attempt to create a resource that already exists
- **RESOURCE_CONFLICT**: The request conflicts with the current state
- **RESOURCE_GONE**: The resource once existed but is no longer available

### Rate Limiting Errors

- **RATE_LIMIT_EXCEEDED**: Too many requests in a given time frame

### Server Errors

- **INTERNAL_ERROR**: An unexpected server error occurred
- **SERVICE_UNAVAILABLE**: The service is temporarily unavailable
- **DEPENDENCY_ERROR**: Error in a dependent service

## Example Error Responses

### Authentication Error

```http
HTTP/1.1 401 Unauthorized
Content-Type: application/json

{
    "status": "error",
    "code": "TOKEN_EXPIRED",
    "message": "Authentication token has expired",
    "details": {}
}
```

### Validation Error

```http
HTTP/1.1 400 Bad Request
Content-Type: application/json

{
    "status": "error",
    "code": "VALIDATION_ERROR",
    "message": "Invalid request parameters",
    "details": {
        "title": ["Title is required"],
        "dueDate": ["Due date must be in the future"],
        "priority": ["Priority must be one of: 'low', 'medium', 'high'"]
    }
}
```

### Resource Not Found Error

```http
HTTP/1.1 404 Not Found
Content-Type: application/json

{
    "status": "error",
    "code": "NOT_FOUND",
    "message": "Task with ID '123e4567-e89b-12d3-a456-426614174000' not found",
    "details": {}
}
```

### Rate Limit Error

```http
HTTP/1.1 429 Too Many Requests
Content-Type: application/json
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1680278400

{
    "status": "error",
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Try again after 2023-04-01T00:00:00Z",
    "details": {}
}
```

## Handling Validation Errors

Validation errors are returned with a 400 status code and include detailed information about each field that failed validation:

```json
{
    "status": "error",
    "code": "VALIDATION_ERROR",
    "message": "Invalid request parameters",
    "details": {
        "title": [
            "Title is required",
            "Title must be between 3 and 100 characters"
        ],
        "dueDate": [
            "Due date must be in the future"
        ],
        "estimatedDuration": [
            "Estimated duration must be a positive number"
        ]
    }
}
```

The `details` object contains field names as keys and arrays of error messages as values. Multiple validation errors can be included for a single field.

## Error Handling Best Practices for API Clients

### Parse the Error Code

Always check the `code` field for programmatic handling of errors:

```javascript
if (error.code === 'TOKEN_EXPIRED') {
  // Refresh the token
} else if (error.code === 'VALIDATION_ERROR') {
  // Display validation errors to the user
}
```

### Display Field-Specific Errors

For validation errors, display field-specific error messages alongside the relevant form fields:

```javascript
if (error.code === 'VALIDATION_ERROR') {
  Object.entries(error.details).forEach(([field, messages]) => {
    const errorElement = document.getElementById(`${field}-error`);
    if (errorElement) {
      errorElement.textContent = messages[0];
      errorElement.style.display = 'block';
    }
  });
}
```

### Implement Retry Logic

For certain server errors (e.g., 503 Service Unavailable), implement retry logic with exponential backoff:

```javascript
async function fetchWithRetry(url, options, maxRetries = 3) {
  let retries = 0;
  while (retries < maxRetries) {
    try {
      const response = await fetch(url, options);
      if (response.ok || response.status !== 503) {
        return response;
      }
    } catch (error) {
      console.error(`Attempt ${retries + 1} failed:`, error);
    }

    retries++;
    const delay = Math.pow(2, retries) * 1000; // Exponential backoff
    await new Promise(resolve => setTimeout(resolve, delay));
  }

  throw new Error(`Failed after ${maxRetries} retries`);
}
```

### Handle Authentication Errors

Implement logic to handle authentication errors (401) by redirecting to the login page or refreshing the token:

```javascript
if (error.status === 401) {
  if (error.code === 'TOKEN_EXPIRED') {
    try {
      await refreshToken();
      // Retry the original request
    } catch (refreshError) {
      // Redirect to login page
      window.location.href = '/login';
    }
  } else {
    // Redirect to login page
    window.location.href = '/login';
  }
}
```

## Implementation Guidelines for API Developers

### Consistent Error Structure

Ensure all API endpoints return errors in the standardized format described above.

### Proper Status Codes

Use the appropriate HTTP status code for each error scenario.

### Descriptive Messages

Provide clear, descriptive error messages that help the client understand what went wrong.

### Avoid Sensitive Information

Never include sensitive information (passwords, tokens, etc.) in error messages.

### Log Errors

Log all server errors with appropriate detail for debugging, but avoid logging sensitive data.

### Validate Input

Implement thorough input validation to catch errors early and provide helpful feedback.

### Handle Exceptions

Properly catch and handle exceptions to prevent exposing internal error details.

## Related Resources

- [API Documentation](./api_documentation.md)
- [API Design Guidelines](./api_design_guidelines.md)
- [Authentication Flow](./authentication_flow.md)
