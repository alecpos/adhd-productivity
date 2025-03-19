# ADHD Calendar: Epic 5 Integration Guide

**Version**: 1.0  
**Last Updated**: 2025-06-15  
**Target Audience**: Developers integrating fairness components

## Overview

This integration guide provides detailed instructions for incorporating the fairness, bias mitigation, and ethical implementation components from Epic 5 into the ADHD Calendar system. Following these guidelines will ensure that your ML models benefit from explainability, bias mitigation, and proper fallback protocols.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Integration Architecture](#integration-architecture)
3. [Integrating SHAP Explainability](#integrating-shap-explainability)
4. [Integrating Adversarial Debiasing](#integrating-adversarial-debiasing)
5. [Integrating Fallback Protocols](#integrating-fallback-protocols)
6. [Integrating Bias Auditing](#integrating-bias-auditing)
7. [Frontend Integration](#frontend-integration)
8. [Testing Your Integration](#testing-your-integration)
9. [Common Issues and Solutions](#common-issues-and-solutions)
10. [Performance Considerations](#performance-considerations)

## Prerequisites

Before integrating Epic 5 components, ensure you have:

- Access to the ADHD Calendar codebase (v2.5 or higher)
- Python 3.10+ environment with dependencies installed
- Understanding of the existing ML models (from Epics 1-4)
- Basic knowledge of fairness concepts in ML
- Frontend development environment (for explanation UI integration)

Required packages:
```
shap==0.40.0
matplotlib==3.5.1
tensorflow==2.9.0
numpy==1.22.3
pandas==1.4.2
aioredis==2.0.1
sqlalchemy==1.4.36
```

## Integration Architecture

The Epic 5 components are designed as layers that wrap around the existing ML models:

```
┌────────────────────────┐
│     User Interface     │
└───────────┬────────────┘
            │
┌───────────▼────────────┐
│    Application Logic    │
└───────────┬────────────┘
            │
┌───────────▼────────────┐
│  Epic 5: Fairness Layer │
│  ┌──────────────────┐  │
│  │  Bias Auditing   │  │
│  └──────────────────┘  │
│  ┌──────────────────┐  │
│  │    Debiasing     │  │
│  └──────────────────┘  │
│  ┌──────────────────┐  │
│  │ Fallback Protocol│  │
│  └──────────────────┘  │
│  ┌──────────────────┐  │
│  │  Explainability  │  │
│  └──────────────────┘  │
└───────────┬────────────┘
            │
┌───────────▼────────────┐
│   ML Models (Epic 1-4)  │
└────────────────────────┘
```

## Integrating SHAP Explainability

### Step 1: Import the SHAP Explainer

```python
from app.ml.fairness.shap_explainer import create_explainer, SHAPExplainer
```

### Step 2: Create an Explainer for your Model

For each model requiring explanations, create a dedicated explainer:

```python
# For a productivity model
productivity_explainer = create_explainer(
    model_type='productivity',
    model_instance=your_productivity_model
)

# For a duration prediction model
duration_explainer = create_explainer(
    model_type='duration',
    model_instance=your_duration_model
)
```

### Step 3: Generate Explanations for Predictions

Whenever your model makes a prediction that needs explanation:

```python
# Prepare input data (same format used for prediction)
input_data = {
    'time_of_day': 10,
    'day_of_week': 2,
    'task_type': 'writing',
    'energy_level': 'high',
    'focus_level': 'medium'
}

# Make prediction
prediction = your_productivity_model.predict(input_data)

# Generate explanation
explanation = productivity_explainer.explain(
    input_data=input_data,
    prediction=prediction
)

# Access explanation components
text_explanation = explanation.text
visual_explanation = explanation.visual  # Base64 encoded image
feature_importances = explanation.feature_importances
```

### Step 4: Store Explanations with Predictions

Update your database schema to store explanations alongside predictions:

```python
# Example SQLAlchemy model update
class ProductivityPrediction(Base):
    __tablename__ = "productivity_predictions"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    prediction = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # New fields for explanations
    explanation_text = Column(Text, nullable=True)
    explanation_visual = Column(Text, nullable=True)  # Base64 encoded
    explanation_features = Column(JSON, nullable=True)
```

## Integrating Adversarial Debiasing

### Step 1: Import the Debiasing Service

```python
from app.ml.fairness.adversarial_debiasing import get_debiasing_service
```

### Step 2: Apply Debiasing to Predictions

Whenever your model makes a prediction that might be affected by bias:

```python
# Get the singleton debiasing service
debiasing_service = get_debiasing_service()

# Original prediction from your model
original_prediction = {
    'reminder_urgency': 0.8,
    'suggested_time': '14:00',
    'message': 'Start working on project'
}

# User's protected attributes
user_attributes = {
    'age_group': '18-25',
    'adhd_type': 'inattentive',
    'gender': 'non_binary'
}

# Apply debiasing
debiased_prediction = debiasing_service.mitigate_bias(
    prediction=original_prediction,
    protected_attributes=user_attributes
)

# Use the debiased prediction
# ...
```

### Step 3: Model-Specific Debiasing

For specific model types, use the specialized debiasing methods:

```python
# For reminder models
debiased_reminder = debiasing_service.debias_reminder(
    reminder_data=reminder_model_output,
    user_attributes=user_attributes
)

# For schedule suggestions
debiased_suggestion = debiasing_service.debias_schedule_suggestion(
    suggestion=scheduler_model_output,
    user_attributes=user_attributes
)
```

### Step 4: Train Debiasing Models with Your Data

For optimal performance, train the debiasing models with your application's data:

```python
# Prepare training data
training_data = [
    {'features': {...}, 'outcome': 1, 'adhd_type': 'inattentive', 'age_group': '18-25'},
    {'features': {...}, 'outcome': 0, 'adhd_type': 'hyperactive', 'age_group': '26-40'},
    # ...
]

# Specify which attributes to protect
protected_attributes = ['adhd_type', 'age_group', 'gender']

# Train the debiasing model
debiasing_service.train_debiasing_model(
    training_data=training_data,
    protected_attributes=protected_attributes
)
```

## Integrating Fallback Protocols

### Step 1: Import the Fallback Manager

```python
from app.ml.fairness.fallback_protocols import (
    get_fallback_manager,
    ProgressiveFallbackProtocol,
    BinaryFallbackProtocol
)
```

### Step 2: Define Fallback Protocols for Your Models

For each model that needs fallback handling:

```python
# Get the fallback manager
fallback_manager = get_fallback_manager()

# Create a progressive fallback protocol for complex models
reminder_protocol = ProgressiveFallbackProtocol(
    protocol_id="reminder_fallback",
    confidence_threshold=0.7,
    fallback_stages=[
        {"threshold": 0.7, "action": "notify", "message": "This is a lower confidence reminder"},
        {"threshold": 0.5, "action": "alternative", "alternatives": ["option1", "option2"]},
        {"threshold": 0.3, "action": "default", "default_value": {"time": "12:00", "message": "Default reminder"}}
    ]
)

# Create a simple binary fallback for simpler models
focus_protocol = BinaryFallbackProtocol(
    protocol_id="focus_fallback",
    confidence_threshold=0.6,
    default_value="medium_focus"
)

# Register the protocols
fallback_manager.register_protocol("reminder_model", reminder_protocol)
fallback_manager.register_protocol("focus_model", focus_protocol)
```

### Step 3: Apply Fallback Protocols to Predictions

Whenever your model makes a prediction, apply the appropriate fallback protocol:

```python
# Make prediction with confidence score
prediction = your_model.predict(input_data)
confidence = your_model.get_confidence(input_data)

# Apply fallback protocol
result = fallback_manager.apply_protocol(
    model_id="reminder_model",
    prediction=prediction,
    confidence=confidence,
    context={"user_id": "user123", "importance": "high"}
)

# Handle the result based on the fallback action
action = result["action"]
processed_prediction = result["prediction"]

if action == "notify":
    # Just show the prediction with a confidence note
    show_prediction(processed_prediction, low_confidence=True)
elif action == "alternative":
    # Show multiple options
    show_alternatives(processed_prediction, result["alternatives"])
elif action == "default":
    # Use the safe default
    show_default_option(processed_prediction)
```

## Integrating Bias Auditing

### Step 1: Import the Bias Auditor

```python
from app.ml.fairness.bias_auditing import get_bias_auditor, BiasAuditReport
```

### Step 2: Schedule Regular Audits

Set up regular audits for your models:

```python
# Get the bias auditor
bias_auditor = get_bias_auditor()

# Schedule a weekly audit of the reminder model
audit_job_id = bias_auditor.schedule_audit(
    model_id="reminder_model",
    frequency="weekly",
    metrics=["disparate_impact", "equal_opportunity", "demographic_parity"],
    protected_attributes=["age_group", "adhd_type", "gender"]
)

# Store the audit job ID for later reference
save_audit_job_id(audit_job_id)
```

### Step 3: Implement Audit Data Collection

Ensure your system collects the necessary data for auditing:

```python
# Example: Setting up data collection middleware
class BiasAuditDataCollector:
    def __init__(self, bias_auditor):
        self.bias_auditor = bias_auditor
        self.prediction_buffer = []
    
    async def collect_prediction_data(self, user_id, model_id, prediction, actual_outcome=None):
        # Get user attributes
        user = await get_user(user_id)
        protected_attributes = {
            "adhd_type": user.adhd_type,
            "age_group": user.age_group,
            "gender": user.gender
        }
        
        # Store prediction data
        self.prediction_buffer.append({
            "model_id": model_id,
            "prediction": prediction,
            "outcome": actual_outcome,
            "user_id": user_id,
            "protected_attributes": protected_attributes,
            "timestamp": datetime.utcnow()
        })
        
        # Periodically flush buffer to storage
        if len(self.prediction_buffer) >= 100:
            await self.flush_buffer()
    
    async def flush_buffer(self):
        # Save to database for later auditing
        await save_prediction_data(self.prediction_buffer)
        self.prediction_buffer = []
```

### Step 4: Implement Audit Report Handling

Set up a process to review and act on audit reports:

```python
# Example: Scheduled task to review audit reports
async def review_audit_reports():
    bias_auditor = get_bias_auditor()
    
    # Get recent audit reports
    audit_ids = await get_recent_audit_ids()
    for audit_id in audit_ids:
        report = bias_auditor.generate_report(audit_id)
        
        # Check for fairness violations
        if report.violations:
            # Alert administrators
            await send_fairness_alert(report)
            
            # Log detailed information
            logger.warning(f"Fairness violations detected in audit {audit_id}: {report.violations}")
            
            # Apply mitigation if available
            if report.recommendations:
                for recommendation in report.recommendations:
                    await apply_fairness_recommendation(recommendation)
```

## Frontend Integration

### Displaying Explanations in the UI

```javascript
// Example React component for displaying explanations
function PredictionExplanation({ explanation }) {
  return (
    <div className="explanation-container">
      <div className="explanation-text">{explanation.text}</div>
      
      {explanation.visual && (
        <div className="explanation-visual">
          <img src={`data:image/png;base64,${explanation.visual}`} 
               alt="Feature importance visualization" />
        </div>
      )}
      
      <div className="explanation-features">
        <h4>Key Factors:</h4>
        <ul>
          {explanation.top_features.map(feature => (
            <li key={feature.name}>
              <span className="feature-name">{feature.display_name}</span>: 
              <span className="feature-impact">{feature.impact_percentage}%</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
```

### Handling Fallback Protocol UI

```javascript
// Example React component for handling fallback results
function FallbackHandler({ fallbackResult }) {
  const { action, prediction, message, alternatives } = fallbackResult;

  switch (action) {
    case 'notify':
      return (
        <div className="fallback-notification">
          <div className="prediction-content">{renderPrediction(prediction)}</div>
          <div className="confidence-notice">{message}</div>
        </div>
      );
      
    case 'alternative':
      return (
        <div className="fallback-alternatives">
          <div className="alternatives-prompt">
            We're not completely confident. Please choose an option:
          </div>
          <div className="alternatives-list">
            {alternatives.map((alt, index) => (
              <button 
                key={index}
                className="alternative-option"
                onClick={() => selectAlternative(alt)}
              >
                {renderAlternative(alt)}
              </button>
            ))}
          </div>
        </div>
      );
      
    case 'default':
      return (
        <div className="fallback-default">
          <div className="default-notice">
            We couldn't make a confident prediction, so we're using a safe default.
          </div>
          <div className="prediction-content">{renderPrediction(prediction)}</div>
        </div>
      );
      
    default:
      return (
        <div className="prediction-content">{renderPrediction(prediction)}</div>
      );
  }
}
```

## Testing Your Integration

### SHAP Explainability Tests

```python
def test_productivity_explanation():
    # Arrange
    explainer = create_explainer('productivity', mock_productivity_model)
    input_data = {'time_of_day': 10, 'day_of_week': 2, 'task_type': 'writing'}
    prediction = 0.85
    
    # Act
    explanation = explainer.explain(input_data, prediction)
    
    # Assert
    assert explanation is not None
    assert explanation.text is not None
    assert "time of day" in explanation.text.lower()
    assert explanation.feature_importances is not None
    assert len(explanation.top_features) > 0
```

### Adversarial Debiasing Tests

```python
@pytest.mark.asyncio
async def test_reminder_debiasing():
    # Arrange
    debiasing_service = get_debiasing_service()
    reminder_data = {
        'reminder_urgency': 0.8,
        'suggested_time': '14:00',
        'message': 'Start working on project'
    }
    user_attributes = {
        'adhd_type': 'inattentive',
        'age_group': '18-25',
        'gender': 'female'
    }
    
    # Act
    debiased_reminder = debiasing_service.debias_reminder(
        reminder_data=reminder_data,
        user_attributes=user_attributes
    )
    
    # Assert
    assert debiased_reminder is not None
    assert 'reminder_urgency' in debiased_reminder
    assert 'suggested_time' in debiased_reminder
    
    # Check that values have been adjusted
    assert debiased_reminder != reminder_data
```

### Fallback Protocol Tests

```python
def test_progressive_fallback():
    # Arrange
    fallback_manager = get_fallback_manager()
    protocol = ProgressiveFallbackProtocol(
        protocol_id="test_protocol",
        confidence_threshold=0.7,
        fallback_stages=[
            {"threshold": 0.7, "action": "notify", "message": "Low confidence"},
            {"threshold": 0.5, "action": "alternative", "alternatives": ["opt1", "opt2"]},
            {"threshold": 0.3, "action": "default", "default_value": "default_value"}
        ]
    )
    fallback_manager.register_protocol("test_model", protocol)
    
    # Act - high confidence
    result_high = fallback_manager.apply_protocol(
        model_id="test_model",
        prediction="predicted_value",
        confidence=0.9
    )
    
    # Act - medium confidence
    result_medium = fallback_manager.apply_protocol(
        model_id="test_model",
        prediction="predicted_value",
        confidence=0.6
    )
    
    # Act - low confidence
    result_low = fallback_manager.apply_protocol(
        model_id="test_model",
        prediction="predicted_value",
        confidence=0.2
    )
    
    # Assert
    assert result_high["action"] is None  # No fallback
    assert result_medium["action"] == "notify"
    assert result_low["action"] == "default"
    assert result_low["prediction"] == "default_value"
```

### Bias Auditing Tests

```python
@pytest.mark.asyncio
async def test_bias_audit():
    # Arrange
    bias_auditor = get_bias_auditor()
    predictions = [
        {"score": 0.8}, {"score": 0.6}, {"score": 0.9},
        {"score": 0.7}, {"score": 0.5}, {"score": 0.8}
    ]
    outcomes = [1, 0, 1, 1, 0, 1]
    protected_attributes = {
        "adhd_type": ["inattentive", "hyperactive", "combined", 
                      "inattentive", "hyperactive", "combined"]
    }
    
    # Act
    report = bias_auditor.audit_predictions(
        predictions=predictions,
        outcomes=outcomes,
        protected_attributes=protected_attributes,
        metrics=["demographic_parity"]
    )
    
    # Assert
    assert report is not None
    assert "demographic_parity" in report.fairness_scores
    assert isinstance(report.violations, list)
    assert isinstance(report.recommendations, list)
```

## Common Issues and Solutions

### Explanation Generation Performance

**Issue**: Generating explanations is computationally expensive and slows down responses.

**Solution**: Implement asynchronous explanation generation and caching:

```python
# Implement a cached explanation service
class CachedExplanationService:
    def __init__(self, cache_ttl=3600):  # 1 hour TTL
        self.cache = {}
        self.cache_ttl = cache_ttl
        self.explainers = {}
    
    def get_explainer(self, model_type, model_instance):
        if model_type not in self.explainers:
            self.explainers[model_type] = create_explainer(model_type, model_instance)
        return self.explainers[model_type]
    
    async def get_explanation(self, model_type, model_instance, input_data, prediction):
        # Create cache key
        cache_key = self._create_cache_key(model_type, input_data, prediction)
        
        # Check cache
        if cache_key in self.cache and self._is_cache_valid(cache_key):
            return self.cache[cache_key]["explanation"]
        
        # Generate explanation asynchronously
        explanation = await self._generate_explanation_async(
            model_type, model_instance, input_data, prediction
        )
        
        # Cache the result
        self.cache[cache_key] = {
            "explanation": explanation,
            "timestamp": time.time()
        }
        
        return explanation
    
    async def _generate_explanation_async(self, model_type, model_instance, input_data, prediction):
        # Get the appropriate explainer
        explainer = self.get_explainer(model_type, model_instance)
        
        # Run explanation generation in a thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        explanation = await loop.run_in_executor(
            None, 
            lambda: explainer.explain(input_data, prediction)
        )
        
        return explanation
    
    def _create_cache_key(self, model_type, input_data, prediction):
        # Create a deterministic cache key from the inputs
        input_str = json.dumps(input_data, sort_keys=True)
        pred_str = str(prediction)
        return f"{model_type}:{input_str}:{pred_str}"
    
    def _is_cache_valid(self, cache_key):
        # Check if cache entry is still valid
        entry_time = self.cache[cache_key]["timestamp"]
        return (time.time() - entry_time) < self.cache_ttl
```

### Debiasing Without Sacrificing Accuracy

**Issue**: Debiasing sometimes reduces overall model accuracy.

**Solution**: Use a gradual approach with tunable debiasing strength:

```python
# When initializing the debiasing service
debiasing_service = get_debiasing_service()
debiasing_service.set_debiasing_strength(0.7)  # 70% strength

# Or adjust per prediction
debiased_prediction = debiasing_service.mitigate_bias(
    prediction=original_prediction,
    protected_attributes=user_attributes,
    debiasing_strength=0.8  # 80% strength for this prediction
)
```

### Handling Missing Protected Attributes

**Issue**: User hasn't provided some protected attributes needed for debiasing.

**Solution**: Implement attribute inference while respecting privacy:

```python
def get_protected_attributes(user_id):
    # Get user profile
    user = get_user(user_id)
    
    # Start with explicitly provided attributes
    protected_attributes = {}
    
    if user.adhd_type:
        protected_attributes["adhd_type"] = user.adhd_type
    
    if user.age_group:
        protected_attributes["age_group"] = user.age_group
    
    if user.gender:
        protected_attributes["gender"] = user.gender
    
    # For missing attributes, use aggregate values when available
    if "adhd_type" not in protected_attributes and user.interactions:
        # Infer from interaction patterns, not personally identifying
        protected_attributes["adhd_type"] = infer_adhd_type_from_interactions(user.interactions)
    
    # Ensure we're using attribute buckets, not specific values
    if "age" in protected_attributes:
        protected_attributes["age_group"] = convert_age_to_group(protected_attributes["age"])
        del protected_attributes["age"]
    
    return protected_attributes
```

## Performance Considerations

1. **Explanation Caching**: Cache explanations for frequently used predictions
2. **Batch Processing**: Run bias audits during off-peak hours
3. **Selective Explanation**: Only generate explanations for important decisions
4. **Progressive Loading**: Load explanation visuals after text explanations
5. **Asynchronous Debiasing**: Process debiasing in background when possible

For production deployments with high traffic:

```python
# Example: Configure explanation settings for high traffic
EXPLANATION_CONFIG = {
    "cache_ttl": 3600,  # Cache explanations for 1 hour
    "background_generation": True,  # Generate in background
    "visual_explanation_limit": 100,  # Limit visual explanations per minute
    "feature_limit": 5,  # Show only top 5 features
    "explanation_log_sample_rate": 0.1  # Log only 10% of explanations
}

# Apply configuration
explanation_service = CachedExplanationService(
    cache_ttl=EXPLANATION_CONFIG["cache_ttl"]
)
explanation_service.enable_background_generation(
    EXPLANATION_CONFIG["background_generation"]
)
explanation_service.set_visual_rate_limit(
    EXPLANATION_CONFIG["visual_explanation_limit"]
)
```

---

© 2025 ADHD Calendar - Fair and ethical AI for everyone 