#!/usr/bin/env python3
"""
Template Selector for ML Reasoning Templates.

This module selects and customizes ML reasoning templates based on the specific
ML task type and project context.
"""

import os
import sys
import argparse
import shutil
import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Any
from datetime import datetime

class MLTaskType:
    """ML task types for template selection."""
    NLP = "nlp"
    TIME_SERIES = "time_series"
    COMPUTER_VISION = "computer_vision"
    REINFORCEMENT_LEARNING = "reinforcement_learning"
    RECOMMENDATION = "recommendation"
    TABULAR = "tabular"
    ANOMALY_DETECTION = "anomaly_detection"
    CLUSTERING = "clustering"
    GENERAL = "general"
    # New task types for Epic 4
    MULTI_MODAL = "multi_modal"
    OPTIMIZATION = "optimization"
    SCHEDULE_REBALANCING = "schedule_rebalancing"
    PROGRESS_MONITORING = "progress_monitoring"
    CIRCADIAN_AWARE = "circadian_aware"

    @classmethod
    def get_epic4_domains(cls) -> List[str]:
        """Return domains relevant to Epic 4."""
        return [
            cls.REINFORCEMENT_LEARNING,
            cls.TIME_SERIES,
            cls.MULTI_MODAL,
            cls.OPTIMIZATION,
            cls.SCHEDULE_REBALANCING,
            cls.PROGRESS_MONITORING,
            cls.CIRCADIAN_AWARE
        ]

    @classmethod
    def map_to_research_domains(cls, domain: str) -> List[str]:
        """Map ML domain to relevant research domains from the provided literature."""
        research_mapping = {
            cls.REINFORCEMENT_LEARNING: [
                "Threshold-based RL architectures for ADHD populations",
                "Momentum-Aware RL with time-on-task decay models",
                "Ethical RL Frameworks with adversarial debiasing"
            ],
            cls.TIME_SERIES: [
                "Ultradian cycle alignment (90-minute focus/rest cycles)",
                "Personalized Chronotype Detection with federated learning",
                "Dynamic Light Exposure Adjustments for task-switching"
            ],
            cls.SCHEDULE_REBALANCING: [
                "Partial reinforcement schedules with dynamic reward shaping",
                "Causal ML for ADHD management interventions",
                "Equitable AI for preventing schedule optimization bias"
            ],
            cls.CIRCADIAN_AWARE: [
                "Sleep-wake phase predictions with differential privacy",
                "Circadian Rhythm optimization for ADHD cognitive performance",
                "40 lux blue light exposure effects on task-switching efficiency"
            ]
        }

        return research_mapping.get(domain, [])

