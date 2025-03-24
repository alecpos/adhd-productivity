"""Scheduling service module."""

from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from uuid import UUID, uuid4
from dataclasses import dataclass
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.services.base_service import BaseService, OPEN, CLOSED, HALF_OPEN
from app.models.scheduling_model import ScheduleBlock, BlockType, WorkHours, Break, Interruption, SchedulePreferences
from app.models.task_model import TaskModel
from app.schemas.scheduling_schema import (
    ScheduleBlock as ScheduleBlockSchema,
    ScheduleOptimizationRequest,
    OptimizedSchedule,
    ScheduleSuggestion,
    WorkHoursSchema,
    BreakSchema,
    InterruptionSchema,
    SchedulePreferencesSchema,
    GenerateScheduleRequest
)
from app.models.enums_model import TaskPriority
from app.utils.decorators import handle_service_error
from app.schemas.optimizer_schema import (
    EnergyOptimizer as EnergyOptimizerSchema,
    FocusOptimizer as FocusOptimizerSchema,
    MentalHealthOptimizer as MentalHealthOptimizerSchema,
)


@dataclass
class ScheduleSuggestionSchema(BaseService):
    blocks: List[ScheduleBlock]
    score: float


class SchedulingService(BaseService[ScheduleBlock, OptimizedSchedule, ScheduleOptimizationRequest]):
    """Service for managing time blocks and scheduling."""

    def __init__(self, db: AsyncSession):
        """Initialize the service with database session."""
        super().__init__(db=db, model=ScheduleBlock, schema=OptimizedSchedule)
        self.db = db
        self.energy_optimizer = EnergyOptimizerSchema()
        self.focus_optimizer = FocusOptimizerSchema()
        self.mental_health_optimizer = MentalHealthOptimizerSchema()
        self.optimizers = {'energy': self.energy_optimizer, 'focus': self.focus_optimizer, 'mental_health': self.mental_health_optimizer}
        self.logger = logging.getLogger(self.__class__.__name__)
        self.task_service = TaskService(db)
        self.energy_service = EnergyService(db)
        self.focus_service = FocusService(db)

    @handle_service_error
    async def optimize_schedule(self, user_id: UUID, time_blocks: List[ScheduleBlockSchema], optimization_type: str, user_preferences: Optional[Dict[str, Any]]=None) -> List[ScheduleBlockSchema]:
        """Optimize a schedule using the specified optimizer."""
        if not time_blocks:
            return []
        if optimization_type not in self.optimizers:
            raise ValueError(f'Unknown optimization type: {optimization_type}')
        optimizer = self.optimizers[optimization_type]
        user_prefs = user_preferences or {}
        if 'work_start' not in user_prefs:
            user_prefs['work_start'] = datetime.now().replace(hour=9, minute=0)
        if 'work_end' not in user_prefs:
            user_prefs['work_end'] = datetime.now().replace(hour=17, minute=0)
        return await optimizer.optimize_schedule(time_blocks, user_prefs)

    @handle_service_error
    async def get_time_blocks_in_range(self, user_id: UUID, from_date: datetime, to_date: datetime) -> List[ScheduleBlockSchema]:
        """Get all time blocks within a date range."""
        query = select(ScheduleBlock).where(and_(ScheduleBlock.user_id == user_id, ScheduleBlock.start_time >= from_date, ScheduleBlock.end_time <= to_date))
        result = await self.db.execute(query)
        return list(result.scalars().all())

    @handle_service_error
    async def create_time_block(self, user_id: UUID, start_time: datetime, end_time: datetime, block_type: str, title: str, task_id: Optional[UUID]=None, meta_data: Optional[Dict[str, Any]]=None) -> ScheduleBlockSchema:
        """Create a new time block."""
        time_block = ScheduleBlock(
            user_id=user_id,
            start_time=start_time,
            end_time=end_time,
            block_type=block_type,
            title=title,
            task_id=task_id,
            meta_data=meta_data or {}
        )
        self.db.add(time_block)
        await self.db.commit()
        await self.db.refresh(time_block)
        return time_block

    async def _calculate_time_slot_score(self, start_time: datetime, task: TaskModel, user_id: UUID) -> float:
        """Calculate a score for scheduling a task at a given time."""
        if start_time.tzinfo is None:
            start_time = start_time.replace(tzinfo=timezone.utc)
        hour = start_time.hour
        time_of_day_score = 1.0
        if 8 <= hour < 12:
            time_of_day_score = 1.0
        elif 12 <= hour < 15:
            time_of_day_score = 0.8
        elif 15 <= hour < 18:
            time_of_day_score = 0.6
        else:
            time_of_day_score = 0.4
        priority_map = {TaskPriority.LOW: 0, TaskPriority.MEDIUM: 1, TaskPriority.HIGH: 2, TaskPriority.URGENT: 3}
        priority_score = priority_map[task.priority] / 3.0
        return (time_of_day_score + priority_score) / 2.0

    async def _is_suitable_time(self, time_slot: datetime, task: TaskModel, user_id: UUID) -> bool:
        """Check if a time slot is suitable for a task."""
        if await self._has_conflict(time_slot, task.estimated_duration, user_id):
            return False
        
        # Check if time slot is within working hours (9 AM to 5 PM)
        if time_slot.hour < 9 or time_slot.hour >= 17:
            return False
            
        # Check if task would end before working hours end
        end_time = time_slot + timedelta(minutes=task.estimated_duration)
        if end_time.hour >= 17:
            return False
            
        return True

    async def _has_conflict(self, time_slot: datetime, duration: int, user_id: UUID) -> bool:
        """Check if there are any scheduling conflicts."""
        end_time = time_slot + timedelta(minutes=duration)
        existing_blocks = await self.db.execute(select(ScheduleBlock).where(and_(ScheduleBlock.user_id == user_id, ScheduleBlock.start_time < end_time, ScheduleBlock.end_time > time_slot)))
        return bool(existing_blocks.scalar_one_or_none())

    @handle_service_error
    async def schedule_blocks(self, user_id: UUID, tasks: List[TaskModel], start_time: datetime, end_time: datetime) -> List[ScheduleBlockSchema]:
        """Schedule tasks into time blocks."""
        if not tasks:
            return []
        if start_time.tzinfo is None:
            start_time = start_time.replace(tzinfo=timezone.utc)
        if end_time.tzinfo is None:
            end_time = end_time.replace(tzinfo=timezone.utc)
        if start_time >= end_time:
            raise HTTPException(status_code=400, detail='Start time must be before end time')
        now = datetime.now(timezone.utc)
        if start_time < now:
            raise HTTPException(status_code=400, detail='Cannot schedule tasks in the past')
        existing_blocks = await self._get_overlapping_blocks(user_id, start_time, end_time)
        if existing_blocks:
            raise HTTPException(status_code=409, detail='Time slot conflicts with existing block')
        total_duration = sum((task.estimated_duration for task in tasks))
        available_duration = int((end_time - start_time).total_seconds() / 60)
        if total_duration > available_duration:
            raise HTTPException(status_code=400, detail='Insufficient time to schedule all tasks')
        blocks = []
        current_time = start_time
        for task in tasks:
            if task.estimated_duration <= 0:
                raise HTTPException(status_code=400, detail='Task duration must be positive')
            block_end_time = current_time + timedelta(minutes=task.estimated_duration)
            energy_level = task.energy_required / 5.0 if task.energy_required else 0.2
            focus_level = 0.4
            mental_health_score = 0.4
            block = ScheduleBlock(
                user_id=user_id,
                task_id=task.id,
                title=task.title,
                start_time=current_time,
                end_time=block_end_time,
                block_type=BlockType.TASK,
                energy_requirement=energy_level,
                focus_requirement=focus_level,
                meta_data={
                    'priority': task.priority,
                    'energy_required': task.energy_required,
                    'score': (energy_level + focus_level + mental_health_score) / 3
                }
            )
            blocks.append(block)
            current_time = block_end_time
        for block in blocks:
            self.db.add(block)
        await self.db.commit()
        for block in blocks:
            await self.db.refresh(block)
        return blocks

    async def _get_overlapping_blocks(self, user_id: UUID, start_time: datetime, end_time: datetime) -> List[ScheduleBlockSchema]:
        """Get existing blocks that overlap with the given time range."""
        if start_time.tzinfo is None:
            start_time = start_time.replace(tzinfo=timezone.utc)
        if end_time.tzinfo is None:
            end_time = end_time.replace(tzinfo=timezone.utc)
        query = select(ScheduleBlock).where(and_(ScheduleBlock.user_id == user_id, ScheduleBlock.start_time < end_time, ScheduleBlock.end_time > start_time))
        result = await self.db.execute(query)
        return list(result.scalars().all())

    @handle_service_error
    async def suggest_optimal_schedule(self, user_id: UUID, tasks: List[TaskModel], start_time: datetime, end_time: datetime) -> ScheduleSuggestionSchema:
        """Suggest an optimal schedule for tasks."""
        if start_time.tzinfo is None:
            start_time = start_time.replace(tzinfo=timezone.utc)
        if end_time.tzinfo is None:
            end_time = end_time.replace(tzinfo=timezone.utc)
        if start_time >= end_time:
            raise HTTPException(status_code=400, detail='Start time must be before end time')
        now = datetime.now(timezone.utc)
        if start_time < now:
            raise HTTPException(status_code=400, detail='Cannot schedule tasks in the past')
        existing_blocks = await self._get_overlapping_blocks(user_id, start_time, end_time)
        if existing_blocks:
            raise HTTPException(status_code=409, detail='Time slot conflicts with existing block')
        total_duration = sum((task.estimated_duration for task in tasks))
        available_duration = int((end_time - start_time).total_seconds() / 60)
        if total_duration > available_duration:
            raise HTTPException(status_code=400, detail='Insufficient time to schedule all tasks')
        blocks = []
        current_time = start_time
        total_score = 0.0
        for task in tasks:
            if task.estimated_duration <= 0:
                raise HTTPException(status_code=400, detail='TaskModelSchema duration must be positive')
            slot_score = await self._calculate_time_slot_score(current_time, task, user_id)
            total_score += slot_score
            block_end_time = current_time + timedelta(minutes=task.estimated_duration)
            energy_level = task.energy_required / 5.0 if task.energy_required else 0.2
            focus_level = 0.4
            mental_health_score = 0.4
            block = ScheduleBlock(
                user_id=user_id,
                task_id=task.id,
                title=task.title,
                start_time=current_time,
                end_time=block_end_time,
                block_type=BlockType.TASK,
                energy_requirement=energy_level,
                focus_requirement=focus_level,
                meta_data={
                    'priority': task.priority,
                    'energy_required': task.energy_required,
                    'score': slot_score
                }
            )
            blocks.append(block)
            current_time = block_end_time
        avg_score = total_score / len(tasks) if tasks else 0.0
        return ScheduleSuggestionSchema(blocks=blocks, score=avg_score)

    @handle_service_error
    async def get_schedule_stats(self, user_id: UUID, from_date: datetime, to_date: datetime) -> Dict[str, Any]:
        """Get schedule statistics and improvement suggestions."""
        blocks = await self.get_time_blocks_in_range(user_id, from_date, to_date)
        if not blocks:
            return {'total_blocks': 0, 'completion_rate': 0.0, 'average_effectiveness': 0.0, 'peak_performance_hours': [], 'focus_distribution': {'morning': 0.0, 'afternoon': 0.0, 'evening': 0.0}, 'improvement_suggestions': ['Start scheduling tasks to track your productivity patterns', 'Try scheduling tasks during your typical high-energy periods', 'Consider using breaks between tasks to maintain focus']}
        total_blocks = len(blocks)
        completed_blocks = sum((1 for block in blocks if block.completed))
        completion_rate = completed_blocks / total_blocks if total_blocks > 0 else 0.0
        effectiveness_scores = [block.effectiveness_score for block in blocks if block.effectiveness_score is not None]
        average_effectiveness = sum(effectiveness_scores) / len(effectiveness_scores) if effectiveness_scores else 0.0
        hour_effectiveness = {}
        for block in blocks:
            if block.effectiveness_score is not None and block.start_time is not None:
                hour = block.start_time.hour
                if hour not in hour_effectiveness:
                    hour_effectiveness[hour] = []
                hour_effectiveness[hour].append(block.effectiveness_score)
        peak_hours = []
        for hour, scores in hour_effectiveness.items():
            avg_score = sum(scores) / len(scores)
            if avg_score >= 0.8:
                peak_hours.append(f'{hour:02d}:00')
        morning_blocks = [b for b in blocks if b.start_time and 5 <= b.start_time.hour < 12]
        afternoon_blocks = [b for b in blocks if b.start_time and 12 <= b.start_time.hour < 17]
        evening_blocks = [b for b in blocks if b.start_time and 17 <= b.start_time.hour < 22]
        total_focus = len(morning_blocks) + len(afternoon_blocks) + len(evening_blocks)
        focus_distribution = {'morning': len(morning_blocks) / total_focus if total_focus > 0 else 0.0, 'afternoon': len(afternoon_blocks) / total_focus if total_focus > 0 else 0.0, 'evening': len(evening_blocks) / total_focus if total_focus > 0 else 0.0}
        suggestions = []
        if completion_rate < 0.7:
            suggestions.append('Consider breaking down tasks into smaller, more manageable chunks to improve completion rate')
        if average_effectiveness < 0.6:
            suggestions.append('Try scheduling high-priority tasks during your peak performance hours')
        if not peak_hours:
            suggestions.append('Track your energy levels throughout the day to identify your most productive hours')
        if focus_distribution['morning'] < 0.2 and any((5 <= h.hour < 12 for h in peak_hours)):
            suggestions.append('Consider scheduling more tasks in the morning when your effectiveness is higher')
        if len([b for b in blocks if b.block_type == BlockType.BREAK]) / total_blocks < 0.1:
            suggestions.append('Include more regular breaks to maintain productivity and prevent burnout')
        if any((b.effectiveness_score and b.effectiveness_score < 0.5 for b in blocks)):
            suggestions.append('Review tasks with low effectiveness scores and identify common patterns or obstacles')
        if not suggestions:
            suggestions.append('Your schedule looks well-optimized! Keep monitoring your patterns for continued improvement')
        return {'total_blocks': total_blocks, 'completion_rate': completion_rate, 'average_effectiveness': average_effectiveness, 'peak_performance_hours': sorted(peak_hours), 'focus_distribution': focus_distribution, 'improvement_suggestions': suggestions}

    @handle_service_error
    async def get_user_data(self, user_id: UUID = None) -> Dict[str, Any]:
        """Get user data including circadian rhythm preferences and sleep patterns.
        
        Args:
            user_id: User ID (optional - uses service user_id if not provided)
            
        Returns:
            Dictionary containing user data for circadian optimization
        """
        from app.models.user_model import UserModel, UserPreferences
        
        if user_id is None and hasattr(self, 'user') and self.user:
            user_id = self.user.id
            
        if not user_id:
            raise ValueError("User ID is required")
        
        # Query for user data
        query = select(UserModel).where(UserModel.id == user_id)
        result = await self.db.execute(query)
        user = result.scalars().first()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Query for user preferences
        query = select(UserPreferences).where(UserPreferences.user_id == user_id)
        result = await self.db.execute(query)
        preferences = result.scalars().first()
        
        # Default values for circadian data
        user_data = {
            "sleep_time": datetime.now().replace(hour=23, minute=0, second=0, microsecond=0).time(),
            "wake_time": datetime.now().replace(hour=7, minute=0, second=0, microsecond=0).time(),
            "sleep_quality": 0.7,
            "sleep_duration": 8.0,
            "medications": [],
            "circadian_profile": {
                "focus_intensive_preferred_hours": [9, 10, 11],
                "creative_preferred_hours": [14, 15, 16],
                "routine_preferred_hours": [12, 13, 17],
                "administrative_preferred_hours": [8, 18, 19]
            }
        }
        
        # Update with actual data if available
        if preferences:
            if hasattr(preferences, 'sleep_schedule') and preferences.sleep_schedule:
                sleep_data = preferences.sleep_schedule
                if 'sleep_time' in sleep_data and sleep_data['sleep_time']:
                    try:
                        sleep_time = datetime.fromisoformat(sleep_data['sleep_time']).time()
                        user_data["sleep_time"] = sleep_time
                    except (ValueError, TypeError):
                        pass
                        
                if 'wake_time' in sleep_data and sleep_data['wake_time']:
                    try:
                        wake_time = datetime.fromisoformat(sleep_data['wake_time']).time()
                        user_data["wake_time"] = wake_time
                    except (ValueError, TypeError):
                        pass
                        
                if 'sleep_quality' in sleep_data:
                    user_data["sleep_quality"] = float(sleep_data.get('sleep_quality', 0.7))
                    
                if 'sleep_duration' in sleep_data:
                    user_data["sleep_duration"] = float(sleep_data.get('sleep_duration', 8.0))
            
            # Get medications if available
            if hasattr(preferences, 'medication_schedule') and preferences.medication_schedule:
                medications = []
                for med in preferences.medication_schedule:
                    if 'name' in med and 'time_taken' in med:
                        try:
                            time_taken = datetime.fromisoformat(med['time_taken']).time()
                            medications.append({
                                "name": med['name'],
                                "time_taken": time_taken
                            })
                        except (ValueError, TypeError):
                            pass
                user_data["medications"] = medications
                
            # Get circadian profile if available
            if hasattr(preferences, 'productivity_preferences') and preferences.productivity_preferences:
                prod_pref = preferences.productivity_preferences
                
                circadian_profile = user_data["circadian_profile"]
                
                if 'focus_peak_hours' in prod_pref:
                    circadian_profile["focus_intensive_preferred_hours"] = prod_pref.get('focus_peak_hours', [9, 10, 11])
                    
                if 'creative_peak_hours' in prod_pref:
                    circadian_profile["creative_preferred_hours"] = prod_pref.get('creative_peak_hours', [14, 15, 16])
                    
                if 'routine_preferred_hours' in prod_pref:
                    circadian_profile["routine_preferred_hours"] = prod_pref.get('routine_preferred_hours', [12, 13, 17])
                    
                if 'admin_preferred_hours' in prod_pref:
                    circadian_profile["administrative_preferred_hours"] = prod_pref.get('admin_preferred_hours', [8, 18, 19])
                
                user_data["circadian_profile"] = circadian_profile
                
            # Get stored model path if available
            if hasattr(preferences, 'ml_models') and preferences.ml_models:
                ml_models = preferences.ml_models
                if 'circadian_dqn_model_path' in ml_models:
                    user_data["circadian_dqn_model_path"] = ml_models.get('circadian_dqn_model_path')
        
        return user_data
    
    @handle_service_error
    async def update_user_data(self, user_id: UUID = None, data_updates: Dict[str, Any] = {}) -> bool:
        """Update user data with new values.
        
        Args:
            user_id: User ID (optional - uses service user_id if not provided)
            data_updates: Dictionary of data to update
            
        Returns:
            True if update was successful
        """
        from app.models.user_model import UserModel, UserPreferences
        
        if user_id is None and hasattr(self, 'user') and self.user:
            user_id = self.user.id
            
        if not user_id:
            raise ValueError("User ID is required")
        
        if not data_updates:
            return True  # Nothing to update
        
        # Query for user preferences
        query = select(UserPreferences).where(UserPreferences.user_id == user_id)
        result = await self.db.execute(query)
        preferences = result.scalars().first()
        
        if not preferences:
            # Create new preferences if not found
            preferences = UserPreferences(user_id=user_id)
            self.db.add(preferences)
        
        # Update preferences
        # Handle ML model paths
        if 'circadian_dqn_model_path' in data_updates:
            if not hasattr(preferences, 'ml_models') or not preferences.ml_models:
                preferences.ml_models = {}
                
            preferences.ml_models['circadian_dqn_model_path'] = data_updates['circadian_dqn_model_path']
        
        # Handle other updates as needed
        # Sleep schedule updates
        sleep_updates = {}
        for key in ['sleep_time', 'wake_time', 'sleep_quality', 'sleep_duration']:
            if key in data_updates:
                sleep_updates[key] = data_updates[key]
                
        if sleep_updates and hasattr(preferences, 'sleep_schedule'):
            if not preferences.sleep_schedule:
                preferences.sleep_schedule = {}
                
            for key, value in sleep_updates.items():
                preferences.sleep_schedule[key] = value
        
        # Commit changes
        await self.db.commit()
        return True

    @BaseService.with_retry(
        max_retries=3,
        initial_delay=0.1,
        max_delay=2.0,
        backoff_factor=2.0,
        error_message="Failed to generate schedule"
    )
    @BaseService.with_circuit_breaker(
        name="schedule_generation",
        failure_threshold=5,
        recovery_timeout=30
    )
    async def generate_schedule(
        self, 
        user_id: UUID, 
        request: GenerateScheduleRequest
    ) -> Dict[str, Any]:
        """Generate a daily schedule with time blocks for tasks.
        
        This method orchestrates the schedule generation process by:
        1. Getting user tasks to schedule
        2. Fetching energy and focus patterns
        3. Analyzing cognitive requirements of tasks
        4. Generating an optimal schedule with the scheduler
        5. Returning the generated schedule blocks
        """
        try:
            # Get tasks to schedule
            tasks_to_schedule = await self._get_tasks_to_schedule(
                user_id, 
                request.date,
                request.include_task_ids,
                request.exclude_task_ids
            )
            
            if not tasks_to_schedule:
                return {"error": "No tasks available to schedule", "blocks": []}
            
            # Get energy and focus patterns
            try:
                energy_pattern = await self.bulkhead(
                    self._get_energy_pattern,
                    user_id, 
                    request.date,
                    timeout=3
                )
            except Exception as e:
                self.logger.warning(f"Failed to get energy pattern: {str(e)}")
                # Use default energy pattern if real one can't be fetched
                energy_pattern = self._get_default_energy_pattern(request.date)
            
            try:
                focus_curve = await self.bulkhead(
                    self._get_focus_curve,
                    user_id, 
                    request.date,
                    timeout=3
                )
            except Exception as e:
                self.logger.warning(f"Failed to get focus curve: {str(e)}")
                # Use default focus curve if real one can't be fetched
                focus_curve = self._get_default_focus_curve(request.date)
            
            # Get work hours and breaks
            work_hours = await self._get_work_hours(user_id, request.date)
            breaks = await self._get_breaks(user_id, request.date)
            
            # Get scheduling preferences
            preferences = await self._get_schedule_preferences(user_id)
            
            # Get existing calendar events to avoid conflicts
            calendar_events = await self._get_calendar_events(user_id, request.date)
            
            # Generate schedule blocks
            schedule_blocks = await self._generate_schedule_blocks(
                user_id=user_id,
                date=request.date,
                tasks=tasks_to_schedule,
                energy_pattern=energy_pattern,
                focus_curve=focus_curve,
                work_hours=work_hours,
                breaks=breaks,
                preferences=preferences,
                calendar_events=calendar_events
            )
            
            # Save generated blocks
            saved_blocks = await self._save_schedule_blocks(user_id, schedule_blocks)
            
            return {
                "date": request.date.isoformat(),
                "blocks": [block.model_dump() for block in saved_blocks],
                "energy_pattern": energy_pattern,
                "focus_curve": focus_curve
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate schedule: {str(e)}", exc_info=True)
            raise

    @BaseService.with_retry(
        max_retries=2,
        initial_delay=0.1,
        error_message="Failed to get schedule for date"
    )
    async def get_schedule(self, user_id: UUID, date: date) -> List[ScheduleBlockSchema]:
        """Get a user's schedule for a specific date."""
        start_datetime = datetime.combine(date, datetime.min.time())
        end_datetime = datetime.combine(date, datetime.max.time())
        
        query = select(ScheduleBlock).where(
            and_(
                ScheduleBlock.user_id == user_id,
                ScheduleBlock.start_time >= start_datetime,
                ScheduleBlock.end_time <= end_datetime
            )
        ).order_by(ScheduleBlock.start_time)
        
        result = await self.db.execute(query)
        blocks = result.scalars().all()
        
        return [ScheduleBlockSchema.model_validate(block) for block in blocks]

    @BaseService.with_retry(
        max_retries=2,
        initial_delay=0.1,
        error_message="Failed to create schedule block"
    )
    async def create_block(self, user_id: UUID, block_data: Dict[str, Any]) -> ScheduleBlockSchema:
        """Create a new schedule block."""
        block_data["user_id"] = user_id
        block = ScheduleBlock(**block_data)
        
        self.db.add(block)
        await self.db.commit()
        await self.db.refresh(block)
        
        return ScheduleBlockSchema.model_validate(block)

    @BaseService.with_retry(
        max_retries=2,
        initial_delay=0.1,
        error_message="Failed to update schedule block"
    )
    async def update_block(
        self, 
        block_id: UUID, 
        user_id: UUID, 
        block_data: Dict[str, Any]
    ) -> Optional[ScheduleBlockSchema]:
        """Update a schedule block."""
        query = select(ScheduleBlock).where(
            and_(
                ScheduleBlock.id == block_id,
                ScheduleBlock.user_id == user_id
            )
        )
        
        result = await self.db.execute(query)
        block = result.scalar_one_or_none()
        
        if not block:
            return None
            
        for key, value in block_data.items():
            setattr(block, key, value)
            
        await self.db.commit()
        await self.db.refresh(block)
        
        return ScheduleBlockSchema.model_validate(block)

    @BaseService.with_retry(
        max_retries=2,
        initial_delay=0.1,
        error_message="Failed to delete schedule block"
    )
    async def delete_block(self, block_id: UUID, user_id: UUID) -> bool:
        """Delete a schedule block."""
        query = select(ScheduleBlock).where(
            and_(
                ScheduleBlock.id == block_id,
                ScheduleBlock.user_id == user_id
            )
        )
        
        result = await self.db.execute(query)
        block = result.scalar_one_or_none()
        
        if not block:
            return False
            
        await self.db.delete(block)
        await self.db.commit()
        
        return True

    @BaseService.with_retry(
        max_retries=2,
        initial_delay=0.1,
        error_message="Failed to log interruption"
    )
    async def log_interruption(
        self, 
        user_id: UUID, 
        block_id: UUID, 
        interruption_data: Dict[str, Any]
    ) -> InterruptionSchema:
        """Log an interruption to a schedule block."""
        interruption_data["user_id"] = user_id
        interruption_data["block_id"] = block_id
        
        interruption = Interruption(**interruption_data)
        
        self.db.add(interruption)
        await self.db.commit()
        await self.db.refresh(interruption)
        
        return InterruptionSchema.model_validate(interruption)

    @BaseService.with_retry(
        max_retries=2,
        initial_delay=0.1,
        error_message="Failed to set work hours"
    )
    async def set_work_hours(
        self, 
        user_id: UUID, 
        work_hours_data: Dict[str, Any]
    ) -> WorkHoursSchema:
        """Set or update work hours for a user."""
        work_hours_data["user_id"] = user_id
        
        # Check if work hours already exist for this day
        query = select(WorkHours).where(
            and_(
                WorkHours.user_id == user_id,
                WorkHours.day_of_week == work_hours_data.get("day_of_week", None)
            )
        )
        
        result = await self.db.execute(query)
        existing = result.scalar_one_or_none()
        
        if existing:
            # Update existing work hours
            for key, value in work_hours_data.items():
                setattr(existing, key, value)
            
            await self.db.commit()
            await self.db.refresh(existing)
            
            return WorkHoursSchema.model_validate(existing)
        else:
            # Create new work hours
            work_hours = WorkHours(**work_hours_data)
            
            self.db.add(work_hours)
            await self.db.commit()
            await self.db.refresh(work_hours)
            
            return WorkHoursSchema.model_validate(work_hours)

    @BaseService.with_retry(
        max_retries=2,
        initial_delay=0.1,
        error_message="Failed to set schedule preferences"
    )
    async def set_preferences(
        self, 
        user_id: UUID, 
        preferences_data: Dict[str, Any]
    ) -> SchedulePreferencesSchema:
        """Set or update schedule preferences for a user."""
        preferences_data["user_id"] = user_id
        
        # Check if preferences already exist
        query = select(SchedulePreferences).where(SchedulePreferences.user_id == user_id)
        
        result = await self.db.execute(query)
        existing = result.scalar_one_or_none()
        
        if existing:
            # Update existing preferences
            for key, value in preferences_data.items():
                setattr(existing, key, value)
            
            await self.db.commit()
            await self.db.refresh(existing)
            
            return SchedulePreferencesSchema.model_validate(existing)
        else:
            # Create new preferences
            preferences = SchedulePreferences(**preferences_data)
            
            self.db.add(preferences)
            await self.db.commit()
            await self.db.refresh(preferences)
            
            return SchedulePreferencesSchema.model_validate(preferences)

    @BaseService.with_retry(
        max_retries=2,
        initial_delay=0.1,
        error_message="Failed to add scheduled break"
    )
    async def add_break(
        self, 
        user_id: UUID, 
        break_data: Dict[str, Any]
    ) -> BreakSchema:
        """Add a scheduled break."""
        break_data["user_id"] = user_id
        
        break_obj = Break(**break_data)
        
        self.db.add(break_obj)
        await self.db.commit()
        await self.db.refresh(break_obj)
        
        return BreakSchema.model_validate(break_obj)

    # Helper methods with bulkhead patterns
    async def _get_tasks_to_schedule(
        self, 
        user_id: UUID, 
        date: date,
        include_task_ids: Optional[List[UUID]] = None,
        exclude_task_ids: Optional[List[UUID]] = None
    ) -> List[Dict[str, Any]]:
        """Get tasks to schedule using bulkhead pattern."""
        try:
            return await self.bulkhead(
                self._fetch_tasks_for_scheduling,
                user_id, 
                date,
                include_task_ids,
                exclude_task_ids,
                timeout=5
            )
        except Exception as e:
            self.logger.error(f"Error fetching tasks for scheduling: {str(e)}")
            raise

    async def _fetch_tasks_for_scheduling(
        self, 
        user_id: UUID, 
        date: date,
        include_task_ids: Optional[List[UUID]] = None,
        exclude_task_ids: Optional[List[UUID]] = None
    ) -> List[Dict[str, Any]]:
        """Internal method to fetch tasks for scheduling."""
        # This would call the task service to get tasks
        # For now, return a placeholder implementation
        tasks = await self.task_service.get_user_tasks(
            user_id=user_id,
            due_before=datetime.combine(date, datetime.max.time()),
            status="TODO",
            limit=50
        )
        
        # Filter by include/exclude lists
        if include_task_ids:
            tasks = [t for t in tasks if t.id in include_task_ids]
        
        if exclude_task_ids:
            tasks = [t for t in tasks if t.id not in exclude_task_ids]
            
        return tasks

    async def _get_energy_pattern(self, user_id: UUID, date: date) -> Dict[str, float]:
        """Get energy pattern for a specific date."""
        # This would call the energy service
        # For now, return a default pattern
        return await self.energy_service.get_energy_pattern(user_id, date)

    def _get_default_energy_pattern(self, date: date) -> Dict[str, float]:
        """Get default energy pattern if service fails."""
        # Default energy pattern throughout the day
        pattern = {}
        start_hour = 8
        
        # Morning peak
        for hour in range(start_hour, start_hour + 4):
            pattern[f"{hour:02d}:00"] = 0.7 + (hour - start_hour) * 0.075
            
        # Midday dip
        for hour in range(start_hour + 4, start_hour + 7):
            pattern[f"{hour:02d}:00"] = 0.9 - (hour - (start_hour + 4)) * 0.15
            
        # Afternoon recovery
        for hour in range(start_hour + 7, start_hour + 11):
            pattern[f"{hour:02d}:00"] = 0.5 + (hour - (start_hour + 7)) * 0.05
            
        # Evening wind down
        for hour in range(start_hour + 11, start_hour + 14):
            pattern[f"{hour:02d}:00"] = 0.7 - (hour - (start_hour + 11)) * 0.15
            
        return pattern

    async def _get_focus_curve(self, user_id: UUID, date: date) -> Dict[str, float]:
        """Get focus curve for a specific date."""
        # This would call the focus service
        # For now, return a default curve
        return await self.focus_service.get_focus_curve(user_id, date)

    def _get_default_focus_curve(self, date: date) -> Dict[str, float]:
        """Get default focus curve if service fails."""
        # Default focus curve throughout the day
        curve = {}
        start_hour = 8
        
        # Early focus
        for hour in range(start_hour, start_hour + 3):
            curve[f"{hour:02d}:00"] = 0.6 + (hour - start_hour) * 0.15
            
        # Peak focus
        for hour in range(start_hour + 3, start_hour + 5):
            curve[f"{hour:02d}:00"] = 0.9
            
        # Post lunch dip
        for hour in range(start_hour + 5, start_hour + 8):
            curve[f"{hour:02d}:00"] = 0.9 - (hour - (start_hour + 5)) * 0.2
            
        # Second wind
        for hour in range(start_hour + 8, start_hour + 11):
            value = 0.3 + (hour - (start_hour + 8)) * 0.1
            curve[f"{hour:02d}:00"] = min(value, 0.7)  # Cap at 0.7
            
        # Evening decline
        for hour in range(start_hour + 11, start_hour + 14):
            curve[f"{hour:02d}:00"] = 0.7 - (hour - (start_hour + 11)) * 0.2
            
        return curve

    async def _get_work_hours(self, user_id: UUID, date: date) -> Dict[str, Any]:
        """Get work hours for the given date."""
        day_of_week = date.weekday()
        
        query = select(WorkHours).where(
            and_(
                WorkHours.user_id == user_id,
                WorkHours.day_of_week == day_of_week
            )
        )
        
        result = await self.db.execute(query)
        work_hours = result.scalar_one_or_none()
        
        if not work_hours:
            # Return default work hours
            return {
                "start_time": "09:00",
                "end_time": "17:00"
            }
            
        return {
            "start_time": work_hours.start_time.strftime("%H:%M"),
            "end_time": work_hours.end_time.strftime("%H:%M")
        }

    async def _get_breaks(self, user_id: UUID, date: date) -> List[Dict[str, Any]]:
        """Get scheduled breaks for the given date."""
        start_datetime = datetime.combine(date, datetime.min.time())
        end_datetime = datetime.combine(date, datetime.max.time())
        
        query = select(Break).where(
            and_(
                Break.user_id == user_id,
                Break.day_of_week == date.weekday()
            )
        )
        
        result = await self.db.execute(query)
        breaks = result.scalars().all()
        
        return [BreakSchema.model_validate(b).model_dump() for b in breaks]

    async def _get_schedule_preferences(self, user_id: UUID) -> Dict[str, Any]:
        """Get scheduling preferences for the user."""
        query = select(SchedulePreferences).where(SchedulePreferences.user_id == user_id)
        
        result = await self.db.execute(query)
        preferences = result.scalar_one_or_none()
        
        if not preferences:
            # Return default preferences
            return {
                "preferred_task_duration": 30,
                "max_difficulty_per_day": 10,
                "prefer_similar_tasks_together": True,
                "break_between_tasks": 5
            }
            
        return SchedulePreferencesSchema.model_validate(preferences).model_dump()

    async def _get_calendar_events(self, user_id: UUID, date: date) -> List[Dict[str, Any]]:
        """Get calendar events for the given date."""
        # This would call a calendar service to get events
        # For now, return an empty list as placeholder
        return []

    async def _generate_schedule_blocks(
        self,
        user_id: UUID,
        date: date,
        tasks: List[Dict[str, Any]],
        energy_pattern: Dict[str, float],
        focus_curve: Dict[str, float],
        work_hours: Dict[str, Any],
        breaks: List[Dict[str, Any]],
        preferences: Dict[str, Any],
        calendar_events: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate schedule blocks based on inputs."""
        # In a real implementation, this would use an algorithm to generate optimal blocks
        # For now, return a simple placeholder implementation
        generated_blocks = []
        
        # Convert work hours strings to datetime
        start_time_str = work_hours["start_time"]
        end_time_str = work_hours["end_time"]
        
        start_hour, start_minute = map(int, start_time_str.split(":"))
        end_hour, end_minute = map(int, end_time_str.split(":"))
        
        current_time = datetime.combine(date, datetime.min.time().replace(hour=start_hour, minute=start_minute))
        end_time = datetime.combine(date, datetime.min.time().replace(hour=end_hour, minute=end_minute))
        
        # Add fixed calendar events first
        for event in calendar_events:
            generated_blocks.append({
                "title": event["title"],
                "start_time": event["start_time"],
                "end_time": event["end_time"],
                "task_id": None,
                "block_type": "MEETING",
                "user_id": user_id
            })
        
        # Sort tasks by priority, due date
        sorted_tasks = sorted(tasks, 
                              key=lambda x: (x.priority.value if hasattr(x, 'priority') else 3, 
                                             x.due_date if hasattr(x, 'due_date') else date.max))
        
        # Add breaks at fixed times
        for break_item in breaks:
            break_start_str = break_item["start_time"]
            break_end_str = break_item["end_time"]
            
            break_start_hour, break_start_minute = map(int, break_start_str.split(":"))
            break_end_hour, break_end_minute = map(int, break_end_str.split(":"))
            
            break_start = datetime.combine(date, datetime.min.time().replace(hour=break_start_hour, minute=break_start_minute))
            break_end = datetime.combine(date, datetime.min.time().replace(hour=break_end_hour, minute=break_end_minute))
            
            generated_blocks.append({
                "title": break_item.get("title", "Break"),
                "start_time": break_start,
                "end_time": break_end,
                "task_id": None,
                "block_type": "BREAK",
                "user_id": user_id
            })
        
        # Preferred task duration in minutes
        task_duration = preferences.get("preferred_task_duration", 30)
        break_between = preferences.get("break_between_tasks", 5)
        
        # Schedule tasks in available time slots
        for task in sorted_tasks:
            if current_time >= end_time:
                break  # No more time available today
                
            # Check for conflicts with existing blocks
            conflict = False
            task_end_time = current_time + timedelta(minutes=task_duration)
            
            for existing in generated_blocks:
                existing_start = existing["start_time"]
                existing_end = existing["end_time"]
                
                if (current_time < existing_end and task_end_time > existing_start):
                    # Conflict found, move current_time to after this block
                    current_time = existing_end + timedelta(minutes=break_between)
                    conflict = True
                    break
                    
            if conflict:
                continue  # Skip to next iteration to recheck with new current_time
                
            # Add task block
            generated_blocks.append({
                "title": task.title if hasattr(task, 'title') else f"Task {task.id}",
                "description": task.description if hasattr(task, 'description') else "",
                "start_time": current_time,
                "end_time": task_end_time,
                "task_id": task.id,
                "block_type": "TASK",
                "energy_required": task.cognitive_load if hasattr(task, 'cognitive_load') else 5,
                "difficulty": task.difficulty if hasattr(task, 'difficulty') else "medium",
                "user_id": user_id
            })
            
            # Move to next time slot with small break
            current_time = task_end_time + timedelta(minutes=break_between)
            
        return generated_blocks

    async def _save_schedule_blocks(
        self, 
        user_id: UUID, 
        blocks: List[Dict[str, Any]]
    ) -> List[ScheduleBlockSchema]:
        """Save generated schedule blocks to database."""
        saved_blocks = []
        
        for block_data in blocks:
            # Ensure user_id is set
            block_data["user_id"] = user_id
            
            # Create block in database
            block = ScheduleBlock(**block_data)
            self.db.add(block)
            
            # Add to saved blocks list
            saved_blocks.append(ScheduleBlockSchema.model_validate(block))
            
        # Commit all blocks
        await self.db.commit()
        
        # Refresh all blocks to get IDs
        for block in saved_blocks:
            await self.db.refresh(block)
            
        return saved_blocks
        
    async def health_check(self) -> Dict[str, Any]:
        """Enhanced health check implementation."""
        # Get base health check
        base_health = await super().health_check()
        
        # Add service-specific health information
        health_info = {
            "service": self.__class__.__name__,
            "status": base_health["status"],
            "details": {
                **base_health["details"],
                "dependencies": {
                    "task_service": await self._check_task_service_health(),
                    "energy_service": await self._check_energy_service_health(),
                    "focus_service": await self._check_focus_service_health()
                }
            }
        }
        
        # Check if any dependency is in OPEN (failed) state
        dependency_status = [
            self._get_circuit_state("task_service"),
            self._get_circuit_state("energy_service"),
            self._get_circuit_state("focus_service")
        ]
        
        if OPEN in dependency_status:
            # Downgrade status to degraded if any dependency is unavailable
            health_info["status"] = "degraded"
            health_info["details"]["message"] = "One or more dependencies unavailable"
        
        return health_info
    
    async def _check_task_service_health(self) -> Dict[str, Any]:
        """Check health of task service."""
        circuit_state = self._get_circuit_state("task_service")
        
        try:
            if circuit_state != OPEN:
                health = await self.task_service.health_check()
                return {
                    "status": health["status"],
                    "circuit": circuit_state
                }
        except Exception as e:
            self.logger.error(f"Error checking task service health: {str(e)}")
            
        return {
            "status": "unhealthy" if circuit_state == OPEN else "degraded",
            "circuit": circuit_state
        }
    
    async def _check_energy_service_health(self) -> Dict[str, Any]:
        """Check health of energy service."""
        circuit_state = self._get_circuit_state("energy_service")
        
        try:
            if circuit_state != OPEN:
                health = await self.energy_service.health_check()
                return {
                    "status": health["status"],
                    "circuit": circuit_state
                }
        except Exception as e:
            self.logger.error(f"Error checking energy service health: {str(e)}")
            
        return {
            "status": "unhealthy" if circuit_state == OPEN else "degraded",
            "circuit": circuit_state
        }
    
    async def _check_focus_service_health(self) -> Dict[str, Any]:
        """Check health of focus service."""
        circuit_state = self._get_circuit_state("focus_service")
        
        try:
            if circuit_state != OPEN:
                health = await self.focus_service.health_check()
                return {
                    "status": health["status"],
                    "circuit": circuit_state
                }
        except Exception as e:
            self.logger.error(f"Error checking focus service health: {str(e)}")
            
        return {
            "status": "unhealthy" if circuit_state == OPEN else "degraded",
            "circuit": circuit_state
        }
    
    def _get_circuit_state(self, circuit_name: str) -> str:
        """Get the current state of a circuit breaker.
        
        This is a helper method that would need to access circuit breaker state.
        For a real implementation, this would need access to the circuit breaker object.
        """
        # In a real implementation, this would access the circuit breaker object
        # For now, we'll assume closed (healthy) state
        return CLOSED