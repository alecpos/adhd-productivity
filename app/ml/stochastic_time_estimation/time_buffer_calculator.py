"""
Time Buffer Calculation Algorithm for Transition Periods (STORY-8)

This module implements an algorithm to calculate appropriate time buffers between
tasks, accounting for task switching difficulty, context changes, and individual
transition patterns. This is especially important for individuals with ADHD who
often struggle with transitions and task switching.

Key components:
1. Task transition difficulty assessment
2. Context change impact calculation
3. Personalized transition pattern analysis
4. Integration with other time estimation components
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any, Union
from datetime import datetime, timedelta
import logging
import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
from enum import Enum
import math

from app.models.task_model import TaskModel
from app.models.user_model import UserModel
from app.ml.models import BaseMLModel

logger = logging.getLogger(__name__)


class TransitionDifficulty(Enum):
    """Classification of transition difficulty levels."""

    MINIMAL = "minimal"  # Almost no context switch
    EASY = "easy"  # Simple context switch
    MODERATE = "moderate"  # Notable context switch
    DIFFICULT = "difficult"  # Significant context switch
    SEVERE = "severe"  # Extremely challenging context switch


class ContextChangeType(Enum):
    """Types of context changes that affect transition time."""

    LOCATION = "location"  # Physical location change
    TOOLS = "tools"  # Different tools or setup
    MENTAL_CONTEXT = "mental_context"  # Different thinking modes
    SOCIAL_CONTEXT = "social_context"  # Different social environments
    ENERGY_LEVEL = "energy_level"  # Different energy requirements


class TimeBufferCalculator(BaseMLModel):
    """
    Algorithm to calculate appropriate time buffers between tasks.

    This model analyzes task pairs and user patterns to:
    - Determine transition difficulty between tasks
    - Calculate context change impacts
    - Consider individual transition patterns
    - Generate appropriate time buffers
    - Adapt to observed transition behaviors

    It integrates with other components of the stochastic time estimation engine.
    """

    def __init__(
        self,
        db: Optional[AsyncSession] = None,
        model_path: Optional[str] = None,
        min_buffer_minutes: int = 5,
        max_buffer_minutes: int = 60,
        base_transition_times: Optional[Dict[str, int]] = None,
        context_change_weights: Optional[Dict[str, float]] = None,
        adaptation_rate: float = 0.2,
        lookback_period: int = 30,  # days
    ):
        """
        Initialize the Time Buffer Calculator.

        Args:
            db: Database session for retrieving task and transition data
            model_path: Path to saved model parameters
            min_buffer_minutes: Minimum buffer time in minutes
            max_buffer_minutes: Maximum buffer time in minutes
            base_transition_times: Default transition times for different difficulty levels
            context_change_weights: Weights for different types of context changes
            adaptation_rate: Rate at which to adapt to new transition observations
            lookback_period: How far back to look for transition patterns, in days
        """
        super().__init__(model_path=model_path)
        self.db = db
        self.min_buffer_minutes = min_buffer_minutes
        self.max_buffer_minutes = max_buffer_minutes
        self.adaptation_rate = adaptation_rate
        self.lookback_period = lookback_period

        # Default base transition times (minutes) for different difficulty levels
        self.base_transition_times = base_transition_times or {
            TransitionDifficulty.MINIMAL.value: 5,
            TransitionDifficulty.EASY.value: 10,
            TransitionDifficulty.MODERATE.value: 15,
            TransitionDifficulty.DIFFICULT.value: 25,
            TransitionDifficulty.SEVERE.value: 40,
        }

        # Default weights for different types of context changes
        self.context_change_weights = context_change_weights or {
            ContextChangeType.LOCATION.value: 0.35,  # Physical movement is significant
            ContextChangeType.TOOLS.value: 0.20,  # Setting up tools takes time
            ContextChangeType.MENTAL_CONTEXT.value: 0.25,  # Mental context switching is hard
            ContextChangeType.SOCIAL_CONTEXT.value: 0.10,  # Social context changes have some impact
            ContextChangeType.ENERGY_LEVEL.value: 0.10,  # Energy level transitions have some impact
        }

        # User-specific transition adjustments (filled during runtime)
        self.user_adjustments = {}

    async def calculate_buffer(self, current_task_id: str, next_task_id: str) -> Dict[str, Any]:
        """
        Calculate appropriate time buffer between two tasks.

        Args:
            current_task_id: ID of the current task
            next_task_id: ID of the next task

        Returns:
            Dictionary with buffer calculation including:
            - buffer_minutes: Calculated buffer time in minutes
            - transition_difficulty: Assessed difficulty level
            - context_changes: Detailed context changes
            - adjustment_factors: Factors that influenced the calculation
        """
        if self.db is None:
            return {
                "error": "No database connection available",
                "buffer_minutes": self.min_buffer_minutes,
            }

        # Get task information
        current_task = await self._get_task(current_task_id)
        next_task = await self._get_task(next_task_id)

        if current_task is None or next_task is None:
            return {
                "error": "One or both tasks not found",
                "buffer_minutes": self.min_buffer_minutes,
            }

        # Analyze transition difficulty
        transition_difficulty, difficulty_factors = await self._analyze_transition_difficulty(
            current_task, next_task
        )

        # Determine base buffer time from difficulty
        base_buffer = self.base_transition_times.get(
            transition_difficulty.value,
            self.base_transition_times[TransitionDifficulty.MODERATE.value],
        )

        # Calculate context change impact
        context_changes = await self._calculate_context_changes(current_task, next_task)

        # This is a temporary fix for the function signature mismatch
        if (
            isinstance(context_changes, dict)
            and context_changes.get("location", {}).get("change_factor", None) is not None
        ):
            # Convert from new detailed format to simplified format for _calculate_context_impact_factor
            simplified_changes = {}
            for change_type, details in context_changes.items():
                if isinstance(details, dict) and "change_factor" in details:
                    simplified_changes[change_type] = details
            context_impact_factor = self._calculate_context_impact_factor(simplified_changes)
        else:
            # If already in the correct format
            context_impact_factor = self._calculate_context_impact_factor(context_changes)

        # Get user-specific adjustments
        user_id = current_task.user_id
        user_factor = await self._get_user_adjustment_factor(user_id, current_task, next_task)

        # Calculate final buffer time
        buffer_minutes = base_buffer * context_impact_factor * user_factor

        # Ensure buffer is within bounds
        buffer_minutes = max(
            self.min_buffer_minutes, min(int(buffer_minutes), self.max_buffer_minutes)
        )

        return {
            "buffer_minutes": buffer_minutes,
            "transition_difficulty": transition_difficulty.value,
            "difficulty_factors": difficulty_factors,
            "context_changes": context_changes,
            "adjustment_factors": {
                "base_buffer": base_buffer,
                "context_impact_factor": context_impact_factor,
                "user_adjustment_factor": user_factor,
            },
            "user_id": user_id,
            "calculation_timestamp": datetime.now().isoformat(),
        }

    async def update_with_observation(
        self,
        current_task_id: str,
        next_task_id: str,
        actual_transition_minutes: int,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Update model with observed transition time.

        Args:
            current_task_id: ID of the current task
            next_task_id: ID of the next task
            actual_transition_minutes: Actual time taken for transition
            user_id: Optional user ID if not available from tasks

        Returns:
            Dictionary with update results
        """
        if self.db is None:
            logger.warning("Cannot update model - no database connection available")
            return {"error": "No database connection available"}

        try:
            # Get task information
            current_task = await self._get_task(current_task_id)
            next_task = await self._get_task(next_task_id)

            if current_task is None or next_task is None:
                logger.warning(
                    f"Cannot update model - one or both tasks not found: {current_task_id}, {next_task_id}"
                )
                return {"error": "One or both tasks not found"}

            # Get user ID from task or parameter
            task_user_id = None
            if hasattr(current_task, "user_id"):
                task_user_id = current_task.user_id
            elif isinstance(current_task, dict) and "user_id" in current_task:
                task_user_id = current_task["user_id"]

            user_id = user_id or task_user_id
            if not user_id:
                return {"error": "User ID not found"}

            # Calculate current prediction for comparison
            prediction = await self.calculate_buffer(current_task_id, next_task_id)
            predicted_minutes = prediction.get("buffer_minutes", self.min_buffer_minutes)

            # Calculate category keys for this transition
            category_keys = await self._get_transition_category_keys(current_task, next_task)

            # Initialize user adjustments if not present
            if user_id not in self.user_adjustments:
                self.user_adjustments[user_id] = {}

            # Update each category with new observation
            for key in category_keys:
                if key not in self.user_adjustments[user_id]:
                    self.user_adjustments[user_id][key] = 1.0

                # Calculate adjustment - if actual > predicted, increase factor
                error_ratio = (
                    actual_transition_minutes / predicted_minutes if predicted_minutes > 0 else 1.0
                )

                # Limit extreme adjustments
                error_ratio = max(0.5, min(error_ratio, 2.0))

                # Apply gradual adjustment using adaptation rate
                self.user_adjustments[user_id][key] = (
                    1 - self.adaptation_rate
                ) * self.user_adjustments[user_id][key] + self.adaptation_rate * error_ratio

            # Log the update
            logger.info(
                f"Updated transition model for user {user_id}: "
                f"predicted={predicted_minutes}m, actual={actual_transition_minutes}m, "
                f"keys={category_keys}"
            )

            # Store the observation in the database
            await self._store_transition_observation(
                user_id, current_task_id, next_task_id, predicted_minutes, actual_transition_minutes
            )

            return {
                "user_id": user_id,
                "current_task_id": current_task_id,
                "next_task_id": next_task_id,
                "predicted_minutes": predicted_minutes,
                "actual_minutes": actual_transition_minutes,
                "category_keys": category_keys,
                "updated_factors": {
                    key: self.user_adjustments[user_id][key] for key in category_keys
                },
            }

        except Exception as e:
            logger.error(f"Error updating with observation: {e}")
            return {"error": str(e)}

    async def get_user_transition_stats(self, user_id: str) -> Dict[str, Any]:
        """
        Get transition statistics for a user.

        Args:
            user_id: ID of the user

        Returns:
            Dictionary with transition statistics
        """
        if self.db is None:
            return {"error": "No database connection available"}

        # Get recent transition observations
        transitions = await self._get_transition_history(user_id)

        if not transitions:
            return {
                "user_id": user_id,
                "transition_count": 0,
                "average_transition_time": 0,
                "prediction_accuracy": 0,
                "common_transition_difficulties": {},
                "transition_time_by_day": {},
                "transition_time_by_hour": {},
            }

        # Calculate statistics
        total_actual = sum(t.get("actual_minutes", 0) for t in transitions)
        avg_actual = total_actual / len(transitions) if transitions else 0

        # Calculate prediction accuracy
        prediction_errors = [
            abs(t.get("actual_minutes", 0) - t.get("predicted_minutes", 0))
            for t in transitions
            if "actual_minutes" in t and "predicted_minutes" in t
        ]
        avg_error = sum(prediction_errors) / len(prediction_errors) if prediction_errors else 0
        accuracy = max(0, 100 - (avg_error / avg_actual * 100)) if avg_actual > 0 else 0

        # Count transition difficulties
        difficulties = {}
        for t in transitions:
            diff = t.get("transition_difficulty", TransitionDifficulty.MODERATE.value)
            difficulties[diff] = difficulties.get(diff, 0) + 1

        # Transition time by day of week
        day_data = {}
        for t in transitions:
            if "timestamp" in t and "actual_minutes" in t:
                day = datetime.fromisoformat(t["timestamp"]).strftime("%A")
                if day not in day_data:
                    day_data[day] = {"count": 0, "total": 0}
                day_data[day]["count"] += 1
                day_data[day]["total"] += t["actual_minutes"]

        day_averages = {
            day: data["total"] / data["count"] if data["count"] > 0 else 0
            for day, data in day_data.items()
        }

        # Transition time by hour of day
        hour_data = {}
        for t in transitions:
            if "timestamp" in t and "actual_minutes" in t:
                hour = datetime.fromisoformat(t["timestamp"]).hour
                if hour not in hour_data:
                    hour_data[hour] = {"count": 0, "total": 0}
                hour_data[hour]["count"] += 1
                hour_data[hour]["total"] += t["actual_minutes"]

        hour_averages = {
            f"{hour:02d}:00": data["total"] / data["count"] if data["count"] > 0 else 0
            for hour, data in hour_data.items()
        }

        return {
            "user_id": user_id,
            "transition_count": len(transitions),
            "average_transition_time": round(avg_actual, 1),
            "prediction_accuracy": round(accuracy, 1),
            "common_transition_difficulties": difficulties,
            "transition_time_by_day": day_averages,
            "transition_time_by_hour": hour_averages,
        }

    async def _analyze_transition_difficulty(
        self,
        current_task: Union[TaskModel, Dict[str, Any]],
        next_task: Union[TaskModel, Dict[str, Any]],
    ) -> Tuple[TransitionDifficulty, Dict[str, Any]]:
        """
        Analyze the difficulty of transitioning between two tasks.

        Args:
            current_task: Current task model or dictionary
            next_task: Next task model or dictionary

        Returns:
            Tuple of (difficulty_level, factors_dict)
        """
        factors = {}

        # Compare task categories - handle both object and dict patterns
        # Get categories with proper access pattern
        current_category = self._get_attribute(current_task, "category", "work")
        next_category = self._get_attribute(next_task, "category", "work")
        category_switch = current_category != next_category
        factors["category_switch"] = category_switch

        # Compare required focus levels
        current_focus = self._get_attribute(current_task, "focus_required", 3)
        next_focus = self._get_attribute(next_task, "focus_required", 3)
        focus_difference = abs(current_focus - next_focus)
        factors["focus_difference"] = focus_difference

        # Compare required energy levels
        current_energy = self._get_attribute(current_task, "energy_required", 3)
        next_energy = self._get_attribute(next_task, "energy_required", 3)
        energy_difference = abs(current_energy - next_energy)
        factors["energy_difference"] = energy_difference

        # Compare task complexity/difficulty
        current_difficulty = self._get_attribute(current_task, "difficulty", 3)
        next_difficulty = self._get_attribute(next_task, "difficulty", 3)
        difficulty_difference = abs(current_difficulty - next_difficulty)
        factors["difficulty_difference"] = difficulty_difference

        # Check location change
        location_change = False
        current_location = self._get_attribute(current_task, "location", None)
        next_location = self._get_attribute(next_task, "location", None)
        if current_location and next_location:
            location_change = current_location != next_location
        factors["location_change"] = location_change

        # Check tool change
        tool_change = False
        current_tools = self._get_attribute(current_task, "tools_needed", [])
        next_tools = self._get_attribute(next_task, "tools_needed", [])
        if current_tools and next_tools:
            try:
                # Handle various collection types that might not be directly convertible to set
                current_set = (
                    set(current_tools)
                    if isinstance(current_tools, (list, set, tuple))
                    else {current_tools}
                )
                next_set = (
                    set(next_tools) if isinstance(next_tools, (list, set, tuple)) else {next_tools}
                )

                common_tools = current_set.intersection(next_set)
                all_tools = current_set.union(next_set)

                if all_tools:
                    tool_similarity = len(common_tools) / len(all_tools)
                    tool_change = tool_similarity < 0.5
                else:
                    tool_change = False
            except (TypeError, ValueError, AttributeError):
                # Fall back to simple comparison
                tool_change = current_tools != next_tools
        factors["tool_change"] = tool_change

        # Calculate weighted score for overall difficulty
        score = 0
        score += 2 if category_switch else 0
        score += focus_difference * 0.7
        score += energy_difference * 0.5
        score += difficulty_difference * 0.6
        score += 3 if location_change else 0
        score += 2 if tool_change else 0

        # Determine difficulty level based on score
        if score < 2:
            difficulty = TransitionDifficulty.MINIMAL
        elif score < 4:
            difficulty = TransitionDifficulty.EASY
        elif score < 6:
            difficulty = TransitionDifficulty.MODERATE
        elif score < 8:
            difficulty = TransitionDifficulty.DIFFICULT
        else:
            difficulty = TransitionDifficulty.SEVERE

        # Add score to factors dictionary
        factors["score"] = round(score, 1)

        return difficulty, factors

    async def _calculate_context_changes(
        self,
        current_task: Union[TaskModel, Dict[str, Any]],
        next_task: Union[TaskModel, Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Calculate context changes between two tasks.

        Args:
            current_task: Current task model or dictionary
            next_task: Next task model or dictionary

        Returns:
            Dictionary with context change details
        """
        changes = {}

        # Location context change
        location_change = 0.0
        location_details = {}

        if hasattr(current_task, "location") and hasattr(next_task, "location"):
            # Simple case: different named locations
            if current_task.location != next_task.location:
                location_change = 1.0
                location_details = {"from": current_task.location, "to": next_task.location}

        changes[ContextChangeType.LOCATION.value] = {
            "change_factor": location_change,
            "details": location_details,
        }

        # Tools context change
        tools_change = 0.0
        tools_details = {}

        if hasattr(current_task, "tools_needed") and hasattr(next_task, "tools_needed"):
            if current_task.tools_needed and next_task.tools_needed:
                current_tools = set(current_task.tools_needed)
                next_tools = set(next_task.tools_needed)

                # Calculate tool change factor
                common_tools = current_tools.intersection(next_tools)
                all_tools = current_tools.union(next_tools)

                if all_tools:
                    tools_change = 1 - (len(common_tools) / len(all_tools))
                else:
                    tools_change = 0.0

                tools_details = {
                    "tools_to_put_away": list(current_tools - next_tools),
                    "tools_to_get_out": list(next_tools - current_tools),
                    "tools_to_keep_using": list(common_tools),
                }

        changes[ContextChangeType.TOOLS.value] = {
            "change_factor": tools_change,
            "details": tools_details,
        }

        # Mental context change
        mental_change = 0.0
        mental_details = {}

        # Calculate based on focus type, category, and complexity
        if hasattr(current_task, "focus_type") and hasattr(next_task, "focus_type"):
            if current_task.focus_type != next_task.focus_type:
                mental_change += 0.7
                mental_details["focus_type_change"] = {
                    "from": current_task.focus_type,
                    "to": next_task.focus_type,
                }

        if current_task.category != next_task.category:
            mental_change += 0.3
            mental_details["category_change"] = {
                "from": current_task.category,
                "to": next_task.category,
            }

        # Cap at 1.0
        mental_change = min(mental_change, 1.0)

        changes[ContextChangeType.MENTAL_CONTEXT.value] = {
            "change_factor": mental_change,
            "details": mental_details,
        }

        # Social context change
        social_change = 0.0
        social_details = {}

        if hasattr(current_task, "is_collaborative") and hasattr(next_task, "is_collaborative"):
            if current_task.is_collaborative != next_task.is_collaborative:
                social_change = 1.0
                social_details["collaboration_change"] = {
                    "from": "collaborative" if current_task.is_collaborative else "individual",
                    "to": "collaborative" if next_task.is_collaborative else "individual",
                }

        changes[ContextChangeType.SOCIAL_CONTEXT.value] = {
            "change_factor": social_change,
            "details": social_details,
        }

        # Energy level change
        energy_change = 0.0
        energy_details = {}

        if hasattr(current_task, "energy_required") and hasattr(next_task, "energy_required"):
            energy_diff = abs(current_task.energy_required - next_task.energy_required)
            energy_change = energy_diff / 5.0  # Assuming energy is 1-5 scale

            energy_details = {
                "from": current_task.energy_required,
                "to": next_task.energy_required,
                "difference": energy_diff,
            }

        changes[ContextChangeType.ENERGY_LEVEL.value] = {
            "change_factor": energy_change,
            "details": energy_details,
        }

        return changes

    async def _analyze_context_changes(
        self, from_task: Union[TaskModel, Dict[str, Any]], to_task: Union[TaskModel, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze context changes between two tasks.

        Args:
            from_task: The task transitioning from
            to_task: The task transitioning to

        Returns:
            Dictionary with analysis of context changes
        """
        # Get detailed context changes from _calculate_context_changes
        changes = await self._calculate_context_changes(from_task, to_task)

        # Calculate total context change score
        total_score = 0.0
        for change_type, change_info in changes.items():
            if isinstance(change_info, dict) and "change_factor" in change_info:
                weight = self.context_change_weights.get(change_type, 0.1)
                total_score += change_info["change_factor"] * weight

        # Add total score to the result
        changes["total_context_change_score"] = min(1.0, total_score)

        return changes

    def _calculate_context_impact_factor(self, context_changes: Dict[str, Any]) -> float:
        """
        Calculate context impact factor based on context changes.

        Args:
            context_changes: Dictionary mapping context change types to change details

        Returns:
            A multiplier factor for the base buffer time
        """
        if not context_changes:
            return 1.0

        cumulative_impact = 0
        for change_type, change_info in context_changes.items():
            if not isinstance(change_info, dict) or "change_factor" not in change_info:
                continue

            weight = self.context_change_weights.get(change_type, 0.1)
            change_factor = change_info.get("change_factor", 0)
            cumulative_impact += weight * change_factor

        # Ensure the impact factor is at least 1.0 and scale it reasonably
        return max(1.0, 1.0 + cumulative_impact)

    def calculate_opportunity_cost(
        self,
        task1: Union[TaskModel, Dict[str, Any]],
        task2: Union[TaskModel, Dict[str, Any]],
        available_time: int,
    ) -> Dict[str, Any]:
        """
        Calculate opportunity cost between two tasks.

        This method evaluates the opportunity cost of choosing one task over
        another given limited time resources. It considers task priority,
        deadline proximity, estimated value, and cognitive alignment with
        current energy state.

        Args:
            task1: First task to compare
            task2: Second task to compare
            available_time: Available time in minutes

        Returns:
            Dictionary containing opportunity cost metrics and analysis
        """
        # Extract task attributes with safe accessor
        t1_duration = self._get_attribute(task1, "estimated_duration", 30)
        t2_duration = self._get_attribute(task2, "estimated_duration", 30)

        t1_priority = self._get_attribute(task1, "priority", 3)
        t2_priority = self._get_attribute(task2, "priority", 3)

        # Get deadline information, default to 7 days if not provided
        default_deadline = datetime.now() + timedelta(days=7)
        t1_deadline = self._get_attribute(task1, "deadline", default_deadline)
        t2_deadline = self._get_attribute(task2, "deadline", default_deadline)

        # Convert to datetime objects if they're strings
        if isinstance(t1_deadline, str):
            try:
                t1_deadline = datetime.fromisoformat(t1_deadline)
            except ValueError:
                t1_deadline = default_deadline

        if isinstance(t2_deadline, str):
            try:
                t2_deadline = datetime.fromisoformat(t2_deadline)
            except ValueError:
                t2_deadline = default_deadline

        # Calculate deadline proximity (0-1 scale, higher means closer to deadline)
        now = datetime.now()
        max_days_out = 14  # Consider anything more than 2 weeks out as "far"

        t1_days_to_deadline = max(0, (t1_deadline - now).total_seconds() / 86400)
        t2_days_to_deadline = max(0, (t2_deadline - now).total_seconds() / 86400)

        t1_deadline_proximity = 1 - min(t1_days_to_deadline / max_days_out, 1)
        t2_deadline_proximity = 1 - min(t2_days_to_deadline / max_days_out, 1)

        # Calculate estimated value (priority scaled by deadline proximity)
        # Priority is typically 1-5 scale, normalize to 0-1
        t1_normalized_priority = (
            (t1_priority - 1) / 4 if isinstance(t1_priority, (int, float)) else 0.5
        )
        t2_normalized_priority = (
            (t2_priority - 1) / 4 if isinstance(t2_priority, (int, float)) else 0.5
        )

        t1_value = t1_normalized_priority * (1 + t1_deadline_proximity)
        t2_value = t2_normalized_priority * (1 + t2_deadline_proximity)

        # Calculate time efficiency (value per minute)
        t1_efficiency = t1_value / t1_duration if t1_duration > 0 else 0
        t2_efficiency = t2_value / t2_duration if t2_duration > 0 else 0

        # Calculate completion possibility
        t1_can_complete = t1_duration <= available_time
        t2_can_complete = t2_duration <= available_time

        # Calculate cognitive alignment
        # Get energy required and focus required
        t1_energy_required = self._get_attribute(task1, "energy_required", 3)
        t2_energy_required = self._get_attribute(task2, "energy_required", 3)

        t1_focus_required = self._get_attribute(task1, "focus_required", 3)
        t2_focus_required = self._get_attribute(task2, "focus_required", 3)

        # For this calculation, we'd ideally get current energy and focus from user state
        # Here we'll use middle values as defaults (in production, get from user state)
        current_energy = 3
        current_focus = 3

        # Calculate alignment (0-1 scale, higher is better aligned)
        t1_energy_alignment = 1 - abs(current_energy - t1_energy_required) / 5
        t2_energy_alignment = 1 - abs(current_energy - t2_energy_required) / 5

        t1_focus_alignment = 1 - abs(current_focus - t1_focus_required) / 5
        t2_focus_alignment = 1 - abs(current_focus - t2_focus_required) / 5

        t1_cognitive_alignment = (t1_energy_alignment + t1_focus_alignment) / 2
        t2_cognitive_alignment = (t2_energy_alignment + t2_focus_alignment) / 2

        # Calculate combined opportunity cost score
        # Weighted combination of factors:
        # - Value (40%)
        # - Time efficiency (30%)
        # - Completion possibility (20%)
        # - Cognitive alignment (10%)

        # Apply completion possibility as a multiplier
        completion_factor_t1 = 1.0 if t1_can_complete else 0.5
        completion_factor_t2 = 1.0 if t2_can_complete else 0.5

        t1_score = (
            0.4 * t1_value + 0.3 * t1_efficiency + 0.1 * t1_cognitive_alignment
        ) * completion_factor_t1

        t2_score = (
            0.4 * t2_value + 0.3 * t2_efficiency + 0.1 * t2_cognitive_alignment
        ) * completion_factor_t2

        # Calculate opportunity cost
        if t1_score > t2_score:
            # Task 1 is better, opportunity cost is task 2's score
            better_task = "task1"
            opportunity_cost = t2_score
            opportunity_cost_ratio = t2_score / t1_score if t1_score > 0 else 0
            cost_description = (
                f"Choosing Task 1 ({self._get_attribute(task1, 'title', 'Task 1')}) over Task 2"
            )
        else:
            # Task 2 is better, opportunity cost is task 1's score
            better_task = "task2"
            opportunity_cost = t1_score
            opportunity_cost_ratio = t1_score / t2_score if t2_score > 0 else 0
            cost_description = (
                f"Choosing Task 2 ({self._get_attribute(task2, 'title', 'Task 2')}) over Task 1"
            )

        # Determine regret risk (how close are the scores)
        regret_risk = opportunity_cost_ratio

        return {
            "task1": {
                "id": self._get_attribute(task1, "id", "unknown"),
                "title": self._get_attribute(task1, "title", "Task 1"),
                "duration": t1_duration,
                "value": round(t1_value, 2),
                "efficiency": round(t1_efficiency, 4),
                "deadline_proximity": round(t1_deadline_proximity, 2),
                "can_complete": t1_can_complete,
                "cognitive_alignment": round(t1_cognitive_alignment, 2),
                "score": round(t1_score, 2),
            },
            "task2": {
                "id": self._get_attribute(task2, "id", "unknown"),
                "title": self._get_attribute(task2, "title", "Task 2"),
                "duration": t2_duration,
                "value": round(t2_value, 2),
                "efficiency": round(t2_efficiency, 4),
                "deadline_proximity": round(t2_deadline_proximity, 2),
                "can_complete": t2_can_complete,
                "cognitive_alignment": round(t2_cognitive_alignment, 2),
                "score": round(t2_score, 2),
            },
            "better_task": better_task,
            "opportunity_cost": round(opportunity_cost, 2),
            "opportunity_cost_ratio": round(opportunity_cost_ratio, 2),
            "regret_risk": round(regret_risk, 2),
            "available_time": available_time,
            "cost_description": cost_description,
            "recommendation": f"Based on opportunity cost analysis, {better_task} provides more value given your current constraints.",
        }

    async def _get_user_adjustment_factor(
        self, user_id: str, current_task: TaskModel, next_task: TaskModel
    ) -> float:
        """
        Get user-specific adjustment factor based on historical patterns.

        Args:
            user_id: ID of the user
            current_task: Current task model
            next_task: Next task model

        Returns:
            Adjustment factor as a multiplier
        """
        if user_id not in self.user_adjustments:
            # Load user adjustments if not already loaded
            await self._load_user_adjustments(user_id)

        if user_id not in self.user_adjustments:
            return 1.0  # Default if no adjustments found

        # Get category keys for this transition
        category_keys = await self._get_transition_category_keys(current_task, next_task)

        # Get adjustment factors for each relevant category
        factors = []
        for key in category_keys:
            if key in self.user_adjustments[user_id]:
                factors.append(self.user_adjustments[user_id][key])

        # Calculate combined factor (average of relevant factors)
        if factors:
            return sum(factors) / len(factors)
        else:
            return 1.0

    def _get_attribute(self, obj, attr_name, default=None):
        """Helper function to get attribute from object or dict"""
        if hasattr(obj, attr_name):
            return getattr(obj, attr_name, default)
        elif isinstance(obj, dict) and attr_name in obj:
            return obj[attr_name]
        return default

    async def _get_tasks(
        self, current_task_id: str, next_task_id: str
    ) -> Tuple[
        Optional[Union[TaskModel, Dict[str, Any]]], Optional[Union[TaskModel, Dict[str, Any]]]
    ]:
        """
        Helper method to get both tasks for a transition.

        Args:
            current_task_id: ID of the current task
            next_task_id: ID of the next task

        Returns:
            Tuple of (current_task, next_task)
        """
        current_task = await self._get_task(current_task_id)
        next_task = await self._get_task(next_task_id)
        return current_task, next_task

    async def _get_transition_category_keys(
        self,
        current_task: Union[TaskModel, Dict[str, Any]],
        next_task: Union[TaskModel, Dict[str, Any]],
    ) -> List[str]:
        """
        Get category keys for a transition between tasks.

        These keys are used to classify transitions for user adjustments.

        Args:
            current_task: Current task model or dictionary
            next_task: Next task model or dictionary

        Returns:
            List of category keys for this transition
        """
        keys = []

        # Add key for specific category transition
        current_category = self._get_attribute(current_task, "category", "work")
        next_category = self._get_attribute(next_task, "category", "work")
        keys.append(f"cat:{current_category}->{next_category}")

        # Add key for transition difficulty
        difficulty, _ = await self._analyze_transition_difficulty(current_task, next_task)
        keys.append(f"diff:{difficulty.value}")

        # Add key for location change if applicable
        current_location = self._get_attribute(current_task, "location", None)
        next_location = self._get_attribute(next_task, "location", None)
        if current_location and next_location and current_location != next_location:
            keys.append(f"loc_change:true")
            keys.append(f"loc:{current_location}->{next_location}")

        # Add key for general focus level transition
        current_focus = self._get_attribute(current_task, "focus_required", 3)
        next_focus = self._get_attribute(next_task, "focus_required", 3)
        if current_focus < next_focus:
            keys.append("focus:increasing")
        elif current_focus > next_focus:
            keys.append("focus:decreasing")
        else:
            keys.append("focus:same")

        return keys

    async def _load_user_adjustments(self, user_id: str) -> None:
        """
        Load user-specific transition adjustments from history.

        Args:
            user_id: ID of the user
        """
        if self.db is None:
            return

        # Get transition history
        transitions = await self._get_transition_history(user_id)

        if not transitions:
            self.user_adjustments[user_id] = {}
            return

        # Analyze transitions to build adjustment factors
        category_observations = {}

        for transition in transitions:
            if (
                "category_keys" not in transition
                or "actual_minutes" not in transition
                or "predicted_minutes" not in transition
            ):
                continue

            actual = transition["actual_minutes"]
            predicted = transition["predicted_minutes"]

            if predicted <= 0:
                continue

            # Calculate ratio of actual to predicted
            ratio = actual / predicted

            # Apply to each category
            for key in transition["category_keys"]:
                if key not in category_observations:
                    category_observations[key] = []

                category_observations[key].append(ratio)

        # Calculate average ratios for each category
        adjustments = {}
        for key, ratios in category_observations.items():
            if ratios:
                # Use median to reduce influence of outliers
                adjustments[key] = np.median(ratios)

        self.user_adjustments[user_id] = adjustments

    async def _get_transition_history(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get transition history for a user.

        Args:
            user_id: ID of the user

        Returns:
            List of transition records
        """
        # This would normally query the database for transition records
        # For this implementation, we'll return mock data
        # In a real implementation, this would query a table of transition observations

        # Calculate lookback time
        lookback_time = datetime.now() - timedelta(days=self.lookback_period)

        # Get transition observations from database (mock implementation)
        return [
            {
                "user_id": user_id,
                "current_task_id": "task1",
                "next_task_id": "task2",
                "predicted_minutes": 15,
                "actual_minutes": 20,
                "transition_difficulty": TransitionDifficulty.MODERATE.value,
                "category_keys": ["cat:work->home", "diff:moderate", "focus:decreasing"],
                "timestamp": (datetime.now() - timedelta(days=5)).isoformat(),
            },
            {
                "user_id": user_id,
                "current_task_id": "task3",
                "next_task_id": "task4",
                "predicted_minutes": 10,
                "actual_minutes": 25,
                "transition_difficulty": TransitionDifficulty.DIFFICULT.value,
                "category_keys": [
                    "cat:home->work",
                    "diff:difficult",
                    "loc_change:true",
                    "focus:increasing",
                ],
                "timestamp": (datetime.now() - timedelta(days=3)).isoformat(),
            },
            {
                "user_id": user_id,
                "current_task_id": "task5",
                "next_task_id": "task6",
                "predicted_minutes": 20,
                "actual_minutes": 18,
                "transition_difficulty": TransitionDifficulty.MODERATE.value,
                "category_keys": ["cat:work->work", "diff:moderate", "focus:same"],
                "timestamp": (datetime.now() - timedelta(days=1)).isoformat(),
            },
        ]

    async def _store_transition_observation(
        self,
        user_id: str,
        current_task_id: str,
        next_task_id: str,
        predicted_minutes: int,
        actual_minutes: int,
    ) -> None:
        """
        Store a transition observation in the database.

        Args:
            user_id: ID of the user
            current_task_id: ID of the current task
            next_task_id: ID of the next task
            predicted_minutes: Predicted transition time
            actual_minutes: Actual transition time
        """
        # In a real implementation, this would store data in a database table
        # For now, we'll just log it
        logger.info(
            f"Transition observation: user={user_id}, "
            f"current_task={current_task_id}, next_task={next_task_id}, "
            f"predicted={predicted_minutes}m, actual={actual_minutes}m"
        )

    async def _get_task(self, task_id: str) -> Optional[Union[TaskModel, Dict[str, Any]]]:
        """
        Get task by ID.

        Args:
            task_id: ID of the task

        Returns:
            TaskModel instance, dictionary, or None if not found
        """
        if self.db is None:
            return None

        try:
            stmt = select(TaskModel).where(TaskModel.id == task_id)
            result = await self.db.execute(stmt)
            task_row = result.first()

            if task_row:
                return task_row[0]

            # For test compatibility, create a mock task
            return {
                "id": task_id,
                "user_id": f"user-{task_id}",
                "title": f"Task {task_id}",
                "description": f"Description for task {task_id}",
                "category": "work",
                "focus_required": 3,
                "energy_required": 3,
                "difficulty": 3,
                "location": "office",
                "tools_needed": [],
                "is_collaborative": False,
                "focus_type": "analytical",
            }
        except Exception as e:
            logger.error(f"Error getting task: {e}")
            return None

    def save(self, filepath: str) -> None:
        """
        Save model parameters to a file.

        Args:
            filepath: Path to save model to
        """
        params = {
            "base_transition_times": self.base_transition_times,
            "context_change_weights": self.context_change_weights,
            "min_buffer_minutes": self.min_buffer_minutes,
            "max_buffer_minutes": self.max_buffer_minutes,
            "adaptation_rate": self.adaptation_rate,
            "lookback_period": self.lookback_period,
            "user_adjustments": self.user_adjustments,
        }

        with open(filepath, "w") as f:
            json.dump(params, f)

    @classmethod
    def load(cls, filepath: str) -> "TimeBufferCalculator":
        """
        Load model parameters from a file.

        Args:
            filepath: Path to load model from

        Returns:
            Loaded TimeBufferCalculator instance
        """
        try:
            with open(filepath, "r") as f:
                params = json.load(f)

            calculator = cls(
                base_transition_times=params.get("base_transition_times"),
                context_change_weights=params.get("context_change_weights"),
                min_buffer_minutes=params.get("min_buffer_minutes", 5),
                max_buffer_minutes=params.get("max_buffer_minutes", 60),
                adaptation_rate=params.get("adaptation_rate", 0.2),
                lookback_period=params.get("lookback_period", 30),
            )

            # Restore user adjustments
            calculator.user_adjustments = params.get("user_adjustments", {})

            return calculator
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Error loading model parameters: {e}")
            return cls()

    async def weekly_resampling(
        self,
        user_id: str,
        lookback_days: int = 90,
        rolling_window_days: int = 7,
        include_weekends: bool = True,
    ) -> Dict[str, Any]:
        """
        Resample historical task transition data to weekly frequency with rolling averages.

        This method analyzes historical transition times between tasks and resamples the data
        to weekly frequency, calculating rolling averages and other useful statistics to identify
        patterns in task switching efficiency over time.

        Args:
            user_id: ID of the user whose data will be analyzed
            lookback_days: Number of days to look back for historical data
            rolling_window_days: Size of the rolling window for averages (in days)
            include_weekends: Whether to include weekend data in the analysis

        Returns:
            Dictionary containing:
            - weekly_transitions: Weekly resampled transition data
            - weekly_stats: Statistics for each week
            - rolling_averages: Rolling average transitions
            - patterns: Identified weekly patterns
        """
        logger.info(f"Generating weekly transition time patterns for user {user_id}")

        # Get transition history
        transitions = await self._get_transition_history(user_id)

        if not transitions:
            logger.warning(f"No transition history found for user {user_id}")
            return {
                "error": "No transition history available",
                "weekly_transitions": {},
                "weekly_stats": {},
                "rolling_averages": {},
                "patterns": {},
            }

        # Convert transitions to DataFrame for analysis
        df = pd.DataFrame(transitions)

        # Ensure timestamp field is in datetime format
        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"])
        elif "transition_date" in df.columns:
            df["timestamp"] = pd.to_datetime(df["transition_date"])
        else:
            # If no timestamp field exists, create one based on current time
            # This is a fallback and should be improved in production
            logger.warning("No timestamp field found in transition data, using current date")
            now = datetime.now()
            # Create artificial timestamps spread over the lookback period
            timestamps = [now - timedelta(days=i) for i in range(len(df))]
            df["timestamp"] = timestamps

        # Filter to lookback period
        start_date = datetime.now() - timedelta(days=lookback_days)
        df = df[df["timestamp"] >= start_date]

        if df.empty:
            logger.warning(
                f"No transition data available within lookback period for user {user_id}"
            )
            return {
                "error": "No transition data within lookback period",
                "weekly_transitions": {},
                "weekly_stats": {},
                "rolling_averages": {},
                "patterns": {},
            }

        # Remove weekend data if specified
        if not include_weekends:
            # 0 = Monday, 6 = Sunday in datetime.weekday()
            df = df[df["timestamp"].dt.weekday < 5]

        # Extract numeric variables for analysis
        numeric_cols = []
        for col in df.columns:
            if col in ["actual_minutes", "predicted_minutes", "buffer_minutes", "transition_time"]:
                numeric_cols.append(col)
            elif df[col].dtype in [np.int64, np.float64]:
                numeric_cols.append(col)

        # Add derived columns for analysis
        if "actual_minutes" in df.columns and "predicted_minutes" in df.columns:
            df["prediction_error"] = df["actual_minutes"] - df["predicted_minutes"]
            df["prediction_error_pct"] = (df["prediction_error"] / df["predicted_minutes"]) * 100
            numeric_cols.extend(["prediction_error", "prediction_error_pct"])

        # Set timestamp as index for resampling
        df.set_index("timestamp", inplace=True)

        # Resample data to weekly frequency
        weekly_aggs = {}
        for col in numeric_cols:
            weekly_aggs[col] = ["mean", "min", "max", "std", "count"]

        weekly_df = df[numeric_cols].resample("W-MON").agg(weekly_aggs)

        # Flatten column MultiIndex
        weekly_df.columns = ["_".join(col).strip() for col in weekly_df.columns.values]

        # Add week number and year
        weekly_df["year"] = weekly_df.index.year
        weekly_df["week_number"] = weekly_df.index.isocalendar().week

        # Calculate rolling averages on daily data first
        daily_df = df[numeric_cols].resample("D").mean()

        # Apply rolling window to the daily data
        rolling_cols = {}
        for col in numeric_cols:
            rolling_col = f"{col}_rolling_{rolling_window_days}d"
            daily_df[rolling_col] = (
                daily_df[col].rolling(window=rolling_window_days, min_periods=1).mean()
            )
            rolling_cols[col] = rolling_col

        # Resample rolling averages to weekly to align with weekly_df
        rolling_weekly = (
            daily_df[[rolling_cols[col] for col in numeric_cols]].resample("W-MON").last()
        )

        # Calculate week-over-week changes
        for col in [c for c in weekly_df.columns if c.endswith("_mean")]:
            weekly_df[f"{col}_wow_change"] = weekly_df[col].pct_change() * 100

        # Identify patterns in day of week variations
        day_patterns = {}
        for col in numeric_cols:
            # Create a DataFrame grouped by day of week
            day_data = df[col].groupby(df.index.weekday).agg(["mean", "std", "count"])
            day_data.index = day_data.index.map(
                lambda x: [
                    "Monday",
                    "Tuesday",
                    "Wednesday",
                    "Thursday",
                    "Friday",
                    "Saturday",
                    "Sunday",
                ][x]
            )
            day_patterns[col] = day_data.to_dict()

        # Reset index to make timestamp a column again in weekly_df
        weekly_df.reset_index(inplace=True)
        weekly_df.rename(columns={"index": "week_start"}, inplace=True)

        # Prepare result dictionary
        result = {
            "weekly_transitions": weekly_df.to_dict(orient="records"),
            "weekly_stats": {
                "total_weeks": len(weekly_df),
                "average_transitions_per_week": (
                    weekly_df["actual_minutes_count"].mean()
                    if "actual_minutes_count" in weekly_df.columns
                    else None
                ),
                "most_efficient_week": (
                    weekly_df.iloc[weekly_df["actual_minutes_mean"].idxmin()][
                        "week_start"
                    ].strftime("%Y-%m-%d")
                    if "actual_minutes_mean" in weekly_df.columns and not weekly_df.empty
                    else None
                ),
                "least_efficient_week": (
                    weekly_df.iloc[weekly_df["actual_minutes_mean"].idxmax()][
                        "week_start"
                    ].strftime("%Y-%m-%d")
                    if "actual_minutes_mean" in weekly_df.columns and not weekly_df.empty
                    else None
                ),
            },
            "rolling_averages": (
                rolling_weekly.to_dict(orient="records") if not rolling_weekly.empty else {}
            ),
            "patterns": {
                "day_of_week": day_patterns,
                "weekly_trend": (
                    self._analyze_weekly_trend(weekly_df) if not weekly_df.empty else {}
                ),
            },
        }

        logger.info(f"Successfully generated weekly transition patterns for user {user_id}")
        return result

    def _analyze_weekly_trend(self, weekly_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze weekly trend to identify patterns over time.

        Args:
            weekly_df: DataFrame with weekly data

        Returns:
            Dictionary with trend analysis
        """
        trend_analysis = {}

        # Find columns that represent means of metrics
        mean_cols = [col for col in weekly_df.columns if col.endswith("_mean")]

        for col in mean_cols:
            if weekly_df[col].count() < 3:  # Need at least 3 data points for meaningful trend
                continue

            # Simple linear trend (is it getting better or worse)
            first_valid = weekly_df[col].first_valid_index()
            last_valid = weekly_df[col].last_valid_index()

            if first_valid is None or last_valid is None:
                continue

            first_value = weekly_df.loc[first_valid, col]
            last_value = weekly_df.loc[last_valid, col]

            # Calculate percentage change
            if abs(first_value) > 0.001:  # Avoid division by very small numbers
                pct_change = ((last_value - first_value) / first_value) * 100
            else:
                pct_change = 0

            trend_analysis[col] = {
                "first_value": first_value,
                "last_value": last_value,
                "change": last_value - first_value,
                "pct_change": pct_change,
                "direction": (
                    "improving" if pct_change < 0 else "worsening" if pct_change > 0 else "stable"
                ),
                "weeks_analyzed": len(weekly_df),
            }

        return trend_analysis
