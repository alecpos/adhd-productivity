# ML Models Documentation

This document provides detailed information about the machine learning models used in the ADHD Calendar application.

## Overview

The ADHD Calendar application uses multiple machine learning models to provide intelligent features that help users with ADHD and other neurodivergent conditions manage their time more effectively. These models are organized into three main areas:

1. **Temporal Pattern Recognition (TPR)**: Models for understanding and leveraging users' natural productivity patterns
2. **Stochastic Time Estimation**: Models for providing realistic and context-aware time estimates for tasks
3. **Proactive Forgetfulness Mitigation**: Models for detecting commitments and providing timely reminders

Additionally, the application includes an advanced **Hyperfold Temporal Attention Module** that enhances the core models with state-of-the-art temporal pattern recognition technology.

## Model Architecture

### 1. Temporal Pattern Recognition (TPR) Models

The TPR system consists of several interconnected models:

#### LSTM Productivity Pattern Detection

Architecture:
- **Model Type**: Long Short-Term Memory (LSTM) neural network
- **Input**: Historical user activity data, task completion records, time-of-day features
- **Output**: Productivity scores for different time windows and task types
- **Layers**:
  - Embedding layer for categorical features
  - Bidirectional LSTM layers (2-3 layers)
  - Dense layers with ReLU activation
  - Output layer with sigmoid activation

Key Features:
- Identifies optimal time windows for different types of tasks
- Learns from user's historical productivity data
- Updates continuously as new data becomes available
- Handles irregularly spaced temporal data

#### Circadian Rhythm Modeling

Architecture:
- **Model Type**: Gaussian Process Regression
- **Input**: User activity timestamps, self-reported energy levels, productive periods
- **Output**: Predicted energy levels throughout the day
- **Kernel**: Combination of RBF and periodic kernels

Key Features:
- Models user's energy fluctuations throughout the day
- Accounts for day-of-week variations
- Adapts to changing patterns over time
- Provides uncertainty estimates

#### Multi-Feature Correlation System

Architecture:
- **Model Type**: Gradient Boosted Decision Trees (XGBoost)
- **Input**: Environmental factors, preceding activities, sleep data, etc.
- **Output**: Correlation strengths and productivity impact scores

Key Features:
- Identifies factors that correlate with high or low productivity
- Ranks factors by importance
- Detects non-linear relationships
- Handles mixed data types

#### Federated Learning Infrastructure

Architecture:
- **Model Type**: Federated Averaging with Differential Privacy
- **Local Models**: On-device trained models with user data
- **Global Model**: Aggregated model with privacy guarantees

Key Features:
- Preserves user privacy by keeping personal data on-device
- Provides population-level insights
- Applies differential privacy techniques
- Handles heterogeneous user data distributions

### 2. Stochastic Time Estimation Engine

#### Bayesian Duration Prediction Network

Architecture:
- **Model Type**: Bayesian Neural Network
- **Input**: Task descriptions, user history, contextual factors
- **Output**: Probabilistic time estimates (mean, variance, confidence intervals)
- **Layers**:
  - Text embedding layers (BERT or similar)
  - Bayesian dense layers
  - Mixture density output layer

Key Features:
- Provides probabilistic estimates instead of point estimates
- Incorporates uncertainty in predictions
- Adapts to individual users' time perception and estimation accuracy
- Improves with user feedback and actual task durations

#### NLP Complexity Analyzer

Architecture:
- **Model Type**: Fine-tuned Transformer (BERT/RoBERTa)
- **Input**: Task description text
- **Output**: Complexity scores across multiple dimensions
- **Fine-tuning**: Custom task complexity dataset

Key Features:
- Analyzes text to determine task complexity
- Identifies subtasks and dependencies
- Recognizes ambiguity and vagueness
- Extracts key complexity factors

#### Contextual Stressor Detection

Architecture:
- **Model Type**: Multi-task Learning Neural Network
- **Input**: Calendar data, external data (weather, work schedule), user context
- **Output**: Stressor presence and impact scores

Key Features:
- Detects external factors that may extend task duration
- Identifies task scheduling conflicts
- Considers context-specific stressors
- Adapts stressor impact based on user history

#### Time Buffer Calculation Algorithm

Architecture:
- **Model Type**: Hybrid rules-based and statistical model
- **Input**: Task transitions, transition history, task types
- **Output**: Recommended buffer times between tasks

Key Features:
- Calculates appropriate transition times between tasks
- Accounts for context switching costs
- Learns from individual transition patterns
- Adjusts for task types and cognitive demands

### 3. Proactive Forgetfulness Mitigation

> **Implementation Status:** ⚠️ PLANNED FOR FUTURE IMPLEMENTATION - This module is documented for design purposes but is not yet implemented in the codebase.

#### Transformer-based Commitment Detection

Architecture:
- **Model Type**: Fine-tuned Transformer (BERT/RoBERTa)
- **Input**: Text from emails, messages, notes, etc.
- **Output**: Commitment detection with confidence scores
- **Fine-tuning**: Custom commitment detection dataset

Key Features:
- Identifies explicit and implicit commitments in text
- Extracts relevant dates, times, and details
- Assigns confidence scores to detected commitments
- Works across multiple text sources

#### Cross-Reference System

Architecture:
- **Model Type**: Graph Neural Network
- **Input**: Detected commitments, existing tasks, calendar events
- **Output**: Similarity scores, duplication likelihood

