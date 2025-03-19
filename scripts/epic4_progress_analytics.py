#!/usr/bin/env python3
"""
Epic 4 Progress Analytics System

This module provides tools for analyzing and visualizing progress on ML development tasks
for Epic 4: Dynamic Schedule Rebalancing. It integrates with existing ML workflow
components to provide insights on development velocity, ML model improvements,
and research implementation tracking.
"""

import os
import sys
import json
import datetime
import re
import glob
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple, Any, Optional, Union
from collections import defaultdict, Counter
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.colors import LinearSegmentedColormap
import io
import base64
import argparse

# Add project root to path to enable imports
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.append(ROOT_DIR)

# Import project-specific modules if available
try:
    from scripts.ml_tech_debt_patterns import MLDebtSubcategory, get_tech_debt_by_subcategory
except ImportError:
    # Define a minimal version if the module is not available
    class MLDebtSubcategory(Enum):
        """Minimal version of MLDebtSubcategory."""
        REINFORCEMENT_LEARNING = "reinforcement_learning"
        MONITORING = "monitoring"
        CIRCADIAN = "circadian"
        OPTIMIZATION = "optimization"

class ProgressMetricType(Enum):
    """Types of progress metrics for ML development workflow."""
    STORY_COMPLETION = "story_completion"
    CODE_COVERAGE = "code_coverage"
    MODEL_PERFORMANCE = "model_performance"
    TECHNICAL_DEBT = "technical_debt"
    RESEARCH_IMPLEMENTATION = "research_implementation"
    DOCUMENTATION_COVERAGE = "documentation_coverage"
    TEST_COVERAGE = "test_coverage"
    EXPERIMENT_COUNT = "experiment_count"
    REVIEW_COMPLETION = "review_completion"

class MLTaskStage(Enum):
    """Development stages for ML tasks."""
    PLANNING = "planning"
    DATA_PREPARATION = "data_preparation"
    MODEL_DEVELOPMENT = "model_development"
    EVALUATION = "evaluation"
    DOCUMENTATION = "documentation"
    REVIEW = "review"
    DEPLOYMENT = "deployment"

@dataclass
class Epic4Story:
    """Represents a story in Epic 4."""
    story_id: str
    title: str
    status: str = "Not Started"
    progress: float = 0.0  # 0.0 to 1.0
    current_stage: MLTaskStage = MLTaskStage.PLANNING
    stages_completed: List[MLTaskStage] = field(default_factory=list)
    research_references: List[str] = field(default_factory=list)
    ml_task_types: List[str] = field(default_factory=list)
    
    def calculate_progress(self) -> float:
        """Calculate progress based on completed stages."""
        # Define stage weights (customize as needed)
        stage_weights = {
            MLTaskStage.PLANNING: 0.1,
            MLTaskStage.DATA_PREPARATION: 0.2,
            MLTaskStage.MODEL_DEVELOPMENT: 0.3,
            MLTaskStage.EVALUATION: 0.2,
            MLTaskStage.DOCUMENTATION: 0.1,
            MLTaskStage.REVIEW: 0.05,
            MLTaskStage.DEPLOYMENT: 0.05
        }
        
        completed_weight = sum(stage_weights[stage] for stage in self.stages_completed)
        
        # Add partial credit for current stage (50% of its weight)
        if self.current_stage not in self.stages_completed:
            completed_weight += stage_weights[self.current_stage] * 0.5
            
        self.progress = min(completed_weight, 1.0)
        return self.progress
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "story_id": self.story_id,
            "title": self.title,
            "status": self.status,
            "progress": self.progress,
            "current_stage": self.current_stage.value if isinstance(self.current_stage, MLTaskStage) else self.current_stage,
            "stages_completed": [s.value if isinstance(s, MLTaskStage) else s for s in self.stages_completed],
            "research_references": self.research_references,
            "ml_task_types": self.ml_task_types
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Epic4Story':
        """Create from dictionary."""
        # Convert string stage names to MLTaskStage enum
        current_stage = data.get("current_stage", MLTaskStage.PLANNING.value)
        if isinstance(current_stage, str):
            current_stage = MLTaskStage(current_stage)
            
        stages_completed = data.get("stages_completed", [])
        stages_completed = [MLTaskStage(s) if isinstance(s, str) else s for s in stages_completed]
        
        return cls(
            story_id=data.get("story_id", ""),
            title=data.get("title", ""),
            status=data.get("status", "Not Started"),
            progress=data.get("progress", 0.0),
            current_stage=current_stage,
            stages_completed=stages_completed,
            research_references=data.get("research_references", []),
            ml_task_types=data.get("ml_task_types", [])
        )

@dataclass
class MLExperiment:
    """Represents an ML experiment."""
    experiment_id: str
    story_id: str
    title: str
    ml_task_type: str
    created_at: datetime.datetime = field(default_factory=datetime.datetime.now)
    metrics: Dict[str, float] = field(default_factory=dict)
    parameters: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    is_baseline: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "experiment_id": self.experiment_id,
            "story_id": self.story_id,
            "title": self.title,
            "ml_task_type": self.ml_task_type,
            "created_at": self.created_at.isoformat(),
            "metrics": self.metrics,
            "parameters": self.parameters,
            "tags": self.tags,
            "is_baseline": self.is_baseline
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MLExperiment':
        """Create from dictionary."""
        # Parse datetime string
        created_at = data.get("created_at", datetime.datetime.now().isoformat())
        if isinstance(created_at, str):
            try:
                created_at = datetime.datetime.fromisoformat(created_at)
            except ValueError:
                created_at = datetime.datetime.now()
                
        return cls(
            experiment_id=data.get("experiment_id", ""),
            story_id=data.get("story_id", ""),
            title=data.get("title", ""),
            ml_task_type=data.get("ml_task_type", ""),
            created_at=created_at,
            metrics=data.get("metrics", {}),
            parameters=data.get("parameters", {}),
            tags=data.get("tags", []),
            is_baseline=data.get("is_baseline", False)
        )

