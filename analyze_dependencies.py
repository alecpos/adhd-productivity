#!/usr/bin/env python
"""
Dependency Analysis Tool for ADHD Calendar Backend.

This script analyzes Python module dependencies, generates dependency graphs,
and provides RAG-based suggestions for improvements.
"""

import os
import sys
import argparse
import json
import logging
from pathlib import Path

from app.utils.dependency_analyzer import DependencyAnalyzer, get_dependency_analyzer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_parser() -> argparse.ArgumentParser:
    """Set up the argument parser."""
    parser = argparse.ArgumentParser(
        description="Analyze module dependencies and suggest improvements"
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # analyze-file command
    analyze_file_parser = subparsers.add_parser(
        "analyze-file", help="Analyze a single file"
    )
    analyze_file_parser.add_argument(
        "file_path", type=str, help="Path to the Python file to analyze"
    )
    analyze_file_parser.add_argument(
        "--output", "-o", type=str,
        help="Path to save the analysis output (JSON)"
    )

    # analyze-directory command
    analyze_dir_parser = subparsers.add_parser(
        "analyze-directory", help="Analyze all Python files in a directory"
    )
    analyze_dir_parser.add_argument(
        "directory", type=str, nargs="?", default=".",
        help="Directory to analyze (defaults to current directory)"
    )
    analyze_dir_parser.add_argument(
        "--output", "-o", type=str,
        help="Path to save the analysis output (JSON)"
    )

    # dependency-graph command
    graph_parser = subparsers.add_parser(
        "dependency-graph", help="Generate a dependency graph"
    )
    graph_parser.add_argument(
        "directory", type=str, nargs="?", default=".",
        help="Directory to analyze (defaults to current directory)"
    )
    graph_parser.add_argument(
        "--format", "-f", type=str, choices=["json", "dot", "mermaid"],
        default="json", help="Output format (defaults to json)"
    )
    graph_parser.add_argument(
        "--output", "-o", type=str,
        help="Path to save the graph output"
    )

    # trace-deps command
    trace_parser = subparsers.add_parser(
        "trace-deps", help="Trace dependencies using RAG"
    )
    trace_parser.add_argument(
        "file_path", type=str, help="Path to the Python file to analyze"
    )
    trace_parser.add_argument(
        "--output", "-o", type=str,
        help="Path to save the output (JSON)"
    )

    # suggest command
    suggest_parser = subparsers.add_parser(
        "suggest", help="Get RAG-based suggestions for a file"
    )
    suggest_parser.add_argument(
        "file_path", type=str, help="Path to the Python file to analyze"
    )
    suggest_parser.add_argument(
        "--query", "-q", type=str,
        help="Query to send to the RAG system (defaults to dependency analysis query)"
    )
    suggest_parser.add_argument(
        "--output", "-o", type=str,
        help="Path to save the suggestions (text)"
    )

    # circular command
    circular_parser = subparsers.add_parser(
        "circular", help="Find circular dependencies"
    )
    circular_parser.add_argument(
        "directory", type=str, nargs="?", default=".",
        help="Directory to analyze (defaults to current directory)"
    )
    circular_parser.add_argument(
        "--output", "-o", type=str,
        help="Path to save the output (JSON)"
    )

    # weekly-resampling command
    weekly_parser = subparsers.add_parser(
        "weekly-resampling", help="Analyze dependencies for weekly resampling feature"
    )
    weekly_parser.add_argument(
        "file_path", type=str,
        help="Path to the TimeBufferCalculator file to analyze"
    )
    weekly_parser.add_argument(
        "--output", "-o", type=str,
        help="Path to save the analysis output (JSON)"
    )

    return parser

def handle_analyze_file(args):
    """Handle the analyze-file command."""
    analyzer = get_dependency_analyzer()

    try:
        results = analyzer.analyze_file(args.file_path)

        if "error" in results:
            logger.error(f"Error analyzing file: {results['error']}")
            return 1

        print(f"File: {args.file_path}")
        print(f"Module: {results['module']}")
        print(f"Imports: {', '.join(results['imports'])}")
        print(f"Functions: {len(results['functions'])}")
        print(f"Classes: {len(results['classes'])}")

        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"Analysis saved to {args.output}")

        return 0

    except Exception as e:
        logger.error(f"Error analyzing file: {str(e)}")
        return 1

def handle_analyze_directory(args):
    """Handle the analyze-directory command."""
    analyzer = get_dependency_analyzer()

    try:
        results = analyzer.analyze_directory(args.directory)

        print(f"Directory: {args.directory}")
        print(f"Modules analyzed: {len(results['modules'])}")
        print(f"Errors: {len(results['errors'])}")

        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"Analysis saved to {args.output}")

        return 0

    except Exception as e:
        logger.error(f"Error analyzing directory: {str(e)}")
        return 1

