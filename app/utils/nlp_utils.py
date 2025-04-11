import spacy
import re
from typing import List, Dict, Optional
from datetime import timedelta
import subprocess

from .time_utils import parse_datetime

# Load the English language model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    # If model not found, download it

    subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")


def extract_time_expressions(text: str) -> List[Dict]:
    """Extract time-related expressions from text."""
    doc = nlp(text)
    time_entities = []

    for ent in doc.ents:
        if ent.label_ in ["TIME", "DATE"]:
            time_entities.append(
                {"text": ent.text, "label": ent.label_, "start": ent.start_char, "end": ent.end_char}
            )

    return time_entities


def parse_duration(text: str) -> Optional[timedelta]:
    """Parse duration expressions from text."""
    doc = nlp(text)
    for token in doc:
        if token.like_num and token.dep_ == "nummod":
            number = float(token.text)
            if token.nbor().text.lower() in ["hour", "hours"]:
                return timedelta(hours=number)
            elif token.nbor().text.lower() in ["minute", "minutes"]:
                return timedelta(minutes=number)
            elif token.nbor().text.lower() in ["day", "days"]:
                return timedelta(days=number)
    return None


def extract_task_metadata(text: str) -> Dict:
    """Extract metadata from task description."""
    doc = nlp(text)
    metadata = {
        "priority": "medium",
        "category": "uncategorized",
        "estimated_duration": None
    }

    # Extract priority
    for token in doc:
        if token.text.lower() in ["urgent", "important", "critical"]:
            metadata["priority"] = "high"
        elif token.text.lower() in ["low", "optional"]:
            metadata["priority"] = "low"

    # Extract category
    for ent in doc.ents:
        if ent.label_ == "ORG":
            metadata["category"] = ent.text.lower()

    # Extract duration
    duration = parse_duration(text)
    if duration:
        metadata["estimated_duration"] = duration.total_seconds() / 3600  # Convert to hours

    return metadata


def get_task_suggestions(task_history: List[Dict]) -> List[Dict]:
    """Get task suggestions based on history."""
    suggestions = []
    if not task_history:
        return suggestions

    # Group tasks by category
    category_tasks = {}
    for task in task_history:
        category = task.get("category", "uncategorized")
        if category not in category_tasks:
            category_tasks[category] = []
        category_tasks[category].append(task)

    # Generate suggestions for each category
    for category, tasks in category_tasks.items():
        if len(tasks) >= 3:  # Only suggest if we have enough data
            avg_duration = sum(t.get("duration", 0) for t in tasks) / len(tasks)
            common_time = max(
                set(t.get("time_of_day", "") for t in tasks),
                key=lambda x: list(tasks).count(x)
            )

            suggestions.append({
                "category": category,
                "suggested_duration": avg_duration,
                "preferred_time": common_time,
                "confidence": min(len(tasks) / 10, 1.0)  # Confidence based on sample size
            })

    return suggestions


def extract_event_category(text: str) -> Optional[str]:
    """Extract event category from text."""
    doc = nlp(text)
    categories = {
        "meeting": ["meeting", "call", "conference"],
        "task": ["task", "todo", "work"],
        "reminder": ["reminder", "alert", "notification"]
    }

    for category, keywords in categories.items():
        if any(keyword in text.lower() for keyword in keywords):
            return category
        else:
            continue

    return None
