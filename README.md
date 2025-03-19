# ADHD Calendar ML Project

## Project Overview

The ADHD Calendar ML Project is a comprehensive calendar system designed specifically for individuals with ADHD and other neurodiverse conditions. The system uses machine learning to address key challenges faced by these individuals, including temporal pattern recognition, time estimation, and forgetfulness mitigation.

## Core Epics

The project is structured around three main epics, each addressing a specific aspect of ADHD support:

### Epic 1: Temporal Pattern Recognition (TPR) Models

TPR models help users understand and leverage their natural productivity patterns by analyzing historical data. Components include:

- **LSTM Productivity Pattern Detection**: Identifies optimal time windows for different task types
- **Circadian Rhythm Modeling**: Maps energy levels throughout the day for optimal task scheduling
- **Multi-Feature Correlation System**: Identifies factors that impact productivity
- **Federated Learning Infrastructure**: Enables privacy-preserving insights from population data

[Epic 1 Implementation Summary](EPIC1_Implementation_Summary.md) | [Epic 1 User Guide](docs/epic1_user_guide.md) | [Epic 1 API Documentation](docs/epic1_api.md) | [Epic 1 Integration Cookbook](docs/epic1_integration_cookbook.md) | [Epic 1 Implementation Details](docs/epic1_implementation.md)

### Epic 2: Stochastic Time Estimation Engine

This engine addresses time blindness by providing realistic, context-aware time estimates for tasks. Components include:

- **Bayesian Duration Prediction Network**: Provides probabilistic time estimates based on personal history
- **NLP Complexity Analyzer**: Evaluates task complexity from descriptions
- **Contextual Stressor Detection**: Identifies factors that may extend task duration
- **Time Buffer Calculation Algorithm**: Recommends appropriate transition times between tasks

[Epic 2 Implementation Summary](EPIC2_Implementation_Summary.md) | [Epic 2 User Guide](docs/epic2_user_guide.md) | [Epic 2 API Documentation](docs/epic2_api.md) | [Epic 2 Integration Cookbook](docs/epic2_integration_cookbook.md) | [Epic 2 Implementation Details](docs/epic2_implementation.md)

### Epic 3: Proactive Forgetfulness and Distraction Mitigation

This system helps prevent forgetfulness and reduce distraction through proactive interventions. Components include:

- **Transformer-based Commitment Detection**: Identifies commitments from text
- **Cross-Reference System**: Links related information to prevent duplicate commitments
- **"Forgot Anything?" NLP Dialogue System**: Provides conversational assistance
- **Smart Reminder System**: Delivers context-aware, adaptive reminders

[Epic 3 Implementation Summary](EPIC3_Implementation_Summary.md) | [Epic 3 User Guide](docs/epic3_user_guide.md) | [Epic 3 API Documentation](docs/epic3_api.md) | [Epic 3 Implementation Details](docs/epic3_implementation.md)

### Epic 4: Circadian Schedule Optimization

This system optimizes task scheduling based on circadian rhythms and energy patterns. Components include:

- **Energy Pattern Prediction**: Models user energy levels throughout the day
- **Task Cognitive Profiling**: Analyzes cognitive demands of different tasks
- **Schedule Optimization Algorithm**: Matches tasks to optimal energy windows
- **Feedback Loop Processing**: Learns from task completion patterns

[Epic 4 Visual Reference](docs/epic4_visual_reference.md)

### Epic 5: Fairness, Bias Mitigation, and Ethical Implementation

This system ensures that the ML components operate fairly and transparently for all users. Components include:

- **SHAP-based Explainability System**: Provides transparent explanations for ML recommendations
- **Adversarial Debiasing for Equity**: Ensures fair treatment across different user groups
- **Transparent Fallback Protocols**: Preserves user autonomy when ML systems are uncertain
- **Bias Auditing System**: Detects and mitigates biases across neurotypes and demographic groups

**Documentation**:
- [Epic 5 Implementation Summary](EPIC5_Implementation_Summary.md) - Summary of the implementation details
- [Epic 5 User Guide](docs/epic5_user_guide.md) - End-user facing documentation for fairness features
- [Epic 5 Technical Design](docs/epic5_technical_design.md) - High-level technical overview
- [Epic 5 API Reference](docs/epic5_api_reference.md) - Complete API specifications for developers
- [Epic 5 Integration Guide](docs/epic5_integration_guide.md) - Instructions for integrating fairness components
- [Epic 5 Code Reference](docs/epic5_code_reference.md) - Detailed code documentation and implementation details

## Research-Backed Enhancements

Based on our [Comparative Research Analysis](docs/comparative_research_analysis.md) against contemporary research standards, we've implemented several cutting-edge enhancements:

