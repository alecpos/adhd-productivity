#!/usr/bin/env python3
"""
Script to fix naming conventions and inheritance patterns in the codebase.
"""


def create_init_files(root_dir: str, missing_dirs: List[str]) -> None:
    """Create missing __init__.py files."""
    for dir_path in missing_dirs:
        full_path = os.path.join(root_dir, dir_path)
        init_file = os.path.join(full_path, "__init__.py")
        if not os.path.exists(init_file):
            os.makedirs(os.path.dirname(init_file), exist_ok=True)
            with open(init_file, "w") as f:
                f.write('"""Package initialization."""\n')
            print(f"Created {init_file}")


def fix_class_definitions(file_path: str, patterns: List[Tuple[str, str, str]]) -> None:
    """Fix class definitions based on patterns."""
    with open(file_path, "r") as f:
        content = f.read()

    modified = False
    for old_pattern, new_suffix, parent_class in patterns:
        # Find class definitions that need to be updated
        class_pattern = r"class\s+(\w+)(?:\([\w\[\],\s]*\))?\s*:"
        matches = re.finditer(class_pattern, content)

        for match in matches:
            class_name = match.group(1)
            if not class_name.endswith(new_suffix):
                new_name = f"{class_name}{new_suffix}"
                if f"class {new_name}" not in content:  # Avoid duplicate renames
                    old_def = f"class {class_name}"
                    new_def = f"class {new_name}({parent_class})"
                    content = content.replace(old_def, new_def)
                    modified = True
                    print(f"Updated {class_name} to {new_name} in {file_path}")

    if modified:
        with open(file_path, "w") as f:
            f.write(content)


def main():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Directories missing __init__.py
    missing_init_dirs = [
        "enums",
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
        "schemas/scheduling",
        "__tests__",
        "ml/saved_models",
        "ml/saved_models/schedule_optimizer",
        "ml/saved_models/schedule_optimizer/best",
        "ml/saved_models/schedule_optimizer/best/variables",
        "ml/saved_models/schedule_optimizer/best/assets",
        "ml/logs",
        "services/misc",
    ]

    # Create missing __init__.py files
    create_init_files(root_dir, missing_init_dirs)

    # Patterns for class fixes: (directory_pattern, new_suffix, parent_class)
    patterns = [
        ("schemas", "Schema", "BaseModel"),
        ("services", "Service", "BaseService"),
        ("models", "Model", "Base"),
        ("routes", "Router", "BaseRouter"),
    ]

    # Walk through the codebase and fix class definitions
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith(".py"):
                file_path = os.path.join(dirpath, filename)
                rel_path = os.path.relpath(file_path, root_dir)

                # Apply relevant patterns based on file location
                for dir_pattern, suffix, parent in patterns:
                    if dir_pattern in rel_path:
                        fix_class_definitions(file_path, [(dir_pattern, suffix, parent)])


if __name__ == "__main__":
    main()
