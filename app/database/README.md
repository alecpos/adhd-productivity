# Database Directory

This directory contains database-related modules and migrations for the ADHD Calendar backend.

## Overview

The database directory handles database connections, session management, and migrations. It provides a centralized place for database-related functionality that's used throughout the application.

## Components

- **session.py**: Database session management
- **base.py**: Base class for SQLAlchemy models
- **repositories/**: Repository pattern implementations for data access
- **migrations/**: Database migration scripts
- **seeders/**: Data seeding scripts for development and testing
- **utils.py**: Database utility functions

## Repository Pattern

This application uses the repository pattern to abstract data access:

- Repositories provide a clean API for data access operations
- Each model has a corresponding repository
- Repositories handle query construction and execution
- Services use repositories rather than direct database access

## Migrations

Database migrations are managed using Alembic:

- Migration scripts are located in `migrations/versions/`
- The migration environment is configured in `migrations/env.py`
- Migration scripts are generated and executed using Alembic commands

## Connection Management

Database connections are managed through:

- Connection pooling for efficient resource usage
- Session lifecycle management
- Transaction handling

## Usage Example

```python
from app.database.session import get_db
from app.database.repositories.user_repository import UserRepository

# Using a database session
def get_user_by_id(user_id: int):
    db = next(get_db())
    repository = UserRepository(db)
    return repository.get_by_id(user_id)
```

## Development Guidelines

When working with database components:

1. Always use migrations for schema changes
2. Use repositories for data access operations
3. Ensure proper transaction handling
4. Consider performance implications of queries
5. Write tests for database operations

## Related Documentation

- [Database Schema](../../docs/database_schema.md)
- [Alembic Migration Guide](../../docs/alembic_guide.md)
- [Repository Pattern Implementation](../../docs/repository_pattern.md)
