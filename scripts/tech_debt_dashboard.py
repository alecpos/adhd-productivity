#!/usr/bin/env python3
"""
Technical Debt Dashboard Generator.

This script generates a visual dashboard of technical debt in the project,
including metrics, trends, and prioritized action items. It implements the
debt quantification framework from the research paper.
"""

import os
import sys
import json
import datetime
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from tabulate import tabulate

# Add project root to path to enable imports
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from app.utils.tech_debt import (
    DebtSeverity,
    DebtCategory,
    DebtStatus,
    MLDebtSubcategory,
    get_debt_manager
)

class TechnicalDebtDashboard:
    """Generate technical debt dashboards and reports."""

    def __init__(self, output_dir: Optional[str] = None):
        """Initialize the dashboard generator."""
        self.output_dir = output_dir or os.path.join(project_root, "docs")
        self.debt_manager = get_debt_manager()

        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)

        # Set up date information
        self.today = datetime.datetime.now()
        self.date_str = self.today.strftime("%Y-%m-%d")

    def generate_dashboard(self,
                          include_charts: bool = True,
                          output_format: str = "markdown",
                          include_resolved: bool = False) -> str:
        """Generate the technical debt dashboard."""
        # Generate the debt report from the manager
        report = self.debt_manager.generate_report(
            output_format=output_format,
            include_resolved=include_resolved,
            group_by="category"
        )

        # Get debt metrics for charts
        metrics = self.debt_manager.get_metrics()

        # Generate extended report with prioritization and charts
        if output_format == "markdown":
            dashboard = self._generate_markdown_dashboard(report, metrics, include_charts)
        elif output_format == "html":
            dashboard = self._generate_html_dashboard(report, metrics, include_charts)
        else:
            dashboard = report  # Default to basic report for other formats

        # Save the dashboard
        output_path = os.path.join(
            self.output_dir,
            f"technical_debt_dashboard_{self.date_str}.{output_format}"
        )

        with open(output_path, "w") as f:
            f.write(dashboard)

        print(f"Dashboard generated at {output_path}")
        return dashboard

    def _generate_markdown_dashboard(self,
                                    basic_report: str,
                                    metrics: Dict[str, Any],
                                    include_charts: bool) -> str:
        """Generate a markdown dashboard with charts and prioritization."""
        # Start with a header
        lines = [
            "# Technical Debt Dashboard",
            f"**Generated on:** {self.date_str}",
            "",
            "## Summary Metrics",
            ""
        ]

        # Add summary metrics in a table
        metrics_table = [
            ["Total Items", metrics.get("total_items", 0)],
            ["Critical Items", metrics.get("by_severity", {}).get("critical", 0)],
            ["High Severity Items", metrics.get("by_severity", {}).get("high", 0)],
            ["Debt Density", f"{metrics.get('debt_density', 0.0):.2f}%"],
            ["ML-Specific Items", metrics.get("by_category", {}).get("ml_specific", 0)]
        ]

        lines.append(tabulate(metrics_table, tablefmt="pipe", headers=["Metric", "Value"]))
        lines.append("")

        # Calculate and add debt score
        debt_score = self._calculate_project_debt_score(metrics)
        lines.append(f"**Project Debt Score:** {debt_score:.2f}/10.0 ({self._get_debt_score_assessment(debt_score)})")
        lines.append("")

        # Add prioritized items section
        prioritized_items = self._get_prioritized_items()
        if prioritized_items:
            lines.append("## Prioritized Action Items")
            lines.append("")
            lines.append("| ID | Title | Priority Score | Category | Severity | Status |")
            lines.append("|---|-------|----------------|----------|----------|--------|")

            for item in prioritized_items[:10]:  # Show top 10
                lines.append(f"| {item['id']} | {item['title']} | {item['priority_score']:.2f} | {item['category']} | {item['severity']} | {item['status']} |")

            lines.append("")

        # Add section headers to the basic report
        # (the report already contains the items grouped by category)
        lines.append("## Technical Debt Inventory")
        lines.append("")
        lines.append(basic_report)

        # Add trends section if charts are included
        if include_charts:
            lines.append("## Debt Trends")
            lines.append("")

            # Generate and save charts
            chart_files = self._generate_charts()

            for chart_desc, chart_file in chart_files.items():
                # Convert to relative path for markdown
                rel_path = os.path.relpath(chart_file, self.output_dir)
                lines.append(f"### {chart_desc}")
                lines.append("")
                lines.append(f"![{chart_desc}]({rel_path})")
                lines.append("")

        # Add recommendations section
        lines.append("## Recommendations")
        lines.append("")
        for recommendation in self._generate_recommendations(metrics):
            lines.append(f"- {recommendation}")

        lines.append("")
        lines.append("## Next Debt Reduction Sprint")
        lines.append("")
        sprint_items = self._suggest_sprint_items(metrics)
        lines.append("| ID | Title | Estimated Effort | Category | Severity |")
        lines.append("|---|-------|------------------|----------|----------|")

        for item in sprint_items:
            lines.append(f"| {item['id']} | {item['title']} | {item['estimated_effort'] or 'Medium'} | {item['category']} | {item['severity']} |")

        return "\n".join(lines)

    def _generate_html_dashboard(self,
                               basic_report: str,
                               metrics: Dict[str, Any],
                               include_charts: bool) -> str:
        """Generate an HTML dashboard (simplified version)."""
        # This would be a more elaborate HTML version
        # For now, we'll just convert the markdown to basic HTML
        markdown_dashboard = self._generate_markdown_dashboard(basic_report, metrics, include_charts)

        # Basic conversion to HTML (in a real implementation, use a proper markdown to HTML converter)
        html_lines = [
            "<!DOCTYPE html>",
            "<html>",
            "<head>",
            "    <title>Technical Debt Dashboard</title>",
            "    <style>",
            "        body { font-family: Arial, sans-serif; margin: 40px; }",
            "        table { border-collapse: collapse; width: 100%; }",
            "        th, td { border: 1px solid #ddd; padding: 8px; }",
            "        th { background-color: #f2f2f2; }",
            "        .critical { background-color: #ffdddd; }",
            "        .high { background-color: #ffffcc; }",
            "        .medium { background-color: #e6f3ff; }",
            "        .low { background-color: #f2f2f2; }",
            "        h1, h2, h3 { color: #333366; }",
            "    </style>",
            "</head>",
            "<body>",
        ]

        # Basic conversion of markdown headings and content
        for line in markdown_dashboard.split('\n'):
            if line.startswith("# "):
                html_lines.append(f"<h1>{line[2:]}</h1>")
            elif line.startswith("## "):
                html_lines.append(f"<h2>{line[3:]}</h2>")
            elif line.startswith("### "):
                html_lines.append(f"<h3>{line[4:]}</h3>")
            elif line.startswith("!["):
                # Extract image info
                img_text = line[2:].split("](")[0]
                img_path = line.split("](")[1][:-1]
                html_lines.append(f'<img src="{img_path}" alt="{img_text}" style="max-width:800px;"/>')
            elif line.startswith("| "):
                # This is a table row, already handled in markdown
                html_lines.append(line)
            elif line.startswith("- "):
                html_lines.append(f"<li>{line[2:]}</li>")
            else:
                if line.strip() and not line.startswith("|"):
                    html_lines.append(f"<p>{line}</p>")
                else:
                    html_lines.append(line)

        html_lines.append("</body>")
        html_lines.append("</html>")

        return "\n".join(html_lines)

    def _calculate_project_debt_score(self, metrics: Dict[str, Any]) -> float:
        """
        Calculate overall project technical debt score.

        Based on the research formula:
        Debt Score = (0.4 × Severity Score) + (0.3 × Debt Density) + (0.3 × ML Impact)
        """
        # Calculate severity score (0-10)
        total_items = metrics.get("total_items", 0)
        if total_items == 0:
            return 0.0

        severity_weights = {
            "critical": 10,
            "high": 7,
            "medium": 4,
            "low": 1
        }

        by_severity = metrics.get("by_severity", {})
        severity_score = sum(
            count * severity_weights[severity]
            for severity, count in by_severity.items()
            if severity in severity_weights
        ) / (total_items * 10)  # Normalize to 0-1
        severity_score = min(severity_score * 10, 10)  # Scale to 0-10

        # Debt density score (0-10)
        debt_density = metrics.get("debt_density", 0.0) / 100  # Convert to 0-1
        debt_density_score = min(debt_density * 10, 10)  # Scale to 0-10

        # ML impact score (0-10)
        ml_items = metrics.get("by_category", {}).get("ml_specific", 0)
        ml_impact = ml_items / total_items if total_items > 0 else 0
        ml_impact_score = min(ml_impact * 10, 10)  # Scale to 0-10

        # Calculate final score
        debt_score = (0.4 * severity_score) + (0.3 * debt_density_score) + (0.3 * ml_impact_score)

        return debt_score

    def _get_debt_score_assessment(self, score: float) -> str:
        """Get a qualitative assessment of the debt score."""
        if score < 2:
            return "Excellent"
        elif score < 4:
            return "Good"
        elif score < 6:
            return "Moderate"
        elif score < 8:
            return "Concerning"
        else:
            return "Critical"

    def _get_prioritized_items(self) -> List[Dict[str, Any]]:
        """
        Get prioritized technical debt items.

        Uses the research-backed priority formula:
        Priority = (0.4 × File Criticality) + (0.3 × Commit Frequency) + (0.3 × User Impact)

        Adapted for this implementation:
        Priority = (0.4 × Severity) + (0.3 × Category Impact) + (0.3 × Age)
        """
        # Get all debt items
        all_items = self.debt_manager.list_items()

        # Skip if no items
        if not all_items:
            return []

        # Severity weights
        severity_weights = {
            DebtSeverity.CRITICAL: 1.0,
            DebtSeverity.HIGH: 0.8,
            DebtSeverity.MEDIUM: 0.5,
            DebtSeverity.LOW: 0.2
        }

        # Category impact weights (especially important for ML projects)
        category_weights = {
            DebtCategory.SECURITY: 1.0,
            DebtCategory.ML_SPECIFIC: 0.9,
            DebtCategory.PERFORMANCE: 0.8,
            DebtCategory.ARCHITECTURE: 0.7,
            DebtCategory.TESTS: 0.6,
            DebtCategory.CODE_QUALITY: 0.5,
            DebtCategory.DOCUMENTATION: 0.4,
            DebtCategory.USABILITY: 0.3,
            DebtCategory.DEPLOYMENT: 0.3,
            DebtCategory.DEPENDENCY: 0.3,
            DebtCategory.ACCESSIBILITY: 0.2,
            DebtCategory.MONITORING: 0.2
        }

        # Calculate priority scores
        prioritized = []
        today = datetime.datetime.now()

        for item in all_items:
            # Skip resolved items
            if item.status == DebtStatus.RESOLVED:
                continue

            # Get or default severity weight
            severity = item.severity
            if isinstance(severity, str):
                severity = DebtSeverity(severity)
            severity_weight = severity_weights.get(severity, 0.2)

            # Get or default category weight
            category = item.category
            if isinstance(category, str):
                category = DebtCategory(category)
            category_weight = category_weights.get(category, 0.2)

            # Calculate age weight (older items get higher priority, max 180 days = ~6 months)
            created_date = item.created_at if item.created_at else today
            age_days = (today - created_date).days
            age_weight = min(age_days / 180, 1.0)

            # Apply the priority formula
            priority_score = (0.4 * severity_weight) + (0.3 * category_weight) + (0.3 * age_weight)

            # Format the item for output
            prioritized.append({
                "id": item.id,
                "title": item.title,
                "priority_score": priority_score * 10,  # Scale to 0-10
                "severity": item.severity.value if isinstance(item.severity, DebtSeverity) else item.severity,
                "category": item.category.value if isinstance(item.category, DebtCategory) else item.category,
                "status": item.status.value if isinstance(item.status, DebtStatus) else item.status,
                "created_at": item.created_at,
                "description": item.description,
                "estimated_effort": item.estimated_effort
            })

        # Sort by priority score (descending)
        return sorted(prioritized, key=lambda x: x["priority_score"], reverse=True)

    def _generate_charts(self) -> Dict[str, str]:
        """Generate charts for the dashboard."""
        chart_files = {}

        # Get metrics data
        metrics = self.debt_manager.get_metrics()

        # Create directory for charts
        charts_dir = os.path.join(self.output_dir, "tech_debt_charts")
        os.makedirs(charts_dir, exist_ok=True)

        # 1. Debt by severity chart
        severity_data = metrics.get("by_severity", {})
        if severity_data:
            plt.figure(figsize=(10, 6))
            severity_labels = list(severity_data.keys())
            severity_values = list(severity_data.values())

            plt.bar(severity_labels, severity_values, color=['#d62728', '#ff7f0e', '#ffbb78', '#98df8a'])
            plt.title("Technical Debt by Severity")
            plt.xlabel("Severity")
            plt.ylabel("Number of Items")
            plt.tight_layout()

            chart_path = os.path.join(charts_dir, f"severity_chart_{self.date_str}.png")
            plt.savefig(chart_path)
            plt.close()

            chart_files["Debt by Severity"] = chart_path

        # 2. Debt by category chart
        category_data = metrics.get("by_category", {})
        if category_data:
            plt.figure(figsize=(12, 8))
            category_labels = list(category_data.keys())
            category_values = list(category_data.values())

            plt.barh(category_labels, category_values, color='#2ca02c')
            plt.title("Technical Debt by Category")
            plt.xlabel("Number of Items")
            plt.ylabel("Category")
            plt.tight_layout()

            chart_path = os.path.join(charts_dir, f"category_chart_{self.date_str}.png")
            plt.savefig(chart_path)
            plt.close()

            chart_files["Debt by Category"] = chart_path

        # 3. ML-specific debt breakdown chart
        ml_data = metrics.get("by_ml_subcategory", {})
        if ml_data:
            plt.figure(figsize=(10, 7))
            ml_labels = list(ml_data.keys())
            ml_values = list(ml_data.values())

            plt.pie(ml_values, labels=ml_labels, autopct='%1.1f%%', startangle=90)
            plt.title("ML-Specific Technical Debt Breakdown")
            plt.axis('equal')
            plt.tight_layout()

            chart_path = os.path.join(charts_dir, f"ml_debt_chart_{self.date_str}.png")
            plt.savefig(chart_path)
            plt.close()

            chart_files["ML Debt Breakdown"] = chart_path

        return chart_files

    def _generate_recommendations(self, metrics: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on metrics."""
        recommendations = []

        # Get prioritized items to reference in recommendations
        prioritized_items = self._get_prioritized_items()

        # Add recommendations based on severity distribution
        critical_count = metrics.get("by_severity", {}).get("critical", 0)
        high_count = metrics.get("by_severity", {}).get("high", 0)

        if critical_count > 0:
            recommendations.append(
                f"Address the {critical_count} critical technical debt items as a priority. "
                f"These represent significant risk to the system."
            )

        # Add recommendations based on ML-specific debt
        ml_debt_count = metrics.get("by_category", {}).get("ml_specific", 0)
        if ml_debt_count > 0:
            ml_subcategories = metrics.get("by_ml_subcategory", {})
            highest_subcategory = max(ml_subcategories.items(), key=lambda x: x[1]) if ml_subcategories else (None, 0)

            if highest_subcategory[0]:
                recommendations.append(
                    f"Focus on reducing ML technical debt in the '{highest_subcategory[0]}' area, "
                    f"which has the highest concentration ({highest_subcategory[1]} items)."
                )

        # Add recommendation based on debt density
        debt_density = metrics.get("debt_density", 0.0)
        if debt_density > 15:
            recommendations.append(
                f"Current debt density of {debt_density:.2f}% exceeds the research-recommended 15% threshold. "
                f"Consider allocating more time to debt reduction in the next sprint."
            )

        # Add recommendations based on highest priority items
        if prioritized_items:
            top_item = prioritized_items[0]
            recommendations.append(
                f"Highest priority debt item is '{top_item['title']}' (ID: {top_item['id']}). "
                f"Addressing this would have the most immediate impact."
            )

        # Add general recommendations based on research
        recommendations.append(
            "Based on research, allocate 20% of development time (1 day per week) to systematic debt reduction."
        )

        recommendations.append(
            "Consider a dedicated debt-reduction sprint every quarter to address accumulated technical debt."
        )

        return recommendations

    def _suggest_sprint_items(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Suggest items for the next debt reduction sprint."""
        # Get prioritized items
        prioritized_items = self._get_prioritized_items()

        # Mix of high priority and quick wins
        sprint_items = []

        # Add top 3 priority items
        sprint_items.extend(prioritized_items[:3])

        # Add a couple of quick wins (medium or low severity items)
        quick_wins = [
            item for item in prioritized_items[3:]
            if item["severity"] in ["medium", "low"] and
               item["estimated_effort"] in ["low", "medium", None]
        ]

        sprint_items.extend(quick_wins[:2])

        return sprint_items[:5]  # Return up to 5 items


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Generate technical debt dashboard.")
    parser.add_argument("--output-dir", help="Directory to store the dashboard output")
    parser.add_argument("--format", choices=["markdown", "html"], default="markdown", help="Output format")
    parser.add_argument("--include-resolved", action="store_true", help="Include resolved items")
    args = parser.parse_args()

    dashboard = TechnicalDebtDashboard(output_dir=args.output_dir)
    dashboard.generate_dashboard(
        include_charts=True,
        output_format=args.format,
        include_resolved=args.include_resolved
    )

if __name__ == "__main__":
    main()
