#!/usr/bin/env python3
"""Script to run all tests for Epic 4: Dynamic Schedule Rebalancing.

This script will run all the tests for the components of Epic 4, including:
- DQNScheduler model from ADHD-17
- CircadianDQNModel from ADHD-18
- ModelFactory methods
- TemporalPatternRecognitionService optimization methods
- API endpoints
"""

import os
import sys
import pytest


def main():
    """Run all Epic 4 tests."""
    print("Running tests for Epic 4: Dynamic Schedule Rebalancing")

    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Add parent directories to path if needed
    parent_dir = os.path.abspath(os.path.join(script_dir, "..", "..", ".."))
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)

    # Ensure the conftest.py file is accessible
    conftest_path = os.path.join(script_dir, "conftest.py")
    if not os.path.exists(conftest_path):
        print(f"⚠️  Warning: conftest.py not found at {conftest_path}")
    else:
        print(f"✓ Found conftest.py at {conftest_path}")

    # Run all tests in the dynamic_schedule_rebalancing directory
    test_args = [
        script_dir,
        "-v",  # Verbose output
        "--tb=short",  # Shorter traceback format
        "--color=yes",  # Colored output
        "--cov=app.ml.models.adhd17_reinforcement_model",  # Coverage for ADHD models
        "--cov=app.routes.scheduling_routes",  # Coverage for scheduling routes
    ]

    # Run the tests
    print("\n🧪 Running tests...")
    result = pytest.main(test_args)

    # Print summary
    if result == 0:
        print("\n✅ All Epic 4 tests passed!")
    else:
        print(f"\n❌ Epic 4 tests failed with exit code: {result}")

        # Show troubleshooting help
        print("\nTroubleshooting:")
        print("  - Check for missing dependencies (pip install pytest pytest-asyncio)")
        print("  - Ensure test fixtures are properly defined in conftest.py")
        print("  - Make sure the CircadianDQNModel implementation is accessible")

    return result


if __name__ == "__main__":
    sys.exit(main())
