#!/usr/bin/env python3
"""
Technical Debt Detection Script for Pre-commit Integration.

This script analyzes staged files to identify potential technical debt patterns
and provides a severity-weighted assessment. It implements the Enhanced Static Analysis
Integration approach from the research, combining regex patterns with more advanced
code quality analysis.
"""

import os
import re
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set, Any
from dataclasses import dataclass
import argparse
import git

# Add project root to path to enable imports
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from app.utils.tech_debt import (
    TechnicalDebtItem,
    DebtSeverity,
    DebtCategory,
    DebtStatus,
    MLDebtSubcategory,
    get_debt_manager,
)

# Import our Epic 4 ML tech debt patterns
try:
    from ml_tech_debt_patterns import get_epic4_tech_debt_patterns, MLDebtSubcategory

    HAS_EPIC4_PATTERNS = True
except ImportError:
    HAS_EPIC4_PATTERNS = False


@dataclass
class AnalysisResult:
    """Result of a technical debt analysis."""

    file_path: str
    line_number: int
    pattern_type: str
    debt_category: DebtCategory
    severity: DebtSeverity
    message: str
    matched_text: str
    subcategory: Optional[MLDebtSubcategory] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "file_path": self.file_path,
            "line_number": self.line_number,
            "pattern_type": self.pattern_type,
            "debt_category": (
                self.debt_category.value
                if isinstance(self.debt_category, DebtCategory)
                else self.debt_category
            ),
            "severity": (
                self.severity.value if isinstance(self.severity, DebtSeverity) else self.severity
            ),
            "message": self.message,
            "matched_text": self.matched_text,
            "subcategory": (
                self.subcategory.value
                if isinstance(self.subcategory, MLDebtSubcategory)
                else self.subcategory
            ),
        }


