# Machine Learning Directory

This directory contains the machine learning models and algorithms for the ADHD Calendar application.

## Overview

The ML directory implements the three core ML features of the ADHD Calendar:

1. **Temporal Pattern Recognition (TPR) Models** - Help users understand and leverage their natural productivity patterns
2. **Stochastic Time Estimation Engine** - Addresses time blindness with realistic, context-aware time estimates
3. **Proactive Forgetfulness Mitigation** - Prevents forgetfulness through proactive interventions

## Core Models

### Temporal Pattern Recognition (TPR)

- **LSTM Productivity Pattern Detection**: Identifies optimal time windows for different task types
- **Circadian Rhythm Modeling**: Maps energy levels throughout the day
- **Multi-Feature Correlation System**: Identifies factors impacting productivity
- **Federated Learning Infrastructure**: Enables privacy-preserving insights

### Stochastic Time Estimation Engine

- **Bayesian Duration Prediction Network**: Provides probabilistic time estimates
- **NLP Complexity Analyzer**: Evaluates task complexity from descriptions
- **Contextual Stressor Detection**: Identifies factors that may extend task duration
- **Time Buffer Calculation Algorithm**: Recommends transition times between tasks

### Forgetfulness Mitigation

- **Transformer-based Commitment Detection**: Identifies commitments from text
- **Cross-Reference System**: Links related information to prevent duplicate commitments
- **"Forgot Anything?" NLP Dialogue System**: Provides conversational assistance
- **Smart Reminder System**: Delivers context-aware, adaptive reminders

### Hyperfold Temporal Attention Module

Advanced temporal pattern recognition technology that:
- Utilizes Riemannian geometry to represent attention in curved temporal spaces
- Implements multi-dimensional folding of temporal sequences
- Integrates circadian rhythm data with attention mechanisms

## Usage

Each ML module is exposed through a corresponding service in the `app/services` directory. These services provide high-level interfaces for the application to interact with the ML models.

## Demo Scripts

- `demo_hyperfold_integration.py`: Demonstrates the Hyperfold module with visualizations
- `demo_tpr_models.py`: Showcases the TPR models with sample data
- `demo_time_estimation.py`: Illustrates time estimation capabilities

## Development

When extending or modifying ML models:
1. Update model implementation in this directory
2. Update corresponding service in `app/services`
3. Add tests in `app/tests/ml`
4. Update documentation in `docs`

## Documentation

- [ML Models Documentation](../../docs/ml_models.md)
- [TPR Models Documentation](../../docs/tpr_models.md)
- [Time Estimation Documentation](../../docs/time_estimation.md)
- [Forgetfulness Mitigation Documentation](../../docs/forgetfulness_mitigation.md)
- [Hyperfold Module Documentation](../../docs/hyperfold_module.md) 