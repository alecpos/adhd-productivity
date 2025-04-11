from datetime import datetime, timedelta
from uuid import uuid4


def create_valid_data(schema_class):
    """Create valid data for testing schema validation."""
    base_time = datetime.now()

    # Common fields that should always be included
    always_include = {
        "email": "test@example.com",
        "username": "test_user",
        "password": "TestPassword123!",
        "id": str(uuid4()),
        "user_id": str(uuid4()),
        "title": "Test Title",
        "description": "Test Description",
        "success": True,
        "message": "Test message",
        "name": "Test Name",
        "amount": 100.0,
        "active_period": "monthly",
        "due_date": base_time.isoformat(),
        "created_at": base_time.isoformat(),
        "updated_at": base_time.isoformat(),
        "average_energy": 1.0,
        "average_focus": 1.0,
        "time_of_day": "morning",
        "total_focus_time": 120,
        "total_break_time": 30,
        "block_duration": 25,
        "break_duration": 5,
        "start": "09:00",
        "end": "17:00",
        "start_time": base_time.isoformat(),
        "end_time": (base_time + timedelta(hours=1)).isoformat(),
    }

    # Response-specific fields
    response_fields = {
        "data": {
            "id": str(uuid4()),
            "created_at": base_time.isoformat(),
            "updated_at": base_time.isoformat(),
            "user_id": str(uuid4()),
            "name": "Test Name",
            "amount": 100.0,
            "active_period": "monthly",
            "title": "Test Title",
            "description": "Test Description",
            "due_date": base_time.isoformat(),
            "success": True,
            "message": "Test message",
            "email": "test@example.com",
            "start_time": base_time.isoformat(),
            "end_time": (base_time + timedelta(hours=1)).isoformat(),
        }
    }

    # List fields
    list_fields = {
        "sessions": [
            {
                "id": str(uuid4()),
                "created_at": base_time.isoformat(),
                "updated_at": base_time.isoformat(),
                "user_id": str(uuid4()),
                "session_type": "one_on_one",
                "activity_type": "study",
                "start_time": base_time.isoformat(),
                "end_time": (base_time + timedelta(hours=1)).isoformat(),
                "success": True,
                "message": "Test message",
                "data": {"key": "value"},
            }
        ],
        "timeline": [
            {
                "id": 1,
                "user_id": str(uuid4()),
                "event_type": "task",
                "due_date": base_time.isoformat(),
                "title": "Test Event",
                "start_time": base_time.isoformat(),
                "end_time": (base_time + timedelta(hours=1)).isoformat(),
            }
        ],
        "blocks": [
            {
                "id": str(uuid4()),
                "user_id": str(uuid4()),
                "title": "Test Block",
                "start_time": base_time.isoformat(),
                "end_time": (base_time + timedelta(minutes=25)).isoformat(),
                "created_at": base_time.isoformat(),
                "updated_at": base_time.isoformat(),
            }
        ],
        "events": [
            {
                "id": str(uuid4()),
                "user_id": str(uuid4()),
                "title": "Test Event",
                "start_time": base_time.isoformat(),
                "end_time": (base_time + timedelta(hours=1)).isoformat(),
                "created_at": base_time.isoformat(),
                "updated_at": base_time.isoformat(),
            }
        ],
        "data": [
            {
                "id": str(uuid4()),
                "user_id": str(uuid4()),
                "title": "Test Data",
                "created_at": base_time.isoformat(),
                "updated_at": base_time.isoformat(),
                "name": "Test Name",
                "amount": 100.0,
                "active_period": "monthly",
                "due_date": base_time.isoformat(),
                "start_time": base_time.isoformat(),
                "end_time": (base_time + timedelta(hours=1)).isoformat(),
            }
        ],
    }

    # Time-based fields
    time_fields = {
        "working_hours": {"start": "09:00", "end": "17:00"},
        "peak_hours": [
            {
                "start_time": "09:00",
                "end_time": "12:00",
                "average_energy": 1.0,
                "average_focus": 1.0,
            }
        ],
        "low_hours": [
            {
                "start_time": "14:00",
                "end_time": "16:00",
                "average_energy": 0.5,
                "average_focus": 0.5,
            }
        ],
    }

    # User-related fields
    user_fields = {
        "user": {
            "id": str(uuid4()),
            "email": "test@example.com",
            "username": "test_user",
            "created_at": base_time.isoformat(),
            "updated_at": base_time.isoformat(),
        }
    }

    # Pattern-related fields
    pattern_fields = {
        "patterns": {
            "daily_patterns": {},
            "peak_hours": [
                {
                    "start_time": "09:00",
                    "end_time": "12:00",
                    "average_energy": 1.0,
                    "average_focus": 1.0,
                }
            ],
            "low_hours": [
                {
                    "start_time": "14:00",
                    "end_time": "16:00",
                    "average_energy": 0.5,
                    "average_focus": 0.5,
                }
            ],
            "environmental_impacts": ["noise", "lighting"],
            "recommendations": ["test"],
        }
    }

    # Start with an empty valid_data dictionary
    valid_data = {}
    schema_name = schema_class.__name__.lower()
    schema_fields = schema_class.model_fields if hasattr(schema_class, "model_fields") else {}

    # Handle response schemas differently
    if "response" in schema_name:
        if "list" in schema_name:
            if "subscription" in schema_name:
                valid_data["data"] = list_fields["data"]
            elif "event" in schema_name:
                valid_data["events"] = list_fields["events"]
            elif "block" in schema_name:
                valid_data["blocks"] = list_fields["blocks"]
            valid_data["total_count"] = 1
        elif "analytics" in schema_name or "insights" in schema_name:
            valid_data["data"] = response_fields["data"]

    # Add fields based on schema name and fields
    for field_name, field in schema_fields.items():
        if field_name in always_include:
            valid_data[field_name] = always_include[field_name]
        elif field_name in response_fields:
            valid_data[field_name] = response_fields[field_name]
        elif field_name in list_fields:
            valid_data[field_name] = list_fields[field_name]
        elif field_name in time_fields:
            valid_data[field_name] = time_fields[field_name]
        elif field_name in user_fields:
            valid_data[field_name] = user_fields[field_name]
        elif field_name in pattern_fields:
            valid_data[field_name] = pattern_fields[field_name]
        elif field.is_required():
            if "email" in field_name.lower():
                valid_data[field_name] = "test@example.com"
            elif "time" in field_name.lower():
                if "start" in field_name.lower():
                    valid_data[field_name] = base_time.isoformat()
                elif "end" in field_name.lower():
                    valid_data[field_name] = (base_time + timedelta(hours=1)).isoformat()
            elif field_name == "time_of_day":
                valid_data[field_name] = "morning"

    return valid_data
