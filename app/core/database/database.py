"""Database configuration module."""

import logging
from typing import AsyncGenerator

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

from app.core.config import settings
from app.models.base_model import Base

logger = logging.getLogger(__name__)
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DB_ECHO,
    future=True,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_POOL_MAX_OVERFLOW,
    pool_timeout=settings.DB_POOL_TIMEOUT,
    pool_recycle=settings.DB_POOL_RECYCLE,
    poolclass=QueuePool,
    pool_pre_ping=True,
)
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting async database sessions."""
    session = AsyncSessionLocal()
    logger.debug("Creating new database session")
    try:
        await session.commit()
        logger.debug("Database session committed successfully")
    except SQLAlchemyError as e:
        await session.rollback()
        logger.error(f"Database session rolled back due to error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error occurred") from e
    except Exception as e:
        await session.rollback()
        logger.error(f"Unexpected error in database session: {str(e)}")
    finally:
        await session.close()
        logger.debug("Database session closed")


async def verify_database_connection() -> bool:
    """Verify database connection is working."""
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
            logger.info("Database connection verified successfully")
    except DBAPIError as e:
        logger.error(f"Database connection verification failed: {str(e)}")


async def create_db_and_tables() -> None:
    """Create database and tables."""

    logger.info("Creating database and tables...")
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database and tables created successfully")
    except SQLAlchemyError as e:
        logger.error(f"SQLAlchemy error creating database and tables: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error creating database and tables: {str(e)}")


async def close_db_connection() -> None:
    """Close database connection."""
    logger.info("Closing database connection...")
    try:
        await engine.dispose()
        logger.info("Database connection closed successfully")
    except Exception as e:
        logger.error(f"Error closing database connection: {str(e)}")


async def check_db_health() -> dict:
    """Check database health and return status."""
    try:
        connection_ok = await verify_database_connection()
        pool_status = {
            "pool_size": engine.pool.size(),
            "checked_out": engine.pool.checkedout(),
            "overflow": engine.pool.overflow(),
        }
        return {
            "status": "healthy" if connection_ok else "unhealthy",
            "connection": "ok" if connection_ok else "failed",
            "pool": pool_status,
        }
    except Exception as e:
        logger.error(f"Error checking database health: {str(e)}")
        return {"status": "unhealthy", "error": str(e)}
