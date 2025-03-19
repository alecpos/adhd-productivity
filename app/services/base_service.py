"""Base service module for common CRUD operations."""

from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Tuple, Callable
from uuid import UUID
import asyncio
import logging
from functools import wraps

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy.exc

from app.core.exceptions import ServiceError

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

ModelType = TypeVar("ModelType")
SchemaType = TypeVar("SchemaType")
CreateSchemaType = TypeVar("CreateSchemaType")
T = TypeVar("T")

class BaseService(Generic[ModelType, SchemaType, CreateSchemaType]):
    """Base service class with common CRUD operations."""

    def __init__(self, db: AsyncSession, model: Type[ModelType], schema_class: Type[SchemaType]):
        """Initialize service with database session, model class, and schema class."""
        self.db = db
        self.model = model
        self.schema_class = schema_class

    async def _with_retry(
        self,
        operation: Callable[..., T],
        max_retries: int = 3,
        initial_delay: float = 0.05,
        max_delay: float = 0.5,
        backoff_factor: float = 1.5,
        retry_exceptions: Tuple = (
            sqlalchemy.exc.OperationalError,
            sqlalchemy.exc.InternalError,
            sqlalchemy.exc.DBAPIError,
            sqlalchemy.exc.TimeoutError,
            asyncio.TimeoutError,
        ),
        error_message: Optional[str] = None,
    ) -> T:
        """Execute an async operation with exponential backoff retry logic."""
        retry_count = 0
        delay = initial_delay
        last_exception = None

        while retry_count <= max_retries:
            try:
                return await asyncio.wait_for(operation(), timeout=1.0)
            except retry_exceptions as e:
                error_str = str(e).lower()
                concurrency_errors = [
                    "deadlock",
                    "lock timeout",
                    "could not obtain lock",
                    "duplicate key",
                    "serialization failure",
                    "timeout",
                ]

                is_retryable = isinstance(e, asyncio.TimeoutError) or any(err in error_str for err in concurrency_errors)
                if not is_retryable:
                    raise

                last_exception = e
                retry_count += 1

                if retry_count > max_retries:
                    raise ServiceError(f"Max retries ({max_retries}) exceeded. Last error: {error_str}")

                matched_error = "timeout" if isinstance(e, asyncio.TimeoutError) else next(
                    (err for err in concurrency_errors if err in error_str), "unknown"
                )
                log_message = error_message or f"Operation failed due to {matched_error}"
                logger.warning(f"{log_message} (Attempt {retry_count}/{max_retries})")

                delay = min(delay * backoff_factor, max_delay)
                await asyncio.sleep(delay)

        if last_exception:
            raise last_exception
        raise ServiceError("Operation failed after retries")

    @staticmethod
    def with_concurrency_control(
        max_retries: int = 3,
        initial_delay: float = 0.05,
        max_delay: float = 0.5,
        backoff_factor: float = 1.5,
        retry_exceptions: Tuple = (
            sqlalchemy.exc.OperationalError,
            sqlalchemy.exc.InternalError,
            sqlalchemy.exc.DBAPIError,
            sqlalchemy.exc.TimeoutError,
            asyncio.TimeoutError,
        ),
        error_message: Optional[str] = None,
    ):
        """Decorator for adding retry logic to async methods."""
        def decorator(func: Callable[..., T]) -> Callable[..., T]:
            @wraps(func)
            async def wrapper(*args, **kwargs) -> T:
                async def operation():
                    return await func(*args, **kwargs)

                service_instance = args[0]  # Get the service instance from the method call
                return await service_instance._with_retry(
                    operation=operation,
                    max_retries=max_retries,
                    initial_delay=initial_delay,
                    max_delay=max_delay,
                    backoff_factor=backoff_factor,
                    retry_exceptions=retry_exceptions,
                    error_message=error_message,
                )
            return wrapper
        return decorator

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[SchemaType]:
        """Get all items with pagination."""
        try:
            result = await self.db.execute(
                select(self.model).offset(skip).limit(limit)
            )
            items = list(result.scalars().all())
            return [self.schema_class.from_orm(item) for item in items]
        except Exception as e:
            raise ServiceError(f"Error retrieving items: {str(e)}")

    async def get_by_id(self, id: UUID) -> Optional[ModelType]:
        """Get item by ID."""
        try:
            result = await self.db.execute(
                select(self.model).where(self.model.id == id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            raise ServiceError(f"Error retrieving item: {str(e)}")

    @with_concurrency_control()
    async def create(self, data: CreateSchemaType) -> SchemaType:
        """Create a new item with concurrency control."""
        try:
            item = self.model(**data.dict())
            self.db.add(item)
            await self.db.commit()
            await self.db.refresh(item)
            return self.schema_class.from_orm(item)
        except Exception as e:
            await self.db.rollback()
            raise ServiceError(f"Error creating item: {str(e)}")

    @with_concurrency_control()
    async def update(self, id: UUID, data: Dict[str, Any]) -> Optional[SchemaType]:
        """Update an existing item with concurrency control."""
        try:
            item = await self.get_by_id(id)
            if not item:
                return None

            for key, value in data.items():
                setattr(item, key, value)

            await self.db.commit()
            await self.db.refresh(item)
            return self.schema_class.from_orm(item)
        except Exception as e:
            await self.db.rollback()
            raise ServiceError(f"Error updating item: {str(e)}")

    @with_concurrency_control()
    async def delete(self, id: UUID) -> bool:
        """Delete an item by ID with concurrency control."""
        try:
            item = await self.get_by_id(id)
            if not item:
                return False

            await self.db.delete(item)
            await self.db.commit()
            return True
        except Exception as e:
            await self.db.rollback()
            raise ServiceError(f"Error deleting item: {str(e)}")

    async def exists(self, id: UUID) -> bool:
        """Check if an item exists by ID."""
        try:
            result = await self.db.execute(
                select(self.model).where(self.model.id == id)
            )
            return result.scalar_one_or_none() is not None
        except Exception as e:
            raise ServiceError(f"Error checking item existence: {str(e)}")

    async def count(self) -> int:
        """Get total count of items."""
        try:
            result = await self.db.execute(
                select(self.model)
            )
            return len(result.scalars().all())
        except Exception as e:
            raise ServiceError(f"Error counting items: {str(e)}")

    async def get_by_field(self, field: str, value: Any) -> Optional[SchemaType]:
        """Get item by a specific field value."""
        try:
            result = await self.db.execute(
                select(self.model).where(getattr(self.model, field) == value)
            )
            item = result.scalar_one_or_none()
            return self.schema_class.from_orm(item) if item else None
        except Exception as e:
            raise ServiceError(f"Error retrieving item by field: {str(e)}")

    async def get_many_by_field(self, field: str, value: Any) -> List[SchemaType]:
        """Get multiple items by a specific field value."""
        try:
            result = await self.db.execute(
                select(self.model).where(getattr(self.model, field) == value)
            )
            items = list(result.scalars().all())
            return [self.schema_class.from_orm(item) for item in items]
        except Exception as e:
            raise ServiceError(f"Error retrieving items by field: {str(e)}")
