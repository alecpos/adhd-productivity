#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "Running tests before removing deprecated files..."
pytest tests/test_consolidation.py

if [ $? -eq 0 ]; then
    echo -e "${GREEN}Tests passed. Proceeding with removal of deprecated files...${NC}"
    
    # List of deprecated files to remove
    DEPRECATED_FILES=(
        "app/auth.py"
        "app/core/config.py"
        "app/core/service_factory.py"
        "app/error_handling.py"
    )
    
    # Remove each deprecated file
    for file in "${DEPRECATED_FILES[@]}"; do
        if [ -f "$file" ]; then
            echo "Removing $file..."
            rm "$file"
            echo -e "${GREEN}✓ Removed $file${NC}"
        else
            echo -e "${RED}× File $file not found${NC}"
        fi
    done
    
    # Try to remove empty core directory if it exists
    if [ -d "app/core" ] && [ -z "$(ls -A app/core)" ]; then
        echo "Removing empty app/core directory..."
        rmdir "app/core"
        echo -e "${GREEN}✓ Removed empty app/core directory${NC}"
    fi
    
    echo -e "${GREEN}Cleanup complete!${NC}"
else
    echo -e "${RED}Tests failed. Aborting file removal.${NC}"
    exit 1
fi 