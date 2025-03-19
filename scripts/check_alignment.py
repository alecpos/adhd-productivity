#!/usr/bin/env python3
"""Script to check naming conventions and file relationships in the codebase."""


# File type patterns
MODEL_PATTERN = r"_model\.py$"
SCHEMA_PATTERN = r"_schema\.py$"
SERVICE_PATTERN = r"_service\.py$"
TEST_PATTERN = r"^test_.*\.py$"

# Files that should exist together
RELATED_PATTERNS = {
    "models": {
        "pattern": MODEL_PATTERN,
        "related": [
            (
                "schema",
                lambda x: x.replace("_model.py", "_schema.py").replace("/models/", "/schemas/"),
            ),
            ("test", lambda x: f"test_{os.path.basename(x)}".replace("/models/", "/tests/models/")),
        ],
    },
    "schemas": {
        "pattern": SCHEMA_PATTERN,
        "related": [
            (
                "model",
                lambda x: x.replace("_schema.py", "_model.py").replace("/schemas/", "/models/"),
            ),
        ],
    },
    "services": {
        "pattern": SERVICE_PATTERN,
        "related": [
            (
                "test",
                lambda x: f"test_{os.path.basename(x)}".replace("/services/", "/tests/services/"),
            ),
        ],
    },
}


def should_ignore_file(filepath: str) -> bool:
    """Check if a file should be ignored in checks."""
    ignore_patterns = [
        "__init__.py",
        "__pycache__",
        ".pyc",
        ".coverage",
        "pytest_cache",
        "schema_manager.py",
        "schema_registry.py",
        "schema_factory.py",
        "schema_utils.py",
        "schema_validation.py",
        "base_model.py",
        "base_schema.py",
    ]
    return any(pattern in filepath for pattern in ignore_patterns)


def find_python_files(directory: str) -> List[str]:
    """Find all Python files in a directory recursively."""
    python_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py") and not should_ignore_file(os.path.join(root, file)):
                python_files.append(os.path.join(root, file))


def check_naming_conventions(files: List[str]) -> List[str]:
    """Check if files follow naming conventions."""
    issues = []

    for file in files:
        basename = os.path.basename(file)
        if "/models/" in file and not re.search(MODEL_PATTERN, basename):
            issues.append(f"Model file without _model suffix: {file}")
        elif "/schemas/" in file and not re.search(SCHEMA_PATTERN, basename):
            issues.append(f"Schema file without _schema suffix: {file}")
        elif "/services/" in file and not re.search(SERVICE_PATTERN, basename):
            issues.append(f"Service file without _service suffix: {file}")
        elif "/tests/" in file and not re.search(TEST_PATTERN, basename):
            issues.append(f"Test file not starting with test_: {file}")


def check_related_files(files: List[str]) -> List[str]:
    """Check if related files exist (e.g., model->schema, service->test)."""
    issues = []

    for file in files:
        for file_type, config in RELATED_PATTERNS.items():
            if f"/{file_type}/" in file and re.search(config["pattern"], os.path.basename(file)):
                for rel_type, transform in config["related"]:
                    related_file = transform(file)
                    if not os.path.exists(related_file):
                        issues.append(f"Missing {rel_type} file for {file}: {related_file}")


def find_duplicate_content(files: List[str]) -> List[Tuple[str, str]]:
    """Find files with identical content that aren't supposed to be identical."""
    duplicates = []
    file_hashes = {}

    for file in files:
        with open(file, "rb") as f:
            content = f.read()
            file_hash = hashlib.sha256(content).hexdigest()

            if file_hash in file_hashes:
                # Don't report test files matching their implementation
                if not (
                    ("/tests/" in file and file_hashes[file_hash] in file)
                    or ("/tests/" in file_hashes[file_hash] and file in file_hashes[file_hash])
                ):
                    duplicates.append((file, file_hashes[file_hash]))
            else:
                file_hashes[file_hash] = file


def main():
    """Run the alignment checks."""
    print("Starting codebase structure checks...")

    # Find all Python files
    python_files = find_python_files("app")

    # Check naming conventions
    print("\nChecking naming conventions...")
    naming_issues = check_naming_conventions(python_files)
    if naming_issues:
        print("\n❌ Found naming convention issues:")
        for issue in naming_issues:
            print(f"  - {issue}")
    else:
        print("✅ All files follow naming conventions")

    # Check related files
    print("\nChecking related files...")
    missing_files = check_related_files(python_files)
    if missing_files:
        print("\n❌ Found missing related files:")
        for issue in missing_files:
            print(f"  - {issue}")
    else:
        print("✅ All related files exist")

    # Check for duplicates
    print("\nChecking for duplicate content...")
    duplicates = find_duplicate_content(python_files)
    if duplicates:
        print("\n❌ Found files with identical content:")
        for file1, file2 in duplicates:
            print(f"  - Duplicate: {file1}")
            print(f"    matches:   {file2}")
    else:
        print("✅ No duplicate content found")

    # Return error code if any issues found
    return 1 if naming_issues or missing_files or duplicates else 0


if __name__ == "__main__":
    exit(main())
