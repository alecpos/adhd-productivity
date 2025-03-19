"""Energy optimizer module."""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.time_block_model import TimeBlockModel
from app.services.base_service import BaseService
from app.services.base_optimizer_service import BaseOptimizerService


class EnergyOptimizerServiceSchema(BaseService, BaseOptimizerService):
    """Energy optimizer class."""

    def __init__(self, db: AsyncSession):
        """Initialize energy optimizer."""
        super().__init__(db)

    async def optimize_schedule(
        self, time_blocks: List[TimeBlockModel], user_preferences: Dict[str, Any]
    ) -> List[TimeBlockModel]:
        """Optimize the schedule based on energy levels."""
        if not time_blocks:
            return []
        sorted_blocks = sorted(time_blocks, key=lambda x: x.energy_level or 0.0, reverse=True)
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
        if 8 <= hour <= 11:
            return 0.9
        elif 14 <= hour <= 16:
            return 0.7
        elif 16 <= hour <= 18:
            return 0.5
        else:
            return 0.3
