#!/usr/bin/env python3
"""
Epic 4 Knowledge Graph Builder

This script builds a knowledge graph specifically for Epic 4: Dynamic Schedule Rebalancing,
connecting concepts, research, implementation details, and documentation.
"""

import os
import sys
import json
import re
import glob
import networkx as nx
import matplotlib.pyplot as plt
import io
import base64
from typing import Dict, List, Set, Tuple, Any, Optional
from collections import defaultdict
import argparse

# Add project root to path to enable imports
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.append(ROOT_DIR)


class Epic4KnowledgeGraph:
    """Builder for Epic 4 knowledge graph."""

    # Node types
    TYPE_ML_TECHNIQUE = "ml_technique"
    TYPE_RESEARCH_PAPER = "research_paper"
    TYPE_CODE_MODULE = "code_module"
    TYPE_DOCUMENTATION = "documentation"
    TYPE_CONCEPT = "concept"
    TYPE_STORY = "story"
    TYPE_REQUIREMENT = "requirement"

    # Edge types
    EDGE_IMPLEMENTS = "implements"
    EDGE_REFERENCES = "references"
    EDGE_DEPENDS_ON = "depends_on"
    EDGE_DOCUMENTS = "documents"
    EDGE_APPLIES = "applies"
    EDGE_RELATED = "related_to"
    EDGE_USES = "uses"

    def __init__(self, output_dir: str = None):
        """Initialize the knowledge graph builder."""
        self.output_dir = output_dir or os.path.join(ROOT_DIR, "docs")
        os.makedirs(self.output_dir, exist_ok=True)

        # Initialize the graph
        self.graph = nx.DiGraph()

        # Node data storage
        self.nodes = {}

        # Node color mapping
        self.node_colors = {
            self.TYPE_ML_TECHNIQUE: "#e41a1c",  # Red
            self.TYPE_RESEARCH_PAPER: "#377eb8",  # Blue
            self.TYPE_CODE_MODULE: "#4daf4a",  # Green
            self.TYPE_DOCUMENTATION: "#984ea3",  # Purple
            self.TYPE_CONCEPT: "#ff7f00",  # Orange
            self.TYPE_STORY: "#ffff33",  # Yellow
            self.TYPE_REQUIREMENT: "#a65628",  # Brown
        }

        # Epic 4 story IDs
        self.epic4_stories = ["ADHD-20", "ADHD-17", "ADHD-18", "ADHD-19"]

        # Epic 4 core concepts
        self.epic4_concepts = [
            ("reinforcement_learning", "Reinforcement Learning for scheduling"),
            ("progress_monitoring", "Real-time progress monitoring"),
            ("opportunity_cost", "Opportunity cost calculation"),
            ("circadian_aware", "Circadian-aware scheduling"),
            ("dynamic_rebalancing", "Dynamic schedule rebalancing"),
            ("threshold_based_policy", "Threshold-based policy optimization"),
            ("momentum_aware", "Momentum-aware task scheduling"),
            ("ethical_ai", "Ethical AI considerations"),
            ("ultradian_cycles", "Ultradian cycle alignment"),
            ("chronotype_detection", "Personalized chronotype detection"),
            ("federated_learning", "Federated learning privacy"),
            ("adhd_behavior", "ADHD behavioral patterns"),
        ]

        # Epic 4 research papers
        self.epic4_research = [
            (
                "journal_attention_disorders_2025",
                "Journal of Attention Disorders (2025) - Reinforcement Learning for ADHD",
                "Demonstrates threshold-based RL architectures outperform traditional calendar approaches by 23% in task adherence metrics",
            ),
            (
                "pmc5701950",
                "PMC5701950 - ADHD Performance Decay",
                "Shows ADHD performance declines 37% faster than neurotypical baselines during sustained attention tasks",
            ),
            (
                "icml_2025",
                "ICML 2025 Workshop on Causal ML for Health",
                "Emphasizes partial reinforcement schedules with dynamic reward shaping for ADHD interventions",
            ),
            (
                "neurips_2025",
                "NeurIPS 2025 Workshop on Equitable AI",
                "Recommends adversarial debiasing to prevent schedule optimization bias toward hyperfocus-prone individuals",
            ),
            (
                "journal_circadian_rhythms_2025",
                "Journal of Circadian Rhythms (2025)",
                "Identifies ultradian cycle alignment as critical for ADHD populations, with 72% improved task completion",
            ),
            (
                "nature_digital_medicine",
                "Nature Digital Medicine (2025)",
                "Shows 40 lux blue light exposure during transitions improves task-switching efficiency by 18% in ADHD cohorts",
            ),
            (
                "rlc_2025",
                "Reinforcement Learning Conference (2025)",
                "Presents threshold-based policy optimization for behavioral interventions reducing cognitive load",
            ),
        ]

    def add_node(
        self,
        node_id: str,
        node_type: str,
        name: str,
        description: str = None,
        attributes: Dict = None,
    ) -> None:
        """
        Add a node to the knowledge graph.

        Args:
            node_id: Unique identifier for the node
            node_type: Type of node (technique, paper, module, etc.)
            name: Display name for the node
            description: Optional description
            attributes: Optional additional attributes
        """
        # Create the node in networkx
        if not self.graph.has_node(node_id):
            node_data = {
                "id": node_id,
                "type": node_type,
                "name": name,
                "description": description or "",
            }

            # Add any additional attributes
            if attributes:
                node_data.update(attributes)

            # Store the node data
            self.nodes[node_id] = node_data

            # Add to networkx graph
            self.graph.add_node(node_id, **node_data)

    def add_edge(
        self,
        source_id: str,
        target_id: str,
        edge_type: str,
        weight: float = 1.0,
        attributes: Dict = None,
    ) -> None:
        """
        Add an edge between two nodes.

        Args:
            source_id: Source node ID
            target_id: Target node ID
            edge_type: Type of relationship
            weight: Edge weight
            attributes: Optional additional attributes
        """
        # Ensure both nodes exist
        if source_id not in self.graph.nodes or target_id not in self.graph.nodes:
            return

        # Create edge data
        edge_data = {"type": edge_type, "weight": weight}

        # Add any additional attributes
        if attributes:
            edge_data.update(attributes)

        # Add to networkx graph
        self.graph.add_edge(source_id, target_id, **edge_data)

    def build_base_graph(self) -> None:
        """Build the base knowledge graph for Epic 4."""
        # Add epic node
        self.add_node(
            "epic_4",
            self.TYPE_CONCEPT,
            "Epic 4: Dynamic Schedule Rebalancing",
            "Implementation of dynamic schedule rebalancing for ADHD/neurodiverse users",
        )

        # Add story nodes
        stories = {
            "ADHD-20": "Create real-time progress monitoring and adaptive adjustment",
            "ADHD-17": "Implement reinforcement learning for adaptive scheduling",
            "ADHD-18": "Create opportunity cost calculator for task rescheduling",
            "ADHD-19": "Implement circadian-aware schedule adjustment system",
        }

        for story_id, description in stories.items():
            self.add_node(
                f"story_{story_id.lower().replace('-', '_')}",
                self.TYPE_STORY,
                story_id,
                description,
            )

            # Connect to epic
            self.add_edge(
                f"story_{story_id.lower().replace('-', '_')}", "epic_4", self.EDGE_IMPLEMENTS
            )

        # Add concept nodes
        for concept_id, description in self.epic4_concepts:
            self.add_node(
                f"concept_{concept_id}",
                self.TYPE_CONCEPT,
                concept_id.replace("_", " ").title(),
                description,
            )

            # Connect to epic
            self.add_edge(f"concept_{concept_id}", "epic_4", self.EDGE_RELATED)

        # Add research nodes
        for paper_id, title, description in self.epic4_research:
            self.add_node(f"research_{paper_id}", self.TYPE_RESEARCH_PAPER, title, description)

            # Connect to epic
            self.add_edge(f"research_{paper_id}", "epic_4", self.EDGE_REFERENCES)

        # Connect stories to concepts
        story_concept_map = {
            "story_adhd_20": ["concept_progress_monitoring", "concept_dynamic_rebalancing"],
            "story_adhd_17": [
                "concept_reinforcement_learning",
                "concept_threshold_based_policy",
                "concept_momentum_aware",
                "concept_ethical_ai",
            ],
            "story_adhd_18": ["concept_opportunity_cost", "concept_dynamic_rebalancing"],
            "story_adhd_19": [
                "concept_circadian_aware",
                "concept_ultradian_cycles",
                "concept_chronotype_detection",
            ],
        }

        for story_id, concepts in story_concept_map.items():
            for concept_id in concepts:
                self.add_edge(story_id, concept_id, self.EDGE_IMPLEMENTS)

        # Connect concepts to research
        concept_research_map = {
            "concept_reinforcement_learning": [
                "research_journal_attention_disorders_2025",
                "research_icml_2025",
                "research_rlc_2025",
            ],
            "concept_momentum_aware": ["research_pmc5701950"],
            "concept_ethical_ai": ["research_neurips_2025"],
            "concept_ultradian_cycles": ["research_journal_circadian_rhythms_2025"],
            "concept_chronotype_detection": ["research_journal_circadian_rhythms_2025"],
            "concept_threshold_based_policy": ["research_rlc_2025"],
        }

        for concept_id, papers in concept_research_map.items():
            for paper_id in papers:
                self.add_edge(concept_id, paper_id, self.EDGE_REFERENCES)

    def scan_documentation(self) -> None:
        """Scan project documentation to add to the knowledge graph."""
        # Find all markdown files in the docs directory
        doc_files = glob.glob(os.path.join(ROOT_DIR, "docs", "**", "*.md"), recursive=True)

        for doc_file in doc_files:
            # Extract relative path for node ID
            rel_path = os.path.relpath(doc_file, ROOT_DIR)
            node_id = f"doc_{rel_path.replace('/', '_').replace('.', '_')}"

            # Read file to extract title and scan content
            try:
                with open(doc_file, "r", encoding="utf-8") as f:
                    content = f.read()

                # Try to extract title (first # heading)
                title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
                title = title_match.group(1) if title_match else os.path.basename(doc_file)

                # Add as documentation node
                self.add_node(
                    node_id, self.TYPE_DOCUMENTATION, title, f"Documentation file: {rel_path}"
                )

                # Check for mentions of Epic 4 concepts
                for concept_id, _ in self.epic4_concepts:
                    concept_name = concept_id.replace("_", " ")
                    if re.search(rf"\b{concept_name}\b", content, re.IGNORECASE):
                        self.add_edge(node_id, f"concept_{concept_id}", self.EDGE_DOCUMENTS)

                # Check for mentions of research papers
                for paper_id, title, _ in self.epic4_research:
                    # Extract key terms from the title for matching
                    key_terms = title.split(" - ")[0].lower()
                    if re.search(rf"\b{key_terms}\b", content, re.IGNORECASE):
                        self.add_edge(node_id, f"research_{paper_id}", self.EDGE_REFERENCES)

                # Check for mentions of stories
                for story_id in self.epic4_stories:
                    if re.search(rf"\b{story_id}\b", content):
                        self.add_edge(
                            node_id,
                            f"story_{story_id.lower().replace('-', '_')}",
                            self.EDGE_DOCUMENTS,
                        )

            except Exception as e:
                print(f"Error processing documentation file {doc_file}: {e}")

    def scan_code(self) -> None:
        """Scan project code to add to the knowledge graph."""
        # Find potential Python modules for Epic 4
        py_files = []

        # Look in app/ml directory
        py_files.extend(
            glob.glob(os.path.join(ROOT_DIR, "app", "ml", "**", "*.py"), recursive=True)
        )

        # Look in app/services directory
        py_files.extend(
            glob.glob(os.path.join(ROOT_DIR, "app", "services", "**", "*.py"), recursive=True)
        )

        for py_file in py_files:
            # Extract relative path for node ID
            rel_path = os.path.relpath(py_file, ROOT_DIR)
            node_id = f"code_{rel_path.replace('/', '_').replace('.', '_')}"

            # Read file to extract docstring and scan content
            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()

                # Try to extract module docstring
                docstring_match = re.search(r'"""(.+?)"""', content, re.DOTALL)
                description = (
                    docstring_match.group(1).strip()
                    if docstring_match
                    else "No description available"
                )

                # Use filename as title
                title = os.path.basename(py_file)

                # Add as code module node
                self.add_node(node_id, self.TYPE_CODE_MODULE, title, description)

                # Check for mentions of Epic 4 concepts
                for concept_id, _ in self.epic4_concepts:
                    concept_name = concept_id.replace("_", " ")
                    if re.search(rf"\b{concept_name}\b", content, re.IGNORECASE):
                        self.add_edge(node_id, f"concept_{concept_id}", self.EDGE_IMPLEMENTS)

                # Check for class names that might match concepts
                for concept_id, _ in self.epic4_concepts:
                    # Convert snake_case to CamelCase for class name matching
                    camel_case = "".join(word.capitalize() for word in concept_id.split("_"))
                    if re.search(rf"class\s+\w*{camel_case}\w*", content):
                        self.add_edge(
                            node_id, f"concept_{concept_id}", self.EDGE_IMPLEMENTS, weight=2.0
                        )

            except Exception as e:
                print(f"Error processing code file {py_file}: {e}")

    def analyze_gaps(self) -> List[Dict[str, Any]]:
        """
        Analyze knowledge graph for gaps in implementation or documentation.

        Returns:
            List of gap descriptions
        """
        gaps = []

        # Check for concepts without code implementation
        for concept_id, description in self.epic4_concepts:
            concept_node = f"concept_{concept_id}"

            # Find code nodes that implement this concept
            implementing_code = [
                n
                for n in self.graph.predecessors(concept_node)
                if n in self.nodes and self.nodes[n]["type"] == self.TYPE_CODE_MODULE
            ]

            if not implementing_code:
                gaps.append(
                    {
                        "type": "implementation_gap",
                        "concept": concept_id.replace("_", " ").title(),
                        "description": f"No code found implementing the concept: {description}",
                    }
                )

        # Check for research papers without corresponding documentation
        for paper_id, title, _ in self.epic4_research:
            paper_node = f"research_{paper_id}"

            # Find documentation that references this research
            referencing_docs = [
                n
                for n in self.graph.predecessors(paper_node)
                if n in self.nodes and self.nodes[n]["type"] == self.TYPE_DOCUMENTATION
            ]

            if not referencing_docs:
                gaps.append(
                    {
                        "type": "documentation_gap",
                        "research": title,
                        "description": f"No documentation found referencing the research: {title}",
                    }
                )

        # Check for stories without documentation
        for story_id in self.epic4_stories:
            story_node = f"story_{story_id.lower().replace('-', '_')}"

            # Find documentation for this story
            story_docs = [
                n
                for n in self.graph.predecessors(story_node)
                if n in self.nodes and self.nodes[n]["type"] == self.TYPE_DOCUMENTATION
            ]

            if not story_docs:
                gaps.append(
                    {
                        "type": "story_documentation_gap",
                        "story": story_id,
                        "description": f"No documentation found for story: {story_id}",
                    }
                )

        return gaps

    def visualize_graph(self) -> str:
        """
        Visualize the knowledge graph and return as a base64 encoded image.

        Returns:
            Base64 encoded PNG image of the graph visualization
        """
        plt.figure(figsize=(12, 10))

        # Create node color map
        node_colors = [
            self.node_colors.get(self.nodes[node]["type"], "#999999") for node in self.graph.nodes()
        ]

        # Use spring layout for better visualization
        pos = nx.spring_layout(self.graph, k=0.5, iterations=50)

        # Draw nodes
        nx.draw_networkx_nodes(self.graph, pos, node_size=700, node_color=node_colors, alpha=0.8)

        # Draw edges
        edge_types = set(nx.get_edge_attributes(self.graph, "type").values())
        for edge_type in edge_types:
            edges = [
                (u, v) for u, v, d in self.graph.edges(data=True) if d.get("type") == edge_type
            ]
            nx.draw_networkx_edges(
                self.graph,
                pos,
                edgelist=edges,
                width=1.5,
                alpha=0.6,
                edge_color=plt.cm.tab10(list(edge_types).index(edge_type) % 10),
            )

        # Draw node labels
        nx.draw_networkx_labels(
            self.graph,
            pos,
            {n: self.nodes[n]["name"] for n in self.graph.nodes()},
            font_size=10,
            font_weight="bold",
        )

        # Create legend for node types
        legend_elements = [
            plt.Line2D(
                [0],
                [0],
                marker="o",
                color="w",
                markerfacecolor=color,
                markersize=10,
                label=node_type.replace("_", " ").title(),
            )
            for node_type, color in self.node_colors.items()
        ]

        plt.legend(handles=legend_elements, loc="upper right")
        plt.axis("off")
        plt.title("Epic 4 Knowledge Graph")
        plt.tight_layout()

        # Convert to base64
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=150)
        buf.seek(0)

        # Close the plot to free memory
        plt.close()

        return base64.b64encode(buf.read()).decode("utf-8")

    def generate_full_graph(self) -> nx.DiGraph:
        """
        Generate the full knowledge graph.

        Returns:
            The complete NetworkX graph
        """
        # Build base graph
        self.build_base_graph()

        # Scan documentation
        self.scan_documentation()

        # Scan code
        self.scan_code()

        return self.graph

    def generate_ml_subgraph(self) -> nx.DiGraph:
        """
        Generate a subgraph focused on ML techniques.

        Returns:
            NetworkX subgraph containing ML techniques and directly related nodes
        """
        # Ensure full graph is built
        if len(self.graph.nodes) == 0:
            self.generate_full_graph()

        # Find all ML technique nodes
        ml_nodes = [
            n
            for n in self.graph.nodes
            if n in self.nodes
            and (
                self.nodes[n]["type"] == self.TYPE_ML_TECHNIQUE
                or (
                    self.nodes[n]["type"] == self.TYPE_CONCEPT
                    and any(
                        c in n
                        for c in ["reinforcement", "learning", "model", "neural", "algorithm"]
                    )
                )
            )
        ]

        # Add directly connected nodes
        connected_nodes = set(ml_nodes)
        for node in ml_nodes:
            connected_nodes.update(self.graph.predecessors(node))
            connected_nodes.update(self.graph.successors(node))

        # Create subgraph
        return self.graph.subgraph(connected_nodes).copy()

    def export_graph(self, filename: str = None) -> str:
        """
        Export the knowledge graph to a JSON file.

        Args:
            filename: Optional filename to save to

        Returns:
            Path to the exported file
        """
        if len(self.graph.nodes) == 0:
            self.generate_full_graph()

        # Convert NetworkX graph to JSON-serializable format
        graph_data = {"nodes": [], "edges": []}

        # Add nodes
        for node_id in self.graph.nodes:
            node_data = self.nodes[node_id].copy()
            graph_data["nodes"].append(node_data)

        # Add edges
        for source, target, data in self.graph.edges(data=True):
            edge_data = {
                "source": source,
                "target": target,
                "type": data.get("type", "related_to"),
                "weight": data.get("weight", 1.0),
            }
            graph_data["edges"].append(edge_data)

        # Generate filename if not provided
        if not filename:
            filename = os.path.join(self.output_dir, "epic4_knowledge_graph.json")

        # Write to file
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(graph_data, f, indent=2)

        print(f"Knowledge graph exported to {filename}")
        return filename

    def generate_report(self) -> str:
        """
        Generate a Markdown report of the knowledge graph.

        Returns:
            Markdown string of the report
        """
        # Ensure full graph is built
        if len(self.graph.nodes) == 0:
            self.generate_full_graph()

        # Generate visualization
        graph_image = self.visualize_graph()

        # Get gaps
        gaps = self.analyze_gaps()

        # Calculate statistics
        num_nodes = len(self.graph.nodes)
        num_edges = len(self.graph.edges)

        node_types = defaultdict(int)
        for node_id in self.graph.nodes:
            node_type = self.nodes[node_id]["type"]
            node_types[node_type] += 1

        edge_types = defaultdict(int)
        for _, _, data in self.graph.edges(data=True):
            edge_type = data.get("type", "related_to")
            edge_types[edge_type] += 1

        # Generate report
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        md = [
            f"# Epic 4 Knowledge Graph Report\n",
            f"**Generated:** {timestamp}\n\n",
            "## Overview\n\n",
            f"This knowledge graph connects concepts, research, code, and documentation ",
            f"for Epic 4: Dynamic Schedule Rebalancing.\n\n",
            f"**Total Nodes:** {num_nodes}  \n",
            f"**Total Connections:** {num_edges}\n\n",
            "### Node Distribution\n\n",
            "| Node Type | Count |\n",
            "|-----------|-------|\n",
        ]

        for node_type, count in sorted(node_types.items()):
            md.append(f"| {node_type.replace('_', ' ').title()} | {count} |\n")

        md.append("\n### Connection Types\n\n")
        md.append("| Connection Type | Count |\n")
        md.append("|----------------|-------|\n")

        for edge_type, count in sorted(edge_types.items()):
            md.append(f"| {edge_type.replace('_', ' ').title()} | {count} |\n")

        md.append("\n## Knowledge Graph Visualization\n\n")
        md.append(f"![Knowledge Graph](data:image/png;base64,{graph_image})\n\n")

        md.append("## Implementation Gaps\n\n")

        implementation_gaps = [g for g in gaps if g["type"] == "implementation_gap"]
        if implementation_gaps:
            for gap in implementation_gaps:
                md.append(f"- **{gap['concept']}**: {gap['description']}\n")
        else:
            md.append("*No implementation gaps identified.*\n")

        md.append("\n## Documentation Gaps\n\n")

        doc_gaps = [g for g in gaps if g["type"] == "documentation_gap"]
        if doc_gaps:
            for gap in doc_gaps:
                md.append(f"- **{gap['research']}**: {gap['description']}\n")
        else:
            md.append("*No documentation gaps identified.*\n")

        md.append("\n## Story Documentation Gaps\n\n")

        story_gaps = [g for g in gaps if g["type"] == "story_documentation_gap"]
        if story_gaps:
            for gap in story_gaps:
                md.append(f"- **{gap['story']}**: {gap['description']}\n")
        else:
            md.append("*No story documentation gaps identified.*\n")

        # Return the report content
        return "".join(md)

    def save_report(self, markdown_content: str) -> str:
        """
        Save report to a Markdown file.

        Args:
            markdown_content: Markdown content to save

        Returns:
            Path to the saved file
        """
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(self.output_dir, f"epic4_knowledge_graph_report_{timestamp}.md")

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)

        print(f"Report saved to {output_path}")
        return output_path


