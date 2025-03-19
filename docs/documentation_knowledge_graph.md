# Documentation Knowledge Graph System

This document describes the Documentation Knowledge Graph system, which helps interconnect and navigate the project's documentation, code, and conceptual elements.

## Overview

The Documentation Knowledge Graph represents documentation and related elements (concepts, models, epics, etc.) as a network of interconnected nodes. This helps in:

1. Discovering relationships between different pieces of documentation
2. Finding conceptually related documents
3. Navigating across documentation based on semantic connections
4. Creating visualizations of documentation relationships
5. Improving documentation discoverability and reducing duplication

## Table of Contents

- [Key Concepts](#key-concepts)
- [Node Types](#node-types)
- [Relationship Types](#relationship-types)
- [Command-Line Interface](#command-line-interface)
- [Integration with Documentation Workflow](#integration-with-documentation-workflow)
- [Best Practices](#best-practices)
- [System Setup](#system-setup)
- [Future Enhancements](#future-enhancements)

## Key Concepts

### Knowledge Graph

A knowledge graph is a network of entities (nodes) and their relationships (edges). In our context:

- **Nodes** represent documentation artifacts, concepts, ML models, epics, etc.
- **Edges** represent relationships between nodes (references, dependencies, etc.)
- **Properties** are additional metadata attached to nodes and edges

### Semantic Extraction

The system automatically extracts semantic information from documentation:

- Document titles, headings, and summaries
- References to concepts (bold/emphasized terms)
- References to other documents or code files
- References to ML models and techniques
- Tags and categorization information

### Graph Queries

You can query the knowledge graph to find:

- Documents related to specific concepts
- All documents within an epic
- Documentation that references a specific model
- Conceptually related documents, even if not explicitly linked

## Node Types

The knowledge graph includes different types of nodes:

| Node Type | Description |
|-----------|-------------|
| `document` | A markdown documentation file |
| `concept` | A specific concept or term used across documentation |
| `model` | An ML model or technique |
| `epic` | A project epic grouping related work |
| `api` | API documentation |
| `implementation` | Implementation documentation |
| `user_guide` | User guide or tutorial |
| `code_module` | A module in the codebase |
| `test` | A test file or test suite |
| `ml_technique` | A specific ML technique or approach |
| `algorithm` | A specific algorithm |

## Relationship Types

Nodes can be connected by various relationship types:

| Relationship Type | Description |
|-------------------|-------------|
| `references` | Document references another document, concept, or code |
| `implements` | Document describes implementation of a concept or model |
| `explains` | Document explains a concept or model |
| `part_of` | Document is part of a larger group (e.g., epic) |
| `depends_on` | Document depends on another document |
| `tested_by` | Element is tested by specific tests |
| `uses` | Document uses a concept, model, or technique |
| `extends` | Document extends another document |
| `related_to` | Documents are semantically related |
| `derived_from` | Document is derived from another document |
| `documented_by` | Code is documented by a specific document |

## Command-Line Interface

The documentation knowledge graph system provides a command-line interface for interacting with the graph:

### Getting Started

```bash
# Display help
python scripts/docs_knowledge_cli.py --help

# List all commands
python scripts/docs_knowledge_cli.py
```

### Scanning Documentation

```bash
# Scan docs directory
python scripts/docs_knowledge_cli.py scan docs

# Scan a specific directory
python scripts/docs_knowledge_cli.py scan app/ml
```

### Querying the Graph

```bash
# Free text search
python scripts/docs_knowledge_cli.py query --search "time series"

# Filter by node type
python scripts/docs_knowledge_cli.py query --node-type "concept"

# Filter by tags
python scripts/docs_knowledge_cli.py query --tags "model,evaluation"

# Combined search
python scripts/docs_knowledge_cli.py query --search "prediction" --node-type "document" --tags "ml"
```

### Finding Related Nodes

```bash
# Find nodes related to a specific node
python scripts/docs_knowledge_cli.py related <node_id>

# Increase search depth
python scripts/docs_knowledge_cli.py related <node_id> --depth 2
```

### Getting Node Information

```bash
# Get detailed information about a node
python scripts/docs_knowledge_cli.py info <node_id>
```

### Generating Visualizations and Reports

```bash
# Generate a visualization
python scripts/docs_knowledge_cli.py visualize --output docs_graph

# Generate a markdown report
python scripts/docs_knowledge_cli.py report --output docs/knowledge_graph_report.md
```

### Viewing Statistics

```bash
# View knowledge graph statistics
python scripts/docs_knowledge_cli.py stats
```

## Integration with Documentation Workflow

### Document Tagging

To improve the knowledge graph's effectiveness, consider adding metadata to your markdown documents:

```markdown
# Document Title

Tags: tag1, tag2, tag3

This document explains **important concepts** and references the `file_name.py` module.

## Epic 1: Component Name

...
```

### Explicit Concept Highlighting

Use bold text to mark important concepts in your documentation:

```markdown
The **time-series forecasting** approach uses **ARIMA** and **seasonal decomposition**.
```

### File References

Use backticks to reference code files:

```markdown
The implementation is in `app/ml/time_series_model.py`.
```

### Regular Scanning

After adding or updating documentation, scan the documentation directories:

```bash
python scripts/docs_knowledge_cli.py scan docs
```

## Best Practices

### Document Organization

1. **Consistent Structure**: Use consistent document structure with clear headings
2. **Explicit Concepts**: Mark important concepts with bold text
3. **Clear References**: Reference related documents and code files
4. **Metadata**: Include tags, epic information, and other metadata

### Knowledge Graph Usage

1. **Regular Updates**: Scan documentation whenever significant changes are made
2. **Cross-Linking**: Use the graph to identify missing cross-references
3. **Gap Analysis**: Use the graph to identify documentation gaps
4. **Conceptual Mapping**: Regularly review concept nodes to ensure consistency

## System Setup

The documentation knowledge graph system can be set up using the provided setup script:

```bash
python scripts/setup_knowledge_graph.py
```

This script will:
1. Create necessary directories for the knowledge graph
2. Scan the documentation directories
3. Generate an initial visualization
4. Generate an initial report

### Setup Options

```bash
# Skip visualization generation
python scripts/setup_knowledge_graph.py --no-visualize

# Skip report generation
python scripts/setup_knowledge_graph.py --no-report
```

### System Requirements

The documentation knowledge graph system requires:
- Python 3.7+
- Graphviz (optional, for visualizations)
- Access to the filesystem for storing graph databases and reports

## Future Enhancements

We plan to enhance the documentation knowledge graph system with:

- Web-based visualization and exploration interface
- Integration with search functionality
- Automated documentation gap analysis
- Concept consistency checking
- Documentation health metrics
- Automated documentation organization recommendations 