class TaskComplexity:
    """Complexity levels for ML tasks."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class MLTemplateSelector:
    """Selects and customizes ML reasoning templates based on task type and context."""

    def __init__(self, templates_dir: str = None):
        """Initialize the template selector."""
        self.templates_dir = templates_dir or os.path.dirname(os.path.abspath(__file__))
        self.templates = self._load_templates()
        self.domain_specific_sections = self._load_domain_specific_sections()

    def _load_templates(self) -> Dict[str, str]:
        """Load all available templates."""
        templates = {}
        template_files = Path(self.templates_dir).glob("*_reasoning_template.md")

        for template_file in template_files:
            task_type = template_file.stem.replace("_reasoning_template", "")
            with open(template_file, "r") as f:
                templates[task_type] = f.read()

        return templates

    def _load_domain_specific_sections(self) -> Dict[str, Dict[str, str]]:
        """Load domain-specific sections for template customization."""
        domain_sections_path = os.path.join(self.templates_dir, "domain_specific_sections.json")

        if os.path.exists(domain_sections_path):
            with open(domain_sections_path, "r") as f:
                return json.load(f)

        # Default domain-specific sections if file doesn't exist
        return {
            "nlp": {
                "ML Architecture": "### NLP Architecture\n- **Model Type:** [e.g., Transformer, LSTM, etc.]\n- **Tokenization Approach:** [approach details]\n- **Embedding Strategy:** [strategy details]\n- **Contextual Features:** [features description]",
                "Ethical Considerations": "### NLP-Specific Ethical Considerations\n- **Language Bias Assessment:** [assessment details]\n- **Multilingual Support:** [support details]\n- **Cultural Context Awareness:** [awareness approach]"
            },
            "time_series": {
                "ML Architecture": "### Time Series Architecture\n- **Model Type:** [e.g., ARIMA, Prophet, RNN, etc.]\n- **Forecasting Horizon:** [horizon details]\n- **Seasonality Handling:** [approach details]\n- **Anomaly Detection:** [detection method]",
                "Data Requirements": "### Time Series Data Requirements\n- **Historical Data Span:** [time span required]\n- **Sampling Frequency:** [frequency details]\n- **Missing Data Strategy:** [strategy details]\n- **Seasonal Factors:** [factors to consider]"
            },
            "computer_vision": {
                "ML Architecture": "### Computer Vision Architecture\n- **Model Type:** [e.g., CNN, YOLO, etc.]\n- **Image Preprocessing:** [preprocessing details]\n- **Feature Extraction:** [extraction approach]\n- **Augmentation Strategy:** [strategy details]",
                "Ethical Considerations": "### Vision-Specific Ethical Considerations\n- **Facial Recognition Policy:** [policy details]\n- **Image Source Ethics:** [ethical considerations]\n- **Visual Privacy:** [privacy approach]"
            }
        }

    def select_template(self, task_type: str, project_context: Dict[str, Any] = None) -> str:
        """Select a template based on the task type and project context."""
        task_type = task_type.lower()

        # Default to general template if the specific one doesn't exist
        if task_type not in self.templates:
            task_type = MLTaskType.GENERAL

        template = self.templates[task_type]

        # Customize template based on project context if provided
        if project_context:
            template = self._customize_template(template, task_type, project_context)

        return template

    def _customize_template(self, template: str, task_type: str, context: Dict[str, Any]) -> str:
        """Customize the template based on task type and project context."""
        # Replace basic placeholders
        for key, value in context.items():
            placeholder = f"[{key}]"
            if isinstance(value, str) and placeholder in template:
                template = template.replace(placeholder, value)

        # Apply domain-specific section customizations if available
        if task_type in self.domain_specific_sections:
            for section_name, section_content in self.domain_specific_sections[task_type].items():
                section_pattern = f"## [0-9]+\\. {section_name}.*?(?=## [0-9]+\\.|$)"
                match = re.search(section_pattern, template, re.DOTALL)

                if match:
                    section_text = match.group(0)
                    enhanced_section = f"{section_text}\n\n{section_content}"
                    template = template.replace(section_text, enhanced_section)

        # Add complexity-specific considerations if applicable
        if "complexity" in context:
            complexity = context["complexity"].lower()
            if complexity == TaskComplexity.HIGH:
                template = self._add_high_complexity_sections(template, task_type)

        # Apply research insights if it's an Epic 4 domain
        if task_type in MLTaskType.get_epic4_domains():
            template = self.incorporate_research_insights(template, task_type)

        return template

    def _add_high_complexity_sections(self, template: str, task_type: str) -> str:
        """Add high-complexity considerations to the template."""
        # Add scalability section
        scalability_section = (
            "## 11. Scalability Considerations\n\n"
            "### Computational Requirements\n"
            "| Component | CPU/GPU Requirements | Memory Needs | Scaling Strategy |\n"
            "|-----------|----------------------|-------------|------------------|\n"
            "| [Component 1] | [Requirements] | [Memory] | [Strategy] |\n"
            "| [Component 2] | [Requirements] | [Memory] | [Strategy] |\n\n"
            "### Performance Optimization\n"
            "| Bottleneck | Detection Method | Optimization Approach | Expected Improvement |\n"
            "|------------|------------------|----------------------|----------------------|\n"
            "| [Bottleneck 1] | [Method] | [Approach] | [Improvement] |\n"
            "| [Bottleneck 2] | [Method] | [Approach] | [Improvement] |\n"
        )

        if "## 11." not in template:
            template += "\n\n" + scalability_section

        return template

    def incorporate_research_insights(self, template: str, task_type: str) -> str:
        """
        Enhances a template with relevant research insights from the literature.

        Args:
            template: The template to enhance
            task_type: The ML task type

        Returns:
            The enhanced template with research insights
        """
        research_insights = MLTaskType.map_to_research_domains(task_type)

        if not research_insights:
            return template

        # Create a section for research insights
        research_section = (
            "### Peer-Reviewed Research Insights\n\n"
            "Consider incorporating these research findings into your implementation:\n\n"
        )

        for insight in research_insights:
            research_section += f"- **{insight}**\n"

        research_section += "\n"

        # Add to Research Alignment section if it exists
        if "## 3. Research Alignment" in template:
            insert_position = template.find("## 3. Research Alignment") + len("## 3. Research Alignment")
            template = template[:insert_position] + "\n\n" + research_section + template[insert_position:]
        else:
            # Or add as a new section if it doesn't exist
            template += "\n## Research Insights\n\n" + research_section

        return template

    def generate_domain_template(self, task_type: str, template_path: Optional[str] = None) -> str:
        """Generate a new domain-specific template if it doesn't exist."""
        if task_type in self.templates:
            return f"Template for {task_type} already exists"

        # Start with the general template as a base
        base_template = self.templates.get(MLTaskType.GENERAL, "")

        # Create domain-specific template by modifying relevant sections
        domain_template = base_template.replace("General ML", f"{task_type.upper()} ML")

        # Save the new template if path is provided
        if template_path:
            with open(template_path, "w") as f:
                f.write(domain_template)

        # Add the template to the loaded templates
        template_filename = f"{task_type}_reasoning_template.md"
        full_path = os.path.join(self.templates_dir, template_filename)

        with open(full_path, "w") as f:
            f.write(domain_template)

        self.templates[task_type] = domain_template

        return f"Created new template for {task_type}"

    def list_available_templates(self) -> List[str]:
        """List all available templates."""
        return list(self.templates.keys())

    def update_domain_specific_sections(self, task_type: str, section_updates: Dict[str, str]) -> None:
        """Update domain-specific sections for a task type."""
        if task_type not in self.domain_specific_sections:
            self.domain_specific_sections[task_type] = {}

        for section_name, section_content in section_updates.items():
            self.domain_specific_sections[task_type][section_name] = section_content

        # Save updated domain-specific sections
        domain_sections_path = os.path.join(self.templates_dir, "domain_specific_sections.json")
        with open(domain_sections_path, "w") as f:
            json.dump(self.domain_specific_sections, f, indent=2)

    def get_domain_specific_sections(self, task_type: str) -> Dict[str, str]:
        """Get domain-specific sections for a task type."""
        return self.domain_specific_sections.get(task_type, {})

