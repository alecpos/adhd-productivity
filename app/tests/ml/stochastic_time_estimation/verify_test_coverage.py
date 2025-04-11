#!/usr/bin/env python
"""
Test Coverage Verification for Stochastic Time Estimation Engine

This script analyzes test files to verify they cover important aspects of each component.
It provides a detailed report of test coverage without requiring actual execution.
"""

import os
import sys
import re
from collections import defaultdict

# Directory containing the test files
TEST_DIR = os.path.dirname(os.path.abspath(__file__))

# Test coverage expectations for each component
COVERAGE_EXPECTATIONS = {
    "bayesian_duration_predictor": {
        "required_methods": [
            "test_init",
            "test_fit",
            "test_predict",
            "test_evaluate",
            "test_update_with_observation",
            "test_extract_features",
            "test_save_and_load"
        ],
        "test_count_minimum": 10
    },
    "nlp_complexity_analyzer": {
        "required_methods": [
            "test_init",
            "test_analyze_task",
            "test_analyze_tasks_batch",
            "test_get_time_factor",
            "test_extract_complexity_features",
            "test_calculate_complexity_score",
            "test_save_and_load"
        ],
        "test_count_minimum": 10
    },
    "contextual_stressor_detector": {
        "required_methods": [
            "test_init",
            "test_detect_current_stress",
            "test_get_task_stress_adjustment",
            "test_analyze_physiological_stress",
            "test_calculate_overall_stress",
            "test_calculate_stress_time_impact",
            "test_save_and_load"
        ],
        "test_count_minimum": 10
    },
    "time_buffer_calculator": {
        "required_methods": [
            "test_init",
            "test_calculate_buffer",
            "test_update_with_observation",
            "test_calculate_buffers_for_task_sequence",
            "test_analyze_transition_difficulty",
            "test_analyze_context_changes",
            "test_save_and_load"
        ],
        "test_count_minimum": 10
    }
}

def extract_test_methods(test_file):
    """
    Extract all test methods from a test file.
    Returns a list of method names.
    """
    with open(test_file, 'r') as f:
        content = f.read()

    # Find all test methods using regex
    # Pattern matches "def test_something" with optional whitespace and supports async def
    method_pattern = re.compile(r"(?:async\s+)?def\s+(test_\w+)\s*\(")
    matches = method_pattern.findall(content)

    return matches

def verify_test_coverage(component):
    """
    Verify that a test file covers all expected aspects of a component.
    Returns a tuple (success, report).
    """
    test_file = os.path.join(TEST_DIR, f"test_{component}.py")

    if not os.path.exists(test_file):
        return False, f"❌ Test file {test_file} does not exist."

    try:
        # Extract all test methods
        test_methods = extract_test_methods(test_file)

        # Get expectations for this component
        expectations = COVERAGE_EXPECTATIONS.get(component, {})
        required_methods = expectations.get("required_methods", [])
        test_count_minimum = expectations.get("test_count_minimum", 5)

        # Verify test count
        test_count = len(test_methods)
        test_count_ok = test_count >= test_count_minimum

        # Verify required methods
        missing_methods = []
        for required in required_methods:
            # Check if any test method starts with the required prefix
            if not any(method.startswith(required) for method in test_methods):
                missing_methods.append(required)

        # Create the report
        report_lines = []
        report_lines.append(f"Test File: {os.path.basename(test_file)}")
        report_lines.append(f"Total Test Methods: {test_count} {'✅' if test_count_ok else '❌'} (minimum expected: {test_count_minimum})")

        if missing_methods:
            report_lines.append(f"Missing Required Test Methods: {'❌'}")
            for missing in missing_methods:
                report_lines.append(f"  - {missing}")
        else:
            report_lines.append(f"Required Test Methods: ✅ All present")

        # List all test methods found
        report_lines.append("\nTest Methods Found:")
        for method in sorted(test_methods):
            required = "✅" if any(method.startswith(req) for req in required_methods) else "  "
            report_lines.append(f"  {required} {method}")

        success = test_count_ok and not missing_methods
        return success, "\n".join(report_lines)

    except Exception as e:
        return False, f"❌ Error analyzing test file {test_file}: {e}"

def main():
    """Main function to verify test coverage for all components."""
    print("\n📊 Analyzing Test Coverage for Stochastic Time Estimation Engine...\n")

    overall_success = True
    results = {}

    for component in COVERAGE_EXPECTATIONS.keys():
        success, report = verify_test_coverage(component)
        results[component] = {"success": success, "report": report}
        overall_success = overall_success and success

        # Print component header
        print(f"\n{'═' * 80}")
        print(f"Component: {component}")
        print(f"{'═' * 80}")
        print(report)
        print(f"\nVerdict: {'✅ PASS' if success else '❌ FAIL'}")

    # Print summary
    print(f"\n{'═' * 80}")
    print("Summary")
    print(f"{'═' * 80}")

    for component, result in results.items():
        status = "✅ PASS" if result["success"] else "❌ FAIL"
        print(f"{component}: {status}")

    if overall_success:
        print("\n✅ All components have adequate test coverage!")
    else:
        print("\n❌ Some components need improved test coverage. See details above.")

    return 0 if overall_success else 1

if __name__ == "__main__":
    sys.exit(main())
