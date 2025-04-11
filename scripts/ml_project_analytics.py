#!/usr/bin/env python3
"""
ML Project Analytics Dashboard.

This script collects, analyzes, and visualizes metrics from ML experiments,
model training, and project progress. It integrates with the existing metrics
system and provides actionable insights on model performance and project status.
"""

import os
import sys
import json
import datetime
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union
import re
import glob

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from tabulate import tabulate

try:
    from sklearn.metrics import (
        confusion_matrix,
        classification_report,
        mean_squared_error,
        r2_score,
    )
except ImportError:
    # Mock these if not available
    confusion_matrix = lambda y_true, y_pred: np.zeros((len(set(y_true)), len(set(y_true))))
    classification_report = lambda y_true, y_pred: "Not available"
    mean_squared_error = lambda y_true, y_pred: ((y_true - y_pred) ** 2).mean()
    r2_score = lambda y_true, y_pred: 0.0

# Add project root to path to enable imports
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

# Import project-specific utilities if available
try:
    from app.utils.metrics import ServiceMetrics
except ImportError:
    # Create a mock ServiceMetrics class
    class ServiceMetrics:
        def __init__(self, name):
            self.name = name


class MLProjectAnalytics:
    """ML project analytics and visualization dashboard."""

    def __init__(self, output_dir: Optional[str] = None):
        """Initialize the analytics dashboard."""
        self.output_dir = output_dir or os.path.join(project_root, "docs", "ml_analytics")

        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)

        # Set up date information
        self.today = datetime.datetime.now()
        self.date_str = self.today.strftime("%Y-%m-%d")

        # Initialize service metrics
        self.metrics = ServiceMetrics("ml_analytics")

        # Initialize model collections
        self.models = {}
        self.experiments = {}
        self.performance_history = {}

    def scan_model_directories(self, base_dir: Optional[str] = None) -> None:
        """Scan directories for model files and metadata."""
        base_dir = base_dir or os.path.join(project_root, "app", "ml", "saved_models")

        print(f"Scanning for models in {base_dir}...")

        # Find all model directories
        model_dirs = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]

        for model_dir in model_dirs:
            model_path = os.path.join(base_dir, model_dir)
            metadata_path = os.path.join(model_path, "metadata.json")

            if os.path.exists(metadata_path):
                try:
                    with open(metadata_path, "r") as f:
                        metadata = json.load(f)

                    self.models[model_dir] = metadata
                    print(f"Found model: {model_dir}")
                except Exception as e:
                    print(f"Error reading metadata for {model_dir}: {e}")

        print(f"Found {len(self.models)} models with metadata.")

    def scan_experiment_logs(self, logs_dir: Optional[str] = None) -> None:
        """Scan experiment log files for training metrics."""
        logs_dir = logs_dir or os.path.join(project_root, "app", "ml", "logs")

        print(f"Scanning for experiment logs in {logs_dir}...")

        # Find all log files
        log_files = glob.glob(os.path.join(logs_dir, "*.json"))

        for log_file in log_files:
            try:
                with open(log_file, "r") as f:
                    log_data = json.load(f)

                experiment_id = os.path.basename(log_file).replace(".json", "")
                self.experiments[experiment_id] = log_data
                print(f"Found experiment log: {experiment_id}")
            except Exception as e:
                print(f"Error reading log file {log_file}: {e}")

        print(f"Found {len(self.experiments)} experiment logs.")

    def collect_performance_history(self) -> None:
        """Collect historical performance metrics for models."""
        print("Collecting model performance history...")

        # Extract performance metrics from models and experiments
        for model_id, model_data in self.models.items():
            # Get evaluation metrics if available
            eval_metrics = model_data.get("evaluation_metrics", {})

            if eval_metrics:
                timestamp = model_data.get("created_at") or model_data.get("timestamp")

                if not timestamp:
                    continue

                # Convert timestamp to datetime
                if isinstance(timestamp, str):
                    try:
                        timestamp = datetime.datetime.fromisoformat(timestamp)
                    except ValueError:
                        # Try common formats
                        for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"]:
                            try:
                                timestamp = datetime.datetime.strptime(timestamp, fmt)
                                break
                            except ValueError:
                                continue

                # Skip if we couldn't parse the timestamp
                if not isinstance(timestamp, datetime.datetime):
                    continue

                # Add to performance history
                if model_id not in self.performance_history:
                    self.performance_history[model_id] = []

                self.performance_history[model_id].append(
                    {
                        "timestamp": timestamp,
                        "metrics": eval_metrics,
                        "version": model_data.get("version", "unknown"),
                    }
                )

        # Sort history by timestamp
        for model_id in self.performance_history:
            self.performance_history[model_id].sort(key=lambda x: x["timestamp"])

        print(f"Collected performance history for {len(self.performance_history)} models.")

    def analyze_experiment_trends(self) -> Dict[str, Any]:
        """Analyze trends across experiments."""
        print("Analyzing experiment trends...")

        trends = {"hyperparameters": {}, "metrics": {}, "training_times": [], "model_sizes": []}

        # Collect hyperparameters and metrics
        for exp_id, exp_data in self.experiments.items():
            # Training time
            if "start_time" in exp_data and "end_time" in exp_data:
                try:
                    start = datetime.datetime.fromisoformat(exp_data["start_time"])
                    end = datetime.datetime.fromisoformat(exp_data["end_time"])
                    duration = (end - start).total_seconds() / 60  # in minutes

                    trends["training_times"].append(
                        {
                            "experiment_id": exp_id,
                            "duration_minutes": duration,
                            "model_type": exp_data.get("model_type", "unknown"),
                        }
                    )
                except (ValueError, TypeError):
                    pass

            # Model size
            if "model_size_kb" in exp_data:
                trends["model_sizes"].append(
                    {
                        "experiment_id": exp_id,
                        "size_kb": exp_data["model_size_kb"],
                        "model_type": exp_data.get("model_type", "unknown"),
                    }
                )

            # Hyperparameters
            hyperparams = exp_data.get("hyperparameters", {})
            for param, value in hyperparams.items():
                if param not in trends["hyperparameters"]:
                    trends["hyperparameters"][param] = []

                trends["hyperparameters"][param].append(
                    {
                        "experiment_id": exp_id,
                        "value": value,
                        "performance": exp_data.get("best_metric", 0),
                    }
                )

            # Metrics
            metrics = exp_data.get("metrics", {})
            for metric_name, metric_value in metrics.items():
                if metric_name not in trends["metrics"]:
                    trends["metrics"][metric_name] = []

                # Only add if it's a numeric value
                if isinstance(metric_value, (int, float)):
                    trends["metrics"][metric_name].append(
                        {
                            "experiment_id": exp_id,
                            "value": metric_value,
                            "model_type": exp_data.get("model_type", "unknown"),
                            "timestamp": exp_data.get("end_time", ""),
                        }
                    )

        return trends

    def identify_best_models(self) -> Dict[str, Dict[str, Any]]:
        """Identify the best models for each task."""
        print("Identifying best models...")

        best_models = {}
        task_groups = {}

        # Group models by task
        for model_id, model_data in self.models.items():
            task = model_data.get("task", "unknown")

            if task not in task_groups:
                task_groups[task] = []

            task_groups[task].append((model_id, model_data))

        # Find best model for each task
        for task, models in task_groups.items():
            if not models:
                continue

            # Determine the primary metric for this task
            primary_metric = self._get_primary_metric_for_task(task)

            # Find the model with the best metric
            best_model = None
            best_value = None

            for model_id, model_data in models:
                metrics = model_data.get("evaluation_metrics", {})

                if primary_metric not in metrics:
                    continue

                value = metrics[primary_metric]

                if not isinstance(value, (int, float)):
                    continue

                # Higher is better for most metrics
                # For error metrics (MSE, RMSE, etc.), lower is better
                is_error_metric = any(
                    err in primary_metric.lower() for err in ["error", "loss", "mse", "rmse", "mae"]
                )

                if (
                    best_value is None
                    or (is_error_metric and value < best_value)
                    or (not is_error_metric and value > best_value)
                ):
                    best_value = value
                    best_model = (model_id, model_data)

            if best_model:
                model_id, model_data = best_model
                best_models[task] = {
                    "model_id": model_id,
                    "metrics": model_data.get("evaluation_metrics", {}),
                    "created_at": model_data.get("created_at", ""),
                    "version": model_data.get("version", "unknown"),
                    "hyperparameters": model_data.get("hyperparameters", {}),
                }

        return best_models

    def _get_primary_metric_for_task(self, task: str) -> str:
        """Determine the primary evaluation metric for a task."""
        task_lower = task.lower()

        if "classification" in task_lower:
            return "accuracy"
        elif "regression" in task_lower:
            return "r2_score"
        elif "recommendation" in task_lower:
            return "precision_at_k"
        elif "similarity" in task_lower:
            return "cosine_similarity"
        elif "clustering" in task_lower:
            return "silhouette_score"
        elif "generation" in task_lower:
            return "bleu_score"
        elif "reinforcement" in task_lower:
            return "reward"
        else:
            return "accuracy"  # Default

    def calculate_project_metrics(self) -> Dict[str, Any]:
        """Calculate overall project metrics."""
        print("Calculating project metrics...")

        metrics = {
            "model_count": len(self.models),
            "experiment_count": len(self.experiments),
            "tasks_covered": len(
                set(model.get("task", "unknown") for model in self.models.values())
            ),
            "model_types": set(
                model.get("model_type", "unknown") for model in self.models.values()
            ),
            "latest_model_date": None,
            "improvement_trends": {},
            "average_training_time": None,
            "experiment_success_rate": 0,
        }

        # Latest model date
        dates = []
        for model in self.models.values():
            created_at = model.get("created_at") or model.get("timestamp")
            if created_at:
                try:
                    if isinstance(created_at, str):
                        created_at = datetime.datetime.fromisoformat(
                            created_at.replace("Z", "+00:00")
                        )
                    dates.append(created_at)
                except (ValueError, TypeError):
                    pass

        if dates:
            metrics["latest_model_date"] = max(dates)

        # Improvement trends
        for model_id, history in self.performance_history.items():
            if len(history) <= 1:
                continue

            first = history[0]
            last = history[-1]

            for metric, value in first["metrics"].items():
                if (
                    metric in last["metrics"]
                    and isinstance(value, (int, float))
                    and isinstance(last["metrics"][metric], (int, float))
                ):
                    if model_id not in metrics["improvement_trends"]:
                        metrics["improvement_trends"][model_id] = {}

                    # Calculate improvement percentage
                    # For error metrics, improvement is a decrease
                    is_error_metric = any(
                        err in metric.lower() for err in ["error", "loss", "mse", "rmse", "mae"]
                    )

                    if is_error_metric:
                        if value > 0:  # Avoid division by zero
                            improvement = (value - last["metrics"][metric]) / value * 100
                        else:
                            improvement = 0
                    else:
                        if value > 0:  # Avoid division by zero
                            improvement = (last["metrics"][metric] - value) / value * 100
                        else:
                            improvement = (
                                last["metrics"][metric] * 100
                            )  # Treat as 100% improvement from 0

                    metrics["improvement_trends"][model_id][metric] = improvement

        # Average training time
        training_times = []
        for exp in self.experiments.values():
            if "start_time" in exp and "end_time" in exp:
                try:
                    start = datetime.datetime.fromisoformat(exp["start_time"])
                    end = datetime.datetime.fromisoformat(exp["end_time"])
                    duration = (end - start).total_seconds() / 60  # in minutes
                    training_times.append(duration)
                except (ValueError, TypeError):
                    pass

        if training_times:
            metrics["average_training_time"] = sum(training_times) / len(training_times)

        # Experiment success rate
        if self.experiments:
            success_count = sum(
                1 for exp in self.experiments.values() if exp.get("status") == "success"
            )
            metrics["experiment_success_rate"] = success_count / len(self.experiments) * 100

        return metrics

    def generate_performance_charts(self) -> Dict[str, str]:
        """Generate charts visualizing model performance."""
        print("Generating performance charts...")

        chart_files = {}

        # Create directory for charts
        charts_dir = os.path.join(self.output_dir, "charts")
        os.makedirs(charts_dir, exist_ok=True)

        # 1. Model performance by task
        best_models = self.identify_best_models()
        if best_models:
            plt.figure(figsize=(12, 8))

            tasks = list(best_models.keys())
            metrics = []

            # Get the most common metric across all models
            all_metrics = []
            for model_data in best_models.values():
                all_metrics.extend(model_data["metrics"].keys())

            if not all_metrics:
                print("No metrics found for model performance chart.")
            else:
                most_common_metric = max(set(all_metrics), key=all_metrics.count)

                # Get values for this metric
                for task in tasks:
                    model_data = best_models[task]
                    value = model_data["metrics"].get(most_common_metric, 0)
                    metrics.append(value)

                # Create chart
                plt.bar(tasks, metrics)
                plt.title(f"Best Model Performance by Task ({most_common_metric})")
                plt.xlabel("Task")
                plt.ylabel(most_common_metric)
                plt.xticks(rotation=45, ha="right")
                plt.tight_layout()

                chart_path = os.path.join(
                    charts_dir, f"model_performance_by_task_{self.date_str}.png"
                )
                plt.savefig(chart_path)
                plt.close()

                chart_files["Model Performance by Task"] = chart_path

        # 2. Performance trends over time
        trends = self.analyze_experiment_trends()

        for metric_name, metric_data in trends["metrics"].items():
            if len(metric_data) < 2:
                continue

            plt.figure(figsize=(10, 6))

            # Sort by timestamp
            metric_data.sort(key=lambda x: x["timestamp"] if x["timestamp"] else "")

            # Group by model type
            model_types = {}
            for item in metric_data:
                model_type = item["model_type"]
                if model_type not in model_types:
                    model_types[model_type] = {"timestamps": [], "values": []}

                # Skip items without timestamp
                if not item["timestamp"]:
                    continue

                try:
                    timestamp = datetime.datetime.fromisoformat(
                        item["timestamp"].replace("Z", "+00:00")
                    )
                    model_types[model_type]["timestamps"].append(timestamp)
                    model_types[model_type]["values"].append(item["value"])
                except (ValueError, TypeError):
                    continue

            # Plot each model type
            for model_type, data in model_types.items():
                if data["timestamps"] and data["values"]:
                    plt.plot(data["timestamps"], data["values"], marker="o", label=model_type)

            plt.title(f"{metric_name} Over Time")
            plt.xlabel("Date")
            plt.ylabel(metric_name)
            plt.legend()
            plt.grid(True, linestyle="--", alpha=0.7)
            plt.xticks(rotation=45, ha="right")
            plt.tight_layout()

            chart_path = os.path.join(charts_dir, f"{metric_name}_trend_{self.date_str}.png")
            plt.savefig(chart_path)
            plt.close()

            chart_files[f"{metric_name} Trend"] = chart_path

        # 3. Training times by model type
        if trends["training_times"]:
            plt.figure(figsize=(12, 6))

            # Group by model type
            model_types = {}
            for item in trends["training_times"]:
                model_type = item["model_type"]
                if model_type not in model_types:
                    model_types[model_type] = []

                model_types[model_type].append(item["duration_minutes"])

            # Calculate average training time per model type
            types = []
            times = []

            for model_type, durations in model_types.items():
                types.append(model_type)
                times.append(sum(durations) / len(durations))

            plt.bar(types, times)
            plt.title("Average Training Time by Model Type")
            plt.xlabel("Model Type")
            plt.ylabel("Training Time (minutes)")
            plt.xticks(rotation=45, ha="right")
            plt.tight_layout()

            chart_path = os.path.join(charts_dir, f"training_time_by_model_{self.date_str}.png")
            plt.savefig(chart_path)
            plt.close()

            chart_files["Training Time by Model Type"] = chart_path

        return chart_files

    def generate_dashboard(self, format: str = "markdown") -> str:
        """Generate a dashboard of ML project analytics."""
        print("Generating ML project analytics dashboard...")

        # Scan for models and experiments
        self.scan_model_directories()
        self.scan_experiment_logs()

        # Collect and analyze data
        self.collect_performance_history()
        trends = self.analyze_experiment_trends()
        best_models = self.identify_best_models()
        project_metrics = self.calculate_project_metrics()

        # Generate charts
        chart_files = self.generate_performance_charts()

        # Generate report
        if format == "markdown":
            dashboard = self._generate_markdown_dashboard(
                trends, best_models, project_metrics, chart_files
            )
        elif format == "html":
            dashboard = self._generate_html_dashboard(
                trends, best_models, project_metrics, chart_files
            )
        else:
            dashboard = "Unsupported format"

        # Save dashboard
        output_path = os.path.join(
            self.output_dir, f"ml_project_dashboard_{self.date_str}.{format}"
        )

        with open(output_path, "w") as f:
            f.write(dashboard)

        print(f"Dashboard generated at {output_path}")
        return dashboard

    def _generate_markdown_dashboard(
        self,
        trends: Dict[str, Any],
        best_models: Dict[str, Dict[str, Any]],
        project_metrics: Dict[str, Any],
        chart_files: Dict[str, str],
    ) -> str:
        """Generate a markdown dashboard."""
        lines = [
            "# ML Project Analytics Dashboard",
            f"**Generated on:** {self.date_str}",
            "",
            "## Project Summary",
            "",
        ]

        # Project summary
        summary_table = [
            ["Total Models", project_metrics["model_count"]],
            ["Total Experiments", project_metrics["experiment_count"]],
            ["Tasks Covered", project_metrics["tasks_covered"]],
            ["Model Types", ", ".join(project_metrics["model_types"])],
            [
                "Latest Model",
                (
                    project_metrics["latest_model_date"].strftime("%Y-%m-%d")
                    if project_metrics["latest_model_date"]
                    else "N/A"
                ),
            ],
            [
                "Avg. Training Time",
                (
                    f"{project_metrics['average_training_time']:.1f} minutes"
                    if project_metrics["average_training_time"]
                    else "N/A"
                ),
            ],
            [
                "Experiment Success Rate",
                (
                    f"{project_metrics['experiment_success_rate']:.1f}%"
                    if project_metrics["experiment_success_rate"]
                    else "N/A"
                ),
            ],
        ]

        lines.append(tabulate(summary_table, tablefmt="pipe", headers=["Metric", "Value"]))
        lines.append("")

        # Best models section
        lines.append("## Best Models by Task")
        lines.append("")

        if not best_models:
            lines.append("No models with evaluation metrics found.")
        else:
            for task, model_data in best_models.items():
                lines.append(f"### {task}")
                lines.append("")
                lines.append(f"**Model ID:** {model_data['model_id']}")
                lines.append(f"**Version:** {model_data['version']}")
                lines.append(f"**Created:** {model_data['created_at']}")
                lines.append("")

                # Metrics table
                lines.append("#### Metrics")
                lines.append("")
                metrics_table = []

                for metric, value in model_data["metrics"].items():
                    metrics_table.append([metric, value])

                lines.append(tabulate(metrics_table, tablefmt="pipe", headers=["Metric", "Value"]))
                lines.append("")

                # Hyperparameters table
                if model_data["hyperparameters"]:
                    lines.append("#### Hyperparameters")
                    lines.append("")
                    hyperparams_table = []

                    for param, value in model_data["hyperparameters"].items():
                        hyperparams_table.append([param, value])

                    lines.append(
                        tabulate(
                            hyperparams_table, tablefmt="pipe", headers=["Hyperparameter", "Value"]
                        )
                    )
                    lines.append("")

        # Performance trends
        lines.append("## Performance Trends")
        lines.append("")

        # Add charts
        for chart_desc, chart_file in chart_files.items():
            # Convert to relative path for markdown
            rel_path = os.path.relpath(chart_file, self.output_dir)
            lines.append(f"### {chart_desc}")
            lines.append("")
            lines.append(f"![{chart_desc}]({rel_path})")
            lines.append("")

        # Hyperparameter analysis
        lines.append("## Hyperparameter Analysis")
        lines.append("")

        if not trends["hyperparameters"]:
            lines.append("No hyperparameter data available.")
        else:
            for param, values in trends["hyperparameters"].items():
                if len(values) < 2:
                    continue

                lines.append(f"### {param}")
                lines.append("")

                # Create a table of values and performance
                hp_table = []

                for item in values:
                    hp_table.append([item["experiment_id"], item["value"], item["performance"]])

                lines.append(
                    tabulate(
                        hp_table, tablefmt="pipe", headers=["Experiment", "Value", "Performance"]
                    )
                )
                lines.append("")

        # Improvement analysis
        lines.append("## Model Improvement Analysis")
        lines.append("")

        if not project_metrics["improvement_trends"]:
            lines.append("No improvement data available.")
        else:
            improvement_table = []

            for model_id, metrics in project_metrics["improvement_trends"].items():
                for metric, improvement in metrics.items():
                    improvement_table.append([model_id, metric, f"{improvement:.2f}%"])

            lines.append(
                tabulate(
                    improvement_table, tablefmt="pipe", headers=["Model", "Metric", "Improvement"]
                )
            )
            lines.append("")

        # Recommendations
        lines.append("## Recommendations")
        lines.append("")

        recommendations = self._generate_recommendations(trends, best_models, project_metrics)

        for recommendation in recommendations:
            lines.append(f"- {recommendation}")

        return "\n".join(lines)

    def _generate_html_dashboard(
        self,
        trends: Dict[str, Any],
        best_models: Dict[str, Dict[str, Any]],
        project_metrics: Dict[str, Any],
        chart_files: Dict[str, str],
    ) -> str:
        """Generate an HTML dashboard."""
        # In a real implementation, use a proper HTML template engine
        # For simplicity, we're just building a basic HTML file here
        markdown = self._generate_markdown_dashboard(
            trends, best_models, project_metrics, chart_files
        )

        # Basic conversion to HTML
        html_lines = [
            "<!DOCTYPE html>",
            "<html>",
            "<head>",
            "    <title>ML Project Analytics Dashboard</title>",
            "    <style>",
            "        body { font-family: Arial, sans-serif; margin: 40px; }",
            "        table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }",
            "        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }",
            "        th { background-color: #f2f2f2; }",
            "        h1, h2, h3 { color: #333366; }",
            "        img { max-width: 100%; height: auto; margin: 20px 0; }",
            "    </style>",
            "</head>",
            "<body>",
        ]

        # Simple conversion from markdown to HTML
        in_table = False
        for line in markdown.split("\n"):
            if line.startswith("# "):
                html_lines.append(f"<h1>{line[2:]}</h1>")
            elif line.startswith("## "):
                html_lines.append(f"<h2>{line[3:]}</h2>")
            elif line.startswith("### "):
                html_lines.append(f"<h3>{line[4:]}</h3>")
            elif line.startswith("#### "):
                html_lines.append(f"<h4>{line[5:]}</h4>")
            elif line.startswith("!["):
                # Extract image info
                img_text = line[2:].split("](")[0]
                img_path = line.split("](")[1][:-1]
                html_lines.append(f'<img src="{img_path}" alt="{img_text}"/>')
            elif line.startswith("| "):
                if not in_table:
                    html_lines.append("<table>")
                    in_table = True

                # Convert markdown table row to HTML
                cells = line.split("|")[1:-1]  # Remove empty first/last cells
                is_header = "---" in cells[0] if cells else False

                if is_header:
                    # Skip separator rows
                    continue

                html_lines.append("<tr>")
                for cell in cells:
                    if "**" in cell:
                        # Make bold cells table headers
                        cell = cell.replace("**", "")
                        html_lines.append(f"<th>{cell.strip()}</th>")
                    else:
                        html_lines.append(f"<td>{cell.strip()}</td>")
                html_lines.append("</tr>")
            elif line.startswith("- "):
                html_lines.append(f"<li>{line[2:]}</li>")
            else:
                if in_table and not line.startswith("|"):
                    html_lines.append("</table>")
                    in_table = False

                if line.strip():
                    html_lines.append(f"<p>{line}</p>")

        if in_table:
            html_lines.append("</table>")

        html_lines.append("</body>")
        html_lines.append("</html>")

        return "\n".join(html_lines)

    def _generate_recommendations(
        self,
        trends: Dict[str, Any],
        best_models: Dict[str, Dict[str, Any]],
        project_metrics: Dict[str, Any],
    ) -> List[str]:
        """Generate recommendations based on analysis."""
        recommendations = []

        # Recommend based on model types
        if project_metrics["model_types"]:
            # Check for common model types
            has_ensemble = any("ensemble" in mt.lower() for mt in project_metrics["model_types"])
            has_neural_net = any(
                nn in " ".join(project_metrics["model_types"]).lower()
                for nn in ["neural", "deep", "nn", "transformer", "bert", "gpt"]
            )

            if not has_ensemble:
                recommendations.append(
                    "Consider using ensemble methods to potentially improve model performance."
                )

            if not has_neural_net and project_metrics["model_count"] > 5:
                recommendations.append(
                    "Explore deep learning approaches for tasks with sufficient data."
                )

        # Recommend based on experiment success rate
        if project_metrics["experiment_success_rate"] < 75:
            recommendations.append(
                f"Improve experiment pipeline reliability (current success rate: {project_metrics['experiment_success_rate']:.1f}%)."
            )

        # Recommend based on hyperparameters
        for param, values in trends["hyperparameters"].items():
            if len(values) < 3:
                continue

            # Check if performance correlates with parameter values
            # Simple check - are higher values generally better?
            values_sorted = sorted(
                values, key=lambda x: x["value"] if isinstance(x["value"], (int, float)) else 0
            )

            if len(values_sorted) >= 3:
                first_perf = (
                    values_sorted[0]["performance"]
                    if isinstance(values_sorted[0]["performance"], (int, float))
                    else 0
                )
                last_perf = (
                    values_sorted[-1]["performance"]
                    if isinstance(values_sorted[-1]["performance"], (int, float))
                    else 0
                )

                if last_perf > first_perf * 1.2:  # 20% improvement
                    recommendations.append(
                        f"Consider higher values for '{param}' as they show better performance."
                    )
                elif first_perf > last_perf * 1.2:  # 20% improvement
                    recommendations.append(
                        f"Consider lower values for '{param}' as they show better performance."
                    )

        # Recommend based on training time
        if trends["training_times"]:
            # Find model types with long training times
            avg_times = {}
            for item in trends["training_times"]:
                model_type = item["model_type"]
                if model_type not in avg_times:
                    avg_times[model_type] = []

                avg_times[model_type].append(item["duration_minutes"])

            for model_type, times in avg_times.items():
                avg_time = sum(times) / len(times)

                if avg_time > 60:  # More than 1 hour
                    recommendations.append(
                        f"Optimize training pipeline for {model_type} models (average training time: {avg_time:.1f} minutes)."
                    )

        # General recommendations
        if project_metrics["model_count"] > 0:
            recommendations.append(
                "Implement regular model monitoring to detect performance degradation over time."
            )

            recommendations.append(
                "Consider A/B testing the best models in production to validate offline metrics."
            )

        return recommendations


def main():
    """Main function to run the dashboard generation."""
    parser = argparse.ArgumentParser(description="Generate ML project analytics dashboard.")
    parser.add_argument("--output-dir", help="Directory to store the dashboard output")
    parser.add_argument(
        "--format", choices=["markdown", "html"], default="markdown", help="Output format"
    )
    parser.add_argument("--model-dir", help="Directory containing model files")
    parser.add_argument("--logs-dir", help="Directory containing experiment logs")
    args = parser.parse_args()

    dashboard = MLProjectAnalytics(output_dir=args.output_dir)

    # Scan specific directories if provided
    if args.model_dir:
        dashboard.scan_model_directories(args.model_dir)
    if args.logs_dir:
        dashboard.scan_experiment_logs(args.logs_dir)

    dashboard.generate_dashboard(format=args.format)


if __name__ == "__main__":
    main()
