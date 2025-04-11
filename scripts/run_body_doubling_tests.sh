#!/bin/bash

# Set the directory
APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." >/dev/null 2>&1 && pwd)"
TEST_DIR="$APP_DIR/app/tests/services/body_doubling"

# Define colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Parse command line arguments
RUN_PERFORMANCE=false
RUN_INTEGRATION=false
RUN_ALL=true

for arg in "$@"
do
    case $arg in
        --all)
        RUN_ALL=true
        shift
        ;;
        --unit-only)
        RUN_ALL=false
        shift
        ;;
        --with-performance)
        RUN_PERFORMANCE=true
        shift
        ;;
        --with-integration)
        RUN_INTEGRATION=true
        shift
        ;;
        --help)
        echo -e "${CYAN}Body Doubling Service Test Runner${NC}"
        echo
        echo "Usage: ./scripts/run_body_doubling_tests.sh [options]"
        echo
        echo "Options:"
        echo "  --all               Run all tests (default)"
        echo "  --unit-only         Run only unit tests"
        echo "  --with-performance  Include performance tests"
        echo "  --with-integration  Include integration tests with database"
        echo "  --help              Show this help message"
        exit 0
        ;;
    esac
done

echo -e "${YELLOW}Running Body Doubling Service tests...${NC}"
echo

# Run unit tests
echo -e "${YELLOW}Running session manager tests${NC}"
python -m pytest "$TEST_DIR/test_session_manager.py" -v
if [ $? -ne 0 ]; then
    echo -e "${RED}Session manager tests failed${NC}"
    exit 1
fi
echo

echo -e "${YELLOW}Running matching engine tests${NC}"
python -m pytest "$TEST_DIR/test_matching_engine.py" -v
if [ $? -ne 0 ]; then
    echo -e "${RED}Matching engine tests failed${NC}"
    exit 1
fi
echo

echo -e "${YELLOW}Running main service tests${NC}"
python -m pytest "$TEST_DIR/test_body_doubling_service.py" -v
if [ $? -ne 0 ]; then
    echo -e "${RED}Main service tests failed${NC}"
    exit 1
fi
echo

echo -e "${YELLOW}Running analytics service tests${NC}"
python -m pytest "$TEST_DIR/test_analytics_service.py" -v
if [ $? -ne 0 ]; then
    echo -e "${RED}Analytics service tests failed${NC}"
    exit 1
fi
echo

echo -e "${YELLOW}Running basic algorithm tests${NC}"
python "$TEST_DIR/test_simple.py"
if [ $? -ne 0 ]; then
    echo -e "${RED}Basic algorithm tests failed${NC}"
    exit 1
fi
echo

# Run integration tests
echo -e "${YELLOW}Running integration tests${NC}"
python -m pytest "$TEST_DIR/test_integration.py" -v
if [ $? -ne 0 ]; then
    echo -e "${RED}Integration tests failed${NC}"
    exit 1
fi
echo

# Run advanced integration tests if requested
if [ "$RUN_ALL" = true ] || [ "$RUN_INTEGRATION" = true ]; then
    echo -e "${YELLOW}Running database integration tests${NC}"
    python -m app.services.body_doubling.integration_test
    if [ $? -ne 0 ]; then
        echo -e "${RED}Database integration tests failed${NC}"
        exit 1
    fi
    echo
fi

# Run performance tests if requested
if [ "$RUN_ALL" = true ] || [ "$RUN_PERFORMANCE" = true ]; then
    echo -e "${YELLOW}Running performance tests${NC}"
    python -m app.services.body_doubling.performance_test
    if [ $? -ne 0 ]; then
        echo -e "${RED}Performance tests failed${NC}"
        exit 1
    fi
    echo
fi

# Run code coverage
echo -e "${YELLOW}Running code coverage${NC}"
python -m pytest "$TEST_DIR" --cov=app.services.body_doubling --cov-report=term-missing
echo

echo -e "${GREEN}All tests passed successfully!${NC}"
echo -e "${CYAN}For more testing options, see scripts/README_TESTS.md${NC}"
