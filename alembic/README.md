# Alembic Directory

This directory contains database migration scripts and configuration for the ADHD Calendar application.

## Overview

The alembic directory manages database migrations using the Alembic migration tool for SQLAlchemy. Migrations allow for versioned database schema changes that can be applied or rolled back as needed.

## Directory Structure

- **versions/**: Contains individual migration scripts
- **env.py**: Alembic environment configuration
- **script.py.mako**: Template for generating new migration scripts
- **alembic.ini**: Alembic configuration file

## Migration Scripts

Migration scripts in the `versions/` directory follow a naming convention:

- Scripts are prefixed with a unique version identifier
- The identifier is followed by a descriptive name
- For example: `a1b2c3d4e5f6_add_user_table.py`

Each migration script contains:

- `upgrade()`: Function to apply changes to move to this version
- `downgrade()`: Function to revert changes to the previous version
- Revision identifiers and dependencies
- Optional description and comments

## Common Operations

### Creating a New Migration

To create a new migration:

```bash
# Autogenerate a migration based on model changes
alembic revision --autogenerate -m "Description of changes"

# Create an empty migration
alembic revision -m "Description of changes"
```

### Applying Migrations

To apply migrations:

```bash
# Upgrade to the latest version
alembic upgrade head

# Upgrade to a specific version
alembic upgrade a1b2c3d4e5f6

# Upgrade by a relative number of versions
alembic upgrade +2
```

### Rolling Back Migrations

To rollback migrations:

```bash
# Downgrade to the previous version
alembic downgrade -1

# Downgrade to a specific version
alembic downgrade a1b2c3d4e5f6

# Downgrade to the base (remove all migrations)
alembic downgrade base
```

### Viewing Migration Information

To view migration information:

```bash
# Show current version
alembic current

# Show migration history
alembic history

# Show migration history with details
alembic history -v
```

## Migration Best Practices

1. **Incremental Changes**: Make small, focused migrations rather than large schema changes
2. **Test Migrations**: Test both upgrade and downgrade paths
3. **Data Migrations**: Include data migrations alongside schema changes when necessary
4. **Backward Compatibility**: Ensure backward compatibility when possible
5. **Transaction Safety**: Ensure migrations are transaction-safe
6. **Documentation**: Include clear comments explaining complex migrations

## Configuration

The alembic configuration is defined in:

- **alembic.ini**: Base configuration file
- **env.py**: Python environment configuration

Key configuration settings include:

- Database connection URL (typically loaded from environment variables)
- Script location
- Template configuration
- Logging settings

## Integration with Application

The migration system is integrated with the application through:

- SQLAlchemy models defined in `app/models/`
- Base metadata imported from the application models
- Environment configuration in `env.py`

## Related Documentation

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [Database Schema](../docs/database_schema.md)
- [SQLAlchemy Models](../docs/sqlalchemy_models.md)
- [Migration Guide](../docs/migration_guide.md)
