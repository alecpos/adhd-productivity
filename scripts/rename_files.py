#!/usr/bin/env python3
"""Script to rename files according to our naming conventions."""


def get_new_name(filepath: str) -> str:
    """Get the new name for a file based on our conventions."""
    dirname = os.path.dirname(filepath)
    basename = os.path.basename(filepath)
    
    # Skip files that should be ignored
    if any(pattern in filepath for pattern in [
        "__init__.py",
        "__pycache__",
        ".pyc",
        "conftest.py",  # Special pytest file
    ]):
        
    # Models
    if "/models/" in filepath and not basename.endswith("_model.py"):
        # Handle special cases
        if basename == "calendar_enums.py":
            return None  # This is fine as is - it's not a model
        if basename.endswith("_models.py"):
            return os.path.join(dirname, basename.replace("_models.py", "_model.py"))
        if basename.endswith(".py"):
            return os.path.join(dirname, basename.replace(".py", "_model.py"))
            
    # Schemas
    if "/schemas/" in filepath and not basename.endswith("_schema.py"):
        if basename.endswith("_schemas.py"):
            return os.path.join(dirname, basename.replace("_schemas.py", "_schema.py"))
        if basename.endswith(".py"):
            return os.path.join(dirname, basename.replace(".py", "_schema.py"))
            
    # Services
    if "/services/" in filepath and not basename.endswith("_service.py"):
        if basename == "generators.py":
            return os.path.join(dirname, "generator_service.py")
        if basename.endswith("_services.py"):
            return os.path.join(dirname, basename.replace("_services.py", "_service.py"))
        if basename.endswith(".py"):
            return os.path.join(dirname, basename.replace(".py", "_service.py"))
            
    # Tests
    if "/tests/" in filepath and not basename.startswith("test_") and basename != "conftest.py":
        return os.path.join(dirname, f"test_{basename}")
        

def main():
    """Rename files according to conventions."""
    print("Starting file renaming process...")
    
    # Find all Python files
    renames = []
    for root, _, files in os.walk("app"):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                new_name = get_new_name(filepath)
                if new_name:
                    renames.append((filepath, new_name))
    
    # Show planned renames
    if not renames:
        print("No files need to be renamed.")
        return 0
        
    print("\nPlanned renames:")
    for old, new in renames:
        print(f"  {old} -> {new}")
        
    # Confirm with user
    response = input("\nProceed with renaming? [y/N] ")
    if response.lower() != 'y':
        print("Aborting.")
        return 1
        
    # Perform renames
    print("\nPerforming renames...")
    for old, new in renames:
        os.makedirs(os.path.dirname(new), exist_ok=True)
        try:
            os.rename(old, new)
            print(f"✅ Renamed: {old} -> {new}")
        except Exception as e:
            print(f"❌ Failed to rename {old}: {str(e)}")
            
    print("\nRenaming complete!")
    return 0

if __name__ == "__main__":
    exit(main()) 