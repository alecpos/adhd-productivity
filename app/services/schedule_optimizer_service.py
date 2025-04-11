"""Service for optimizing user schedules using ML models."""

import logging
from datetime import datetime, time, timedelta, timezone
from typing import Any, Dict, List, Optional

import tensorflow as tf
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.time_block_model import TimeBlockModel, BlockType, BlockPriority
from app.schemas.scheduling_schema import (
    WorkHours,
    EnergySchedulingPattern as EnergyPatternSchema,
    SchedulePreferences as ScheduleParamsSchema,
    TimeBlockBaseSchema as ScheduleOptimizerSchema,
)


# Simple schema for None returns
class NoneSchema:
    pass


logger = logging.getLogger(__name__)


class ScheduleOptimizerService:
    """Service for optimizing user schedules using ML models."""

    def __init__(self, db: AsyncSession):
        """Initialize the service."""
        self.db = db
        self.model = None

    async def initialize(self):
        """Initialize the service and load the model."""
        self.model = ScheduleOptimizerSchema()
        print("Loaded pre-trained schedule optimizer model.")

    def _ensure_timezone_aware(self, dt: datetime) -> datetime:
        """Ensure a datetime is timezone-aware by converting to UTC if naive."""
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt

    async def optimize_schedule(
        self,
        user_id: str,
        tasks: List[Dict[str, Any]],
        date: datetime,
        work_hours: Optional[WorkHours] = None,
        energy_pattern: Optional[EnergyPatternSchema] = None,
    ) -> List[TimeBlockModel]:
        """Optimize a daily schedule for a user."""
        date = self._ensure_timezone_aware(date)
        if work_hours is None or energy_pattern is None:
            preferences = await self._get_user_preferences(user_id)
            work_hours = work_hours or preferences.work_hours
            energy_pattern = energy_pattern or preferences.energy_pattern
        try:
            historical_data = await self._get_historical_blocks(user_id)
        except Exception as e:
            print(f"Error retrieving historical blocks: {str(e)}")
            historical_data = []
        schedule = self.model.optimize_schedule(
            tasks=tasks,
            work_hours=work_hours,
            energy_pattern=energy_pattern,
            historical_data=historical_data,
        )
        time_blocks = []
        for block in schedule:
            block_start = None
            block_end = None
            if isinstance(block, dict):
                start_time = block.get("start_time")
                if isinstance(start_time, str):
                    block_start = datetime.fromisoformat(start_time)
                elif isinstance(start_time, dict):
                    block_start = datetime.combine(
                        date.date(),
                        time(
                            hour=start_time.get("hour", 0),
                            minute=start_time.get("minute", 0),
                        ),
                    )
            else:
                try:
                    block_start = getattr(block, "start_time")
                except AttributeError:
                    block_start = None
            is_flexible = (
                block.get("is_flexible", True)
                if isinstance(block, dict)
                else getattr(block, "is_flexible", True)
            )
            if block_start is None and is_flexible:
                block_start = date.replace(hour=9, minute=0)
            if isinstance(block, dict):
                end_time = block.get("end_time")
                if isinstance(end_time, str):
                    block_end = datetime.fromisoformat(end_time)
                elif isinstance(end_time, dict):
                    block_end = datetime.combine(
                        date.date(),
                        time(
                            hour=end_time.get("hour", 0),
                            minute=end_time.get("minute", 0),
                        ),
                    )
            else:
                try:
                    block_end = getattr(block, "end_time")
                except AttributeError:
                    block_end = None
            if block_end is None and block_start is not None:
                duration = (
                    block.get("estimated_duration", 60)
                    if isinstance(block, dict)
                    else getattr(block, "estimated_duration", 60)
                )
                block_end = block_start + timedelta(minutes=duration)
            if block_start is None or block_end is None:
                raise ValueError(f"Invalid time format for block: {block}")
            block_start = self._ensure_timezone_aware(block_start)
            block_end = self._ensure_timezone_aware(block_end)
            time_block = TimeBlockModel(
                user_id=user_id,
                title=(
                    block.get("title", "")
                    if isinstance(block, dict)
                    else getattr(block, "title", "")
                ),
                description=(
                    block.get("description", "")
                    if isinstance(block, dict)
                    else getattr(block, "description", "")
                ),
                start_time=block_start,
                end_time=block_end,
                block_type=(
                    block.get("block_type", "task")
                    if isinstance(block, dict)
                    else getattr(block, "block_type", "task")
                ),
                priority=(
                    block.get("priority", 1)
                    if isinstance(block, dict)
                    else getattr(block, "priority", 1)
                ),
                is_flexible=is_flexible,
                energy_level=(
                    block.get("energy_level")
                    if isinstance(block, dict)
                    else getattr(block, "energy_level", None)
                ),
                focus_level=(
                    block.get("focus_level")
                    if isinstance(block, dict)
                    else getattr(block, "focus_level", None)
                ),
                effectiveness_score=(
                    block.get("effectiveness_score", 0.0)
                    if isinstance(block, dict)
                    else getattr(block, "effectiveness_score", 0.0)
                ),
            )
            time_blocks.append(time_block)
        return time_blocks

    async def _get_historical_blocks(self, user_id: str) -> List[TimeBlockModel]:
        """Get historical time blocks for training."""
        try:
            query = (
                select(TimeBlockModel)
                .where(TimeBlockModel.user_id == user_id)
                .order_by(TimeBlockModel.start_time.desc())
                .limit(100)
            )
            result = await self.db.execute(query)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error retrieving historical blocks: {str(e)}")
            return []

    async def _train_model(self, user_id: str) -> NoneSchema:
        """Train the model using historical data."""
        blocks = await self._get_historical_blocks(user_id)
        if not blocks:
            logger.warning("No historical data available for training")
            return
        X = {
            "block_type": tf.constant(
                [list(BlockType).index(block.block_type) for block in blocks],
                dtype=tf.int32,
            ),
            "priority": tf.constant(
                [list(BlockPriority).index(block.priority) for block in blocks],
                dtype=tf.int32,
            ),
            "time_features": tf.constant(
                [
                    [
                        block.start_time.hour / 24.0,
                        block.start_time.minute / 60.0,
                        1.0 if block.is_flexible else 0.0,
                    ]
                    for block in blocks
                ],
                dtype=tf.float32,
            ),
            "energy_features": tf.constant(
                [[block.energy_level / 10.0] * 48 for block in blocks], dtype=tf.float32
            ),
            "historical_metrics": tf.constant(
                [
                    [
                        block.completion_rate or 0.0,
                        block.effectiveness_score or 0.0,
                        block.focus_level / 10.0 if block.focus_level else 0.0,
                        block.energy_level / 10.0 if block.energy_level else 0.0,
                    ]
                    for block in blocks
                ],
                dtype=tf.float32,
            ),
        }
        y = {
            "score_output": tf.constant(
                [
                    [(block.effectiveness_score or 0.0) * (block.completion_rate or 0.0)]
                    for block in blocks
                ],
                dtype=tf.float32,
            ),
            "duration_output": tf.constant(
                [[(block.end_time - block.start_time).total_seconds() / 60.0] for block in blocks],
                dtype=tf.float32,
            ),
        }
        history = self.model.fit(X, y, epochs=5, batch_size=32, verbose=0)
        logger.info(f"Model trained with history: {history.history}")

    async def _get_energy_patterns(self, user_id: str) -> List[EnergyPatternSchema]:
        """Get energy patterns for a user."""
        return [
            EnergyPatternSchema(
                pattern_type="morning",
                peak_hours=[
                    {"start": time(9, 0), "end": time(12, 0)},
                    {"start": time(14, 0), "end": time(17, 0)},
                ],
                low_energy_periods=[{"start": time(12, 0), "end": time(14, 0)}],
            )
        ]

    async def _get_work_hours(self, user_id: str) -> List[WorkHours]:
        """Get work hours for a user."""
        return [
            WorkHours(
                start=time(9, 0),
                end=time(17, 0),
                breaks=[{"start": time(12, 0), "end": time(13, 0)}],
            )
        ]

    async def _get_user_preferences(self, user_id: str) -> ScheduleParamsSchema:
        """Get scheduling preferences for a user."""
        work_hours = await self._get_work_hours(user_id)
        energy_patterns = await self._get_energy_patterns(user_id)
        return ScheduleParamsSchema(work_hours=work_hours[0], energy_pattern=energy_patterns[0])
