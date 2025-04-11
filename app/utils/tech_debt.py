"""
Technical Debt Management System.

This module provides utilities for tracking, categorizing, and managing technical debt
throughout the ML development lifecycle. It helps in documenting, prioritizing, and
addressing technical debt systematically.
"""

import json
import os
import re
import sys
import logging
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Tuple, Set

logger = logging.getLogger(__name__)

class DebtSeverity(Enum):
    """Severity levels for technical debt items."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DebtCategory(Enum):
    """Categories of technical debt."""

    CODE_QUALITY = "code_quality"
    ARCHITECTURE = "architecture"
    DOCUMENTATION = "documentation"
    TESTS = "tests"
    PERFORMANCE = "performance"
    SECURITY = "security"
    DEPENDENCY = "dependency"
    ML_SPECIFIC = "ml_specific"
    USABILITY = "usability"
    ACCESSIBILITY = "accessibility"
    DEPLOYMENT = "deployment"
    MONITORING = "monitoring"


class DebtStatus(Enum):
    """Status of technical debt items."""

    IDENTIFIED = "identified"
    ACKNOWLEDGED = "acknowledged"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    WONTFIX = "wontfix"
    DEFERRED = "deferred"


class MLDebtSubcategory(Enum):
    """ML-specific subcategories of technical debt."""

    DATA_QUALITY = "data_quality"
    MODEL_COMPLEXITY = "model_complexity"
    FEATURE_ENGINEERING = "feature_engineering"
    MODEL_DRIFT = "model_drift"
    PIPELINE_COMPLEXITY = "pipeline_complexity"
    EXPLAINABILITY = "explainability"
    REPRODUCIBILITY = "reproducibility"
    MONITORING = "monitoring"
    FAIRNESS = "fairness"
    EVALUATION = "evaluation"


class TechnicalDebtItem:
    """Represents a single technical debt item in the system."""

    def __init__(
        self,
        title: str,
        description: str,
        category: Union[DebtCategory, str],
        severity: Union[DebtSeverity, str],
        status: Union[DebtStatus, str] = DebtStatus.IDENTIFIED,
        file_path: Optional[str] = None,
        line_numbers: Optional[Union[List[int], Tuple[int, int]]] = None,
        created_by: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        due_date: Optional[datetime] = None,
        estimated_effort: Optional[str] = None,
        subcategory: Optional[Union[MLDebtSubcategory, str]] = None,
        tags: Optional[List[str]] = None,
        related_items: Optional[List[str]] = None,
        resolution_plan: Optional[str] = None,
        resolution_commit: Optional[str] = None,
        impact: Optional[str] = None,
    ):
        """Initialize a technical debt item."""
        self.id = f"debt_{datetime.now().strftime('%Y%m%d%H%M%S')}_{abs(hash(title)) % 10000}"
        self.title = title
        self.description = description

        # Handle category as either enum or string
        if isinstance(category, str):
            try:
                self.category = DebtCategory(category)
            except ValueError:
                raise ValueError(f"Invalid debt category: {category}")
        else:
            self.category = category

        # Handle severity as either enum or string
        if isinstance(severity, str):
            try:
                self.severity = DebtSeverity(severity)
            except ValueError:
                raise ValueError(f"Invalid debt severity: {severity}")
        else:
            self.severity = severity

        # Handle status as either enum or string
        if isinstance(status, str):
            try:
                self.status = DebtStatus(status)
            except ValueError:
                raise ValueError(f"Invalid debt status: {status}")
        else:
            self.status = status

        # Handle subcategory if provided
        self.subcategory = None
        if subcategory:
            if isinstance(subcategory, str):
                try:
                    self.subcategory = MLDebtSubcategory(subcategory)
                except ValueError:
                    raise ValueError(f"Invalid ML debt subcategory: {subcategory}")
            else:
                self.subcategory = subcategory

        self.file_path = file_path
        self.line_numbers = line_numbers
        self.created_by = created_by or os.environ.get("USER", "unknown")
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
        self.due_date = due_date
        self.estimated_effort = estimated_effort
        self.tags = tags or []
        self.related_items = related_items or []
        self.resolution_plan = resolution_plan
        self.resolution_commit = resolution_commit
        self.impact = impact
        self.history = [{
            "timestamp": self.created_at.isoformat(),
            "status": self.status.value,
            "message": "Item created"
        }]

    def update_status(self, new_status: Union[DebtStatus, str], message: Optional[str] = None) -> None:
        """Update the status of this debt item."""
        if isinstance(new_status, str):
            try:
                new_status = DebtStatus(new_status)
            except ValueError:
                raise ValueError(f"Invalid debt status: {new_status}")

        self.status = new_status
        self.updated_at = datetime.now()

        self.history.append({
            "timestamp": self.updated_at.isoformat(),
            "status": self.status.value,
            "message": message or f"Status changed to {self.status.value}"
        })

    def add_comment(self, comment: str, author: Optional[str] = None) -> None:
        """Add a comment to this debt item."""
        if not hasattr(self, "comments"):
            self.comments = []

        self.comments.append({
            "author": author or os.environ.get("USER", "unknown"),
            "timestamp": datetime.now().isoformat(),
            "text": comment
        })
        self.updated_at = datetime.now()

    def update_resolution_plan(self, plan: str) -> None:
        """Update the resolution plan for this debt item."""
        self.resolution_plan = plan
        self.updated_at = datetime.now()

        self.history.append({
            "timestamp": self.updated_at.isoformat(),
            "status": self.status.value,
            "message": "Resolution plan updated"
        })

    def to_dict(self) -> Dict[str, Any]:
        """Convert the debt item to a dictionary for serialization."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "category": self.category.value,
            "severity": self.severity.value,
            "status": self.status.value,
            "file_path": self.file_path,
            "line_numbers": self.line_numbers,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "estimated_effort": self.estimated_effort,
            "subcategory": self.subcategory.value if self.subcategory else None,
            "tags": self.tags,
            "related_items": self.related_items,
            "resolution_plan": self.resolution_plan,
            "resolution_commit": self.resolution_commit,
            "impact": self.impact,
            "history": self.history,
            "comments": getattr(self, "comments", [])
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TechnicalDebtItem":
        """Create a debt item from a dictionary."""
        # Convert string timestamps back to datetime objects
        created_at = datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None
        updated_at = datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None
        due_date = datetime.fromisoformat(data["due_date"]) if data.get("due_date") else None

        # Create the debt item
        item = cls(
            title=data["title"],
            description=data["description"],
            category=data["category"],
            severity=data["severity"],
            status=data["status"],
            file_path=data.get("file_path"),
            line_numbers=data.get("line_numbers"),
            created_by=data.get("created_by"),
            created_at=created_at,
            updated_at=updated_at,
            due_date=due_date,
            estimated_effort=data.get("estimated_effort"),
            subcategory=data.get("subcategory"),
            tags=data.get("tags", []),
            related_items=data.get("related_items", []),
            resolution_plan=data.get("resolution_plan"),
            resolution_commit=data.get("resolution_commit"),
            impact=data.get("impact")
        )

        # Restore ID and history
        item.id = data["id"]
        item.history = data.get("history", [])

        # Restore comments if present
        if "comments" in data:
            item.comments = data["comments"]

        return item


