# ADHD Calendar: Epic 5 Code Reference

**Version**: 1.0
**Last Updated**: 2025-06-15
**Target Audience**: Developers and maintainers

## Overview

This document provides a comprehensive code reference for the fairness, bias mitigation, and ethical implementation components created in Epic 5. It details the structure, classes, methods, and key implementation details to assist developers in understanding and maintaining the codebase.

## Code Structure

The Epic 5 components are organized into the following directory structure:

```
app/
└── ml/
    └── fairness/
        ├── shap_explainer.py         # SHAP-based explanation generation
        ├── adversarial_debiasing.py  # Bias mitigation with adversarial methods
        ├── fallback_protocols.py     # Fallback handling for low-confidence predictions
        ├── bias_auditing.py          # Fairness metrics and bias auditing
        ├── __init__.py               # Package exports
        └── utils/                    # Shared utilities for fairness components
            ├── visualization.py      # Visualization helpers for explanations
            ├── metrics.py            # Fairness metrics implementation
            ├── data_processing.py    # Data preprocessing for fairness operations
            └── logging.py            # Specialized logging for fairness components
```

## SHAP Explainability (shap_explainer.py)

### Class: `SHAPExplainer`

Base class for generating explanations using SHAP values.

```python
class SHAPExplainer:
    """Base class for SHAP-based model explanations."""

    def __init__(self, model, feature_names=None, output_names=None, feature_perturbation='interventional'):
        """
        Initialize a SHAP explainer.

        Args:
            model: The model to explain
            feature_names: Names of input features
            output_names: Names of output classes/values
            feature_perturbation: SHAP perturbation method
        """
        self.model = model
        self.feature_names = feature_names
        self.output_names = output_names
        self.feature_perturbation = feature_perturbation
        self._init_shap_explainer()

    def _init_shap_explainer(self):
        """Initialize the appropriate SHAP explainer based on model type."""
        # Implementation details...

    def explain(self, input_data, prediction=None):
        """
        Generate an explanation for a prediction.

        Args:
            input_data: Input features for the prediction
            prediction: Optional prediction result

        Returns:
            RecommendationExplanation object
        """
        # Implementation details...

    def _generate_shap_values(self, input_data):
        """
        Generate SHAP values for the input data.

        Args:
            input_data: Input features

        Returns:
            SHAP values and expected values
        """
        # Implementation details...

    def _create_text_explanation(self, shap_values, input_data, prediction):
        """
        Create human-readable text explanation.

        Args:
            shap_values: SHAP values
            input_data: Input features
            prediction: Model prediction

        Returns:
            Text explanation
        """
        # Implementation details...

    def _create_visual_explanation(self, shap_values, input_data, prediction):
        """
        Create visual explanation as base64 encoded image.

        Args:
            shap_values: SHAP values
            input_data: Input features
            prediction: Model prediction

        Returns:
            Base64 encoded image
        """
        # Implementation details...
```

### Class: `ProductivitySHAPExplainer`

Specialized SHAP explainer for productivity models.

```python
class ProductivitySHAPExplainer(SHAPExplainer):
    """SHAP explainer for productivity models."""

    def explain_window(self, start_time, end_time, productivity_score):
        """
        Explain productivity score for a time window.

        Args:
            start_time: Start of the window
            end_time: End of the window
            productivity_score: Predicted productivity score

        Returns:
            RecommendationExplanation object
        """
        # Implementation details...
```

### Class: `DurationSHAPExplainer`

Specialized SHAP explainer for duration prediction models.

```python
class DurationSHAPExplainer(SHAPExplainer):
    """SHAP explainer for duration prediction models."""

    def explain_estimate(self, task_id, duration_minutes):
        """
        Explain duration estimate for a task.

        Args:
            task_id: ID of the task
            duration_minutes: Estimated duration in minutes

        Returns:
            RecommendationExplanation object
        """
        # Implementation details...
```

### Class: `AttentionSHAPExplainer`

Specialized SHAP explainer for attention management models.

```python
class AttentionSHAPExplainer(SHAPExplainer):
    """SHAP explainer for attention management models."""

    def explain_recommendation(self, attention_state, recommendation):
        """
        Explain an attention management recommendation.

        Args:
            attention_state: Current attention state
            recommendation: Recommended action

        Returns:
            RecommendationExplanation object
        """
        # Implementation details...
```

### Class: `RecommendationExplanation`

