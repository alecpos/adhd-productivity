def validate_task_data(data: dict):
    if not data.get("title"):
        raise ValueError("TaskModelSchemaSchema title is required")
    if not data.get("due_date"):
        raise ValueError("TaskModelSchemaSchema due date is required")
