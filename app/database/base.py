"""Base module for database operations."""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Tuple, Type, TypeVar, Union

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

logger = logging.getLogger(__name__)

# Create the SQLAlchemy base
Base = declarative_base()

# Import models after Base is created
# Instead of importing specific models here that might cause circular imports,
# we'll leave it to the engine initialization code to ensure models are loaded
# when needed.

# Create async engine
def create_engine():
    """Create SQLAlchemy engine with settings."""
    engine = create_async_engine(
        settings.SQLALCHEMY_DATABASE_URI,
        echo=settings.DB_ECHO,
        pool_pre_ping=True,
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_MAX_OVERFLOW,
    )
    return engine

# Define session
def create_session_factory(engine):
    """Create session factory."""
    session_factory = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    return session_factory