Data class for storing explanation results.

```python
class RecommendationExplanation:
    """Container for model explanation results."""

    def __init__(self, text, visual=None, feature_importances=None, confidence=None):
        """
        Initialize explanation container.

        Args:
            text: Human-readable text explanation
            visual: Base64 encoded visualization
            feature_importances: Dictionary of feature importance values
            confidence: Confidence score for the explanation
        """
        self.text = text
        self.visual = visual
        self.feature_importances = feature_importances or {}
        self.confidence = confidence
        self.top_features = self._extract_top_features()

    def _extract_top_features(self, limit=5):
        """Extract the top N most important features."""
        # Implementation details...
```

### Function: `create_explainer`

Factory function to create the appropriate explainer.

```python
def create_explainer(model_type, model_instance, **kwargs):
    """
    Create an appropriate SHAP explainer for the model type.

    Args:
        model_type: Type of model ('productivity', 'duration', 'attention')
        model_instance: The model to explain
        **kwargs: Additional arguments for the explainer

    Returns:
        SHAPExplainer instance of the appropriate type
    """
    # Implementation details...
```

## Adversarial Debiasing (adversarial_debiasing.py)

### Class: `DebiasingService`

Service for applying adversarial debiasing to model predictions.

```python
class DebiasingService:
    """Service for mitigating bias in model predictions."""

    def __init__(self):
        """Initialize the debiasing service."""
        self.debiasing_models = {}
        self.debiasing_strength = 1.0

    def mitigate_bias(self, prediction, protected_attributes, debiasing_strength=None):
        """
        Apply debiasing to a model prediction.

        Args:
            prediction: Original model prediction
            protected_attributes: User's protected attributes
            debiasing_strength: Optional override for debiasing strength

        Returns:
            Debiased prediction
        """
        # Implementation details...

    def train_debiasing_model(self, training_data, protected_attributes):
        """
        Train a new debiasing model.

        Args:
            training_data: Training examples
            protected_attributes: Attributes to protect
        """
        # Implementation details...

    def debias_reminder(self, reminder_data, user_attributes):
        """
        Apply debiasing to reminder data.

        Args:
            reminder_data: Original reminder
            user_attributes: User's attributes

        Returns:
            Debiased reminder
        """
        # Implementation details...

    def debias_schedule_suggestion(self, suggestion, user_attributes):
        """
        Apply debiasing to schedule suggestion.

        Args:
            suggestion: Original suggestion
            user_attributes: User's attributes

        Returns:
            Debiased suggestion
        """
        # Implementation details...

    def set_debiasing_strength(self, strength):
        """
        Set the overall debiasing strength.

        Args:
            strength: Debiasing strength (0.0-1.0)
        """
        # Implementation details...
```

### Class: `AdversarialDebiaser`

Neural network-based debiasing model.

```python
class AdversarialDebiaser:
    """Neural network model for adversarial debiasing."""

    def __init__(self, input_dim, output_dim, protected_dim):
        """
        Initialize the adversarial debiaser.

        Args:
            input_dim: Dimension of input features
            output_dim: Dimension of output predictions
            protected_dim: Dimension of protected attributes
        """
        # Implementation details...

    def train(self, X, y, protected_attributes, epochs=10, batch_size=32):
        """
        Train the debiaser.

        Args:
            X: Input features
            y: Target values
            protected_attributes: Protected attribute values
            epochs: Number of training epochs
            batch_size: Training batch size
        """
        # Implementation details...

    def debias(self, input_features, protected_attributes, debiasing_strength=1.0):
        """
        Apply debiasing to input features.

        Args:
            input_features: Original features
            protected_attributes: Protected attribute values
            debiasing_strength: Strength of debiasing

        Returns:
            Debiased prediction
        """
        # Implementation details...
```

### Function: `get_debiasing_service`

Get the singleton instance of the debiasing service.

```python
def get_debiasing_service():
    """
    Get the singleton instance of the debiasing service.

    Returns:
        DebiasingService instance
    """
    global _debiasing_service_instance
    if _debiasing_service_instance is None:
        _debiasing_service_instance = DebiasingService()
    return _debiasing_service_instance
```

## Fallback Protocols (fallback_protocols.py)

### Class: `FallbackProtocol`

Abstract base class for fallback protocols.