@dataclass
class ResearchImplementation:
    """Tracks implementation of research insights."""
    research_id: str
    title: str
    source: str
    key_insights: List[str] = field(default_factory=list)
    implemented_insights: List[str] = field(default_factory=list)
    related_stories: List[str] = field(default_factory=list)
    implementation_progress: float = 0.0  # 0.0 to 1.0
    
    def calculate_progress(self) -> float:
        """Calculate implementation progress."""
        if not self.key_insights:
            return 0.0
            
        self.implementation_progress = len(self.implemented_insights) / len(self.key_insights)
        return self.implementation_progress
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "research_id": self.research_id,
            "title": self.title,
            "source": self.source,
            "key_insights": self.key_insights,
            "implemented_insights": self.implemented_insights,
            "related_stories": self.related_stories,
            "implementation_progress": self.implementation_progress
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ResearchImplementation':
        """Create from dictionary."""
        return cls(
            research_id=data.get("research_id", ""),
            title=data.get("title", ""),
            source=data.get("source", ""),
            key_insights=data.get("key_insights", []),
            implemented_insights=data.get("implemented_insights", []),
            related_stories=data.get("related_stories", []),
            implementation_progress=data.get("implementation_progress", 0.0)
        )

@dataclass
class TechnicalDebtRecord:
    """Tracks technical debt over time."""
    date: datetime.date
    total_debt_score: float
    debt_by_category: Dict[str, int] = field(default_factory=dict)
    debt_by_severity: Dict[str, int] = field(default_factory=dict)
    debt_by_ml_category: Dict[str, int] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "date": self.date.isoformat(),
            "total_debt_score": self.total_debt_score,
            "debt_by_category": self.debt_by_category,
            "debt_by_severity": self.debt_by_severity,
            "debt_by_ml_category": self.debt_by_ml_category
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TechnicalDebtRecord':
        """Create from dictionary."""
        # Parse date string
        date_str = data.get("date", datetime.date.today().isoformat())
        if isinstance(date_str, str):
            try:
                date = datetime.date.fromisoformat(date_str)
            except ValueError:
                date = datetime.date.today()
        else:
            date = datetime.date.today()
            
        return cls(
            date=date,
            total_debt_score=data.get("total_debt_score", 0.0),
            debt_by_category=data.get("debt_by_category", {}),
            debt_by_severity=data.get("debt_by_severity", {}),
            debt_by_ml_category=data.get("debt_by_ml_category", {})
        )

