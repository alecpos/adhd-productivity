"""Scheduling service module."""

from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from uuid import UUID, uuid4
from dataclasses import dataclass
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.services.base_service import BaseService
from app.models.scheduling_model import ScheduleBlock, BlockType
from app.models.task_model import TaskModel
from app.schemas.scheduling_schema import (
    ScheduleBlock as ScheduleBlockSchema,
    ScheduleOptimizationRequest,
    OptimizedSchedule,
    ScheduleSuggestion,
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