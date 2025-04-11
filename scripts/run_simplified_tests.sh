#!/bin/bash

# Run simplified tests for AnalyticsService
echo "Running simplified tests for AnalyticsService..."
python -m app.services.body_doubling.simplified_test

echo -e "\nSimplified tests completed!" 