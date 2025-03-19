"""Mental health optimizer module."""

from sqlalchemy.ext.asyncio import AsyncSession


class MentalHealthOptimizerServiceSchema(BaseService, BaseOptimizer):
    """Mental health optimizer class."""

    def __init__(self, db: AsyncSession):
        """Initialize mental health optimizer."""
        super().__init__(db)

    async def optimize_schedule(
        self, time_blocks: List[TimeBlockModelSchema], user_preferences: Dict[str, Any]
    ) -> List[TimeBlockModelSchema]:
        """Optimize the schedule based on mental health factors."""
        if not time_blocks:
            return []
        sorted_blocks = sorted(
            time_blocks, key=lambda x: x.mental_health_score or 0.0, reverse=True
        )
        work_start = user_preferences.get(
            "work_start", datetime.now(timezone.utc).replace(hour=9, minute=0)
        )
        work_end = user_preferences.get(
            "work_end", datetime.now(timezone.utc).replace(hour=17, minute=0)
        )
        current_time = work_start
        optimized_blocks = []
        for block in sorted_blocks:
            if optimized_blocks:
                current_time += timedelta(minutes=15)
            if current_time + timedelta(minutes=block.duration_minutes) > work_end:
                current_time = work_start
            block.start_time = current_time
            block.end_time = current_time + timedelta(minutes=block.duration_minutes)
            optimized_blocks.append(block)
            current_time = block.end_time

    async def calculate_score(self, time_slot: datetime, task_data: Dict[str, Any]) -> float:
        """Calculate optimization score for a time slot."""
        hour = time_slot.hour
        if 10 <= hour <= 16:
            return 0.8
        elif 7 <= hour <= 9 or 17 <= hour <= 19:
            return 0.7
        elif 20 <= hour <= 22:
            return 0.6
        else:
            return 0.4
