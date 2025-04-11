#!/usr/bin/env python3

import json
import os

# Load the analysis file
with open('adhd_calendar_analysis.json', 'r') as f:
    analysis = json.load(f)

# Files to check
target_files = [
    "/Users/alecposner/documents/adhd_calendar_backend/app/database.py",
    "/Users/alecposner/documents/adhd_calendar_backend/app/main.py",
    "/Users/alecposner/documents/adhd_calendar_backend/app/ui/project_management_integration.py",
    "/Users/alecposner/documents/adhd_calendar_backend/app/ui/integrations/jira_integration.py",
    "/Users/alecposner/documents/adhd_calendar_backend/app/ui/services/sync_service.py"
]

# Find and report nested depth
for file_data in analysis:
    if file_data["file_path"] in target_files:
        print(f"File: {os.path.basename(file_data['file_path'])}")
        print(f"  Nested Depth: {file_data['structure'].get('nested_depth', 'N/A')}")
        print(f"  Cyclomatic Complexity: {file_data['cyclomatic_complexity']}")
        print(f"  Maintainability Index: {file_data['maintainability_index']}")
        print(f"  Technical Debt Scores:")
        for score_name, score_value in file_data['technical_debt_scores'].items():
            print(f"    {score_name}: {score_value}")
        print() 