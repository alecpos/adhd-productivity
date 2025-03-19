#!/usr/bin/env python3
"""
Script to fix various codebase issues including:
1. File naming conventions
2. Class inheritance
3. Missing __init__.py files
4. Import statements
"""


def is_project_file(file_path: Path) -> bool:
    """Check if the file is part of our project (not in venv)."""
    return "venv" not in str(file_path) and "site-packages" not in str(file_path)


class ImportTransformer(cst.CSTTransformer):
    def __init__(self):
        self.import_changes = {}

    def leave_Import(self, original_node: cst.Import, updated_node: cst.Import) -> cst.Import:
        for name in original_node.names:
            if "routes" in str(name.name):
                self.import_changes[str(name.name)] = "app.api.v1.routes"
            elif "schemas" in str(name.name):
                if "requests" not in str(name.name) and "responses" not in str(name.name):
                    self.import_changes[str(name.name)] = "app.schemas.requests"


def fix_file_naming():
    """Fix file naming conventions."""
    # Route files
    route_files = Path("app/api/v1/routes").glob("*.py")
    for file in route_files:
        if (
            not file.name.endswith("_routes.py")
            and file.name != "__init__.py"
            and is_project_file(file)
        ):
            new_name = f"{file.stem}_routes.py"
            file.rename(file.parent / new_name)

    # Model files
    model_files = Path("app/models").rglob("*.py")
    for file in model_files:
        if (
            not file.name.endswith("_model.py")
            and file.name != "__init__.py"
            and is_project_file(file)
        ):
            new_name = f"{file.stem}_model.py"
            file.rename(file.parent / new_name)

    # Test files
    test_files = Path("tests").rglob("*.py")
    for file in test_files:
        if (
            not file.name.startswith("test_")
            and file.name != "__init__.py"
            and file.name != "conftest.py"
            and is_project_file(file)
        ):
            new_name = f"test_{file.name}"
            file.rename(file.parent / new_name)


def fix_class_inheritance():
    """Fix class inheritance issues."""
    python_files = [f for f in Path("app").rglob("*.py") if is_project_file(f)]

    for file in python_files:
        try:
            with open(file, "r") as f:
                content = f.read()

            tree = ast.parse(content)
            classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]

            modified = False
            for cls in classes:
                # Service classes
                if cls.name.endswith("Service") and not any(
                    base.id == "BaseService" for base in cls.bases if isinstance(base, ast.Name)
                ):
                    if not any(
                        "from app.services.base_service import BaseService" in line
                        for line in content.split("\n")
                    ):
                        content = "from app.services.base_service import BaseService\n" + content
                    cls.bases.append(ast.Name(id="BaseService", ctx=ast.Load()))
                    modified = True

                # Router classes
                elif cls.name.endswith("Router") and not any(
                    base.id == "BaseRouter" for base in cls.bases if isinstance(base, ast.Name)
                ):
                    if not any(
                        "from app.api.v1.routes.base_router import BaseRouter" in line
                        for line in content.split("\n")
                    ):
                        content = "from app.api.v1.routes.base_router import BaseRouter\n" + content
                    cls.bases.append(ast.Name(id="BaseRouter", ctx=ast.Load()))
                    modified = True

                # Model classes
                elif cls.name.endswith("Model") and not any(
                    base.id == "Base" for base in cls.bases if isinstance(base, ast.Name)
                ):
                    if not any(
                        "from app.database import Base" in line for line in content.split("\n")
                    ):
                        content = "from app.database import Base\n" + content
                    cls.bases.append(ast.Name(id="Base", ctx=ast.Load()))
                    modified = True

            if modified:
                with open(file, "w") as f:
                    f.write(content)

        except SyntaxError:
            print(f"Syntax error in {file}")


def create_init_files():
    """Create missing __init__.py files."""
    missing_init_dirs = [
        "app/enums",
        "tests/utils",
        "tests/models",
        "tests/models/body_doubling",
        "tests/models/gamification",
        "tests/models/hyperfocus",
        "tests/models/pomodoro",
        "tests/schemas",
        "tests/nlp",
        "tests/htmlcov",
        "tests/routes",
        "tests/services/body_doubling",
        "tests/services/hyperfocus",
        "tests/services/pomodoro",
        "app/schemas/scheduling",
        "__tests__",
        "ml/saved_models",
        "ml/saved_models/schedule_optimizer",
        "ml/saved_models/schedule_optimizer/best",
        "ml/saved_models/schedule_optimizer/best/variables",
        "ml/saved_models/schedule_optimizer/best/assets",
        "ml/logs",
        "app/services/misc",
    ]

    for dir_path in missing_init_dirs:
        init_file = Path(dir_path) / "__init__.py"
        if not init_file.exists():
            init_file.parent.mkdir(parents=True, exist_ok=True)
            init_file.touch()


def fix_imports():
    """Fix import statements."""
    python_files = [f for f in Path("app").rglob("*.py") if is_project_file(f)]

    for file in python_files:
        try:
            with open(file, "r") as f:
                content = f.read()

            tree = cst.parse_module(content)
            transformer = ImportTransformer()
            modified_tree = tree.visit(transformer)

            if transformer.import_changes:
                with open(file, "w") as f:
                    f.write(modified_tree.code)

        except Exception as e:
            print(f"Error processing {file}: {str(e)}")


def main():
    """Main function to run all fixes."""
    print("Starting codebase fixes...")

    print("Fixing file naming conventions...")
    fix_file_naming()

    print("Fixing class inheritance...")
    fix_class_inheritance()

    print("Creating missing __init__.py files...")
    create_init_files()

    print("Fixing import statements...")
    fix_imports()

    print("Codebase fixes completed.")


if __name__ == "__main__":
    main()