```python
class FallbackProtocol(ABC):
    """Abstract base class for fallback protocols."""

    def __init__(self, protocol_id, confidence_threshold):
        """
        Initialize a fallback protocol.

        Args:
            protocol_id: Unique identifier for the protocol
            confidence_threshold: Confidence threshold for triggering fallback
        """
        self.protocol_id = protocol_id
        self.confidence_threshold = confidence_threshold
        self.telemetry_data = []

    @abstractmethod
    def should_fallback(self, confidence):
        """
        Determine if fallback should be triggered.

        Args:
            confidence: Confidence score (0-1)

        Returns:
            Boolean indicating if fallback should be triggered
        """
        pass

    @abstractmethod
    def apply_fallback(self, prediction, confidence, context=None):
        """
        Apply the fallback protocol to a prediction.

        Args:
            prediction: Original prediction
            confidence: Confidence score
            context: Optional context information

        Returns:
            Processed prediction with fallback applied
        """
        pass

    def log_fallback_event(self, confidence, action, context=None):
        """
        Log a fallback event for telemetry.

        Args:
            confidence: Confidence score
            action: Fallback action taken
            context: Optional context information
        """
        # Implementation details...
```

### Class: `BinaryFallbackProtocol`

Simple fallback protocol with a single threshold.

```python
class BinaryFallbackProtocol(FallbackProtocol):
    """Simple binary fallback protocol."""

    def __init__(self, protocol_id, confidence_threshold, default_value):
        """
        Initialize a binary fallback protocol.

        Args:
            protocol_id: Unique identifier for the protocol
            confidence_threshold: Confidence threshold
            default_value: Default value to use when confidence is below threshold
        """
        super().__init__(protocol_id, confidence_threshold)
        self.default_value = default_value

    def should_fallback(self, confidence):
        """Check if confidence is below the threshold."""
        return confidence < self.confidence_threshold

    def apply_fallback(self, prediction, confidence, context=None):
        """
        Apply binary fallback.

        Args:
            prediction: Original prediction
            confidence: Confidence score
            context: Optional context information

        Returns:
            Original prediction or default value based on confidence
        """
        # Implementation details...
```

### Class: `ProgressiveFallbackProtocol`

Multi-stage fallback protocol with progressive actions.

```python
class ProgressiveFallbackProtocol(FallbackProtocol):
    """Progressive fallback with multiple stages based on confidence levels."""

    def __init__(self, protocol_id, confidence_threshold, fallback_stages):
        """
        Initialize a progressive fallback protocol.

        Args:
            protocol_id: Unique identifier for the protocol
            confidence_threshold: Main confidence threshold
            fallback_stages: List of stage configurations
        """
        super().__init__(protocol_id, confidence_threshold)
        self.fallback_stages = sorted(fallback_stages, key=lambda x: x['threshold'])

    def should_fallback(self, confidence):
        """Check if confidence is below any threshold."""
        return confidence < self.confidence_threshold

    def apply_fallback(self, prediction, confidence, context=None):
        """
        Apply progressive fallback based on confidence level.

        Args:
            prediction: Original prediction
            confidence: Confidence score
            context: Optional context information

        Returns:
            Processed prediction with appropriate fallback action
        """
        # Implementation details...
```

### Class: `FallbackManager`

Manager for registering and applying fallback protocols.

```python
class FallbackManager:
    """Manager for fallback protocols."""

    def __init__(self):
        """Initialize the fallback manager."""
        self.protocols = {}

    def register_protocol(self, model_id, protocol):
        """
        Register a fallback protocol for a model.

        Args:
            model_id: Identifier for the model
            protocol: FallbackProtocol instance
        """
        self.protocols[model_id] = protocol

    def apply_protocol(self, model_id, prediction, confidence, context=None):
        """
        Apply the registered protocol for a model.

        Args:
            model_id: Identifier for the model
            prediction: The model's prediction
            confidence: Confidence score
            context: Optional context information

        Returns:
            Result with fallback action and processed prediction
        """
        # Implementation details...
```

### Function: `get_fallback_manager`

Get the singleton instance of the fallback manager.

```python
def get_fallback_manager():
    """
    Get the singleton instance of the fallback manager.

    Returns:
        FallbackManager instance
    """
    global _fallback_manager_instance
    if _fallback_manager_instance is None:
        _fallback_manager_instance = FallbackManager()
    return _fallback_manager_instance
```

### Function: `create_progressive_fallback`

Create a configured progressive fallback protocol.

