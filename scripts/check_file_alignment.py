"""Script to check file alignment across directories."""

import hashlib
import os
from pathlib import Path
from typing import Dict, List, Tuple


def get_file_hash(filepath: str) -> str:
    """Calculate SHA-256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def find_similar_files(root_dir: str, file_patterns: List[str]) -> Dict[str, List[str]]:
    """Find files with same name across different directories."""
    similar_files = {}
    excluded_dirs = {"exports", "venv"}
    for pattern in file_patterns:
        for root, _, files in os.walk(root_dir):
            # Skip excluded directories
            if any(excluded in root.split(os.sep) for excluded in excluded_dirs):
                continue
            for file in files:
                if file == pattern:
                    filepath = os.path.join(root, file)
                    if file not in similar_files:
                        similar_files[file] = []
                    similar_files[file].append(filepath)
    return similar_files


def check_file_alignment(root_dir: str, file_patterns: List[str]) -> List[Tuple[str, List[str]]]:
    """Check alignment of similar files across directories."""
    misaligned_files = []
    similar_files = find_similar_files(root_dir, file_patterns)

    for filename, filepaths in similar_files.items():
        if len(filepaths) > 1:
            # Calculate hashes for all versions of this file
            file_hashes = {filepath: get_file_hash(filepath) for filepath in filepaths}

            # If not all hashes are the same, we have misalignment
            if len(set(file_hashes.values())) > 1:
                misaligned_files.append((filename, filepaths))

    return misaligned_files


def main():
    """Main function to run alignment checks."""
    # Add patterns for files that should be checked for alignment
    file_patterns = [
        "schemas.py",
        "models.py",
        "enums.py",
        "config.py",
        "constants.py",
    ]

    root_dir = str(Path(__file__).parent.parent)  # Get project root directory
    misaligned_files = check_file_alignment(root_dir, file_patterns)

    if misaligned_files:
        print("\n🚨 Found misaligned files:")
        for filename, filepaths in misaligned_files:
            print(f"\n{filename}:")
            for filepath in filepaths:
                print(f"  - {filepath}")
        exit(1)
    else:
        print("\n✅ All checked files are properly aligned!")
        exit(0)


if __name__ == "__main__":
    main()