def handle_dependency_graph(args):
    """Handle the dependency-graph command."""
    analyzer = get_dependency_analyzer()

    try:
        # First analyze the directory to build the dependency graph
        analyzer.analyze_directory(args.directory)

        # Then generate the graph representation
        graph = analyzer.generate_dependency_graph(args.format)

        if args.output:
            with open(args.output, 'w') as f:
                f.write(graph)
            print(f"Dependency graph saved to {args.output}")
        else:
            print(graph)

        return 0

    except Exception as e:
        logger.error(f"Error generating dependency graph: {str(e)}")
        return 1

def handle_trace_deps(args):
    """Handle the trace-deps command."""
    analyzer = get_dependency_analyzer()

    try:
        results = analyzer.trace_dependencies(args.file_path, args.output)

        if "error" in results:
            logger.error(f"Error tracing dependencies: {results['error']}")
            return 1

        # If we have raw output and not structured data, print it
        if "raw_output" in results:
            print(results["raw_output"])
        else:
            # Otherwise format the results
            print(f"File: {results.get('file_path', args.file_path)}")
            deps = results.get("dependencies", [])
            print(f"Dependencies found: {len(deps)}")

            for i, dep in enumerate(deps, 1):
                dep_name = dep.get("name", f"Dependency {i}")
                dep_source = dep.get("source", "unknown")
                print(f"{i}. {dep_name} (source: {dep_source})")

        if args.output and not os.path.exists(args.output):
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"Dependency trace saved to {args.output}")

        return 0

    except Exception as e:
        logger.error(f"Error tracing dependencies: {str(e)}")
        return 1

def handle_suggest(args):
    """Handle the suggest command."""
    analyzer = get_dependency_analyzer()

    try:
        results = analyzer.suggest_with_rag(args.file_path, args.query)

        if "error" in results:
            logger.error(f"Error generating suggestions: {results['error']}")
            return 1

        print(f"File: {args.file_path}")
        print(f"Query: {results.get('query', args.query)}")
        print("\n--- Suggestion ---\n")
        print(results.get("suggestion", "No suggestion generated"))

        if args.output:
            with open(args.output, 'w') as f:
                f.write(results.get("suggestion", "No suggestion generated"))
            print(f"Suggestion saved to {args.output}")

        return 0

    except Exception as e:
        logger.error(f"Error generating suggestions: {str(e)}")
        return 1

def handle_circular(args):
    """Handle the circular command."""
    analyzer = get_dependency_analyzer()

    try:
        # First analyze the directory to build the dependency graph
        analyzer.analyze_directory(args.directory)

        # Then find circular dependencies
        cycles = analyzer.find_circular_dependencies()

        print(f"Directory: {args.directory}")
        print(f"Circular dependencies found: {len(cycles)}")

        for i, cycle in enumerate(cycles, 1):
            print(f"{i}. {' -> '.join(cycle)}")

        if args.output:
            with open(args.output, 'w') as f:
                json.dump(cycles, f, indent=2)
            print(f"Circular dependencies saved to {args.output}")

        return 0

    except Exception as e:
        logger.error(f"Error finding circular dependencies: {str(e)}")
        return 1

def handle_weekly_resampling(args):
    """Handle the weekly-resampling command."""
    analyzer = get_dependency_analyzer()

    try:
        results = analyzer.analyze_weekly_resampling_dependencies(args.file_path)

        if "error" in results:
            logger.error(f"Error analyzing weekly resampling: {results['error']}")
            return 1

        print(f"File: {args.file_path}")
        deps = results.get("dependencies", [])
        print(f"Dependencies found: {len(deps)}")

        for i, dep in enumerate(deps, 1):
            dep_name = dep.get("name", f"Dependency {i}")
            dep_source = dep.get("source", "unknown")
            print(f"{i}. {dep_name} (source: {dep_source})")

        print("\n--- Weekly Resampling Suggestion ---\n")
        print(results.get("weekly_resampling_suggestion", "No suggestion generated"))

        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"Analysis saved to {args.output}")

        return 0

    except Exception as e:
        logger.error(f"Error analyzing weekly resampling: {str(e)}")
        return 1

def main():
    """Main entry point."""
    parser = setup_parser()
    args = parser.parse_args()

    if args.command == "analyze-file":
        return handle_analyze_file(args)
    elif args.command == "analyze-directory":
        return handle_analyze_directory(args)
    elif args.command == "dependency-graph":
        return handle_dependency_graph(args)
    elif args.command == "trace-deps":
        return handle_trace_deps(args)
    elif args.command == "suggest":
        return handle_suggest(args)
    elif args.command == "circular":
        return handle_circular(args)
    elif args.command == "weekly-resampling":
        return handle_weekly_resampling(args)
    else:
        parser.print_help()
        return 1

if __name__ == "__main__":
    sys.exit(main())
