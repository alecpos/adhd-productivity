"""
Resilient Jira API Client Module

This module provides a resilient client for making requests to the Jira API
with retry and circuit breaker patterns.
"""

import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple

from app.ui.project_management_integration import ProjectToolConfig
from app.ui.integrations.jira_authenticator import JiraAuthenticator
from app.ui.integrations.jira_error_handler import JiraErrorHandler
from app.ui.integrations.jira_api_client import JiraApiClient

logger = logging.getLogger(__name__)


class ResilientJiraApiClient(JiraApiClient):
    """Jira API client with retry and circuit breaker patterns."""

    def __init__(
        self,
        config: ProjectToolConfig,
        authenticator: JiraAuthenticator,
        retry_count: int = 3,
        backoff_factor: float = 1.5,
        circuit_breaker_threshold: int = 5,
        circuit_breaker_reset_time: int = 60,
    ):
        """
        Initialize the resilient Jira API client.

        Args:
            config: Configuration for the Jira integration
            authenticator: Authenticator for Jira API
            retry_count: Maximum number of retry attempts
            backoff_factor: Factor for exponential backoff
            circuit_breaker_threshold: Number of failures before opening circuit
            circuit_breaker_reset_time: Time in seconds before resetting circuit
        """
        super().__init__(config, authenticator)
        self.error_handler = JiraErrorHandler()
        self.retry_count = retry_count
        self.backoff_factor = backoff_factor
        self.circuit_breaker_failures = 0
        self.circuit_breaker_threshold = circuit_breaker_threshold
        self.circuit_breaker_reset_time = circuit_breaker_reset_time
        self.circuit_open_until = None

        # Track API calls for rate limiting
        self.api_call_history = []
        self.rate_limit_per_minute = 60  # Default: assume 60 calls per minute

    async def _make_request(
        self,
        url: str,
        method: str = "GET",
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        json: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Make HTTP request to Jira API with retry and circuit breaker patterns.

        Args:
            url: Request URL
            method: HTTP method
            params: URL parameters
            headers: HTTP headers
            json: Request body as JSON

        Returns:
            Response data as dictionary

        Raises:
            Exception: When all retries fail or circuit breaker is open
        """
        # Check if circuit breaker is open
        if self._is_circuit_open():
            raise Exception("Circuit breaker open, Jira API temporarily disabled")

        # Apply rate limiting
        await self._apply_rate_limiting()

        # Try the request with exponential backoff
        attempt = 0
        last_exception = None

        while attempt < self.retry_count:
            try:
                # Record API call for rate limiting
                self.api_call_history.append(datetime.utcnow())

                # In real implementation:
                # async with aiohttp.ClientSession() as session:
                #     async with session.request(
                #         method, url, params=params, headers=headers, json=json
                #     ) as response:
                #         response.raise_for_status()
                #         if method == "DELETE":
                #             return None
                #         return await response.json()

                # For this refactoring, use the parent implementation
                response = await super()._make_request(url, method, params, headers, json)

                # Reset circuit breaker counter on success
                self.circuit_breaker_failures = 0
                return response

            except Exception as e:
                last_exception = e

                # Special handling for different error types
                should_retry = self._should_retry(e, attempt)
                if not should_retry:
                    self._increment_circuit_breaker()
                    raise

                # Exponential backoff
                backoff_time = self.backoff_factor**attempt
                logger.warning(
                    f"Retrying request in {backoff_time:.2f} seconds (attempt {attempt+1}/{self.retry_count})"
                )
                await asyncio.sleep(backoff_time)
                attempt += 1

        # If we got here, all retries failed
        self._increment_circuit_breaker()
        self.error_handler.handle_error(
            f"All {self.retry_count} retry attempts failed for {method} request to {url}",
            last_exception,
            reraise=True,
        )

    def _should_retry(self, exception, attempt_number):
        """
        Determine if a request should be retried based on the exception and attempt number.

        Args:
            exception: The exception that occurred
            attempt_number: The current attempt number

        Returns:
            bool: True if the request should be retried, False otherwise
        """
        # Don't retry if we've reached the max retry count
        if attempt_number >= self.retry_count:
            return False

        # Check if exception is in retryable categories
        return (
            self._is_connection_error(exception)
            or self._is_rate_limit_error(exception)
            or self._is_server_error(exception)
            or self._is_timeout_error(exception)
        )

    def _is_connection_error(self, exception):
        """Check if the exception is a connection error."""
        error_str = str(exception).lower()
        return (
            "connection" in error_str
            or "connecttimeout" in error_str
            or isinstance(exception, ConnectionError)
        )

    def _is_rate_limit_error(self, exception):
        """Check if the exception is a rate limit error."""
        if hasattr(exception, "status_code") and exception.status_code == 429:
            return True

        error_str = str(exception).lower()
        return "rate limit" in error_str or "too many requests" in error_str

    def _is_server_error(self, exception):
        """Check if the exception is a server error (5xx)."""
        if hasattr(exception, "status_code") and 500 <= exception.status_code < 600:
            return True

        error_str = str(exception).lower()
        return "server error" in error_str or "internal server error" in error_str

    def _is_timeout_error(self, exception):
        """Check if the exception is a timeout error."""
        error_str = str(exception).lower()
        return "timeout" in error_str or "timed out" in error_str

    def _is_circuit_open(self) -> bool:
        """
        Check if circuit breaker is open.

        Returns:
            True if circuit breaker is open, False otherwise
        """
        if self.circuit_open_until and datetime.utcnow() < self.circuit_open_until:
            logger.warning(f"Circuit breaker open until {self.circuit_open_until}")
            return True

        # Reset if the circuit was open but now the timeout has passed
        if self.circuit_open_until:
            logger.info("Circuit breaker reset")
            self.circuit_open_until = None
            self.circuit_breaker_failures = 0

        return False

    def _increment_circuit_breaker(self) -> None:
        """
        Increment the circuit breaker failure counter and open if threshold exceeded.
        """
        self.circuit_breaker_failures += 1
        logger.debug(
            f"Circuit breaker failure count: {self.circuit_breaker_failures}/{self.circuit_breaker_threshold}"
        )

        if self.circuit_breaker_failures >= self.circuit_breaker_threshold:
            # Open the circuit for the configured reset time
            self.circuit_open_until = datetime.utcnow() + timedelta(
                seconds=self.circuit_breaker_reset_time
            )
            logger.warning(
                f"Circuit breaker opened for Jira API due to {self.circuit_breaker_failures} "
                f"consecutive failures. Will reset at {self.circuit_open_until}"
            )

    async def _apply_rate_limiting(self) -> None:
        """
        Apply rate limiting to avoid hitting API limits.
        """
        # Clean up history - keep only calls from the last minute
        now = datetime.utcnow()
        self.api_call_history = [t for t in self.api_call_history if now - t < timedelta(minutes=1)]

        # Check if we've exceeded the rate limit
        if len(self.api_call_history) >= self.rate_limit_per_minute:
            # Calculate how long to wait
            oldest_call = min(self.api_call_history)
            wait_time = 60 - (now - oldest_call).total_seconds()

            if wait_time > 0:
                logger.warning(
                    f"Rate limit reached. Waiting {wait_time:.2f} seconds before next request"
                )
                await asyncio.sleep(wait_time)

    def get_health_metrics(self) -> Dict[str, Any]:
        """
        Get health metrics for the client.

        Returns:
            Dictionary of health metrics
        """
        return {
            "circuit_breaker_failures": self.circuit_breaker_failures,
            "circuit_breaker_threshold": self.circuit_breaker_threshold,
            "circuit_open_until": self.circuit_open_until,
            "api_calls_last_minute": len(self.api_call_history),
            "error_stats": self.error_handler.get_error_stats(),
        }
