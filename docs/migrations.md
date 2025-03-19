# Database Migration Documentation

## Overview

This document details the database migration process for the ADHD Calendar Backend.

## Migration Architecture

### Alembic Setup

The project uses Alembic for database migrations:
- Version control for database schema
- Automated migration generation
- Migration history tracking
- Rollback support
- Dependency resolution

### Migration Directory Structure

```
alembic/
├── versions/
│   ├── 001_initial.py
│   ├── 002_add_user_preferences.py
│   └── 003_task_relationships.py
├── env.py
└── alembic.ini
```

## Migration Process

### Creating Migrations

#### Automatic Generation

Generate migrations from model changes:

```bash
alembic revision --autogenerate -m "Add user preferences"
```

#### Manual Creation

Create empty migration:

```bash
alembic revision -m "Custom migration"
```

### Migration Structure

```python
"""Add user preferences

Revision ID: abc123def456
Revises: 98765ghi4321
Create Date: 2024-01-01 12:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

def upgrade():
    """Upgrade to this version."""
    op.create_table(
        'user_preferences',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('timezone', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    """Downgrade from this version."""
    op.drop_table('user_preferences')
```

## Migration Operations

### Table Operations

Create and modify tables:

```python
# Create table
op.create_table(
    'tasks',
    sa.Column('id', sa.Integer(), primary_key=True),
    sa.Column('title', sa.String(), nullable=False)
)

# Alter table
op.alter_column('tasks', 'title',
    existing_type=sa.String(),
    type_=sa.Text(),
    nullable=False
)

# Drop table
op.drop_table('old_tasks')
```

### Column Operations

Manage table columns:

```python
# Add column
op.add_column('users',
    sa.Column('email', sa.String())
)

# Modify column
op.alter_column('users', 'email',
    existing_type=sa.String(),
    nullable=False
)

# Drop column
op.drop_column('users', 'old_field')
```

### Index Operations

Manage database indexes:

```python
# Create index
op.create_index(
    'idx_user_email',
    'users',
    ['email'],
    unique=True
)

# Drop index
op.drop_index('idx_user_email')
```

## Data Migration

### Bulk Data Updates

Update existing data:

```python
def upgrade():
    connection = op.get_bind()
    
    # Update all task priorities
    connection.execute(
        sa.text("""
        UPDATE tasks
        SET priority = 'medium'
        WHERE priority IS NULL
        """)
    )
```

### Complex Migrations

Handle complex data transformations:

```python
def upgrade():
    connection = op.get_bind()
    
    # Get existing data
    tasks = connection.execute(
        sa.text("SELECT * FROM old_tasks")
    ).fetchall()
    
    # Transform and insert data
    for task in tasks:
        connection.execute(
            sa.text("""
            INSERT INTO new_tasks (id, title, status)
            VALUES (:id, :title, :status)
            """),
            {
                "id": task.id,
                "title": task.name,  # Field renamed
                "status": "active"  # New field
            }
        )
```

## Migration Management

### Running Migrations

```bash
# Apply all pending migrations
alembic upgrade head

# Upgrade to specific version
alembic upgrade abc123def456

# Downgrade to previous version
alembic downgrade -1

# Downgrade to base
alembic downgrade base
```

### Migration History

```bash
# View migration history
alembic history

# View current version
alembic current

# View migration SQL
alembic upgrade head --sql
```

## Best Practices

### Migration Design

1. Make migrations atomic
2. Include both upgrade and downgrade
3. Test migrations thoroughly
4. Document complex migrations
5. Handle data preservation

### Performance

1. Use batch operations
2. Consider table size
3. Handle long-running migrations
4. Plan maintenance windows
5. Monitor system resources

### Safety

1. Backup before migrating
2. Test in staging first
3. Plan rollback strategy
4. Monitor errors
5. Validate data integrity

## Testing

### Migration Tests

Test migration functionality:

```python
def test_migration_upgrade():
    """Test migration upgrade path."""
    # Apply migration
    alembic.command.upgrade(config, "head")
    
    # Verify schema
    inspector = inspect(engine)
    assert "user_preferences" in inspector.get_table_names()
```

### Data Tests

Test data integrity:

```python
def test_data_migration():
    """Test data transformation."""
    # Apply migration
    alembic.command.upgrade(config, "target_revision")
    
    # Verify data
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM new_tasks"))
        assert result.rowcount > 0
```

## Troubleshooting

### Common Issues

1. Migration conflicts
2. Data integrity errors
3. Performance problems
4. Dependency issues
5. Rollback failures

### Solutions

1. Resolve revision conflicts
2. Validate data before migration
3. Optimize long-running migrations
4. Fix dependency ordering
5. Test rollback procedures

## Monitoring

### Migration Metrics

Monitor migration performance:

```python
def upgrade():
    with metrics.timer("migration_duration"):
        # Perform migration
        op.create_table(...)
```

### Health Checks

Verify database health:

```python
def check_migration_health():
    """Check migration status."""
    return {
        "current_revision": current_head(),
        "pending_migrations": get_pending(),
        "last_migration_time": get_last_run()
    }
``` 