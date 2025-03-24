# Service Resilience Patterns Documentation

This document outlines the resilience patterns implemented in the ADHD Calendar backend services. These patterns are designed to improve the robustness, fault tolerance, and availability of our microservices architecture, especially important for users with ADHD who rely on consistent service availability.

## Table of Contents

- [Overview](#overview)
- [BaseService Implementation](#baseservice-implementation)
- [Core Resilience Patterns](#core-resilience-patterns)
  - [Retry Pattern](#retry-pattern)
  - [Circuit Breaker Pattern](#circuit-breaker-pattern)
  - [Bulkhead Pattern](#bulkhead-pattern)
- [Health Checks](#health-checks)
- [Implementation Examples](#implementation-examples)
- [Testing Resilience Patterns](#testing-resilience-patterns)
- [Best Practices](#best-practices)

## Overview

In distributed systems, failures are inevitable. Networks fail, services become overloaded, and dependencies can become unavailable. For users with ADHD, unexpected application disruptions can be particularly problematic. Our resilience patterns are designed to:

1. **Automatically recover from transient failures** without user intervention
2. **Prevent cascading failures** across the system
3. **Degrade gracefully** when dependencies are unavailable
4. **Provide clear health status** for monitoring and alerting
5. **Maintain responsiveness** even under high load or partial outages

## BaseService Implementation

All service classes inherit from the `BaseService` class, which provides:

- Common retry and circuit breaker decorators
- Bulkhead isolation functionality
- Base health check implementation
- Standard error handling patterns

## Core Resilience Patterns

### Retry Pattern

The retry pattern automatically retries failed operations with exponential backoff.

#### Implementation

```python
@BaseService.with_retry(
    max_retries=3,
    initial_delay=0.1,
    max_delay=2.0,
    backoff_factor=2.0,
    error_message="Failed to complete operation"
)
async def some_method(self, arg1, arg2):
    # Method logic here
    pass
```

#### Key Features

- **Configurable retry count**: Limit the number of retry attempts
- **Exponential backoff**: Increasing delay between retries to avoid overwhelming the system
- **Jitter**: Random variation in retry delays to prevent synchronized retry storms
- **Exception filtering**: Only retry on specific types of exceptions (e.g., connection errors)

### Circuit Breaker Pattern

The circuit breaker pattern prevents repeated calls to failing services, allowing them time to recover.

#### Implementation

```python
@BaseService.with_circuit_breaker(
    name="dependency_name",
    failure_threshold=5,
    recovery_timeout=30
)
async def call_external_service(self, arg1, arg2):
    # Method logic here
    pass
```

#### States

1. **CLOSED**: Normal operation, calls pass through to the service
2. **OPEN**: Service calls are failing, circuit is "broken" and calls fail fast
3. **HALF_OPEN**: Testing if the service has recovered by allowing limited calls

#### Key Features

- **Failure counting**: Tracks consecutive failures until a threshold is reached
- **Timeout period**: Automatic transition to half-open state after a recovery period
- **Failure rate detection**: Opens circuit when failure percentage exceeds threshold
- **Context preservation**: Circuit state is shared across service instances

### Bulkhead Pattern

The bulkhead pattern isolates different parts of the system to prevent cascading failures.

#### Implementation

```python
async def method_with_dependencies(self):
    # Call dependency in isolated context with timeout
    try:
        result = await self.bulkhead(
            self._call_dependency,
            arg1, 
            arg2,
            timeout=3
        )
    except Exception as e:
        # Handle failure and provide fallback
        result = self._fallback_method()
```

#### Key Features

- **Resource isolation**: Limits resources consumed by each dependency
- **Timeouts**: Prevents waiting indefinitely for slow responses
- **Concurrent call limiting**: Restricts the number of parallel calls to a dependency
- **Graceful degradation**: Allows using fallbacks when dependencies fail

## Health Checks

Each service implements a `health_check()` method that provides:

1. Service status (healthy, degraded, or unhealthy)
2. Circuit breaker status for each dependency
3. Resource utilization metrics
4. Response timing information

### Example Health Check Response

```json
{
  "service": "TaskService",
  "status": "degraded",
  "details": {
    "version": "1.2.3",
    "uptime": 3600,
    "message": "One or more dependencies unavailable",
    "dependencies": {
      "task_analyzer": {
        "status": "unhealthy",
        "circuit": "OPEN"
      },
      "notification_service": {
        "status": "healthy",
        "circuit": "CLOSED"
      }
    }
  }
}
```

## Implementation Examples

### TaskService

The TaskService implements resilience patterns for task management operations:

- **Retry pattern** on database operations like `create_task` and `update_task`
- **Circuit breaker** on external dependencies like task analysis and notifications
- **Bulkhead pattern** for isolating CPU-intensive task analysis
- **Enhanced health checks** that monitor all dependencies

### SchedulingService

The SchedulingService implements resilience patterns for schedule generation:

- **Retry pattern** on operations like `generate_schedule` and `create_block`
- **Circuit breaker** on energy pattern and focus curve generation
- **Bulkhead pattern** with fallbacks for calendar integration
- **Health check** integration with dependent services

## Testing Resilience Patterns

We test resilience patterns using the `resilience_tester.py` script, which:

1. Creates mock services with configurable failure modes
2. Verifies retry behavior with transient failures
3. Tests circuit breaker state transitions
4. Confirms bulkhead isolation prevents cascading failures
5. Validates health check accuracy during degraded conditions

## Best Practices

1. **Apply resilience patterns to all external calls** including:
   - Database operations
   - External API calls
   - Integration with calendar providers
   - Calls to other microservices

2. **Provide appropriate fallbacks** when dependencies fail:
   - Default energy patterns when real ones can't be fetched
   - Simplified task analysis when detailed analysis fails
   - Basic scheduling when optimized scheduling is unavailable

3. **Configure patterns appropriately**:
   - Retry counts and delays based on operation importance
   - Circuit breaker thresholds based on typical failure patterns
   - Bulkhead timeouts based on expected response times

4. **Monitor resilience metrics**:
   - Track retry attempts and success rates
   - Monitor circuit breaker state changes
   - Measure bulkhead timeouts and rejections

5. **Test resilience regularly**:
   - Use chaos testing to inject failures
   - Simulate dependency outages
   - Verify system behavior during partial failures 