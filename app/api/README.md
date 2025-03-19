# API Directory

This directory contains API endpoint implementations for the ADHD Calendar backend.

## Purpose

The API directory implements RESTful endpoints that handle HTTP requests and responses for the ADHD Calendar application. It exposes functionality from the services layer to external clients, including the frontend application.

## Structure

- **endpoints/**: Individual API endpoint modules organized by resource type
- **dependencies/**: Shared dependencies for API endpoints
- **middlewares/**: Middleware components for request/response processing

## Key Features

- RESTful API implementation
- JWT authentication
- Request validation using Pydantic schemas
- Error handling and response formatting
- API versioning

## Usage

API endpoints are registered in the main FastAPI application in `app/main.py`. To add a new endpoint, create a new module in the appropriate subdirectory and register it with the application.

## Related Documentation

- [API Documentation](../../docs/api_documentation.md)
- [Authentication Guide](../../docs/authentication.md)
- [API Integration Examples](../../docs/api_integration_examples.md) 