def detect_ml_domain(task_description: str) -> str:
    """
    Analyzes a task description and detects the most likely ML domain.

    Args:
        task_description: Description of the ML task

    Returns:
        The most likely ML domain category
    """
    # Convert to lowercase for easier matching
    description = task_description.lower()

    # Count occurrences of domain-related keywords
    domain_scores: Dict[str, int] = {
        MLTaskType.NLP: 0,
        MLTaskType.TIME_SERIES: 0,
        MLTaskType.COMPUTER_VISION: 0,
        MLTaskType.REINFORCEMENT_LEARNING: 0,
        MLTaskType.RECOMMENDATION: 0,
        MLTaskType.CLUSTERING: 0,
        MLTaskType.MULTI_MODAL: 0,
        MLTaskType.OPTIMIZATION: 0,
        MLTaskType.SCHEDULE_REBALANCING: 0,
        MLTaskType.PROGRESS_MONITORING: 0,
        MLTaskType.CIRCADIAN_AWARE: 0
    }

    # NLP-related keywords
    nlp_keywords = [
        "text", "language", "nlp", "sentiment", "topic", "document", "word",
        "sentence", "paragraph", "token", "bert", "gpt", "transformer",
        "embedding", "semantic", "syntax", "grammar", "translation"
    ]

    # Time-series related keywords
    time_series_keywords = [
        "time series", "time-series", "temporal", "forecast", "prediction",
        "sequence", "trend", "seasonal", "periodicity", "lstm", "arima",
        "prophet", "anomaly detection", "time window", "timestamp"
    ]

    # Computer vision related keywords
    vision_keywords = [
        "image", "vision", "computer vision", "video", "camera", "visual",
        "object detection", "recognition", "segmentation", "cnn", "convolutional",
        "yolo", "resnet", "pixel", "scene", "face", "gesture"
    ]

    # Reinforcement Learning related keywords
    rl_keywords = [
        "reinforcement", "rl", "agent", "environment", "reward", "action", "state",
        "policy", "q-learning", "dqn", "a3c", "ppo", "mdp", "markov", "trajectory",
        "episode", "adaptive schedule", "behavioral intervention"
    ]

    # Multi-modal related keywords
    multimodal_keywords = [
        "multi-modal", "multimodal", "cross-modal", "multiple modalities", "sensor fusion",
        "modality", "heterogeneous data", "multi-input", "wearable", "biometric", "calendar"
    ]

    # Optimization related keywords
    optimization_keywords = [
        "optimization", "scheduling", "allocate", "maximize", "minimize", "constraint",
        "objective function", "linear programming", "nonlinear", "combinatorial",
        "opportunity cost", "tradeoff", "utility", "resource allocation"
    ]

    # Schedule rebalancing keywords
    rebalancing_keywords = [
        "rebalance", "reschedule", "dynamic schedule", "adaptive scheduling", "task shift",
        "schedule adjustment", "reallocation", "priority adjustment", "time management",
        "executive function", "time blindness"
    ]

    # Progress monitoring keywords
    monitoring_keywords = [
        "monitor", "progress", "tracking", "real-time", "dashboard", "visualization",
        "alert", "notification", "completion rate", "performance metric", "milestone",
        "status update", "adaptive adjustment"
    ]

    # Circadian-aware keywords
    circadian_keywords = [
        "circadian", "sleep", "wake", "rhythm", "diurnal", "cycle", "chronotype",
        "morning", "evening", "ultradian", "energy level", "focus window", "sleep-wake",
        "light exposure", "90-minute cycle", "chronobiology"
    ]

    # Count keyword occurrences
    for keyword in nlp_keywords:
        if keyword in description:
            domain_scores[MLTaskType.NLP] += 1

    for keyword in time_series_keywords:
        if keyword in description:
            domain_scores[MLTaskType.TIME_SERIES] += 1

    for keyword in vision_keywords:
        if keyword in description:
            domain_scores[MLTaskType.COMPUTER_VISION] += 1

    for keyword in rl_keywords:
        if keyword in description:
            domain_scores[MLTaskType.REINFORCEMENT_LEARNING] += 1

    for keyword in multimodal_keywords:
        if keyword in description:
            domain_scores[MLTaskType.MULTI_MODAL] += 1

    for keyword in optimization_keywords:
        if keyword in description:
            domain_scores[MLTaskType.OPTIMIZATION] += 1

    for keyword in rebalancing_keywords:
        if keyword in description:
            domain_scores[MLTaskType.SCHEDULE_REBALANCING] += 1

    for keyword in monitoring_keywords:
        if keyword in description:
            domain_scores[MLTaskType.PROGRESS_MONITORING] += 1

    for keyword in circadian_keywords:
        if keyword in description:
            domain_scores[MLTaskType.CIRCADIAN_AWARE] += 1

    # Determine the most likely domain
    if max(domain_scores.values()) == 0:
        return MLTaskType.GENERAL

    # If there's a tie, prioritize Epic 4 domains
    max_score = max(domain_scores.values())
    candidates = [domain for domain, score in domain_scores.items() if score == max_score]

    for domain in MLTaskType.get_epic4_domains():
        if domain in candidates:
            return domain

    return max(domain_scores.items(), key=lambda x: x[1])[0]

