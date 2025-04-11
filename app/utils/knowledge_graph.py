"""
Documentation Knowledge Graph System.

This module provides utilities for creating, managing, and querying a knowledge graph
of documentation in the ML project. It helps connect related documents, concepts,
and code, making it easier to navigate the documentation landscape.
"""

import os
import re
import json
import logging
import glob
from datetime import datetime
from typing import Dict, List, Set, Tuple, Optional, Any, Union
from pathlib import Path
from collections import defaultdict

logger = logging.getLogger(__name__)


class NodeType:
    """Types of nodes in the knowledge graph."""

    DOCUMENT = "document"
    CONCEPT = "concept"
    MODEL = "model"
    EPIC = "epic"
    API = "api"
    IMPLEMENTATION = "implementation"
    USER_GUIDE = "user_guide"
    CODE_MODULE = "code_module"
    TEST = "test"
    ML_TECHNIQUE = "ml_technique"
    ALGORITHM = "algorithm"


class EdgeType:
    """Types of edges (relationships) in the knowledge graph."""

    REFERENCES = "references"
    IMPLEMENTS = "implements"
    EXPLAINS = "explains"
    PART_OF = "part_of"
    DEPENDS_ON = "depends_on"
    TESTED_BY = "tested_by"
    USES = "uses"
    EXTENDS = "extends"
    RELATED_TO = "related_to"
    DERIVED_FROM = "derived_from"
    DOCUMENTED_BY = "documented_by"


