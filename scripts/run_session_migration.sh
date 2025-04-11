#!/bin/bash

# Exit on error
set -e

# Load environment variables
set -a
source .env
set +a

echo "Starting session model migration process..."

# Format database URL for pg_dump (remove async driver)
SYNC_DB_URL=$(echo $DATABASE_URL | sed 's/postgresql+asyncpg/postgresql/')
PG_URL=$(echo $SYNC_DB_URL | sed 's/postgresql:\/\///')
DB_NAME=$(echo $PG_URL | cut -d'/' -f2)
DB_HOST=$(echo $PG_URL | cut -d'/' -f1 | cut -d'@' -f2)
DB_HOST=${DB_HOST:-localhost}

# 1. Create database backup
echo "Creating database backup..."
PGPASSWORD=$POSTGRES_PASSWORD pg_dump -h $DB_HOST -U $POSTGRES_USER $DB_NAME > session_migration_backup.sql

# 2. Run alembic migration
echo "Running alembic migration..."
alembic upgrade head

# 3. Verify migration
echo "Verifying migration..."
python3 - << EOF
from sqlalchemy import create_engine, text
import os

# Use sync URL for verification
SYNC_DB_URL = os.getenv('DATABASE_URL').replace('postgresql+asyncpg', 'postgresql')
engine = create_engine(SYNC_DB_URL)

with engine.connect() as conn:
    # Check new tables exist
    tables = ['pomodoro_sessions', 'hyperfocus_sessions', 'body_doubling_sessions']
    for table in tables:
        result = conn.execute(text(f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '{table}')"))
        exists = result.scalar()
        if not exists:
            raise Exception(f"Table {table} not found!")
        print(f"✓ Table {table} exists")

        # Check data was migrated
        count = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
        print(f"  - {count} records in {table}")

print("\nMigration verification complete!")
EOF

echo "Migration completed successfully!"
echo "Backup file created: session_migration_backup.sql"
