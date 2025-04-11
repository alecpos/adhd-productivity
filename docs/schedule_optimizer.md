# ML-Powered Schedule Optimizer

The Schedule Optimizer uses machine learning to create optimal daily schedules based on your work patterns, energy levels, and historical performance data.

## Features

- Learns from your historical performance
- Adapts to your energy patterns
- Optimizes break distribution
- Respects task priorities and dependencies
- Considers work hours and constraints
- Provides effectiveness predictions

## Usage

### Basic Schedule Optimization

```python
from datetime import datetime, time
from app.models.time_block_model import BlockType, BlockPriority

# Create a schedule optimization request
request = {
    "user_id": "your_user_id",
    "tasks": [
        {
            "title": "Deep Work Session",
            "description": "Focus on coding",
            "block_type": BlockType.FOCUS,
            "priority": BlockPriority.HIGH,
            "estimated_duration": 90,
            "energy_requirement": 8,
            "is_flexible": True
        },
        {
            "title": "Team Meeting",
            "description": "Weekly sync",
            "block_type": BlockType.MEETING,
            "priority": BlockPriority.MEDIUM,
            "estimated_duration": 60,
            "preferred_time": "2024-01-10T14:00:00",
            "is_flexible": False
        }
    ],
    "date": "2024-01-10",
    "work_hours": {
        "start": "09:00",
        "end": "17:00",
        "breaks": [
            {
                "start": "12:00",
                "end": "13:00"
            }
        ]
    }
}

# Make API request
response = await client.post("/schedule/optimal", json=request)
optimized_schedule = response.json()
```

### With Energy Patterns

```python
# Add energy pattern to optimize task placement
request["energy_pattern"] = {
    "pattern_type": "morning",
    "peak_hours": [
        {
            "start": "09:00",
            "end": "11:00"
        }
    ],
    "low_energy_periods": [
        {
            "start": "14:00",
            "end": "15:00"
        }
    ]
}
```

## Task Properties

| Property | Type | Description |
|----------|------|-------------|
| title | string | Task title |
| description | string | Optional task description |
| block_type | BlockType | Type of block (TASK, BREAK, FOCUS, MEETING, etc.) |
| priority | BlockPriority | Task priority (LOW, MEDIUM, HIGH, URGENT) |
| estimated_duration | int | Estimated duration in minutes |
| energy_requirement | int | Required energy level (1-10) |
| focus_requirement | int | Required focus level (1-10) |
| preferred_time | datetime | Preferred start time (optional) |
| is_flexible | bool | Whether the task timing is flexible |
| dependencies | List[str] | IDs of tasks this task depends on |

## Response Format

```python
[
    {
        "start_time": "2024-01-10T09:00:00",
        "end_time": "2024-01-10T10:30:00",
        "block_type": "focus",
        "title": "Deep Work Session",
        "description": "Focus on coding",
        "priority": "high",
        "effectiveness_score": 0.85,
        "energy_level": 8,
        "focus_level": 9,
        "is_flexible": true,
        "buffer_before": 5,
        "buffer_after": 5
    },
    # ... more blocks
]
```

## Optimization Metrics

The optimizer considers several metrics when creating schedules:

1. **Effectiveness Score (0-1)**
   - Historical completion rates
   - Energy level alignment
   - Focus level requirements
   - Break optimization

2. **Energy Alignment (0-1)**
   - Task-energy pattern matching
   - High-energy tasks during peak hours
   - Low-energy tasks during valleys

3. **Focus Utilization (0-1)**
   - Deep work during high-focus periods
   - Meetings during medium-focus periods
   - Breaks optimally distributed

4. **Constraint Satisfaction (0-1)**
   - Work hours respected
   - Break requirements met
   - Task dependencies handled
   - Fixed-time meetings scheduled

## Best Practices

1. **Task Configuration**
   - Set realistic energy requirements
   - Mark meetings as inflexible
   - Specify dependencies accurately
   - Use appropriate priorities

2. **Energy Pattern Setup**
   - Update energy patterns regularly
   - Mark clear peak hours
   - Identify low-energy periods
   - Consider daily variations

3. **Break Optimization**
   - Allow flexible breaks
   - Set minimum break durations
   - Specify lunch breaks
   - Consider transition times

4. **Schedule Adaptation**
   - Review effectiveness scores
   - Adjust energy patterns
   - Update task preferences
   - Monitor completion rates

## Example Scenarios

### Deep Work Morning

```python
request = {
    "tasks": [
        {
            "title": "Deep Work",
            "block_type": BlockType.FOCUS,
            "priority": BlockPriority.HIGH,
            "estimated_duration": 120,
            "energy_requirement": 9,
            "is_flexible": True
        }
    ],
    "energy_pattern": {
        "pattern_type": "morning",
        "peak_hours": [{"start": "09:00", "end": "11:00"}]
    }
}
```

### Meeting-Heavy Afternoon

```python
request = {
    "tasks": [
        {
            "title": "Team Sync",
            "block_type": BlockType.MEETING,
            "priority": BlockPriority.MEDIUM,
            "estimated_duration": 30,
            "preferred_time": "14:00"
        },
        {
            "title": "Client Call",
            "block_type": BlockType.MEETING,
            "priority": BlockPriority.HIGH,
            "estimated_duration": 60,
            "preferred_time": "15:00"
        }
    ],
    "energy_pattern": {
        "pattern_type": "afternoon",
        "peak_hours": [{"start": "14:00", "end": "16:00"}]
    }
}
```

## Error Handling

The API returns appropriate error responses for various scenarios:

- 400: Invalid request parameters
- 409: Scheduling conflicts
- 422: Validation errors
- 500: Server errors

Example error response:
```json
{
    "detail": "Cannot schedule conflicting meetings at 10:00 and 10:30"
}
```

## Performance Considerations

1. **Historical Data**
   - More historical data improves predictions
   - Recent data weighted more heavily
   - Minimum 2 weeks of data recommended

2. **Model Training**
   - Models retrain periodically
   - User-specific patterns learned
   - Continuous improvement

3. **Response Times**
   - Typical response: 200-500ms
   - Complex schedules: up to 2s
   - Cached patterns when possible
