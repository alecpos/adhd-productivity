"""Script to analyze service, model, route, and schema structures for consistency."""

import ast
import os
from pathlib import Path
from typing import Dict, List, Set, Tuple


def get_base_structure(file_path: str) -> Dict:
    """Get the structure of a base class from its file."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    tree = ast.parse(content)
    base_classes = {}
    
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            base_classes[node.name] = {
                'methods': set(n.name for n in node.body if isinstance(n, ast.FunctionDef)),
                'class_vars': set(n.targets[0].id for n in node.body if isinstance(n, ast.Assign)),
                'type_params': [
                    param.id for param in node.bases 
                    if isinstance(param, ast.Subscript) 
                    for param in getattr(param.slice, 'elts', [])
                    if isinstance(param, ast.Name)
                ]
            }
    
    return base_classes


def analyze_derived_classes(directory: str, base_structure: Dict) -> List[Tuple[str, str, str]]:
    """Analyze classes in a directory for consistency with base structure."""
    mismatches = []
    
    for root, _, files in os.walk(directory):
        for file in files:
            if not file.endswith('.py') or file.startswith('__'):
                continue
                
            file_path = os.path.join(root, file)
            with open(file_path, 'r') as f:
                content = f.read()
            
            try:
                tree = ast.parse(content)
            except SyntaxError:
                print(f"Syntax error in {file_path}")
                continue
            
            for node in ast.walk(tree):
                if not isinstance(node, ast.ClassDef):
                    continue
                    
                for base in node.bases:
                    base_name = None
                    if isinstance(base, ast.Name):
                        base_name = base.id
                    elif isinstance(base, ast.Subscript):
                        if isinstance(base.value, ast.Name):
                            base_name = base.value.id
                    
                    if base_name in base_structure:
                        # Check methods
                        class_methods = set(n.name for n in node.body if isinstance(n, ast.FunctionDef))
                        missing_methods = base_structure[base_name]['methods'] - class_methods
                        if missing_methods:
                            mismatches.append((
                                file_path,
                                node.name,
                                f"Missing methods from {base_name}: {', '.join(missing_methods)}"
                            ))
                        
                        # Check type parameters
                        if isinstance(base, ast.Subscript):
                            actual_params = []
                            if hasattr(base.slice, 'elts'):
                                actual_params = [
                                    param.id for param in base.slice.elts 
                                    if isinstance(param, ast.Name)
                                ]
                            expected_params = base_structure[base_name]['type_params']
                            if len(actual_params) != len(expected_params):
                                mismatches.append((
                                    file_path,
                                    node.name,
                                    f"Incorrect number of type parameters for {base_name}: "
                                    f"expected {len(expected_params)}, got {len(actual_params)}"
                                ))
    
    return mismatches


def main():
    """Main function to analyze codebase structure."""
    workspace_root = Path(__file__).parent.parent
    
    # Get base structures
    base_structures = {
        'BaseService': get_base_structure(str(workspace_root / 'app' / 'services' / 'base_service.py')),
        'Base': get_base_structure(str(workspace_root / 'app' / 'models' / 'base_model.py')),
        'BaseRouter': get_base_structure(str(workspace_root / 'app' / 'routes' / 'base_routes.py')),
        'BaseSchema': get_base_structure(str(workspace_root / 'app' / 'schemas' / 'base_schema.py')),
    }
    
    # Analyze directories
    directories = {
        'services': str(workspace_root / 'app' / 'services'),
        'models': str(workspace_root / 'app' / 'models'),
        'routes': str(workspace_root / 'app' / 'routes'),
        'schemas': str(workspace_root / 'app' / 'schemas'),
    }
    
    print("\n=== Structure Analysis Results ===\n")
    
    for dir_name, dir_path in directories.items():
        base_name = {
            'services': 'BaseService',
            'models': 'Base',
            'routes': 'BaseRouter',
            'schemas': 'BaseSchema',
        }[dir_name]
        
        print(f"\nAnalyzing {dir_name}...")
        mismatches = analyze_derived_classes(dir_path, base_structures[base_name])
        
        if mismatches:
            print(f"\nFound {len(mismatches)} issues in {dir_name}:")
            for file_path, class_name, issue in mismatches:
                rel_path = os.path.relpath(file_path, workspace_root)
                print(f"\n{rel_path} -> {class_name}:")
                print(f"  {issue}")
        else:
            print(f"No issues found in {dir_name}")


if __name__ == '__main__':
    main() 