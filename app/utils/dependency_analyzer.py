"""
Dependency Analyzer Utility.

This module provides tools for analyzing Python module dependencies,
tracking import relationships, and suggesting improvements using 
the technical debt RAG system.
"""

import os
import sys
import subprocess
import importlib
import logging
from typing import Dict, List, Optional, Set, Tuple, Any, Union
from pathlib import Path
import json
import re
import ast
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass
class DependencyContext:
    """Context information for a dependency."""
    module_name: str
    location: Optional[str] = None
    source_code: Optional[str] = None
    functions: List[str] = field(default_factory=list)
    classes: List[str] = field(default_factory=list)
    exports: List[str] = field(default_factory=list)
    description: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "module_name": self.module_name,
            "location": self.location,
            "functions": self.functions,
            "classes": self.classes,
            "exports": self.exports,
            "description": self.description
        }

class DependencyAnalyzer:
    """
    Analyzer for Python module dependencies.
    
    This class provides functionality to analyze Python module dependencies,
    track import relationships, detect unused imports, and suggest improvements.
    It can also integrate with the technical debt RAG system for enhanced
    dependency analysis and suggestions.
    """
    
    def __init__(
        self, 
        project_root: Optional[str] = None,
        rag_config_path: Optional[str] = None
    ):
        """
        Initialize the DependencyAnalyzer.
        
        Args:
            project_root: Root directory of the project to analyze
            rag_config_path: Path to the RAG configuration file
        """
        self.project_root = project_root or os.getcwd()
        self.rag_config_path = rag_config_path or os.path.join(self.project_root, '.debt_rag_config.yaml')
        
        # Dependency tracking structures
        self.dependencies: Dict[str, Set[str]] = {}  # module -> set of imported modules
        self.reverse_dependencies: Dict[str, Set[str]] = {}  # module -> set of modules that import it
        self.module_info: Dict[str, DependencyContext] = {}  # module -> metadata
        
        # Unused import tracking
        self.unused_imports: Dict[str, List[str]] = {}  # module -> list of potentially unused imports
        
        # Initialize RAG system if available
        self.rag_available = self._check_rag_availability()
        
    def _check_rag_availability(self) -> bool:
        """
        Check if the technical debt RAG system is available.
        
        Returns:
            Boolean indicating if RAG is available
        """
        try:
            # Try to import the technical debt RAG module
            from technical_debt.cli_dependency_rag import get_rag_engine
            return True
        except ImportError:
            logger.warning("Technical debt RAG system not available. Some advanced features will be disabled.")
            return False
    
    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """
        Analyze imports and dependencies in a Python file.
        
        Args:
            file_path: Path to the Python file to analyze
            
        Returns:
            Dictionary with dependency analysis results
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                
            module_name = self._get_module_name(file_path)
            
            # Parse the file with AST
            tree = ast.parse(content)
            
            # Extract imports
            imports = self._extract_imports(tree)
            
            # Extract function and class definitions
            functions, classes = self._extract_definitions(tree)
            
            # Create dependency context
            context = DependencyContext(
                module_name=module_name,
                location=file_path,
                functions=functions,
                classes=classes,
                exports=functions + [c for c in classes],
                description=ast.get_docstring(tree)
            )
            
            # Store module info
            self.module_info[module_name] = context
            
            # Update dependency graph
            self.dependencies[module_name] = set(imports)
            
            # Update reverse dependencies
            for imp in imports:
                if imp not in self.reverse_dependencies:
                    self.reverse_dependencies[imp] = set()
                self.reverse_dependencies[imp].add(module_name)
            
            return {
                "module": module_name,
                "imports": imports,
                "functions": functions,
                "classes": classes
            }
            
        except Exception as e:
            logger.error(f"Error analyzing file {file_path}: {str(e)}")
            return {
                "module": self._get_module_name(file_path),
                "error": str(e)
            }
    
    def _get_module_name(self, file_path: str) -> str:
        """
        Convert a file path to a Python module name.
        
        Args:
            file_path: Path to a Python file
            
        Returns:
            Python module name
        """
        rel_path = os.path.relpath(file_path, self.project_root)
        
        # Handle __init__.py files
        if os.path.basename(file_path) == "__init__.py":
            rel_path = os.path.dirname(rel_path)
        else:
            # Remove .py extension
            rel_path = os.path.splitext(rel_path)[0]
            
        # Convert path separators to dots
        module_name = rel_path.replace(os.path.sep, ".")
        
        return module_name
    
    def _extract_imports(self, tree: ast.AST) -> List[str]:
        """
        Extract imports from an AST tree.
        
        Args:
            tree: AST tree of a Python file
            
        Returns:
            List of imported module names
        """
        imports = []
        
        for node in ast.walk(tree):
            # Handle regular imports
            if isinstance(node, ast.Import):
                for name in node.names:
                    imports.append(name.name)
            
            # Handle from imports
            elif isinstance(node, ast.ImportFrom):
                if node.module:  # Skip relative imports with no module
                    imports.append(node.module)
        
        return imports
    
    def _extract_definitions(self, tree: ast.AST) -> Tuple[List[str], List[str]]:
        """
        Extract function and class definitions from an AST tree.
        
        Args:
            tree: AST tree of a Python file
            
        Returns:
            Tuple of (function names, class names)
        """
        functions = []
        classes = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append(node.name)
            elif isinstance(node, ast.ClassDef):
                classes.append(node.name)
        
        return functions, classes
    
    def analyze_directory(self, directory: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze all Python files in a directory.
        
        Args:
            directory: Directory to analyze (defaults to project root)
            
        Returns:
            Dictionary with analysis results
        """
        directory = directory or self.project_root
        results = {"modules": [], "errors": []}
        
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    try:
                        file_result = self.analyze_file(file_path)
                        if "error" in file_result:
                            results["errors"].append(file_result)
                        else:
                            results["modules"].append(file_result)
                    except Exception as e:
                        results["errors"].append({
                            "file": file_path,
                            "error": str(e)
                        })
        
        return results
    
    def find_circular_dependencies(self) -> List[List[str]]:
        """
        Find circular dependencies in the analyzed modules.
        
        Returns:
            List of circular dependency chains
        """
        cycles = []
        visited = set()
        path = []
        
        def dfs(node):
            if node in path:
                # Found a cycle
                cycle_start = path.index(node)
                cycles.append(path[cycle_start:] + [node])
                return
                
            if node in visited:
                return
                
            visited.add(node)
            path.append(node)
            
            # Visit dependencies
            for dep in self.dependencies.get(node, set()):
                dfs(dep)
                
            path.pop()
        
        # Run DFS from each node
        for node in self.dependencies:
            if node not in visited:
                dfs(node)
                
        return cycles
    
    def find_unused_imports(self) -> Dict[str, List[str]]:
        """
        Find potentially unused imports in the analyzed modules.
        
        Note: This is a basic implementation that may produce false positives.
        
        Returns:
            Dictionary of module -> list of unused imports
        """
        # This would require more sophisticated analysis
        # For now, just return an empty result
        return {}
    
    def generate_dependency_graph(self, output_format: str = "json") -> str:
        """
        Generate a dependency graph representation.
        
        Args:
            output_format: Format of the output ('json', 'dot', 'mermaid')
            
        Returns:
            String representation of the dependency graph
        """
        if output_format == "json":
            graph = {}
            for module, deps in self.dependencies.items():
                graph[module] = list(deps)
            return json.dumps(graph, indent=2)
            
        elif output_format == "dot":
            lines = ["digraph G {"]
            for module, deps in self.dependencies.items():
                for dep in deps:
                    lines.append(f'  "{module}" -> "{dep}";')
            lines.append("}")
            return "\n".join(lines)
            
        elif output_format == "mermaid":
            lines = ["graph TD;"]
            for module, deps in self.dependencies.items():
                for dep in deps:
                    lines.append(f'  {module.replace(".", "_")} --> {dep.replace(".", "_")};')
            return "\n".join(lines)
            
        else:
            raise ValueError(f"Unsupported output format: {output_format}")
    
    def get_module_dependencies(self, module_name: str) -> Dict[str, Any]:
        """
        Get detailed dependency information for a module.
        
        Args:
            module_name: Name of the module
            
        Returns:
            Dictionary with dependency information
        """
        if module_name not in self.dependencies:
            return {"error": f"Module {module_name} not found in dependency graph"}
            
        return {
            "module": module_name,
            "imports": list(self.dependencies.get(module_name, set())),
            "imported_by": list(self.reverse_dependencies.get(module_name, set())),
            "info": self.module_info.get(module_name, DependencyContext(module_name=module_name)).to_dict()
        }
    
    def trace_dependencies(self, file_path: str, output_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Trace dependencies for a single file using the CLI dependency RAG.
        
        Args:
            file_path: Path to the file to analyze
            output_path: Path to save the output JSON (optional)
            
        Returns:
            Dictionary with dependency analysis results
        """
        if not self.rag_available:
            return {
                "error": "RAG system not available. Cannot trace dependencies using RAG.",
                "file": file_path,
                "dependencies": []
            }
            
        try:
            # This uses subprocess to run the CLI tool since direct imports might
            # not work well across different environments
            cmd = [
                sys.executable, "-m", "technical_debt.cli_dependency_rag", 
                "trace-deps", file_path
            ]
            
            if output_path:
                cmd.extend(["--output", output_path])
                
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                return {
                    "error": f"Failed to trace dependencies: {result.stderr}",
                    "file": file_path,
                    "dependencies": []
                }
                
            # If output path specified, read from there
            if output_path and os.path.exists(output_path):
                with open(output_path, 'r') as f:
                    return json.load(f)
                    
            # Otherwise try to parse from stdout
            try:
                return json.loads(result.stdout)
            except json.JSONDecodeError:
                # If JSON parsing fails, return raw output
                return {
                    "file": file_path,
                    "raw_output": result.stdout,
                    "dependencies": []
                }
                
        except Exception as e:
            logger.error(f"Error tracing dependencies for {file_path}: {str(e)}")
            return {
                "error": str(e),
                "file": file_path,
                "dependencies": []
            }
    
    def suggest_with_rag(
        self, 
        file_path: str, 
        query: Optional[str] = None, 
        language: str = "python"
    ) -> Dict[str, Any]:
        """
        Generate dependency-aware suggestions using RAG.
        
        Args:
            file_path: Path to the file to analyze
            query: Query to send to the RAG system
            language: Programming language of the file
            
        Returns:
            Dictionary with RAG suggestions
        """
        if not self.rag_available:
            return {
                "error": "RAG system not available. Cannot generate suggestions.",
                "file": file_path
            }
            
        try:
            # Default query if none provided
            if not query:
                query = "Analyze this code and suggest dependency improvements"
                
            # Run RAG CLI command
            cmd = [
                sys.executable, "-m", "technical_debt.cli_dependency_rag", 
                "suggest-with-deps", query,
                "--file-path", file_path,
                "--language", language
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                return {
                    "error": f"Failed to generate suggestions: {result.stderr}",
                    "file": file_path
                }
                
            # Extract suggestion from output
            # The output format is complex with various sections,
            # so this is a simplified parsing
            output = result.stdout
            
            # Simple parsing of the suggestion
            suggestion = ""
            in_suggestion = False
            for line in output.split("\n"):
                if "===== Generated Suggestion =====" in line:
                    in_suggestion = True
                    continue
                elif in_suggestion and line.strip() == "":
                    # Empty line might indicate end of section
                    continue
                elif in_suggestion and line.startswith("====="):
                    # New section indicates end of suggestion
                    in_suggestion = False
                elif in_suggestion:
                    suggestion += line + "\n"
            
            return {
                "file": file_path,
                "query": query,
                "suggestion": suggestion.strip(),
                "raw_output": output
            }
                
        except Exception as e:
            logger.error(f"Error generating suggestions for {file_path}: {str(e)}")
            return {
                "error": str(e),
                "file": file_path
            }
    
    def analyze_weekly_resampling_dependencies(self, file_path: str) -> Dict[str, Any]:
        """
        Specifically analyze dependencies for weekly resampling functionality.
        
        This is a specialized method tailored for the ADHD Calendar's time buffer calculation
        and weekly resampling features.
        
        Args:
            file_path: Path to the file to analyze
            
        Returns:
            Dictionary with dependency analysis for weekly resampling
        """
        # First trace general dependencies
        deps = self.trace_dependencies(file_path)
        
        # Then use RAG to get specific suggestions for weekly resampling
        rag_query = "Add a weekly_resampling method to TimeBufferCalculator that resamples historical task data to weekly frequency with rolling averages"
        suggestions = self.suggest_with_rag(file_path, rag_query)
        
        # Combine the results
        return {
            "file": file_path,
            "dependencies": deps.get("dependencies", []),
            "weekly_resampling_suggestion": suggestions.get("suggestion", ""),
            "error": deps.get("error") or suggestions.get("error")
        }


# Helper function to get an instance of the analyzer
def get_dependency_analyzer(project_root: Optional[str] = None) -> DependencyAnalyzer:
    """
    Get a DependencyAnalyzer instance.
    
    Args:
        project_root: Root directory of the project
        
    Returns:
        DependencyAnalyzer instance
    """
    return DependencyAnalyzer(project_root=project_root) 