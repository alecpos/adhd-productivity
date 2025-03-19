"""Metrics collection and monitoring utilities."""

import logging
import time
from contextlib import contextmanager
from enum import Enum
from typing import Any, Dict, Optional

from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram

logger = logging.getLogger(__name__)


class MetricType(Enum):
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"


class MetricsCollector:
    """Centralized metrics collection and management."""

    def __init__(self):
        # Create a unique registry for this instance
        self.registry = CollectorRegistry()

        # Initialize counters
        self.api_requests = Counter(
            "api_requests_total",
            "Total API requests",
            ["endpoint", "method", "status"],
            registry=self.registry,
        )

        self.error_counter = Counter(
            "error_total",
            "Total errors by type",
            ["error_type"],
            registry=self.registry,
        )

        # Initialize histograms
        self.request_duration = Histogram(
            "request_duration_seconds",
            "Request duration in seconds",
            ["endpoint"],
            registry=self.registry,
        )

        # Initialize gauges
        self.active_sessions = Gauge(
            "active_sessions",
            "Number of active sessions",
            ["session_type"],
            registry=self.registry,
        )

    def increment_request(self, endpoint: str, method: str, status: int) -> None:
        """Increment the API request counter."""
        self.api_requests.labels(endpoint=endpoint, method=method, status=status).inc()

    def record_error(self, error_type: str) -> None:
        """Record an error occurrence."""
        self.error_counter.labels(error_type=error_type).inc()
        logger.error(f"Error recorded: {error_type}")

    def observe_request_duration(self, endpoint: str, duration: float) -> None:
        """Record the duration of a request."""
        self.request_duration.labels(endpoint=endpoint).observe(duration)

    def update_active_sessions(self, session_type: str, count: int) -> None:
        """Update the number of active sessions."""
        self.active_sessions.labels(session_type=session_type).set(count)

    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics values."""
        return {
            "api_requests": self.api_requests._metrics,
            "errors": self.error_counter._metrics,
            "request_duration": self.request_duration._metrics,
            "active_sessions": self.active_sessions._metrics,
        }


class DatabaseMetrics:
    """Database-specific metrics collection."""

    def __init__(self):
        # Query metrics
        self.query_counter = Counter(
            "database_queries_total", "Total database queries", ["operation", "table"]
        )

        self.query_duration = Histogram(
            "database_query_duration_seconds",
            "Database query duration in seconds",
            ["operation", "table"],
        )

        # Connection metrics
        self.active_connections = Gauge(
            "database_active_connections", "Number of active database connections"
        )

        self.connection_errors = Counter(
            "database_connection_errors_total", "Total database connection errors"
        )

    def record_query(self, operation: str, table: str) -> None:
        """Record a database query."""
        self.query_counter.labels(operation=operation, table=table).inc()

    def observe_query_duration(self, operation: str, table: str, duration: float) -> None:
        """Record the duration of a database query."""
        self.query_duration.labels(operation=operation, table=table).observe(duration)

    def update_connections(self, count: int) -> None:
        """Update the number of active connections."""
        self.active_connections.set(count)

    def record_connection_error(self) -> None:
        """Record a database connection error."""
        self.connection_errors.inc()
        logger.error("Database connection error recorded")


class ServiceMetrics:
    """Service metrics tracking and monitoring."""

    _instances: Dict[str, "ServiceMetrics"] = {}

    def __new__(cls, service_name: str) -> "ServiceMetrics":
        if service_name not in cls._instances:
            cls._instances[service_name] = super().__new__(cls)
            cls._instances[service_name]._initialized = False
        return cls._instances[service_name]

    def __init__(self, service_name: str):
        if not hasattr(self, "_initialized") or not self._initialized:
            self.service_name = service_name
            self._counters: Dict[str, int] = {
                "requests": 0,
                "errors": 0,
                "successes": 0,
                "cache_hits": 0,
                "cache_misses": 0,
            }
            self._gauges: Dict[str, float] = {}
            self._histograms: Dict[str, list] = {
                "operation_duration": [],
                "response_time": [],
            }
            self._initialized = True

    def increment_counter(self, metric: str, value: int = 1) -> None:
        """Increment a counter metric."""
        if metric not in self._counters:
            self._counters[metric] = 0
        self._counters[metric] += value

    def decrement_counter(self, metric: str, value: int = 1) -> None:
        """Decrement a counter metric."""
        if metric not in self._counters:
            self._counters[metric] = 0
        self._counters[metric] = max(0, self._counters[metric] - value)

    def set_gauge(self, metric: str, value: float) -> None:
        """Set a gauge metric."""
        self._gauges[metric] = value

    def record_histogram(self, metric: str, value: float) -> None:
        """Record a value in a histogram metric."""
        if metric not in self._histograms:
            self._histograms[metric] = []
        self._histograms[metric].append(value)

    def observe_operation_duration(self, operation: str) -> Any:
        """Context manager to observe operation duration."""

        @contextmanager
        def _observe():
            start_time = time.time()
            try:
                yield
            finally:
                duration = time.time() - start_time
                self.record_histogram(f"{operation}_duration", duration)

        return _observe()

    def get_counter(self, metric: str) -> int:
        """Get the current value of a counter metric."""
        return self._counters.get(metric, 0)

    def get_gauge(self, metric: str) -> Optional[float]:
        """Get the current value of a gauge metric."""
        return self._gauges.get(metric)

    def get_histogram_stats(self, metric: str) -> Dict[str, float]:
        """Get statistics for a histogram metric."""
        values = self._histograms.get(metric, [])
        if not values:
            return {
                "count": 0,
                "min": 0.0,
                "max": 0.0,
                "mean": 0.0,
            }

        return {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "mean": sum(values) / len(values),
        }

    def reset(self) -> None:
        """Reset all metrics."""
        self._counters = {k: 0 for k in self._counters}
        self._gauges.clear()
        self._histograms = {k: [] for k in self._histograms}

    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all metrics."""
        return {
            "counters": self._counters.copy(),
            "gauges": self._gauges.copy(),
            "histograms": {k: self.get_histogram_stats(k) for k in self._histograms},
        }

    def record_error(self, error_type: str, severity: str = "error") -> None:
        """Record an error with type and severity."""
        self.increment_counter("errors")
        logger.error(
            f"Error recorded: {error_type} in {self.service_name} with severity {severity}"
        )

    def record_success(self, operation: str) -> None:
        """Record a successful operation."""
        self.increment_counter("successes")
        logger.info(f"Success recorded: {operation} in {self.service_name}")

    def record_cache_hit(self) -> None:
        """Record a cache hit."""
        self.increment_counter("cache_hits")

    def record_cache_miss(self) -> None:
        """Record a cache miss."""
        self.increment_counter("cache_misses")

    def get_cache_hit_ratio(self) -> float:
        """Calculate cache hit ratio."""
        hits = self.get_counter("cache_hits")
        misses = self.get_counter("cache_misses")
        total = hits + misses
        return hits / total if total > 0 else 0.0