class ProgressAnalyticsEngine:
    """
    Engine for tracking and analyzing ML development progress.
    
    This class handles loading data, calculating metrics, and managing
    the analytics state for Epic 4 development progress.
    """
    
    def __init__(self, data_dir: str = None):
        """
        Initialize the progress analytics engine.
        
        Args:
            data_dir: Directory to store/load progress data (defaults to workspace/data/progress)
        """
        self.data_dir = data_dir or os.path.join(ROOT_DIR, "data", "progress")
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize data stores
        self.stories: Dict[str, Epic4Story] = {}
        self.experiments: Dict[str, MLExperiment] = {}
        self.research_implementations: Dict[str, ResearchImplementation] = {}
        self.technical_debt_history: List[TechnicalDebtRecord] = []
        
        # Track baseline metrics for experiments
        self.baseline_metrics: Dict[str, Dict[str, float]] = {}
        
        # Initialize Epic 4 stories
        self._initialize_epic4_stories()
        
        # Try to load existing data
        self.load_data()
    
    def _initialize_epic4_stories(self):
        """Initialize Epic 4 stories from the predefined list."""
        epic4_stories = [
            ("ADHD-20", "Create real-time progress monitoring and adaptive adjustment"),
            ("ADHD-17", "Implement reinforcement learning for adaptive scheduling"),
            ("ADHD-18", "Create opportunity cost calculator for task rescheduling"),
            ("ADHD-19", "Implement circadian-aware schedule adjustment system")
        ]
        
        ml_task_types = {
            "ADHD-20": ["progress_monitoring", "time_series"],
            "ADHD-17": ["reinforcement_learning"],
            "ADHD-18": ["optimization", "scheduling"],
            "ADHD-19": ["circadian_aware", "time_series"]
        }
        
        research_references = {
            "ADHD-20": ["journal_attention_disorders_2025"],
            "ADHD-17": ["rlc_2025", "pmc5701950", "icml_2025", "neurips_2025"],
            "ADHD-18": ["learning_dynamics_control_2025"],
            "ADHD-19": ["journal_circadian_rhythms_2025", "nature_digital_medicine"]
        }
        
        for story_id, title in epic4_stories:
            self.stories[story_id] = Epic4Story(
                story_id=story_id,
                title=title,
                ml_task_types=ml_task_types.get(story_id, []),
                research_references=research_references.get(story_id, [])
            )
    
    def save_data(self):
        """Save all data to the data directory."""
        # Save stories
        stories_data = {story_id: story.to_dict() for story_id, story in self.stories.items()}
        with open(os.path.join(self.data_dir, "epic4_stories.json"), "w") as f:
            json.dump(stories_data, f, indent=2)
            
        # Save experiments
        experiments_data = {exp_id: exp.to_dict() for exp_id, exp in self.experiments.items()}
        with open(os.path.join(self.data_dir, "epic4_experiments.json"), "w") as f:
            json.dump(experiments_data, f, indent=2)
            
        # Save research implementations
        research_data = {res_id: res.to_dict() for res_id, res in self.research_implementations.items()}
        with open(os.path.join(self.data_dir, "epic4_research.json"), "w") as f:
            json.dump(research_data, f, indent=2)
            
        # Save technical debt history
        debt_data = [record.to_dict() for record in self.technical_debt_history]
        with open(os.path.join(self.data_dir, "epic4_technical_debt.json"), "w") as f:
            json.dump(debt_data, f, indent=2)
            
        # Save baseline metrics
        with open(os.path.join(self.data_dir, "epic4_baselines.json"), "w") as f:
            json.dump(self.baseline_metrics, f, indent=2)
    
    def load_data(self):
        """Load data from the data directory."""
        # Load stories
        stories_path = os.path.join(self.data_dir, "epic4_stories.json")
        if os.path.exists(stories_path):
            try:
                with open(stories_path, "r") as f:
                    stories_data = json.load(f)
                    for story_id, story_dict in stories_data.items():
                        self.stories[story_id] = Epic4Story.from_dict(story_dict)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading stories data: {e}")
                
        # Load experiments
        experiments_path = os.path.join(self.data_dir, "epic4_experiments.json")
        if os.path.exists(experiments_path):
            try:
                with open(experiments_path, "r") as f:
                    experiments_data = json.load(f)
                    for exp_id, exp_dict in experiments_data.items():
                        self.experiments[exp_id] = MLExperiment.from_dict(exp_dict)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading experiments data: {e}")
                
        # Load research implementations
        research_path = os.path.join(self.data_dir, "epic4_research.json")
        if os.path.exists(research_path):
            try:
                with open(research_path, "r") as f:
                    research_data = json.load(f)
                    for res_id, res_dict in research_data.items():
                        self.research_implementations[res_id] = ResearchImplementation.from_dict(res_dict)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading research data: {e}")
                
        # Load technical debt history
        debt_path = os.path.join(self.data_dir, "epic4_technical_debt.json")
        if os.path.exists(debt_path):
            try:
                with open(debt_path, "r") as f:
                    debt_data = json.load(f)
                    self.technical_debt_history = [TechnicalDebtRecord.from_dict(record) for record in debt_data]
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading technical debt data: {e}")
                
        # Load baseline metrics
        baseline_path = os.path.join(self.data_dir, "epic4_baselines.json")
        if os.path.exists(baseline_path):
            try:
                with open(baseline_path, "r") as f:
                    self.baseline_metrics = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading baseline metrics: {e}")
    
    def update_story(self, story_id: str, **kwargs) -> Epic4Story:
        """
        Update a story with new information.
        
        Args:
            story_id: ID of the story to update
            **kwargs: Fields to update
            
        Returns:
            Updated story object
        """
        if story_id not in self.stories:
            raise ValueError(f"Story {story_id} not found")
            
        story = self.stories[story_id]
        
        # Update fields
        for field, value in kwargs.items():
            if hasattr(story, field):
                setattr(story, field, value)
                
        # Recalculate progress
        story.calculate_progress()
        
        # Save data
        self.save_data()
        
        return story
    
    def complete_story_stage(self, story_id: str, stage: Union[str, MLTaskStage]) -> Epic4Story:
        """
        Mark a stage as completed for a story.
        
        Args:
            story_id: ID of the story
            stage: Stage to mark as completed
            
        Returns:
            Updated story object
        """
        if story_id not in self.stories:
            raise ValueError(f"Story {story_id} not found")
            
        story = self.stories[story_id]
        
        # Convert string to enum if needed
        if isinstance(stage, str):
            stage = MLTaskStage(stage)
            
        # Add to completed stages if not already there
        if stage not in story.stages_completed:
            story.stages_completed.append(stage)
            
        # Recalculate progress
        story.calculate_progress()
        
        # Update status based on progress
        if story.progress >= 0.99:
            story.status = "Done"
        elif story.progress > 0:
            story.status = "In Progress"
            
        # Save data
        self.save_data()
        
        return story
    
    def add_experiment(self, experiment: MLExperiment) -> str:
        """
        Add an ML experiment to the system.
        
        Args:
            experiment: The experiment to add
            
        Returns:
            ID of the added experiment
        """
        # Generate ID if not provided
        if not experiment.experiment_id:
            experiment.experiment_id = f"exp_{len(self.experiments) + 1}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
        # Add to experiments
        self.experiments[experiment.experiment_id] = experiment
        
        # If this is a baseline experiment, store metrics
        if experiment.is_baseline:
            self.baseline_metrics[experiment.story_id] = experiment.metrics
            
        # Save data
        self.save_data()
        
        return experiment.experiment_id
    
    def add_research_implementation(self, research: ResearchImplementation) -> str:
        """
        Add a research implementation to the system.
        
        Args:
            research: The research implementation to add
            
        Returns:
            ID of the added research implementation
        """
        # Generate ID if not provided
        if not research.research_id:
            research.research_id = f"res_{len(self.research_implementations) + 1}_{datetime.datetime.now().strftime('%Y%m%d')}"
            
        # Calculate progress
        research.calculate_progress()
        
        # Add to research implementations
        self.research_implementations[research.research_id] = research
        
        # Save data
        self.save_data()
        
        return research.research_id
    
    def add_technical_debt_record(self, record: TechnicalDebtRecord = None, 
                                detect_current: bool = True) -> TechnicalDebtRecord:
        """
        Add a technical debt record to the history.
        
        Args:
            record: The record to add, or None to create a new one
            detect_current: Whether to run technical debt detection
            
        Returns:
            The added record
        """
        if record is None:
            # Create new record for today
            record = TechnicalDebtRecord(
                date=datetime.date.today(),
                total_debt_score=0.0
            )
            
        # If requested, run technical debt detection
        if detect_current:
            try:
                debt_data = self._run_tech_debt_detection()
                
                # Update record with detected data
                record.total_debt_score = debt_data.get("score", 0.0)
                
                # Count by category and severity
                results = debt_data.get("results", [])
                category_counts = Counter()
                severity_counts = Counter()
                ml_category_counts = Counter()
                
                for issue in results:
                    category = issue.get("debt_category", "UNKNOWN")
                    severity = issue.get("severity", "MEDIUM")
                    subcategory = issue.get("subcategory")
                    
                    category_counts[category] += 1
                    severity_counts[severity] += 1
                    
                    # Count ML-specific subcategories
                    if subcategory:
                        ml_category_counts[subcategory] += 1
                        
                record.debt_by_category = dict(category_counts)
                record.debt_by_severity = dict(severity_counts)
                record.debt_by_ml_category = dict(ml_category_counts)
                
            except Exception as e:
                print(f"Error running technical debt detection: {e}")
                
        # Add to history
        self.technical_debt_history.append(record)
        
        # Sort by date
        self.technical_debt_history.sort(key=lambda r: r.date)
        
        # Save data
        self.save_data()
        
        return record
    
    def _run_tech_debt_detection(self) -> Dict[str, Any]:
        """
        Run technical debt detection and return results.
        
        Returns:
            Dictionary with technical debt detection results
        """
        # Try to import and run detect_tech_debt.py
        try:
            script_path = os.path.join(SCRIPT_DIR, "detect_tech_debt.py")
            if not os.path.exists(script_path):
                return {"score": 0.0, "results": []}
                
            # Run the script with --all --json --epic "Epic 4" flags
            import subprocess
            result = subprocess.run(
                ["python", script_path, "--all", "--json", "--epic", "Epic 4"],
                capture_output=True,
                text=True,
                check=True
            )
            
            # Parse JSON output
            return json.loads(result.stdout)
            
        except Exception as e:
            print(f"Error running technical debt detection: {e}")
            return {"score": 0.0, "results": []}
    
    def get_story_progress(self, story_id: str = None) -> Dict[str, float]:
        """
        Get progress for stories.
        
        Args:
            story_id: Optional story ID to get progress for, or None for all stories
            
        Returns:
            Dictionary mapping story IDs to progress percentages
        """
        if story_id:
            if story_id not in self.stories:
                raise ValueError(f"Story {story_id} not found")
                
            return {story_id: self.stories[story_id].calculate_progress()}
        else:
            return {s_id: story.calculate_progress() for s_id, story in self.stories.items()}
    
    def get_research_implementation_progress(self) -> Dict[str, float]:
        """
        Get progress for research implementations.
        
        Returns:
            Dictionary mapping research IDs to implementation progress
        """
        return {r_id: research.calculate_progress() 
                for r_id, research in self.research_implementations.items()}
    
    def get_overall_epic_progress(self) -> float:
        """
        Calculate overall progress for Epic 4.
        
        Returns:
            Progress percentage (0.0 to 1.0)
        """
        if not self.stories:
            return 0.0
            
        # Calculate average progress across all stories
        story_progresses = self.get_story_progress()
        return sum(story_progresses.values()) / len(story_progresses)
    
    def get_experiment_metrics(self, story_id: str = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get metrics for experiments.
        
        Args:
            story_id: Optional story ID to filter experiments by
            
        Returns:
            Dictionary mapping metric names to lists of (date, value) pairs
        """
        # Filter experiments by story ID if provided
        filtered_experiments = list(self.experiments.values())
        if story_id:
            filtered_experiments = [exp for exp in filtered_experiments if exp.story_id == story_id]
            
        if not filtered_experiments:
            return {}
            
        # Collect all metrics
        all_metrics: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        
        for experiment in sorted(filtered_experiments, key=lambda e: e.created_at):
            for metric_name, metric_value in experiment.metrics.items():
                all_metrics[metric_name].append({
                    "date": experiment.created_at,
                    "value": metric_value,
                    "experiment_id": experiment.experiment_id,
                    "experiment_title": experiment.title
                })
                
        return dict(all_metrics)
    
    def get_technical_debt_trend(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get technical debt trends over time.
        
        Returns:
            Dictionary with technical debt trends
        """
        if not self.technical_debt_history:
            return {}
            
        # Sort records by date
        sorted_records = sorted(self.technical_debt_history, key=lambda r: r.date)
        
        # Extract total score trend
        total_score_trend = [
            {"date": record.date, "value": record.total_debt_score}
            for record in sorted_records
        ]
        
        # Collect all ML categories
        all_ml_categories = set()
        for record in sorted_records:
            all_ml_categories.update(record.debt_by_ml_category.keys())
            
        # Extract ML category trends
        ml_category_trends = {}
        for category in all_ml_categories:
            ml_category_trends[category] = [
                {"date": record.date, "value": record.debt_by_ml_category.get(category, 0)}
                for record in sorted_records
            ]
            
        return {
            "total_score": total_score_trend,
            "ml_categories": ml_category_trends
        }
    
    def get_baseline_improvements(self, story_id: str = None) -> Dict[str, Dict[str, float]]:
        """
        Calculate improvements over baseline metrics.
        
        Args:
            story_id: Optional story ID to filter by
            
        Returns:
            Dictionary mapping story IDs to dictionaries of metric improvements
        """
        story_ids = [story_id] if story_id else list(self.stories.keys())
        improvements = {}
        
        for s_id in story_ids:
            # Skip if no baseline for this story
            if s_id not in self.baseline_metrics:
                continue
                
            baseline = self.baseline_metrics[s_id]
            
            # Get the latest experiment for this story
            story_experiments = [e for e in self.experiments.values() if e.story_id == s_id]
            if not story_experiments:
                continue
                
            latest_experiment = max(story_experiments, key=lambda e: e.created_at)
            
            # Calculate improvements
            story_improvements = {}
            for metric_name, baseline_value in baseline.items():
                if metric_name in latest_experiment.metrics:
                    current_value = latest_experiment.metrics[metric_name]
                    improvement = current_value - baseline_value
                    story_improvements[metric_name] = improvement
                    
            if story_improvements:
                improvements[s_id] = story_improvements
                
        return improvements 

class ProgressDashboardGenerator:
    """
    Generator for Epic 4 progress dashboards.
    
    This class handles creating visualizations and generating reports
    for Epic 4 development progress.
    """
    
    def __init__(self, analytics_engine: ProgressAnalyticsEngine, output_dir: str = None):
        """
        Initialize the dashboard generator.
        
        Args:
            analytics_engine: The progress analytics engine
            output_dir: Directory to store generated reports (defaults to workspace/docs/progress)
        """
        self.analytics = analytics_engine
        self.output_dir = output_dir or os.path.join(ROOT_DIR, "docs", "progress")
        os.makedirs(self.output_dir, exist_ok=True)
    
    def _plot_story_progress(self) -> str:
        """
        Create a bar plot of story progress.
        
        Returns:
            Base64-encoded PNG image
        """
        # Get story progress
        progress_data = self.analytics.get_story_progress()
        
        if not progress_data:
            return ""
            
        # Create figure
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Sort stories by ID
        story_ids = sorted(progress_data.keys())
        progresses = [progress_data[s_id] * 100 for s_id in story_ids]  # Convert to percentages
        
        # Get story titles for better labels
        story_titles = {s_id: self.analytics.stories[s_id].title for s_id in story_ids}
        labels = [f"{s_id}: {story_titles[s_id][:30]}..." if len(story_titles[s_id]) > 30 else f"{s_id}: {story_titles[s_id]}" 
                 for s_id in story_ids]
        
        # Create horizontal bar chart
        bars = ax.barh(labels, progresses, color='skyblue')
        
        # Add percentage labels
        for bar in bars:
            width = bar.get_width()
            label_x_pos = width + 1
            ax.text(label_x_pos, bar.get_y() + bar.get_height()/2, f"{width:.1f}%",
                   va='center')
        
        # Add gridlines
        ax.grid(axis='x', linestyle='--', alpha=0.7)
        
        # Set labels and title
        ax.set_xlabel('Completion Percentage')
        ax.set_title('Epic 4 Story Progress')
        
        # Set x-axis limit
        ax.set_xlim(0, 110)  # Leave room for percentage labels
        
        plt.tight_layout()
        
        # Convert to base64
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100)
        buf.seek(0)
        plt.close(fig)
        
        return base64.b64encode(buf.read()).decode('utf-8')
    
    def _plot_overall_progress(self) -> str:
        """
        Create a radial chart of overall Epic 4 progress.
        
        Returns:
            Base64-encoded PNG image
        """
        # Get overall progress
        overall_progress = self.analytics.get_overall_epic_progress()
        
        # Create figure
        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw={'projection': 'polar'})
        
        # Plot progress as a partially filled circle
        theta = np.linspace(0, 2 * np.pi * overall_progress, 100)
        radii = np.ones_like(theta)
        
        # Create background circle (light gray)
        ax.fill_between(np.linspace(0, 2 * np.pi, 100), 0, 0.8, color='lightgray', alpha=0.5)
        
        # Create progress arc
        ax.fill_between(theta, 0, 0.8, color='green', alpha=0.6)
        
        # Remove grid and tick labels
        ax.grid(False)
        ax.set_xticks([])
        ax.set_yticks([])
        
        # Add percentage text in the center
        percentage = int(overall_progress * 100)
        ax.text(0, 0, f"{percentage}%", fontsize=36, ha='center', va='center')
        
        plt.tight_layout()
        
        # Convert to base64
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100)
        buf.seek(0)
        plt.close(fig)
        
        return base64.b64encode(buf.read()).decode('utf-8')
    
    def _plot_research_implementation(self) -> str:
        """
        Create a bar chart of research implementation progress.
        
        Returns:
            Base64-encoded PNG image
        """
        # Get research implementation progress
        research_progress = self.analytics.get_research_implementation_progress()
        
        if not research_progress:
            return ""
            
        # Create figure
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Sort by research ID
        research_ids = sorted(research_progress.keys())
        progresses = [research_progress[r_id] * 100 for r_id in research_ids]  # Convert to percentages
        
        # Get research titles for better labels
        research_titles = {r_id: self.analytics.research_implementations[r_id].title for r_id in research_ids}
        labels = [f"{research_titles[r_id][:40]}..." if len(research_titles[r_id]) > 40 else research_titles[r_id]
                 for r_id in research_ids]
        
        # Create horizontal bar chart
        bars = ax.barh(labels, progresses, color='lightgreen')
        
        # Add percentage labels
        for bar in bars:
            width = bar.get_width()
            label_x_pos = width + 1
            ax.text(label_x_pos, bar.get_y() + bar.get_height()/2, f"{width:.1f}%",
                   va='center')
        
        # Add gridlines
        ax.grid(axis='x', linestyle='--', alpha=0.7)
        
        # Set labels and title
        ax.set_xlabel('Implementation Percentage')
        ax.set_title('Research Implementation Progress')
        
        # Set x-axis limit
        ax.set_xlim(0, 110)  # Leave room for percentage labels
        
        plt.tight_layout()
        
        # Convert to base64
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100)
        buf.seek(0)
        plt.close(fig)
        
        return base64.b64encode(buf.read()).decode('utf-8')
    
    def _plot_tech_debt_trend(self) -> str:
        """
        Create a line chart of technical debt trends.
        
        Returns:
            Base64-encoded PNG image
        """
        # Get technical debt trends
        debt_trends = self.analytics.get_technical_debt_trend()
        
        if not debt_trends or 'total_score' not in debt_trends:
            return ""
            
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Plot total score trend
        total_score_trend = debt_trends['total_score']
        dates = [item['date'] for item in total_score_trend]
        values = [item['value'] for item in total_score_trend]
        
        ax.plot(dates, values, marker='o', linestyle='-', linewidth=2, label='Total Debt Score')
        
        # Format x-axis as dates
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.xticks(rotation=45)
        
        # Add gridlines
        ax.grid(linestyle='--', alpha=0.7)
        
        # Set labels and title
        ax.set_xlabel('Date')
        ax.set_ylabel('Technical Debt Score')
        ax.set_title('Technical Debt Trend')
        
        plt.tight_layout()
        
        # Convert to base64
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100)
        buf.seek(0)
        plt.close(fig)
        
        return base64.b64encode(buf.read()).decode('utf-8')
    
    def _plot_ml_debt_categories(self) -> str:
        """
        Create a stacked area chart of ML technical debt categories.
        
        Returns:
            Base64-encoded PNG image
        """
        # Get technical debt trends
        debt_trends = self.analytics.get_technical_debt_trend()
        
        if not debt_trends or 'ml_categories' not in debt_trends or not debt_trends['ml_categories']:
            return ""
            
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Get all categories and dates
        ml_categories = debt_trends['ml_categories']
        all_dates = sorted(set(item['date'] for items in ml_categories.values() for item in items))
        
        # Create a DataFrame for plotting
        df = pd.DataFrame(index=all_dates, columns=ml_categories.keys())
        
        # Fill DataFrame with data
        for category, items in ml_categories.items():
            for item in items:
                df.at[item['date'], category] = item['value']
                
        # Fill NaN values with 0
        df = df.fillna(0)
        
        # Sort by date
        df = df.sort_index()
        
        # Create stacked area plot
        df.plot.area(ax=ax, stacked=True, alpha=0.7)
        
        # Format x-axis as dates
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.xticks(rotation=45)
        
        # Add gridlines
        ax.grid(linestyle='--', alpha=0.7)
        
        # Set labels and title
        ax.set_xlabel('Date')
        ax.set_ylabel('Issue Count')
        ax.set_title('ML Technical Debt Categories')
        
        # Add legend with cleaner labels
        handles, labels = ax.get_legend_handles_labels()
        clean_labels = [label.replace('_', ' ').title() for label in labels]
        ax.legend(handles, clean_labels, loc='upper left')
        
        plt.tight_layout()
        
        # Convert to base64
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100)
        buf.seek(0)
        plt.close(fig)
        
        return base64.b64encode(buf.read()).decode('utf-8')
    
    def _plot_experiment_metrics(self, story_id: str = None) -> Dict[str, str]:
        """
        Create line charts for experiment metrics.
        
        Args:
            story_id: Optional story ID to filter by
            
        Returns:
            Dictionary mapping metric names to base64-encoded PNG images
        """
        # Get experiment metrics
        metrics_data = self.analytics.get_experiment_metrics(story_id)
        
        if not metrics_data:
            return {}
            
        # Create a plot for each metric
        metric_plots = {}
        
        for metric_name, metric_values in metrics_data.items():
            # Sort by date
            sorted_values = sorted(metric_values, key=lambda x: x['date'])
            
            # Extract dates and values
            dates = [item['date'] for item in sorted_values]
            values = [item['value'] for item in sorted_values]
            titles = [item['experiment_title'] for item in sorted_values]
            
            # Create figure
            fig, ax = plt.subplots(figsize=(12, 6))
            
            # Plot values
            ax.plot(dates, values, marker='o', linestyle='-', linewidth=2)
            
            # Add data point labels
            for i, (date, value, title) in enumerate(zip(dates, values, titles)):
                ax.annotate(f"{title}",
                          xy=(date, value),
                          xytext=(0, 10),
                          textcoords="offset points",
                          ha='center', va='bottom',
                          rotation=45,
                          fontsize=8)
            
            # Format x-axis as dates
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
            plt.xticks(rotation=45)
            
            # Add gridlines
            ax.grid(linestyle='--', alpha=0.7)
            
            # Set labels and title
            ax.set_xlabel('Date')
            ax.set_ylabel(metric_name)
            ax.set_title(f'Experiment Metric: {metric_name}')
            
            plt.tight_layout()
            
            # Convert to base64
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=100)
            buf.seek(0)
            plt.close(fig)
            
            metric_plots[metric_name] = base64.b64encode(buf.read()).decode('utf-8')
            
        return metric_plots
    
    def _plot_baseline_improvements(self) -> str:
        """
        Create a bar chart of improvements over baseline.
        
        Returns:
            Base64-encoded PNG image
        """
        # Get baseline improvements
        improvements = self.analytics.get_baseline_improvements()
        
        if not improvements:
            return ""
            
        # Collect all metrics across all stories
        all_metrics = set()
        for story_improvements in improvements.values():
            all_metrics.update(story_improvements.keys())
            
        if not all_metrics:
            return ""
            
        # Create a DataFrame for plotting
        df = pd.DataFrame(index=sorted(improvements.keys()), columns=sorted(all_metrics))
        
        # Fill DataFrame with data
        for story_id, story_improvements in improvements.items():
            for metric, value in story_improvements.items():
                df.at[story_id, metric] = value
                
        # Fill NaN values with 0
        df = df.fillna(0)
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Plot as grouped bar chart
        df.plot(kind='bar', ax=ax)
        
        # Add gridlines
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Set labels and title
        ax.set_xlabel('Story ID')
        ax.set_ylabel('Improvement')
        ax.set_title('Improvements Over Baseline')
        
        # Add legend
        ax.legend(title='Metrics')
        
        plt.tight_layout()
        
        # Convert to base64
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100)
        buf.seek(0)
        plt.close(fig)
        
        return base64.b64encode(buf.read()).decode('utf-8')
    
    def generate_dashboard(self) -> str:
        """
        Generate a Markdown dashboard with progress analytics.
        
        Returns:
            Markdown string of the dashboard
        """
        # Generate all plots
        story_progress_plot = self._plot_story_progress()
        overall_progress_plot = self._plot_overall_progress()
        research_plot = self._plot_research_implementation()
        tech_debt_plot = self._plot_tech_debt_trend()
        ml_debt_plot = self._plot_ml_debt_categories()
        baseline_plot = self._plot_baseline_improvements()
        experiment_plots = self._plot_experiment_metrics()
        
        # Generate Markdown
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        overall_progress = self.analytics.get_overall_epic_progress() * 100  # Convert to percentage
        
        md = [
            f"# Epic 4: Dynamic Schedule Rebalancing - Progress Dashboard\n\n",
            f"**Generated:** {timestamp}\n\n",
            f"**Overall Progress:** {overall_progress:.1f}%\n\n",
            
            "## Progress Overview\n\n"
        ]
        
        if overall_progress_plot:
            md.append(f"![Overall Progress](data:image/png;base64,{overall_progress_plot})\n\n")
            
        if story_progress_plot:
            md.append("### Story Progress\n\n")
            md.append(f"![Story Progress](data:image/png;base64,{story_progress_plot})\n\n")
            
        # Add story details table
        md.append("### Story Details\n\n")
        md.append("| Story ID | Title | Status | Current Stage | Progress |\n")
        md.append("|----------|-------|--------|---------------|----------|\n")
        
        for story_id, story in sorted(self.analytics.stories.items()):
            current_stage = story.current_stage.value if isinstance(story.current_stage, MLTaskStage) else story.current_stage
            md.append(f"| {story.story_id} | {story.title} | {story.status} | {current_stage} | {story.progress*100:.1f}% |\n")
            
        md.append("\n")
        
        # Add research implementation section if available
        if research_plot:
            md.append("## Research Implementation\n\n")
            md.append(f"![Research Implementation](data:image/png;base64,{research_plot})\n\n")
            
            # Add research details table
            md.append("### Research Implementation Details\n\n")
            md.append("| Research | Source | Implementation Progress | Related Stories |\n")
            md.append("|----------|--------|-------------------------|----------------|\n")
            
            for research_id, research in sorted(self.analytics.research_implementations.items()):
                related_stories = ", ".join(research.related_stories) if research.related_stories else "None"
                md.append(f"| {research.title} | {research.source} | {research.implementation_progress*100:.1f}% | {related_stories} |\n")
                
            md.append("\n")
        
        # Add technical debt section if available
        if tech_debt_plot or ml_debt_plot:
            md.append("## Technical Debt\n\n")
            
            if tech_debt_plot:
                md.append(f"![Technical Debt Trend](data:image/png;base64,{tech_debt_plot})\n\n")
                
            if ml_debt_plot:
                md.append(f"![ML Debt Categories](data:image/png;base64,{ml_debt_plot})\n\n")
                
            # Add current technical debt summary if available
            if self.analytics.technical_debt_history:
                latest_debt = self.analytics.technical_debt_history[-1]
                
                md.append("### Current Technical Debt Summary\n\n")
                md.append(f"**Date:** {latest_debt.date}\n\n")
                md.append(f"**Total Debt Score:** {latest_debt.total_debt_score:.2f}\n\n")
                
                if latest_debt.debt_by_ml_category:
                    md.append("#### ML-Specific Debt Categories\n\n")
                    md.append("| Category | Issue Count |\n")
                    md.append("|----------|------------|\n")
                    
                    for category, count in sorted(latest_debt.debt_by_ml_category.items(), key=lambda x: x[1], reverse=True):
                        clean_category = category.replace('_', ' ').title() if isinstance(category, str) else str(category)
                        md.append(f"| {clean_category} | {count} |\n")
                        
                    md.append("\n")
        
        # Add experiment metrics section if available
        if experiment_plots:
            md.append("## Experiment Metrics\n\n")
            
            for metric_name, plot in experiment_plots.items():
                md.append(f"### {metric_name}\n\n")
                md.append(f"![{metric_name}](data:image/png;base64,{plot})\n\n")
                
        # Add baseline improvements section if available
        if baseline_plot:
            md.append("## Improvements Over Baseline\n\n")
            md.append(f"![Baseline Improvements](data:image/png;base64,{baseline_plot})\n\n")
            
            # Add baseline improvements table
            improvements = self.analytics.get_baseline_improvements()
            
            if improvements:
                md.append("### Metric Improvements by Story\n\n")
                
                # Get all metrics
                all_metrics = set()
                for story_improvements in improvements.values():
                    all_metrics.update(story_improvements.keys())
                    
                # Create table header
                md.append("| Story ID | " + " | ".join(sorted(all_metrics)) + " |\n")
                md.append("|----------|" + "|".join(["---------" for _ in all_metrics]) + "|\n")
                
                # Add rows
                for story_id, story_improvements in sorted(improvements.items()):
                    row = [story_id]
                    for metric in sorted(all_metrics):
                        value = story_improvements.get(metric, "N/A")
                        if isinstance(value, (int, float)):
                            row.append(f"{value:.2f}")
                        else:
                            row.append(str(value))
                    md.append("| " + " | ".join(row) + " |\n")
                    
                md.append("\n")
        
        return "".join(md)
    
    def save_dashboard(self, markdown_content: str = None) -> str:
        """
        Save the dashboard to a file.
        
        Args:
            markdown_content: Optional content to save, or None to generate new content
            
        Returns:
            Path to the saved file
        """
        if markdown_content is None:
            markdown_content = self.generate_dashboard()
            
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = os.path.join(self.output_dir, f"epic4_progress_dashboard_{timestamp}.md")
        
        with open(output_path, "w") as f:
            f.write(markdown_content)
            
        print(f"Dashboard saved to {output_path}")
        return output_path

