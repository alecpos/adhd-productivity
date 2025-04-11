"""NLP parser for converting natural language commands into structured task data."""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import re

from app.services.llm_service import LLMService


class NLPParser:
    """Parser for converting natural language into structured task data."""

    def __init__(self):
        """Initialize the NLP parser."""
        self.llm_service = LLMService()

    @staticmethod
    async def parse(command: str) -> Dict[str, Any]:
        """
        Parse a natural language command into task data.

        Args:
            command: The natural language command to parse

        Returns:
            Dict containing parsed task data
        """
        try:
            # Initialize parser
            parser = NLPParser()

            # Get structured analysis from LLM
            analysis = await parser.llm_service.analyze_task_complexity(command)

            # Extract task components
            task_data = {
                "title": parser._extract_title(command),
                "description": command,
                "estimated_duration": analysis.get("time_estimate", 30),
                "energy_requirement": int(analysis.get("focus_requirements", {}).get("energy", 5)),
                "focus_requirement": int(analysis.get("focus_requirements", {}).get("focus", 5)),
                "due_date": parser._extract_due_date(command),
                "priority": parser._extract_priority(command, analysis),
                "subtasks": parser._extract_subtasks(command, analysis),
                "tags": parser._extract_tags(command),
                "meta_data": {
                    "nlp_confidence": analysis.get("confidence_score", 0.7),
                    "complexity_level": analysis.get("complexity_level", 3),
                    "adhd_friendly_score": analysis.get("adhd_friendly_score", 0.7),
                },
            }

            return task_data

        except Exception as e:
            raise ValueError(f"Error parsing NLP command: {str(e)}")

    def _extract_title(self, text: str) -> str:
        """Extract task title from text."""
        # Get first sentence or first N words
        first_sentence = text.split(".")[0].strip()
        if len(first_sentence) > 100:
            return " ".join(first_sentence.split()[:10]) + "..."
        return first_sentence

    def _extract_due_date(self, text: str) -> Optional[datetime]:
        """Extract due date from text."""
        # Common date patterns
        patterns = [
            r"due\s+(?:on|by)?\s*(\d{1,2}(?:st|nd|rd|th)?\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*(?:\s+\d{4})?)",
            r"by\s+(\d{1,2}(?:st|nd|rd|th)?\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*(?:\s+\d{4})?)",
            r"(?:next|this)\s+(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)",
            r"(?:in|within)\s+(\d+)\s+(day|week|month)s?",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                # Convert matched text to datetime
                # This is a simplified version - you'd want more robust date parsing
                return datetime.now() + timedelta(days=7)

        return None

    def _extract_priority(self, text: str, analysis: Dict[str, Any]) -> str:
        """Extract task priority from text and analysis."""
        # Look for priority keywords
        if re.search(r"\b(urgent|asap|emergency|critical)\b", text, re.IGNORECASE):
            return "HIGH"
        elif re.search(r"\b(low|minor|whenever|no rush)\b", text, re.IGNORECASE):
            return "LOW"

        # Use complexity analysis as fallback
        complexity = analysis.get("complexity_level", 3)
        if complexity > 4:
            return "HIGH"
        elif complexity < 2:
            return "LOW"

        return "MEDIUM"

    def _extract_subtasks(self, text: str, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract subtasks from text and analysis."""
        subtasks = []

        # Use breakdown suggestions from analysis
        breakdown = analysis.get("breakdown_suggestions", [])
        if breakdown:
            for i, step in enumerate(breakdown):
                subtasks.append(
                    {
                        "title": step,
                        "description": step,
                        "estimated_duration": 15,  # Default duration
                        "priority": "MEDIUM",
                    }
                )

        return subtasks

    def _extract_tags(self, text: str) -> List[str]:
        """Extract tags from text."""
        tags = []

        # Look for hashtags
        hashtags = re.findall(r"#(\w+)", text)
        if hashtags:
            tags.extend(hashtags)

        # Look for common categories
        categories = ["work", "personal", "study", "health", "shopping", "finance"]
        for category in categories:
            if re.search(rf"\b{category}\b", text, re.IGNORECASE):
                tags.append(category)

        return list(set(tags))  # Remove duplicates