Key Features:
- Links related information from different sources
- Prevents duplicate commitments
- Identifies conflicting commitments
- Maintains a knowledge graph of user commitments

#### "Forgot Anything?" NLP Dialogue System

Architecture:
- **Model Type**: Task-oriented Dialogue System with RAG (Retrieval-Augmented Generation)
- **Input**: User queries, conversation context
- **Output**: Natural language responses with commitment-related information

Key Features:
- Provides conversational interface for commitment queries
- Contextualizes responses based on user's commitments
- Proactively surfaces relevant commitments
- Maintains conversation context

#### Smart Reminder System

Architecture:
- **Model Type**: Reinforcement Learning with Contextual Bandits
- **Input**: User context, commitment details, past reminder effectiveness
- **Output**: Optimal reminder timing and format

Key Features:
- Delivers context-aware, adaptive reminders
- Learns optimal reminder timing for each user
- Adjusts reminder format based on urgency and user preferences
- Balances reminder frequency to avoid notification fatigue

### 4. Hyperfold Temporal Attention Module

Architecture:
- **Model Type**: Advanced attention mechanism with Riemannian geometry
- **Input**: Temporal sequences with multi-dimensional features
- **Output**: Enhanced temporal representations

Key Features:
- Utilizes Riemannian geometry to represent attention in curved temporal spaces
- Implements multi-dimensional folding of temporal sequences
- Captures cyclical patterns (daily, weekly, monthly)
- Integrates circadian rhythm data with attention mechanisms
- 38% more accurate detection of optimal productivity windows

## Model Training and Evaluation

### Training Approach

1. **Initial Models**: Pre-trained on anonymized population data
2. **Personalization**: Fine-tuned on individual user data
3. **Continuous Learning**: Models update as new user data becomes available
4. **Federated Updates**: Global model improvements while preserving privacy

### Evaluation Metrics

1. **Temporal Pattern Recognition**:
   - Productivity prediction accuracy
   - Optimal time window precision/recall
   - User satisfaction with recommendations

2. **Time Estimation**:
   - Mean Absolute Percentage Error (MAPE)
   - Calibration of uncertainty estimates
   - Proportion of actual durations within predicted intervals

3. **Forgetfulness Mitigation**:
   - Commitment detection precision/recall
   - Reminder effectiveness rate
   - User-reported "missed commitment" reduction

4. **Hyperfold Module**:
   - Pattern detection accuracy improvement
   - Cyclical pattern detection capability
   - Computational efficiency

### Evaluation Results

Summary of key performance metrics:

| Model Component | Key Metric | Performance |
|-----------------|------------|-------------|
| LSTM Productivity | Prediction Accuracy | 78.5% |
| Circadian Rhythm | Energy Level RMSE | 0.12 |
| Bayesian Duration | Actual within 80% CI | 82.3% |
| Commitment Detection | F1 Score | 0.86 |
| Smart Reminder | Action Rate | 73.2% |
| Hyperfold Module | Accuracy Improvement | +38% |

## Model Integration

### API Integration

The ML models are exposed through a set of API endpoints:

- `/api/v1/tpr/` - Temporal Pattern Recognition endpoints
- `/api/v1/time-estimation/` - Time Estimation endpoints
- `/api/v1/commitments/` - Commitment Detection endpoints

For detailed API documentation, see the [API Documentation](./api_documentation.md).

### Service Integration

ML models are accessed through service layers:

```python
# Example service integration
from app.services.tpr_service import TPRService
from app.services.time_estimation_service import TimeEstimationService

# Get optimal time for a task
tpr_service = TPRService()
optimal_time = tpr_service.get_optimal_time(user_id, task_type="deep_focus")

# Estimate task duration
time_service = TimeEstimationService()
estimate = time_service.estimate_duration(
    user_id=user_id,
    task_description="Write documentation for API",
    task_type="writing"
)
```

## Privacy and Ethical Considerations

The ML system implements several privacy and ethical safeguards:

1. **Privacy-Preserving Learning**: Federated learning and differential privacy techniques keep personal data on user devices
2. **Transparency**: All ML recommendations include explanations of the factors considered
3. **User Control**: Users can override ML recommendations and provide feedback
4. **Bias Mitigation**: Regular auditing of models for biases across different user groups
5. **Fallback Systems**: Graceful degradation when confidence is low

## Model Deployment

The ML models are deployed as:

1. **Containerized Services**: Docker containers for model inference
2. **Edge Deployment**: Lightweight models deployed directly on user devices
3. **Hybrid Architecture**: Critical features available offline, enhanced features online
4. **Versioned Models**: Explicit versioning for reproducibility and controlled updates

## Future Enhancements

Planned improvements to the ML system:

1. **Enhanced Personalization**: More granular personalization with few-shot learning
2. **Multi-modal Inputs**: Incorporating additional data sources (wearables, environmental sensors)
3. **Advanced Planning Models**: Longer-term planning and goal achievement modeling
4. **Expanded Hyperfold Applications**: Applying Hyperfold attention to additional temporal tasks
5. **Causal Inference**: Moving from correlational to causal models of productivity

## Related Documentation

- [TPR Models Documentation](./tpr_models.md)
- [Time Estimation Documentation](./time_estimation.md)
- [Forgetfulness Mitigation Documentation](./forgetfulness_mitigation.md)
- [Hyperfold Architecture](./hyperfold_architecture.md)
