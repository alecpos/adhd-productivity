# Stochastic Time Estimation Engine Tests

This directory contains tests for the Stochastic Time Estimation Engine, a core component of the ADHD Calendar application that provides realistic time estimates for tasks.

## Test Components

The test suite covers the following components:

1. **Bayesian Duration Predictor** (`test_bayesian_duration_predictor.py`): Tests for the machine learning model that predicts task durations.
2. **NLP Complexity Analyzer** (`test_nlp_complexity_analyzer.py`): Tests for the component that analyzes task descriptions to determine complexity.
3. **Contextual Stressor Detector** (`test_contextual_stressor_detector.py`): Tests for the component that detects stressors that may affect task performance.
4. **Time Buffer Calculator** (`test_time_buffer_calculator.py`): Tests for the component that calculates buffer times between tasks.
5. **Integration Tests** (`test_integration.py`): Tests for ensuring all components work together correctly.

## Running Tests

### Using Docker (Recommended)

The easiest way to run the tests is using Docker, which ensures all dependencies are correctly installed:

```bash
# Make sure the script is executable
chmod +x tests/ml/stochastic_time_estimation/run_tests_docker.sh

# Run all tests
./tests/ml/stochastic_time_estimation/run_tests_docker.sh

# Run a specific test file
./tests/ml/stochastic_time_estimation/run_tests_docker.sh tests/ml/stochastic_time_estimation/test_bayesian_duration_predictor.py -v

# Run a specific test
./tests/ml/stochastic_time_estimation/run_tests_docker.sh tests/ml/stochastic_time_estimation/test_nlp_complexity_analyzer.py::TestNLPComplexityAnalyzer::test_analyze_task -v
```

### Without Docker

If you need to run tests without Docker, you'll need to ensure all dependencies are correctly installed:

```bash
# Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r tests/ml/stochastic_time_estimation/test-requirements.txt

# Install NLP data
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet')"

# Run the tests
pytest tests/ml/stochastic_time_estimation/ -v
```

> **Warning**: Due to dependency conflicts (especially with PyMC3 and NumPy), running tests outside Docker may be challenging.

## Troubleshooting

### Common Issues

1. **Import Errors**: If you encounter import errors, ensure your PYTHONPATH includes the project root:
   ```bash
   export PYTHONPATH=/path/to/project/root:$PYTHONPATH
   ```

2. **Dependency Conflicts**: The most common issue is conflicts between PyMC3 and newer versions of NumPy. Use the Docker approach to avoid these issues.

3. **Failed Tests**: If tests fail, check the test output for details. You can run specific failing tests with:
   ```bash
   ./tests/ml/stochastic_time_estimation/run_tests_docker.sh tests/ml/stochastic_time_estimation/specific_test_file.py::TestClass::test_method -v
   ```

## Continuous Integration

The tests are automatically run via GitHub Actions when changes are pushed to the main and develop branches. The workflow configuration is in `.github/workflows/ste_tests.yml`.

## Test Verification

To verify test coverage without running the actual tests:

```bash
# Verify basic test structure
python tests/ml/stochastic_time_estimation/run_mock_tests.py

# Analyze test coverage
python tests/ml/stochastic_time_estimation/verify_test_coverage.py
```

## Documentation

For more detailed information about the tests, see the `TEST_SUMMARY.md` file in this directory.

## Contributing

When adding new features to the Stochastic Time Estimation Engine, please add corresponding tests following the existing patterns. Make sure to:

1. Include both unit tests for individual functions and integration tests
2. Cover edge cases and failure scenarios
3. Use proper mocking to isolate the component being tested
4. Keep tests independent and idempotent 