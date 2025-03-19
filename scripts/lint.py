#!/usr/bin/env python3
"""Script to run all linting and formatting tools."""

import subprocess
import sys
from pathlib import Path
from typing import List, Tuple


def run_command(command: List[str]) -> Tuple[int, str, str]:
    """Run a command and return exit code, stdout, and stderr."""
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = process.communicate()
    return process.returncode, stdout, stderr


def main():
    """Run all linting and formatting tools."""
    root_dir = Path(__file__).parent.parent

    commands = [
        (["black", "."], "Running Black formatter..."),
        (["isort", "."], "Running isort..."),
        (["ruff", "check", ".", "--fix"], "Running Ruff linter..."),
        (["python", "scripts/check_file_alignment.py"], "Checking file alignment..."),
    ]

    exit_code = 0
    for command, message in commands:
        print(f"\n{message}")
        code, stdout, stderr = run_command(command)

        if stdout:
            print(stdout)
        if stderr:
            print(stderr, file=sys.stderr)

        if code != 0:
            exit_code = code
            print(f"❌ {' '.join(command)} failed with exit code {code}")
        else:
            print(f"✅ {' '.join(command)} completed successfully")

    if exit_code != 0:
        print("\n🚨 Some checks failed. Please fix the issues above.")
    else:
        print("\n✅ All checks passed!")

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
