#!/usr/bin/env python3
"""
Setup script for the Documentation Knowledge Graph System.

This script helps set up the documentation knowledge graph system by:
1. Creating necessary directories
2. Scanning documentation directories
3. Generating initial knowledge graph
4. Creating visualizations and reports
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

# Add parent directory to path so we can import from app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from app.utils.knowledge_graph import get_knowledge_graph
except ImportError:
    print("Error importing knowledge_graph module. Make sure it's installed correctly.")
    sys.exit(1)


def create_directories() -> None:
    """Create necessary directories for the knowledge graph system."""
    # Directory for knowledge graph reports
    reports_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reports", "knowledge_graph"
    )
    os.makedirs(reports_dir, exist_ok=True)
    print(f"Created directory: {reports_dir}")

    # Directory for knowledge graph visualizations
    visualizations_dir = os.path.join(reports_dir, "visualizations")
    os.makedirs(visualizations_dir, exist_ok=True)
    print(f"Created directory: {visualizations_dir}")


def scan_documentation() -> None:
    """Scan documentation directories using the knowledge graph CLI tool."""
    try:
        # List of directories to scan
        directories = ["docs"]

        # Add app directory if it has markdown files
        app_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app")
        if os.path.exists(app_dir) and any(
            f.endswith(".md")
            for f in os.listdir(app_dir)
            if os.path.isfile(os.path.join(app_dir, f))
        ):
            directories.append("app")

        # Scan each directory
        for directory in directories:
            cmd = [
                sys.executable,
                os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs_knowledge_cli.py"),
                "scan",
                directory,
            ]

            print(f"Scanning documentation directory: {directory}")
            process = subprocess.run(cmd, capture_output=True, text=True)

            if process.returncode == 0:
                print(f"Successfully scanned {directory}:")
                print(process.stdout)
            else:
                print(f"Error scanning {directory}: {process.stderr}")

    except Exception as e:
        print(f"Error scanning documentation: {e}")


def generate_visualization() -> None:
    """Generate a visualization of the knowledge graph."""
    try:
        # Path to visualization
        vis_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "reports",
            "knowledge_graph",
            "visualizations",
            "docs_knowledge_graph",
        )

        # Run docs_knowledge_cli.py visualize
        cmd = [
            sys.executable,
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs_knowledge_cli.py"),
            "visualize",
            "--output",
            vis_path,
        ]

        print("Generating knowledge graph visualization...")
        process = subprocess.run(cmd, capture_output=True, text=True)

        if process.returncode == 0:
            print(f"Visualization generated successfully: {vis_path}.png")
        else:
            print(f"Error generating visualization: {process.stderr}")
    except Exception as e:
        print(f"Error generating visualization: {e}")


def generate_report() -> None:
    """Generate a report of the knowledge graph."""
    try:
        # Path to report
        report_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "reports",
            "knowledge_graph",
            "knowledge_graph_report.md",
        )

        # Run docs_knowledge_cli.py report
        cmd = [
            sys.executable,
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs_knowledge_cli.py"),
            "report",
            "--output",
            report_path,
        ]

        print("Generating knowledge graph report...")
        process = subprocess.run(cmd, capture_output=True, text=True)

        if process.returncode == 0:
            print(f"Report generated successfully: {report_path}")
        else:
            print(f"Error generating report: {process.stderr}")
    except Exception as e:
        print(f"Error generating report: {e}")


def print_stats() -> None:
    """Print statistics about the knowledge graph."""
    try:
        # Run docs_knowledge_cli.py stats
        cmd = [
            sys.executable,
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs_knowledge_cli.py"),
            "stats",
        ]

        print("Knowledge graph statistics:")
        process = subprocess.run(cmd, capture_output=True, text=True)

        if process.returncode == 0:
            print(process.stdout)
        else:
            print(f"Error getting statistics: {process.stderr}")
    except Exception as e:
        print(f"Error getting statistics: {e}")


def main() -> None:
    """Main entry point for the setup script."""
    parser = argparse.ArgumentParser(
        description="Setup script for the documentation knowledge graph system"
    )
    parser.add_argument("--no-visualize", action="store_true", help="Skip visualization generation")
    parser.add_argument("--no-report", action="store_true", help="Skip report generation")

    args = parser.parse_args()

    print("Setting up documentation knowledge graph system...")

    create_directories()
    scan_documentation()

    if not args.no_visualize:
        try:
            generate_visualization()
        except Exception as e:
            print(f"Error generating visualization (continuing anyway): {e}")

    if not args.no_report:
        generate_report()

    print_stats()

    print("Setup complete! You can now use the documentation knowledge graph system.")
    print("")
    print("Quick start:")
    print("  - Scan documentation: python scripts/docs_knowledge_cli.py scan <directory>")
    print('  - Search the graph: python scripts/docs_knowledge_cli.py query --search "<query>"')
    print("  - Find related documents: python scripts/docs_knowledge_cli.py related <node_id>")
    print("  - Generate visualization: python scripts/docs_knowledge_cli.py visualize")
    print("  - Generate report: python scripts/docs_knowledge_cli.py report")
    print("")
    print("For more information, run: python scripts/docs_knowledge_cli.py --help")


if __name__ == "__main__":
    main()
