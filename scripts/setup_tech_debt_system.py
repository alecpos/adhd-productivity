#!/usr/bin/env python3
"""
Setup script for the Technical Debt Management System.

This script helps set up the technical debt management system by:
1. Creating necessary directories
2. Installing Git hooks
3. Running an initial scan for technical debt
4. Generating an initial report
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

# Add parent directory to path so we can import from app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from app.utils.tech_debt import get_debt_manager
except ImportError:
    print("Error importing tech_debt module. Make sure it's installed correctly.")
    sys.exit(1)


def create_directories() -> None:
    """Create necessary directories for the tech debt system."""
    # Directory for tech debt reports
    reports_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reports", "tech_debt"
    )
    os.makedirs(reports_dir, exist_ok=True)
    print(f"Created directory: {reports_dir}")

    # Directory for git hooks
    git_hooks_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".git", "hooks"
    )
    os.makedirs(git_hooks_dir, exist_ok=True)
    print(f"Created directory: {git_hooks_dir}")


def install_git_hooks() -> None:
    """Install git hooks for the tech debt system."""
    # Source pre-commit hook
    source_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "scripts",
        "git_hooks",
        "pre-commit",
    )

    # Destination pre-commit hook
    dest_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".git", "hooks", "pre-commit"
    )

    # Make sure the source file exists
    if not os.path.exists(source_path):
        print(f"Error: Source file not found: {source_path}")
        return

    # Create symlink or copy the file
    try:
        # Try to create a symlink first
        if os.path.exists(dest_path):
            os.remove(dest_path)

        try:
            os.symlink(os.path.relpath(source_path, os.path.dirname(dest_path)), dest_path)
            print(f"Created symlink: {dest_path} -> {source_path}")
        except OSError:
            # If symlink creation fails, copy the file instead
            shutil.copy2(source_path, dest_path)
            print(f"Copied file: {source_path} -> {dest_path}")

        # Make the hook executable
        os.chmod(dest_path, 0o755)
        print(f"Made hook executable: {dest_path}")
    except Exception as e:
        print(f"Error installing git hook: {e}")


def scan_for_tech_debt(auto_add: bool = False) -> None:
    """Scan the codebase for technical debt markers."""
    try:
        # Run tech_debt_cli.py scan
        cmd = [
            sys.executable,
            os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "scripts",
                "tech_debt_cli.py",
            ),
            "scan",
            "--auto-add" if auto_add else "",
        ]
        cmd = [c for c in cmd if c]  # Remove empty strings

        print("Scanning for technical debt markers...")
        process = subprocess.run(cmd, capture_output=True, text=True)

        if process.returncode == 0:
            print("Scan completed successfully.")
            print(process.stdout)
        else:
            print(f"Error scanning for technical debt: {process.stderr}")
    except Exception as e:
        print(f"Error scanning for technical debt: {e}")


def generate_initial_report() -> None:
    """Generate an initial tech debt report."""
    try:
        # Path to report
        report_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "reports",
            "tech_debt",
            f"initial_report_{get_timestamp()}.md",
        )

        # Run tech_debt_cli.py report
        cmd = [
            sys.executable,
            os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "scripts",
                "tech_debt_cli.py",
            ),
            "report",
            "--output",
            report_path,
        ]

        print("Generating initial technical debt report...")
        process = subprocess.run(cmd, capture_output=True, text=True)

        if process.returncode == 0:
            print(f"Report generated successfully: {report_path}")
        else:
            print(f"Error generating report: {process.stderr}")
    except Exception as e:
        print(f"Error generating report: {e}")


def get_timestamp() -> str:
    """Get a timestamp string for filenames."""
    from datetime import datetime

    return datetime.now().strftime("%Y%m%d%H%M%S")


def main() -> None:
    """Main entry point for the setup script."""
    parser = argparse.ArgumentParser(
        description="Setup script for the technical debt management system"
    )
    parser.add_argument("--no-git-hooks", action="store_true", help="Skip git hook installation")
    parser.add_argument(
        "--auto-add", action="store_true", help="Automatically add found tech debt items"
    )
    parser.add_argument("--no-scan", action="store_true", help="Skip scanning for tech debt")
    parser.add_argument(
        "--no-report", action="store_true", help="Skip generating an initial report"
    )

    args = parser.parse_args()

    print("Setting up technical debt management system...")

    create_directories()

    if not args.no_git_hooks:
        install_git_hooks()

    if not args.no_scan:
        scan_for_tech_debt(args.auto_add)

    if not args.no_report:
        generate_initial_report()

    print("Setup complete! You can now use the technical debt management system.")
    print("")
    print("Quick start:")
    print(
        '  - Add new tech debt item: python scripts/tech_debt_cli.py add --title "..." --description "..."'
    )
    print("  - List tech debt items: python scripts/tech_debt_cli.py list")
    print("  - Generate a report: python scripts/tech_debt_cli.py report")
    print("  - View metrics: python scripts/tech_debt_cli.py metrics")
    print("")
    print("For more information, see docs/tech_debt_management.md")


if __name__ == "__main__":
    main()
