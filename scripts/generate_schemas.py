#!/usr/bin/env python3
"""Script to generate schema files from existing models."""

import ast
import os
from typing import Optional


class ModelVisitor(ast.NodeVisitor):
    """AST visitor to extract model information."""

    def __init__(self):
        self.classes = []
        self.imports = set()
        self.current_class = None

    def visit_ClassDef(self, node):
        """Visit a class definition."""
        class_info = {
            "name": node.name,
            "bases": [base.id for base in node.bases if isinstance(base, ast.Name)],
            "fields": [],
            "decorators": [d.id for d in node.decorator_list if isinstance(d, ast.Name)],
        }

        self.current_class = class_info
        self.generic_visit(node)
        self.classes.append(class_info)
        self.current_class = None

    def visit_AnnAssign(self, node):
        """Visit annotated assignments (class fields)."""
        if self.current_class and isinstance(node.target, ast.Name):
            field_info = {
                "name": node.target.id,
                "type": self._get_type_str(node.annotation),
                "default": self._get_default_value(node.value) if node.value else None,
            }
            self.current_class["fields"].append(field_info)

    def _get_type_str(self, node) -> str:
        """Convert AST type annotation to string."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Subscript):
            value = self._get_type_str(node.value)
            slice_value = self._get_type_str(node.slice)
            return f"{value}[{slice_value}]"
        elif isinstance(node, ast.Constant):
            return str(node.value)
        return "Any"

    def _get_default_value(self, node) -> Optional[str]:
        """Convert AST default value to string."""
        if isinstance(node, ast.Constant):
            return repr(node.value)
        elif isinstance(node, ast.List):
            return "[]"
        elif isinstance(node, ast.Dict):
            return "{}"
        return None


def generate_schema_from_model(model_path: str) -> str:
    """Generate schema content from a model file."""
    with open(model_path, "r") as f:
        tree = ast.parse(f.read())

    visitor = ModelVisitor()
    visitor.visit(tree)

    schema_content = [
        "from typing import Optional, List, Dict, Any",
        "from pydantic import BaseModel, Field",
        "from datetime import datetime, date",
        "",
        "# Generated from " + os.path.basename(model_path),
        "",
    ]

    for class_info in visitor.classes:
        # Skip classes that are clearly not models
        if not any(base.endswith("Base") for base in class_info["bases"]):
            continue

        # Convert SQLAlchemy model to Pydantic schema
        schema_name = class_info["name"].replace("Model", "Schema")
        bases = ["BaseModel"]  # Default to Pydantic BaseModel

        schema_content.extend(
            [
                f"class {schema_name}({', '.join(bases)}):",
                '    """',
                f'    Schema for {class_info["name"]}',
                '    """',
                "",
            ]
        )

        # Add fields
        for field in class_info["fields"]:
            field_type = field["type"]
            # Convert SQLAlchemy types to Pydantic types
            field_type = field_type.replace("Column", "")

            if field["default"] is not None:
                schema_content.append(f"    {field['name']}: {field_type} = {field['default']}")
            else:
                schema_content.append(f"    {field['name']}: Optional[{field_type}] = None")

        schema_content.append("")  # Add blank line between classes

    return "\n".join(schema_content)


def main():
    """Generate schema files for models that don't have them."""
    print("Starting schema generation...")

    # Find all model files
    model_files = []
    for root, _, files in os.walk("app/models"):
        for file in files:
            if file.endswith("_model.py"):
                model_files.append(os.path.join(root, file))

    # Generate corresponding schema files
    for model_path in model_files:
        schema_path = model_path.replace("/models/", "/schemas/").replace("_model.py", "_schema.py")

        # Skip if schema already exists
        if os.path.exists(schema_path):
            print(f"✓ Schema exists: {schema_path}")
            continue

        # Create schema directory if needed
        os.makedirs(os.path.dirname(schema_path), exist_ok=True)

        try:
            schema_content = generate_schema_from_model(model_path)
            with open(schema_path, "w") as f:
                f.write(schema_content)
            print(f"✅ Generated: {schema_path}")
        except Exception as e:
            print(f"❌ Failed to generate schema for {model_path}: {str(e)}")

    print("\nSchema generation complete!")
    return 0


if __name__ == "__main__":
    exit(main())
