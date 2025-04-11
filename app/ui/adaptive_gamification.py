"""
Adaptive Gamification Engine for Motivation Enhancement (ADHD-28)

This module provides a neurodiverse-focused gamification engine that adapts
to individual user preferences, motivation patterns, and ADHD traits.
"""

import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Tuple, Union, Any

import numpy as np
from pydantic import BaseModel, Field

from app.models.user_model import UserModel
from app.services.gamification_service import GamificationService
from app.services.user_insights_service import UserInsightsService

logger = logging.getLogger(__name__)


class UserMotivationModel:
    """
    Model for predicting user motivation patterns and optimal gamification strategies.

    This model analyzes user behavior and preferences to determine the most effective
    motivation techniques for each individual user, with special consideration for
    ADHD traits and patterns.
    """

    def __init__(self, user_id: str):
        """
        Initialize the user motivation model for a specific user.

        Args:
            user_id: The ID of the user this model is for
        """
        self.user_id = user_id
        self.motivation_weights = {}
        self.reward_weights = {}
        self.mechanic_weights = {}
        self.novelty_decay_rates = {}

    def predict(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict optimal motivation strategies based on user context.

        Args:
            context: Dictionary containing contextual information about the user's
                    current state, task, and environment

        Returns:
            Dictionary with predicted optimal motivation strategies
        """
        # This would normally contain complex prediction logic
        # For now, return a simple placeholder response
        return {
            "optimal_mechanics": ["progress_bar", "challenge", "feedback"],
            "optimal_rewards": ["points", "badges"],
            "motivation_factors": {
                "achievement": 0.8,
                "novelty": 0.6,
                "autonomy": 0.7
            }
        }

    def update(self, behavior_data: Dict[str, Any]) -> None:
        """
        Update the model based on new user behavior data.

        Args:
            behavior_data: Dictionary containing information about user's
                          responses to different motivation techniques
        """
        # This would normally update the model weights based on behavior data
        logging.info(f"Updating motivation model for user {self.user_id}")

    def get_burnout_risk(self) -> float:
        """
        Calculate the risk of motivation burnout for the user.

        Returns:
            Float between 0 and 1 representing burnout risk
        """
        # Placeholder implementation
        return 0.3


class MotivationType(str, Enum):
    """Types of motivation that may work for different users."""
    ACHIEVEMENT = "achievement"
    SOCIAL = "social"
    IMMERSION = "immersion"
    COMPLETION = "completion"
    NOVELTY = "novelty"
    CURIOSITY = "curiosity"
    MASTERY = "mastery"
    AUTONOMY = "autonomy"


class RewardType(str, Enum):
    """Types of rewards that can be offered to users."""
    POINTS = "points"
    BADGES = "badges"
    LEVELS = "levels"
    VIRTUAL_CURRENCY = "virtual_currency"
    STREAK = "streak"
    ACHIEVEMENT = "achievement"
    VISUAL_THEME = "visual_theme"
    SOUND_EFFECT = "sound_effect"
    ANIMATION = "animation"
    UNLOCKABLE_FEATURE = "unlockable_feature"


class GameMechanic(str, Enum):
    """Game mechanics that can be applied for different users."""
    PROGRESS_BAR = "progress_bar"
    LEADERBOARD = "leaderboard"
    CHALLENGE = "challenge"
    QUEST = "quest"
    COLLECTION = "collection"
    CUSTOMIZATION = "customization"
    FEEDBACK = "feedback"
    SURPRISE = "surprise"
    NARRATIVE = "narrative"
    TIMER = "timer"
    COUNTDOWN = "countdown"
    SOCIAL_INTERACTION = "social_interaction"


class UserMotivationProfile(BaseModel):
    """User's motivation profile with preferences and effectiveness scores."""
    user_id: str
    motivation_types: Dict[MotivationType, float] = Field(
        default_factory=lambda: {t: 0.5 for t in MotivationType}
    )
    reward_preferences: Dict[RewardType, float] = Field(
        default_factory=lambda: {t: 0.5 for t in RewardType}
    )
    mechanic_effectiveness: Dict[GameMechanic, float] = Field(
        default_factory=lambda: {m: 0.5 for m in GameMechanic}
    )
    burnout_risk: float = 0.0
    novelty_decay_rates: Dict[str, float] = Field(default_factory=dict)
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class GamificationAction(BaseModel):
    """A specific gamification action to take for user motivation."""
    user_id: str
    mechanic: GameMechanic
    reward_type: Optional[RewardType] = None
    context: Dict[str, Any] = Field(default_factory=dict)
    strength: float = 1.0  # How strongly to apply the mechanic
    message: Optional[str] = None
    visual_element: Optional[Dict[str, Any]] = None


class AdaptiveGamificationEngine:
    """
    Engine for adapting gamification elements based on user's ADHD profile,
    motivation patterns, and current context.
    """

    def __init__(
        self,
        gamification_service: GamificationService,
        user_insights_service: UserInsightsService,
        model_refresh_interval: timedelta = timedelta(days=1),
    ):
        self.gamification_service = gamification_service
        self.user_insights_service = user_insights_service
        self.model_refresh_interval = model_refresh_interval
        self.user_models: Dict[str, Tuple[UserMotivationModel, datetime]] = {}
        self._load_default_templates()

    def _load_default_templates(self):
        """Load default message and visual templates for gamification elements."""
        self.message_templates = {
            GameMechanic.PROGRESS_BAR: [
                "You're making great progress! {progress}% complete!",
                "Keep it up! Only {remaining}% to go!",
                "You've come so far already - {progress}% done!"
            ],
            GameMechanic.CHALLENGE: [
                "New challenge unlocked: {challenge_name}",
                "Ready for a challenge? Try {challenge_name}!",
                "Challenge yourself with: {challenge_name}"
            ],
            # Add more templates for other mechanics
        }

        self.visual_templates = {
            # Templates for visual elements
            RewardType.BADGES: {
                "adhd_friendly": True,
                "high_contrast": True,
                "animation_duration": 2.0,
                "celebration_level": "medium",
            }
        }

    async def get_user_profile(self, user_id: str) -> UserMotivationProfile:
        """Get or create a motivation profile for a user."""
        profile = await self.gamification_service.get_motivation_profile(user_id)
        if not profile:
            profile = UserMotivationProfile(user_id=user_id)
            await self.gamification_service.save_motivation_profile(profile)
        return profile

    async def update_profile_from_behavior(
        self, user_id: str, behaviors: Dict[str, Any]
    ) -> UserMotivationProfile:
        """Update the motivation profile based on observed user behaviors."""
        profile = await self.get_user_profile(user_id)

        # Get or load the user motivation model
        model = await self._get_user_model(user_id)

        # Use the model to update the profile based on behaviors
        updated_values = model.predict(behaviors)

        # Update the profile with new values
        for motivation_type, score in updated_values.get('motivation_types', {}).items():
            if motivation_type in profile.motivation_types:
                # Apply exponential moving average to smooth changes
                alpha = 0.3  # Learning rate
                profile.motivation_types[motivation_type] = (
                    (1 - alpha) * profile.motivation_types[motivation_type] + alpha * score
                )

        # Update other profile aspects similarly
        for reward_type, score in updated_values.get('reward_preferences', {}).items():
            if reward_type in profile.reward_preferences:
                alpha = 0.3
                profile.reward_preferences[reward_type] = (
                    (1 - alpha) * profile.reward_preferences[reward_type] + alpha * score
                )

        for mechanic, score in updated_values.get('mechanic_effectiveness', {}).items():
            if mechanic in profile.mechanic_effectiveness:
                alpha = 0.3
                profile.mechanic_effectiveness[mechanic] = (
                    (1 - alpha) * profile.mechanic_effectiveness[mechanic] + alpha * score
                )

        # Update burnout risk if provided
        if 'burnout_risk' in updated_values:
            profile.burnout_risk = (
                0.7 * profile.burnout_risk + 0.3 * updated_values['burnout_risk']
            )

        # Update novelty decay rates
        for element, rate in updated_values.get('novelty_decay_rates', {}).items():
            profile.novelty_decay_rates[element] = rate

        profile.last_updated = datetime.utcnow()
        await self.gamification_service.save_motivation_profile(profile)

        return profile

    async def _get_user_model(self, user_id: str) -> UserMotivationModel:
        """Get or create a motivation model for the user."""
        now = datetime.utcnow()

        # Check if we have a recent model
        if user_id in self.user_models:
            model, timestamp = self.user_models[user_id]
            if now - timestamp < self.model_refresh_interval:
                return model

        # Load or create a new model
        user_data = await self.user_insights_service.get_user_motivation_data(user_id)
        model = UserMotivationModel(user_id=user_id)
        model.update(user_data)

        # Cache the model
        self.user_models[user_id] = (model, now)
        return model

    async def get_optimal_mechanics(
        self, user_id: str, context: Dict[str, Any], limit: int = 3
    ) -> List[GameMechanic]:
        """
        Get the most effective game mechanics for the user based on their profile
        and current context.
        """
        profile = await self.get_user_profile(user_id)

        # Factor in context-specific effectiveness
        adjusted_effectiveness = dict(profile.mechanic_effectiveness)

        # Adjust based on task type
        task_type = context.get("task_type")
        if task_type == "boring":
            # For boring tasks, boost engaging mechanics
            adjusted_effectiveness[GameMechanic.NARRATIVE] *= 3.0  # Increase the boost factor
            if GameMechanic.SURPRISE in adjusted_effectiveness:
                adjusted_effectiveness[GameMechanic.SURPRISE] *= 1.5
        elif task_type == "difficult":
            # For difficult tasks, boost achievement and progress mechanics
            adjusted_effectiveness[GameMechanic.PROGRESS_BAR] *= 1.5
            adjusted_effectiveness[GameMechanic.CHALLENGE] *= 1.2

        # Adjust based on time of day (circadian factors)
        hour = context.get("current_hour")
        if hour is not None and 14 <= hour <= 16:  # Afternoon slump
            adjusted_effectiveness[GameMechanic.TIMER] *= 2.5  # Increase the boost factor
            if GameMechanic.SOCIAL_INTERACTION in adjusted_effectiveness:
                adjusted_effectiveness[GameMechanic.SOCIAL_INTERACTION] *= 1.2

        # Adjust for burnout risk
        if profile.burnout_risk > 0.7:
            # Reduce intensity for high burnout risk
            for mechanic in adjusted_effectiveness:
                if mechanic in [GameMechanic.CHALLENGE, GameMechanic.LEADERBOARD]:
                    adjusted_effectiveness[mechanic] *= 0.7

        # Apply novelty decay
        for mechanic_str, mechanic in [(m.value, m) for m in GameMechanic]:
            if mechanic_str in profile.novelty_decay_rates:
                days_since_update = (datetime.utcnow() - profile.last_updated).days
                novelty_factor = np.exp(-profile.novelty_decay_rates[mechanic_str] * days_since_update)
                adjusted_effectiveness[mechanic] *= (0.5 + 0.5 * novelty_factor)

        # Sort by effectiveness and return top mechanics
        sorted_mechanics = sorted(
            adjusted_effectiveness.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return [mechanic for mechanic, _ in sorted_mechanics[:limit]]

    async def get_gamification_actions(
        self, user_id: str, context: Dict[str, Any], count: int = 1
    ) -> List[GamificationAction]:
        """
        Generate gamification actions tailored to the user's profile and current context.
        """
        optimal_mechanics = await self.get_optimal_mechanics(user_id, context, limit=count*2)
        profile = await self.get_user_profile(user_id)
        actions = []

        for mechanic in optimal_mechanics[:count]:
            # Select the most effective reward type for this mechanic
            reward_type = max(
                profile.reward_preferences.items(),
                key=lambda x: x[1]
            )[0]

            # Create a message based on the context and mechanic
            message = self._generate_message(mechanic, context)

            # Create visual element configuration
            visual_element = self._generate_visual_element(mechanic, reward_type, context)

            # Calculate strength based on user's current state
            strength = self._calculate_action_strength(profile, mechanic, context)

            actions.append(GamificationAction(
                user_id=user_id,
                mechanic=mechanic,
                reward_type=reward_type,
                context=context,
                strength=strength,
                message=message,
                visual_element=visual_element
            ))

        return actions

    def _generate_message(
        self, mechanic: GameMechanic, context: Dict[str, Any]
    ) -> str:
        """Generate a contextually appropriate message for the gamification mechanic."""
        if mechanic not in self.message_templates:
            return f"You're making progress with {mechanic.value}!"

        templates = self.message_templates[mechanic]
        template = np.random.choice(templates)

        # Replace placeholders with context values
        message = template

        # Handle progress specially
        if "{progress}" in message:
            if "progress" in context:
                # Direct progress value
                message = message.replace("{progress}", str(context["progress"]))
            elif "completed" in context and "total" in context:
                # Calculate progress from completed/total
                progress = int(100 * context["completed"] / max(1, context["total"]))
                message = message.replace("{progress}", str(progress))

        if "{remaining}" in message:
            if "remaining" in context:
                # Direct remaining value
                message = message.replace("{remaining}", str(context["remaining"]))
            elif "completed" in context and "total" in context:
                # Calculate remaining from completed/total
                remaining = int(100 * (context["total"] - context["completed"]) / max(1, context["total"]))
                message = message.replace("{remaining}", str(remaining))

        # Replace other placeholders with context values
        for key, value in context.items():
            placeholder = f"{{{key}}}"
            if placeholder in message:
                message = message.replace(placeholder, str(value))

        return message

    def _generate_visual_element(
        self, mechanic: GameMechanic, reward_type: RewardType, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate visual element configuration based on the mechanic and context."""
        visual_config = {
            "type": mechanic.value,
            "adhd_friendly": True,
            "animation_duration": 1.5,  # Default animation duration in seconds
            "color_scheme": "high_contrast",
        }

        # Add reward-type specific configuration
        if reward_type in self.visual_templates:
            visual_config.update(self.visual_templates[reward_type])

        # Add mechanic-specific configuration
        if mechanic == GameMechanic.PROGRESS_BAR:
            visual_config.update({
                "progress_percent": context.get("progress", 0),
                "segmented": True,  # Segmented progress is better for ADHD users
                "show_milestones": True,
            })
        elif mechanic == GameMechanic.CHALLENGE:
            visual_config.update({
                "challenge_name": context.get("challenge_name", "Daily Challenge"),
                "difficulty": context.get("difficulty", "medium"),
                "time_limited": context.get("time_limited", False),
            })
        elif mechanic == GameMechanic.TIMER:
            visual_config.update({
                "duration": context.get("duration", 25 * 60),  # Default 25 minutes
                "visual_countdown": True,
                "audio_cues": context.get("audio_cues", True),
            })

        return visual_config

    def _calculate_action_strength(
        self, profile: UserMotivationProfile, mechanic: GameMechanic, context: Dict[str, Any]
    ) -> float:
        """Calculate how strongly to apply a gamification mechanic based on user state."""
        # Base strength from profile effectiveness
        base_strength = profile.mechanic_effectiveness.get(mechanic, 0.5)

        # If context is empty, return the base strength directly
        if not context:
            return base_strength

        # Adjust for burnout - reduce strength when burnout risk is high
        burnout_factor = 1.0 - (profile.burnout_risk * 0.5)

        # Adjust for task importance - strengthen for important tasks
        importance_factor = 1.0 + (context.get("importance", 0.5) * 0.5)

        # Adjust for task difficulty - strengthen for difficult tasks that need motivation
        difficulty_factor = 1.0 + (context.get("difficulty", 0.5) * 0.3)

        # Adjust for user's current energy level - strengthen for low energy
        energy_factor = 1.0 + ((1.0 - context.get("energy_level", 0.5)) * 0.4)

        return min(1.0, base_strength * burnout_factor * importance_factor *
                  difficulty_factor * energy_factor)

    async def apply_gamification_action(
        self, action: GamificationAction
    ) -> Dict[str, Any]:
        """Apply a gamification action and track its effectiveness."""
        # Log the action for effectiveness tracking
        await self.gamification_service.log_gamification_action(
            user_id=action.user_id,
            mechanic=action.mechanic.value,
            reward_type=action.reward_type.value if action.reward_type else None,
            context=action.context,
            strength=action.strength,
        )

        # Return the action details for the UI to render
        return {
            "user_id": action.user_id,
            "mechanic": action.mechanic.value,
            "reward_type": action.reward_type.value if action.reward_type else None,
            "message": action.message,
            "visual_element": action.visual_element,
            "strength": action.strength,
        }

    async def track_gamification_effectiveness(
        self, user_id: str, action_id: str, engagement_metrics: Dict[str, Any]
    ) -> None:
        """
        Track how effective a gamification action was based on user engagement metrics.
        This feedback improves future recommendations.
        """
        # Get the original action
        action = await self.gamification_service.get_gamification_action(action_id)
        if not action:
            logger.warning(f"Action {action_id} not found for effectiveness tracking")
            return

        # Calculate effectiveness score from engagement metrics
        completion_rate = engagement_metrics.get("completion_rate", 0.0)
        time_engaged = engagement_metrics.get("time_engaged_seconds", 0)
        reaction_score = engagement_metrics.get("reaction_score", 0.0)

        # Weight the factors based on their importance
        effectiveness = (
            0.4 * completion_rate +
            0.3 * min(1.0, time_engaged / 300) +  # Normalize to 0-1 (5 minutes max)
            0.3 * reaction_score
        )

        # Record the effectiveness
        await self.gamification_service.record_action_effectiveness(
            action_id=action_id,
            effectiveness=effectiveness,
            engagement_metrics=engagement_metrics
        )

        # Update the user's motivation profile based on this feedback
        behaviors = {
            "action_mechanic": action["mechanic"],
            "action_reward_type": action["reward_type"],
            "effectiveness": effectiveness,
            "context": action["context"],
            "engagement_metrics": engagement_metrics,
        }
        await self.update_profile_from_behavior(user_id, behaviors)