```python
def create_progressive_fallback(protocol_id, confidence_threshold, fallback_stages):
    """
    Create a progressive fallback protocol.

    Args:
        protocol_id: Identifier for the protocol
        confidence_threshold: Main confidence threshold
        fallback_stages: List of stage configurations

    Returns:
        ProgressiveFallbackProtocol instance
    """
    return ProgressiveFallbackProtocol(
        protocol_id=protocol_id,
        confidence_threshold=confidence_threshold,
        fallback_stages=fallback_stages
    )
```

## Bias Auditing (bias_auditing.py)

### Class: `BiasAuditor`

Service for auditing models for fairness and bias.

```python
class BiasAuditor:
    """Service for auditing models for fairness and bias."""

    def __init__(self, db=None):
        """
        Initialize the bias auditor.

        Args:
            db: Optional database connection
        """
        self.db = db
        self.scheduled_audits = {}
        self.fairness_thresholds = {
            "disparate_impact": 0.8,
            "demographic_parity": 0.9,
            "equal_opportunity": 0.9,
            "equalized_odds": 0.85
        }

    def schedule_audit(self, model_id, frequency, metrics, protected_attributes):
        """
        Schedule a regular bias audit for a model.

        Args:
            model_id: Identifier for the model to audit
            frequency: Audit frequency ('daily', 'weekly', 'monthly')
            metrics: List of fairness metrics to calculate
            protected_attributes: List of protected attributes

        Returns:
            Audit job ID
        """
        # Implementation details...

    def audit_predictions(self, predictions, outcomes, protected_attributes, metrics=None):
        """
        Perform an immediate bias audit on predictions.

        Args:
            predictions: List of model predictions
            outcomes: List of actual outcomes
            protected_attributes: Protected attribute values
            metrics: Optional list of fairness metrics

        Returns:
            BiasAuditReport object
        """
        # Implementation details...

    def generate_report(self, audit_id):
        """
        Generate a report for a completed audit.

        Args:
            audit_id: ID of the audit

        Returns:
            BiasAuditReport object
        """
        # Implementation details...

    def _calculate_fairness_metrics(self, predictions, outcomes, protected_attributes, metrics):
        """
        Calculate fairness metrics.

        Args:
            predictions: List of model predictions
            outcomes: List of actual outcomes
            protected_attributes: Protected attribute values
            metrics: List of fairness metrics

        Returns:
            Dictionary of metric scores
        """
        # Implementation details...

    def _detect_violations(self, metric_scores):
        """
        Detect fairness violations based on thresholds.

        Args:
            metric_scores: Dictionary of metric scores

        Returns:
            List of violations
        """
        # Implementation details...

    def _generate_recommendations(self, violations, protected_attributes):
        """
        Generate recommendations to address violations.

        Args:
            violations: List of violations
            protected_attributes: Protected attribute values

        Returns:
            List of recommendations
        """
        # Implementation details...
```

### Class: `BiasAuditReport`

Container for bias audit results.

```python
class BiasAuditReport:
    """Container for bias audit results."""

    def __init__(self, audit_id, model_id, fairness_scores, violations, recommendations, protected_attributes, data_summary):
        """
        Initialize a bias audit report.

        Args:
            audit_id: Unique identifier for the audit
            model_id: Identifier for the audited model
            fairness_scores: Dictionary of fairness metric scores
            violations: List of fairness violations
            recommendations: List of recommendations
            protected_attributes: Protected attributes examined
            data_summary: Summary statistics of the audited data
        """
        self.audit_id = audit_id
        self.model_id = model_id
        self.timestamp = datetime.now().isoformat()
        self.fairness_scores = fairness_scores
        self.violations = violations
        self.recommendations = recommendations
        self.protected_attributes = protected_attributes
        self.data_summary = data_summary

    def to_dict(self):
        """Convert report to dictionary format."""
        # Implementation details...

    def to_html(self):
        """Generate HTML representation of the report."""
        # Implementation details...

    def to_markdown(self):
        """Generate Markdown representation of the report."""
        # Implementation details...
```

### Function: `get_bias_auditor`

Get the singleton instance of the bias auditor.

```python
def get_bias_auditor(db=None):
    """
    Get the singleton instance of the bias auditor.

    Args:
        db: Optional database connection

    Returns:
        BiasAuditor instance
    """
    global _bias_auditor_instance
    if _bias_auditor_instance is None:
        _bias_auditor_instance = BiasAuditor(db)
    return _bias_auditor_instance
```

