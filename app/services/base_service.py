"""Base service module for common CRUD operations and resilience patterns."""

from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Tuple, Callable, Union
from uuid import UUID
import asyncio
import logging
import functools
import time
from datetime import datetime
from functools import wraps
from concurrent.futures import ThreadPoolExecutor

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

# Default circuit breaker states
CLOSED = "closed"      # Normal operation, requests go through
OPEN = "open"          # Failure threshold exceeded, requests fail fast
HALF_OPEN = "half-open"  # Testing if service is back online


class CircuitBreaker:
    """
    Circuit breaker implementation to prevent cascading failures.
    
    This class implements the circuit breaker pattern to prevent an application
    from repeatedly trying to execute an operation that's likely to fail.
    """
    
    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: int = 30,
        expected_exceptions: Tuple = (Exception,),
    ):
        """
        Initialize the circuit breaker.
        
        Args:
            name: A name for this circuit breaker (for logging)
            failure_threshold: Number of failures before opening the circuit
            recovery_timeout: Seconds to wait before trying to recover
            expected_exceptions: Exceptions that will increment the failure counter
        """
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exceptions = expected_exceptions
        
        # Circuit state
        self.state = CLOSED
        self.failure_count = 0
        self.last_failure_time = None
        
        logger.info(f"Circuit breaker '{name}' initialized with failure_threshold={failure_threshold}, "
                   f"recovery_timeout={recovery_timeout}")
        
    def __call__(self, func):
        """Make the circuit breaker callable as a decorator."""
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await self.call(func, *args, **kwargs)
        return wrapper
        
    async def call(self, func, *args, **kwargs):
        """
        Call the function with circuit breaker protection.
        
        This method checks the current state of the circuit before executing
        the wrapped function, potentially fast-failing if the circuit is open.
        """
        if self.state == OPEN:
            if self._should_attempt_recovery():
                logger.info(f"Circuit '{self.name}' transitioning from OPEN to HALF-OPEN")
                self.state = HALF_OPEN
            else:
                logger.warning(f"Circuit '{self.name}' is OPEN - fast failing")
                raise ServiceError(f"Service unavailable (circuit '{self.name}' is open)")
                
        try:
            result = await func(*args, **kwargs)
            
            # Reset on successful call if in half-open state
            if self.state == HALF_OPEN:
                logger.info(f"Circuit '{self.name}' recovered, transitioning to CLOSED")
                self._reset()
                
            return result
            
        except self.expected_exceptions as e:
            self._handle_failure(e)
            raise
            
    def _handle_failure(self, exception):
        """Handle a failure, potentially opening the circuit."""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        logger.warning(f"Circuit '{self.name}' recorded failure {self.failure_count}/{self.failure_threshold}: {str(exception)}")
        
        if self.state == HALF_OPEN or self.failure_count >= self.failure_threshold:
            logger.error(f"Circuit '{self.name}' is now OPEN due to failures")
            self.state = OPEN
            
    def _should_attempt_recovery(self):
        """Determine if enough time has passed to try recovery."""
        if not self.last_failure_time:
            return True
            
        now = datetime.now()
        seconds_since_failure = (now - self.last_failure_time).total_seconds()
        return seconds_since_failure >= self.recovery_timeout
        
    def _reset(self):
        """Reset the circuit breaker to closed state."""
        self.failure_count = 0
        self.state = CLOSED
        self.last_failure_time = None


