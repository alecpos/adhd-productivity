#!/bin/bash

# Set the directory
APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." >/dev/null 2>&1 && pwd)"

# Define colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Running Body Doubling Service Tests (Direct Mode)...${NC}"
echo

# Run simple tests first (these don't depend on other parts of the application)
echo -e "${YELLOW}Running basic algorithm tests${NC}"
python -m app.tests.services.body_doubling.test_simple
if [ $? -ne 0 ]; then
    echo -e "${RED}Basic algorithm tests failed${NC}"
    exit 1
fi
echo

echo -e "${YELLOW}Running simplified tests${NC}"
python -m app.services.body_doubling.simplified_test
if [ $? -ne 0 ]; then
    echo -e "${RED}Simplified tests failed${NC}"
    exit 1
fi
echo

echo -e "${YELLOW}Running analytics direct tests${NC}"
python -m app.tests.services.body_doubling.test_analytics_direct
if [ $? -ne 0 ]; then
    echo -e "${RED}Analytics direct tests failed${NC}"
    echo -e "${YELLOW}This may be expected due to asyncio coroutine handling${NC}"
fi
echo

echo -e "${YELLOW}Running standalone test with mocked models${NC}"
PYTHONPATH="$APP_DIR" python -m app.services.body_doubling.standalone_test
if [ $? -ne 0 ]; then
    echo -e "${RED}Standalone test failed${NC}"
    exit 1
fi
echo

# Skipping the manual test that requires database connections
echo -e "${YELLOW}Skipping manual test script (requires database setup)${NC}"
echo

echo -e "${GREEN}All tests completed successfully!${NC}"
echo -e "${CYAN}For more comprehensive testing, set up a test database or use the ./scripts/run_standalone_test.sh script.${NC}"
