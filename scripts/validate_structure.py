#!/usr/bin/env python3
import ast
import os
import re
from typing import List, Dict, Counter
from dataclasses import dataclass
from collections import defaultdict

"""Script to validate codebase structure and conventions."""


class ValidationError:
    """Represents a validation error."""

    def __init__(self, file_path: str, error_type: str, message: str):
        self.file_path = file_path
        self.error_type = error_type
        self.message = message

    def __str__(self):
        return f"{self.error_type}: {self.file_path} - {self.message}"


class CodebaseValidator:
    """Validates codebase structure and conventions."""

    def __init__(self):
        self.errors: List[ValidationError] = []
        self.excluded_dirs = ["deprecated"]

    def _should_skip_path(self, path: str) -> bool:
        """Check if path should be skipped."""
        return any(excluded in path for excluded in self.excluded_dirs)

    def validate_naming_conventions(self, base_path: str = "app"):
        """Validate file and class naming conventions."""
        naming_rules = {
            r"/models/.*\.py$": (r"_model\.py$", "Model files should end with _model.py"),
            r"/schemas/.*\.py$": (r"_schema\.py$", "Schema files should end with _schema.py"),
            r"/services/.*\.py$": (r"_service\.py$", "Service files should end with _service.py"),
            r"/tests/.*\.py$": (r"^test_.*\.py$", "Test files should start with test_"),
            r"/routes/.*\.py$": (r"_routes\.py$", "Route files should end with _routes.py"),
        }

        for root, _, files in os.walk(base_path):
            if self._should_skip_path(root):
                continue

            for file in files:
                if not file.endswith(".py") or file == "__init__.py":
                    continue

                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, base_path)

                for path_pattern, (name_pattern, message) in naming_rules.items():
                    if re.search(path_pattern, file_path) and not re.search(name_pattern, file):
                        self.errors.append(ValidationError(rel_path, "Naming Convention", message))

    def validate_imports(self, base_path: str = "app"):
        """Validate import statements follow the new structure."""
        import_patterns = {
            r"from\s+app\.models\s+import": "Use app.models",
            r"from\s+app\.routes\s+import": "Use app.routes",
            r"from\s+app\.schemas\s+import": "Use app.schemas",
        }

        for root, _, files in os.walk(base_path):
            if self._should_skip_path(root):
                continue

            for file in files:
                if not file.endswith(".py"):
                    continue

                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, base_path)

                with open(file_path, "r") as f:
                    content = f.read()

                for pattern, message in import_patterns.items():
                    if re.search(pattern, content):
                        self.errors.append(ValidationError(rel_path, "Import Structure", message))

    def validate_class_conventions(self, base_path: str = "app"):
        """Validate class naming and inheritance conventions."""
        class_rules = {
            r"/models/.*_model\.py$": (
                r"Model$",
                "Base",
                "Model classes should end with 'Model' and inherit from 'Base'",
            ),
            r"/schemas/.*_schema\.py$": (
                r"Schema$",
                "BaseModel",
                "Schema classes should end with 'Schema' and inherit from 'BaseModel'",
            ),
            r"/services/.*_service\.py$": (
                r"Service$",
                "BaseService",
                "Service classes should end with 'Service' and inherit from 'BaseService'",
            ),
            r"/routes/.*\.py$": (
                r"Router$",
                "BaseRouter",
                "Router classes should end with 'Router' and inherit from 'BaseRouter'",
            ),
        }

        for root, _, files in os.walk(base_path):
            if self._should_skip_path(root):
                continue

            for file in files:
                if not file.endswith(".py"):
                    continue

                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, base_path)

                try:
                    with open(file_path, "r") as f:
                        tree = ast.parse(f.read())

                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            for path_pattern, (
                                name_pattern,
                                base_class,
                                message,
                            ) in class_rules.items():
                                if re.search(path_pattern, file_path):
                                    if not re.search(name_pattern, node.name):
                                        self.errors.append(
                                            ValidationError(
                                                rel_path,
                                                "Class Naming",
                                                f"{message} (class: {node.name})",
                                            )
                                        )
                                    if not any(
                                        base_class in getattr(b, "id", "") for b in node.bases
                                    ):
                                        self.errors.append(
                                            ValidationError(
                                                rel_path,
                                                "Class Inheritance",
                                                f"{message} (class: {node.name})",
                                            )
                                        )
                except Exception as e:
                    self.errors.append(ValidationError(rel_path, "Parsing Error", str(e)))

    def validate_directory_structure(self, base_path: str = "app"):
        """Validate the expected directory structure exists."""
        expected_dirs = [
            "core/config",
            "core/database",
            "core/security",
            "core/dependencies",
            "models",
            "schemas",
            "services",
            "routes",
            "utils/helpers",
            "utils/constants",
            "tests/unit",
            "tests/integration",
            "tests/e2e",
        ]

        for dir_path in expected_dirs:
            full_path = os.path.join(base_path, dir_path)
            if not os.path.exists(full_path):
                self.errors.append(
                    ValidationError(
                        dir_path, "Directory Structure", "Required directory is missing"
                    )
                )

    def validate_init_files(self, base_path: str = "app"):
        """Validate __init__.py files exist in all packages."""
        for root, dirs, _ in os.walk(base_path):
            if root.endswith("__pycache__") or self._should_skip_path(root):
                continue

            init_file = os.path.join(root, "__init__.py")
            if not os.path.exists(init_file):
                rel_path = os.path.relpath(root, base_path)
                self.errors.append(
                    ValidationError(rel_path, "Package Structure", "Missing __init__.py file")
                )

    def run_all_validations(self):
        """Run all validation checks."""
        print("Starting codebase validation...")

        self.validate_directory_structure()
        print("✓ Checked directory structure")

        self.validate_naming_conventions()
        print("✓ Checked naming conventions")

        self.validate_imports()
        print("✓ Checked import statements")

        self.validate_class_conventions()
        print("✓ Checked class conventions")

        self.validate_init_files()
        print("✓ Checked package structure")

        if self.errors:
            print("\n❌ Found validation errors:")
            for error in self.errors:
                print(f"  - {error}")
        else:
            print("\n✅ All validations passed!")

        return len(self.errors) == 0


def main():
    """Run the validation script."""
    validator = CodebaseValidator()
    success = validator.run_all_validations()
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
