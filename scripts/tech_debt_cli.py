#!/usr/bin/env python3
"""
Technical Debt Management CLI Tool.

This script provides a command-line interface for interacting with the technical debt
management system. It allows for adding, querying, updating, and reporting on technical debt.
"""

import argparse
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any

# Add parent directory to path so we can import from app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils.tech_debt import (
    TechnicalDebtItem, 
    DebtCategory, 
    DebtSeverity, 
    DebtStatus,
    MLDebtSubcategory,
    get_debt_manager
)


def setup_parser() -> argparse.ArgumentParser:
    """Set up command line argument parser."""
    parser = argparse.ArgumentParser(
        description="Technical Debt Management CLI Tool",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Add command
    add_parser = subparsers.add_parser("add", help="Add a new technical debt item")
    add_parser.add_argument("--title", required=True, help="Title of the debt item")
    add_parser.add_argument("--description", required=True, help="Description of the debt item")
    add_parser.add_argument(
        "--category", 
        choices=[c.value for c in DebtCategory], 
        default=DebtCategory.CODE_QUALITY.value,
        help="Category of the debt item"
    )
    add_parser.add_argument(
        "--severity", 
        choices=[s.value for s in DebtSeverity], 
        default=DebtSeverity.MEDIUM.value,
        help="Severity of the debt item"
    )
    add_parser.add_argument(
        "--status", 
        choices=[s.value for s in DebtStatus], 
        default=DebtStatus.IDENTIFIED.value,
        help="Status of the debt item"
    )
    add_parser.add_argument("--file-path", help="File path associated with the debt item")
    add_parser.add_argument("--line-number", type=int, help="Line number associated with the debt item")
    add_parser.add_argument("--author", help="Author of the debt item (defaults to current user)")
    add_parser.add_argument("--tags", help="Comma-separated list of tags")
    add_parser.add_argument("--resolution-plan", help="Plan for resolving the debt")
    add_parser.add_argument("--effort", help="Estimated effort to resolve the debt (e.g., '2 days')")
    add_parser.add_argument("--impact", help="Impact of the debt on the project")
    add_parser.add_argument(
        "--subcategory", 
        choices=[s.value for s in MLDebtSubcategory], 
        help="ML-specific subcategory of the debt item"
    )
    
    # List command
    list_parser = subparsers.add_parser("list", help="List technical debt items")
    list_parser.add_argument(
        "--status", 
        choices=[s.value for s in DebtStatus], 
        help="Filter by status"
    )
    list_parser.add_argument(
        "--category",
        choices=[c.value for c in DebtCategory],
        help="Filter by category"
    )
    list_parser.add_argument(
        "--severity",
        choices=[s.value for s in DebtSeverity],
        help="Filter by severity"
    )
    list_parser.add_argument(
        "--subcategory",
        choices=[s.value for s in MLDebtSubcategory],
        help="Filter by ML subcategory"
    )
    list_parser.add_argument("--tags", help="Filter by comma-separated list of tags")
    list_parser.add_argument("--search", help="Search query for filtering items")
    list_parser.add_argument("--file-path", help="Filter by file path")
    list_parser.add_argument("--format", choices=["json", "human"], default="human", help="Output format")
    
    # Show command
    show_parser = subparsers.add_parser("show", help="Show details of a technical debt item")
    show_parser.add_argument("item_id", help="ID of the debt item to show")
    show_parser.add_argument("--format", choices=["json", "human"], default="human", help="Output format")
    
    # Update command
    update_parser = subparsers.add_parser("update", help="Update a technical debt item")
    update_parser.add_argument("item_id", help="ID of the debt item to update")
    update_parser.add_argument("--title", help="Title of the debt item")
    update_parser.add_argument("--description", help="Description of the debt item")
    update_parser.add_argument(
        "--category", 
        choices=[c.value for c in DebtCategory], 
        help="Category of the debt item"
    )
    update_parser.add_argument(
        "--severity", 
        choices=[s.value for s in DebtSeverity], 
        help="Severity of the debt item"
    )
    update_parser.add_argument(
        "--status", 
        choices=[s.value for s in DebtStatus], 
        help="Status of the debt item"
    )
    update_parser.add_argument("--file-path", help="File path associated with the debt item")
    update_parser.add_argument("--line-number", type=int, help="Line number associated with the debt item")
    update_parser.add_argument("--tags", help="Comma-separated list of tags")
    update_parser.add_argument("--resolution-plan", help="Plan for resolving the debt")
    update_parser.add_argument("--effort", help="Estimated effort to resolve the debt (e.g., '2 days')")
    update_parser.add_argument("--impact", help="Impact of the debt on the project")
    update_parser.add_argument(
        "--subcategory", 
        choices=[s.value for s in MLDebtSubcategory], 
        help="ML-specific subcategory of the debt item"
    )
    
    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete a technical debt item")
    delete_parser.add_argument("item_id", help="ID of the debt item to delete")
    delete_parser.add_argument("--confirm", action="store_true", help="Confirm deletion without prompting")
    
    # Report command
    report_parser = subparsers.add_parser("report", help="Generate a technical debt report")
    report_parser.add_argument(
        "--format", 
        choices=["markdown", "json"], 
        default="markdown", 
        help="Output format"
    )
    report_parser.add_argument(
        "--group-by", 
        choices=["category", "severity", "status"], 
        help="Group items in the report"
    )
    report_parser.add_argument(
        "--include-resolved", 
        action="store_true", 
        help="Include resolved items in the report"
    )
    report_parser.add_argument(
        "--output", 
        help="Output file path (defaults to stdout)"
    )
    
    # Scan command
    scan_parser = subparsers.add_parser("scan", help="Scan a directory for technical debt comments in code")
    scan_parser.add_argument(
        "directory", 
        nargs="?", 
        default=".", 
        help="Directory to scan (defaults to current directory)"
    )
    scan_parser.add_argument(
        "--extensions", 
        help="Comma-separated list of file extensions to scan (defaults to common source code extensions)"
    )
    scan_parser.add_argument(
        "--auto-add", 
        action="store_true", 
        help="Automatically add found items to the database"
    )
    scan_parser.add_argument(
        "--format", 
        choices=["json", "human"], 
        default="human", 
        help="Output format"
    )
    
    # Metrics command
    metrics_parser = subparsers.add_parser("metrics", help="Get technical debt metrics")
    metrics_parser.add_argument(
        "--format", 
        choices=["json", "human"], 
        default="human", 
        help="Output format"
    )
    
    # Add comment command
    comment_parser = subparsers.add_parser("comment", help="Add a comment to a technical debt item")
    comment_parser.add_argument("item_id", help="ID of the debt item to comment on")
    comment_parser.add_argument("text", help="Comment text")
    comment_parser.add_argument("--author", help="Comment author (defaults to current user)")
    
    return parser


def handle_add(args) -> None:
    """Handle the 'add' command."""
    manager = get_debt_manager()
    
    # Parse line numbers
    line_numbers = None
    if args.line_number:
        line_numbers = [args.line_number]
    
    # Parse tags
    tags = []
    if args.tags:
        tags = [tag.strip() for tag in args.tags.split(",")]
    
    # Create and add the item
    item = TechnicalDebtItem(
        title=args.title,
        description=args.description,
        category=args.category,
        severity=args.severity,
        status=args.status,
        file_path=args.file_path,
        line_numbers=line_numbers,
        created_by=args.author,
        tags=tags,
        resolution_plan=args.resolution_plan,
        estimated_effort=args.effort,
        impact=args.impact,
        subcategory=args.subcategory
    )
    
    item_id = manager.add_item(item)
    print(f"Added technical debt item with ID: {item_id}")


def format_item_for_display(item: TechnicalDebtItem) -> str:
    """Format a debt item for human-readable display."""
    result = [
        f"ID: {item.id}",
        f"Title: {item.title}",
        f"Description: {item.description}",
        f"Category: {item.category.value}",
        f"Severity: {item.severity.value}",
        f"Status: {item.status.value}",
    ]
    
    if item.subcategory:
        result.append(f"Subcategory: {item.subcategory.value}")
    
    if item.file_path:
        result.append(f"File: {item.file_path}")
        if item.line_numbers:
            if isinstance(item.line_numbers, list):
                line_str = ", ".join(str(line) for line in item.line_numbers)
            else:
                line_str = f"{item.line_numbers[0]}-{item.line_numbers[1]}"
            result.append(f"Lines: {line_str}")
    
    if item.tags:
        result.append(f"Tags: {', '.join(item.tags)}")
    
    if item.impact:
        result.append(f"Impact: {item.impact}")
    
    if item.resolution_plan:
        result.append(f"Resolution Plan: {item.resolution_plan}")
    
    result.append(f"Created By: {item.created_by}")
    result.append(f"Created At: {item.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
    result.append(f"Updated At: {item.updated_at.strftime('%Y-%m-%d %H:%M:%S')}")
    
    if item.estimated_effort:
        result.append(f"Estimated Effort: {item.estimated_effort}")
    
    if hasattr(item, "comments") and item.comments:
        result.append("Comments:")
        for comment in item.comments:
            result.append(f"  - {comment['author']} ({comment['timestamp']}): {comment['text']}")
    
    return "\n".join(result)


def handle_list(args) -> None:
    """Handle the 'list' command."""
    manager = get_debt_manager()
    
    # Parse tags
    tags = None
    if args.tags:
        tags = [tag.strip() for tag in args.tags.split(",")]
    
    # Get filtered items
    items = manager.list_items(
        status=args.status,
        category=args.category,
        severity=args.severity,
        subcategory=args.subcategory,
        tags=tags,
        search_query=args.search,
        file_path=args.file_path
    )
    
    if not items:
        print("No technical debt items found.")
        return
    
    if args.format == "json":
        # Output as JSON
        result = {
            "items": [item.to_dict() for item in items]
        }
        print(json.dumps(result, indent=2))
    else:
        # Output in human-readable format
        print(f"Found {len(items)} technical debt items:")
        print()
        
        # Sort by severity (critical first)
        severity_order = {
            DebtSeverity.CRITICAL: 0,
            DebtSeverity.HIGH: 1,
            DebtSeverity.MEDIUM: 2,
            DebtSeverity.LOW: 3
        }
        
        items.sort(key=lambda item: (severity_order.get(item.severity, 999), item.title))
        
        for i, item in enumerate(items, 1):
            print(f"{i}. [{item.severity.value.upper()}] {item.title} ({item.id})")
            print(f"   Status: {item.status.value}")
            print(f"   Category: {item.category.value}")
            if item.file_path:
                print(f"   File: {item.file_path}")
            print()


def handle_show(args) -> None:
    """Handle the 'show' command."""
    manager = get_debt_manager()
    
    item = manager.get_item(args.item_id)
    if not item:
        print(f"No technical debt item found with ID: {args.item_id}")
        return
    
    if args.format == "json":
        # Output as JSON
        print(json.dumps(item.to_dict(), indent=2))
    else:
        # Output in human-readable format
        print(format_item_for_display(item))


def handle_update(args) -> None:
    """Handle the 'update' command."""
    manager = get_debt_manager()
    
    item = manager.get_item(args.item_id)
    if not item:
        print(f"No technical debt item found with ID: {args.item_id}")
        return
    
    # Collect updates
    updates = {}
    
    if args.title:
        updates["title"] = args.title
    
    if args.description:
        updates["description"] = args.description
    
    if args.category:
        updates["category"] = DebtCategory(args.category)
    
    if args.severity:
        updates["severity"] = DebtSeverity(args.severity)
    
    if args.status:
        item.update_status(args.status, "Status updated via CLI")
    
    if args.file_path:
        updates["file_path"] = args.file_path
    
    if args.line_number:
        updates["line_numbers"] = [args.line_number]
    
    if args.tags:
        updates["tags"] = [tag.strip() for tag in args.tags.split(",")]
    
    if args.resolution_plan:
        item.update_resolution_plan(args.resolution_plan)
    
    if args.effort:
        updates["estimated_effort"] = args.effort
    
    if args.impact:
        updates["impact"] = args.impact
    
    if args.subcategory:
        updates["subcategory"] = MLDebtSubcategory(args.subcategory)
    
    # Apply updates
    if updates:
        if manager.update_item(args.item_id, **updates):
            print(f"Updated technical debt item with ID: {args.item_id}")
        else:
            print(f"Failed to update technical debt item with ID: {args.item_id}")
    else:
        print("No updates specified.")


def handle_delete(args) -> None:
    """Handle the 'delete' command."""
    manager = get_debt_manager()
    
    item = manager.get_item(args.item_id)
    if not item:
        print(f"No technical debt item found with ID: {args.item_id}")
        return
    
    # Confirm deletion if not already confirmed
    if not args.confirm:
        confirm = input(f"Are you sure you want to delete '{item.title}' ({args.item_id})? [y/N] ")
        if confirm.lower() not in ["y", "yes"]:
            print("Deletion cancelled.")
            return
    
    if manager.delete_item(args.item_id):
        print(f"Deleted technical debt item with ID: {args.item_id}")
    else:
        print(f"Failed to delete technical debt item with ID: {args.item_id}")


def handle_report(args) -> None:
    """Handle the 'report' command."""
    manager = get_debt_manager()
    
    report = manager.generate_report(
        output_format=args.format,
        include_resolved=args.include_resolved,
        group_by=args.group_by
    )
    
    if args.output:
        os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
        with open(args.output, "w") as f:
            f.write(report)
        print(f"Report written to {args.output}")
    else:
        print(report)


def handle_scan(args) -> None:
    """Handle the 'scan' command."""
    manager = get_debt_manager()
    
    # Parse extensions
    extensions = None
    if args.extensions:
        extensions = [ext.strip() if ext.strip().startswith(".") else f".{ext.strip()}" 
                     for ext in args.extensions.split(",")]
    
    try:
        tags = manager.scan_directory_for_tech_debt(
            directory=args.directory,
            file_extensions=extensions,
            auto_add=args.auto_add
        )
        
        if not tags:
            print(f"No technical debt comments found in {args.directory}")
            return
        
        if args.format == "json":
            # Output as JSON
            print(json.dumps({"tags": tags}, indent=2))
        else:
            # Output in human-readable format
            print(f"Found {len(tags)} technical debt comments:")
            print()
            
            for i, tag in enumerate(tags, 1):
                print(f"{i}. [{tag['severity'].value.upper()}] {tag['file_path']}:{tag['line_number']}")
                print(f"   {tag['description']}")
                print()
            
            if args.auto_add:
                print(f"Added {len(tags)} technical debt items to the database.")
    
    except ValueError as e:
        print(f"Error: {e}")


def handle_metrics(args) -> None:
    """Handle the 'metrics' command."""
    manager = get_debt_manager()
    
    metrics = manager.get_metrics()
    
    if args.format == "json":
        # Output as JSON
        print(json.dumps(metrics, indent=2))
    else:
        # Output in human-readable format
        print("Technical Debt Metrics:")
        print(f"Total Items: {metrics['total_items']}")
        print(f"Active Items: {metrics['active_items']}")
        print(f"Debt Score: {metrics['debt_score']}")
        
        if metrics.get('trend'):
            trend = metrics['trend']
            change_symbol = "↑" if trend['score_change'] > 0 else "↓" if trend['score_change'] < 0 else "→"
            print(f"Trend: {change_symbol} {abs(trend['score_change'])} ({trend['percentage_change']:.1f}%)")
        
        print()
        print("By Severity:")
        for severity, count in metrics['by_severity'].items():
            print(f"  {severity.title()}: {count}")
        
        print()
        print("By Category:")
        for category, count in metrics['by_category'].items():
            if count > 0:
                print(f"  {category.replace('_', ' ').title()}: {count}")
        
        print()
        print("By Status:")
        for status, count in metrics['by_status'].items():
            if count > 0:
                print(f"  {status.replace('_', ' ').title()}: {count}")


def handle_comment(args) -> None:
    """Handle the 'comment' command."""
    manager = get_debt_manager()
    
    item = manager.get_item(args.item_id)
    if not item:
        print(f"No technical debt item found with ID: {args.item_id}")
        return
    
    item.add_comment(args.text, args.author)
    manager._save_items()  # Force save
    
    print(f"Added comment to technical debt item with ID: {args.item_id}")


def main() -> None:
    """Main entry point for the CLI tool."""
    parser = setup_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Dispatch to the appropriate handler based on the command
    handlers = {
        "add": handle_add,
        "list": handle_list,
        "show": handle_show,
        "update": handle_update,
        "delete": handle_delete,
        "report": handle_report,
        "scan": handle_scan,
        "metrics": handle_metrics,
        "comment": handle_comment
    }
    
    handler = handlers.get(args.command)
    if handler:
        handler(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main() 