class ErrorMetrics:
    """Error metrics tracking and monitoring."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not hasattr(self, "_initialized") or not self._initialized:
            self.error_counter = Counter("error_total", "Total errors by type", ["error_type"])
            self._initialized = True

    def increment_error(self, error_type: str) -> None:
        """Increment error counter for a specific error type."""
        self.error_counter.labels(error_type=error_type).inc()
        logger.error(f"Error recorded: {error_type}")


class SecurityMetrics:
    """Security-specific metrics collection."""

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            # Authentication metrics
            self.auth_attempts = Counter(
                "authentication_attempts_total",
                "Total authentication attempts",
                ["status", "method"],
            )

            self.token_operations = Counter(
                "token_operations_total",
                "Total token operations",
                ["operation", "status"],
            )

            # Security event metrics
            self.security_events = Counter(
                "security_events_total",
                "Total security events",
                ["event_type", "severity"],
            )

            # Active sessions
            self.active_sessions = Gauge("active_user_sessions", "Number of active user sessions")

            # Rate limiting metrics
            self.rate_limit_counters = Counter(
                "rate_limit_total", "Total rate limit events", ["event_type"]
            )

            self._initialized = True

    def record_auth_attempt(self, status: str, method: str = "password") -> None:
        """Record an authentication attempt."""
        self.auth_attempts.labels(status=status, method=method).inc()

    def record_token_operation(self, operation: str, status: str = "success") -> None:
        """Record a token operation (creation, validation, refresh)."""
        self.token_operations.labels(operation=operation, status=status).inc()

    def record_security_event(self, event_type: str, severity: str = "info") -> None:
        """Record a security event."""
        self.security_events.labels(event_type=event_type, severity=severity).inc()
        if severity in ["warning", "error", "critical"]:
            logger.warning(f"Security event: {event_type} with severity {severity}")

    def update_active_sessions(self, count: int) -> None:
        """Update the count of active user sessions."""
        self.active_sessions.set(count)

    def increment_counter(self, event_type: str) -> None:
        """Increment a rate limit counter."""
        self.rate_limit_counters.labels(event_type=event_type).inc()


class RouteMetrics:
    """Route-specific metrics collection."""

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            # Route metrics
            self.route_requests = Counter(
                "route_requests_total",
                "Total route requests",
                ["route", "method", "status"],
            )

            self.route_duration = Histogram(
                "route_duration_seconds",
                "Route request duration in seconds",
                ["route", "method"],
            )

            self.route_errors = Counter(
                "route_errors_total", "Total route errors", ["route", "error_type"]
            )

            self._initialized = True

    def record_request(self, route: str, method: str, status: int) -> None:
        """Record a route request."""
        self.route_requests.labels(route=route, method=method, status=status).inc()

    def observe_duration(self, route: str, method: str, duration: float) -> None:
        """Record the duration of a route request."""
        self.route_duration.labels(route=route, method=method).observe(duration)

    def record_error(self, route: str, error_type: str) -> None:
        """Record a route error."""
        self.route_errors.labels(route=route, error_type=error_type).inc()
        logger.error(f"Route error recorded: {route} - {error_type}")


# Create singleton instances
metrics_collector = MetricsCollector()
database_metrics = DatabaseMetrics()
service_metrics = ServiceMetrics(service_name="global")
error_metrics = ErrorMetrics()
security_metrics = SecurityMetrics()
route_metrics = RouteMetrics()

__all__ = [
    "MetricsCollector",
    "DatabaseMetrics",
    "ServiceMetrics",
    "ErrorMetrics",
    "SecurityMetrics",
    "RouteMetrics",
    "metrics_collector",
    "database_metrics",
    "service_metrics",
    "error_metrics",
    "security_metrics",
    "route_metrics",
]
