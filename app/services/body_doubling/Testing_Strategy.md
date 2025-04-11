# Body Doubling Service Testing Strategy

This document outlines the testing approach for the refactored Body Doubling Service modules.

## 1. Test Structure

The test suite is organized into several levels:

### 1.1. Unit Tests

Unit tests verify that individual components function correctly in isolation, with dependencies mocked:

- **SessionManager Tests** - Tests for the session management functions
- **MatchingEngine Tests** - Tests for user matching and compatibility algorithms
- **AnalyticsService Tests** - Tests for analytics data processing
- **NotificationService Tests** - Tests for notification dispatching

### 1.2. Integration Tests

Integration tests verify that multiple components work together correctly:

- **Body Doubling Service Tests** - Tests for the main service that orchestrates the specialized components
- **End-to-End Workflow Tests** - Tests that cover complete user workflows (session creation, joining, feedback, etc.)

## 2. Test Coverage Goals

We aim for the following test coverage:

- **Core Business Logic**: 90%+ coverage
- **Edge Cases and Error Handling**: 85%+ coverage
- **Utility Functions**: 70%+ coverage

## 3. Mocking Strategy

### 3.1. Database Interactions

- Use `AsyncMock` for the database session in unit tests
- Use in-memory SQLite with `create_async_engine("sqlite+aiosqlite:///:memory:")` for integration tests

### 3.2. Dependencies

- In unit tests, mock all dependencies to isolate the component under test
- In integration tests, use real implementations of internal components

## 4. Test Data

- Use fixtures to create test data (sessions, user IDs, preferences)
- Use deterministic UUIDs for consistent test output

## 5. Test Execution

### 5.1. Running Tests

Execute tests using the `run_body_doubling_tests.sh` script:

```bash
./scripts/run_body_doubling_tests.sh
```

This will run:
1. Unit tests for each component
2. Integration tests
3. Generate a coverage report

### 5.2. Test Output

The test runner will display:
- Verbose test output showing which tests passed/failed
- Code coverage report highlighting any uncovered code

## 6. Continuous Integration

Tests should be integrated into the CI/CD pipeline to:
- Run on every pull request
- Report code coverage changes
- Prevent merging if tests fail or coverage decreases significantly

## 7. Maintenance

### 7.1. Testing New Features

For any new feature:
1. Write unit tests for new component code
2. Update integration tests to cover feature workflows
3. Verify backward compatibility with existing code

### 7.2. Regression Testing

For any bug fix:
1. Write a test that reproduces the bug
2. Fix the bug
3. Verify the test passes with the fix

## 8. Test Quality Metrics

We measure test quality based on:

- **Coverage** - Percentage of code executed during tests
- **Specificity** - Tests should verify specific behavior, not just execute code
- **Independence** - Tests should not depend on each other
- **Speed** - Test suite should run quickly to encourage frequent testing
- **Comprehensibility** - Tests should be clear and document expected behavior
