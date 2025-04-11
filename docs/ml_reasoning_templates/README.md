# ML Reasoning Templates

This directory contains templates for structuring ML task reasoning and implementation planning. These templates help ensure consistent, thorough consideration of important aspects when implementing ML features.

## Available Templates

The following domain-specific templates are available:

- **General ML**: For general machine learning tasks
- **NLP**: For natural language processing tasks
- **Time Series**: For time series analysis and forecasting
- **Computer Vision**: For image and video processing tasks
- **Reinforcement Learning**: For RL and agent-based systems
- **Recommendation Systems**: For personalization and recommendation features
- **Tabular ML**: For structured, tabular data analysis
- **Anomaly Detection**: For outlier and anomaly identification
- **Clustering**: For unsupervised grouping tasks

Additional templates can be generated dynamically for specialized domains as needed.

## Using the Template Selector

The `template_selector.py` module provides a dynamic template selection and customization system. It adapts templates based on the ML task type and project context.

### Basic Usage

```python
from docs.ml_reasoning_templates.template_selector import MLTemplateSelector, MLTaskType

# Initialize the template selector
selector = MLTemplateSelector()

# Get a template for a specific ML task type
template = selector.select_template(MLTaskType.NLP)

# Save the template to a new file
with open("nlp_task_reasoning.md", "w") as f:
    f.write(template)
```

### Customizing Templates

You can customize templates by providing a project context:

```python
# Create a context with project-specific details
project_context = {
    "Story ID": "STORY-2.4",
    "Epic": "Epic 2",
    "Title": "Sentiment Analysis for User Feedback",
    "Priority": "High",
    "Complexity": "Medium"
}

# Get a customized template
custom_template = selector.select_template(MLTaskType.NLP, project_context)
```

### Creating New Domain Templates

If you need a template for a new domain, you can generate one:

```python
# Generate a new template for a custom domain
selector.generate_domain_template("graph_neural_networks",
                                 "graph_nn_reasoning_template.md")
```

### Extending Domain-Specific Sections

You can add or update domain-specific sections:

```python
# Add custom sections for a domain
custom_sections = {
    "ML Architecture": "### Graph Neural Network Architecture\n- **Model Type:** [e.g., GCN, GAT, etc.]\n- **Node Features:** [feature description]\n- **Edge Features:** [feature description]\n- **Readout Function:** [function details]"
}

selector.update_domain_specific_sections("graph_neural_networks", custom_sections)
```

## Template Structure

Each template follows a consistent structure with sections for:

1. **Problem Analysis**: Understanding the problem and success criteria
2. **Component Mapping**: Identifying affected components and required changes
3. **Research Alignment**: Connecting to research and literature
4. **Development Approach**: Planning implementation details
5. **Ethical Considerations**: Addressing ethical implications
6. **Implementation Plan**: Breaking down work into phases
7. **Risk Assessment**: Identifying and mitigating risks
8. **Documentation Plan**: Planning necessary documentation
9. **Cross-Epic Integration**: Connecting with other epics
10. **Definition of Done**: Clear completion criteria

Domain-specific templates add specialized sections relevant to that ML domain.

## Best Practices

- Complete all sections of the template for comprehensive planning
- Update sections as you learn more during implementation
- Link to specific research papers and code references where applicable
- Include diagrams for complex data flows and architectures
- Be specific about metrics and evaluation criteria
- Document all ethical considerations thoroughly
- Include time estimates for each implementation phase
- Identify dependencies early

## Customization

Templates can be customized by:

1. Editing the markdown template files directly
2. Adding new domain-specific templates
3. Updating the domain-specific sections in `domain_specific_sections.json`
4. Extending the `MLTemplateSelector` class for more complex customization

## Integration with Workflow

These templates are designed to be integrated with your ML development workflow:

1. Start each new ML task by selecting and filling out the appropriate template
2. Include the completed template in task documentation
3. Reference the template during implementation
4. Update the template as you refine your approach
5. Use the template to facilitate code reviews and knowledge sharing

## Contribution

To contribute new templates or improvements:

1. Create a new template file or edit an existing one
2. Add domain-specific sections to the `domain_specific_sections.json` file
3. Update this README with any new template information
4. Submit a PR with your changes
