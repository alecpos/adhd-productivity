#!/usr/bin/env python3
"""Script to update import statements to match the new directory structure."""

import ast
import os


class ImportUpdater(ast.NodeTransformer):
    """AST transformer to update import statements."""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.changes_made = False

    def visit_Import(self, node):
        """Visit import statements."""
        new_names = []
        for alias in node.names:
            new_name = self._update_import_path(alias.name)
            if new_name != alias.name:
                self.changes_made = True
                new_names.append(ast.alias(name=new_name, asname=alias.asname))
            else:
                new_names.append(alias)
        return ast.Import(names=new_names)

    def visit_ImportFrom(self, node):
        """Visit from ... import statements."""
        if node.module:
            new_module = self._update_import_path(node.module)
            if new_module != node.module:
                self.changes_made = True
                return ast.ImportFrom(module=new_module, names=node.names, level=node.level)

    def _update_import_path(self, import_path: str) -> str:
        """Update an import path to match the new structure."""
        # Map of old paths to new paths
        path_updates = {
            "app.models.": "app.models.persistence.",
            "app.routes.": "app.api.v1.routes.",
            "app.schemas.": "app.schemas.responses.",  # Default to responses
            "app.core.": "app.core.",  # Keep core imports as is
            "app.services.": "app.services.",  # Service category will be determined
        }

        # Special cases for schema imports
        request_indicators = ["request", "input", "create", "update"]
        response_indicators = ["response", "output", "result"]

        for old, new in path_updates.items():
            if import_path.startswith(old):
                # Handle schemas specially
                if old == "app.schemas.":
                    module = import_path.split(".")[-1]
                    if any(ind in module.lower() for ind in request_indicators):
                        return import_path.replace(old, "app.schemas.requests.")
                    elif any(ind in module.lower() for ind in response_indicators):
                        return import_path.replace(old, "app.schemas.responses.")

                # Handle services based on their category
                elif old == "app.services.":
                    service_categories = {
                        "auth": ["auth", "authentication"],
                        "user": ["user", "profile"],
                        "task": ["task", "todo"],
                        "analytics": ["analytics", "metrics"],
                        "gamification": ["gamification"],
                        "scheduling": ["schedule", "calendar", "time"],
                        "health": ["health", "wellness", "mental"],
                    }

                    service_name = import_path.split(".")[-1]
                    for category, keywords in service_categories.items():
                        if any(kw in service_name.lower() for kw in keywords):
                            return import_path.replace(old, f"app.services.{category}.")

                return import_path.replace(old, new)


def update_file_imports(file_path: str) -> bool:
    """Update imports in a single file."""
    try:
        with open(file_path, "r") as f:
            content = f.read()

        tree = ast.parse(content)
        updater = ImportUpdater(file_path)
        new_tree = updater.visit(tree)

        if updater.changes_made:
            new_content = ast.unparse(new_tree)
            with open(file_path, "w") as f:
                f.write(new_content)
            print(f"✅ Updated imports in: {file_path}")

    except Exception as e:
        print(f"❌ Failed to update {file_path}: {str(e)}")


def main():
    """Update import statements across the codebase."""
    print("Starting import updates...")

    # Find all Python files
    python_files = []
    for root, _, files in os.walk("app"):
        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))

    # Update imports in each file
    updated_count = 0
    for file_path in python_files:
        if update_file_imports(file_path):
            updated_count += 1

    print(f"\nUpdated imports in {updated_count} files.")
    return 0


if __name__ == "__main__":
    exit(main())
