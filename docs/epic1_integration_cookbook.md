# Epic 1: Integration Cookbook - Temporal Pattern Recognition (TPR) Models

## Overview

This cookbook provides comprehensive, practical examples for integrating the Temporal Pattern Recognition (TPR) Models into your applications. The TPR models help users understand their productivity patterns, optimize task scheduling based on circadian rhythms, analyze multi-factor correlations, and preserve privacy through federated learning.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start Guide](#quick-start-guide)
3. [LSTM Productivity Pattern Detection](#lstm-productivity-pattern-detection)
4. [Circadian Rhythm Optimization](#circadian-rhythm-optimization)
5. [Multi-Factor Correlation Analysis](#multi-factor-correlation-analysis)
6. [Federated Learning Integration](#federated-learning-integration)
7. [Combining TPR Components](#combining-tpr-components)
8. [Troubleshooting](#troubleshooting)
9. [Performance Optimization](#performance-optimization)
10. [Security Considerations](#security-considerations)

## Prerequisites

- Python 3.9+
- Required packages installed (see `requirements.txt`)
- Access to the ADHD Calendar API
- Basic understanding of ML concepts

```bash
# Install required dependencies
pip install -r requirements.txt
```

## Quick Start Guide

Here's how to quickly integrate the TPR models into your application:

```python
from app.models.tpr.lstm_productivity import ProductivityPatternDetector
from app.models.tpr.circadian_model import CircadianOptimizer
from app.services.tpr_service import TPRService

# Initialize the TPR service
tpr_service = TPRService()

# Get productivity insights for a user
user_id = "user123"
productivity_insights = tpr_service.get_productivity_patterns(user_id)

# Get optimal task scheduling based on circadian rhythms
task_id = "task456"
optimal_time = tpr_service.get_optimal_task_time(user_id, task_id)

print(f"Best time to schedule task: {optimal_time}")
```

## LSTM Productivity Pattern Detection

### Basic Integration

```python
from app.models.tpr.lstm_productivity import ProductivityPatternDetector
import pandas as pd

# Initialize the model
detector = ProductivityPatternDetector()

# Prepare user data
user_data = pd.DataFrame({
    'timestamp': ['2023-01-01 08:00', '2023-01-01 10:00', '2023-01-01 14:00'],
    'task_completed': [True, True, False],
    'focus_score': [8, 7, 4],
    # Additional features
})

# Get productivity patterns
patterns = detector.analyze_patterns(user_data)
print(patterns)

# Get productivity forecasts
future_productivity = detector.forecast_productivity(user_data, days_ahead=3)
print(future_productivity)
```

### Advanced Usage: Custom Model Training

```python
# Train with custom parameters
detector.train(
    user_data,
    epochs=50,
    batch_size=32,
    validation_split=0.2,
    lstm_units=128,
    dropout_rate=0.3
)

# Save the trained model
detector.save_model('user_specific_model.h5')

# Load a previously trained model
detector.load_model('user_specific_model.h5')
```

## Circadian Rhythm Optimization

### Basic Integration

```python
from app.models.tpr.circadian_model import CircadianOptimizer
import datetime

# Initialize the optimizer
optimizer = CircadianOptimizer()

# Get optimal times for different task types
user_id = "user123"
focus_task_time = optimizer.get_optimal_time(
    user_id,
    task_type="focus",
    duration_minutes=60
)

creative_task_time = optimizer.get_optimal_time(
    user_id,
    task_type="creative",
    duration_minutes=90
)

print(f"Best time for focus work: {focus_task_time}")
print(f"Best time for creative work: {creative_task_time}")
```

### Advanced Usage: Integrating Wearable Data

```python
# Import wearable data service
from app.services.wearable_data_service import WearableDataService

# Get wearable data
wearable_service = WearableDataService()
sleep_data = wearable_service.get_sleep_data(user_id, days=30)
activity_data = wearable_service.get_activity_data(user_id, days=30)

# Update circadian model with wearable data
optimizer.update_model_with_wearables(user_id, sleep_data, activity_data)

# Get enhanced optimal times
enhanced_focus_time = optimizer.get_optimal_time(
    user_id,
    task_type="focus",
    duration_minutes=60,
    use_wearable_data=True
)
```

## Multi-Factor Correlation Analysis

### Basic Integration

```python
from app.models.tpr.multifactor_analyzer import MultiFactorAnalyzer

# Initialize the analyzer
analyzer = MultiFactorAnalyzer()

# Analyze correlations between multiple factors
factors = [
    "sleep_duration",
    "medication_timing",
    "exercise_minutes",
    "screen_time",
    "caffeine_intake"
]

correlations = analyzer.analyze_correlations(user_id, factors, target="productivity_score")
print(correlations)

# Get insights in natural language
insights = analyzer.generate_insights(correlations)
for insight in insights:
    print(f"- {insight}")
```

### Advanced Usage: Custom Factor Analysis

```python
# Define custom factors and data sources
custom_factors = {
    "room_temperature": {
        "source": "smart_home_api",
        "transformation": lambda x: x * 1.8 + 32  # Convert to Fahrenheit
    },
    "noise_level": {
        "source": "environment_monitor",
        "transformation": None
    }
}

# Analyze with custom factors
custom_analysis = analyzer.analyze_with_custom_factors(
    user_id,
    standard_factors=factors,
    custom_factors=custom_factors,
    target="focus_duration"
)
```

## Federated Learning Integration

### Basic Integration

```python
from app.models.tpr.federated_learning import FederatedLearningClient

# Initialize federated learning client
fl_client = FederatedLearningClient(user_id)

# Participate in federated learning while preserving privacy
fl_client.participate_in_learning(
    model_type="productivity_pattern",
    local_data_only=True,
    privacy_level="high"
)

# Get insights from federated model
federated_insights = fl_client.get_federated_insights()
print(federated_insights)
```

### Advanced Usage: Custom Privacy Settings

```python
# Configure advanced privacy settings
from app.models.tpr.privacy_config import PrivacyConfig

privacy_config = PrivacyConfig(
    differential_privacy=True,
    epsilon=0.5,
    delta=1e-5,
    secure_aggregation=True,
    feature_masking=["medication_data", "location_data"]
)

# Use custom privacy configuration
fl_client.participate_in_learning(
    model_type="circadian_rhythm",
    privacy_config=privacy_config
)
```

## Combining TPR Components

Here's how to combine multiple TPR components for a comprehensive productivity solution:

```python
from app.services.tpr_service import TPRService
import datetime

# Initialize the TPR service
tpr_service = TPRService()

# Get user's productivity data
user_id = "user123"
start_date = datetime.datetime.now() - datetime.timedelta(days=30)
end_date = datetime.datetime.now()

# Comprehensive productivity analysis
comprehensive_analysis = tpr_service.get_comprehensive_analysis(
    user_id=user_id,
    start_date=start_date,
    end_date=end_date,
    include_productivity_patterns=True,
    include_circadian_analysis=True,
    include_multifactor_correlations=True,
    include_federated_insights=True
)

# Use analysis to optimize user's schedule
optimal_schedule = tpr_service.generate_optimal_schedule(
    user_id=user_id,
    tasks=["task1", "task2", "task3"],
    target_date=datetime.datetime.now() + datetime.timedelta(days=1),
    optimization_focus="productivity"  # Alternative: "well_being"
)

print(optimal_schedule)
```

## Troubleshooting

Common issues and their solutions:

1. **Insufficient Data Warning**
   ```
   Warning: Not enough data points for reliable pattern detection
   ```
   **Solution**: Ensure at least 14 days of user data is available. Use the `minimum_data_points` parameter to adjust requirements.

2. **Model Convergence Issues**
   ```
   Warning: Model did not converge after 100 epochs
   ```
   **Solution**: Try increasing `max_epochs` or adjusting learning rate with `learning_rate=0.001`.

3. **Privacy Constraint Errors**
   ```
   Error: Cannot process request due to privacy constraints
   ```
   **Solution**: Check privacy settings and ensure user has consented to data usage. Try increasing privacy level with `privacy_level="high"`.

## Performance Optimization

For large-scale deployments:

```python
# Configure caching for performance
from app.services.tpr_service import TPRService
from app.cache.redis_manager import RedisCacheManager

# Initialize cache
cache_manager = RedisCacheManager(
    expiration_time=3600,  # Cache results for 1 hour
    max_cache_size_mb=100
)

# Use cached TPR service
tpr_service = TPRService(cache_manager=cache_manager)

# Configure batch processing for multiple users
user_ids = ["user1", "user2", "user3", "user4"]
batch_results = tpr_service.batch_process_users(
    user_ids=user_ids,
    analysis_type="productivity_patterns",
    parallel_processing=True,
    max_workers=4
)
```

## Security Considerations

Ensure secure integration:

```python
from app.security.encryption import DataEncryption
from app.models.tpr.secure_tpr_client import SecureTPRClient

# Initialize encryption
encryption = DataEncryption(encryption_key=config.SECRET_KEY)

# Create secure TPR client
secure_tpr = SecureTPRClient(
    user_id=user_id,
    encryption_service=encryption,
    secure_data_transfer=True,
    audit_logging=True
)

# Use secure client for sensitive operations
secure_results = secure_tpr.get_productivity_insights(
    include_sensitive_data=True
)
```

---

For additional examples and advanced use cases, refer to the [API Documentation](epic1_api.md) and [Implementation Details](epic1_implementation.md).
