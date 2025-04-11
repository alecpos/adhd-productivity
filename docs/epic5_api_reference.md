# ADHD Calendar: Epic 5 API Reference

**Version**: 1.0
**Last Updated**: 2025-06-15
**Target Audience**: Developers integrating with fairness components

## Overview

This document provides detailed API specifications for the fairness, bias mitigation, and ethical implementation components created in Epic 5. These APIs enable developers to integrate explainability, debiasing, fallback protocols, and bias auditing into the ADHD Calendar system.

## Table of Contents

1. [SHAP Explainability API](#shap-explainability-api)
2. [Adversarial Debiasing API](#adversarial-debiasing-api)
3. [Fallback Protocols API](#fallback-protocols-api)
4. [Bias Auditing API](#bias-auditing-api)
5. [Common Data Types](#common-data-types)
6. [Error Handling](#error-handling)
7. [Rate Limits](#rate-limits)

## SHAP Explainability API

The SHAP Explainability API provides methods for generating human-readable explanations for model predictions.

### Base Explainer

#### `create_explainer(model_type: str, model_instance: Any) → SHAPExplainer`

Creates a new explainer instance for the given model.

**Parameters**:
- `model_type`: String indicating the type of model ('productivity', 'duration', 'attention')
- `model_instance`: The trained model instance to explain

**Returns**:
- A specialized `SHAPExplainer` instance for the given model

**Example**:
```python
from app.ml.fairness.shap_explainer import create_explainer

# Create an explainer for a productivity model
explainer = create_explainer('productivity', productivity_model)
```

#### `SHAPExplainer.explain(input_data: Dict[str, Any], prediction: Any) → RecommendationExplanation`

Generate an explanation for a specific prediction.

**Parameters**:
- `input_data`: Dictionary of input features used for the prediction
- `prediction`: The model's prediction to explain

**Returns**:
- `RecommendationExplanation` object containing text and visual explanations

**Example**:
```python
# Get an explanation for a productivity prediction
explanation = explainer.explain(
    input_data={'time_of_day': 10, 'day_of_week': 2, 'task_type': 'writing'},
    prediction=0.85  # Productivity score
)

# Access the explanation
text_explanation = explanation.text
visual_data = explanation.visual
```

### Specialized Explainers

#### `ProductivitySHAPExplainer.explain_window(start_time: datetime, end_time: datetime, productivity_score: float) → RecommendationExplanation`

Explain why a specific time window has a particular productivity score.

**Parameters**:
- `start_time`: Start of the productivity window
- `end_time`: End of the productivity window
- `productivity_score`: The predicted productivity score

**Returns**:
- `RecommendationExplanation` for the productivity window

#### `DurationSHAPExplainer.explain_estimate(task_id: str, duration_minutes: int) → RecommendationExplanation`

Explain a task duration estimate.

**Parameters**:
- `task_id`: ID of the task
- `duration_minutes`: Estimated duration in minutes

**Returns**:
- `RecommendationExplanation` for the duration estimate

#### `AttentionSHAPExplainer.explain_recommendation(attention_state: Dict[str, Any], recommendation: str) → RecommendationExplanation`

Explain an attention management recommendation.

**Parameters**:
- `attention_state`: Current attention state data
- `recommendation`: Recommended attention management action

**Returns**:
- `RecommendationExplanation` for the attention recommendation

## Adversarial Debiasing API

The Adversarial Debiasing API provides methods for ensuring fairness in ML predictions.

### Core Debiasing Service

#### `get_debiasing_service() → DebiasingService`

Get the singleton instance of the debiasing service.

**Returns**:
- Singleton `DebiasingService` instance

**Example**:
```python
from app.ml.fairness.adversarial_debiasing import get_debiasing_service

# Get the debiasing service
debiasing_service = get_debiasing_service()
```

#### `DebiasingService.mitigate_bias(prediction: Dict[str, Any], protected_attributes: Dict[str, Any]) → Dict[str, Any]`

Apply debiasing to a model prediction.

**Parameters**:
- `prediction`: Original model prediction data
- `protected_attributes`: Dictionary of protected attribute values

**Returns**:
- Debiased prediction

**Example**:
```python
# Get debiased prediction
debiased_prediction = debiasing_service.mitigate_bias(
    prediction={'reminder_urgency': 0.8, 'suggested_time': '14:00'},
    protected_attributes={'age_group': '18-25', 'adhd_type': 'inattentive'}
)
```

#### `DebiasingService.train_debiasing_model(training_data: List[Dict[str, Any]], protected_attributes: List[str]) → None`

Train a new debiasing model using training data.

**Parameters**:
- `training_data`: List of training examples with features and outcomes
- `protected_attributes`: List of attribute names to protect from bias

### Model-Specific Debiasing

#### `DebiasingService.debias_reminder(reminder_data: Dict[str, Any], user_attributes: Dict[str, Any]) → Dict[str, Any]`

Apply debiasing specifically to reminder model outputs.

**Parameters**:
- `reminder_data`: Original reminder model output
- `user_attributes`: User attribute data including protected attributes

**Returns**:
- Debiased reminder data

#### `DebiasingService.debias_schedule_suggestion(suggestion: Dict[str, Any], user_attributes: Dict[str, Any]) → Dict[str, Any]`

Apply debiasing to schedule suggestions.

**Parameters**:
- `suggestion`: Original schedule suggestion
- `user_attributes`: User attribute data including protected attributes

**Returns**:
- Debiased schedule suggestion

## Fallback Protocols API

The Fallback Protocols API provides methods for handling uncertainty in ML predictions.

### Protocol Management

#### `get_fallback_manager() → FallbackManager`

Get the singleton instance of the fallback protocol manager.

**Returns**:
- Singleton `FallbackManager` instance

**Example**:
```python
from app.ml.fairness.fallback_protocols import get_fallback_manager

# Get the fallback manager
fallback_manager = get_fallback_manager()
```

#### `FallbackManager.register_protocol(model_id: str, protocol: FallbackProtocol) → None`

Register a fallback protocol for a specific model.

**Parameters**:
- `model_id`: Identifier for the model
- `protocol`: FallbackProtocol instance

**Example**:
```python
from app.ml.fairness.fallback_protocols import ProgressiveFallbackProtocol

# Create and register a progressive fallback protocol
protocol = ProgressiveFallbackProtocol(
    protocol_id="reminder_fallback",
    confidence_threshold=0.7,
    fallback_stages=[
        {"threshold": 0.7, "action": "notify", "message": "Lower confidence prediction"},
        {"threshold": 0.5, "action": "alternative", "alternatives": ["option1", "option2"]},
        {"threshold": 0.3, "action": "default", "default_value": "safe_default"}
    ]
)

fallback_manager.register_protocol("reminder_model", protocol)
```

### Protocol Application

#### `FallbackManager.apply_protocol(model_id: str, prediction: Any, confidence: float, context: Dict[str, Any] = None) → Dict[str, Any]`

Apply the registered fallback protocol for a model prediction.

**Parameters**:
- `model_id`: Identifier for the model
- `prediction`: The model's prediction
- `confidence`: Confidence score for the prediction (0-1)
- `context`: Optional context information

**Returns**:
- Result object with the fallback action and processed prediction

**Example**:
```python
# Apply fallback protocol to a prediction with low confidence
result = fallback_manager.apply_protocol(
    model_id="reminder_model",
    prediction={"time": "14:00", "message": "Start project research"},
    confidence=0.45,
    context={"user_id": "user123", "importance": "high"}
)

# Result contains the fallback action and processed prediction
action = result["action"]  # e.g., "alternative"
processed_prediction = result["prediction"]
```

### Predefined Protocols

#### `create_progressive_fallback(protocol_id: str, confidence_threshold: float, fallback_stages: List[Dict[str, Any]]) → ProgressiveFallbackProtocol`

Create a progressive fallback protocol with multiple stages.

**Parameters**:
- `protocol_id`: Identifier for the protocol
- `confidence_threshold`: Main confidence threshold
- `fallback_stages`: List of fallback stage configurations

**Returns**:
- Configured `ProgressiveFallbackProtocol` instance

#### `create_binary_fallback(protocol_id: str, confidence_threshold: float, default_value: Any) → BinaryFallbackProtocol`

Create a simple binary fallback protocol with a single threshold.

**Parameters**:
- `protocol_id`: Identifier for the protocol
- `confidence_threshold`: Confidence threshold
- `default_value`: Default value to use when confidence is below threshold

**Returns**:
- Configured `BinaryFallbackProtocol` instance

## Bias Auditing API

The Bias Auditing API provides methods for detecting and monitoring bias in model predictions.

### Audit Management

#### `get_bias_auditor() → BiasAuditor`

Get the singleton instance of the bias auditor.

**Returns**:
- Singleton `BiasAuditor` instance

**Example**:
```python
from app.ml.fairness.bias_auditing import get_bias_auditor

# Get the bias auditor
bias_auditor = get_bias_auditor()
```

#### `BiasAuditor.schedule_audit(model_id: str, frequency: str, metrics: List[str], protected_attributes: List[str]) → str`

Schedule a regular bias audit for a model.

**Parameters**:
- `model_id`: Identifier for the model to audit
- `frequency`: Audit frequency ('daily', 'weekly', 'monthly')
- `metrics`: List of fairness metrics to calculate
- `protected_attributes`: List of protected attributes to check

**Returns**:
- Audit job ID

**Example**:
```python
# Schedule a weekly audit of the reminder model
audit_job_id = bias_auditor.schedule_audit(
    model_id="reminder_model",
    frequency="weekly",
    metrics=["disparate_impact", "equal_opportunity"],
    protected_attributes=["age_group", "adhd_type"]
)
```

### On-Demand Auditing

#### `BiasAuditor.audit_predictions(predictions: List[Dict[str, Any]], outcomes: List[Any], protected_attributes: Dict[str, List[Any]], metrics: List[str] = None) → BiasAuditReport`

Perform an immediate bias audit on a set of predictions.

**Parameters**:
- `predictions`: List of model predictions
- `outcomes`: List of actual outcomes
- `protected_attributes`: Dictionary mapping attribute names to lists of values
- `metrics`: Optional list of fairness metrics to calculate

**Returns**:
- `BiasAuditReport` containing audit results

**Example**:
```python
# Perform an on-demand audit
report = bias_auditor.audit_predictions(
    predictions=[{"score": 0.8}, {"score": 0.6}, {"score": 0.9}],
    outcomes=[1, 0, 1],
    protected_attributes={
        "adhd_type": ["inattentive", "hyperactive", "combined"]
    },
    metrics=["demographic_parity", "equalized_odds"]
)

# Access audit results
fairness_scores = report.fairness_scores
violations = report.violations
recommendations = report.recommendations
```

#### `BiasAuditor.generate_report(audit_id: str) → BiasAuditReport`

Generate a detailed report for a completed audit.

**Parameters**:
- `audit_id`: ID of the completed audit

**Returns**:
- `BiasAuditReport` containing audit results

## Common Data Types

### `RecommendationExplanation`

Object representing an explanation for a model prediction.

**Properties**:
- `text`: String containing human-readable explanation
- `visual`: Base64-encoded image of feature importance plot
- `feature_importances`: Dictionary mapping features to importance values
- `top_features`: List of the most important features
- `confidence`: Confidence score for the explanation

### `BiasAuditReport`

Object representing the results of a bias audit.

**Properties**:
- `audit_id`: Unique identifier for the audit
- `model_id`: Identifier for the audited model
- `timestamp`: When the audit was performed
- `fairness_scores`: Dictionary mapping metrics to scores
- `violations`: List of fairness violations detected
- `recommendations`: List of recommendations to address bias
- `protected_attributes`: Protected attributes examined in the audit
- `data_summary`: Summary statistics of the audited data

## Error Handling

All API methods use consistent error handling with the following exception types:

- `InvalidModelError`: The specified model doesn't exist or isn't supported
- `ExplanationError`: Failed to generate an explanation
- `DebiasingError`: Error in the debiasing process
- `FallbackProtocolError`: Error in fallback protocol application
- `BiasAuditError`: Error during bias auditing

Each error includes:
- HTTP status code
- Error message
- Error code
- Suggested resolution

## Rate Limits

- **Explanation APIs**: 100 requests per minute
- **Debiasing APIs**: 200 requests per minute
- **Fallback Protocol APIs**: 500 requests per minute
- **Bias Auditing APIs**: 10 requests per minute

For higher limits, please contact the platform team.
