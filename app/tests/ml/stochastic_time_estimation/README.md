# Stochastic Time Estimation Engine Test Documentation

This document provides a comprehensive overview of the testing strategy and implementation for the Stochastic Time Estimation Engine (Epic 2).

## System Overview

The Stochastic Time Estimation Engine is a critical component of the ADHD Calendar system, providing personalized and realistic time estimates for tasks. It consists of four main components:

1. **BayesianDurationPredictor**: A probabilistic model that provides task duration estimates with confidence intervals.
2. **NLPComplexityAnalyzer**: A natural language processing model that evaluates task complexity from descriptions.
3. **ContextualStressorDetector**: A system that identifies factors affecting focus and productivity.
4. **TimeBufferCalculator**: An algorithm that determines optimal transition times between tasks.

## Test Coverage

| Component | Total Tests | Passing | Failing | Coverage % |
|-----------|-------------|---------|---------|------------|
| BayesianDurationPredictor | 47 | 42 | 5 | 89% |
| NLPComplexityAnalyzer | 38 | 35 | 3 | 92% |
| ContextualStressorDetector | 41 | 35 | 6 | 85% |
| TimeBufferCalculator | 34 | 31 | 3 | 86% |
| **Total** | **160** | **143** | **17** | **88%** |

## Known Issues

### BayesianDurationPredictor

1. **Prior Initialization Failure**:
   - Issue: Custom prior distributions fail to initialize with certain parameter sets
   - File: `app/ml/stochastic_time_estimation/bayesian_predictor.py`
   - Test: `test_custom_prior_initialization`
   - Priority: High

2. **Confidence Interval Calculation**:
   - Issue: Confidence intervals can become too narrow with large datasets
   - File: `app/ml/stochastic_time_estimation/bayesian_predictor.py`
   - Test: `test_confidence_interval_with_large_dataset`
   - Priority: Medium

3. **Cold Start Handling**:
   - Issue: Cold start fallback doesn't properly categorize new task types
   - File: `app/ml/stochastic_time_estimation/cold_start_handler.py`
   - Test: `test_cold_start_task_categorization`
   - Priority: Medium

4. **Incremental Update Performance**:
   - Issue: Model updates become slow after accumulating >1000 data points
   - File: `app/ml/stochastic_time_estimation/model_updater.py`
   - Test: `test_incremental_update_performance`
   - Priority: Low

5. **Task Similarity Matching**:
   - Issue: Similar task matching fails for tasks with specialized terminology
   - File: `app/ml/stochastic_time_estimation/task_similarity.py`
   - Test: `test_domain_specific_terminology_matching`
   - Priority: Medium

### NLPComplexityAnalyzer

1. **Ambiguity Detection**:
   - Issue: Fails to correctly identify ambiguous instructions in technical contexts
   - File: `app/ml/stochastic_time_estimation/nlp_analyzer.py`
   - Test: `test_ambiguity_in_technical_context`
   - Priority: High

2. **Language Model Loading**:
   - Issue: Timeout when loading model in resource-constrained environments
   - File: `app/ml/stochastic_time_estimation/model_loader.py`
   - Test: `test_model_loading_with_resource_constraints`
   - Priority: Medium

3. **Subtask Detection**:
   - Issue: Misses implicit subtasks in complex nested sentences
   - File: `app/ml/stochastic_time_estimation/subtask_detector.py`
   - Test: `test_nested_subtask_detection`
   - Priority: Low

### ContextualStressorDetector

1. **Wearable Data Integration**:
   - Issue: Connection failures with certain wearable device APIs
   - File: `app/ml/stochastic_time_estimation/wearable_connector.py`
   - Test: `test_wearable_api_connection_resilience`
   - Priority: High

2. **False Positive Rate**:
   - Issue: Elevated false positive rate for noise-related stressors
   - File: `app/ml/stochastic_time_estimation/stressor_detector.py`
   - Test: `test_noise_stressor_false_positive_rate`
   - Priority: Medium

3. **Stressor Impact Calculation**:
   - Issue: Impact calculation doesn't properly account for stressor duration
   - File: `app/ml/stochastic_time_estimation/stressor_impact.py`
   - Test: `test_duration_dependent_impact_calculation`
   - Priority: Medium

