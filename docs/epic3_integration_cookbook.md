# Epic 3: Integration Cookbook - Proactive Forgetfulness and Distraction Mitigation

## Overview

This cookbook provides comprehensive, practical examples for integrating the Proactive Forgetfulness and Distraction Mitigation features into your applications. These tools help users with ADHD/neurodiversity overcome challenges with forgetfulness and distraction by detecting commitments, cross-referencing information, providing proactive dialogues, and implementing contextually-aware reminder systems.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start Guide](#quick-start-guide)
3. [Commitment Detection System](#commitment-detection-system)
4. [Cross-Reference System](#cross-reference-system)
5. [NLP Dialogue System](#nlp-dialogue-system)
6. [Contextual Reminder System](#contextual-reminder-system)
7. [Combining Components](#combining-components)
8. [Troubleshooting](#troubleshooting)
9. [Performance Optimization](#performance-optimization)
10. [Privacy and Security](#privacy-and-security)

## Prerequisites

- Python 3.9+
- Required packages installed (see `requirements.txt`)
- Access to the ADHD Calendar API
- Basic understanding of NLP and ML concepts

```bash
# Install required dependencies
pip install -r requirements.txt
```

## Quick Start Guide

Here's how to quickly integrate the Proactive Forgetfulness and Distraction Mitigation features:

```python
from app.models.forgetfulness.commitment_detector import CommitmentDetector
from app.models.forgetfulness.reminder_system import SmartReminderSystem
from app.services.forgetfulness_service import ForgetfulnessService

# Initialize the service
forget_service = ForgetfulnessService()

# Detect commitments in text
user_id = "user123"
text = "I need to call John tomorrow about the project proposal. Also, I should email Sarah by Friday."

# Extract commitments
commitments = forget_service.detect_commitments(user_id, text)
for commitment in commitments:
    print(f"Commitment: {commitment.description}")
    print(f"Due: {commitment.due_date}")
    print(f"Priority: {commitment.priority}/10")
    print(f"People involved: {commitment.people}")
    print("---")

# Set up a smart reminder
reminder = forget_service.create_smart_reminder(
    user_id=user_id,
    commitment=commitments[0],
    contextual_triggers=["location:office", "time:morning"]
)
print(f"Reminder created: {reminder.id}")
```

## Commitment Detection System

### Basic Integration

```python
from app.models.forgetfulness.commitment_detector import CommitmentDetector

# Initialize the detector
detector = CommitmentDetector()

# Detect commitments in text
journal_entry = """
Had a meeting with the team today. I promised to review the designs by Wednesday.
Also, I need to call the doctor to schedule that appointment sometime next week.
Don't forget to pick up groceries tomorrow evening.
"""

commitments = detector.detect_commitments(journal_entry)

for commitment in commitments:
    print(f"Description: {commitment.description}")
    print(f"Due date: {commitment.due_date}")
    print(f"Confidence: {commitment.confidence_score}")
    print(f"Type: {commitment.commitment_type}")
    print("---")
```

### Advanced Usage: Custom Training and Specialized Detection

```python
# Configure custom commitment types
custom_commitment_types = {
    "work_deliverable": {
        "keywords": ["submit", "deliver", "finish", "complete"],
        "entities": ["project", "report", "document", "presentation"],
        "importance_base": 0.8
    },
    "social_obligation": {
        "keywords": ["call", "meet", "attend", "join"],
        "entities": ["friend", "family", "party", "event"],
        "importance_base": 0.7
    }
}

# Initialize with custom configuration
detector = CommitmentDetector(custom_commitment_types=custom_commitment_types)

# Train with user-specific data
import pandas as pd

training_data = pd.DataFrame({
    'text': [
        "I need to finish the report by Friday",
        "Going to meet with Sarah for coffee next Tuesday",
        "Don't forget to buy cat food"
    ],
    'is_commitment': [True, True, True],
    'commitment_type': ['work_deliverable', 'social_obligation', 'personal_task'],
    'due_date': ['Friday', 'next Tuesday', None],
    'importance': [8, 6, 7]
})

# Fine-tune the model
detector.train(
    training_data,
    epochs=10,
    learning_rate=0.001,
    validation_split=0.2
)

# Save the trained model
detector.save_model('user_specific_commitment_model.h5')

# Load a previously trained model
detector.load_model('user_specific_commitment_model.h5')
```

## Cross-Reference System

### Basic Integration

```python
from app.models.forgetfulness.cross_reference import CrossReferenceSystem

# Initialize the system
cross_ref = CrossReferenceSystem()

# Add a newly detected commitment
commitment = {
    "id": "commit123",
    "user_id": "user123",
    "description": "Review project proposal",
    "due_date": "2023-06-20",
    "people": ["John", "Sarah"],
    "project": "Client XYZ"
}

# Find related items for cross-referencing
related_items = cross_ref.find_related_items(
    user_id="user123",
    commitment=commitment,
    sources=["calendar", "email", "notes"]
)

print(f"Found {len(related_items)} related items:")
for item in related_items:
    print(f"- {item.type}: {item.title} ({item.relevance_score})")
    print(f"  Source: {item.source}")
    print(f"  Date: {item.date}")
```

### Advanced Usage: Semantic Matching and Custom Sources

```python
# Configure custom data sources
custom_sources = {
    "slack": {
        "api_key": "YOUR_SLACK_API_KEY",
        "channels": ["team-projects", "general"],
        "search_depth_days": 30,
        "weight": 0.8
    },
    "notion": {
        "api_key": "YOUR_NOTION_API_KEY",
        "databases": ["projects", "tasks"],
        "weight": 0.9
    }
}

# Initialize with custom configuration
cross_ref = CrossReferenceSystem(custom_sources=custom_sources)

# Set semantic matching parameters
semantic_params = {
    "model": "sentence-transformer",
    "similarity_threshold": 0.75,
    "max_results_per_source": 5,
    "boost_recency": True
}

# Find related items with advanced parameters
advanced_related_items = cross_ref.find_related_items_advanced(
    user_id="user123",
    commitment=commitment,
    semantic_params=semantic_params,
    context_aware=True
)

# Merge or link related commitments
merged_commitment = cross_ref.merge_commitments(
    primary_commitment_id="commit123",
    secondary_commitment_ids=["commit124", "commit127"],
    merge_strategy="smart"  # Options: "combine", "smart", "primary_first"
)

print(f"Merged commitment: {merged_commitment.description}")
print(f"References: {len(merged_commitment.references)}")
```

## NLP Dialogue System

### Basic Integration

```python
from app.models.forgetfulness.dialogue_system import ForgotAnythingDialogue

# Initialize the dialogue system
dialogue = ForgotAnythingDialogue()

# Get a "Forgot anything?" prompt
user_id = "user123"
departure_context = {
    "location": "office",
    "time": "17:30",
    "destination": "home",
    "calendar_events": ["Meeting with team", "Call with client"]
}

# Generate a contextual prompt
prompt = dialogue.generate_prompt(
    user_id=user_id,
    context=departure_context
)

print(f"Contextual prompt: {prompt.message}")
print(f"Prompt triggered by: {prompt.trigger}")
print(f"Items to remember: {prompt.items}")
```

### Advanced Usage: Custom Prompts and Response Processing

```python
# Configure custom prompt templates
custom_templates = {
    "leaving_work": [
        "Before you leave work, have you remembered to {item_list}?",
        "I notice you're leaving the office. Don't forget to {item_list}!",
        "Quick check before you go: {item_list}"
    ],
    "morning_routine": [
        "Good morning! For today, remember to {item_list}",
        "Starting your day? Here's what's on your plate: {item_list}",
        "Morning checklist: {item_list}"
    ]
}

# Initialize with custom configuration
dialogue = ForgotAnythingDialogue(custom_templates=custom_templates)

# Generate prompt with specific template
custom_prompt = dialogue.generate_prompt(
    user_id=user_id,
    context=departure_context,
    template_key="leaving_work",
    prioritize_items=True
)

# Process user response to a prompt
user_response = "I've taken care of the report, but I still need to call John"
processed_response = dialogue.process_response(
    user_id=user_id,
    prompt_id=custom_prompt.id,
    response_text=user_response
)

# Update commitments based on response
completed_commitments = processed_response.completed_items
new_commitments = processed_response.new_items

for commitment in new_commitments:
    print(f"New commitment detected: {commitment.description}")
```

## Contextual Reminder System

### Basic Integration

```python
from app.models.forgetfulness.reminder_system import SmartReminderSystem
import datetime

# Initialize the reminder system
reminder_system = SmartReminderSystem()

# Create a smart reminder
user_id = "user123"
commitment = {
    "id": "commit123",
    "description": "Call doctor to schedule appointment",
    "priority": 8,
    "due_date": datetime.datetime.now() + datetime.timedelta(days=2)
}

# Create a context-aware reminder
reminder = reminder_system.create_reminder(
    user_id=user_id,
    commitment=commitment,
    contextual_triggers=[
        "time:morning",
        "location:home",
        "activity:idle"
    ]
)

print(f"Reminder created: {reminder.id}")
print(f"Triggers: {reminder.triggers}")
print(f"Delivery strategy: {reminder.delivery_strategy}")
```

### Advanced Usage: Adaptive Reminders and Multi-Channel Delivery

```python
# Create an adaptive reminder with complex rules
adaptive_reminder = reminder_system.create_adaptive_reminder(
    user_id=user_id,
    commitment=commitment,
    base_importance=8,
    escalation_strategy={
        "start_hours_before": 48,
        "frequency_increase": "exponential",
        "channel_progression": ["notification", "email", "sms"],
        "max_reminders": 5
    },
    contextual_rules=[
        {
            "condition": "location:car",
            "action": "read_aloud",
            "priority_modifier": 1.5
        },
        {
            "condition": "focus_state:deep_work",
            "action": "delay",
            "delay_minutes": 30
        },
        {
            "condition": "stress_level:high",
            "action": "simplify_message",
            "priority_modifier": 0.8
        }
    ],
    delivery_preferences={
        "notification": {
            "app_id": "com.example.calendar",
            "sound": "gentle_chime",
            "vibration": True
        },
        "email": {
            "address": "user@example.com",
            "template": "friendly_reminder"
        },
        "sms": {
            "phone": "+1234567890",
            "prefix": "ADHD Calendar:"
        }
    }
)

# Test if a reminder should trigger in the current context
current_context = {
    "location": "home",
    "time": datetime.datetime.now(),
    "focus_state": "browsing",
    "stress_level": "medium",
    "device_status": "active"
}

should_trigger = reminder_system.should_reminder_trigger(
    reminder_id=adaptive_reminder.id,
    current_context=current_context
)

print(f"Should trigger now: {should_trigger}")
if should_trigger:
    print(f"Trigger confidence: {should_trigger.confidence}")
    print(f"Recommended channel: {should_trigger.recommended_channel}")

# Configure learning from user responses
reminder_system.configure_learning(
    user_id=user_id,
    learn_from_dismissals=True,
    learn_from_completions=True,
    adaptive_timing=True,
    feedback_weight=0.3
)
```

## Combining Components

Here's how to combine all components of the Proactive Forgetfulness and Distraction Mitigation system:

```python
from app.services.forgetfulness_service import ForgetfulnessService
import datetime

# Initialize the service
forget_service = ForgetfulnessService()

# Create a comprehensive forgetfulness management flow
user_id = "user123"

# 1. Monitor for commitments in user input
journal_text = """
Had a great meeting with the team today. I promised to send the draft proposal
by Thursday. Also need to remember to call Mom on her birthday next Tuesday.
Should pick up some groceries on the way home tonight.
"""

# Detect commitments
detected_commitments = forget_service.detect_commitments(
    user_id=user_id,
    text=journal_text
)

# 2. Cross-reference with existing information
for commitment in detected_commitments:
    # Find related information
    related_items = forget_service.find_related_items(
        user_id=user_id,
        commitment=commitment
    )
    
    # If significant conflicts or duplicates, handle them
    if related_items.has_conflicts:
        resolved_commitment = forget_service.resolve_conflicts(
            commitment=commitment,
            conflicting_items=related_items.conflicts
        )
    else:
        # Store the commitment
        stored_commitment = forget_service.store_commitment(commitment)
        
        # 3. Create smart reminders for each commitment
        reminder = forget_service.create_smart_reminder(
            user_id=user_id,
            commitment=stored_commitment,
            importance_factors={
                "deadline_proximity": 0.8,
                "explicit_importance": 0.9,
                "people_involved": 0.7,
                "repetition_in_text": 0.5
            }
        )

# 4. Generate a departure checklist when appropriate
departure_context = {
    "location": "office",
    "time": "17:30",
    "destination": "home",
    "heading_out": True
}

checklist = forget_service.generate_departure_checklist(
    user_id=user_id,
    context=departure_context
)

print("Departure Checklist:")
for item in checklist.items:
    print(f"- {item.description} (Priority: {item.priority})")

# 5. Schedule regular check-ins for important commitments
forget_service.schedule_commitment_checkins(
    user_id=user_id,
    frequency="daily",
    preferred_time="20:00",
    max_items=5,
    include_categories=["work", "health", "family"]
)
```

## Troubleshooting

Common issues and their solutions:

1. **Low Confidence Commitment Detection**
   ```
   Warning: Low confidence commitment detection (score: 0.45)
   ```
   **Solution**: Use `detector.detect_commitments(text, min_confidence=0.4)` to adjust the confidence threshold, or provide more context with `additional_context={"previous_messages": [...]}`.

2. **Missing Due Dates**
   ```
   Warning: Could not determine due date for commitment
   ```
   **Solution**: Provide a default timeframe with `detector.detect_commitments(text, default_timeframe_days=7)` or explicitly parse dates with `detect_commitments(text, force_date_parsing=True)`.

3. **Reminder Trigger Issues**
   ```
   Error: Reminder not triggering in expected context
   ```
   **Solution**: Debug reminder triggers with `reminder_system.validate_trigger_rules(reminder_id)` and adjust sensitivity with `reminder_system.update_reminder(reminder_id, trigger_sensitivity=0.7)`.

## Performance Optimization

For large-scale deployments:

```python
# Configure the service for high performance
from app.services.forgetfulness_service import ForgetfulnessService
from app.cache.redis_manager import RedisCacheManager

# Initialize cache
cache_manager = RedisCacheManager(
    expiration_time=1800,  # Cache results for 30 minutes
    max_cache_size_mb=100
)

# Create optimized service
forget_service = ForgetfulnessService(
    cache_manager=cache_manager,
    batch_processing=True,
    preload_user_models=True
)

# Configure batch processing for dialogue generation
user_ids = ["user1", "user2", "user3", "user4"]
contexts = [
    {"location": "home", "time": "08:00", "activity": "starting_day"},
    {"location": "office", "time": "17:30", "activity": "ending_day"},
    {"location": "car", "time": "12:15", "activity": "traveling"},
    {"location": "home", "time": "22:00", "activity": "evening"}
]

# Batch generate prompts
batch_prompts = forget_service.batch_generate_prompts(
    user_ids=user_ids,
    contexts=contexts,
    parallel_processing=True,
    max_workers=4
)
```

## Privacy and Security

Ensure secure integration:

```python
from app.security.encryption import DataEncryption
from app.models.forgetfulness.secure_client import SecureForgetfulnessClient

# Initialize encryption
encryption = DataEncryption(encryption_key=config.SECRET_KEY)

# Create secure client
secure_client = SecureForgetfulnessClient(
    user_id=user_id,
    encryption_service=encryption,
    secure_data_transfer=True,
    privacy_level="high"
)

# Configure privacy settings for commitment detection
secure_client.configure_privacy(
    store_raw_text=False,
    anonymize_people_names=True,
    redact_sensitive_info=True,
    sensitive_categories=["medical", "financial"]
)

# Use secure client for handling sensitive information
secure_commitments = secure_client.detect_commitments_secure(
    text="I need to call Dr. Smith about my test results and transfer $500 to my savings account",
    apply_privacy_filters=True
)

# Configure data retention
secure_client.set_data_retention_policy(
    commitment_retention_days=90,
    reminder_retention_days=30,
    anonymize_after_days=60
)
```

---

For additional examples and advanced use cases, refer to the [API Documentation](epic3_api.md) and [Implementation Details](epic3_implementation.md). 