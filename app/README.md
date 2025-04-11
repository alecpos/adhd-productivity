# App Directory

This directory contains the main backend application code for the ADHD Calendar project.

## Directory Structure

- **api/**: API endpoints and route handlers
- **core/**: Core application configurations and settings
- **database/**: Database-related modules and migrations
- **enums/**: Enumeration classes used throughout the application
- **exceptions/**: Custom exception classes
- **ml/**: Machine learning models and algorithms
  - Contains implementation of TPR Models, Time Estimation Engine, and Forgetfulness Mitigation
  - Includes the Hyperfold Temporal Attention Module
- **models/**: Database models/schemas
- **routes/**: API route definitions
- **schemas/**: Request/response data schemas
- **services/**: Business logic services
- **tests/**: Unit and integration tests
- **ui/**: User interface related code
- **utils/**: Utility functions and helpers

## Key Files

- **main.py**: Application entry point
- **database.py**: Database configuration and connection
- **auth.py**: Authentication-related functions

## Getting Started

To start the application, run the following from the project root:

```bash
python run.py
```

## Related Documentation

For more information on the app's components, refer to the following:
- [API Documentation](../docs/api_documentation.md)
- [ML Models Documentation](../docs/ml_models.md)
- [Database Schema](../docs/database_schema.md)
