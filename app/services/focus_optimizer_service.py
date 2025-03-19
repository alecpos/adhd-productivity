"""Focus optimizer module."""

from sqlalchemy.ext.asyncio import AsyncSession


class FocusOptimizerServiceSchema(BaseService, BaseOptimizer):
    """Focus optimizer class."""

    def __init__(self, db: AsyncSession):
        """Initialize focus optimizer."""
        super().__init__(db)

    async def optimize_schedule(
        self, time_blocks: List[TimeBlockModelSchema], user_preferences: Dict[str, Any]
    ) -> List[TimeBlockModelSchema]:
        """Optimize the schedule based on focus requirements."""
        if not time_blocks:
            return []
        focus_duration = user_preferences.get("focus_duration", 25)
        break_duration = user_preferences.get("break_duration", 5)
        long_break_duration = user_preferences.get("long_break_duration", 15)
        sessions_before_long_break = user_preferences.get("sessions_before_long_break", 4)
        sorted_blocks = sorted(time_blocks, key=lambda x: x.focus_level or 0.0, reverse=True)
        optimized_blocks = []
        session_count = 0
        current_time = datetime.now(timezone.utc).replace(hour=9, minute=0)
        for block in sorted_blocks:
            if block.block_type == BlockType.TASK:
                block.start_time = current_time
                block.end_time = current_time + timedelta(minutes=focus_duration)
                optimized_blocks.append(block)
                current_time = block.end_time
                session_count += 1
                if session_count % sessions_before_long_break == 0:
                    break_block = TimeBlockModelSchema(
                        user_id=block.user_id,
                        start_time=current_time,
                        end_time=current_time + timedelta(minutes=long_break_duration),
                        block_type=BlockType.BREAK,
                        title="Long Break",
                        is_break=True,
                    )
                    optimized_blocks.append(break_block)
                    current_time = break_block.end_time
                else:
                    break_block = TimeBlockModelSchema(
                        user_id=block.user_id,
                        start_time=current_time,
                        end_time=current_time + timedelta(minutes=break_duration),
                        block_type=BlockType.BREAK,
                        title="Short Break",
                        is_break=True,
                    )
                    optimized_blocks.append(break_block)
                    current_time = break_block.end_time
            else:
                block.start_time = current_time
                block.end_time = current_time + timedelta(minutes=block.duration_minutes)
                optimized_blocks.append(block)
                current_time = block.end_time

    async def calculate_score(self, time_slot: datetime, task_data: Dict[str, Any]) -> float:
        """Calculate optimization score for a time slot."""
        hour = time_slot.hour
        if 9 <= hour <= 12:
            return 0.9
        elif 15 <= hour <= 17:
            return 0.8
        elif 19 <= hour <= 21:
            return 0.6
        else:
            return 0.4