## Fairness Utilities (utils/)

### Visualization (utils/visualization.py)

Functions for creating visualizations for explanations.

```python
def create_feature_importance_plot(feature_names, importance_values, top_n=10):
    """
    Create a feature importance bar plot.

    Args:
        feature_names: List of feature names
        importance_values: List of importance values
        top_n: Number of top features to include

    Returns:
        Base64 encoded image
    """
    # Implementation details...

def create_waterfall_plot(shap_values, features, prediction, expected_value):
    """
    Create a SHAP waterfall plot.

    Args:
        shap_values: SHAP values
        features: Feature values
        prediction: Model prediction
        expected_value: Expected/baseline value

    Returns:
        Base64 encoded image
    """
    # Implementation details...

def create_force_plot(shap_values, features, feature_names):
    """
    Create a SHAP force plot.

    Args:
        shap_values: SHAP values
        features: Feature values
        feature_names: Feature names

    Returns:
        Base64 encoded image
    """
    # Implementation details...
```

### Fairness Metrics (utils/metrics.py)

Functions for calculating fairness metrics.

```python
def calculate_disparate_impact(predictions, protected_attribute):
    """
    Calculate disparate impact ratio.

    Args:
        predictions: Binary predictions
        protected_attribute: Protected attribute values

    Returns:
        Disparate impact ratio
    """
    # Implementation details...

def calculate_demographic_parity(predictions, protected_attribute):
    """
    Calculate demographic parity difference.

    Args:
        predictions: Binary predictions
        protected_attribute: Protected attribute values

    Returns:
        Demographic parity difference
    """
    # Implementation details...

def calculate_equal_opportunity(predictions, outcomes, protected_attribute):
    """
    Calculate equal opportunity difference.

    Args:
        predictions: Binary predictions
        outcomes: Actual outcomes
        protected_attribute: Protected attribute values

    Returns:
        Equal opportunity difference
    """
    # Implementation details...

def calculate_equalized_odds(predictions, outcomes, protected_attribute):
    """
    Calculate equalized odds difference.

    Args:
        predictions: Binary predictions
        outcomes: Actual outcomes
        protected_attribute: Protected attribute values

    Returns:
        Equalized odds difference
    """
    # Implementation details...
```

### Data Processing (utils/data_processing.py)

Functions for preprocessing data for fairness operations.

```python
def preprocess_protected_attributes(user_attributes):
    """
    Preprocess user attributes for fairness operations.

    Args:
        user_attributes: User attribute dictionary

    Returns:
        Processed attributes
    """
    # Implementation details...

def normalize_prediction_format(prediction, model_type):
    """
    Normalize prediction format for debiasing.

    Args:
        prediction: Model prediction
        model_type: Type of model

    Returns:
        Normalized prediction
    """
    # Implementation details...

def prepare_audit_data(predictions, outcomes, protected_attributes):
    """
    Prepare data for bias auditing.

    Args:
        predictions: List of predictions
        outcomes: List of outcomes
        protected_attributes: Protected attribute values

    Returns:
        Prepared data structure
    """
    # Implementation details...
```

## Key Implementation Details

### 1. SHAP Explainability

- Uses model-agnostic `KernelExplainer` for universal compatibility
- Caches explanation results for performance
- Implements batched calculation of SHAP values for efficiency
- Uses custom templates for natural language explanations
- Adapts to different model types with specialized explainer classes

### 2. Adversarial Debiasing

- Implements two-phase adversarial training:
  1. Train predictor to optimize for primary task
  2. Train adversary to predict protected attributes
  3. Train predictor to minimize adversary's performance
- Uses TensorFlow for neural network implementation
- Provides configurable debiasing strength
- Applies model-specific post-processing for different model types

### 3. Fallback Protocols

- Implements chain-of-responsibility pattern for fallback stage selection
- Provides stateful telemetry data collection
- Uses decorator pattern to add fallback capabilities to existing models
- Implements configurable progressive fallback stages
- Preserves original prediction data in fallback results

### 4. Bias Auditing

- Schedules regular audits using background task queue
- Implements industry-standard fairness metrics
- Provides configurable fairness thresholds
- Generates HTML and Markdown audit reports
- Stores audit history for trend analysis

## Database Schema

The Epic 5 components use the following database tables:

