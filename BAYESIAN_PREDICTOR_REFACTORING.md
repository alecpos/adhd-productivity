# Bayesian Duration Predictor Refactoring - Implementation Plan

## Current Issues

The `BayesianDurationPredictor` class in `app/ml/stochastic_time_estimation/bayesian_duration_predictor.py` currently has:

- High cyclomatic complexity (7.0)
- Large methods with multiple responsibilities
- Complex nested logic
- Limited separation of concerns

## Refactoring Goals

1. Reduce cyclomatic complexity by at least 40%
2. Limit maximum nesting depth to 3-4 levels
3. Improve testability and maintenance
4. Maintain all current functionality and backwards compatibility

## Phase 1: Preparation (2 days)

### 1.1 Create Comprehensive Test Suite
- Develop unit tests for all public methods
- Create integration tests for end-to-end behavior
- Document edge cases and specific behaviors

### 1.2 Set Up Metrics Tracking
- Establish baseline metrics:
  - Cyclomatic complexity
  - Nesting depth
  - Method length
  - Class coupling

### 1.3 Document Current Architecture
- Create sequence diagrams for key operations
- Document current data flow

## Phase 2: Class Extraction (3 days)

### 2.1 Create `BayesianModelBuilder` Class
```python
class BayesianModelBuilder:
    """Responsible for building and sampling from Bayesian models."""

    def build_model(self, features, actual_values, estimated_values):
        """Build a PyMC3 model based on input data."""
        pass

    def sample_posterior(self, model, sample_count=2000, tune_count=1000):
        """Sample from the posterior distribution."""
        pass

    def extract_coefficients(self, trace):
        """Extract model coefficients from the trace."""
        pass
```

### 2.2 Create `FeatureProcessor` Class
```python
class FeatureProcessor:
    """Handles feature extraction and processing for the Bayesian model."""

    def __init__(self, feature_importance_threshold=0.05):
        self.feature_importance_threshold = feature_importance_threshold
        self.feature_engineer = FeatureEngineer()

    async def prepare_historical_features(self, historical_data):
        """Extract features from historical task data."""
        pass

    async def prepare_prediction_features(self, task, user_id, context_data=None):
        """Extract features for prediction."""
        pass

    def calculate_feature_importances(self, trace, feature_names):
        """Calculate importance of each feature based on the model trace."""
        pass

    def filter_features_by_importance(self, features, importances):
        """Filter features based on importance threshold."""
        pass
```

### 2.3 Create `PredictionResultFormatter` Class
```python
class PredictionResultFormatter:
    """Formats prediction results and confidence intervals."""

    def __init__(self, confidence_level=0.95):
        self.confidence_level = confidence_level

    def format_prediction(self, expected_ratio, prediction_interval, estimated_duration, factors=None):
        """Format the prediction results into a standardized output format."""
        pass

    def calculate_prediction_interval(self, samples, confidence_level=None):
        """Calculate prediction interval from posterior samples."""
        pass

    def format_prediction_factors(self, features, feature_importances):
        """Format the factors that influenced the prediction."""
        pass
```

## Phase 3: Method Refactoring (3 days)

### 3.1 Refactor Main Class
```python
class BayesianDurationPredictor(BaseMLModel):
    """
    Bayesian network for predicting realistic task durations.
    """

    def __init__(
        self,
        db=None,
        model_path=None,
        confidence_level=0.95,
        min_history_points=5,
        max_history_points=100,
        feature_importance_threshold=0.05,
    ):
        super().__init__(model_path=model_path)
        self.db = db
        self.confidence_level = confidence_level
        self.min_history_points = min_history_points
        self.max_history_points = max_history_points

        # Initialize components
        self.feature_processor = FeatureProcessor(feature_importance_threshold)
        self.model_builder = BayesianModelBuilder()
        self.result_formatter = PredictionResultFormatter(confidence_level)

        # Model state
        self.trace = None
        self.model = None
        self.feature_importances = {}
        self.last_updated = None
```