class DocumentationNode:
    """Represents a node in the documentation knowledge graph."""

    def __init__(
        self,
        id: str,
        name: str,
        node_type: str,
        file_path: Optional[str] = None,
        url: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        content_summary: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        """Initialize a documentation node."""
        self.id = id
        self.name = name
        self.node_type = node_type
        self.file_path = file_path
        self.url = url
        self.tags = tags or []
        self.metadata = metadata or {}
        self.content_summary = content_summary
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert the node to a dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "node_type": self.node_type,
            "file_path": self.file_path,
            "url": self.url,
            "tags": self.tags,
            "metadata": self.metadata,
            "content_summary": self.content_summary,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DocumentationNode":
        """Create a node from a dictionary."""
        # Convert ISO format strings back to datetime objects
        created_at = datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None
        updated_at = datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None

        return cls(
            id=data["id"],
            name=data["name"],
            node_type=data["node_type"],
            file_path=data.get("file_path"),
            url=data.get("url"),
            tags=data.get("tags", []),
            metadata=data.get("metadata", {}),
            content_summary=data.get("content_summary"),
            created_at=created_at,
            updated_at=updated_at,
        )


class DocumentationEdge:
    """Represents an edge (relationship) in the documentation knowledge graph."""

    def __init__(
        self,
        source_id: str,
        target_id: str,
        edge_type: str,
        weight: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None,
        created_at: Optional[datetime] = None,
    ):
        """Initialize a documentation edge."""
        self.source_id = source_id
        self.target_id = target_id
        self.edge_type = edge_type
        self.weight = weight
        self.metadata = metadata or {}
        self.created_at = created_at or datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert the edge to a dictionary for serialization."""
        return {
            "source_id": self.source_id,
            "target_id": self.target_id,
            "edge_type": self.edge_type,
            "weight": self.weight,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DocumentationEdge":
        """Create an edge from a dictionary."""
        # Convert ISO format string back to datetime object
        created_at = datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None

        return cls(
            source_id=data["source_id"],
            target_id=data["target_id"],
            edge_type=data["edge_type"],
            weight=data.get("weight", 1.0),
            metadata=data.get("metadata", {}),
            created_at=created_at,
        )

    def __hash__(self):
        """Make the edge hashable."""
        return hash((self.source_id, self.target_id, self.edge_type))

    def __eq__(self, other):
        """Define equality for the edge."""
        if not isinstance(other, DocumentationEdge):
            return False
        return (
            self.source_id == other.source_id
            and self.target_id == other.target_id
            and self.edge_type == other.edge_type
        )


class DocumentationKnowledgeGraph:
    """Main class for managing the documentation knowledge graph."""

    def __init__(self, db_path: Optional[str] = None):
        """Initialize the knowledge graph."""
        self.db_path = db_path or os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "docs_knowledge_graph.json",
        )
        self.nodes: Dict[str, DocumentationNode] = {}
        self.edges: Set[DocumentationEdge] = set()
        self.edges_by_source: Dict[str, List[DocumentationEdge]] = defaultdict(list)
        self.edges_by_target: Dict[str, List[DocumentationEdge]] = defaultdict(list)
        self.edges_by_type: Dict[str, List[DocumentationEdge]] = defaultdict(list)
        self._load_graph()

    def _load_graph(self) -> None:
        """Load the knowledge graph from the database file."""
        if not os.path.exists(self.db_path):
            # Create the initial database file if it doesn't exist
            self._save_graph()
            return

        try:
            with open(self.db_path, "r") as f:
                data = json.load(f)

            # Load nodes
            for node_data in data.get("nodes", []):
                node = DocumentationNode.from_dict(node_data)
                self.nodes[node.id] = node

            # Load edges
            for edge_data in data.get("edges", []):
                edge = DocumentationEdge.from_dict(edge_data)
                self.edges.add(edge)
                self.edges_by_source[edge.source_id].append(edge)
                self.edges_by_target[edge.target_id].append(edge)
                self.edges_by_type[edge.edge_type].append(edge)

            logger.info(
                f"Loaded knowledge graph with {len(self.nodes)} nodes and {len(self.edges)} edges"
            )
        except Exception as e:
            logger.error(f"Error loading knowledge graph: {e}")

    def _save_graph(self) -> None:
        """Save the knowledge graph to the database file."""
        try:
            data = {
                "last_updated": datetime.now().isoformat(),
                "nodes": [node.to_dict() for node in self.nodes.values()],
                "edges": [edge.to_dict() for edge in self.edges],
            }

            # Ensure directory exists
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

            with open(self.db_path, "w") as f:
                json.dump(data, f, indent=2)

            logger.info(
                f"Saved knowledge graph with {len(self.nodes)} nodes and {len(self.edges)} edges"
            )
        except Exception as e:
            logger.error(f"Error saving knowledge graph: {e}")

    def add_node(self, node: DocumentationNode) -> str:
        """Add a node to the knowledge graph."""
        self.nodes[node.id] = node
        self._save_graph()
        return node.id

    def get_node(self, node_id: str) -> Optional[DocumentationNode]:
        """Get a node by ID."""
        return self.nodes.get(node_id)

    def update_node(self, node_id: str, **kwargs) -> bool:
        """Update a node."""
        node = self.get_node(node_id)
        if not node:
            return False

        for key, value in kwargs.items():
            if hasattr(node, key):
                setattr(node, key, value)

        node.updated_at = datetime.now()
        self._save_graph()
        return True

    def delete_node(self, node_id: str) -> bool:
        """Delete a node and all its edges."""
        if node_id not in self.nodes:
            return False

        # Remove the node
        del self.nodes[node_id]

        # Remove edges connected to this node
        self.edges = {
            edge for edge in self.edges if edge.source_id != node_id and edge.target_id != node_id
        }

        # Update edge indexes
        if node_id in self.edges_by_source:
            del self.edges_by_source[node_id]

        if node_id in self.edges_by_target:
            del self.edges_by_target[node_id]

        # Update edge_by_type index
        for edge_type in self.edges_by_type:
            self.edges_by_type[edge_type] = [
                edge
                for edge in self.edges_by_type[edge_type]
                if edge.source_id != node_id and edge.target_id != node_id
            ]

        self._save_graph()
        return True

    def add_edge(self, edge: DocumentationEdge) -> None:
        """Add an edge to the knowledge graph."""
        # Check that source and target nodes exist
        if edge.source_id not in self.nodes:
            raise ValueError(f"Source node {edge.source_id} does not exist")

        if edge.target_id not in self.nodes:
            raise ValueError(f"Target node {edge.target_id} does not exist")

        # Add the edge
        self.edges.add(edge)
        self.edges_by_source[edge.source_id].append(edge)
        self.edges_by_target[edge.target_id].append(edge)
        self.edges_by_type[edge.edge_type].append(edge)

        self._save_graph()

    def remove_edge(self, source_id: str, target_id: str, edge_type: str) -> bool:
        """Remove an edge from the knowledge graph."""
        # Find the edge
        edge_to_remove = None
        for edge in self.edges:
            if (
                edge.source_id == source_id
                and edge.target_id == target_id
                and edge.edge_type == edge_type
            ):
                edge_to_remove = edge
                break

        if not edge_to_remove:
            return False

        # Remove the edge
        self.edges.remove(edge_to_remove)
        self.edges_by_source[source_id] = [
            edge for edge in self.edges_by_source[source_id] if edge != edge_to_remove
        ]
        self.edges_by_target[target_id] = [
            edge for edge in self.edges_by_target[target_id] if edge != edge_to_remove
        ]
        self.edges_by_type[edge_type] = [
            edge for edge in self.edges_by_type[edge_type] if edge != edge_to_remove
        ]

        self._save_graph()
        return True

    def get_outgoing_edges(self, node_id: str) -> List[DocumentationEdge]:
        """Get all edges originating from a node."""
        return self.edges_by_source.get(node_id, [])

    def get_incoming_edges(self, node_id: str) -> List[DocumentationEdge]:
        """Get all edges targeting a node."""
        return self.edges_by_target.get(node_id, [])

    def get_edges_by_type(self, edge_type: str) -> List[DocumentationEdge]:
        """Get all edges of a specific type."""
        return self.edges_by_type.get(edge_type, [])

    def get_neighbors(
        self, node_id: str, edge_types: Optional[List[str]] = None
    ) -> List[Tuple[DocumentationNode, DocumentationEdge]]:
        """Get all neighbors of a node, optionally filtered by edge types."""
        outgoing_edges = self.get_outgoing_edges(node_id)
        if edge_types:
            outgoing_edges = [edge for edge in outgoing_edges if edge.edge_type in edge_types]

        neighbors = []
        for edge in outgoing_edges:
            target_node = self.get_node(edge.target_id)
            if target_node:
                neighbors.append((target_node, edge))

        return neighbors

    def get_related_nodes(
        self, node_id: str, max_depth: int = 1
    ) -> Dict[str, List[Tuple[DocumentationNode, DocumentationEdge, int]]]:
        """Get all nodes related to a node up to a certain depth."""
        if node_id not in self.nodes:
            return {}

        # BFS to find related nodes
        queue = [(node_id, 0)]  # (node_id, depth)
        visited = set([node_id])
        relations: Dict[str, List[Tuple[DocumentationNode, DocumentationEdge, int]]] = defaultdict(
            list
        )

        while queue:
            current_id, depth = queue.pop(0)

            if depth >= max_depth:
                continue

            # Get all outgoing edges
            for edge in self.get_outgoing_edges(current_id):
                if edge.target_id not in visited:
                    target_node = self.get_node(edge.target_id)
                    if target_node:
                        relations[edge.edge_type].append((target_node, edge, depth + 1))
                        visited.add(edge.target_id)
                        queue.append((edge.target_id, depth + 1))

            # Get all incoming edges
            for edge in self.get_incoming_edges(current_id):
                if edge.source_id not in visited:
                    source_node = self.get_node(edge.source_id)
                    if source_node:
                        # Use a reverse relationship name
                        reverse_type = f"reverse_{edge.edge_type}"
                        relations[reverse_type].append((source_node, edge, depth + 1))
                        visited.add(edge.source_id)
                        queue.append((edge.source_id, depth + 1))

        return relations

    def search_nodes(
        self,
        query: Optional[str] = None,
        node_types: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
    ) -> List[DocumentationNode]:
        """Search for nodes by text, type, or tags."""
        results = list(self.nodes.values())

        # Filter by node types
        if node_types:
            results = [node for node in results if node.node_type in node_types]

        # Filter by tags
        if tags:
            results = [node for node in results if any(tag in node.tags for tag in tags)]

        # Filter by query text
        if query:
            query = query.lower()
            results = [
                node
                for node in results
                if (
                    query in node.name.lower()
                    or (node.content_summary and query in node.content_summary.lower())
                    or any(query in tag.lower() for tag in node.tags)
                )
            ]

        return results

    def extract_metadata_from_markdown(self, file_path: str) -> Dict[str, Any]:
        """Extract metadata from a markdown file."""
        if not os.path.exists(file_path):
            return {}

        metadata = {
            "title": None,
            "tags": [],
            "epic": None,
            "related_files": [],
            "concepts": [],
            "models": [],
        }

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Extract title (e.g., # Title)
            title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
            if title_match:
                metadata["title"] = title_match.group(1).strip()

            # Extract tags (look for "Tags:" or "Keywords:" sections)
            tags_match = re.search(
                r"(?:Tags|Keywords):\s*(.+?)(?:\n\n|\Z)", content, re.MULTILINE | re.DOTALL
            )
            if tags_match:
                tags_text = tags_match.group(1).strip()
                metadata["tags"] = [
                    tag.strip() for tag in re.split(r"[,;]", tags_text) if tag.strip()
                ]

            # Extract epic information
            epic_match = re.search(r"Epic(?:\s+|:|-)([0-9]+)", content, re.IGNORECASE)
            if epic_match:
                metadata["epic"] = f"Epic {epic_match.group(1)}"

            # Extract related files (look for file references)
            file_refs = re.findall(r"`([^`]+\.(py|md|json|yaml|yml|sql))`", content)
            if file_refs:
                metadata["related_files"] = [ref[0] for ref in file_refs]

            # Extract concepts (look for bold/emphasized terms)
            concepts = re.findall(r"\*\*([^*]+)\*\*", content)
            if concepts:
                metadata["concepts"] = list(set(concepts))

            # Extract model references
            model_refs = re.findall(
                r"(?:Model|model|MODEL):\s*(`?)([A-Za-z0-9_]+(?:Model|model))(`?)", content
            )
            if model_refs:
                metadata["models"] = [ref[1] for ref in model_refs]

            # Extract summary (first paragraph after title)
            summary_match = re.search(r"^#.*?\n\n(.*?)(?:\n\n|\Z)", content, re.DOTALL)
            if summary_match:
                metadata["summary"] = summary_match.group(1).strip()
            else:
                metadata["summary"] = None

        except Exception as e:
            logger.error(f"Error extracting metadata from {file_path}: {e}")

        return metadata

    def scan_documentation_directory(self, directory: str) -> None:
        """Scan a directory for documentation files and add them to the graph."""
        if not os.path.exists(directory) or not os.path.isdir(directory):
            raise ValueError(f"Directory not found: {directory}")

        # Find all markdown files
        markdown_files = glob.glob(os.path.join(directory, "**", "*.md"), recursive=True)
        logger.info(f"Found {len(markdown_files)} markdown files in {directory}")

        # Process each file
        for file_path in markdown_files:
            try:
                # Extract metadata
                metadata = self.extract_metadata_from_markdown(file_path)

                # Generate a node ID from the file path
                rel_path = os.path.relpath(file_path, os.path.dirname(os.path.dirname(directory)))
                node_id = f"doc_{rel_path.replace('/', '_').replace('.', '_')}"

                # Determine node type
                node_type = NodeType.DOCUMENT
                if "api" in file_path.lower():
                    node_type = NodeType.API
                elif "implementation" in file_path.lower():
                    node_type = NodeType.IMPLEMENTATION
                elif "user_guide" in file_path.lower() or "guide" in file_path.lower():
                    node_type = NodeType.USER_GUIDE
                elif re.search(r"epic\d+", file_path.lower()):
                    node_type = NodeType.EPIC

                # Create or update the node
                title = (
                    metadata.get("title")
                    or os.path.basename(file_path).replace(".md", "").replace("_", " ").title()
                )

                existing_node = self.get_node(node_id)
                if existing_node:
                    self.update_node(
                        node_id,
                        name=title,
                        tags=metadata.get("tags", []),
                        content_summary=metadata.get("summary"),
                        metadata={
                            "epic": metadata.get("epic"),
                            "related_files": metadata.get("related_files", []),
                            "concepts": metadata.get("concepts", []),
                            "models": metadata.get("models", []),
                        },
                        updated_at=datetime.now(),
                    )
                else:
                    node = DocumentationNode(
                        id=node_id,
                        name=title,
                        node_type=node_type,
                        file_path=file_path,
                        tags=metadata.get("tags", []),
                        content_summary=metadata.get("summary"),
                        metadata={
                            "epic": metadata.get("epic"),
                            "related_files": metadata.get("related_files", []),
                            "concepts": metadata.get("concepts", []),
                            "models": metadata.get("models", []),
                        },
                    )
                    self.add_node(node)

                # Create concept nodes for each concept
                for concept in metadata.get("concepts", []):
                    concept_id = f"concept_{concept.lower().replace(' ', '_')}"
                    if concept_id not in self.nodes:
                        concept_node = DocumentationNode(
                            id=concept_id,
                            name=concept,
                            node_type=NodeType.CONCEPT,
                            tags=["concept"],
                        )
                        self.add_node(concept_node)

                    # Add edge from document to concept
                    edge = DocumentationEdge(
                        source_id=node_id, target_id=concept_id, edge_type=EdgeType.REFERENCES
                    )
                    try:
                        self.add_edge(edge)
                    except ValueError:
                        # Edge might already exist
                        pass

                # Create model nodes for each model
                for model in metadata.get("models", []):
                    model_id = f"model_{model.lower()}"
                    if model_id not in self.nodes:
                        model_node = DocumentationNode(
                            id=model_id, name=model, node_type=NodeType.MODEL, tags=["model"]
                        )
                        self.add_node(model_node)

                    # Add edge from document to model
                    edge = DocumentationEdge(
                        source_id=node_id, target_id=model_id, edge_type=EdgeType.DOCUMENTS
                    )
                    try:
                        self.add_edge(edge)
                    except ValueError:
                        # Edge might already exist
                        pass

                # Create epic nodes if applicable
                if metadata.get("epic"):
                    epic_id = f"epic_{metadata['epic'].lower().replace(' ', '_')}"
                    if epic_id not in self.nodes:
                        epic_node = DocumentationNode(
                            id=epic_id,
                            name=metadata["epic"],
                            node_type=NodeType.EPIC,
                            tags=["epic"],
                        )
                        self.add_node(epic_node)

                    # Add edge from document to epic
                    edge = DocumentationEdge(
                        source_id=node_id, target_id=epic_id, edge_type=EdgeType.PART_OF
                    )
                    try:
                        self.add_edge(edge)
                    except ValueError:
                        # Edge might already exist
                        pass

            except Exception as e:
                logger.error(f"Error processing {file_path}: {e}")

        # Now create relationships between documents
        self._create_document_relationships()

    def _create_document_relationships(self) -> None:
        """Create relationships between documents based on related files, concepts, etc."""
        # For each node, check its related files and create relationships
        for node_id, node in self.nodes.items():
            if node.node_type != NodeType.DOCUMENT:
                continue

            related_files = node.metadata.get("related_files", [])
            for related_file in related_files:
                # Find nodes that might match this related file
                for other_id, other_node in self.nodes.items():
                    if other_id == node_id:
                        continue

                    if (
                        other_node.file_path
                        and os.path.basename(other_node.file_path) == related_file
                    ):
                        # Create a relationship
                        edge = DocumentationEdge(
                            source_id=node_id, target_id=other_id, edge_type=EdgeType.REFERENCES
                        )
                        try:
                            self.add_edge(edge)
                        except ValueError:
                            # Edge might already exist
                            pass

            # Connect documents that share concepts
            if "concepts" in node.metadata:
                node_concepts = set(node.metadata["concepts"])
                for other_id, other_node in self.nodes.items():
                    if other_id == node_id or other_node.node_type != NodeType.DOCUMENT:
                        continue

                    other_concepts = set(other_node.metadata.get("concepts", []))
                    common_concepts = node_concepts.intersection(other_concepts)

                    if common_concepts:
                        # Create a relationship with weight based on number of common concepts
                        edge = DocumentationEdge(
                            source_id=node_id,
                            target_id=other_id,
                            edge_type=EdgeType.RELATED_TO,
                            weight=len(common_concepts)
                            / max(len(node_concepts), len(other_concepts)),
                        )
                        try:
                            self.add_edge(edge)
                        except ValueError:
                            # Edge might already exist
                            pass

    def generate_graph_visualization(self, output_file: str, format: str = "graphviz") -> None:
        """Generate a visualization of the knowledge graph."""
        if format != "graphviz":
            raise ValueError(f"Unsupported visualization format: {format}")

        try:
            import graphviz

            # Create a new graphviz Digraph
            dot = graphviz.Digraph(comment="Documentation Knowledge Graph")

            # Add nodes
            for node_id, node in self.nodes.items():
                # Define node attributes based on node type
                attrs = {"label": node.name, "shape": "box"}

                if node.node_type == NodeType.DOCUMENT:
                    attrs["color"] = "blue"
                    attrs["style"] = "filled"
                    attrs["fillcolor"] = "lightblue"
                elif node.node_type == NodeType.CONCEPT:
                    attrs["color"] = "green"
                    attrs["style"] = "filled"
                    attrs["fillcolor"] = "lightgreen"
                    attrs["shape"] = "ellipse"
                elif node.node_type == NodeType.MODEL:
                    attrs["color"] = "red"
                    attrs["style"] = "filled"
                    attrs["fillcolor"] = "lightpink"
                elif node.node_type == NodeType.EPIC:
                    attrs["color"] = "purple"
                    attrs["style"] = "filled"
                    attrs["fillcolor"] = "lavender"
                    attrs["shape"] = "hexagon"
                elif node.node_type == NodeType.API:
                    attrs["color"] = "orange"
                    attrs["style"] = "filled"
                    attrs["fillcolor"] = "lightyellow"
                elif node.node_type == NodeType.IMPLEMENTATION:
                    attrs["color"] = "brown"
                    attrs["style"] = "filled"
                    attrs["fillcolor"] = "wheat"

                dot.node(node_id, **attrs)

            # Add edges
            for edge in self.edges:
                # Define edge attributes based on edge type
                attrs = {"label": edge.edge_type}

                if edge.edge_type == EdgeType.REFERENCES:
                    attrs["color"] = "blue"
                elif edge.edge_type == EdgeType.PART_OF:
                    attrs["color"] = "red"
                    attrs["style"] = "bold"
                elif edge.edge_type == EdgeType.RELATED_TO:
                    attrs["color"] = "green"
                    attrs["style"] = "dashed"

                # Use weight to influence edge thickness
                if edge.weight != 1.0:
                    attrs["penwidth"] = str(0.5 + edge.weight * 2)

                dot.edge(edge.source_id, edge.target_id, **attrs)

            # Render the graph
            dot.render(output_file, format="png", cleanup=True)
            logger.info(f"Generated graph visualization at {output_file}.png")

        except ImportError:
            logger.error("Could not generate visualization - graphviz Python package not installed")
        except Exception as e:
            logger.error(f"Error generating graph visualization: {e}")

    def generate_markdown_report(self, output_file: str) -> None:
        """Generate a markdown report of the knowledge graph."""
        try:
            with open(output_file, "w") as f:
                f.write("# Documentation Knowledge Graph Report\n\n")
                f.write(f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

                # Summary statistics
                f.write("## Summary\n\n")
                f.write(f"- **Total Nodes**: {len(self.nodes)}\n")
                f.write(f"- **Total Edges**: {len(self.edges)}\n\n")

                # Node statistics by type
                node_types = {}
                for node in self.nodes.values():
                    if node.node_type not in node_types:
                        node_types[node.node_type] = 0
                    node_types[node.node_type] += 1

                f.write("### Node Types\n\n")
                for node_type, count in sorted(
                    node_types.items(), key=lambda x: x[1], reverse=True
                ):
                    f.write(f"- **{node_type}**: {count}\n")
                f.write("\n")

                # Edge statistics by type
                edge_types = {}
                for edge in self.edges:
                    if edge.edge_type not in edge_types:
                        edge_types[edge.edge_type] = 0
                    edge_types[edge.edge_type] += 1

                f.write("### Edge Types\n\n")
                for edge_type, count in sorted(
                    edge_types.items(), key=lambda x: x[1], reverse=True
                ):
                    f.write(f"- **{edge_type}**: {count}\n")
                f.write("\n")

                # Document sections
                if NodeType.DOCUMENT in node_types:
                    f.write("## Documents\n\n")
                    documents = [
                        node for node in self.nodes.values() if node.node_type == NodeType.DOCUMENT
                    ]
                    for doc in sorted(documents, key=lambda x: x.name):
                        f.write(f"### {doc.name}\n\n")

                        if doc.content_summary:
                            f.write(f"{doc.content_summary}\n\n")

                        if doc.file_path:
                            f.write(f"**File**: `{doc.file_path}`\n\n")

                        if doc.tags:
                            f.write(f"**Tags**: {', '.join(doc.tags)}\n\n")

                        # Related documents
                        outgoing = self.get_outgoing_edges(doc.id)
                        if outgoing:
                            f.write("**Relationships**:\n\n")
                            for edge in outgoing:
                                target = self.get_node(edge.target_id)
                                if target:
                                    f.write(
                                        f"- {edge.edge_type.replace('_', ' ').title()} [{target.name}]\n"
                                    )
                            f.write("\n")

                # Concept sections
                if NodeType.CONCEPT in node_types:
                    f.write("## Concepts\n\n")
                    concepts = [
                        node for node in self.nodes.values() if node.node_type == NodeType.CONCEPT
                    ]
                    for concept in sorted(concepts, key=lambda x: x.name):
                        f.write(f"### {concept.name}\n\n")

                        # Documents that reference this concept
                        incoming = self.get_incoming_edges(concept.id)
                        if incoming:
                            f.write("**Referenced by**:\n\n")
                            for edge in incoming:
                                source = self.get_node(edge.source_id)
                                if source and source.node_type == NodeType.DOCUMENT:
                                    f.write(
                                        f"- [{source.name}]({os.path.relpath(source.file_path) if source.file_path else '#'})\n"
                                    )
                            f.write("\n")

                # Epic sections
                if NodeType.EPIC in node_types:
                    f.write("## Epics\n\n")
                    epics = [
                        node for node in self.nodes.values() if node.node_type == NodeType.EPIC
                    ]
                    for epic in sorted(epics, key=lambda x: x.name):
                        f.write(f"### {epic.name}\n\n")

                        # Documents that are part of this epic
                        incoming = self.get_incoming_edges(epic.id)
                        related_docs = []
                        for edge in incoming:
                            source = self.get_node(edge.source_id)
                            if source and source.node_type == NodeType.DOCUMENT:
                                related_docs.append(source)

                        if related_docs:
                            f.write("**Documents**:\n\n")
                            for doc in sorted(related_docs, key=lambda x: x.name):
                                f.write(
                                    f"- [{doc.name}]({os.path.relpath(doc.file_path) if doc.file_path else '#'})\n"
                                )
                            f.write("\n")

                logger.info(f"Generated markdown report at {output_file}")

        except Exception as e:
            logger.error(f"Error generating markdown report: {e}")


# Create a singleton instance
knowledge_graph = DocumentationKnowledgeGraph()


def get_knowledge_graph() -> DocumentationKnowledgeGraph:
    """Get the singleton instance of the knowledge graph."""
    return knowledge_graph