4. **Recovery Time Estimation**:
   - Issue: Recovery time estimates can be inaccurate for combined stressors
   - File: `app/ml/stochastic_time_estimation/recovery_estimator.py`
   - Test: `test_combined_stressor_recovery_time`
   - Priority: Low

5. **Historical Pattern Detection**:
   - Issue: Weekly pattern detection fails with irregular sleep schedules
   - File: `app/ml/stochastic_time_estimation/pattern_detector.py`
   - Test: `test_irregular_sleep_pattern_detection`
   - Priority: Medium

6. **Environment Data Processing**:
   - Issue: Memory leak in environment data processing for long sessions
   - File: `app/ml/stochastic_time_estimation/environment_processor.py`
   - Test: `test_long_session_memory_usage`
   - Priority: High

### TimeBufferCalculator

1. **Minimum Buffer Enforcement**:
   - Issue: Minimum buffer not enforced for certain task type transitions
   - File: `app/ml/stochastic_time_estimation/buffer_calculator.py`
   - Test: `test_minimum_buffer_enforcement`
   - Priority: High

2. **Activity Recommendation**:
   - Issue: Inappropriate transition activities recommended for short buffers
   - File: `app/ml/stochastic_time_estimation/activity_recommender.py`
   - Test: `test_short_buffer_activity_recommendations`
   - Priority: Medium

3. **Calendar Integration**:
   - Issue: Buffer visualization fails with certain calendar providers
   - File: `app/ml/stochastic_time_estimation/calendar_integrator.py`
   - Test: `test_buffer_visualization_cross_provider`
   - Priority: Low

## Next Steps

### Immediate Priorities

1. **Fix High Priority Issues**:
   - Fix prior initialization failure in BayesianDurationPredictor
   - Address ambiguity detection in technical contexts
   - Resolve wearable data integration failures
   - Fix memory leak in environment data processing
   - Ensure minimum buffer enforcement works in all cases

2. **Test Coverage Improvements**:
   - Add tests for edge cases in confidence interval calculation
   - Improve test coverage for recovery time estimation
   - Add performance tests for model updates with large datasets

3. **Integration Testing**:
   - Enhance integration tests between ContextualStressorDetector and BayesianDurationPredictor
   - Add end-to-end tests for the complete time estimation pipeline
   - Test calendar integration with all supported providers

### Future Work

1. **Automated Performance Testing**:
   - Implement automated performance benchmarks
   - Set up regression testing for prediction accuracy
   - Create load testing for concurrent user scenarios

2. **Test Data Enhancement**:
   - Expand test data with more real-world examples
   - Create specialized datasets for edge cases
   - Generate synthetic data for privacy-sensitive scenarios

3. **Test Automation**:
   - Improve CI/CD integration for test suite
   - Implement automatic test result reporting
   - Create visual dashboards for test coverage

## Verification Process

### Unit Testing

All components have unit tests covering core functionality:

- **BayesianDurationPredictor**: Tests for model initialization, prediction, updating, and edge cases
- **NLPComplexityAnalyzer**: Tests for text analysis, complexity scoring, and feature extraction
- **ContextualStressorDetector**: Tests for stressor detection, impact calculation, and pattern analysis
- **TimeBufferCalculator**: Tests for buffer calculation, activity recommendation, and transition analysis

### Integration Testing

Integration tests verify the interactions between components:

- Prediction pipeline from task description to final time estimate
- Stressor detection to prediction adjustment flow
- Buffer calculation based on task characteristics and stressors
- Calendar system integration for buffer visualization

### End-to-End Testing

End-to-end tests simulate real user workflows:

- Creating a task and receiving a time estimate
- Completing a task and seeing model updates
- Detecting environmental changes and updating estimates
- Scheduling sequential tasks with appropriate buffers

### Performance Testing

Performance tests ensure system responsiveness:

- Latency tests for prediction operations (<200ms target)
- Throughput tests for batch operations (>50 predictions/second)
- Memory usage monitoring during extended operations
- Database query performance for historical data retrieval

## Test Execution

### Running All Tests

```bash
# Run all tests
cd app/tests
python -m pytest ml/stochastic_time_estimation

# Run with verbose output
python -m pytest ml/stochastic_time_estimation -v

# Run with coverage report
python -m pytest ml/stochastic_time_estimation --cov=app.ml.stochastic_time_estimation
```

### Running Component-Specific Tests

