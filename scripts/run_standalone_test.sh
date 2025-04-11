#!/bin/bash

# Define colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print usage information
usage() {
    echo -e "${CYAN}Usage: $0 [options]${NC}"
    echo -e "Options:"
    echo -e "  ${GREEN}-h, --help${NC}      Display this help message"
    echo -e "  ${GREEN}-a, --ai${NC}        Run with AI-powered insight generation (requires transformers)"
    echo -e "  ${GREEN}-s, --standalone${NC} Run standalone test with mock model injection (default)"
    echo -e "  ${GREEN}-p, --pytorch${NC}   Force PyTorch-only mode (for Mac users with TensorFlow issues)"
    echo
    echo -e "${YELLOW}Examples:${NC}"
    echo -e "  $0                    # Run with standard mock insights"
    echo -e "  $0 --ai               # Run with AI-powered insights (if available)"
    echo -e "  $0 --ai --pytorch     # Run with AI-powered insights using PyTorch only (for Mac users)"
    echo -e "  $0 --standalone       # Run standard standalone test with mock model injection"
    exit 0
}

# Default to standard standalone test
TEST_TYPE="standalone"
PYTORCH_ONLY=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        -h|--help)
            usage
            ;;
        -a|--ai)
            TEST_TYPE="ai"
            shift
            ;;
        -s|--standalone)
            TEST_TYPE="standalone"
            shift
            ;;
        -p|--pytorch)
            PYTORCH_ONLY="--pytorch-only"
            shift
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            usage
            ;;
    esac
done

if [ "$TEST_TYPE" == "ai" ]; then
    echo -e "${YELLOW}Running Body Doubling AnalyticsService tests with AI-powered insights...${NC}"
    echo -e "${CYAN}This test will use Hugging Face transformers if available, otherwise will fall back to mock insights.${NC}"
    
    # Add Mac-specific guidance
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo -e "${YELLOW}Mac OS detected. If you encounter TensorFlow/Metal plugin issues:${NC}"
        echo -e "${CYAN}1. Run with --pytorch flag to force PyTorch-only mode: $0 --ai --pytorch${NC}"
        echo -e "${CYAN}2. Or reinstall without TensorFlow: pip uninstall -y tensorflow tensorflow-macos && pip install torch transformers${NC}"
    else
        echo -e "${CYAN}To enable AI-powered insights, ensure you have installed: pip install transformers torch${NC}"
    fi
    echo
    
    # Run the mock test with AI integration, passing the PyTorch flag if set
    if [ -n "$PYTORCH_ONLY" ]; then
        echo -e "${BLUE}Running in PyTorch-only mode (no TensorFlow)${NC}"
        TRANSFORMERS_FRAMEWORK="pt" python -m app.services.body_doubling.mock_test
    else
        python -m app.services.body_doubling.mock_test
    fi
else
    echo -e "${YELLOW}Running standalone test for Body Doubling AnalyticsService...${NC}"
    echo -e "${CYAN}This test uses mocked models to avoid database dependency issues.${NC}"
    echo
    
    # Run the standalone test with mock model injection
    python -m app.services.body_doubling.standalone_test
fi

if [ $? -ne 0 ]; then
    echo -e "\n${RED}Test failed!${NC}"
    exit 1
fi

echo -e "\n${GREEN}Tests completed successfully!${NC}"
echo -e "${CYAN}For AI-powered insight testing, run: $0 --ai${NC}"
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo -e "${CYAN}For Mac users with TensorFlow issues, run: $0 --ai --pytorch${NC}"
fi 