def main():
    """Main function to run the progress analytics system."""
    parser = argparse.ArgumentParser(
        description="Epic 4 Progress Analytics System"
    )
    
    # Add subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Dashboard generation command
    dashboard_parser = subparsers.add_parser("dashboard", help="Generate a progress dashboard")
    dashboard_parser.add_argument(
        "--output-dir", 
        help="Output directory for the dashboard"
    )
    
    # Update story command
    update_story_parser = subparsers.add_parser("update-story", help="Update a story's progress")
    update_story_parser.add_argument(
        "story_id", 
        help="ID of the story to update"
    )
    update_story_parser.add_argument(
        "--status", 
        choices=["Not Started", "In Progress", "Done"],
        help="New status for the story"
    )
    update_story_parser.add_argument(
        "--stage", 
        choices=[stage.value for stage in MLTaskStage],
        help="Current stage of the story"
    )
    update_story_parser.add_argument(
        "--complete-stage",
        action="store_true",
        help="Mark the current stage as completed"
    )
    
    # Add experiment command
    add_experiment_parser = subparsers.add_parser("add-experiment", help="Add an experiment")
    add_experiment_parser.add_argument(
        "story_id",
        help="ID of the story for the experiment"
    )
    add_experiment_parser.add_argument(
        "title",
        help="Title of the experiment"
    )
    add_experiment_parser.add_argument(
        "--ml-task-type",
        help="ML task type for the experiment",
        default="reinforcement_learning"
    )
    add_experiment_parser.add_argument(
        "--metrics",
        help="Comma-separated list of metric=value pairs (e.g., accuracy=0.85,loss=0.2)",
        required=True
    )
    add_experiment_parser.add_argument(
        "--parameters",
        help="Comma-separated list of param=value pairs (e.g., learning_rate=0.01,batch_size=32)"
    )
    add_experiment_parser.add_argument(
        "--tags",
        help="Comma-separated list of tags"
    )
    add_experiment_parser.add_argument(
        "--baseline",
        action="store_true",
        help="Mark this experiment as a baseline"
    )
    
    # Add research implementation command
    add_research_parser = subparsers.add_parser("add-research", help="Add a research implementation")
    add_research_parser.add_argument(
        "title",
        help="Title of the research"
    )
    add_research_parser.add_argument(
        "source",
        help="Source of the research"
    )
    add_research_parser.add_argument(
        "--insights",
        help="Comma-separated list of key insights",
        required=True
    )
    add_research_parser.add_argument(
        "--implemented-insights",
        help="Comma-separated list of implemented insights"
    )
    add_research_parser.add_argument(
        "--related-stories",
        help="Comma-separated list of related story IDs"
    )
    
    # Update tech debt command
    tech_debt_parser = subparsers.add_parser("update-tech-debt", help="Update technical debt record")
    tech_debt_parser.add_argument(
        "--detect",
        action="store_true",
        help="Run technical debt detection"
    )
    
    # List stories command
    list_stories_parser = subparsers.add_parser("list-stories", help="List all stories and their progress")
    
    # List experiments command
    list_experiments_parser = subparsers.add_parser("list-experiments", help="List all experiments")
    list_experiments_parser.add_argument(
        "--story-id",
        help="Filter by story ID"
    )
    
    # List research command
    list_research_parser = subparsers.add_parser("list-research", help="List all research implementations")
    
    args = parser.parse_args()
    
    # Initialize the analytics engine
    analytics = ProgressAnalyticsEngine()
    
    # Process the command
    if args.command == "dashboard":
        # Generate dashboard
        dashboard = ProgressDashboardGenerator(analytics, output_dir=args.output_dir)
        dashboard_path = dashboard.save_dashboard()
        print(f"Dashboard generated successfully at {dashboard_path}")
        
    elif args.command == "update-story":
        # Update story progress
        story_id = args.story_id
        
        if args.status or args.stage:
            # Update story fields
            update_kwargs = {}
            if args.status:
                update_kwargs["status"] = args.status
            if args.stage:
                update_kwargs["current_stage"] = MLTaskStage(args.stage)
                
            story = analytics.update_story(story_id, **update_kwargs)
            print(f"Story {story_id} updated: {story.status}, Stage: {story.current_stage.value}")
            
        if args.complete_stage:
            # Complete the current stage
            stage_to_complete = analytics.stories[story_id].current_stage
            story = analytics.complete_story_stage(story_id, stage_to_complete)
            print(f"Completed stage {stage_to_complete.value} for story {story_id}")
            print(f"Progress: {story.progress*100:.1f}%")
            
    elif args.command == "add-experiment":
        # Add experiment
        # Parse metrics
        metrics = {}
        for metric_pair in args.metrics.split(","):
            name, value = metric_pair.split("=")
            metrics[name.strip()] = float(value.strip())
            
        # Parse parameters
        parameters = {}
        if args.parameters:
            for param_pair in args.parameters.split(","):
                name, value = param_pair.split("=")
                try:
                    # Try to convert to number if possible
                    parameters[name.strip()] = float(value.strip())
                except ValueError:
                    parameters[name.strip()] = value.strip()
                    
        # Parse tags
        tags = []
        if args.tags:
            tags = [tag.strip() for tag in args.tags.split(",")]
            
        # Create experiment
        experiment = MLExperiment(
            experiment_id="",  # Will be generated
            story_id=args.story_id,
            title=args.title,
            ml_task_type=args.ml_task_type,
            metrics=metrics,
            parameters=parameters,
            tags=tags,
            is_baseline=args.baseline
        )
        
        # Add experiment
        experiment_id = analytics.add_experiment(experiment)
        print(f"Added experiment {experiment_id} for story {args.story_id}")
        if args.baseline:
            print(f"Set as baseline for story {args.story_id}")
            
    elif args.command == "add-research":
        # Add research implementation
        # Parse insights
        insights = [insight.strip() for insight in args.insights.split(",")]
        
        # Parse implemented insights
        implemented_insights = []
        if args.implemented_insights:
            implemented_insights = [insight.strip() for insight in args.implemented_insights.split(",")]
            
        # Parse related stories
        related_stories = []
        if args.related_stories:
            related_stories = [story_id.strip() for story_id in args.related_stories.split(",")]
            
        # Create research implementation
        research = ResearchImplementation(
            research_id="",  # Will be generated
            title=args.title,
            source=args.source,
            key_insights=insights,
            implemented_insights=implemented_insights,
            related_stories=related_stories
        )
        
        # Add research implementation
        research_id = analytics.add_research_implementation(research)
        print(f"Added research implementation {research_id}")
        progress = research.implementation_progress * 100
        print(f"Implementation progress: {progress:.1f}%")
        
    elif args.command == "update-tech-debt":
        # Update technical debt record
        record = analytics.add_technical_debt_record(detect_current=args.detect)
        print(f"Added technical debt record for {record.date}")
        print(f"Total debt score: {record.total_debt_score:.2f}")
        
        if record.debt_by_ml_category:
            print("ML-specific debt categories:")
            for category, count in sorted(record.debt_by_ml_category.items(), key=lambda x: x[1], reverse=True):
                category_name = category.replace("_", " ").title() if isinstance(category, str) else str(category)
                print(f"  {category_name}: {count}")
                
    elif args.command == "list-stories":
        # List all stories
        print("Epic 4 Stories:")
        print("=" * 80)
        print(f"{'Story ID':<10} {'Title':<50} {'Status':<12} {'Progress':<10}")
        print("-" * 80)
        
        for story_id, story in sorted(analytics.stories.items()):
            progress = story.calculate_progress() * 100
            print(f"{story.story_id:<10} {story.title[:50]:<50} {story.status:<12} {progress:<10.1f}%")
            
    elif args.command == "list-experiments":
        # List all experiments
        filtered_experiments = list(analytics.experiments.values())
        if args.story_id:
            filtered_experiments = [exp for exp in filtered_experiments if exp.story_id == args.story_id]
            
        if not filtered_experiments:
            print("No experiments found.")
            return
            
        print("Experiments:")
        print("=" * 100)
        print(f"{'ID':<15} {'Story':<10} {'Title':<35} {'ML Task Type':<20} {'Created':<15}")
        print("-" * 100)
        
        for exp in sorted(filtered_experiments, key=lambda e: e.created_at):
            created_str = exp.created_at.strftime("%Y-%m-%d")
            print(f"{exp.experiment_id[:15]:<15} {exp.story_id:<10} {exp.title[:35]:<35} {exp.ml_task_type[:20]:<20} {created_str:<15}")
            
        # Print metrics
        print("\nMetrics:")
        for exp in sorted(filtered_experiments, key=lambda e: e.created_at):
            print(f"\n{exp.title} ({exp.experiment_id}):")
            for metric, value in exp.metrics.items():
                print(f"  {metric}: {value}")
                
    elif args.command == "list-research":
        # List all research implementations
        if not analytics.research_implementations:
            print("No research implementations found.")
            return
            
        print("Research Implementations:")
        print("=" * 100)
        print(f"{'ID':<15} {'Title':<35} {'Source':<30} {'Progress':<10}")
        print("-" * 100)
        
        for research_id, research in sorted(analytics.research_implementations.items()):
            progress = research.calculate_progress() * 100
            print(f"{research_id[:15]:<15} {research.title[:35]:<35} {research.source[:30]:<30} {progress:<10.1f}%")
            
        # Print insights
        for research_id, research in sorted(analytics.research_implementations.items()):
            print(f"\n{research.title}:")
            print("  Key insights:")
            for i, insight in enumerate(research.key_insights):
                implemented = " [IMPLEMENTED]" if insight in research.implemented_insights else ""
                print(f"    {i+1}. {insight}{implemented}")
                
    else:
        # No command provided, show help
        parser.print_help()

if __name__ == "__main__":
    main() 