def generate_from_template(
    template_name: str,
    output_path: str,
    replacements: Optional[Dict[str, str]] = None
) -> None:
    """
    Generates a new file from a template with optional replacements.

    Args:
        template_name: Name of the template file
        output_path: Path to save the generated file
        replacements: Dictionary of placeholders and their replacements
    """
    template_dir = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(template_dir, template_name)

    # Check if template exists
    if not os.path.exists(template_path):
        print(f"Error: Template {template_name} not found at {template_path}")
        return

    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(output_path)
    os.makedirs(output_dir, exist_ok=True)

    # If no replacements, just copy the file
    if not replacements:
        shutil.copy(template_path, output_path)
        print(f"Created {output_path} from template {template_name}")
        return

    # Apply replacements
    with open(template_path, 'r') as template_file:
        content = template_file.read()

    for placeholder, replacement in replacements.items():
        content = content.replace(placeholder, replacement)

    with open(output_path, 'w') as output_file:
        output_file.write(content)

    print(f"Created {output_path} from template {template_name} with custom replacements")

def main():
    """Main function to run the script."""
    parser = argparse.ArgumentParser(description="ML Reasoning Template Selector")
    parser.add_argument("--task", required=True, help="Description of the ML task")
    parser.add_argument("--domain", help="Explicitly specify the domain")
    parser.add_argument("--story-id", help="Story ID to include in the template")
    parser.add_argument("--epic", help="Epic to include in the template")
    parser.add_argument("--title", help="Title to include in the template")
    parser.add_argument("--output", required=True, help="Output file path")
    args = parser.parse_args()

    # Detect the domain if not specified
    domain = args.domain or detect_ml_domain(args.task)

    # Initialize the template selector
    selector = MLTemplateSelector()

    # Prepare context with provided details
    context = {}
    if args.story_id:
        context["Story ID"] = args.story_id
    if args.epic:
        context["Epic"] = args.epic
    if args.title:
        context["Title"] = args.title

    # Select the template
    template = selector.select_template(domain, context)

    # Generate the output file
    with open(args.output, "w") as f:
        f.write(template)

    print(f"Template for {domain} domain generated at {args.output}")

if __name__ == "__main__":
    main()
