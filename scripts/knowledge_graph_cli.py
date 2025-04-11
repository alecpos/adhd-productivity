#!/usr/bin/env python3
"""
Documentation Knowledge Graph CLI Tool.

This script provides a command-line interface for managing the documentation
knowledge graph, including building, querying, visualizing, and exporting
various views of the graph.
"""

import os
import sys
import argparse
import json
import textwrap
from pathlib import Path
from typing import Dict, List, Any, Optional
import datetime

# Add project root to path to enable imports
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from app.utils.knowledge_graph import (
    DocumentationNode,
    DocumentationEdge,
    NodeType,
    EdgeType,
    get_knowledge_graph,
)


class CustomJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder for handling dates and other complex objects."""

    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        if isinstance(obj, set):
            return list(obj)
        try:
            return obj.to_dict() if hasattr(obj, "to_dict") else super().default(obj)
        except TypeError:
            return str(obj)


class KnowledgeGraphCLI:
    """Command-line interface for the documentation knowledge graph."""

    def __init__(self):
        """Initialize the CLI."""
        self.graph = get_knowledge_graph()

    def scan_documentation(self, directory: str = None) -> None:
        """Scan documentation directory and build knowledge graph."""
        if directory is None:
            directory = os.path.join(project_root, "docs")

        print(f"Scanning documentation in {directory}...")
        self.graph.scan_documentation_directory(directory)
        print("Documentation scan complete.")
        print(f"Added {len(self.graph.nodes)} nodes and {len(self.graph.edges)} relationships.")

    def create_relationships(self) -> None:
        """Create relationships between documentation nodes."""
        print("Creating relationships between documentation nodes...")
        self.graph._create_document_relationships()
        print(f"Knowledge graph now has {len(self.graph.edges)} relationships.")

    def visualize(self, output_file: str = None, format: str = "graphviz") -> None:
        """Generate a visualization of the knowledge graph."""
        if output_file is None:
            output_file = os.path.join(project_root, "docs", "knowledge_graph_visualization.png")

        print(f"Generating knowledge graph visualization to {output_file}...")
        self.graph.generate_graph_visualization(output_file, format)
        print("Visualization complete.")

    def generate_report(self, output_file: str = None) -> None:
        """Generate a markdown report of the knowledge graph."""
        if output_file is None:
            output_file = os.path.join(project_root, "docs", "knowledge_graph_report.md")

        print(f"Generating knowledge graph report to {output_file}...")
        self.graph.generate_markdown_report(output_file)
        print("Report generation complete.")

    def search(self, query: str, node_types: List[str] = None, tags: List[str] = None) -> None:
        """Search the knowledge graph for nodes matching criteria."""
        results = self.graph.search_nodes(query, node_types, tags)

        if not results:
            print("No matching nodes found.")
            return

        print(f"Found {len(results)} matching nodes:")
        print("-" * 80)

        for node in results:
            print(f"ID: {node.id}")
            print(f"Name: {node.name}")
            print(f"Type: {node.node_type}")
            if node.tags:
                print(f"Tags: {', '.join(node.tags)}")
            if node.file_path:
                print(f"File: {node.file_path}")
            if node.content_summary:
                print(
                    f"Summary: {textwrap.shorten(node.content_summary, width=60, placeholder='...')}"
                )
            print("-" * 80)

    def get_related(self, node_id: str, max_depth: int = 1) -> None:
        """Get related nodes for a specific node."""
        node = self.graph.get_node(node_id)

        if not node:
            print(f"Node with ID {node_id} not found.")
            return

        print(f'Related nodes for "{node.name}" (ID: {node.id}):')
        print("-" * 80)

        related = self.graph.get_related_nodes(node_id, max_depth)

        for depth, nodes_at_depth in sorted(related.items()):
            if nodes_at_depth:
                print(f"\nDepth {depth}:")
                for related_node, edge, _ in nodes_at_depth:
                    edge_type = edge.edge_type
                    print(f"  - {related_node.name} ({related_node.node_type}) - {edge_type}")

    def add_node(
        self,
        name: str,
        node_type: str,
        file_path: str = None,
        tags: List[str] = None,
        content_summary: str = None,
    ) -> None:
        """Add a new node to the knowledge graph."""
        # Generate a unique ID
        node_id = f"{node_type}_{name.lower().replace(' ', '_')}"

        # Create the node
        node = DocumentationNode(
            id=node_id,
            name=name,
            node_type=node_type,
            file_path=file_path,
            tags=tags,
            content_summary=content_summary,
        )

        # Add to the graph
        self.graph.add_node(node)
        print(f"Added node: {name} (ID: {node_id})")

    def add_edge(self, source_id: str, target_id: str, edge_type: str) -> None:
        """Add a new edge to the knowledge graph."""
        # Check if nodes exist
        source_node = self.graph.get_node(source_id)
        target_node = self.graph.get_node(target_id)

        if not source_node:
            print(f"Source node with ID {source_id} not found.")
            return

        if not target_node:
            print(f"Target node with ID {target_id} not found.")
            return

        # Create the edge
        edge = DocumentationEdge(source_id=source_id, target_id=target_id, edge_type=edge_type)

        # Add to the graph
        self.graph.add_edge(edge)
        print(f"Added edge: {source_node.name} --[{edge_type}]--> {target_node.name}")

    def export_graph(self, output_file: str = None) -> None:
        """Export the knowledge graph to JSON."""
        if output_file is None:
            output_file = os.path.join(project_root, "docs", "knowledge_graph_export.json")

        # Prepare data for export
        export_data = {
            "nodes": [node.to_dict() for node in self.graph.nodes.values()],
            "edges": [edge.to_dict() for edge in self.graph.edges],
        }

        # Write to file
        with open(output_file, "w") as f:
            json.dump(export_data, f, indent=2, cls=CustomJSONEncoder, ensure_ascii=False)

        print(f"Knowledge graph exported to {output_file}")

    def import_graph(self, input_file: str) -> None:
        """Import a knowledge graph from JSON."""
        if not os.path.exists(input_file):
            print(f"File not found: {input_file}")
            return

        try:
            with open(input_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Clear existing graph
            self.graph.nodes = {}
            self.graph.edges = []

            # Import nodes
            for node_data in data.get("nodes", []):
                node = DocumentationNode.from_dict(node_data)
                self.graph.nodes[node.id] = node

            # Import edges
            for edge_data in data.get("edges", []):
                edge = DocumentationEdge.from_dict(edge_data)
                self.graph.edges.append(edge)

            print(f"Imported {len(self.graph.nodes)} nodes and {len(self.graph.edges)} edges.")

        except json.JSONDecodeError as e:
            print(f"Error loading knowledge graph: {e}")
        except Exception as e:
            print(f"Error importing graph: {e}")

    def generate_ml_knowledge_subgraph(self, output_file: str = None) -> None:
        """Generate an ML-specific subgraph focusing on ML techniques and models."""
        # Find all ML-related nodes
        ml_nodes = self.graph.search_nodes(
            query=None, node_types=[NodeType.ML_TECHNIQUE, NodeType.ALGORITHM, NodeType.MODEL]
        )

        if not ml_nodes:
            print("No ML-related nodes found.")
            return

        # Create a subgraph by finding connections between these nodes
        ml_node_ids = [node.id for node in ml_nodes]
        ml_edges = []

        for edge in self.graph.edges:
            if edge.source_id in ml_node_ids and edge.target_id in ml_node_ids:
                ml_edges.append(edge)

        # Export to file
        if output_file is None:
            output_file = os.path.join(project_root, "docs", "ml_knowledge_subgraph.json")

        # Prepare data for export
        export_data = {
            "nodes": [node.to_dict() for node in ml_nodes],
            "edges": [edge.to_dict() for edge in ml_edges],
        }

        # Write to file
        with open(output_file, "w") as f:
            json.dump(export_data, f, indent=2, default=str)

        print(f"ML knowledge subgraph exported to {output_file}")
        print(f"Includes {len(ml_nodes)} nodes and {len(ml_edges)} edges.")

    def list_node_types(self) -> None:
        """List all available node types."""
        print("Available node types:")
        for attr in dir(NodeType):
            if not attr.startswith("__"):
                print(f"  - {getattr(NodeType, attr)}")

    def list_edge_types(self) -> None:
        """List all available edge types."""
        print("Available edge types:")
        for attr in dir(EdgeType):
            if not attr.startswith("__"):
                print(f"  - {getattr(EdgeType, attr)}")

    def analyze_knowledge_gaps(self) -> None:
        """Analyze the knowledge graph for gaps and missing connections."""
        # Check for isolated nodes (no connections)
        isolated_nodes = []
        connected_node_ids = set()

        for edge in self.graph.edges:
            connected_node_ids.add(edge.source_id)
            connected_node_ids.add(edge.target_id)

        for node_id, node in self.graph.nodes.items():
            if node_id not in connected_node_ids:
                isolated_nodes.append(node)

        # Check for documentation coverage gaps
        implementation_nodes = [
            n for n in self.graph.nodes.values() if n.node_type == NodeType.IMPLEMENTATION
        ]
        documented_impl_ids = set()

        for edge in self.graph.edges:
            if edge.edge_type == EdgeType.DOCUMENTED_BY:
                documented_impl_ids.add(edge.source_id)

        undocumented_impls = [n for n in implementation_nodes if n.id not in documented_impl_ids]

        # Print results
        print("Knowledge Graph Gap Analysis")
        print("===========================")

        print(f"\nIsolated Nodes: {len(isolated_nodes)}")
        for node in isolated_nodes[:10]:  # Show first 10
            print(f"  - {node.name} ({node.node_type})")
        if len(isolated_nodes) > 10:
            print(f"  ... and {len(isolated_nodes) - 10} more")

        print(f"\nUndocumented Implementations: {len(undocumented_impls)}")
        for node in undocumented_impls[:10]:  # Show first 10
            print(f"  - {node.name}")
        if len(undocumented_impls) > 10:
            print(f"  ... and {len(undocumented_impls) - 10} more")

    def recommend_connections(self, node_id: str, max_suggestions: int = 5) -> None:
        """Recommend potential connections for a node based on content similarity."""
        node = self.graph.get_node(node_id)

        if not node:
            print(f"Node with ID {node_id} not found.")
            return

        # Get all nodes of relevant types to connect with
        potential_connections = []
        relevant_types = []

        # Determine relevant node types based on the current node type
        if node.node_type == NodeType.DOCUMENT:
            relevant_types = [NodeType.CONCEPT, NodeType.MODEL, NodeType.CODE_MODULE]
        elif node.node_type == NodeType.CONCEPT:
            relevant_types = [NodeType.DOCUMENT, NodeType.ALGORITHM, NodeType.ML_TECHNIQUE]
        elif node.node_type == NodeType.MODEL:
            relevant_types = [NodeType.DOCUMENT, NodeType.CODE_MODULE, NodeType.TEST]
        else:
            relevant_types = [t for t in dir(NodeType) if not t.startswith("__")]

        # Get existing connections
        existing_connections = set()
        for edge in self.graph.edges:
            if edge.source_id == node_id:
                existing_connections.add(edge.target_id)
            elif edge.target_id == node_id:
                existing_connections.add(edge.source_id)

        # Find potential connections (simplified heuristic approach)
        # In a real implementation, use text similarity or ML-based recommendation
        for other_id, other_node in self.graph.nodes.items():
            if (
                other_id != node_id
                and other_id not in existing_connections
                and other_node.node_type in relevant_types
            ):

                # Simple heuristic: check for shared words in name or content
                similarity_score = 0

                # Check for shared words in names
                node_words = set(node.name.lower().split())
                other_words = set(other_node.name.lower().split())
                shared_words = node_words.intersection(other_words)

                similarity_score += len(shared_words) * 0.5

                # Check for shared tags
                if node.tags and other_node.tags:
                    shared_tags = set(node.tags).intersection(set(other_node.tags))
                    similarity_score += len(shared_tags) * 2

                # Only consider if there's some similarity
                if similarity_score > 0:
                    potential_connections.append((other_node, similarity_score))

        # Sort by similarity score and get top suggestions
        potential_connections.sort(key=lambda x: x[1], reverse=True)
        top_suggestions = potential_connections[:max_suggestions]

        # Print recommendations
        print(f'Connection recommendations for "{node.name}" (ID: {node.id}):')

        if not top_suggestions:
            print("No relevant connection suggestions found.")
            return

        for suggested_node, score in top_suggestions:
            print(
                f"  - {suggested_node.name} ({suggested_node.node_type}) - similarity: {score:.2f}"
            )
            print(f"    Suggested relationship: {EdgeType.RELATED_TO}")
            print(
                f"    Command to add: add-edge {node.id} {suggested_node.id} {EdgeType.RELATED_TO}"
            )
            print()


def setup_parser() -> argparse.ArgumentParser:
    """Set up command-line argument parser."""
    parser = argparse.ArgumentParser(description="Documentation Knowledge Graph CLI Tool")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Scan documentation
    scan_parser = subparsers.add_parser("scan", help="Scan documentation and build knowledge graph")
    scan_parser.add_argument("--dir", help="Directory to scan (defaults to docs/)")

    # Create relationships
    subparsers.add_parser(
        "create-relationships", help="Create relationships between documentation nodes"
    )

    # Visualize
    visualize_parser = subparsers.add_parser(
        "visualize", help="Generate knowledge graph visualization"
    )
    visualize_parser.add_argument("--output", help="Output file path")
    visualize_parser.add_argument(
        "--format", choices=["graphviz", "d3"], default="graphviz", help="Visualization format"
    )

    # Generate report
    report_parser = subparsers.add_parser("report", help="Generate knowledge graph report")
    report_parser.add_argument("--output", help="Output file path")

    # Search
    search_parser = subparsers.add_parser("search", help="Search the knowledge graph")
    search_parser.add_argument("query", nargs="?", help="Search query")
    search_parser.add_argument("--types", nargs="+", help="Filter by node types")
    search_parser.add_argument("--tags", nargs="+", help="Filter by tags")

    # Get related nodes
    related_parser = subparsers.add_parser("related", help="Get related nodes")
    related_parser.add_argument("node_id", help="Node ID to get related nodes for")
    related_parser.add_argument(
        "--depth", type=int, default=1, help="Maximum depth to search for related nodes"
    )

    # Add node
    add_node_parser = subparsers.add_parser("add-node", help="Add a new node")
    add_node_parser.add_argument("name", help="Node name")
    add_node_parser.add_argument("node_type", help="Node type")
    add_node_parser.add_argument("--file", help="File path")
    add_node_parser.add_argument("--tags", nargs="+", help="Tags")
    add_node_parser.add_argument("--summary", help="Content summary")

    # Add edge
    add_edge_parser = subparsers.add_parser("add-edge", help="Add a new edge")
    add_edge_parser.add_argument("source_id", help="Source node ID")
    add_edge_parser.add_argument("target_id", help="Target node ID")
    add_edge_parser.add_argument("edge_type", help="Edge type")

    # Export graph
    export_parser = subparsers.add_parser("export", help="Export knowledge graph")
    export_parser.add_argument("--output", help="Output file path")

    # Import graph
    import_parser = subparsers.add_parser("import", help="Import knowledge graph")
    import_parser.add_argument("input", help="Input file path")

    # Generate ML knowledge subgraph
    ml_parser = subparsers.add_parser("ml-subgraph", help="Generate ML knowledge subgraph")
    ml_parser.add_argument("--output", help="Output file path")

    # List node types
    subparsers.add_parser("list-node-types", help="List available node types")

    # List edge types
    subparsers.add_parser("list-edge-types", help="List available edge types")

    # Analyze knowledge gaps
    subparsers.add_parser("analyze-gaps", help="Analyze knowledge graph for gaps")

    # Recommend connections
    recommend_parser = subparsers.add_parser("recommend", help="Recommend connections for a node")
    recommend_parser.add_argument("node_id", help="Node ID to get recommendations for")
    recommend_parser.add_argument(
        "--max", type=int, default=5, help="Maximum number of recommendations"
    )

    return parser


def main():
    """Main function to run the CLI."""
    parser = setup_parser()
    args = parser.parse_args()

    cli = KnowledgeGraphCLI()

    if args.command == "scan":
        cli.scan_documentation(args.dir)
    elif args.command == "create-relationships":
        cli.create_relationships()
    elif args.command == "visualize":
        cli.visualize(args.output, args.format)
    elif args.command == "report":
        cli.generate_report(args.output)
    elif args.command == "search":
        cli.search(args.query, args.types, args.tags)
    elif args.command == "related":
        cli.get_related(args.node_id, args.depth)
    elif args.command == "add-node":
        cli.add_node(args.name, args.node_type, args.file, args.tags, args.summary)
    elif args.command == "add-edge":
        cli.add_edge(args.source_id, args.target_id, args.edge_type)
    elif args.command == "export":
        cli.export_graph(args.output)
    elif args.command == "import":
        cli.import_graph(args.input)
    elif args.command == "ml-subgraph":
        cli.generate_ml_knowledge_subgraph(args.output)
    elif args.command == "list-node-types":
        cli.list_node_types()
    elif args.command == "list-edge-types":
        cli.list_edge_types()
    elif args.command == "analyze-gaps":
        cli.analyze_knowledge_gaps()
    elif args.command == "recommend":
        cli.recommend_connections(args.node_id, args.max)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
