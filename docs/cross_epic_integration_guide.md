# Cross-Epic Integration Guide

This guide demonstrates how to integrate and leverage all three epics of the ADHD Calendar ML system together to create powerful, comprehensive solutions for ADHD/neurodiverse users.

## Table of Contents

1. [Introduction](#introduction)
2. [System Architecture Overview](#system-architecture-overview)
3. [Integration Patterns](#integration-patterns)
4. [Common Use Cases](#common-use-cases)
5. [API Integration Examples](#api-integration-examples)
6. [Advanced Integration Scenarios](#advanced-integration-scenarios)
7. [Performance Considerations](#performance-considerations)
8. [Troubleshooting](#troubleshooting)

## Introduction

The ADHD Calendar ML system consists of three main epics:

1. **Epic 1: Temporal Pattern Recognition (TPR) Models** - Identifies productivity patterns and optimal scheduling times
2. **Epic 2: Stochastic Time Estimation Engine** - Provides realistic time estimates for tasks
3. **Epic 3: Proactive Forgetfulness and Distraction Mitigation** - Tracks commitments and provides smart reminders

While each epic can be used independently, their true power emerges when they work together. This guide shows how to integrate these components to create a comprehensive support system for ADHD/neurodiverse users.

## System Architecture Overview

![ADHD Calendar System Architecture](../assets/images/system_architecture.png)

### Core Integration Points

The three epics integrate through several key services:

1. **Scheduler Service** - Coordinates between TPR models and time estimates
2. **User Context Service** - Maintains current user context for all epics
3. **Notification Manager** - Coordinates notifications from all epics
4. **Data Pipeline** - Shares user data across epics with appropriate privacy controls

### Data Flow Diagram

```
                  ┌───────────────────┐
                  │                   │
                  │  User Interfaces  │
                  │                   │
                  └───────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────┐
│                                              │
│            API Gateway Layer                 │
│                                              │
└──────────────────────────────────────────────┘
      │               │                 │
      ▼               ▼                 ▼
┌──────────┐    ┌──────────┐     ┌──────────┐
│          │    │          │     │          │
│  Epic 1  │◄──►│  Epic 2  │◄───►│  Epic 3  │
│   TPR    │    │   Time   │     │Forgetful-│
│  Models  │    │Estimation│     │   ness   │
│          │    │          │     │          │
└──────────┘    └──────────┘     └──────────┘
      │               │                 │
      └───────────────┼─────────────────┘
                      ▼
              ┌───────────────┐
              │               │
              │   Database    │
              │               │
              └───────────────┘
```

## Integration Patterns

### 1. Sequential Integration

The most common integration pattern follows a sequential flow:

1. **Epic 1 (TPR)** → Determines optimal time for task execution
2. **Epic 2 (Time Estimation)** → Calculates realistic time requirements
3. **Epic 3 (Forgetfulness)** → Creates appropriate reminders and tracking

### 2. Parallel Integration

For some scenarios, epics can operate in parallel:

- **Epic 1 & 2** both provide inputs to the scheduler
- **Epic 2 & 3** both contribute to notification content
- **Epic 1 & 3** both inform context-aware reminders

### 3. Feedback Loop Integration

Advanced integration leverages feedback loops:

- Task completion data flows back to Epic 1 to improve pattern detection
- Actual time spent flows back to Epic 2 to improve estimates
- User reminder response flows back to Epic 3 to enhance reminder timing

## Common Use Cases

### Use Case 1: Comprehensive Task Management

This use case demonstrates a complete flow from task creation to completion:

```python
# Initialize services
from app.services.tpr_service import TPRService
from app.services.time_estimation_service import TimeEstimationService
from app.services.forgetfulness_service import ForgetfulnessService
from app.services.scheduler_service import SchedulerService

tpr = TPRService()
time_engine = TimeEstimationService()
forget = ForgetfulnessService()
scheduler = SchedulerService()

# Step 1: User creates a task (e.g., "Prepare quarterly report")
user_id = "user123"
task_description = "Prepare quarterly report"
task_category = "deep_work"

# Step 2: Epic 2 analyzes task complexity
complexity_analysis = time_engine.analyze_complexity(task_description)
print(f"Task complexity score: {complexity_analysis.score}/10")

# Step 3: Epic 1 identifies optimal time windows
optimal_windows = tpr.get_optimal_windows(
    user_id=user_id,
    task_category=task_category,
    days_ahead=3,
    min_duration_minutes=complexity_analysis.min_duration
)
print(f"Found {len(optimal_windows)} optimal time windows")

# Step 4: Epic 2 provides duration estimate
duration_estimate = time_engine.estimate_duration(
    user_id=user_id,
    task_description=task_description,
    complexity_score=complexity_analysis.score,
    task_category=task_category
)
print(f"Estimated duration: {duration_estimate.mean_minutes} minutes (±{duration_estimate.std_dev_minutes})")

# Step 5: Scheduler finds best slot considering both Epic 1 and 2 outputs
scheduled_time = scheduler.find_optimal_slot(
    user_id=user_id,
    optimal_windows=optimal_windows,
    duration_minutes=duration_estimate.mean_minutes,
    buffer_minutes=duration_estimate.buffer_minutes
)
print(f"Task scheduled for: {scheduled_time}")

# Step 6: Epic 3 creates commitment and reminders
commitment = forget.create_commitment(
    user_id=user_id,
    description=task_description,
    due_date=scheduled_time,
    estimated_duration=duration_estimate.mean_minutes,
    importance_score=complexity_analysis.importance
)

# Step 7: Epic 3 sets up smart reminders based on Epic 1 & 2 data
reminder = forget.create_smart_reminder(
    user_id=user_id,
    commitment=commitment,
    contextual_triggers=[
        "time:1_hour_before",
        "location:office",
        f"energy_level:{tpr.get_predicted_energy_level(user_id, scheduled_time)}"
    ],
    adaptive_timing=True
)
print(f"Commitment created with ID: {commitment.id}")
print(f"Smart reminder created with ID: {reminder.id}")
```

### Use Case 2: Focus Session Management

This use case shows how to create distraction-free focus sessions:

```python
# Initialize services
from app.services.tpr_service import TPRService
from app.services.time_estimation_service import TimeEstimationService
from app.services.forgetfulness_service import ForgetfulnessService
from app.services.focus_session_service import FocusSessionService

tpr = TPRService()
time_engine = TimeEstimationService()
forget = ForgetfulnessService()
focus = FocusSessionService()

# Step 1: Identify optimal focus time using Epic 1
user_id = "user123"
optimal_focus_times = tpr.get_optimal_windows(
    user_id=user_id,
    task_category="deep_focus",
    energy_threshold=0.8,
    days_ahead=1
)

if not optimal_focus_times:
    print("No optimal focus times found in the next 24 hours")
else:
    best_focus_time = optimal_focus_times[0]

    # Step 2: Get current stressors using Epic 2
    current_stressors = time_engine.detect_stressors(
        user_id=user_id,
        include_wearable_data=True
    )

    # Step 3: Check commitments during that time using Epic 3
    conflicting_commitments = forget.get_commitments(
        user_id=user_id,
        time_range=(best_focus_time.start, best_focus_time.end)
    )

    if conflicting_commitments:
        print(f"Found {len(conflicting_commitments)} conflicting commitments")
        # Reschedule or handle conflicts
    else:
        # Step 4: Create focus session integrating all three epics
        session = focus.create_focus_session(
            user_id=user_id,
            start_time=best_focus_time.start,
            duration_minutes=90,
            energy_level=tpr.get_predicted_energy_level(user_id, best_focus_time.start),
            stressor_level=current_stressors.level,
            do_not_disturb=True,
            buffer_time_minutes=time_engine.calculate_buffer(
                user_id=user_id,
                from_activity="regular",
                to_activity="deep_focus"
            ).minutes
        )

        # Step 5: Epic 3 defers non-urgent notifications
        forget.defer_notifications(
            user_id=user_id,
            time_range=(session.start_time, session.end_time),
            min_priority=8
        )

        print(f"Focus session created: {session.start_time} to {session.end_time}")
        print(f"Non-urgent notifications deferred during this period")
```

### Use Case 3: Adaptive Daily Planning

This use case demonstrates morning planning integrating all three epics:

```python
# Initialize services
from app.services.tpr_service import TPRService
from app.services.time_estimation_service import TimeEstimationService
from app.services.forgetfulness_service import ForgetfulnessService
from app.services.daily_planner_service import DailyPlannerService
import datetime

tpr = TPRService()
time_engine = TimeEstimationService()
forget = ForgetfulnessService()
planner = DailyPlannerService()

user_id = "user123"
today = datetime.datetime.now().date()

# Step 1: Epic 3 gathers all commitments for today
today_commitments = forget.get_commitments(
    user_id=user_id,
    date=today,
    include_completed=False
)
print(f"Found {len(today_commitments)} commitments for today")

# Step 2: Epic 2 estimates realistic durations for each commitment
for commitment in today_commitments:
    duration = time_engine.estimate_duration(
        user_id=user_id,
        task_description=commitment.description,
        commitment_id=commitment.id
    )
    commitment.estimated_duration = duration.mean_minutes
    commitment.buffer_time = duration.buffer_minutes

# Step 3: Epic 1 provides today's energy forecast
energy_forecast = tpr.get_daily_energy_forecast(
    user_id=user_id,
    date=today,
    granularity_minutes=30
)

# Step 4: Generate optimized schedule using all three epics
daily_schedule = planner.generate_optimized_schedule(
    user_id=user_id,
    date=today,
    commitments=today_commitments,
    energy_forecast=energy_forecast,
    stressor_forecast=time_engine.get_stressor_forecast(user_id, today),
    optimization_goal="balanced"  # Options: productivity, wellbeing, balanced
)

# Step 5: Epic 3 creates adaptive reminders based on the schedule
for block in daily_schedule.time_blocks:
    if block.commitment_id:
        reminder = forget.create_smart_reminder(
            user_id=user_id,
            commitment_id=block.commitment_id,
            contextual_triggers=[
                f"time:{(block.start_time - datetime.timedelta(minutes=15)).isoformat()}",
                f"energy_level:{block.expected_energy_level}",
                "activity:previous_task_completion"
            ]
        )

print(f"Optimized daily schedule created with {len(daily_schedule.time_blocks)} time blocks")
print(f"Smart reminders created for all scheduled commitments")
```

## API Integration Examples

### Basic Integration Client

Here's a simple client class that integrates all three epics:

```python
class ADHDCalendarClient:
    def __init__(self, api_key, base_url="https://api.adhdcalendar.com/v1"):
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        })

    # Epic 1 (TPR) Methods
    def get_productivity_patterns(self, user_id):
        return self.session.get(f"{self.base_url}/productivity-patterns/{user_id}").json()

    def get_optimal_times(self, user_id, task_type, days_ahead=1):
        return self.session.get(
            f"{self.base_url}/productivity-patterns/{user_id}/optimal-times",
            params={"task_type": task_type, "days_ahead": days_ahead}
        ).json()

    # Epic 2 (Time Estimation) Methods
    def estimate_task_duration(self, user_id, task_description, task_type=None):
        return self.session.post(
            f"{self.base_url}/time-estimation/{user_id}/estimate",
            json={"description": task_description, "task_type": task_type}
        ).json()

    def get_buffer_recommendation(self, user_id, from_task_type, to_task_type):
        return self.session.get(
            f"{self.base_url}/time-estimation/{user_id}/buffer",
            params={"from_type": from_task_type, "to_type": to_task_type}
        ).json()

    # Epic 3 (Forgetfulness) Methods
    def detect_commitments(self, user_id, text):
        return self.session.post(
            f"{self.base_url}/commitments/{user_id}/detect",
            json={"text": text}
        ).json()

    def create_smart_reminder(self, user_id, commitment_id, triggers=None):
        return self.session.post(
            f"{self.base_url}/reminders/{user_id}",
            json={"commitment_id": commitment_id, "triggers": triggers or []}
        ).json()

    # Cross-Epic Integration Methods
    def create_optimized_task(self, user_id, task_description, task_type=None, due_by=None):
        """Creates a task with optimized scheduling using all three epics."""
        # Step 1: Estimate duration (Epic 2)
        duration_estimate = self.estimate_task_duration(user_id, task_description, task_type)

        # Step 2: Find optimal time (Epic 1)
        optimal_times = self.get_optimal_times(user_id, task_type or "default")

        # Step 3: Select best time before due date if specified
        if due_by and optimal_times:
            selected_time = next(
                (t for t in optimal_times if t["start_time"] < due_by),
                optimal_times[0]
            )
        elif optimal_times:
            selected_time = optimal_times[0]
        else:
            # Fallback if no optimal times found
            selected_time = {"start_time": datetime.datetime.now().isoformat()}

        # Step 4: Create commitment (Epic 3)
        commitment = self.session.post(
            f"{self.base_url}/commitments/{user_id}",
            json={
                "description": task_description,
                "scheduled_time": selected_time["start_time"],
                "estimated_duration": duration_estimate["mean_minutes"],
                "task_type": task_type
            }
        ).json()

        # Step 5: Create smart reminder (Epic 3)
        reminder = self.create_smart_reminder(
            user_id,
            commitment["id"],
            triggers=["time:1_hour_before", "energy:medium_high"]
        )

        return {
            "commitment": commitment,
            "reminder": reminder,
            "scheduled_time": selected_time["start_time"],
            "estimated_duration": duration_estimate
        }
```

### Integration with External Calendars

This example shows integration with Google Calendar:

```python
def sync_with_google_calendar(user_id, google_credentials, adhd_calendar_client):
    """Syncs ADHD Calendar with Google Calendar using all three epics."""
    # Set up Google Calendar API
    google_calendar = GoogleCalendarAPI(google_credentials)

    # Step 1: Get upcoming Google Calendar events
    upcoming_events = google_calendar.get_upcoming_events(max_results=20)

    # Step 2: Process each event through all three epics
    for event in upcoming_events:
        # Skip events that are already processed (check for custom property)
        if event.get('extendedProperties', {}).get('private', {}).get('adhd_calendar_processed'):
            continue

        # Step 3: Analyze event complexity (Epic 2)
        complexity = adhd_calendar_client.estimate_task_duration(
            user_id,
            f"{event['summary']} - {event.get('description', '')}"
        )

        # Step 4: Check for scheduling optimizations (Epic 1)
        if not event.get('extendedProperties', {}).get('private', {}).get('adhd_calendar_locked'):
            optimal_times = adhd_calendar_client.get_optimal_times(
                user_id,
                "meeting" if "meeting" in event['summary'].lower() else "appointment",
                days_ahead=7
            )

            # Suggest schedule optimization if better time found
            start_time = parser.parse(event['start']['dateTime'])
            for optimal_time in optimal_times:
                optimal_start = parser.parse(optimal_time['start_time'])
                # If within 3 hours of original time but better energy match
                time_diff = abs((optimal_start - start_time).total_seconds() / 3600)
                if time_diff < 3 and optimal_time['energy_score'] > 0.7:
                    # Suggest reschedule for non-fixed events
                    print(f"Suggested reschedule: {event['summary']} to {optimal_start}")
                    # Could implement automatic rescheduling here
                    break

        # Step 5: Create commitment in ADHD Calendar (Epic 3)
        commitment = adhd_calendar_client.session.post(
            f"{adhd_calendar_client.base_url}/commitments/{user_id}",
            json={
                "description": event['summary'],
                "details": event.get('description', ''),
                "scheduled_time": event['start']['dateTime'],
                "estimated_duration": complexity["mean_minutes"],
                "source": "google_calendar",
                "external_id": event['id']
            }
        ).json()

        # Step 6: Calculate buffer times (Epic 2)
        buffer = adhd_calendar_client.get_buffer_recommendation(
            user_id,
            "previous_activity",
            "meeting" if "meeting" in event['summary'].lower() else "appointment"
        )

        # Step 7: Create smart reminder with appropriate timing (Epic 3)
        reminder = adhd_calendar_client.create_smart_reminder(
            user_id,
            commitment["id"],
            triggers=[
                f"time:{buffer['minutes']}_minutes_before",
                "location:relevant",
                "preparation_needed:true"
            ]
        )

        # Step 8: Mark event as processed in Google Calendar
        google_calendar.update_event_properties(
            event['id'],
            {
                'adhd_calendar_processed': 'true',
                'adhd_calendar_commitment_id': commitment['id'],
                'adhd_calendar_complexity': str(complexity['score']),
                'adhd_calendar_buffer_minutes': str(buffer['minutes'])
            }
        )

    return {
        "events_processed": len(upcoming_events),
        "commitments_created": len(upcoming_events)
    }
```

## Advanced Integration Scenarios

### 1. Mental Health Monitoring Across Epics

This example shows how to implement cross-epic mental health monitoring:

```python
def analyze_mental_health_indicators(user_id, start_date, end_date, client):
    """Analyze mental health indicators by combining data from all three epics."""
    # Get data from all three epics
    productivity_data = client.session.get(
        f"{client.base_url}/productivity-patterns/{user_id}/analysis",
        params={"start_date": start_date, "end_date": end_date}
    ).json()

    time_estimation_data = client.session.get(
        f"{client.base_url}/time-estimation/{user_id}/history",
        params={"start_date": start_date, "end_date": end_date}
    ).json()

    commitment_data = client.session.get(
        f"{client.base_url}/commitments/{user_id}/completion",
        params={"start_date": start_date, "end_date": end_date}
    ).json()

    # Extract mental health indicators
    indicators = {
        # From Epic 1
        "productivity_variance": productivity_data["productivity_variance"],
        "energy_instability": productivity_data["energy_instability"],
        "circadian_disruption": productivity_data["circadian_disruption"],

        # From Epic 2
        "time_blindness_score": time_estimation_data["time_blindness_score"],
        "stressor_frequency": time_estimation_data["stressor_frequency"],
        "context_sensitivity": time_estimation_data["context_sensitivity"],

        # From Epic 3
        "commitment_completion_rate": commitment_data["completion_rate"],
        "forgotten_commitments_rate": commitment_data["forgotten_rate"],
        "reminder_effectiveness": commitment_data["reminder_effectiveness"]
    }

    # Calculate composite scores
    indicators["overall_functioning"] = (
        indicators["productivity_variance"] * 0.2 +
        indicators["commitment_completion_rate"] * 0.3 +
        (1 - indicators["time_blindness_score"]) * 0.2 +
        (1 - indicators["forgotten_commitments_rate"]) * 0.3
    )

    indicators["stress_level"] = (
        indicators["stressor_frequency"] * 0.4 +
        indicators["energy_instability"] * 0.3 +
        indicators["circadian_disruption"] * 0.3
    )

    return indicators
```

### 2. Cross-Epic Machine Learning Pipeline

This example shows a unified ML pipeline that leverages data from all epics:

```python
def train_cross_epic_model(user_id, trainer_service):
    """Trains a unified ML model using data from all three epics."""
    # Define features from each epic
    epic1_features = [
        "daily_energy_curve",
        "productivity_time_blocks",
        "focus_duration_history",
        "task_completion_timestamps"
    ]

    epic2_features = [
        "estimation_accuracy_history",
        "task_complexity_scores",
        "stressor_presence_history",
        "buffer_effectiveness"
    ]

    epic3_features = [
        "commitment_types",
        "reminder_response_times",
        "forgotten_commitment_characteristics",
        "completion_success_rate"
    ]

    # Gather training data from all epics
    training_data = trainer_service.gather_cross_epic_data(
        user_id=user_id,
        epic1_features=epic1_features,
        epic2_features=epic2_features,
        epic3_features=epic3_features,
        days=90  # Use last 90 days of data
    )

    # Define target variables
    targets = [
        "optimal_scheduling_time",     # Epic 1 target
        "realistic_duration",          # Epic 2 target
        "effective_reminder_timing"    # Epic 3 target
    ]

    # Train unified model
    model = trainer_service.train_unified_model(
        user_id=user_id,
        training_data=training_data,
        target_variables=targets,
        model_type="xgboost",
        hyperparameters={
            "max_depth": 6,
            "learning_rate": 0.01,
            "n_estimators": 100
        }
    )

    # Deploy model for user
    model_id = trainer_service.deploy_model(
        user_id=user_id,
        model=model,
        version_name="unified-adhd-assistant-v1"
    )

    return {
        "model_id": model_id,
        "features_used": len(epic1_features) + len(epic2_features) + len(epic3_features),
        "training_samples": len(training_data),
        "metrics": model.metrics
    }
```

## Performance Considerations

When integrating all three epics, consider these performance optimizations:

### 1. Caching Strategy

```python
# Example of cross-epic caching
from app.cache.redis_manager import RedisCacheManager

cache = RedisCacheManager(
    expiration_time=3600,  # 1 hour default
    custom_expirations={
        "productivity_patterns": 86400,    # Epic 1: 24 hours
        "time_estimates": 3600,           # Epic 2: 1 hour
        "commitments": 1800               # Epic 3: 30 minutes
    }
)

# Use in services
tpr_service = TPRService(cache_manager=cache)
time_service = TimeEstimationService(cache_manager=cache)
forget_service = ForgetfulnessService(cache_manager=cache)
```

### 2. Batch Processing

```python
# Example of cross-epic batch processing
def batch_process_new_tasks(user_id, task_list, services):
    """Process multiple tasks at once across all epics."""
    # Step 1: Batch complexity analysis (Epic 2)
    complexity_results = services.time_engine.batch_analyze_complexity(
        [task["description"] for task in task_list]
    )

    # Step 2: Get optimal times for all task types (Epic 1)
    unique_task_types = set(task.get("type", "default") for task in task_list)
    optimal_times = {}
    for task_type in unique_task_types:
        optimal_times[task_type] = services.tpr.get_optimal_windows(
            user_id=user_id,
            task_category=task_type,
            days_ahead=7
        )

    # Step 3: Batch create commitments (Epic 3)
    commitments = []
    for i, task in enumerate(task_list):
        task_type = task.get("type", "default")
        best_time = optimal_times[task_type][0] if optimal_times[task_type] else None

        commitments.append({
            "description": task["description"],
            "scheduled_time": best_time["start_time"] if best_time else None,
            "estimated_duration": complexity_results[i]["mean_minutes"],
            "complexity_score": complexity_results[i]["score"],
            "task_type": task_type
        })

    created_commitments = services.forget.batch_create_commitments(user_id, commitments)

    # Step 4: Batch create reminders (Epic 3)
    reminder_configs = []
    for commitment in created_commitments:
        reminder_configs.append({
            "commitment_id": commitment["id"],
            "triggers": ["time:1_hour_before", "energy:appropriate"]
        })

    created_reminders = services.forget.batch_create_reminders(user_id, reminder_configs)

    return {
        "tasks_processed": len(task_list),
        "commitments_created": len(created_commitments),
        "reminders_created": len(created_reminders)
    }
```

### 3. Asynchronous Processing

```python
# Example of asynchronous cross-epic processing
async def async_optimize_day(user_id, date, services):
    """Asynchronously optimize a user's day using all three epics."""
    # Run Epic 1 and Epic 3 operations concurrently
    energy_forecast_future = asyncio.create_task(
        services.tpr.async_get_daily_energy_forecast(user_id, date)
    )

    commitments_future = asyncio.create_task(
        services.forget.async_get_commitments(user_id, date)
    )

    # Wait for both to complete
    energy_forecast = await energy_forecast_future
    commitments = await commitments_future

    # Process commitments through Epic 2
    duration_futures = []
    for commitment in commitments:
        duration_futures.append(
            services.time_engine.async_estimate_duration(
                user_id, commitment.description, commitment_id=commitment.id
            )
        )

    # Wait for all duration estimates
    duration_estimates = await asyncio.gather(*duration_futures)

    # Update commitments with duration estimates
    for i, commitment in enumerate(commitments):
        commitment.estimated_duration = duration_estimates[i].mean_minutes
        commitment.buffer_time = duration_estimates[i].buffer_minutes

    # Generate schedule
    schedule = await services.planner.async_generate_optimized_schedule(
        user_id=user_id,
        date=date,
        commitments=commitments,
        energy_forecast=energy_forecast
    )

    return schedule
```

## Troubleshooting

Common cross-epic integration issues and solutions:

### 1. Data Consistency Issues

**Problem**: Inconsistent data between epics (e.g., completion status mismatch)

**Solution**:
```python
def reconcile_cross_epic_data(user_id, services):
    """Reconcile data inconsistencies between epics."""
    # Get data from all epics
    tpr_data = services.tpr.get_user_data(user_id)
    time_data = services.time_engine.get_user_data(user_id)
    forget_data = services.forget.get_user_data(user_id)

    # Check for task completion inconsistencies
    for task_id in tpr_data["completed_tasks"]:
        if task_id in forget_data["commitments"]:
            commitment = forget_data["commitments"][task_id]
            if commitment["status"] != "completed":
                # Fix inconsistency
                services.forget.update_commitment_status(
                    user_id, task_id, "completed",
                    completion_time=tpr_data["completed_tasks"][task_id]["completion_time"]
                )
                print(f"Fixed commitment status for {task_id}")

    # Check for duration inconsistencies
    for task_id in time_data["task_durations"]:
        if task_id in forget_data["commitments"]:
            commitment = forget_data["commitments"][task_id]
            if commitment["actual_duration"] != time_data["task_durations"][task_id]["actual"]:
                # Fix inconsistency
                services.forget.update_commitment_duration(
                    user_id, task_id,
                    actual_duration=time_data["task_durations"][task_id]["actual"]
                )
                print(f"Fixed duration for {task_id}")

    # Add other reconciliation checks as needed

    return {
        "inconsistencies_fixed": {
            "status": len(tpr_data["completed_tasks"]),
            "duration": len(time_data["task_durations"])
        }
    }
```

### 2. Integration Timing Issues

**Problem**: Timing issues between epic operations (e.g., reminder created before time estimation completes)

**Solution**:
```python
def ensure_operation_order(operation_id, services):
    """Ensure operations across epics happen in correct order."""
    operation = services.operation_manager.get_operation(operation_id)

    # Check prerequisites
    for prerequisite in operation["prerequisites"]:
        prereq_status = services.operation_manager.get_operation_status(prerequisite)
        if prereq_status != "completed":
            # Wait for prerequisite to complete
            services.operation_manager.wait_for_operation(prerequisite, timeout_seconds=30)

    # Execute operation
    result = services.operation_manager.execute_operation(operation_id)

    # Update dependent operations
    for dependent in operation["dependents"]:
        services.operation_manager.update_prerequisite_status(
            dependent, operation_id, "completed"
        )

    return result
```

### 3. Performance Bottlenecks

**Problem**: Cross-epic operations causing performance bottlenecks

**Solution**:
```python
def optimize_cross_epic_performance(user_id, services):
    """Identify and address cross-epic performance bottlenecks."""
    # Run performance analysis
    performance = services.performance_analyzer.analyze_operations(user_id, days=7)

    bottlenecks = performance["bottlenecks"]
    optimizations = []

    for bottleneck in bottlenecks:
        if bottleneck["type"] == "excessive_db_queries":
            # Implement caching for this operation
            services.cache_manager.add_cache_rule(
                operation=bottleneck["operation"],
                expiration_seconds=bottleneck["recommended_cache_time"]
            )
            optimizations.append(f"Added caching for {bottleneck['operation']}")

        elif bottleneck["type"] == "sequential_operations":
            # Convert to parallel processing
            services.operation_manager.mark_as_parallelizable(
                operations=bottleneck["operations"]
            )
            optimizations.append(f"Parallelized {len(bottleneck['operations'])} operations")

        elif bottleneck["type"] == "excessive_computation":
            # Implement lazy loading
            services.feature_manager.enable_lazy_loading(
                feature=bottleneck["feature"]
            )
            optimizations.append(f"Enabled lazy loading for {bottleneck['feature']}")

    return {
        "bottlenecks_found": len(bottlenecks),
        "optimizations_applied": optimizations
    }
```

---

This guide provides a comprehensive framework for integrating all three epics of the ADHD Calendar ML system. By understanding the integration patterns, common use cases, and performance considerations, you can create powerful, unified solutions that leverage the full capabilities of the system to support ADHD/neurodiverse users.
