# Documentation Directory

This directory contains comprehensive documentation for the ADHD Calendar project.

## Overview

The docs directory houses all technical, user, and API documentation for the ADHD Calendar application. Documentation is organized by epic and component type to make information easily accessible.

## Documentation Structure

### Epic-Based Documentation

Documentation is organized primarily by the project's core epics:

- **Epic 1: Temporal Pattern Recognition**
  - [User Guide](epic1_user_guide.md)
  - [API Documentation](epic1_api.md)
  - [Integration Cookbook](epic1_integration_cookbook.md)
  - [Implementation Details](epic1_implementation.md)

- **Epic 2: Stochastic Time Estimation Engine**
  - [User Guide](epic2_user_guide.md)
  - [API Documentation](epic2_api.md)
  - [Integration Cookbook](epic2_integration_cookbook.md)
  - [Implementation Details](epic2_implementation.md)

- **Epic 3: Proactive Forgetfulness and Distraction Mitigation**
  - [User Guide](epic3_user_guide.md)
  - [API Documentation](epic3_api.md)
  - [Implementation Details](epic3_implementation.md)

- **Epic 4: Circadian Schedule Optimization**
  - [Visual Reference](epic4_visual_reference.md)

- **Epic 5: Fairness, Bias Mitigation, and Ethical Implementation**
  - [User Guide](epic5_user_guide.md)
  - [Technical Design](epic5_technical_design.md)
  - [API Reference](epic5_api_reference.md)
  - [Integration Guide](epic5_integration_guide.md)
  - [Code Reference](epic5_code_reference.md)

### Cross-Cutting Documentation

Documentation that applies across multiple epics:

- [Cross-Epic Integration Guide](cross_epic_integration_guide.md)
- [Comparative Research Analysis](comparative_research_analysis.md)
- [Database Schema](database_schema.md)
- [API Documentation](api_documentation.md)
- [API Design Guidelines](api_design_guidelines.md)
- [API Design Implementation Progress](api_design_implementation_progress.md)
- [Error Handling Guide](error_handling_guide.md)
- [Error Handling Implementation Progress](error_handling_implementation_progress.md)
- [API Standards Implementation Plan](api_standards_implementation_plan.md)
- [Authentication Flow](authentication_flow.md)
- [Testing Strategy](testing_strategy.md)
- [ML Models Documentation](ml_models.md)

### Technical Reference

- [Database Schema](database_schema.md)
- [Alembic Guide](alembic_guide.md)
- [SQLAlchemy Patterns](sqlalchemy_patterns.md)
- [Authentication Guide](authentication.md)
- [API Integration Examples](api_integration_examples.md)

### ML-Specific Documentation

- [ML Models Overview](ml_models.md)
- [TPR Models](tpr_models.md)
- [Time Estimation](time_estimation.md)
- [Forgetfulness Mitigation](forgetfulness_mitigation.md)
- [Hyperfold Module](hyperfold_module.md)

### Development Guides

- [Contributing Guide](contributing.md)
- [Development Setup](development_setup.md)
- [Testing Guide](testing_guide.md)
- [Code Style Guide](code_style_guide.md)

### User Documentation

- [User Guides](user_guides/)
- [Tutorial Videos](tutorials/)
- [FAQ](faq.md)
- [Troubleshooting](troubleshooting.md)

## Documentation Format

Documentation follows these standards:

- Markdown format for all documents
- Consistent headings and structure
- Code examples with syntax highlighting
- Diagrams using Mermaid syntax where appropriate
- Versioned documentation to match software releases

## Contributing to Documentation

When contributing to documentation:

1. Follow the established format and structure
2. Keep language clear and concise
3. Include code examples where appropriate
4. Update documentation when implementing new features
5. Ensure cross-references between related documents
6. Add explanatory diagrams for complex concepts

## Building Documentation

The documentation can be built into a searchable website using:

```bash
# Install documentation generator
pip install mkdocs

# Build the documentation site
mkdocs build

# Serve the documentation locally
mkdocs serve
```

Visit `http://localhost:8000` to view the documentation.

## Related Resources

- [Main Project README](../README.md)
- [Implementation Summaries](../EPIC1_Implementation_Summary.md) 