class BulkheadManager:
    """
    Bulkhead pattern implementation to isolate resources.
    
    This class implements the bulkhead pattern to prevent a failure in one part
    of the system from cascading to other parts by isolating resources.
    """
    
    def __init__(self, name: str, max_concurrent_calls: int = 10, max_queue_size: int = 20):
        """
        Initialize the bulkhead manager.
        
        Args:
            name: A name for this bulkhead (for logging)
            max_concurrent_calls: Maximum number of concurrent executions
            max_queue_size: Maximum size of the wait queue
        """
        self.name = name
        self.max_concurrent_calls = max_concurrent_calls
        self.max_queue_size = max_queue_size
        self.semaphore = asyncio.Semaphore(max_concurrent_calls)
        self.active_count = 0
        self.queue_count = 0
        
        logger.info(f"Bulkhead '{name}' initialized with max_concurrent_calls={max_concurrent_calls}, "
                   f"max_queue_size={max_queue_size}")
        
    def __call__(self, func):
        """Make the bulkhead callable as a decorator."""
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await self.execute(func, *args, **kwargs)
        return wrapper
        
    async def execute(self, func, *args, **kwargs):
        """
        Execute a function with bulkhead isolation.
        
        This method limits the number of concurrent executions and queued requests
        to prevent resource exhaustion.
        """
        # Check if we can queue this request
        if self.queue_count >= self.max_queue_size:
            logger.error(f"Bulkhead '{self.name}' queue is full - rejecting request")
            raise ServiceError(f"Service overloaded (bulkhead '{self.name}' queue full)")
            
        # Add to queue
        self.queue_count += 1
        logger.debug(f"Bulkhead '{self.name}' queue size: {self.queue_count}")
        
        try:
            # Wait for semaphore (move from queue to active)
            async with self.semaphore:
                self.queue_count -= 1
                self.active_count += 1
                logger.debug(f"Bulkhead '{self.name}' active calls: {self.active_count}")
                
                # Execute the function
                try:
                    return await func(*args, **kwargs)
                finally:
                    self.active_count -= 1
                    logger.debug(f"Bulkhead '{self.name}' active calls: {self.active_count}")
        except:
            # If we fail while waiting in the queue
            self.queue_count -= 1
            raise


