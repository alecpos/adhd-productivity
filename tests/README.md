# Tests Directory

This directory contains the test suite for the ADHD Calendar backend application.

## Overview

The tests directory contains unit, integration, and end-to-end tests for the backend application. These tests help ensure that the application functions correctly, follows specifications, and maintains compatibility during development.

## Test Structure

The tests are organized following the application's structure:

- **api/**: Tests for API endpoints
- **ml/**: Tests for machine learning models and algorithms
  - **tpr/**: Tests for Temporal Pattern Recognition models
  - **time_estimation/**: Tests for the Stochastic Time Estimation Engine
  - **forgetfulness/**: Tests for Proactive Forgetfulness and Distraction Mitigation
  - **hyperfold/**: Tests for the Hyperfold Temporal Attention Module
- **models/**: Tests for database models
- **services/**: Tests for business logic services
- **utils/**: Tests for utility functions
- **integration/**: Integration tests that test multiple components together
- **e2e/**: End-to-end tests that test the entire application flow

## Test Types

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test interactions between components
- **End-to-End Tests**: Test complete user workflows
- **Performance Tests**: Test performance characteristics under load
- **Mocks and Stubs**: Tests that use mock objects to simulate dependencies

## Running Tests

### Running All Tests

```bash
python -m pytest
```

### Running Tests by Directory

```bash
# Run API tests
python -m pytest tests/api

# Run ML tests
python -m pytest tests/ml
```

### Running Tests by Tag

```bash
# Run unit tests
python -m pytest -m "unit"

# Run integration tests
python -m pytest -m "integration"

# Run slow tests
python -m pytest -m "slow"
```

### Running Tests with Coverage

```bash
python -m pytest --cov=app
```

## Test Configuration

Configuration for the test suite is defined in `pytest.ini` and includes:

- Custom markers for categorizing tests
- Test discovery paths
- Fixture scopes and behavior
- Logging settings

## Test Data

Test data is stored in the `tests/data` directory and includes:

- Fixture files for test data
- Sample inputs for ML models
- Expected outputs for comparison
- Mock database snapshots

## Adding New Tests

When adding new tests:

1. Place tests in the appropriate directory based on the component being tested
2. Use descriptive test names that explain what is being tested
3. Follow the naming convention: `test_[component]_[feature].py`
4. Use pytest fixtures for common setup and teardown
5. Add appropriate markers to categorize tests
6. Add clear assertions and error messages

## CI/CD Integration

Tests are automatically run in the CI/CD pipeline:

- Tests run on every pull request
- Code coverage reports are generated
- Test failures block merges to protected branches

## Documentation

For more detailed testing documentation, see:

- [Testing Strategy](../docs/testing_strategy.md)
- [Test Coverage Reports](../docs/test_coverage.md)
- [Performance Testing Guide](../docs/performance_testing_guide.md)
