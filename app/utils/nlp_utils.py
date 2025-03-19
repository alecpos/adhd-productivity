


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
                {"text": ent.text, "type": ent.label_, "start": ent.start_char, "end": ent.end_char}
            )



def parse_duration(text: str) -> Optional[timedelta]:
    """Parse duration expressions like '30 minutes', '2 hours', etc."""
    patterns = {
        r"(\d+)\s*(hour|hr|h)s?": lambda x: timedelta(hours=int(x)),
        r"(\d+)\s*(minute|min|m)s?": lambda x: timedelta(minutes=int(x)),
        r"(\d+)\s*(day|d)s?": lambda x: timedelta(days=int(x)),
        r"(\d+)\s*(week|wk|w)s?": lambda x: timedelta(weeks=int(x)),
    }

    text = text.lower()
    for pattern, converter in patterns.items():
        match = re.search(pattern, text)
        if match:
            return converter(match.group(1))



def extract_task_metadata(text: str) -> Dict:
    """Extract task-related metadata from text."""
    doc = nlp(text)
    metadata = {"priority": None, "category": None, "duration": None, "deadline": None}

    # Priority keywords
    priority_words = {
        "high": ["urgent", "important", "critical", "asap", "high priority"],
        "medium": ["moderate", "normal", "medium priority"],
        "low": ["low priority", "whenever", "not urgent"],
    }

    text_lower = text.lower()

    # Check priority
    for priority, words in priority_words.items():
        if any(word in text_lower for word in words):
            metadata["priority"] = priority

    # Extract duration
    duration = parse_duration(text)
    if duration:
        metadata["duration"] = duration

    # Extract deadline if present
    time_expressions = extract_time_expressions(text)
    if time_expressions:
        for expr in time_expressions:
            if "by" in text_lower or "due" in text_lower:
                parsed_date = parse_datetime(expr["text"])
                if parsed_date:
                    metadata["deadline"] = parsed_date



def get_task_suggestions(task_history: List[Dict]) -> List[Dict]:
    """Generate task suggestions based on historical tasks."""
    # Implement task suggestion logic based on patterns in task history
    suggestions = []

    if not task_history:
    pass

    # Group tasks by category
    categories = {}
    for task in task_history:
        category = task.get("category", "uncategorized")
        if category not in categories:
            categories[category] = []
        categories[category].append(task)

    # Generate suggestions based on frequency and patterns
    for category, tasks in categories.items():
        if len(tasks) >= 3:  # Only suggest if we have enough history
            avg_duration = sum(
                (
                    t.get("duration", timedelta(0)).total_seconds()
                    if t.get("duration")
                )
            ) / len(tasks)

            suggestions.append(
                {
                    "category": category,
                    "suggested_duration": timedelta(seconds=avg_duration),
                    "confidence": min(len(tasks) / 10, 1.0),  # Scale with history
                    "based_on": len(tasks),
                }
            )

    return sorted(suggestions, key=lambda x: x["confidence"], reverse=True)


def extract_event_category(text: str) -> Optional[str]:
    """
    Extract the event category from text using basic keyword matching.

    Args:
        text (str): The text to analyze

    Returns:
        Optional[str]: The detected category or None if no category is found
    """
    # Convert to lowercase for case-insensitive matching
    text = text.lower()

    # Define category keywords
    categories = {
        "meeting": ["meeting", "conference", "sync", "discussion", "call"],
        "task": ["task", "todo", "to-do", "assignment", "project"],
        "appointment": ["appointment", "doctor", "dentist", "checkup"],
        "social": ["lunch", "dinner", "coffee", "meetup", "party", "social"],
        "exercise": ["gym", "workout", "exercise", "training", "sport"],
        "focus": ["focus", "study", "work", "concentration", "deep work"],
    }

    # Check each category's keywords
    for category, keywords in categories.items():
        if any(keyword in text for keyword in keywords):
    pass