class TechnicalDebtDetector:
    """Detect technical debt in code files."""

    # Common technical debt patterns
    TECH_DEBT_PATTERNS = [
        # Todo comments
        {
            "pattern": r"#\s*(todo|fixme|hack|xxx):\s*(.*)",
            "message": "TODO comment indicates potential technical debt: {match}",
            "category": DebtCategory.CODE_QUALITY,
            "severity": DebtSeverity.MEDIUM,
            "type": "todo_comment",
        },
        # Magic numbers
        {
            "pattern": r"\b\d{3,}\b",
            "message": "Magic number detected: {match}",
            "category": DebtCategory.CODE_QUALITY,
            "severity": DebtSeverity.LOW,
            "type": "magic_number",
        },
        # Commented-out code
        {
            "pattern": r"#\s*(if|for|while|def|class)",
            "message": "Commented out code found: {match}",
            "category": DebtCategory.CODE_QUALITY,
            "severity": DebtSeverity.LOW,
            "type": "commented_code",
        },
        # Hardcoded credentials
        {
            "pattern": r'(password|api_key|secret|token|auth)\s*=\s*["\'][^"\']+["\']',
            "message": "Hardcoded credentials detected: {match}",
            "category": DebtCategory.SECURITY,
            "severity": DebtSeverity.CRITICAL,
            "type": "hardcoded_credentials",
        },
        # Long lines
        {
            "pattern": r"^.{120,}$",
            "message": "Line exceeds 120 characters",
            "category": DebtCategory.CODE_QUALITY,
            "severity": DebtSeverity.LOW,
            "type": "long_line",
        },
        # Complex comprehensions
        {
            "pattern": r"\[.*\bfor\b.*\bif\b.*\bfor\b.*\]",
            "message": "Complex list comprehension: {match}",
            "category": DebtCategory.CODE_QUALITY,
            "severity": DebtSeverity.MEDIUM,
            "type": "complex_comprehension",
        },
        # Dynamic imports
        {
            "pattern": r"__import__\(|importlib|eval\(",
            "message": "Dynamic code execution: {match}",
            "category": DebtCategory.SECURITY,
            "severity": DebtSeverity.HIGH,
            "type": "dynamic_execution",
        },
        # Database raw SQL
        {
            "pattern": r'execute\(["\']\s*SELECT|UPDATE|INSERT|DELETE',
            "message": "Raw SQL execution: {match}",
            "category": DebtCategory.SECURITY,
            "severity": DebtSeverity.MEDIUM,
            "type": "raw_sql",
        },
        # ML-specific: Direct model saving
        {
            "pattern": r'\.save\(["\'].*\.pkl["\']\)|pickle\.dump',
            "message": "Using basic pickle for model saving: {match}",
            "category": DebtCategory.ML_SPECIFIC,
            "severity": DebtSeverity.MEDIUM,
            "type": "insecure_serialization",
            "subcategory": MLDebtSubcategory.REPRODUCIBILITY,
        },
        # ML-specific: Hardcoded hyperparameters
        {
            "pattern": r"\b(learning_rate|epochs|batch_size|n_estimators|max_depth|num_leaves|embedding_dim|dropout)\s*=\s*\d+(\.\d+)?",
            "message": "Hardcoded ML hyperparameter: {match}",
            "category": DebtCategory.ML_SPECIFIC,
            "severity": DebtSeverity.MEDIUM,
            "type": "hardcoded_hyperparameter",
            "subcategory": MLDebtSubcategory.MODEL_COMPLEXITY,
        },
        # ML-specific: Data leakage risk
        {
            "pattern": r"train_test_split\([^,]+\)",
            "message": "Potential data leakage - no random state in split: {match}",
            "category": DebtCategory.ML_SPECIFIC,
            "severity": DebtSeverity.HIGH,
            "type": "data_leakage_risk",
            "subcategory": MLDebtSubcategory.DATA_QUALITY,
        },
        # ML-specific: Missing validation
        {
            "pattern": r"\.fit\([^,]+\)",
            "message": "Model training without explicit validation data: {match}",
            "category": DebtCategory.ML_SPECIFIC,
            "severity": DebtSeverity.MEDIUM,
            "type": "missing_validation",
            "subcategory": MLDebtSubcategory.EVALUATION,
        },
    ]

    # File patterns to exclude
    EXCLUDE_PATTERNS = [
        r".*\.git/.*",
        r".*venv/.*",
        r".*__pycache__/.*",
        r".*\.ipynb_checkpoints/.*",
        r".*\.pytest_cache/.*",
        r".*\.(json|md|txt|csv|yml|yaml)$",
    ]

    def __init__(self, repository_root: Optional[str] = None):
        """Initialize the detector with optional repository root."""
        self.repository_root = repository_root or os.getcwd()
        self.git_repo = None

        # Try to initialize git repository
        try:
            self.git_repo = git.Repo(self.repository_root)
        except (git.InvalidGitRepositoryError, git.NoSuchPathError):
            self.git_repo = None

        # Load Epic 4 ML technical debt patterns if available
        self._load_epic4_patterns()

        self.compiled_patterns = [
            {**pattern, "compiled": re.compile(pattern["pattern"])}
            for pattern in self.TECH_DEBT_PATTERNS
        ]
        self.exclude_compiled = [re.compile(pattern) for pattern in self.EXCLUDE_PATTERNS]
        self.debt_manager = get_debt_manager()

    def _load_epic4_patterns(self):
        """Load Epic 4 ML technical debt patterns if available."""
        if HAS_EPIC4_PATTERNS:
            # Add the Epic 4 patterns to our existing patterns
            epic4_patterns = get_epic4_tech_debt_patterns()

            # Convert pattern format to match our existing patterns
            for pattern in epic4_patterns:
                pattern_dict = {
                    "pattern": pattern["pattern"],
                    "message": pattern["message"],
                    "category": (
                        getattr(DebtCategory, pattern["category"])
                        if hasattr(DebtCategory, pattern["category"])
                        else pattern["category"]
                    ),
                    "severity": (
                        getattr(DebtSeverity, pattern["severity"])
                        if hasattr(DebtSeverity, pattern["severity"])
                        else pattern["severity"]
                    ),
                    "type": pattern["type"],
                }

                # Add subcategory if present
                if "subcategory" in pattern:
                    pattern_dict["subcategory"] = pattern["subcategory"]

                self.TECH_DEBT_PATTERNS.append(pattern_dict)

            print(f"Loaded {len(epic4_patterns)} Epic 4 ML technical debt patterns.")

    def is_excluded(self, file_path: str) -> bool:
        """Check if file should be excluded from analysis."""
        for pattern in self.exclude_compiled:
            if pattern.match(file_path):
                return True
        return False

    def get_staged_files(self) -> List[str]:
        """Get list of staged files in git repository."""
        try:
            # Get only staged Python files
            result = subprocess.run(
                ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM", "*.py"],
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout.strip().split("\n") if result.stdout.strip() else []
        except subprocess.CalledProcessError:
            print("Error: Failed to get staged files. Are you in a git repository?")
            return []

    def get_all_files(self) -> List[str]:
        """Get list of all Python files in the repository."""
        all_files = []
        for root, _, files in os.walk(self.repository_root):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.relpath(os.path.join(root, file), self.repository_root)
                    if not self.is_excluded(file_path):
                        all_files.append(file_path)
        return all_files

    def analyze_file(self, file_path: str) -> List[AnalysisResult]:
        """Analyze a file for technical debt patterns."""
        if self.is_excluded(file_path):
            return []

        results = []
        full_path = os.path.join(self.repository_root, file_path)

        try:
            with open(full_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            for line_num, line in enumerate(lines, 1):
                for pattern in self.compiled_patterns:
                    matches = pattern["compiled"].findall(line)
                    if matches:
                        for match in matches:
                            match_text = (
                                match[1] if isinstance(match, tuple) and len(match) > 1 else match
                            )
                            match_text = (
                                match_text if isinstance(match_text, str) else str(match_text)
                            )

                            # Format the message with the match
                            message = pattern["message"].format(match=match_text)

                            # Create an analysis result
                            result = AnalysisResult(
                                file_path=file_path,
                                line_number=line_num,
                                pattern_type=pattern["type"],
                                debt_category=pattern["category"],
                                severity=pattern["severity"],
                                message=message,
                                matched_text=line.strip(),
                                subcategory=pattern.get("subcategory"),
                            )
                            results.append(result)
        except Exception as e:
            print(f"Error analyzing file {file_path}: {e}")

        return results

    def analyze_all_files(self) -> List[AnalysisResult]:
        """Analyze all Python files for technical debt."""
        all_files = self.get_all_files()
        all_results = []

        for file_path in all_files:
            if file_path and not self.is_excluded(file_path):
                results = self.analyze_file(file_path)
                all_results.extend(results)

        return all_results

    def register_technical_debt(
        self, results: List[AnalysisResult], auto_add: bool = False
    ) -> List[str]:
        """Register detected technical debt in the debt manager."""
        added_items = []

        for result in results:
            title = f"{result.pattern_type.replace('_', ' ').title()} in {result.file_path}"
            description = (
                f"{result.message}\nFound at line {result.line_number}: {result.matched_text}"
            )

            if auto_add:
                item = TechnicalDebtItem(
                    title=title,
                    description=description,
                    category=result.debt_category,
                    severity=result.severity,
                    status=DebtStatus.IDENTIFIED,
                    file_path=result.file_path,
                    line_numbers=[result.line_number],
                    subcategory=result.subcategory,
                    tags=[result.pattern_type],
                )

                item_id = self.debt_manager.add_item(item)
                added_items.append(item_id)

        return added_items

    def calculate_debt_score(self, results: List[AnalysisResult]) -> float:
        """
        Calculate a technical debt score based on the analysis results.

        Uses the context-aware severity scoring from the research:
        Debt Score = (0.4 × File Criticality) + (0.3 × Commit Frequency) + (0.3 × User Impact)

        For pre-commit simplification, we use a weighted severity approach.
        """
        if not results:
            return 0.0

        # Severity weights based on research
        severity_weights = {
            DebtSeverity.LOW: 1,
            DebtSeverity.MEDIUM: 3,
            DebtSeverity.HIGH: 5,
            DebtSeverity.CRITICAL: 10,
        }

        # Calculate weighted severity score
        total_weight = 0
        for result in results:
            severity = result.severity
            if isinstance(severity, str):
                severity = DebtSeverity(severity)
            total_weight += severity_weights.get(severity, 1)

        # Normalize by number of issues with a non-linear scaling
        # This approach increases score dramatically with more critical issues
        score = (total_weight / len(results)) * (1 + (len(results) / 10))

        return round(score, 2)

    def format_results_for_display(self, results: List[AnalysisResult], score: float) -> str:
        """Format analysis results for terminal display."""
        if not results:
            return "No technical debt detected in staged files."

        # Group results by file
        files_dict = {}
        for result in results:
            if result.file_path not in files_dict:
                files_dict[result.file_path] = []
            files_dict[result.file_path].append(result)

        # Format output
        output = ["Technical Debt Analysis Results", "=" * 30]
        output.append(f"Debt Score: {score:.2f}")

        # Determine color based on score
        if score < 5:
            score_color = "\033[92m"  # Green
        elif score < 15:
            score_color = "\033[93m"  # Yellow
        else:
            score_color = "\033[91m"  # Red

        output.append(f"Overall Assessment: {score_color}{self._get_assessment(score)}\033[0m")
        output.append("")

        # Add file results
        for file_path, file_results in files_dict.items():
            output.append(f"File: {file_path}")
            output.append("-" * len(f"File: {file_path}"))

            for result in file_results:
                severity = result.severity
                if isinstance(severity, DebtSeverity):
                    severity = severity.value

                # Color code by severity
                if severity == "low":
                    severity_text = "\033[94mLOW\033[0m"  # Blue
                elif severity == "medium":
                    severity_text = "\033[93mMEDIUM\033[0m"  # Yellow
                elif severity == "high":
                    severity_text = "\033[91mHIGH\033[0m"  # Red
                else:  # critical
                    severity_text = "\033[91;1mCRITICAL\033[0m"  # Bold Red

                output.append(f"Line {result.line_number}: [{severity_text}] {result.message}")
                output.append(f"  > {result.matched_text}")
                output.append("")

        # Add recommendations
        output.append("Recommendations:")
        for recommendation in self._get_recommendations(results, score):
            output.append(f"- {recommendation}")

        return "\n".join(output)

    def _get_assessment(self, score: float) -> str:
        """Get an overall assessment based on the debt score."""
        if score < 3:
            return "Excellent - Very low technical debt."
        elif score < 8:
            return "Good - Acceptable level of technical debt."
        elif score < 15:
            return "Warning - Significant technical debt detected."
        else:
            return "Critical - High levels of technical debt require attention."

    def _get_recommendations(self, results: List[AnalysisResult], score: float) -> List[str]:
        """Generate recommendations based on analysis results."""
        recommendations = []

        # Count issues by category
        categories = {}
        for result in results:
            category = result.debt_category
            if isinstance(category, DebtCategory):
                category = category.value
            categories[category] = categories.get(category, 0) + 1

        # Add general recommendation based on score
        if score >= 15:
            recommendations.append(
                "Consider addressing critical and high severity issues before committing."
            )

        # Add specific recommendations based on categories
        if categories.get("security", 0) > 0:
            recommendations.append(
                "Address security-related debt immediately as it poses significant risk."
            )

        if categories.get("ml_specific", 0) > 0:
            recommendations.append(
                "Review ML-specific issues to ensure model reliability and reproducibility."
            )

        if categories.get("code_quality", 0) > 5:
            recommendations.append(
                "Significant code quality debt detected. Consider a focused refactoring session."
            )

        # Add recommendation to register debt
        recommendations.append(
            "Run with --auto-add to register these items in the technical debt system."
        )

        return recommendations

    def analyze_staged_files(self) -> List[AnalysisResult]:
        """Analyze all staged files for technical debt."""
        staged_files = self.get_staged_files()
        all_results = []

        for file_path in staged_files:
            if file_path and not self.is_excluded(file_path):
                results = self.analyze_file(file_path)
                all_results.extend(results)

        return all_results

    def analyze_file_by_epic(self, file_path: str, epic: str) -> List[AnalysisResult]:
        """
        Analyze a file for technical debt specific to an epic.

        Args:
            file_path: Path to the file to analyze
            epic: Epic identifier (e.g., 'Epic 4')

        Returns:
            List of analysis results
        """
        results = []

        if not os.path.isfile(file_path) or self.is_excluded(file_path):
            return results

        # Filter patterns by epic
        epic_patterns = [p for p in self.TECH_DEBT_PATTERNS if p.get("epic") == epic]

        if not epic_patterns:
            return results

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            lines = content.split("\n")

            for i, line in enumerate(lines):
                for pattern in epic_patterns:
                    regex = re.compile(pattern["pattern"], re.IGNORECASE)
                    match = regex.search(line)

                    if match:
                        result = AnalysisResult(
                            file_path=file_path,
                            line_number=i + 1,
                            pattern_type=pattern["type"],
                            debt_category=pattern["category"],
                            severity=pattern["severity"],
                            message=pattern["message"].format(match=match.group(0)),
                            matched_text=match.group(0),
                        )

                        # Add subcategory if present
                        if "subcategory" in pattern:
                            result.subcategory = pattern["subcategory"]

                        results.append(result)
        except Exception as e:
            print(f"Error analyzing file {file_path}: {e}")

        return results

    def analyze_epic4_files(self) -> List[AnalysisResult]:
        """
        Analyze all files for Epic 4 technical debt.

        Returns:
            List of analysis results specific to Epic 4
        """
        results = []
        files = self.get_all_files()

        for file_path in files:
            if self.is_excluded(file_path):
                continue

            file_results = self.analyze_file_by_epic(file_path, "Epic 4")
            results.extend(file_results)

        return results

    def _get_recommendations_by_epic(self, results: List[AnalysisResult], epic: str) -> List[str]:
        """
        Get recommendations for technical debt issues specific to an epic.

        Args:
            results: List of analysis results
            epic: Epic identifier (e.g., 'Epic 4')

        Returns:
            List of recommendation strings
        """
        # Filter results by epic
        epic_results = [r for r in results if hasattr(r, "epic") and r.epic == epic]

        if not epic_results:
            return []

        recommendations = []

        # Group by subcategory
        subcategories = {}
        for result in epic_results:
            if not hasattr(result, "subcategory") or result.subcategory is None:
                continue

            subcategory = result.subcategory
            if subcategory not in subcategories:
                subcategories[subcategory] = []

            subcategories[subcategory].append(result)

        # Generate recommendations by subcategory
        for subcategory, results in subcategories.items():
            if len(results) > 2:
                remediation = next(
                    (r.remediation for r in results if hasattr(r, "remediation")), None
                )
                if remediation:
                    recommendations.append(
                        f"Consider focusing on {subcategory.value} issues: {len(results)} instances found. {remediation}"
                    )

        # Add research-backed recommendations
        research_refs = set(
            r.research_reference
            for r in epic_results
            if hasattr(r, "research_reference") and r.research_reference
        )
        for ref in research_refs:
            recommendations.append(f"Research insight: {ref}")

        return recommendations


def main():
    """Main function to run the technical debt detection."""
    parser = argparse.ArgumentParser(description="Detect technical debt in code.")
    parser.add_argument("--all", action="store_true", help="Scan all Python files in the project")
    parser.add_argument("--staged", action="store_true", help="Scan only staged files")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    parser.add_argument(
        "--auto-add",
        action="store_true",
        help="Automatically add detected issues to the debt tracking system",
    )
    parser.add_argument(
        "--epic", type=str, help='Scan only for technical debt specific to an epic (e.g., "Epic 4")'
    )

    args = parser.parse_args()

    detector = TechnicalDebtDetector()

    if args.epic:
        print(f"Scanning for technical debt specific to {args.epic}...")
        if args.epic.lower() == "epic 4":
            results = detector.analyze_epic4_files()
        else:
            print(f"Epic-specific analysis not supported for {args.epic}")
            return
    elif args.staged:
        print("Scanning staged files for technical debt...")
        results = detector.analyze_staged_files()
    elif args.all:
        print("Scanning all Python files for technical debt...")
        results = detector.analyze_all_files()
    else:
        print("Scanning staged files for technical debt (default)...")
        results = detector.analyze_staged_files()

    # Calculate overall debt score
    score = detector.calculate_debt_score(results)

    if args.json:
        # Output results as JSON
        output = {
            "results": [result.to_dict() for result in results],
            "score": score,
            "assessment": detector._get_assessment(score),
            "recommendations": detector._get_recommendations(results, score),
        }

        if args.epic:
            output["epic_recommendations"] = detector._get_recommendations_by_epic(
                results, args.epic
            )

        print(json.dumps(output, indent=2))
    else:
        # Output results as text
        print(detector.format_results_for_display(results, score))

        if args.epic:
            epic_recommendations = detector._get_recommendations_by_epic(results, args.epic)
            if epic_recommendations:
                print("\nEpic-Specific Recommendations:")
                for rec in epic_recommendations:
                    print(f"- {rec}")

    if args.auto_add:
        added_issues = detector.register_technical_debt(results, auto_add=True)
        if added_issues:
            print(f"\nAuto-added {len(added_issues)} technical debt issues to tracking system.")
        else:
            print("\nNo new technical debt issues to add to tracking system.")

    # Return non-zero exit code if serious issues found
    critical_issues = [r for r in results if r.severity == DebtSeverity.CRITICAL]
    high_issues = [r for r in results if r.severity == DebtSeverity.HIGH]

    if critical_issues:
        return 2
    elif high_issues and len(high_issues) > 3:
        return 1

    return 0


if __name__ == "__main__":
    main()
