from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.database import get_db
from app.models.user_model import UserModel
from app.services.auth_service import get_current_user
from app.services.scheduling_service import SchedulingService
from app.schemas.scheduling_schema import (
    SchedulingRequest,
    SchedulingSuggestion,
    TimeBlockBaseSchema,
    CircadianCalendarOptimizationRequest,
    CircadianCalendarOptimizationResponse,
    ApplyCircadianOptimizationRequest,
    ApplyCircadianOptimizationResponse,
    CircadianOptimizationResult,
)

router = APIRouter(prefix="/api/scheduling", tags=["scheduling"])


@router.post("/check-availability", response_model=SchedulingSuggestion)
async def check_availability(
    request: SchedulingRequest,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SchedulingSuggestion:
    """
    Check availability and get AI-powered scheduling suggestions
    that take into account:
    - Calendar availability
    - Energy patterns
    - Task priority
    - Preferred times
    """
    try:
        scheduling_service = SchedulingService(db, current_user)
        return await scheduling_service.check_availability(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking availability: {str(e)}")


@router.post("/schedule-blocks")
async def schedule_blocks(
    blocks: List[TimeBlockBaseSchema],
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Schedule the selected time blocks and:
    - Save to database
    - Create calendar events
    - Set up notifications
    """
    try:
        scheduling_service = SchedulingService(db, current_user)
        return await scheduling_service.schedule_blocks(blocks)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error scheduling blocks: {str(e)}")


@router.post("/circadian-optimize")
async def optimize_with_circadian(
    request: SchedulingRequest,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Optimize schedule using CircadianDQN model that considers:
    - User's circadian rhythm and energy patterns
    - Task cognitive demands and category suitability
    - Optimal time windows for different task types
    - User's historical productivity data

    This endpoint implements the ADHD-18 story: Circadian Rhythm Optimization
    for Schedule Rebalancing.
    """
    try:
        scheduling_service = SchedulingService(db, current_user)

        # Get user data including sleep patterns
        user_data = await scheduling_service.get_user_data()

        # Delegate to service for actual optimization
        from app.ml.temporal_pattern_recognition import TemporalPatternRecognitionService

        tpr_service = TemporalPatternRecognitionService(db)

        # Convert scheduling request to task list
        tasks = []
        for task in request.tasks:
            tasks.append(
                {
                    "id": str(task.id) if task.id else "",
                    "title": task.title,
                    "description": task.description or "",
                    "estimated_duration": task.duration_minutes,
                    "priority": task.priority.value if hasattr(task, "priority") else 5,
                    "is_flexible": task.is_flexible if hasattr(task, "is_flexible") else True,
                    "deadline": task.deadline.isoformat() if task.deadline else None,
                    "focus_required": task.focus_required if hasattr(task, "focus_required") else 5,
                    "energy_required": (
                        task.energy_required if hasattr(task, "energy_required") else 5
                    ),
                    "creative_required": (
                        task.creative_required if hasattr(task, "creative_required") else 5
                    ),
                    "complexity": task.complexity if hasattr(task, "complexity") else 5,
                    "executive_function_load": (
                        task.executive_function_load
                        if hasattr(task, "executive_function_load")
                        else 5
                    ),
                }
            )

        # Get existing model path from user data if available
        model_path = user_data.get("circadian_dqn_model_path")

        # Perform circadian-aware optimization
        result = await tpr_service.optimize_schedule_with_circadian_dqn(
            user_id=str(current_user.id), tasks=tasks, user_data=user_data, model_path=model_path
        )

        # Update user's model path for future use
        if result.get("model_path") and result.get("model_path") != model_path:
            await scheduling_service.update_user_data(
                {"circadian_dqn_model_path": result.get("model_path")}
            )

        return {
            "schedule": result.get("schedule", []),
            "energy_curve": [
                {"hour": hour, "energy_level": level}
                for hour, level in result.get("energy_curve", {}).items()
            ],
            "message": "Schedule optimized with circadian rhythm awareness",
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error optimizing schedule with circadian awareness: {str(e)}"
        )


@router.post("/circadian-optimize-calendar", response_model=CircadianCalendarOptimizationResponse)
async def optimize_calendar_with_circadian(
    request: CircadianCalendarOptimizationRequest,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CircadianCalendarOptimizationResponse:
    """
    Optimize a user's existing calendar events using circadian rhythm awareness.

    This endpoint:
    1. Fetches real calendar events from the user's connected calendars
    2. Applies the CircadianDQN model to optimize the schedule based on:
       - User's circadian energy patterns
       - Task cognitive demands
       - Calendar constraints
    3. Returns an optimized schedule with suggested time adjustments

    Args:
        request: Contains date range and optimization parameters
        current_user: The authenticated user
        db: Database session

    Returns:
        Optimized schedule with original and suggested timeslots
    """
    try:
        # Initialize services
        from app.services.calendar_service import CalendarService
        from app.services.temporal_pattern_recognition import TemporalPatternRecognitionService
        from app.ml.models.adhd17_reinforcement_model import TaskCognitiveProfile

        scheduling_service = SchedulingService(db, current_user)
        calendar_service = CalendarService(db)
        tpr_service = TemporalPatternRecognitionService(db)

        # Get user data for circadian patterns
        user_data = await scheduling_service.get_user_data()

        # Fetch calendar events for the specified date range
        calendar_events = await calendar_service.get_events(current_user.id)

        # Filter events to the specified date range
        events_in_range = [
            event
            for event in calendar_events
            if request.start_date <= event.start_time <= request.end_date
        ]

        # Convert calendar events to tasks for the optimizer
        tasks = []
        for event in events_in_range:
            # Skip non-flexible events if requested
            meta_data = event.meta_data or {}
            is_flexible = meta_data.get("is_flexible", False)
            if request.only_flexible_events and not is_flexible:
                continue

            # Create task representation for the optimizer
            duration_minutes = event.duration or (
                int((event.end_time - event.start_time).total_seconds() / 60)
            )

            # Extract cognitive demand data or use defaults
            energy_required = event.energy_required or 5
            focus_required = event.focus_required or 5

            # Determine executive function load based on event type
            executive_function_load = 5
            if event.event_type == "meeting":
                executive_function_load = 7
            elif event.event_type == "task":
                executive_function_load = 6

            # Map event priority to numeric scale
            priority_map = {"high": 8, "medium": 5, "low": 3}
            priority = priority_map.get(event.priority, 5) if event.priority else 5

            tasks.append(
                {
                    "id": str(event.id),
                    "title": event.title,
                    "description": event.description or "",
                    "estimated_duration": duration_minutes,
                    "priority": priority,
                    "is_flexible": is_flexible,
                    "deadline": event.end_time.isoformat() if event.end_time else None,
                    "focus_required": focus_required,
                    "energy_required": energy_required,
                    "creative_required": meta_data.get("creative_required", 5),
                    "complexity": meta_data.get("complexity", 5),
                    "executive_function_load": executive_function_load,
                    "original_start_time": event.start_time.isoformat(),
                    "original_end_time": event.end_time.isoformat(),
                }
            )

        # Get existing model path from user data if available
        model_path = user_data.get("circadian_dqn_model_path")

        # Perform circadian-aware optimization
        result = await tpr_service.optimize_schedule_with_circadian_dqn(
            user_id=str(current_user.id), tasks=tasks, user_data=user_data, model_path=model_path
        )

        # Update user's model path for future use
        if result.get("model_path") and result.get("model_path") != model_path:
            await scheduling_service.update_user_data(
                {"circadian_dqn_model_path": result.get("model_path")}
            )

        # Convert optimized schedule back to calendar-friendly format
        optimized_schedule = []
        for item in result.get("schedule", []):
            original_id = item.get("task_id", "")
            original_event = next((e for e in events_in_range if str(e.id) == original_id), None)

            if original_event:
                # Parse dates
                new_start_time = datetime.fromisoformat(item.get("start_time"))
                new_end_time = datetime.fromisoformat(item.get("end_time"))

                # Calculate time differences
                original_start = original_event.start_time
                time_difference_minutes = int(
                    (new_start_time - original_start).total_seconds() / 60
                )

                # Create optimized event entry
                optimized_schedule.append(
                    CircadianOptimizationResult(
                        event_id=original_id,
                        title=original_event.title,
                        original_start=original_event.start_time,
                        original_end=original_event.end_time,
                        suggested_start=new_start_time,
                        suggested_end=new_end_time,
                        time_difference_minutes=time_difference_minutes,
                        suitability_score=item.get("suitability_score", 0.5),
                        cognitive_category=item.get("cognitive_category", "unknown"),
                        energy_level=item.get("energy_level", 5.0),
                    )
                )

        return CircadianCalendarOptimizationResponse(
            optimized_schedule=optimized_schedule,
            energy_curve=[
                {"hour": hour, "energy_level": level}
                for hour, level in result.get("energy_curve", {}).items()
            ],
            events_analyzed=len(events_in_range),
            events_optimized=len(optimized_schedule),
            message="Calendar events optimized with circadian rhythm awareness",
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error optimizing calendar with circadian awareness: {str(e)}"
        )


@router.post("/apply-circadian-optimization", response_model=ApplyCircadianOptimizationResponse)
async def apply_circadian_calendar_optimization(
    request: ApplyCircadianOptimizationRequest,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApplyCircadianOptimizationResponse:
    """
    Apply circadian optimization results to the user's calendar events.

    This endpoint:
    1. Takes the optimization results from optimize_calendar_with_circadian
    2. Updates the actual calendar events with the suggested times
    3. Syncs the changes with external calendar providers if needed

    Args:
        request: Contains optimization results to apply
        current_user: The authenticated user
        db: Database session

    Returns:
        Summary of applied changes
    """
    try:
        # Initialize services
        from app.services.calendar_service import CalendarService

        calendar_service = CalendarService(db)

        # Get the optimization results from the request
        optimization_results = request.optimization_results

        if not optimization_results:
            return ApplyCircadianOptimizationResponse(
                success=False,
                message="No optimization results provided",
                applied_count=0,
                skipped_count=0,
                errors=[],
                total_errors=0,
            )

        # Prepare for service method call
        results_dicts = [result.model_dump() for result in optimization_results]

        # Apply the optimizations
        results = await calendar_service.apply_circadian_optimization(
            user_id=current_user.id, optimization_results=results_dicts
        )

        # Return the results
        return ApplyCircadianOptimizationResponse(
            success=results["applied_count"] > 0,
            message=f"Applied {results['applied_count']} optimizations, skipped {results['skipped_count']}",
            applied_count=results["applied_count"],
            skipped_count=results["skipped_count"],
            errors=results["errors"][:5],  # Limit errors to first 5 for brevity
            total_errors=len(results["errors"]),
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error applying calendar optimizations: {str(e)}"
        )
