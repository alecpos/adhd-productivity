#!/usr/bin/env python3
"""Script to reorganize the codebase structure."""

import os
import shutil

# New directory structure definition
NEW_STRUCTURE = {
    'app': {
        'api': {
            'v1': {
                'routes': {},
                'endpoints': {}
            }
        },
        'core': {
            'config': {},
            'database': {},
            'security': {},
            'dependencies': {}
        },
        'models': {
            'domain': {},
            'persistence': {}
        },
        'schemas': {
            'requests': {},
            'responses': {}
        },
        'services': {
            'auth': {},
            'user': {},
            'task': {},
            'analytics': {},
            'gamification': {},
            'scheduling': {},
            'health': {}
        },
        'utils': {
            'helpers': {},
            'constants': {}
        },
        'tests': {
            'unit': {
                'models': {},
                'services': {},
                'schemas': {}
            },
            'integration': {
                'api': {}
            },
            'e2e': {}
        }
    }
}

# Files to move to core
CORE_FILES = {
    'database.py': 'core/database/',
    'config.py': 'core/config/',
    'auth.py': 'core/security/'
}

def create_directory_structure(base_path: str, structure: dict):
    """Create the new directory structure."""
    for dir_name, substructure in structure.items():
        dir_path = os.path.join(base_path, dir_name)
        os.makedirs(dir_path, exist_ok=True)

        # Create __init__.py in each directory
        init_file = os.path.join(dir_path, '__init__.py')
        if not os.path.exists(init_file):
            with open(init_file, 'w') as f:
                f.write('"""Package initialization."""\n')

        if substructure:  # If there are subdirectories
            create_directory_structure(dir_path, substructure)

def move_file_to_dir(src_path: str, dest_dir: str) -> None:
    """Move a file to a directory, creating the directory if it doesn't exist."""
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    dest_path = os.path.join(dest_dir, os.path.basename(src_path))
    if os.path.exists(dest_path):
        print(f"Warning: {dest_path} already exists, skipping...")
        return

    shutil.move(src_path, dest_path)

def move_routes_to_api(src_dir: str, dest_dir: str):
    """Move route files to the new API structure."""
    if not os.path.exists(src_dir):
        return

    for item in os.listdir(src_dir):
        src_path = os.path.join(src_dir, item)
        if os.path.isfile(src_path) and item.endswith('.py'):
            dest_path = os.path.join(dest_dir, item)
            if not os.path.exists(dest_path):
                shutil.copy2(src_path, dest_path)
                print(f"✅ Moved route: {item}")

def move_core_files(base_path: str):
    """Move core files to their new locations."""
    for file_name, dest_dir in CORE_FILES.items():
        src_path = os.path.join(base_path, file_name)
        if os.path.exists(src_path):
            dest_path = os.path.join(base_path, dest_dir, file_name)
            if not os.path.exists(dest_path):
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                shutil.copy2(src_path, dest_path)
                print(f"✅ Moved core file: {file_name}")

def reorganize_services(src_dir: str, dest_base: str):
    """Reorganize service files into their respective categories."""
    if not os.path.exists(src_dir):
        return

    service_categories = {
        'auth': ['auth', 'authentication'],
        'user': ['user', 'profile'],
        'task': ['task', 'todo'],
        'analytics': ['analytics', 'metrics', 'statistics'],
        'gamification': ['gamification', 'achievement'],
        'scheduling': ['schedule', 'calendar', 'time'],
        'health': ['health', 'wellness', 'mental']
    }

    for item in os.listdir(src_dir):
        if not item.endswith('_service.py'):
            continue

        src_path = os.path.join(src_dir, item)
        if not os.path.isfile(src_path):
            continue

        # Determine category
        category = 'misc'
        for cat, keywords in service_categories.items():
            if any(kw in item.lower() for kw in keywords):
                category = cat

        dest_dir = os.path.join(dest_base, category)
        os.makedirs(dest_dir, exist_ok=True)

        dest_path = os.path.join(dest_dir, item)
        if not os.path.exists(dest_path):
            shutil.copy2(src_path, dest_path)
            print(f"✅ Moved service: {item} -> {category}/")