class TechnicalDebtManager:
    """Manages technical debt items across the codebase."""

    def __init__(self, db_path: Optional[str] = None):
        """Initialize the technical debt manager."""
        self.db_path = db_path or os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "tech_debt.json"
        )
        self.debt_items: Dict[str, TechnicalDebtItem] = {}
        self._load_items()

    def _load_items(self) -> None:
        """Load debt items from the database file."""
        if not os.path.exists(self.db_path):
            # Create the initial database file if it doesn't exist
            self._save_items()
            return

        try:
            with open(self.db_path, "r") as f:
                data = json.load(f)

            for item_data in data.get("items", []):
                item = TechnicalDebtItem.from_dict(item_data)
                self.debt_items[item.id] = item

            logger.info(f"Loaded {len(self.debt_items)} technical debt items from {self.db_path}")
        except Exception as e:
            logger.error(f"Error loading technical debt items: {e}")

    def _save_items(self) -> None:
        """Save debt items to the database file."""
        try:
            data = {
                "last_updated": datetime.now().isoformat(),
                "items": [item.to_dict() for item in self.debt_items.values()]
            }

            # Ensure directory exists
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

            with open(self.db_path, "w") as f:
                json.dump(data, f, indent=2)

            logger.info(f"Saved {len(self.debt_items)} technical debt items to {self.db_path}")
        except Exception as e:
            logger.error(f"Error saving technical debt items: {e}")

    def add_item(self, item: TechnicalDebtItem) -> str:
        """Add a new technical debt item."""
        self.debt_items[item.id] = item
        self._save_items()
        return item.id

    def get_item(self, item_id: str) -> Optional[TechnicalDebtItem]:
        """Get a debt item by ID."""
        return self.debt_items.get(item_id)

    def update_item(self, item_id: str, **kwargs) -> bool:
        """Update a debt item."""
        item = self.get_item(item_id)
        if not item:
            return False

        for key, value in kwargs.items():
            if hasattr(item, key):
                setattr(item, key, value)

        item.updated_at = datetime.now()
        self._save_items()
        return True

    def delete_item(self, item_id: str) -> bool:
        """Delete a debt item."""
        if item_id in self.debt_items:
            del self.debt_items[item_id]
            self._save_items()
            return True
        return False

    def list_items(
        self,
        status: Optional[Union[DebtStatus, str]] = None,
        category: Optional[Union[DebtCategory, str]] = None,
        severity: Optional[Union[DebtSeverity, str]] = None,
        subcategory: Optional[Union[MLDebtSubcategory, str]] = None,
        tags: Optional[List[str]] = None,
        search_query: Optional[str] = None,
        file_path: Optional[str] = None
    ) -> List[TechnicalDebtItem]:
        """List debt items with optional filtering."""
        items = list(self.debt_items.values())

        # Filter by status if provided
        if status:
            if isinstance(status, str):
                try:
                    status = DebtStatus(status)
                except ValueError:
                    raise ValueError(f"Invalid debt status: {status}")
            items = [item for item in items if item.status == status]

        # Filter by category if provided
        if category:
            if isinstance(category, str):
                try:
                    category = DebtCategory(category)
                except ValueError:
                    raise ValueError(f"Invalid debt category: {category}")
            items = [item for item in items if item.category == category]

        # Filter by severity if provided
        if severity:
            if isinstance(severity, str):
                try:
                    severity = DebtSeverity(severity)
                except ValueError:
                    raise ValueError(f"Invalid debt severity: {severity}")
            items = [item for item in items if item.severity == severity]

        # Filter by subcategory if provided
        if subcategory:
            if isinstance(subcategory, str):
                try:
                    subcategory = MLDebtSubcategory(subcategory)
                except ValueError:
                    raise ValueError(f"Invalid ML debt subcategory: {subcategory}")
            items = [item for item in items if item.subcategory == subcategory]

        # Filter by tags if provided
        if tags:
            items = [
                item for item in items
                if any(tag in item.tags for tag in tags)
            ]

        # Filter by file path if provided
        if file_path:
            items = [item for item in items if item.file_path and file_path in item.file_path]

        # Filter by search query if provided
        if search_query:
            search_query = search_query.lower()
            items = [
                item for item in items
                if (
                    search_query in item.title.lower() or
                    search_query in item.description.lower() or
                    (item.resolution_plan and search_query in item.resolution_plan.lower())
                )
            ]

        return items

    def generate_report(
        self,
        output_format: str = "markdown",
        include_resolved: bool = False,
        group_by: Optional[str] = None
    ) -> str:
        """Generate a report of technical debt items."""
        items = self.list_items()

        if not include_resolved:
            items = [item for item in items if item.status != DebtStatus.RESOLVED]

        if not items:
            return "No technical debt items found."

        if output_format == "markdown":
            return self._generate_markdown_report(items, group_by)
        elif output_format == "json":
            return json.dumps({
                "generated_at": datetime.now().isoformat(),
                "items": [item.to_dict() for item in items]
            }, indent=2)
        else:
            raise ValueError(f"Unsupported output format: {output_format}")

    def _generate_markdown_report(
        self,
        items: List[TechnicalDebtItem],
        group_by: Optional[str] = None
    ) -> str:
        """Generate a markdown report of technical debt items."""
        report_parts = [
            "# Technical Debt Report",
            f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Total items: {len(items)}",
            ""
        ]

        # Group items if requested
        if group_by == "category":
            by_category: Dict[DebtCategory, List[TechnicalDebtItem]] = {}
            for item in items:
                if item.category not in by_category:
                    by_category[item.category] = []
                by_category[item.category].append(item)

            for category, category_items in by_category.items():
                report_parts.append(f"## {category.value.replace('_', ' ').title()}")
                report_parts.append(f"Total: {len(category_items)}")
                report_parts.append("")

                for item in category_items:
                    report_parts.extend(self._format_item_for_markdown(item))

        elif group_by == "severity":
            # Sort by severity (critical first)
            severity_order = {
                DebtSeverity.CRITICAL: 0,
                DebtSeverity.HIGH: 1,
                DebtSeverity.MEDIUM: 2,
                DebtSeverity.LOW: 3
            }

            by_severity: Dict[DebtSeverity, List[TechnicalDebtItem]] = {}
            for item in items:
                if item.severity not in by_severity:
                    by_severity[item.severity] = []
                by_severity[item.severity].append(item)

            for severity in sorted(by_severity.keys(), key=lambda s: severity_order.get(s, 999)):
                severity_items = by_severity[severity]
                report_parts.append(f"## {severity.value.title()} Severity Items")
                report_parts.append(f"Total: {len(severity_items)}")
                report_parts.append("")

                for item in severity_items:
                    report_parts.extend(self._format_item_for_markdown(item))

        elif group_by == "status":
            by_status: Dict[DebtStatus, List[TechnicalDebtItem]] = {}
            for item in items:
                if item.status not in by_status:
                    by_status[item.status] = []
                by_status[item.status].append(item)

            for status, status_items in by_status.items():
                report_parts.append(f"## {status.value.replace('_', ' ').title()} Items")
                report_parts.append(f"Total: {len(status_items)}")
                report_parts.append("")

                for item in status_items:
                    report_parts.extend(self._format_item_for_markdown(item))

        else:
            # No grouping, just list all items
            for item in sorted(items, key=lambda i: self._get_sort_key(i)):
                report_parts.extend(self._format_item_for_markdown(item))

        return "\n".join(report_parts)

    def _format_item_for_markdown(self, item: TechnicalDebtItem) -> List[str]:
        """Format a debt item for markdown report."""
        parts = [
            f"### {item.title} ({item.id})",
            "",
            f"**Severity:** {item.severity.value.title()}",
            f"**Status:** {item.status.value.replace('_', ' ').title()}",
            f"**Category:** {item.category.value.replace('_', ' ').title()}",
            ""
        ]

        if item.subcategory:
            parts.append(f"**Subcategory:** {item.subcategory.value.replace('_', ' ').title()}")
            parts.append("")

        parts.append(f"**Description:** {item.description}")
        parts.append("")

        if item.file_path:
            parts.append(f"**File:** `{item.file_path}`")
            if item.line_numbers:
                if isinstance(item.line_numbers, list):
                    line_str = ", ".join(str(line) for line in item.line_numbers)
                else:
                    line_str = f"{item.line_numbers[0]}-{item.line_numbers[1]}"
                parts.append(f"**Lines:** {line_str}")
            parts.append("")

        if item.tags:
            parts.append(f"**Tags:** {', '.join(item.tags)}")
            parts.append("")

        if item.impact:
            parts.append(f"**Impact:** {item.impact}")
            parts.append("")

        if item.resolution_plan:
            parts.append(f"**Resolution Plan:** {item.resolution_plan}")
            parts.append("")

        parts.append(f"**Created by:** {item.created_by} on {item.created_at.strftime('%Y-%m-%d')}")
        if item.estimated_effort:
            parts.append(f"**Estimated Effort:** {item.estimated_effort}")

        if hasattr(item, "comments") and item.comments:
            parts.append("")
            parts.append("**Comments:**")
            parts.append("")
            for comment in item.comments:
                parts.append(f"- **{comment['author']}** ({comment['timestamp']}): {comment['text']}")

        parts.append("")
        parts.append("---")
        parts.append("")

        return parts

    def _get_sort_key(self, item: TechnicalDebtItem) -> Tuple[int, str]:
        """Get a sort key for a debt item (for consistent ordering)."""
        severity_order = {
            DebtSeverity.CRITICAL: 0,
            DebtSeverity.HIGH: 1,
            DebtSeverity.MEDIUM: 2,
            DebtSeverity.LOW: 3
        }
        return (severity_order.get(item.severity, 999), item.title.lower())

    def find_tech_debt_tags(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Find technical debt tags in a file using code comments.

        Looks for special comment markers like:
        # TODO(tech-debt): Description of the issue
        # FIXME(tech-debt): Description of the issue
        # TECH-DEBT: Description of the issue

        Returns a list of dictionaries with information about each tag found.
        """
        if not os.path.exists(file_path):
            return []

        # Regex patterns for different tech debt comment styles
        patterns = [
            r'#\s*TODO\(tech-debt\):\s*(.*?)(?:\n|$)',  # Python-style TODO
            r'#\s*FIXME\(tech-debt\):\s*(.*?)(?:\n|$)',  # Python-style FIXME
            r'//\s*TODO\(tech-debt\):\s*(.*?)(?:\n|$)',  # JS/TS-style TODO
            r'//\s*FIXME\(tech-debt\):\s*(.*?)(?:\n|$)',  # JS/TS-style FIXME
            r'/\*\s*TECH-DEBT:\s*(.*?)\*/',  # C-style comment
            r'<!--\s*TECH-DEBT:\s*(.*?)-->',  # HTML/XML comment
            r'#\s*TECH-DEBT:\s*(.*?)(?:\n|$)',  # Hash comment
            r'//\s*TECH-DEBT:\s*(.*?)(?:\n|$)',  # Double slash comment
        ]

        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        tags = []
        for pattern in patterns:
            for match in re.finditer(pattern, content):
                description = match.group(1).strip()

                # Find line number
                line_number = content[:match.start()].count('\n') + 1

                # Extract any severity indicator if present
                severity = DebtSeverity.MEDIUM  # Default severity
                severity_patterns = [
                    (r'\[severity:(\w+)\]', 1),
                    (r'severity:\s*(\w+)', 1),
                    (r'priority:\s*(\w+)', 1),
                ]

                for severity_pattern, group_idx in severity_patterns:
                    severity_match = re.search(severity_pattern, description, re.IGNORECASE)
                    if severity_match:
                        try:
                            # Try to convert the severity string to enum
                            severity_str = severity_match.group(group_idx).lower()
                            if severity_str in [s.value for s in DebtSeverity]:
                                severity = DebtSeverity(severity_str)
                            # Remove the severity indicator from description
                            description = re.sub(severity_pattern, '', description, flags=re.IGNORECASE).strip()
                        except (ValueError, IndexError):
                            pass

                tags.append({
                    'file_path': file_path,
                    'line_number': line_number,
                    'description': description,
                    'severity': severity
                })

        return tags

    def scan_directory_for_tech_debt(
        self,
        directory: str,
        file_extensions: Optional[List[str]] = None,
        auto_add: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Scan a directory for technical debt tags in code comments.

        Args:
            directory: The directory to scan
            file_extensions: List of file extensions to scan (e.g., ['.py', '.js'])
            auto_add: Whether to automatically add found items to the database

        Returns:
            A list of dictionaries with information about each tag found
        """
        if not os.path.exists(directory) or not os.path.isdir(directory):
            raise ValueError(f"Directory not found: {directory}")

        all_tags = []

        # Default extensions if none provided
        if file_extensions is None:
            file_extensions = ['.py', '.js', '.ts', '.tsx', '.jsx', '.java', '.c', '.cpp', '.h', '.hpp', '.cs', '.go', '.rb', '.php']

        for root, _, files in os.walk(directory):
            for file in files:
                if any(file.endswith(ext) for ext in file_extensions):
                    file_path = os.path.join(root, file)
                    tags = self.find_tech_debt_tags(file_path)

                    if auto_add and tags:
                        for tag in tags:
                            # Convert tag to TechnicalDebtItem and add to manager
                            item = TechnicalDebtItem(
                                title=f"Tech debt in {os.path.basename(tag['file_path'])}",
                                description=tag['description'],
                                category=DebtCategory.CODE_QUALITY,
                                severity=tag['severity'],
                                file_path=tag['file_path'],
                                line_numbers=[tag['line_number']]
                            )
                            self.add_item(item)

                    all_tags.extend(tags)

        return all_tags

    def analyze_commit_for_debt_changes(self, commit_info: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Analyze a commit for changes to technical debt markers.

        Args:
            commit_info: Dictionary with 'added', 'modified', and 'removed' lists of file paths

        Returns:
            Dictionary with 'added', 'modified', and 'removed' lists of tech debt IDs
        """
        result = {
            'added': [],
            'modified': [],
            'removed': []
        }

        # Existing debt items by file path
        debt_by_file: Dict[str, List[TechnicalDebtItem]] = {}
        for item in self.debt_items.values():
            if item.file_path:
                if item.file_path not in debt_by_file:
                    debt_by_file[item.file_path] = []
                debt_by_file[item.file_path].append(item)

        # Check removed files
        for file_path in commit_info.get('removed', []):
            if file_path in debt_by_file:
                for item in debt_by_file[file_path]:
                    # Mark the item as resolved if the file was removed
                    item.update_status(
                        DebtStatus.RESOLVED,
                        f"File was removed in commit"
                    )
                    result['removed'].append(item.id)

        # Check modified files
        for file_path in commit_info.get('modified', []):
            # Look for tech debt tags in the modified file
            tags = self.find_tech_debt_tags(file_path)

            # Check if existing debt items for this file are still present
            if file_path in debt_by_file:
                for item in debt_by_file[file_path]:
                    # Simple check: if the line number is in the modified file's tags
                    if item.line_numbers:
                        line_numbers = item.line_numbers if isinstance(item.line_numbers, list) else list(range(item.line_numbers[0], item.line_numbers[1] + 1))

                        # Check if any tag matches this item's line numbers
                        tag_lines = [tag['line_number'] for tag in tags]
                        if not any(line in tag_lines for line in line_numbers):
                            # The debt item's line numbers are not in the tags,
                            # which might mean it was resolved
                            item.update_status(
                                DebtStatus.RESOLVED,
                                f"Tech debt marker not found after file was modified"
                            )
                            result['removed'].append(item.id)

        # Check added files
        for file_path in commit_info.get('added', []):
            tags = self.find_tech_debt_tags(file_path)
            for tag in tags:
                # Create a new tech debt item for each tag
                item = TechnicalDebtItem(
                    title=f"Tech debt in new file {os.path.basename(file_path)}",
                    description=tag['description'],
                    category=DebtCategory.CODE_QUALITY,
                    severity=tag['severity'],
                    file_path=file_path,
                    line_numbers=[tag['line_number']]
                )
                self.add_item(item)
                result['added'].append(item.id)

        self._save_items()
        return result

    def get_metrics(self) -> Dict[str, Any]:
        """Get metrics about the technical debt in the codebase."""
        items = list(self.debt_items.values())

        # Skip resolved items
        active_items = [item for item in items if item.status != DebtStatus.RESOLVED]

        # Count by severity
        by_severity = {s.value: 0 for s in DebtSeverity}
        for item in active_items:
            by_severity[item.severity.value] += 1

        # Count by category
        by_category = {c.value: 0 for c in DebtCategory}
        for item in active_items:
            by_category[item.category.value] += 1

        # Count by status
        by_status = {s.value: 0 for s in DebtStatus}
        for item in items:  # Include all items, even resolved
            by_status[item.status.value] += 1

        # Calculate debt score
        # Higher severity items contribute more to the score
        severity_weights = {
            DebtSeverity.LOW: 1,
            DebtSeverity.MEDIUM: 3,
            DebtSeverity.HIGH: 6,
            DebtSeverity.CRITICAL: 10
        }

        debt_score = sum(severity_weights[item.severity] for item in active_items)

        # Calculate trend if we have history
        trend = None
        if hasattr(self, '_last_metrics'):
            previous_score = self._last_metrics.get('debt_score', 0)
            trend = {
                'score_change': debt_score - previous_score,
                'percentage_change': (
                    ((debt_score - previous_score) / previous_score) * 100
                    if previous_score else 0
                )
            }

        # Store metrics for trend calculation next time
        self._last_metrics = {'debt_score': debt_score}

        return {
            'total_items': len(items),
            'active_items': len(active_items),
            'by_severity': by_severity,
            'by_category': by_category,
            'by_status': by_status,
            'debt_score': debt_score,
            'trend': trend,
            'last_updated': datetime.now().isoformat()
        }


# Create a singleton instance
debt_manager = TechnicalDebtManager()

def get_debt_manager() -> TechnicalDebtManager:
    """Get the singleton instance of the debt manager."""
    return debt_manager
