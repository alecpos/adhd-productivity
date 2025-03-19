import asyncio
import logging
import time
from functools import wraps
from typing import Callable, Optional, TypeVar

import sqlalchemy.exc

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

T = TypeVar("T")


async def with_retry(
    operation: Callable[..., T],
    max_retries: int = 3,
    initial_delay: float = 0.05,
    max_delay: float = 0.5,
    backoff_factor: float = 1.5,
    retry_exceptions: tuple = (
        sqlalchemy.exc.OperationalError,
        sqlalchemy.exc.InternalError,
        sqlalchemy.exc.DBAPIError,
        sqlalchemy.exc.TimeoutError,
        asyncio.TimeoutError,
    ),
    error_message: Optional[str] = None,
) -> T:
    """
    Execute an async operation with exponential backoff retry logic.

    Args:
        operation: Async callable to execute
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay between retries in seconds
        max_delay: Maximum delay between retries in seconds
        backoff_factor: Multiplier for delay after each retry
        retry_exceptions: Tuple of exceptions to catch and retry on
        error_message: Custom error message to log on retries

    Returns:

    Raises:
    """
    retry_count = 0
    delay = initial_delay
    last_exception = None
    operation_id = str(time.time())[-6:]  # Use last 6 digits of timestamp as operation ID

    logger.info(f"[{operation_id}] Starting operation with max_retries={max_retries}")

    while retry_count <= max_retries:
        try:
            logger.debug(f"[{operation_id}] Attempt {retry_count + 1}/{max_retries + 1}")
            start_time = time.time()

            # Add timeout to the operation
            result = await asyncio.wait_for(
                operation(),
                timeout=1.0,  # 1 second timeout per attempt
            )

            duration = time.time() - start_time
            logger.info(
                f"[{operation_id}] Operation successful after {duration:.2f}s on attempt {retry_count + 1}"
            )

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

            is_retryable = isinstance(e, asyncio.TimeoutError) or any()

            if not is_retryable:
                logger.error(f"[{operation_id}] Non-retryable error encountered: {error_str}")

            last_exception = e
            retry_count += 1

            if retry_count > max_retries:
                logger.error(
                    f"[{operation_id}] Max retries ({max_retries}) exceeded. Last error: {error_str}"
                )

            matched_error = (
                "timeout"
                if isinstance(e, asyncio.TimeoutError)
                else next((err for err in concurrency_errors if err in error_str), "unknown")
            )
            log_message = error_message or f"Operation failed due to {matched_error}"
            logger.warning(f"[{operation_id}] {log_message} (Attempt {retry_count}/{max_retries})")

            delay = min(delay * backoff_factor, max_delay)
            logger.debug(f"[{operation_id}] Waiting {delay:.2f}s before next attempt")
            await asyncio.sleep(delay)

    logger.error(f"[{operation_id}] Operation failed after {max_retries} retries")


def with_concurrency_control(
    max_retries: int = 3,
    initial_delay: float = 0.05,
    max_delay: float = 0.5,
    backoff_factor: float = 1.5,
    retry_exceptions: tuple = (
        sqlalchemy.exc.OperationalError,
        sqlalchemy.exc.InternalError,
        sqlalchemy.exc.DBAPIError,
        sqlalchemy.exc.TimeoutError,
        asyncio.TimeoutError,
    ),
    error_message: Optional[str] = None,
):
    """
    Decorator for adding retry logic to async functions.

    Args:
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay between retries in seconds
        max_delay: Maximum delay between retries in seconds
        backoff_factor: Multiplier for delay after each retry
        retry_exceptions: Tuple of exceptions to catch and retry on
        error_message: Custom error message to log on retries
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            func_name = func.__name__
            logger.debug(f"Applying concurrency control to {func_name}")

            async def operation():
                return await func(*args, **kwargs)

            try:
                return await with_retry(
                    operation=operation,
                    max_retries=max_retries,
                    initial_delay=initial_delay,
                    max_delay=max_delay,
                    backoff_factor=backoff_factor,
                    retry_exceptions=retry_exceptions,
                    error_message=error_message,
                )
            except Exception as e:
                logger.error(f"Function {func_name} failed with error: {str(e)}")
                raise

        return wrapper

    return decorator
