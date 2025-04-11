"""Database configuration module."""

import logging
from typing import AsyncGenerator, Dict, Any, Optional

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# We should use BaseModel directly since it's our DeclarativeBase
from app.models.base_model import BaseModel

# Import all models to ensure proper table registration
from app.database.base import Base

logger = logging.getLogger(__name__)

# Determine if the database is SQLite
is_sqlite = "sqlite" in settings.DATABASE_URL


# Define pool arguments separately to reduce nesting
def get_engine_args() -> Dict[str, Any]:
    """Get database engine arguments based on database type."""
    common_args = {
        "echo": settings.DB_ECHO,
        "future": True,
        "pool_pre_ping": True,
    }

    if is_sqlite:
        return common_args

    # Add pool settings for non-SQLite databases
    pool_args = {
        "pool_size": settings.DB_POOL_SIZE,
        "max_overflow": settings.DB_POOL_MAX_OVERFLOW,
        "pool_timeout": settings.DB_POOL_TIMEOUT,
        "pool_recycle": settings.DB_POOL_RECYCLE,
    }

    return {**common_args, **pool_args}


# Create engine with appropriate arguments
engine = create_async_engine(settings.DATABASE_URL, **get_engine_args())

async_session_maker = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

__all__ = ["get_db", "async_session_maker", "Base"]


async def handle_sqlalchemy_error(session: AsyncSession, error: SQLAlchemyError) -> None:
    """Handle SQLAlchemy errors by rolling back transaction and logging."""
    await session.rollback()
    logger.error(f"Database session rolled back due to error: {str(error)}")
    raise HTTPException(status_code=500, detail="Database error occurred") from error


async def handle_generic_error(session: AsyncSession, error: Exception) -> None:
    """Handle generic errors by rolling back transaction and logging."""
    await session.rollback()
    logger.error(f"Unexpected error in database session: {str(error)}")
    raise


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting async database sessions."""
    session = async_session_maker()
    logger.debug("Creating new database session")

    try:
        yield session
    except SQLAlchemyError as e:
        await handle_sqlalchemy_error(session, e)
    except Exception as e:
        await handle_generic_error(session, e)
    finally:
        await session.close()
        logger.debug("Database session closed")


async def verify_database_connection() -> bool:
    """Verify database connection is working."""
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
            logger.info("Database connection verified successfully")
            return True
    except DBAPIError as e:
        logger.error(f"Database connection verification failed: {str(e)}")
        return False


async def create_db_and_tables() -> None:
    """Create database and tables."""
    logger.info("Creating database and tables...")

    try:
        async with engine.begin() as conn:
            # Use BaseModel to create tables since it's our DeclarativeBase
            await conn.run_sync(BaseModel.metadata.create_all)
        logger.info("Database and tables created successfully")
    except SQLAlchemyError as e:
        logger.error(f"SQLAlchemy error creating database and tables: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error creating database and tables: {str(e)}")
        raise


async def close_db_connection() -> None:
    """Close database connection."""
    logger.info("Closing database connection...")

    try:
        await engine.dispose()
        logger.info("Database connection closed successfully")
    except Exception as e:
        logger.error(f"Error closing database connection: {str(e)}")
        raise


def get_pool_status() -> Dict[str, int]:
    """Get database connection pool status."""
    try:
        return {
            "pool_size": engine.pool.size(),
            "checked_out": engine.pool.checkedout(),
            "overflow": engine.pool.overflow(),
        }
    except Exception as e:
        logger.error(f"Error getting pool status: {str(e)}")
        return {"error": True}


async def check_db_health() -> Dict[str, Any]:
    """Check database health and return status."""
    try:
        connection_ok = await verify_database_connection()
        pool_status = get_pool_status()

        return {
            "status": "healthy" if connection_ok else "unhealthy",
            "connection": "ok" if connection_ok else "failed",
            "pool": pool_status,
        }
    except Exception as e:
        logger.error(f"Error checking database health: {str(e)}")
        return {"status": "unhealthy", "error": str(e)}
