from datetime import timedelta
from typing import List, Dict, Optional

def prioritize_tasks(tasks: List[dict]) -> List[dict]:
    """Prioritize tasks based on urgency and importance"""
    return sorted(tasks, key=lambda x: x.due_date)

def suggest_task(tasks: List[dict]) -> Optional[dict]:
    """Suggest the highest priority task."""
    prioritized_tasks = prioritize_tasks(tasks)
    return prioritized_tasks[0] if prioritized_tasks else None

def suggest_task_based_on_energy(tasks: List[dict], user_energy_profile: Dict[str, List[int]]) -> Optional[dict]:
    """
    Suggest the best task based on user energy mapping.
    """
    prioritized_tasks = prioritize_tasks(tasks)
    peak_time_tasks = [
        task for task in prioritized_tasks
        if task.due_date.hour in user_energy_profile["peak_hours"]
    ]
    return peak_time_tasks[0] if peak_time_tasks else suggest_task(tasks)

def schedule_tasks(tasks: List[dict], user_energy_profile: Dict[str, List[int]]) -> List[dict]:
    """
    Schedule tasks based on energy mapping and urgency.
    """
    tasks = sorted(tasks, key=lambda x: (x.due_date, -x.priority))
    peak_hours = user_energy_profile["peak_hours"]
    scheduled_tasks = []

    for task in tasks:
        if task.due_date.hour in peak_hours:
            task.scheduled_time = task.due_date
        else:
            task.scheduled_time = task.due_date - timedelta(hours=1)
        scheduled_tasks.append(task)
    
    return scheduled_tasks

