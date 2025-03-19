"""Base optimizer for scheduling."""

from abc import ABC, abstractmethod
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any
from datetime import datetime, timedelta
from uuid import UUID

from app.models.user_model import UserModel
from app.schemas.task_schema import TaskSchema
from app.models.task_model import TaskModel
from app.models.time_block_model import TimeBlockModel
from app.services.base_service import BaseService
from app.utils.metrics import ServiceMetrics

service_metrics = ServiceMetrics('optimizers')

class BaseOptimizerService(BaseService, ABC):
    """Base class for schedule optimizers."""

    def __init__(self, db: AsyncSession):
        """Initialize the optimizer with database session."""
        self.db = db
        self.metrics = service_metrics

    @abstractmethod
    async def optimize_schedule(self, time_blocks: List[TimeBlockModel], user_preferences: Dict[str, Any]) -> List[TimeBlockModel]:
        """Optimize the schedule based on specific criteria."""

    @abstractmethod
    async def calculate_score(self, time_slot: datetime, task_data: Dict[str, Any]) -> float:
        """Calculate optimization score for a time slot."""

    async def optimize_tasks(self, user_id: UUID, tasks: List[UserModel]) -> List[UserModel]:
        """Optimize task scheduling."""

    def _validate_time_blocks(self, time_blocks: List[TimeBlockModel]) -> bool:
        """Validate time blocks for scheduling conflicts."""
        if not time_blocks:
            return True
        sorted_blocks = sorted(time_blocks, key=lambda x: x.start_time)
        for i in range(len(sorted_blocks) - 1):
            if sorted_blocks[i].end_time > sorted_blocks[i + 1].start_time:
                return False
        return True

    def _get_available_slots(self, start_time: datetime, end_time: datetime, duration: timedelta, existing_blocks: List[TimeBlockModel]) -> List[datetime]:
        """Find available time slots between existing blocks."""
        available_slots = []
        current_time = start_time
        sorted_blocks = sorted(existing_blocks, key=lambda x: x.start_time)
        for block in sorted_blocks:
            if block.start_time - current_time >= duration:
                available_slots.append(current_time)
            current_time = block.end_time
        if end_time - current_time >= duration:
            available_slots.append(current_time)
