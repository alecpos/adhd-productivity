#!/bin/bash
# Script to run Stochastic Time Estimation Engine tests in Docker

set -e  # Exit on any error

# Print header
echo "====================================================="
echo "Stochastic Time Estimation Engine - Docker Test Runner"
echo "====================================================="

# Get the project root directory (assuming this script is in tests/ml/stochastic_time_estimation/)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"

# Navigate to project root
cd "${PROJECT_ROOT}"

# Build the Docker image
echo -e "\n📦 Building Docker test image..."
docker build -t adhd-calendar-ste-tests -f tests/ml/stochastic_time_estimation/Dockerfile.test .

# Run the tests
echo -e "\n🧪 Running tests..."
if [ $# -eq 0 ]; then
    # Run all STE tests if no arguments
    docker run --rm adhd-calendar-ste-tests tests/ml/stochastic_time_estimation/ -v
else
    # Run specific tests provided as arguments
    docker run --rm adhd-calendar-ste-tests "$@"
fi

# Check if tests passed
if [ $? -eq 0 ]; then
    echo -e "\n✅ All tests passed!"
else
    echo -e "\n❌ Some tests failed!"
    exit 1
fi 