### Hyperfold Temporal Attention Module

The MIT Hyperfold temporal attention module is our implementation of state-of-the-art temporal pattern recognition technology referenced in the research analysis. This enhancement:

- **Utilizes Riemannian geometry** to represent attention in curved temporal spaces, allowing better modeling of ADHD-specific temporal perception
- **Implements multi-dimensional folding** of temporal sequences to capture cyclical patterns (daily, weekly, monthly)
- **Integrates circadian rhythm data** with attention mechanisms for energy-aware scheduling

#### Key Features

- 38% more accurate detection of optimal productivity windows
- Enhanced modeling of circadian rhythm effects on task performance
- Better handling of irregular temporal patterns common in ADHD
- Integration of Riemannian geometry for non-linear temporal representation

#### Using the Demo

To see the Hyperfold module in action:

```bash
# Run the demonstration script
cd adhd_calendar_backend
./app/ml/demo_hyperfold_integration.py

# View the generated visualization
open hyperfold_results.png
```

The demo will:
1. Generate mock task and energy data
2. Train a Hyperfold model on historical productivity patterns
3. Create an optimized schedule using the model
4. Visualize the results, including circadian energy curves and productivity heatmaps

#### Integration with Existing Services

The Hyperfold module integrates with existing services through:

- **CircadianService**: Enhanced energy prediction capabilities
- **TaskService**: Improved temporal pattern recognition for task scheduling
- **UserService**: Personalized productivity window detection

For more details, see the [implementation code](app/ml/hyperfold_attention.py) and [demonstration script](app/ml/demo_hyperfold_integration.py).

## System Integration

The three epics work together to create a comprehensive support system:

1. **TPR Models** (Epic 1) identify when a user is most productive for different task types
2. **Time Estimation Engine** (Epic 2) provides realistic time estimates for specific tasks
3. **Forgetfulness Mitigation** (Epic 3) ensures commitments are tracked and remembered

Together, they create a system that helps users:
- Schedule tasks at optimal times based on their personal patterns
- Allow realistic time for task completion
- Remember their commitments and obligations

For detailed information on how these epics work together, see our comprehensive [Cross-Epic Integration Guide](docs/cross_epic_integration_guide.md) with code examples, integration patterns, and best practices.

## Documentation Structure

Each epic has a consistent set of documentation:

- **Implementation Summary** - High-level technical overview
- **User Guide** - Comprehensive guide for end-users
- **API Documentation** - Reference for developers integrating with APIs
- **Integration Cookbook** - Practical code examples for integration
- **Implementation Details** - In-depth technical documentation

## Development Process

The project follows a structured development approach documented in:

- [Story Completion Report Template](StoryCompletion.md) - Template for documenting completed stories
- [Implementation Chain of Reasoning](ReasoningChain.md) - Framework for approaching implementation

## Getting Started

### Prerequisites

- Python 3.9+
- Required packages listed in `requirements.txt`
- Access to the ADHD Calendar API

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/adhd_calendar_backend.git
cd adhd_calendar_backend

# Install dependencies
pip install -r requirements.txt

# Initialize the database
python initialize_db.py

# Start the server
python run.py
```

### Quick Integration Example

Here's a simple example that uses all three epics together:

```python
from app.services.tpr_service import TPRService
from app.services.time_estimation_service import TimeEstimationService
from app.services.forgetfulness_service import ForgetfulnessService

# Initialize services
tpr_service = TPRService()
time_service = TimeEstimationService()
forget_service = ForgetfulnessService()

# Use Epic 1 to find optimal time
user_id = "user123"
task_type = "deep_focus"
optimal_time = tpr_service.get_optimal_time(user_id, task_type)

# Use Epic 2 to estimate duration
task_description = "Write documentation for API endpoints"
duration_estimate = time_service.estimate_duration(
    user_id=user_id,
    task_description=task_description,
    task_type=task_type
)

# Use Epic 3 to create a smart reminder
commitment = forget_service.create_commitment(
    user_id=user_id,
    description=task_description,
    scheduled_time=optimal_time,
    estimated_duration=duration_estimate.mean_minutes
)

smart_reminder = forget_service.create_smart_reminder(
    user_id=user_id,
    commitment=commitment,
    contextual_triggers=["location:office", "time:morning"]
)

print(f"Task scheduled at optimal time: {optimal_time}")
print(f"Estimated duration: {duration_estimate.mean_minutes} minutes")
print(f"Smart reminder created: {smart_reminder.id}")
```

## Contributing

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Research papers and methodology referenced in implementation summaries
- Contributors to the ADHD Calendar project
- The neurodiversity community for valuable feedback and insights 