def reorganize_models(src_dir: str, dest_base: str):
    """Split models into domain and persistence."""
    if not os.path.exists(src_dir):
        return

    for item in os.listdir(src_dir):
        if not item.endswith('_model.py'):
            continue

        src_path = os.path.join(src_dir, item)
        if not os.path.isfile(src_path):
            continue

        # For now, move all models to persistence
        # In a real project, you'd want to carefully separate domain models
        dest_dir = os.path.join(dest_base, 'persistence')
        dest_path = os.path.join(dest_dir, item)

        if not os.path.exists(dest_path):
            shutil.copy2(src_path, dest_path)
            print(f"✅ Moved model: {item} -> persistence/")

def reorganize_schemas(src_dir: str, dest_base: str):
    """Split schemas into requests and responses."""
    if not os.path.exists(src_dir):
        return

    for item in os.listdir(src_dir):
        if not item.endswith('_schema.py'):
            continue

        src_path = os.path.join(src_dir, item)
        if not os.path.isfile(src_path):
            continue

        # Analyze file content to determine if it's request or response
        with open(src_path, 'r') as f:
            content = f.read().lower()

        if 'request' in content or 'input' in content:
            dest_dir = 'requests'
        elif 'response' in content or 'output' in content:
            dest_dir = 'responses'
        else:
            dest_dir = 'requests'  # Default to requests

        dest_path = os.path.join(dest_base, dest_dir, item)
        if not os.path.exists(dest_path):
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            shutil.copy2(src_path, dest_path)
            print(f"✅ Moved schema: {item} -> {dest_dir}/")

def reorganize_tests(src_dir: str, dest_base: str):
    """Reorganize test files into unit, integration, and e2e tests."""
    if not os.path.exists(src_dir):
        return

    for item in os.listdir(src_dir):
        src_path = os.path.join(src_dir, item)
        if not os.path.isfile(src_path) or not item.startswith('test_'):
            continue

        # Determine test type
        if 'api' in item.lower() or 'endpoint' in item.lower():
            dest_dir = os.path.join(dest_base, 'integration', 'api')
        elif 'e2e' in item.lower() or 'end_to_end' in item.lower():
            dest_dir = os.path.join(dest_base, 'e2e')
        else:
            # Categorize unit tests
            if 'model' in item.lower():
                dest_dir = os.path.join(dest_base, 'unit', 'models')
            elif 'service' in item.lower():
                dest_dir = os.path.join(dest_base, 'unit', 'services')
            elif 'schema' in item.lower():
                dest_dir = os.path.join(dest_base, 'unit', 'schemas')
            else:
                dest_dir = os.path.join(dest_base, 'unit')

        dest_path = os.path.join(dest_dir, item)
        if not os.path.exists(dest_path):
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            shutil.copy2(src_path, dest_path)
            print(f"✅ Moved test: {item}")

def cleanup_old_directories(base_path: str):
    """Remove unnecessary directories and files."""
    to_remove = [
        'components',
        'navigation',
        'types',
        '(auth)',
        '(unauth)',
        '.DS_Store'
    ]

    for item in to_remove:
        path = os.path.join(base_path, item)
        if os.path.exists(path):
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
            print(f"✅ Removed: {item}")

def main():
    """Reorganize the codebase structure."""
    print("Starting codebase reorganization...")

    # Create new directory structure
    create_directory_structure('.', NEW_STRUCTURE)
    print("✅ Created new directory structure")

    # Move and reorganize files
    move_core_files('app')
    move_routes_to_api('app/routes', 'app/api/v1/routes')
    reorganize_services('app/services', 'app/services')
    reorganize_models('app/models', 'app/models')
    reorganize_schemas('app/schemas', 'app/schemas')
    reorganize_tests('app/tests', 'app/tests')

    # Cleanup
    cleanup_old_directories('app')

    print("\nReorganization complete!")
    print("\nNOTE: This script creates copies of files in their new locations.")
    print("Please review the changes and manually delete old files/directories once satisfied.")
    return 0

if __name__ == "__main__":
    exit(main())