```bash
# BayesianDurationPredictor tests
python -m pytest ml/stochastic_time_estimation/test_bayesian_predictor.py

# NLPComplexityAnalyzer tests
python -m pytest ml/stochastic_time_estimation/test_nlp_analyzer.py

# ContextualStressorDetector tests
python -m pytest ml/stochastic_time_estimation/test_stressor_detector.py

# TimeBufferCalculator tests
python -m pytest ml/stochastic_time_estimation/test_buffer_calculator.py
```

### Running Specific Test Cases

```bash
# Run a specific test function
python -m pytest ml/stochastic_time_estimation/test_bayesian_predictor.py::test_confidence_interval_calculation

# Run tests matching a pattern
python -m pytest ml/stochastic_time_estimation/ -k "model or update"

# Run tests by marker
python -m pytest ml/stochastic_time_estimation/ -m "slow"
```

### Performance Tests

```bash
# Run performance tests
python -m pytest ml/stochastic_time_estimation/performance/ --runslow

# Run load tests
python -m pytest ml/stochastic_time_estimation/load_tests/
```

## Test Data

Test data is stored in the following locations:

- `ml/stochastic_time_estimation/test_data/task_descriptions.json`: Sample task descriptions of varying complexity
- `ml/stochastic_time_estimation/test_data/user_profiles.json`: User profiles with different ADHD characteristics
- `ml/stochastic_time_estimation/test_data/wearable_samples.json`: Sample wearable device data streams
- `ml/stochastic_time_estimation/test_data/environment_samples.json`: Environmental condition samples
- `ml/stochastic_time_estimation/test_data/completion_records.json`: Historical task completion records

### Data Generation

Test data can be regenerated or expanded using:

```bash
# Generate synthetic test data
python -m app.tests.ml.stochastic_time_estimation.tools.generate_test_data

# Anonymize production data for testing
python -m app.tests.ml.stochastic_time_estimation.tools.anonymize_data
```

## Mock Services

The following mock services are used during testing:

1. **Mock Wearable API**: Simulates wearable device data streams
   - Location: `ml/stochastic_time_estimation/mocks/mock_wearable_api.py`
   - Usage: `--use-mock-wearable` command line flag

2. **Mock Calendar API**: Simulates calendar integration
   - Location: `ml/stochastic_time_estimation/mocks/mock_calendar_api.py`
   - Usage: `--use-mock-calendar` command line flag

3. **Mock Environment Sensors**: Simulates environmental data
   - Location: `ml/stochastic_time_estimation/mocks/mock_environment_sensors.py`
   - Usage: `--use-mock-environment` command line flag

4. **Mock User Profile Service**: Provides test user profiles
   - Location: `ml/stochastic_time_estimation/mocks/mock_user_profiles.py`
   - Usage: `--use-mock-profiles` command line flag

## CI Integration

Tests are integrated into the CI pipeline with the following stages:

1. **Fast Tests**: Unit tests and basic integration tests (~2 minutes)
   - Runs on every PR and commit to main
   - Must pass for PR approval

2. **Full Test Suite**: All tests including slow integration tests (~10 minutes)
   - Runs on PR approval and before deployment
   - Generates coverage reports

3. **Performance Tests**: Benchmarks and performance tests (~15 minutes)
   - Runs nightly and before major releases
   - Compares against performance baselines

4. **Load Tests**: Simulated multi-user scenarios (~30 minutes)
   - Runs weekly and before major releases
   - Verifies system stability under load

## Known Limitations

1. **Simulation vs. Reality**: Wearable data simulation may not capture all real-world variations
2. **Performance Testing Environment**: CI performance tests run in containerized environments which may differ from production
3. **Database Scale**: Tests use smaller datasets than production, which may miss certain scaling issues
4. **Calendar Integration**: Not all calendar provider edge cases are covered in automated tests
5. **Long-term Pattern Detection**: Tests for features requiring months of data use compressed simulations

## Contributing New Tests

When adding new functionality to the Stochastic Time Estimation Engine, please:

1. Add unit tests covering the core functionality
2. Ensure edge cases are tested
3. Update integration tests if component interfaces change
4. Add performance tests for computationally intensive operations
5. Update this documentation if adding new test categories or tools

For detailed testing guidelines, see `CONTRIBUTING.md`.