def main():
    """Main function to generate the Epic 4 knowledge graph and report."""
    parser = argparse.ArgumentParser(description="Generate Epic 4 knowledge graph and report")
    parser.add_argument("--output-dir", help="Output directory for reports and exports")
    parser.add_argument("--export", action="store_true", help="Export graph to JSON")
    parser.add_argument("--ml-subgraph", action="store_true", help="Generate ML-specific subgraph")

    args = parser.parse_args()

    kg = Epic4KnowledgeGraph(output_dir=args.output_dir)
    kg.generate_full_graph()

    # Generate and save report
    report = kg.generate_report()
    kg.save_report(report)

    # Export graph if requested
    if args.export:
        kg.export_graph()

    # Generate ML subgraph if requested
    if args.ml_subgraph:
        ml_graph = kg.generate_ml_subgraph()
        ml_graph_data = {"nodes": [], "edges": []}

        # Add nodes
        for node_id in ml_graph.nodes:
            ml_graph_data["nodes"].append(kg.nodes[node_id].copy())

        # Add edges
        for source, target, data in ml_graph.edges(data=True):
            edge_data = {
                "source": source,
                "target": target,
                "type": data.get("type", "related_to"),
                "weight": data.get("weight", 1.0),
            }
            ml_graph_data["edges"].append(edge_data)

        # Export ML subgraph
        ml_output_path = os.path.join(kg.output_dir, "epic4_ml_subgraph.json")
        with open(ml_output_path, "w", encoding="utf-8") as f:
            json.dump(ml_graph_data, f, indent=2)

        print(f"ML subgraph exported to {ml_output_path}")


if __name__ == "__main__":
    import datetime

    main()