class ThreadPoolBulkhead:
    """
    Thread pool based bulkhead for CPU-bound operations.
    
    This class provides isolation for CPU-bound operations using thread pools.
    """
    
    _thread_pools = {}  # Shared thread pools by name
    
    @classmethod
    def get_pool(cls, name: str, max_workers: int = 5):
        """Get or create a thread pool with the given name."""
        if name not in cls._thread_pools:
            cls._thread_pools[name] = ThreadPoolExecutor(max_workers=max_workers)
            logger.info(f"Created thread pool '{name}' with max_workers={max_workers}")
        return cls._thread_pools[name]
    
    def __init__(self, name: str, max_workers: int = 5):
        """
        Initialize the thread pool bulkhead.
        
        Args:
            name: A name for this bulkhead pool
            max_workers: Maximum number of worker threads
        """
        self.name = name
        self.max_workers = max_workers
        self.pool = self.get_pool(name, max_workers)
        
    def __call__(self, func):
        """Make the bulkhead callable as a decorator."""
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await self.execute(func, *args, **kwargs)
        return wrapper
    
    async def execute(self, func, *args, **kwargs):
        """Execute a function in the thread pool."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.pool,
            functools.partial(func, *args, **kwargs)
        )


class BaseService(Generic[ModelType, SchemaType, CreateSchemaType]):
    """Base service class with common CRUD operations and resilience patterns."""

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
        max_delay: float = 2.0,
        backoff_factor: float = 2.0,
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
        retry_until = time.time() + (max_delay * max_retries)  # Set an upper time bound

        while retry_count <= max_retries and time.time() < retry_until:
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
                    logger.error(f"Max retries ({max_retries}) exceeded. Last error: {error_str}")
                    raise ServiceError(f"Max retries ({max_retries}) exceeded. Last error: {error_str}")

                matched_error = "timeout" if isinstance(e, asyncio.TimeoutError) else next(
                    (err for err in concurrency_errors if err in error_str), "unknown"
                )
                log_message = error_message or f"Operation failed due to {matched_error}"
                
                # Calculate jitter to avoid thundering herd
                jitter = (0.5 + (0.5 * (hash(str(time.time())) % 100) / 100))
                actual_delay = delay * jitter
                
                logger.warning(f"{log_message} (Attempt {retry_count}/{max_retries}). Retrying in {actual_delay:.2f}s")

                delay = min(delay * backoff_factor, max_delay)
                await asyncio.sleep(actual_delay)

        if last_exception:
            raise ServiceError(f"Operation failed after retries: {str(last_exception)}")
        raise ServiceError("Operation failed after retries")

    @staticmethod
    def with_retry(
        max_retries: int = 3,
        initial_delay: float = 0.05,
        max_delay: float = 2.0,
        backoff_factor: float = 2.0,
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

    @staticmethod
    def with_circuit_breaker(
        name: Optional[str] = None,
        failure_threshold: int = 5,
        recovery_timeout: int = 30,
        expected_exceptions: Tuple = (Exception,),
    ):
        """Decorator for adding circuit breaker to methods."""
        def decorator(func: Callable[..., T]) -> Callable[..., T]:
            # Use function name if none provided
            breaker_name = name or func.__qualname__
            circuit_breaker = CircuitBreaker(
                name=breaker_name,
                failure_threshold=failure_threshold,
                recovery_timeout=recovery_timeout,
                expected_exceptions=expected_exceptions,
            )
            
            @wraps(func)
            async def wrapper(*args, **kwargs) -> T:
                return await circuit_breaker.call(func, *args, **kwargs)
            
            return wrapper
        return decorator

    @staticmethod
    def with_bulkhead(
        name: Optional[str] = None,
        max_concurrent_calls: int = 10,
        max_queue_size: int = 20,
    ):
        """Decorator for adding bulkhead protection to methods."""
        def decorator(func: Callable[..., T]) -> Callable[..., T]:
            # Use function name if none provided
            bulkhead_name = name or func.__qualname__
            bulkhead = BulkheadManager(
                name=bulkhead_name,
                max_concurrent_calls=max_concurrent_calls,
                max_queue_size=max_queue_size,
            )
            
            @wraps(func)
            async def wrapper(*args, **kwargs) -> T:
                return await bulkhead.execute(func, *args, **kwargs)
            
            return wrapper
        return decorator

    @staticmethod
    def with_thread_pool(
        name: Optional[str] = None,
        max_workers: int = 5,
    ):
        """Decorator for adding thread pool isolation to CPU-bound methods."""
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            # Use function name if none provided
            pool_name = name or func.__qualname__
            thread_pool = ThreadPoolBulkhead(
                name=pool_name,
                max_workers=max_workers,
            )
            
            @wraps(func)
            async def wrapper(*args, **kwargs) -> Any:
                return await thread_pool.execute(func, *args, **kwargs)
            
            return wrapper
        return decorator

    async def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check for this service.
        
        Returns:
            A dictionary with health status information
        """
        status = "healthy"
        details = {
            "database": "up",
            "timestamp": datetime.now().isoformat(),
        }
        
        # Check database connection
        try:
            # Simple query to verify database connection
            await self.db.execute(select(1))
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            status = "degraded"
            details["database"] = "down"
            details["database_error"] = str(e)
        
        return {
            "status": status,
            "service": self.__class__.__name__,
            "details": details
        }

    @with_retry()
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

    @with_retry()
    async def get_by_id(self, id: UUID) -> Optional[ModelType]:
        """Get item by ID."""
        try:
            result = await self.db.execute(
                select(self.model).where(self.model.id == id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            raise ServiceError(f"Error retrieving item: {str(e)}")

    @with_retry()
    @with_circuit_breaker(name="create_operation")
    async def create(self, data: CreateSchemaType) -> SchemaType:
        """Create a new item with resilience patterns."""
        try:
            item = self.model(**data.dict())
            self.db.add(item)
            await self.db.commit()
            await self.db.refresh(item)
            return self.schema_class.from_orm(item)
        except Exception as e:
            await self.db.rollback()
            raise ServiceError(f"Error creating item: {str(e)}")

    @with_retry()
    @with_circuit_breaker(name="update_operation")
    async def update(self, id: UUID, data: Dict[str, Any]) -> Optional[SchemaType]:
        """Update an existing item with resilience patterns."""
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

    @with_retry()
    @with_circuit_breaker(name="delete_operation")
    async def delete(self, id: UUID) -> bool:
        """Delete an item by ID with resilience patterns."""
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

    @with_retry()
    async def exists(self, id: UUID) -> bool:
        """Check if an item exists by ID."""
        try:
            result = await self.db.execute(
                select(self.model).where(self.model.id == id)
            )
            return result.scalar_one_or_none() is not None
        except Exception as e:
            raise ServiceError(f"Error checking item existence: {str(e)}")

    @with_retry()
    async def count(self) -> int:
        """Get total count of items."""
        try:
            result = await self.db.execute(
                select(self.model)
            )
            return len(result.scalars().all())
        except Exception as e:
            raise ServiceError(f"Error counting items: {str(e)}")

    @with_retry()
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

    @with_retry()
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
