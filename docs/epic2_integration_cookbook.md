# Epic 2: Integration Cookbook - Stochastic Time Estimation Engine

## Overview

This cookbook provides comprehensive, practical examples for integrating the Stochastic Time Estimation Engine into your applications. This engine helps users with ADHD/neurodiversity challenges overcome time blindness by providing more accurate task duration estimates, analyzing task complexity through NLP, detecting contextual stressors, and calculating appropriate time buffers.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start Guide](#quick-start-guide)
3. [Bayesian Duration Prediction](#bayesian-duration-prediction)
4. [NLP Complexity Analysis](#nlp-complexity-analysis)
5. [Contextual Stressor Detection](#contextual-stressor-detection)
6. [Time Buffer Calculation](#time-buffer-calculation)
7. [Combining Components](#combining-components)
8. [Troubleshooting](#troubleshooting)
9. [Performance Optimization](#performance-optimization)
10. [Security and Privacy](#security-and-privacy)

## Prerequisites

- Python 3.9+
- Required packages installed (see `requirements.txt`)
- Access to the ADHD Calendar API
- Basic understanding of statistical/ML concepts

```bash
# Install required dependencies
pip install -r requirements.txt
```

## Quick Start Guide

Here's how to quickly integrate the Stochastic Time Estimation Engine:

```python
from app.models.time_estimation.bayesian_network import BayesianDurationPredictor
from app.models.time_estimation.nlp_analyzer import NLPComplexityAnalyzer
from app.services.time_estimation_service import TimeEstimationService

# Initialize the service
time_service = TimeEstimationService()

# Get time estimate for a task
user_id = "user123"
task_description = "Write documentation for the new API"
categories = ["writing", "technical"]

estimate = time_service.estimate_task_duration(
    user_id=user_id,
    task_description=task_description,
    categories=categories
)

print(f"Estimated task duration: {estimate.mean_minutes} minutes")
print(f"Confidence interval: {estimate.confidence_interval} minutes")
print(f"Recommended buffer: {estimate.buffer_minutes} minutes")
```

## Bayesian Duration Prediction

### Basic Integration

```python
from app.models.time_estimation.bayesian_network import BayesianDurationPredictor

# Initialize the predictor
predictor = BayesianDurationPredictor()

# Predict duration for a task
user_id = "user123"
task_metadata = {
    "category": "writing",
    "complexity": "medium",
    "familiarity": "high",
    "energy_level": "medium",
    "history": {
        "similar_tasks_count": 15,
        "average_duration": 45,
        "std_deviation": 12
    }
}

# Get prediction
prediction = predictor.predict_duration(user_id, task_metadata)
print(f"Predicted duration: {prediction.mean} minutes")
print(f"Prediction interval (95%): {prediction.interval_95}")
print(f"Distribution: {prediction.distribution_type}")
```

### Advanced Usage: Custom Priors and Model Training

```python
# Set custom Bayesian priors
custom_priors = {
    "writing": {
        "base_rate": 35.0,
        "complexity_factor": 1.5,
        "familiarity_discount": 0.8,
        "energy_multiplier": {
            "low": 1.4,
            "medium": 1.0,
            "high": 0.85
        }
    }
}

# Initialize with custom priors
predictor = BayesianDurationPredictor(custom_priors=custom_priors)

# Train the model with user-specific data
import pandas as pd

historical_data = pd.DataFrame({
    'task_id': ['task1', 'task2', 'task3', 'task4'],
    'category': ['writing', 'coding', 'writing', 'meeting'],
    'complexity': ['high', 'medium', 'medium', 'low'],
    'familiarity': ['low', 'high', 'medium', 'high'],
    'energy_level': ['high', 'medium', 'low', 'high'],
    'actual_duration': [65, 120, 55, 30]
})

# Update model with historical data
predictor.train(user_id, historical_data)

# Save and load user-specific model
predictor.save_user_model(user_id, 'user_models/user123_duration.pkl')
predictor.load_user_model(user_id, 'user_models/user123_duration.pkl')
```

## NLP Complexity Analysis

### Basic Integration

```python
from app.models.time_estimation.nlp_analyzer import NLPComplexityAnalyzer

# Initialize the analyzer
analyzer = NLPComplexityAnalyzer()

# Analyze task description complexity
task_description = "Create a presentation for the quarterly meeting that includes sales data, projections, and competitor analysis"

complexity = analyzer.analyze_complexity(task_description)
print(f"Task complexity score: {complexity.score}/10")
print(f"Complexity factors: {complexity.factors}")
print(f"Suggested duration modifier: {complexity.duration_modifier}")
```

### Advanced Usage: Custom Task Types and Keywords

```python
# Configure custom task types with complexity indicators
custom_task_types = {
    "technical_writing": {
        "keywords": ["documentation", "manual", "guide", "instructions"],
        "complexity_base": 0.7,
        "step_indicator_words": ["first", "then", "finally", "step"],
        "technical_terms": ["API", "function", "integration", "module"]
    },
    "creative_design": {
        "keywords": ["design", "create", "mockup", "prototype"],
        "complexity_base": 0.8,
        "scope_indicator_words": ["comprehensive", "detailed", "simple"],
        "technical_terms": ["layout", "wireframe", "UI", "UX"]
    }
}

# Initialize with custom configuration
analyzer = NLPComplexityAnalyzer(custom_task_types=custom_task_types)

# Process tasks with the custom analyzer
creative_task = "Design a comprehensive mockup for the new mobile app homepage"
technical_task = "Write documentation for the API integration module"

creative_complexity = analyzer.analyze_complexity(creative_task)
technical_complexity = analyzer.analyze_complexity(technical_task)

print(f"Creative task complexity: {creative_complexity.score}/10")
print(f"Technical task complexity: {technical_complexity.score}/10")
```

## Contextual Stressor Detection

### Basic Integration

```python
from app.models.time_estimation.stressor_detector import ContextualStressorDetector
import datetime

# Initialize the detector
detector = ContextualStressorDetector()

# Detect current stressors
user_id = "user123"
current_time = datetime.datetime.now()

stressors = detector.detect_stressors(
    user_id=user_id,
    timestamp=current_time,
    include_wearable_data=True
)

print(f"Detected stressors: {stressors.factors}")
print(f"Overall stress level: {stressors.level}")
print(f"Recommended time adjustment: +{stressors.time_adjustment}%")
```

### Advanced Usage: Custom Stressor Configuration and Wearable Integration

```python
from app.services.wearable_data_service import WearableDataService

# Get wearable data
wearable_service = WearableDataService()
heart_rate_data = wearable_service.get_heart_rate(user_id, hours=3)
hrv_data = wearable_service.get_heart_rate_variability(user_id, hours=3)
sleep_data = wearable_service.get_sleep_quality(user_id, days=1)

# Configure custom stressors
custom_stressors = {
    "environmental": {
        "weather_changes": {
            "source": "weather_api",
            "threshold": 0.7,
            "impact_factor": 1.2
        },
        "noise_level": {
            "source": "environment_monitor",
            "threshold": 65.0,  # dB
            "impact_factor": 1.3
        }
    },
    "personal": {
        "upcoming_deadlines": {
            "source": "calendar_api",
            "timeframe_hours": 24,
            "impact_factor": 1.5
        }
    }
}

# Initialize with custom configuration
detector = ContextualStressorDetector(custom_stressors=custom_stressors)

# Perform detection with custom wearable data
custom_stressors = detector.detect_stressors(
    user_id=user_id,
    timestamp=current_time,
    heart_rate_data=heart_rate_data,
    hrv_data=hrv_data,
    sleep_data=sleep_data,
    environmental_data={"noise_level": 70.5, "temperature": 78.3}
)

# Get time adjustment recommendation based on stressors
adjusted_duration = detector.adjust_duration(
    base_duration_minutes=45,
    stressors=custom_stressors,
    task_type="focus"
)

print(f"Adjusted duration: {adjusted_duration} minutes")
```

## Time Buffer Calculation

### Basic Integration

```python
from app.models.time_estimation.buffer_calculator import TimeBufferCalculator

# Initialize the calculator
buffer_calc = TimeBufferCalculator()

# Calculate appropriate buffer for a transition
user_id = "user123"
from_activity = "deep_work"
to_activity = "meeting"
location_change = True

buffer = buffer_calc.calculate_buffer(
    user_id=user_id,
    from_activity=from_activity,
    to_activity=to_activity,
    location_change=location_change
)

print(f"Recommended buffer time: {buffer.minutes} minutes")
print(f"Buffer breakdown: {buffer.breakdown}")
```

### Advanced Usage: Personalized Buffer Profiles

```python
# Create a custom buffer profile
custom_buffer_profile = {
    "transition_base": {
        "task_to_task": 5,
        "task_to_break": 2,
        "break_to_task": 10
    },
    "location_change": {
        "same_building": 10,
        "different_building": 25,
        "home_to_outside": 15
    },
    "activity_specific": {
        "from_deep_work": 15,
        "to_meeting": 8,
        "from_meeting": 5
    },
    "personal_factors": {
        "medication_timing": {
            "just_taken": 0,
            "wearing_off": 10
        },
        "time_of_day": {
            "morning": 5,
            "afternoon": 8,
            "evening": 12
        }
    }
}

# Initialize with custom profile
buffer_calc = TimeBufferCalculator(custom_buffer_profile=custom_buffer_profile)

# Calculate buffer with detailed context
detailed_buffer = buffer_calc.calculate_detailed_buffer(
    user_id=user_id,
    from_activity="deep_work",
    to_activity="meeting",
    location_change=True,
    location_change_type="different_building",
    time_of_day="afternoon",
    medication_status="wearing_off",
    energy_level="low"
)

print(f"Detailed buffer time: {detailed_buffer.minutes} minutes")
print(f"Detailed breakdown: {detailed_buffer.breakdown}")
print(f"Confidence level: {detailed_buffer.confidence}")

# Learn from user behavior
buffer_calc.learn_from_actual_transitions(
    user_id=user_id,
    transition_data=transition_history_df,
    learning_rate=0.2
)
```

## Combining Components

Here's how to combine all components of the Stochastic Time Estimation Engine:

```python
from app.services.time_estimation_service import TimeEstimationService
import datetime

# Initialize the service
time_service = TimeEstimationService()

# Create comprehensive time estimate for a task and schedule
user_id = "user123"
task = {
    "description": "Create wireframes for the new mobile app dashboard",
    "category": "design",
    "estimated_duration": 90,  # user's initial estimate in minutes
    "scheduled_start": datetime.datetime(2023, 6, 15, 13, 0), # 1:00 PM
    "previous_task": "team_meeting",
    "location_change": True
}

# Get comprehensive time estimate
comprehensive_estimate = time_service.get_comprehensive_estimate(
    user_id=user_id,
    task=task,
    include_complexity_analysis=True,
    include_stressor_detection=True,
    include_buffer_calculation=True,
    confidence_level=0.9
)

print("Comprehensive Time Estimate:")
print(f"Base duration: {comprehensive_estimate.base_duration} minutes")
print(f"Complexity adjustment: {comprehensive_estimate.complexity_adjustment} minutes")
print(f"Stressor adjustment: {comprehensive_estimate.stressor_adjustment} minutes")
print(f"Buffer time: {comprehensive_estimate.buffer_time} minutes")
print(f"Total estimated time: {comprehensive_estimate.total_time} minutes")
print(f"90% confidence interval: {comprehensive_estimate.confidence_interval}")
print(f"Recommended start time: {comprehensive_estimate.recommended_start_time}")
print(f"Recommended end time: {comprehensive_estimate.recommended_end_time}")
```

## Troubleshooting

Common issues and their solutions:

1. **Limited Historical Data Warning**
   ```
   Warning: Limited historical data for accurate Bayesian prediction
   ```
   **Solution**: Provide `minimum_confidence_level=0.7` to relax confidence requirements or use `fallback_estimation=True` to use category averages.

2. **NLP Analysis Timeout**
   ```
   Error: NLP analysis timed out after 5 seconds
   ```
   **Solution**: For long or complex task descriptions, use `analyzer.analyze_complexity(task_description, timeout=10, simplified=True)`.

3. **Wearable Data Connection Errors**
   ```
   Error: Could not connect to wearable data API
   ```
   **Solution**: Use `detector.detect_stressors(user_id, include_wearable_data=False, use_cached_data=True)` to fall back to non-wearable methods.

## Performance Optimization

For large-scale deployments:

```python
# Configure the service for high performance
from app.services.time_estimation_service import TimeEstimationService
from app.cache.redis_manager import RedisCacheManager

# Initialize cache
cache_manager = RedisCacheManager(
    expiration_time=1800,  # Cache results for 30 minutes
    max_cache_size_mb=150
)

# Create optimized service
time_service = TimeEstimationService(
    cache_manager=cache_manager,
    precompute_common_estimates=True,
    batch_processing=True
)

# Process batches of tasks for multiple users
tasks_batch = [
    {"user_id": "user1", "task_id": "task1", "description": "Design logo"},
    {"user_id": "user2", "task_id": "task2", "description": "Write report"},
    {"user_id": "user1", "task_id": "task3", "description": "Code feature"}
]

# Batch process estimates
batch_results = time_service.batch_estimate_durations(
    tasks_batch,
    parallel_processing=True,
    max_workers=4
)
```

## Security and Privacy

Ensure secure integration:

```python
from app.security.encryption import DataEncryption
from app.models.time_estimation.secure_client import SecureTimeEstimationClient

# Initialize encryption
encryption = DataEncryption(encryption_key=config.SECRET_KEY)

# Create secure client
secure_client = SecureTimeEstimationClient(
    user_id=user_id,
    encryption_service=encryption,
    secure_data_transfer=True,
    privacy_level="high"
)

# Use secure client for sensitive operations
secure_estimate = secure_client.get_duration_estimate(
    task_description="Prepare financial report",
    include_personal_factors=True
)

# Configure data retention policy
secure_client.configure_data_retention(
    store_historical_estimates=True,
    anonymize_after_days=30,
    delete_after_days=90
)
```

---

For additional examples and advanced use cases, refer to the [API Documentation](epic2_api.md) and [Implementation Details](epic2_implementation.md).
