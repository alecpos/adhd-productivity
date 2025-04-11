# Scripts Directory

This directory contains utility scripts for the ADHD Calendar project.

## Overview

The scripts directory houses various utility scripts that help with development, testing, deployment, and maintenance of the ADHD Calendar application. These scripts automate common tasks and provide tools for developers and administrators.

## Available Scripts

### Development Scripts

- **generate_code_structure.py** - Generates code structure documentation for the project
- **fix_indentation.py** - Fixes indentation issues in Python code
- **fix_model_imports.py** - Fixes import issues in model files
- **list_model_classes.py** - Lists all model classes in the project

### Database Scripts

- **initialize_db.py** - Initializes the database schema
- **start_server.py** - Starts the application server

### Testing Scripts

- **run_asyncio_tests.py** - Runs tests with asyncio support
- **run_failing_tests.py** - Reruns failing tests
- **run_patched_tests.py** - Runs tests with patched modules
- **run_proper_tests.py** - Runs the full test suite with proper configuration
- **run_specific_tests.py** - Runs specific test cases
- **fix_async_tests.py** - Fixes issues with async tests
- **fix_async_event_loop.py** - Fixes event loop issues in tests
- **direct_test.py** - Direct testing utility
- **run_tpr_tests.py** - Runs tests for TPR models

### Documentation Scripts

- **pytest_doc_generator.py** - Generates documentation for pytest tests
- **test_docstring_generator.py** - Generates docstrings for tests
- **local_test_docstring_generator.py** - Generates local docstrings for tests
- **analyze_report.py** - Analyzes test reports

### Integration Scripts

- **jiraCreate.py** - Creates JIRA tickets from project data
- **createJira.py** - Alternative script for JIRA ticket creation

## Usage Examples

### Initialize Database

```bash
python scripts/initialize_db.py
```

### Start Server

```bash
python scripts/start_server.py
```

### Generate Code Structure Documentation

```bash
python scripts/generate_code_structure.py > app_directory_tree.txt
```

### Run Specific Tests

```bash
python scripts/run_specific_tests.py --test-path tests/ml/test_tpr.py
```

### Fix Model Imports

```bash
python scripts/fix_model_imports.py
```

## Creating New Scripts

When creating new scripts:

1. Place the script in the appropriate subdirectory (if applicable)
2. Include a docstring at the top explaining the script's purpose
3. Add command-line argument parsing where appropriate
4. Include error handling for robustness
5. Add the script to this README with a brief description

## Best Practices

- Scripts should be standalone and not rely on other scripts
- Include proper error handling and exit codes
- Provide meaningful output and logging
- Support both interactive and non-interactive usage
- Add help text for command-line arguments
