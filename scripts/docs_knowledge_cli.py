#!/usr/bin/env python3
"""
Documentation Knowledge Graph CLI Tool.

This script provides a command-line interface for interacting with the documentation
knowledge graph system, allowing users to scan documentation, query the graph, and
generate visualizations and reports.
"""

import argparse
import os
import sys
from typing import Optional, List

# Add parent directory to path so we can import from app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils.knowledge_graph import (
    get_knowledge_graph,
    NodeType,
    EdgeType,
    DocumentationNode,
    DocumentationEdge
)


def setup_parser() -> argparse.ArgumentParser:
    """Set up command line argument parser."""
    parser = argparse.ArgumentParser(
        description="Documentation Knowledge Graph CLI Tool",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Scan command
    scan_parser = subparsers.add_parser("scan", help="Scan documentation directory")
    scan_parser.add_argument(
        "directory",
        nargs="?",
        default="docs",
        help="Directory to scan (defaults to docs)"
    )

    # Visualize command
    visualize_parser = subparsers.add_parser("visualize", help="Generate knowledge graph visualization")
    visualize_parser.add_argument(
        "--output",
        default="docs_knowledge_graph",
        help="Output file path (without extension)"
    )
    visualize_parser.add_argument(
        "--format",
        choices=["graphviz"],
        default="graphviz",
        help="Visualization format"
    )

    # Report command
    report_parser = subparsers.add_parser("report", help="Generate knowledge graph report")
    report_parser.add_argument(
        "--output",
        default="docs/knowledge_graph_report.md",
        help="Output file path"
    )

    # Query command
    query_parser = subparsers.add_parser("query", help="Query the knowledge graph")
    query_parser.add_argument(
        "--search",
        help="Text to search for"
    )
    query_parser.add_argument(
        "--node-type",
        choices=[
            NodeType.DOCUMENT,
            NodeType.CONCEPT,
            NodeType.MODEL,
            NodeType.EPIC,
            NodeType.API,
            NodeType.IMPLEMENTATION,
            NodeType.USER_GUIDE
        ],
        help="Filter by node type"
    )
    query_parser.add_argument(
        "--tags",
        help="Filter by comma-separated list of tags"
    )

    # Find related nodes command
    related_parser = subparsers.add_parser("related", help="Find related nodes")
    related_parser.add_argument(
        "node_id",
        help="ID of the node to find related nodes for"
    )
    related_parser.add_argument(
        "--depth",
        type=int,
        default=1,
        help="Maximum depth to search for related nodes"
    )

    # Node info command
    info_parser = subparsers.add_parser("info", help="Get information about a node")
    info_parser.add_argument(
        "node_id",
        help="ID of the node to get information about"
    )

    # Stats command
    subparsers.add_parser("stats", help="Show knowledge graph statistics")

    return parser


def handle_scan(args) -> None:
    """Handle the 'scan' command."""
    kg = get_knowledge_graph()

    print(f"Scanning documentation directory: {args.directory}")
    try:
        kg.scan_documentation_directory(args.directory)
        print("Scan completed successfully.")
        print(f"Knowledge graph now has {len(kg.nodes)} nodes and {len(kg.edges)} edges.")
    except Exception as e:
        print(f"Error scanning documentation directory: {e}")


def handle_visualize(args) -> None:
    """Handle the 'visualize' command."""
    kg = get_knowledge_graph()

    print(f"Generating knowledge graph visualization: {args.output}")
    try:
        kg.generate_graph_visualization(args.output, args.format)
        print(f"Visualization generated at {args.output}.png")
    except Exception as e:
        print(f"Error generating visualization: {e}")


def handle_report(args) -> None:
    """Handle the 'report' command."""
    kg = get_knowledge_graph()

    print(f"Generating knowledge graph report: {args.output}")
    try:
        kg.generate_markdown_report(args.output)
        print(f"Report generated at {args.output}")
    except Exception as e:
        print(f"Error generating report: {e}")


def handle_query(args) -> None:
    """Handle the 'query' command."""
    kg = get_knowledge_graph()

    # Parse tags
    tags = None
    if args.tags:
        tags = [tag.strip() for tag in args.tags.split(",")]

    # Create list of node types
    node_types = None
    if args.node_type:
        node_types = [args.node_type]

    # Perform the search
    results = kg.search_nodes(
        query=args.search,
        node_types=node_types,
        tags=tags
    )

    if not results:
        print("No nodes found matching the query.")
        return

    print(f"Found {len(results)} nodes:")
    print()

    for i, node in enumerate(sorted(results, key=lambda x: x.name), 1):
        print(f"{i}. [{node.node_type}] {node.name} ({node.id})")
        if node.tags:
            print(f"   Tags: {', '.join(node.tags)}")
        if node.file_path:
            print(f"   File: {node.file_path}")
        print()


def handle_related(args) -> None:
    """Handle the 'related' command."""
    kg = get_knowledge_graph()

    node = kg.get_node(args.node_id)
    if not node:
        print(f"No node found with ID: {args.node_id}")
        return

    print(f"Finding nodes related to '{node.name}' (up to depth {args.depth}):")
    print()

    relations = kg.get_related_nodes(args.node_id, max_depth=args.depth)

    if not relations:
        print("No related nodes found.")
        return

    for relation_type, related_nodes in relations.items():
        print(f"## {relation_type.replace('_', ' ').title()}")
        print()

        for related_node, edge, depth in related_nodes:
            print(f"- [{related_node.node_type}] {related_node.name} (depth: {depth})")
            if edge.weight != 1.0:
                print(f"  Relationship strength: {edge.weight:.2f}")
        print()


def handle_info(args) -> None:
    """Handle the 'info' command."""
    kg = get_knowledge_graph()

    node = kg.get_node(args.node_id)
    if not node:
        print(f"No node found with ID: {args.node_id}")
        return

    print(f"Information about node '{node.name}':")
    print()
    print(f"ID: {node.id}")
    print(f"Type: {node.node_type}")
    if node.file_path:
        print(f"File: {node.file_path}")
    if node.url:
        print(f"URL: {node.url}")
    if node.tags:
        print(f"Tags: {', '.join(node.tags)}")
    print(f"Created: {node.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Updated: {node.updated_at.strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    if node.content_summary:
        print("Summary:")
        print(node.content_summary)
        print()

    if node.metadata:
        print("Metadata:")
        for key, value in node.metadata.items():
            if isinstance(value, list) and value:
                print(f"- {key}: {', '.join(str(v) for v in value)}")
            elif value:
                print(f"- {key}: {value}")
        print()

    # Show outgoing relationships
    outgoing = kg.get_outgoing_edges(node.id)
    if outgoing:
        print("Outgoing Relationships:")
        for edge in outgoing:
            target = kg.get_node(edge.target_id)
            if target:
                print(f"- {edge.edge_type} -> {target.name} ({target.node_type})")
        print()

    # Show incoming relationships
    incoming = kg.get_incoming_edges(node.id)
    if incoming:
        print("Incoming Relationships:")
        for edge in incoming:
            source = kg.get_node(edge.source_id)
            if source:
                print(f"- {edge.edge_type} <- {source.name} ({source.node_type})")
        print()


def handle_stats(args) -> None:
    """Handle the 'stats' command."""
    kg = get_knowledge_graph()

    print("Knowledge Graph Statistics:")
    print()
    print(f"Total Nodes: {len(kg.nodes)}")
    print(f"Total Edges: {len(kg.edges)}")
    print()

    # Node statistics by type
    node_types = {}
    for node in kg.nodes.values():
        if node.node_type not in node_types:
            node_types[node.node_type] = 0
        node_types[node.node_type] += 1

    print("Node Types:")
    for node_type, count in sorted(node_types.items(), key=lambda x: x[1], reverse=True):
        print(f"- {node_type}: {count}")
    print()

    # Edge statistics by type
    edge_types = {}
    for edge in kg.edges:
        if edge.edge_type not in edge_types:
            edge_types[edge.edge_type] = 0
        edge_types[edge.edge_type] += 1

    print("Edge Types:")
    for edge_type, count in sorted(edge_types.items(), key=lambda x: x[1], reverse=True):
        print(f"- {edge_type}: {count}")
    print()


def main() -> None:
    """Main entry point for the CLI tool."""
    parser = setup_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Dispatch to the appropriate handler based on the command
    handlers = {
        "scan": handle_scan,
        "visualize": handle_visualize,
        "report": handle_report,
        "query": handle_query,
        "related": handle_related,
        "info": handle_info,
        "stats": handle_stats
    }

    handler = handlers.get(args.command)
    if handler:
        handler(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
