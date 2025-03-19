# Alembic Migration Guide

This guide provides detailed information about managing database migrations using Alembic in the ADHD Calendar application.

## Overview

Alembic is a database migration tool for SQLAlchemy that allows us to manage and track changes to our database schema over time. It provides a way to:

- Create new migrations
- Apply migrations to update the database schema
- Revert migrations when needed
- Track the migration history

## Migration Directory Structure

The migration system is located in the `alembic/` directory at the root of the project:

- `alembic/versions/`: Contains individual migration scripts
- `alembic/env.py`: Alembic environment configuration
- `alembic/script.py.mako`: Template for generating new migration scripts
- `alembic/alembic.ini`: Alembic configuration file

## Common Migration Tasks

### Setting Up Alembic

Alembic should already be set up for this project, but if you need to set it up in a new environment:

```bash
# Initialize a new Alembic environment
alembic init alembic

# Modify alembic/env.py to import your SQLAlchemy models
# Modify alembic.ini to point to your database URL
```

### Creating a New Migration

There are two ways to create a new migration:

#### 1. Auto-generate a migration

This method compares your SQLAlchemy model definitions to the current database schema and generates migrations automatically:

```bash
# Auto-generate a migration
alembic revision --autogenerate -m "Description of changes"
```

#### 2. Create an empty migration

This method creates an empty migration script that you can fill in manually:

```bash
# Create an empty migration
alembic revision -m "Description of changes"
```

### Reviewing a Generated Migration

Always review auto-generated migrations before applying them. Alembic may not correctly detect all changes, especially:

- Changes to constraints
- Alterations to existing columns
- Custom types
- Enum changes

### Applying Migrations

To apply migrations to your database:

```bash
# Upgrade to the latest version
alembic upgrade head

# Upgrade to a specific version
alembic upgrade revision_id

# Upgrade by a relative number of versions
alembic upgrade +3

# Upgrade to a specific version by its index in the history
alembic upgrade ae1027a6acf:546bc773ac2f
```

### Rolling Back Migrations

To roll back (downgrade) migrations:

```bash
# Downgrade to the previous version
alembic downgrade -1

# Downgrade to a specific version
alembic downgrade revision_id

# Downgrade by a relative number of versions
alembic downgrade -3

# Downgrade to the base (remove all migrations)
alembic downgrade base
```

### Viewing Migration Information

To get information about migrations:

```bash
# Show current version
alembic current

# Show migration history
alembic history

# Show migration history with details
alembic history -v

# Show more migration history (not truncated)
alembic history --verbose
```

## Writing Migration Scripts

### Migration Script Structure

Each migration script contains:

```python
"""Description of changes

Revision ID: a1b2c3d4e5f6
Revises: previous_revision_id
Create Date: 2023-01-01 12:00:00.000000

"""

# revision identifiers, used by Alembic
revision = 'a1b2c3d4e5f6'
down_revision = 'previous_revision_id'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    # Implementation for upgrading to this version
    pass

def downgrade():
    # Implementation for downgrading from this version
    pass
```

### Common Operations in Migration Scripts

#### Creating Tables

```python
def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=128), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
```

#### Adding Columns

```python
def upgrade():
    op.add_column('users', sa.Column('full_name', sa.String(length=255), nullable=True))
```

#### Removing Columns

```python
def upgrade():
    op.drop_column('users', 'temp_field')
```

#### Altering Columns

```python
def upgrade():
    op.alter_column('users', 'email', 
                    existing_type=sa.String(length=255),
                    type_=sa.String(length=320),
                    nullable=False)
```

#### Adding Indexes

```python
def upgrade():
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
```

#### Adding Foreign Keys

```python
def upgrade():
    op.create_foreign_key(
        'fk_tasks_user_id', 'tasks', 'users',
        ['user_id'], ['id'], ondelete='CASCADE'
    )
```

## Best Practices

1. **Small, Focused Migrations**: Create small, focused migrations rather than large schema changes.
2. **Test Migrations**: Test both upgrade and downgrade paths.
3. **Data Migrations**: Include data migrations alongside schema changes when necessary.
4. **Backward Compatibility**: Ensure backward compatibility when possible.
5. **Transaction Safety**: Ensure migrations are transaction-safe.
6. **Documentation**: Include clear comments explaining complex migrations.
7. **Review Auto-Generated Migrations**: Always review and test auto-generated migrations.
8. **Versioning**: Keep migrations in version control along with your code.

## Handling Complex Migrations

For complex migrations, consider:

1. **Split Into Multiple Migrations**: Break down complex changes into smaller, sequential migrations.
2. **Data Migration Strategies**: 
   - For large tables, consider batching data migrations.
   - For sensitive operations, consider using temporary tables.
3. **Testing**: Create test cases for complex migrations.

## Troubleshooting

### Common Issues

1. **Migration Conflicts**: If multiple developers create migrations at the same branch point, use `alembic merge` to resolve.
2. **Failed Migrations**: If a migration fails partway through, you may need to manually fix the database state.
3. **Version Inconsistencies**: If the database version doesn't match what Alembic expects, you may need to manually set the version.

### Fixing the Migration History

If the migration history is out of sync:

```bash
# Stamp the database with a specific version
alembic stamp revision_id

# Stamp the database with the current revision
alembic stamp head
```

## Related Resources

- [SQLAlchemy Models](./sqlalchemy_models.md)
- [Database Schema](./database_schema.md)
- [Official Alembic Documentation](https://alembic.sqlalchemy.org/en/latest/) 