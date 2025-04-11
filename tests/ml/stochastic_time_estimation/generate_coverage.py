#!/usr/bin/env python3
"""
Generates code coverage reports for the Stochastic Time Estimation Engine tests.

This script runs pytest with coverage enabled and generates HTML reports
for easy visualization of test coverage.

Usage:
    python generate_coverage.py [--run-in-docker] [--html] [--xml]
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Generate coverage reports for STE tests")
    parser.add_argument("--run-in-docker", action="store_true", help="Run tests in Docker")
    parser.add_argument("--html", action="store_true", help="Generate HTML report")
    parser.add_argument("--xml", action="store_true", help="Generate XML report")
    return parser.parse_args()


def get_project_root():
    """Get the project root directory."""
    # Assuming this script is in tests/ml/stochastic_time_estimation/
    script_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    return script_dir.parent.parent.parent


def run_coverage_locally(generate_html, generate_xml):
    """Run coverage locally using pytest-cov."""
    project_root = get_project_root()
    os.chdir(project_root)

    # Ensure PYTHONPATH includes project root
    env = os.environ.copy()
    env["PYTHONPATH"] = str(project_root)

    # Base command
    cmd = [
        "python", "-m", "pytest",
        "tests/ml/stochastic_time_estimation/",
        "--cov=app/ml/stochastic_time_estimation",
        "-v"
    ]

    # Add report formats
    if generate_html:
        cmd.append("--cov-report=html")
    if generate_xml:
        cmd.append("--cov-report=xml")

    # Always generate a terminal report
    cmd.append("--cov-report=term")

    # Run the tests with coverage
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, env=env)

    # Print report locations
    if result.returncode == 0:
        print("\nCoverage run successful!")
        if generate_html:
            html_path = project_root / "htmlcov"
            print(f"HTML report generated at: {html_path}")
            print(f"Open with: file://{html_path}/index.html")
        if generate_xml:
            xml_path = project_root / "coverage.xml"
            print(f"XML report generated at: {xml_path}")
    else:
        print("\nCoverage run failed with exit code:", result.returncode)

    return result.returncode


def run_coverage_in_docker(generate_html, generate_xml):
    """Run coverage in Docker container."""
    project_root = get_project_root()
    os.chdir(project_root)

    # Build the Docker image if it doesn't exist
    subprocess.run([
        "docker", "build",
        "-t", "adhd-calendar-ste-tests",
        "-f", "tests/ml/stochastic_time_estimation/Dockerfile.test",
        "."
    ])

    # Base command
    cmd = [
        "docker", "run", "--rm",
        "-v", f"{project_root}/htmlcov:/app/htmlcov",
        "-v", f"{project_root}/coverage.xml:/app/coverage.xml",
        "adhd-calendar-ste-tests",
        "tests/ml/stochastic_time_estimation/",
        "--cov=app/ml/stochastic_time_estimation",
        "-v"
    ]

    # Add report formats
    if generate_html:
        cmd.append("--cov-report=html")
    if generate_xml:
        cmd.append("--cov-report=xml")

    # Always generate a terminal report
    cmd.append("--cov-report=term")

    # Run the tests with coverage
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd)

    # Print report locations
    if result.returncode == 0:
        print("\nCoverage run successful!")
        if generate_html:
            html_path = project_root / "htmlcov"
            print(f"HTML report generated at: {html_path}")
            print(f"Open with: file://{html_path}/index.html")
        if generate_xml:
            xml_path = project_root / "coverage.xml"
            print(f"XML report generated at: {xml_path}")
    else:
        print("\nCoverage run failed with exit code:", result.returncode)

    return result.returncode


def main():
    """Run the coverage generation script."""
    args = parse_arguments()

    # Default to HTML if no format specified
    if not args.html and not args.xml:
        args.html = True

    # Run tests with coverage
    if args.run_in_docker:
        return run_coverage_in_docker(args.html, args.xml)
    else:
        return run_coverage_locally(args.html, args.xml)


if __name__ == "__main__":
    sys.exit(main())
