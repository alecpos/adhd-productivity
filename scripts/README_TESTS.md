# Body Doubling Service Test Runner Scripts

This directory contains scripts for running tests for the Body Doubling Service.

## Available Scripts

### run_body_doubling_tests.sh

This script runs all unit tests for the Body Doubling Service components.

```bash
./scripts/run_body_doubling_tests.sh
```

## Additional Testing Options

Beyond the basic test runner script, the Body Doubling Service offers several specialized testing options:

### Unit Tests

```bash
cd app/tests/services/body_doubling
python -m pytest
```

### Basic Algorithm Tests

```bash
cd app/tests/services/body_doubling
python test_simple.py
```

### Integration Tests

```bash
python -m app.services.body_doubling.integration_test
```

### Performance Tests

```bash
python -m app.services.body_doubling.performance_test
```

### Manual Testing

```bash
python -m app.services.body_doubling.manual_test
```

## Test Documentation

For complete documentation on testing the Body Doubling Service, see:

- [Testing.md](../app/services/body_doubling/Testing.md) - Detailed testing instructions
- [Analytics_Service.md](../app/services/body_doubling/Analytics_Service.md) - Analytics service documentation
- [Technical_Debt.md](../app/services/body_doubling/Technical_Debt.md) - Technical debt tracker

## Test Coverage

Test coverage reports are generated in the `coverage` directory after running the tests.

---

*Last updated: November 15, 2023* 