### 3.2 Refactor `fit()` Method
```python
async def fit(self, user_id: str) -> None:
    """
    Fit the Bayesian model using historical task data for a user.

    Args:
        user_id: ID of the user to fit the model for
    """
    # Get historical data
    historical_data = await self._get_historical_data(user_id)

    if not self._validate_historical_data(historical_data):
        return

    # Process features
    train_features, train_actual, train_estimated = self.feature_processor.prepare_historical_features(historical_data)

    # Calculate deviation ratios
    train_deviation_ratios = self._calculate_deviation_ratios(train_actual, train_estimated)

    # Build and sample from model
    self.model = self.model_builder.build_model(train_features, train_deviation_ratios)
    self.trace = self.model_builder.sample_posterior(self.model)

    # Update state
    self.last_updated = datetime.now()
    self.feature_importances = self.feature_processor.calculate_feature_importances(self.trace, train_features.columns)

    logger.info(f"Successfully fit Bayesian duration model for user {user_id}")
```

### 3.3 Refactor `predict()` Method
```python
async def predict(
    self,
    task_id: str,
    user_id: str,
    context_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Predict task duration using the Bayesian model."""
    # Ensure model is fitted
    if not self._ensure_model_fitted(user_id):
        return self._error_response("Insufficient historical data for prediction")

    # Get task
    task = await self._get_task(task_id)
    if task is None:
        return self._error_response(f"Task {task_id} not found")

    # Extract features
    features = await self.feature_processor.prepare_prediction_features(task, user_id, context_data)

    # Make prediction
    expected_ratio = self._calculate_expected_ratio(features)
    prediction_interval = self._calculate_prediction_interval(features)

    # Get original estimate
    estimated_duration = task.estimated_duration or 60  # Default to 1 hour

    # Format result
    prediction_factors = self.feature_processor.get_prediction_factors(features, self.feature_importances)

    return self.result_formatter.format_prediction(
        expected_ratio,
        prediction_interval,
        estimated_duration,
        prediction_factors
    )
```

## Phase 4: Helper Methods (2 days)

### 4.1 Implement Validation Methods
```python
def _validate_historical_data(self, historical_data):
    """Validate historical data meets requirements."""
    if len(historical_data) < self.min_history_points:
        logger.warning(
            f"Insufficient historical data points ({len(historical_data)}). "
            f"Need at least {self.min_history_points}."
        )
        return False
    return True

def _ensure_model_fitted(self, user_id):
    """Ensure model is fitted, attempt to fit if not."""
    if self.trace is None:
        await self.fit(user_id)

    return self.trace is not None
```

### 4.2 Implement Calculation Methods
```python
def _calculate_deviation_ratios(self, actual_durations, estimated_durations):
    """Calculate ratio of actual to estimated durations."""
    return actual_durations / estimated_durations

def _calculate_expected_ratio(self, features):
    """Calculate expected ratio using model coefficients."""
    alpha_samples = self.trace['alpha']
    return np.dot(features, alpha_samples.mean(axis=0))

def _calculate_prediction_interval(self, features):
    """Calculate prediction interval for the given features."""
    alpha_samples = self.trace['alpha']
    sigma_samples = self.trace['sigma']

    # Calculate expected ratios for all samples
    expected_ratios = np.dot(features, alpha_samples.T)

    # Add noise according to the model
    predicted_ratios = np.random.normal(
        loc=expected_ratios[:, np.newaxis],
        scale=sigma_samples,
        size=(len(features), len(sigma_samples))
    )

    return self.result_formatter.calculate_prediction_interval(predicted_ratios)
```

### 4.3 Implement Error Response Methods
```python
def _error_response(self, error_message):
    """Create standardized error response."""
    return {
        "predicted_duration": None,
        "confidence_interval": None,
        "error": error_message
    }
```

## Phase 5: Integration and Testing (2 days)

### 5.1 Integration
- Integrate all components
- Add proper error handling and logging
- Ensure backward compatibility

### 5.2 Testing
- Run all unit tests
- Run integration tests
- Verify edge cases

### 5.3 Performance Validation
- Compare new implementation against original
- Verify predictions match
- Measure performance improvement

## Phase 6: Documentation and Cleanup (1 day)

### 6.1 Documentation
- Update docstrings
- Create architecture diagram of new implementation
- Document patterns used and rationale

### 6.2 Code Review
- Peer review changes
- Address feedback

### 6.3 Final Metrics
- Calculate final complexity metrics
- Document improvements

## Timeline
- Phase 1: Days 1-2
- Phase 2: Days 3-5
- Phase 3: Days 6-8
- Phase 4: Days 9-10
- Phase 5: Days 11-12
- Phase 6: Day 13
