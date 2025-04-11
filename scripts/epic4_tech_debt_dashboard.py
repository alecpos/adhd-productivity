#!/usr/bin/env python3
"""
Epic 4 Technical Debt Dashboard Generator

This script generates a Markdown dashboard visualizing the state of Epic 4 specific
technical debt in the project, with a focus on ML development issues.
"""

import os
import sys
import json
import subprocess
import datetime
from typing import Dict, List, Any, Optional
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import numpy as np
import io
import base64
from collections import Counter

# Add project root to path to enable imports
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.append(ROOT_DIR)

from scripts.ml_tech_debt_patterns import MLDebtSubcategory, get_tech_debt_by_subcategory


class Epic4TechDebtDashboard:
    """Generator for Epic 4 technical debt dashboards."""

    def __init__(self, output_dir: str = None):
        """Initialize the dashboard generator."""
        self.output_dir = output_dir or os.path.join(ROOT_DIR, "docs")
        os.makedirs(self.output_dir, exist_ok=True)

    def run_debt_detection(self) -> Dict[str, Any]:
        """Run technical debt detection for Epic 4 and return results."""
        try:
            cmd = [
                "python",
                os.path.join(SCRIPT_DIR, "detect_tech_debt.py"),
                "--all",
                "--json",
                "--epic",
                "Epic 4",
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return json.loads(result.stdout)
        except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
            print(f"Error running technical debt detection: {e}")
            return {"results": [], "score": 0, "assessment": "Error", "recommendations": []}

    def _plot_subcategory_distribution(self, results: List[Dict[str, Any]]) -> str:
        """Generate a plot showing the distribution of issues by subcategory."""
        # Count issues by subcategory
        subcategory_counts = Counter()
        for result in results:
            subcategory = result.get("subcategory")
            if subcategory:
                if isinstance(subcategory, dict) and "value" in subcategory:
                    subcategory = subcategory["value"]
                subcategory_counts[subcategory] += 1

        if not subcategory_counts:
            return ""

        # Create the plot
        fig, ax = plt.subplots(figsize=(10, 6))

        # Sort by count
        labels = [
            k for k, v in sorted(subcategory_counts.items(), key=lambda x: x[1], reverse=True)
        ]
        counts = [subcategory_counts[label] for label in labels]

        # Clean up labels
        clean_labels = [label.replace("_", " ").title() for label in labels]

        # Create a custom colormap that goes from yellow to red
        cmap = LinearSegmentedColormap.from_list("yellow_to_red", ["#ffffcc", "#ff0000"])
        colors = cmap(np.linspace(0, 1, len(counts)))

        ax.bar(clean_labels, counts, color=colors)
        ax.set_title("Technical Debt by ML Subcategory")
        ax.set_ylabel("Number of Issues")
        ax.set_xticklabels(clean_labels, rotation=45, ha="right")

        plt.tight_layout()

        # Convert plot to base64 for Markdown embedding
        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)
        plt.close(fig)

        return base64.b64encode(buf.read()).decode("utf-8")

    def _plot_severity_by_subcategory(self, results: List[Dict[str, Any]]) -> str:
        """Generate a plot showing the severity by subcategory."""
        # Aggregate data
        data = {}
        for result in results:
            subcategory = result.get("subcategory")
            severity = result.get("severity")

            if subcategory and severity:
                if isinstance(subcategory, dict) and "value" in subcategory:
                    subcategory = subcategory["value"]
                if isinstance(severity, dict) and "value" in severity:
                    severity = severity["value"]

                if subcategory not in data:
                    data[subcategory] = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}

                data[subcategory][severity] += 1

        if not data:
            return ""

        # Convert to DataFrame for easier plotting
        df = pd.DataFrame(data).T.fillna(0)

        # Sort by total issues
        df["total"] = df.sum(axis=1)
        df = df.sort_values("total", ascending=False).drop("total", axis=1)

        # Clean up index
        df.index = [idx.replace("_", " ").title() for idx in df.index]

        # Create plot
        fig, ax = plt.subplots(figsize=(10, 6))

        df.plot(kind="bar", stacked=True, ax=ax, color=["#ff0000", "#ff9900", "#ffcc00", "#99cc00"])

        ax.set_title("Technical Debt Severity by ML Subcategory")
        ax.set_ylabel("Number of Issues")
        ax.set_xticklabels(df.index, rotation=45, ha="right")

        plt.tight_layout()

        # Convert plot to base64 for Markdown embedding
        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)
        plt.close(fig)

        return base64.b64encode(buf.read()).decode("utf-8")

    def generate_epic4_dashboard(self) -> str:
        """Generate the Epic 4 technical debt dashboard in Markdown format."""
        # Get technical debt results
        debt_data = self.run_debt_detection()
        results = debt_data.get("results", [])

        # Generate plots
        subcategory_plot = self._plot_subcategory_distribution(results)
        severity_plot = self._plot_severity_by_subcategory(results)

        # Generate Markdown dashboard
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        md = [
            f"# Epic 4: Technical Debt Dashboard\n",
            f"**Generated:** {timestamp}\n",
            f"**Total Debt Score:** {debt_data.get('score', 0)}\n",
            f"**Assessment:** {debt_data.get('assessment', 'N/A')}\n\n",
            "## Debt Overview\n\n",
        ]

        # Add plots if available
        if subcategory_plot:
            md.append(f"### Technical Debt by ML Subcategory\n\n")
            md.append(f"![Subcategory Distribution](data:image/png;base64,{subcategory_plot})\n\n")

        if severity_plot:
            md.append(f"### Technical Debt Severity by Subcategory\n\n")
            md.append(f"![Severity Distribution](data:image/png;base64,{severity_plot})\n\n")

        # Add research-informed recommendations
        md.append("## Research-Informed Recommendations\n\n")

        epic_recommendations = debt_data.get("epic_recommendations", [])
        if epic_recommendations:
            for rec in epic_recommendations:
                md.append(f"- {rec}\n")
        else:
            md.append("*No epic-specific recommendations available.*\n")

        md.append("\n## Technical Debt Issues\n\n")

        # Group issues by subcategory
        issues_by_subcategory = {}
        for result in results:
            subcategory = result.get("subcategory")
            if subcategory:
                if isinstance(subcategory, dict) and "value" in subcategory:
                    subcategory = subcategory["value"]

                if subcategory not in issues_by_subcategory:
                    issues_by_subcategory[subcategory] = []

                issues_by_subcategory[subcategory].append(result)

        # Add issues by subcategory
        for subcategory, issues in sorted(issues_by_subcategory.items()):
            clean_subcategory = subcategory.replace("_", " ").title()
            md.append(f"### {clean_subcategory}\n\n")

            md.append("| File | Line | Issue | Severity |\n")
            md.append("|------|------|-------|----------|\n")

            for issue in issues:
                severity = issue.get("severity")
                if isinstance(severity, dict) and "value" in severity:
                    severity = severity["value"]

                file_path = issue.get("file_path", "").replace(ROOT_DIR + "/", "")
                line = issue.get("line_number", "")
                message = issue.get("message", "")

                md.append(f"| {file_path} | {line} | {message} | {severity} |\n")

            md.append("\n")

        # Return the dashboard content
        return "".join(md)

    def save_dashboard(self, markdown_content: str) -> str:
        """Save dashboard to a Markdown file."""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(self.output_dir, f"epic4_tech_debt_dashboard_{timestamp}.md")

        with open(output_path, "w") as f:
            f.write(markdown_content)

        print(f"Dashboard saved to {output_path}")
        return output_path


def main():
    """Main function to generate the Epic 4 technical debt dashboard."""
    parser = argparse.ArgumentParser(description="Generate Epic 4 technical debt dashboard")
    parser.add_argument("--output-dir", help="Output directory for dashboard")

    args = parser.parse_args()

    dashboard = Epic4TechDebtDashboard(output_dir=args.output_dir)
    markdown_content = dashboard.generate_epic4_dashboard()
    dashboard.save_dashboard(markdown_content)


if __name__ == "__main__":
    import argparse

    main()
