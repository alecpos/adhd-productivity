"""
Machine Learning Technical Debt Patterns.

This module defines specific technical debt patterns related to machine learning
and particularly those relevant to Epic 4: Dynamic Schedule Rebalancing.
"""

from enum import Enum, auto
from typing import Dict, List, Any


class MLDebtSubcategory(Enum):
    """Subcategories for ML-specific technical debt."""

    REPRODUCIBILITY = "reproducibility"
    MODEL_COMPLEXITY = "model_complexity"
    DATA_QUALITY = "data_quality"
    EVALUATION = "evaluation"
    ETHICAL_CONCERNS = "ethical_concerns"
    DOCUMENTATION = "documentation"
    OPTIMIZATION = "optimization"
    ADAPTABILITY = "adaptability"
    REINFORCEMENT_LEARNING = "reinforcement_learning"
    MONITORING = "monitoring"
    CIRCADIAN = "circadian"


# ML-specific technical debt patterns for Epic 4
EPIC4_TECH_DEBT_PATTERNS = [
    # Reinforcement learning debt
    {
        "pattern": r"reward\s*=\s*\d+\.?\d*",
        "message": "Hardcoded reward values reduce adaptability and make it difficult to tune reinforcement learning algorithms",
        "category": "ML_SPECIFIC",
        "severity": "HIGH",
        "type": "hardcoded_rewards",
        "subcategory": MLDebtSubcategory.REINFORCEMENT_LEARNING,
        "epic": "Epic 4",
        "remediation": "Implement configurable reward functions based on behavioral objectives",
        "research_reference": "Journal of Attention Disorders (2025) - Partial reinforcement schedules with dynamic reward shaping",
    },
    {
        "pattern": r"class\s+\w+Agent.*?def\s+act.*?return\s+np\.argmax",
        "message": "RL agent lacks exploration strategy, may get stuck in local optima",
        "category": "ML_SPECIFIC",
        "severity": "HIGH",
        "type": "missing_exploration",
        "subcategory": MLDebtSubcategory.REINFORCEMENT_LEARNING,
        "epic": "Epic 4",
        "remediation": "Implement epsilon-greedy, UCB, or entropy-based exploration",
        "research_reference": "RLC 2025 - Threshold-Based Policy Optimization for Behavioral Interventions",
    },
    {
        "pattern": r"class\s+ADHDScheduler.*?(?!time_on_task_decay)",
        "message": "Scheduler doesn't account for ADHD time-on-task decay effects",
        "category": "ML_SPECIFIC",
        "severity": "MEDIUM",
        "type": "missing_momentum",
        "subcategory": MLDebtSubcategory.REINFORCEMENT_LEARNING,
        "epic": "Epic 4",
        "remediation": "Incorporate momentum-aware mechanisms based on research insights",
        "research_reference": "PMC5701950 - ADHD performance declines 37% faster than neurotypical baselines during sustained attention tasks",
    },
    # Progress monitoring debt
    {
        "pattern": r"while.*?sleep\(\d+\).*?progress",
        "message": "Polling-based progress monitoring is inefficient and may miss events",
        "category": "ML_SPECIFIC",
        "severity": "MEDIUM",
        "type": "polling_implementation",
        "subcategory": MLDebtSubcategory.MONITORING,
        "epic": "Epic 4",
        "remediation": "Implement event-driven progress monitoring architecture",
        "research_reference": "Causal ML for Health (ICML 2025)",
    },
    {
        "pattern": r"progress\s*=\s*(True|False)",
        "message": "Binary progress tracking lacks granularity for adaptive adjustment",
        "category": "ML_SPECIFIC",
        "severity": "MEDIUM",
        "type": "binary_progress",
        "subcategory": MLDebtSubcategory.MONITORING,
        "epic": "Epic 4",
        "remediation": "Implement continuous or multi-stage progress tracking",
        "research_reference": "Journal of Attention Disorders (2025) - task adherence metrics",
    },
    # Opportunity cost debt
    {
        "pattern": r"opportunity_cost\s*=\s*\w+",
        "message": "Static opportunity cost model doesn't adapt to changing context",
        "category": "ML_SPECIFIC",
        "severity": "MEDIUM",
        "type": "static_cost_model",
        "subcategory": MLDebtSubcategory.OPTIMIZATION,
        "epic": "Epic 4",
        "remediation": "Implement dynamic opportunity cost calculation based on context",
        "research_reference": "Learning for Dynamics & Control Conference 2025",
    },
    # Circadian-aware debt
    {
        "pattern": r"(morning|afternoon|evening)_block\s*=\s*\[\d+,\s*\d+\]",
        "message": "Hardcoded time blocks don't account for individual circadian variations",
        "category": "ML_SPECIFIC",
        "severity": "HIGH",
        "type": "hardcoded_time_blocks",
        "subcategory": MLDebtSubcategory.CIRCADIAN,
        "epic": "Epic 4",
        "remediation": "Integrate with CircadianRhythmModel from Epic 1 for personalized timing",
        "research_reference": "Journal of Circadian Rhythms (2025) - 72% improved task completion with ultradian cycle alignment",
    },
    {
        "pattern": r"class\s+\w+Scheduler.*?(?!ultradian|90[\s_-]*minute)",
        "message": "Scheduler doesn't account for 90-minute ultradian cycles important for ADHD focus",
        "category": "ML_SPECIFIC",
        "severity": "MEDIUM",
        "type": "missing_ultradian",
        "subcategory": MLDebtSubcategory.CIRCADIAN,
        "epic": "Epic 4",
        "remediation": "Implement ultradian cycle awareness based on research findings",
        "research_reference": "Journal of Circadian Rhythms (2025) - ultradian cycle alignment as critical for ADHD populations",
    },
    # Ethical debt
    {
        "pattern": r"class\s+\w+Scheduler.*?(?!bias_mitigation|fairness)",
        "message": "No explicit bias mitigation in schedule optimization",
        "category": "ML_SPECIFIC",
        "severity": "MEDIUM",
        "type": "missing_fairness",
        "subcategory": MLDebtSubcategory.ETHICAL_CONCERNS,
        "epic": "Epic 4",
        "remediation": "Implement fairness mechanisms to prevent bias toward specific ADHD subtypes",
        "research_reference": "NeurIPS workshop on Equitable AI - ADHD subgroup analyses",
    },
    {
        "pattern": r"class\s+\w+Model.*?(?!explainable|interpretable)",
        "message": "ML model lacks explainability mechanisms",
        "category": "ML_SPECIFIC",
        "severity": "MEDIUM",
        "type": "black_box_model",
        "subcategory": MLDebtSubcategory.ETHICAL_CONCERNS,
        "epic": "Epic 4",
        "remediation": "Add explainability methods such as SHAP or LIME",
        "research_reference": "ADHD-23: Create SHAP-based explainability system for recommendations",
    },
    # General ML debt relevant to Epic 4
    {
        "pattern": r"random\.(random|sample|choice).*?(?!seed)",
        "message": "Non-seeded randomness creates non-reproducible ML behavior",
        "category": "ML_SPECIFIC",
        "severity": "HIGH",
        "type": "non_reproducible_ml",
        "subcategory": MLDebtSubcategory.REPRODUCIBILITY,
        "epic": "Epic 4",
        "remediation": "Set random seeds consistently for reproducibility",
        "research_reference": None,
    },
    {
        "pattern": r"train\(.*?\).*?(?!valid|test|eval)",
        "message": "ML training without validation may lead to overfitting",
        "category": "ML_SPECIFIC",
        "severity": "HIGH",
        "type": "missing_validation",
        "subcategory": MLDebtSubcategory.EVALUATION,
        "epic": "Epic 4",
        "remediation": "Implement proper train/validation/test splits",
        "research_reference": None,
    },
    {
        "pattern": r"(learning_rate|batch_size|hidden_size|n_layers)\s*=\s*\d+\.?\d*",
        "message": "Hardcoded hyperparameters reduce adaptability and experimentation",
        "category": "ML_SPECIFIC",
        "severity": "MEDIUM",
        "type": "hardcoded_hyperparams",
        "subcategory": MLDebtSubcategory.MODEL_COMPLEXITY,
        "epic": "Epic 4",
        "remediation": "Move hyperparameters to configuration files or use hyperparameter optimization",
        "research_reference": None,
    },
]


def get_epic4_tech_debt_patterns() -> List[Dict[str, Any]]:
    """
    Return technical debt patterns specific to Epic 4.

    Returns:
        List of technical debt pattern dictionaries
    """
    return EPIC4_TECH_DEBT_PATTERNS


def get_tech_debt_by_subcategory(subcategory: MLDebtSubcategory) -> List[Dict[str, Any]]:
    """
    Return technical debt patterns filtered by subcategory.

    Args:
        subcategory: The ML debt subcategory to filter by

    Returns:
        List of technical debt pattern dictionaries for the specified subcategory
    """
    return [
        pattern
        for pattern in EPIC4_TECH_DEBT_PATTERNS
        if pattern.get("subcategory") == subcategory
        or (
            isinstance(pattern.get("subcategory"), MLDebtSubcategory)
            and pattern.get("subcategory") == subcategory
        )
    ]
