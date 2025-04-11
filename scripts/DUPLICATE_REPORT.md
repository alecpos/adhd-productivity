# Duplicate Components Report


## Duplicate File Names


## Duplicate Classes


### FunctionInfo
- ./static_analysis.py
- ./function_extractor.py

## Similar Standalone Functions


### Signature: def (node: str)
- find_cycles in ./static_analysis.py
- find_cycles in ./static_analysis.py

### Signature: def (file_path: str)
- extract_functions in ./function_extractor.py
- extract_js_functions in ./function_extractor.py

## Similar Class Methods


### Signature: def (self)
- parse_files in CodeIndexer (./static_analysis.py)
- generate_duplicate_report in CodeIndexer (./static_analysis.py)
- generate_quality_report in CodeIndexer (./static_analysis.py)
- generate_static_analysis_report in CodeIndexer (./static_analysis.py)
- analyze_codebase in CodeIndexer (./static_analysis.py)
- generate_index in CodeIndexer (./static_analysis.py)
- analyze_architecture in CodeIndexer (./static_analysis.py)
- _calculate_cohesion_score in CodeIndexer (./static_analysis.py)
- _calculate_abstraction_score in CodeIndexer (./static_analysis.py)
- detect_package_cycles in CodeIndexer (./static_analysis.py)
- prioritize_issues in CodeIndexer (./static_analysis.py)
- __init__ in RefactoringGenerator (./static_analysis.py)
- __init__ in TestGenerator (./static_analysis.py)
- __init__ in DocumentationGenerator (./static_analysis.py)

### Signature: def (self, node: ast.AST)
- calculate_cyclomatic_complexity in CodeIndexer (./static_analysis.py)
- calculate_cognitive_complexity in CodeIndexer (./static_analysis.py)
- _get_field_accesses in CodeIndexer (./static_analysis.py)

### Signature: def (self, tree: ast.AST, file_path: str)
- analyze_imports in CodeIndexer (./static_analysis.py)
- detect_code_smells in CodeIndexer (./static_analysis.py)

### Signature: def (self, tree: ast.AST)
- analyze_type_hints in CodeIndexer (./static_analysis.py)
- analyze_dependencies in CodeIndexer (./static_analysis.py)

### Signature: def (self, dependency_graph: Dict[str, List[str]])
- _calculate_coupling_score in CodeIndexer (./static_analysis.py)
- _analyze_dependencies in DocumentationGenerator (./static_analysis.py)

### Signature: def (self, graph: Dict[str, List[str]])
- _find_circular_dependencies in CodeIndexer (./static_analysis.py)
- _find_dependency_cycles in DocumentationGenerator (./static_analysis.py)

### Signature: def (self, smell: CodeSmell)
- generate_refactoring in RefactoringGenerator (./static_analysis.py)
- generate_tests in TestGenerator (./static_analysis.py)

### Signature: def (self, smells: List[CodeSmell])
- _generate_impact_analysis in DocumentationGenerator (./static_analysis.py)
- _generate_priority_list in DocumentationGenerator (./static_analysis.py)
- _prioritize_refactorings in DocumentationGenerator (./static_analysis.py)

### Signature: def (self, violations: List[Dict[str, Any]])
- _format_violations in DocumentationGenerator (./static_analysis.py)
- _analyze_patterns in DocumentationGenerator (./static_analysis.py)

### Signature: def (self, results: Dict[str, Any])
- _generate_recommendations in DocumentationGenerator (./static_analysis.py)
- _generate_immediate_actions in DocumentationGenerator (./static_analysis.py)
- _generate_short_term_improvements in DocumentationGenerator (./static_analysis.py)
- _generate_long_term_goals in DocumentationGenerator (./static_analysis.py)
- _generate_best_practices in DocumentationGenerator (./static_analysis.py)
