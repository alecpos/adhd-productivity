# Testing Documentation

## Overview
This document outlines the testing strategy and practices for the ADHD Calendar Backend project.

## Test Structure
The test suite is organized into several key areas:

### Service Tests
- `test_mental_health.py`: Tests for mental health tracking and analysis
- `test_integrated_planning.py`: Tests for schedule and task integration
- `test_pomodoro.py`: Tests for pomodoro session management
- `test_body_doubling.py`: Tests for collaborative focus sessions

### Utility Tests
- `test_utils.py`: Shared test utilities and helper functions
- `test_schema_management.py`: Schema validation and management tests
- `test_routes.py`: API route testing

## Test Categories

### Unit Tests
- Individual service methods
- Schema validation
- Utility functions
- Route handlers

### Integration Tests
- Service interactions
- Database operations
- External API integrations
- WebSocket communications

### End-to-End Tests
- Complete user workflows
- Cross-service scenarios
- Real-time features

## Test Utilities

### TestUtils Class
Located in `test_utils.py`, provides common testing functionality:
- Mock session creation
- Test data generation
- Assertion helpers
- Time utilities

### Fixtures
Common pytest fixtures for:
- Database sessions
- Service instances
- Authentication
- Test data

## Best Practices

### Writing Tests
1. Use descriptive test names that explain the scenario
2. Follow the Arrange-Act-Assert pattern
3. Test both success and failure cases
4. Mock external dependencies
5. Use appropriate assertions

### Test Data
1. Use factory methods from TestUtils
2. Avoid hardcoded test data
3. Clean up test data after tests
4. Use realistic but simplified data

### Async Testing
1. Use proper async/await syntax
2. Handle coroutines correctly
3. Use pytest-asyncio for async tests
4. Properly mock async operations

## Running Tests

### Local Development
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_mental_health.py

# Run with coverage
pytest --cov=app tests/
```

### CI/CD Pipeline
Tests are automatically run in the CI/CD pipeline:
1. On pull requests
2. Before deployments
3. On scheduled intervals

## Test Coverage
- Aim for 80%+ coverage
- Focus on critical paths
- Include edge cases
- Test error handling

## Mocking Strategy
1. Use pytest-mock for mocking
2. Mock external services
3. Mock database operations
4. Mock time-dependent operations

## Error Testing
1. Test validation errors
2. Test permission errors
3. Test timeout scenarios
4. Test resource constraints

## Performance Testing
1. Response time benchmarks
2. Load testing scenarios
3. Memory usage monitoring
4. Database query optimization

## Security Testing
1. Authentication tests
2. Authorization tests
3. Input validation
4. Rate limiting

## Maintenance
1. Regular test updates
2. Remove obsolete tests
3. Update test data
4. Monitor test performance

## Troubleshooting
Common issues and solutions:
1. Async test failures
2. Database connection issues
3. Mock configuration problems
4. Test isolation issues 