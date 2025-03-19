"""Script to analyze classes in the codebase."""

import os
import ast
from collections import defaultdict
from typing import Dict, List, Set, Tuple

def get_class_names(file_path: str) -> List[Tuple[str, int]]:
    """Get class names and their line numbers from a Python file."""
    with open(file_path, 'r') as file:
        try:
            tree = ast.parse(file.read())
            return [(node.name, node.lineno) for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        except:
            print(f"Error parsing {file_path}")
            return []

def analyze_directory(base_path: str) -> Dict[str, Dict[str, List[Tuple[str, int]]]]:
    """Analyze Python files in specified directories for class definitions."""
    directories = ['app/routes', 'app/models', 'app/schemas', 'app/services']
    results = {}
    
    for directory in directories:
        dir_path = os.path.join(base_path, directory)
        if not os.path.exists(dir_path):
            continue
            
        dir_results = {}
        for root, _, files in os.walk(dir_path):
            for file in files:
                if file.endswith('.py') and not file.startswith('__'):
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, base_path)
                    classes = get_class_names(file_path)
                    if classes:
                        dir_results[relative_path] = classes
        
        if dir_results:
            results[directory] = dir_results
            
    return results

def find_duplicates(results: Dict[str, Dict[str, List[Tuple[str, int]]]]) -> Dict[str, List[Tuple[str, str, int]]]:
    """Find duplicate class names within each directory."""
    duplicates = {}
    
    for directory, files in results.items():
        class_locations = defaultdict(list)
        
        for file_path, classes in files.items():
            for class_name, line_no in classes:
                class_locations[class_name].append((file_path, line_no))
        
        dir_duplicates = {
            class_name: locations 
            for class_name, locations in class_locations.items() 
            if len(locations) > 1
        }
        
        if dir_duplicates:
            duplicates[directory] = dir_duplicates
            
    return duplicates

def main():
    """Main function."""
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    results = analyze_directory(base_path)
    duplicates = find_duplicates(results)
    
    # Print results
    print("\n=== Classes by Directory and File ===\n")
    for directory, files in results.items():
        print(f"\n{directory}:")
        print("-" * len(directory))
        
        for file_path, classes in files.items():
            print(f"\n{file_path}:")
            for class_name, line_no in classes:
                print(f"  - {class_name} (line {line_no})")
    
    # Print duplicates
    if duplicates:
        print("\n\n=== Duplicate Classes ===\n")
        for directory, dir_duplicates in duplicates.items():
            print(f"\n{directory}:")
            print("-" * len(directory))
            
            for class_name, locations in dir_duplicates.items():
                print(f"\nClass '{class_name}' found in:")
                for file_path, line_no in locations:
                    print(f"  - {file_path} (line {line_no})")

if __name__ == "__main__":
    main() 