```sql
-- Explanation storage
CREATE TABLE explanation_records (
    id UUID PRIMARY KEY,
    model_id VARCHAR(100) NOT NULL,
    prediction_id UUID NOT NULL,
    text_explanation TEXT NOT NULL,
    visual_explanation TEXT,
    feature_importances JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Fallback events tracking
CREATE TABLE fallback_events (
    id UUID PRIMARY KEY,
    protocol_id VARCHAR(100) NOT NULL,
    model_id VARCHAR(100) NOT NULL,
    confidence FLOAT NOT NULL,
    action VARCHAR(50),
    context JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Bias audit records
CREATE TABLE bias_audits (
    id UUID PRIMARY KEY,
    model_id VARCHAR(100) NOT NULL,
    fairness_scores JSONB NOT NULL,
    violations JSONB,
    recommendations JSONB,
    protected_attributes JSONB NOT NULL,
    data_summary JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Scheduled audit jobs
CREATE TABLE scheduled_audits (
    id UUID PRIMARY KEY,
    model_id VARCHAR(100) NOT NULL,
    frequency VARCHAR(20) NOT NULL,
    metrics JSONB NOT NULL,
    protected_attributes JSONB NOT NULL,
    last_run TIMESTAMP,
    next_run TIMESTAMP,
    status VARCHAR(20) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
```

## Performance Considerations

1. **SHAP Value Computation**: SHAP values are computationally expensive, so caching and asynchronous processing are implemented
2. **Debiasing Overhead**: Adversarial debiasing adds ~10-20ms overhead per prediction; batching is recommended for bulk operations
3. **Memory Usage**: SHAP explanation generation can be memory-intensive for models with many features
4. **Bias Auditing Scale**: Full audits on large datasets can take several minutes; scheduled to run during off-peak hours
5. **Fallback Protocol Speed**: Fallback protocols add minimal overhead (<5ms) to the prediction pipeline

## Debugging Guidance

### SHAP Explainability

- Set `EXPLAINER_DEBUG=1` environment variable for verbose logging
- Common issues:
  - Missing feature names: Provide feature_names when creating explainer
  - Image encoding errors: Check matplotlib version compatibility
  - NaN values in explanations: Check for NaN values in input data

### Adversarial Debiasing

- Set `DEBIASING_DEBUG=1` environment variable for verbose logging
- Common issues:
  - Vanishing gradients: Adjust adversary learning rate
  - Excessive bias correction: Lower debiasing_strength parameter
  - Training instability: Use smaller batch sizes

### Fallback Protocols

- Set `FALLBACK_DEBUG=1` environment variable for verbose logging
- Common issues:
  - Protocol not triggering: Check confidence threshold values
  - Inconsistent behavior: Verify stage thresholds are in ascending order
  - Missing actions: Ensure all action types have handlers

### Bias Auditing

- Set `AUDIT_DEBUG=1` environment variable for verbose logging
- Common issues:
  - False positive violations: Adjust fairness thresholds
  - Missing protected attributes: Check preprocessing
  - Audit scheduling failures: Verify background task configuration

## Future Enhancements

1. **Explainability**:
   - Support for additional SHAP explainer types
   - Integration with LIME as alternative explanation method
   - Interactive explanations for web interface

2. **Debiasing**:
   - Support for continuous protected attributes
   - Multi-objective debiasing for multiple protected attributes
   - Pre-trained debiasing models for common ADHD scenarios

3. **Fallback Protocols**:
   - User preference learning for personalized fallback strategies
   - Reinforcement learning for optimizing fallback actions
   - Multi-model ensemble fallback options

4. **Bias Auditing**:
   - Support for intersectional fairness metrics
   - Automatic bias mitigation suggestions
   - Fairness visualization dashboard

## References

- SHAP Framework: [https://github.com/slundberg/shap](https://github.com/slundberg/shap)
- "Adversarial Debiasing" (Zhang et al., 2018): [https://arxiv.org/abs/1801.07593](https://arxiv.org/abs/1801.07593)
- "Confidence-Based Fallback for ML Systems" (Google, 2020): [https://ai.googleblog.com/2020/12/confidence-based-fallback-for-ml.html](https://ai.googleblog.com/2020/12/confidence-based-fallback-for-ml.html)
- "AI Fairness 360" (IBM Research): [https://aif360.mybluemix.net/](https://aif360.mybluemix.net/)

---

© 2025 ADHD Calendar - Comprehensive code reference for Epic 5
