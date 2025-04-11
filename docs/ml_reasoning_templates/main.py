#!/usr/bin/env python3
"""
Epic 4 ML Reasoning Template CLI

This script provides a command-line interface for generating ML reasoning templates
specifically tailored for Epic 4: Dynamic Schedule Rebalancing.
"""

import os
import sys
import argparse
from typing import Dict, List, Optional

# Add the parent directory to sys.path to import template_selector
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ml_reasoning_templates.template_selector import MLTemplateSelector, MLTaskType


def main():
    parser = argparse.ArgumentParser(
        description="Generate ML reasoning templates for Epic 4 components"
    )

    parser.add_argument("story_id", help="The story ID (e.g., ADHD-17)", type=str)

    parser.add_argument(
        "task_type",
        help=f"ML task type (one of: {', '.join(MLTaskType.get_epic4_domains())})",
        type=str,
        choices=MLTaskType.get_epic4_domains(),
    )

    parser.add_argument("--title", help="Story title", type=str, default="")

    parser.add_argument("--description", help="Task description", type=str, default="")

    parser.add_argument(
        "--complexity",
        help="Task complexity (low, medium, high)",
        type=str,
        choices=["low", "medium", "high"],
        default="medium",
    )

    parser.add_argument(
        "--output",
        help="Output file path (default: ./STORY_ID_reasoning.md)",
        type=str,
        default=None,
    )

    parser.add_argument("--research", help="Include research insights", action="store_true")

    args = parser.parse_args()

    # Initialize template selector
    template_selector = MLTemplateSelector()

    # Prepare context
    context = {
        "story_id": args.story_id,
        "title": args.title,
        "complexity": args.complexity,
        "task_description": args.description,
        "epic": "Epic 4: Dynamic Schedule Rebalancing",
    }

    # Select template
    template = template_selector.select_template(args.task_type, context)

    # Apply research insights if requested
    if args.research:
        template = template_selector.incorporate_research_insights(template, args.task_type)

    # Determine output path
    output_path = args.output or f"{args.story_id.replace('-', '_').lower()}_reasoning.md"

    # Write to file
    with open(output_path, "w") as f:
        f.write(template)

    print(f"Template generated at: {output_path}")
    print(f"Task type: {args.task_type}")
    print(f"Story ID: {args.story_id}")
    if args.research:
        print("Research insights included")


if __name__ == "__main__":
    main()
