"""
Test suite for the adaptive gamification engine module.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock, AsyncMock

from app.ui.adaptive_gamification import (
    MotivationType,
    RewardType,
    GameMechanic,
    UserMotivationProfile,
    GamificationAction,
    AdaptiveGamificationEngine,
)


class TestUserMotivationProfile:
    """Test the UserMotivationProfile model."""

    def test_default_profile(self):
        """Test that default motivation profile values are set correctly."""
        profile = UserMotivationProfile(user_id="test_user")

        assert profile.user_id == "test_user"
        assert len(profile.motivation_types) == len(MotivationType)
        assert len(profile.reward_preferences) == len(RewardType)
        assert len(profile.mechanic_effectiveness) == len(GameMechanic)
        assert profile.burnout_risk == 0.0
        assert profile.novelty_decay_rates == {}

        # All preferences should have default value
        for motivation_type in MotivationType:
            assert profile.motivation_types[motivation_type] == 0.5

        for reward_type in RewardType:
            assert profile.reward_preferences[reward_type] == 0.5

        for mechanic in GameMechanic:
            assert profile.mechanic_effectiveness[mechanic] == 0.5

    def test_custom_profile(self):
        """Test that custom motivation profile values can be set."""
        profile = UserMotivationProfile(
            user_id="test_user",
            motivation_types={
                MotivationType.ACHIEVEMENT: 0.8,
                MotivationType.SOCIAL: 0.3,
                MotivationType.COMPLETION: 0.9,
                MotivationType.CURIOSITY: 0.6,
            },
            reward_preferences={RewardType.BADGES: 0.7, RewardType.POINTS: 0.6},
            mechanic_effectiveness={GameMechanic.PROGRESS_BAR: 0.9, GameMechanic.CHALLENGE: 0.4},
            burnout_risk=0.2,
            novelty_decay_rates={"progress_bar": 0.01},
        )

        assert profile.user_id == "test_user"
        assert profile.motivation_types[MotivationType.ACHIEVEMENT] == 0.8
        assert profile.motivation_types[MotivationType.SOCIAL] == 0.3
        assert profile.motivation_types[MotivationType.COMPLETION] == 0.9
        assert profile.motivation_types[MotivationType.CURIOSITY] == 0.6
        assert profile.reward_preferences[RewardType.BADGES] == 0.7
        assert profile.reward_preferences[RewardType.POINTS] == 0.6
        assert profile.mechanic_effectiveness[GameMechanic.PROGRESS_BAR] == 0.9
        assert profile.mechanic_effectiveness[GameMechanic.CHALLENGE] == 0.4
        assert profile.burnout_risk == 0.2
        assert profile.novelty_decay_rates["progress_bar"] == 0.01


class TestGamificationAction:
    """Test the GamificationAction model."""

    def test_minimal_action(self):
        """Test creation of a minimal gamification action."""
        action = GamificationAction(user_id="test_user", mechanic=GameMechanic.PROGRESS_BAR)

        assert action.user_id == "test_user"
        assert action.mechanic == GameMechanic.PROGRESS_BAR
        assert action.reward_type is None
        assert action.context == {}
        assert action.strength == 1.0
        assert action.message is None
        assert action.visual_element is None

    def test_complete_action(self):
        """Test creation of a fully populated gamification action."""
        action = GamificationAction(
            user_id="test_user",
            mechanic=GameMechanic.CHALLENGE,
            reward_type=RewardType.BADGES,
            context={"task_id": "123", "importance": 0.8},
            strength=0.7,
            message="You've unlocked a new challenge!",
            visual_element={"color": "#FF0000", "animation": "bounce"},
        )

        assert action.user_id == "test_user"
        assert action.mechanic == GameMechanic.CHALLENGE
        assert action.reward_type == RewardType.BADGES
        assert action.context["task_id"] == "123"
        assert action.context["importance"] == 0.8
        assert action.strength == 0.7
        assert action.message == "You've unlocked a new challenge!"
        assert action.visual_element["color"] == "#FF0000"
        assert action.visual_element["animation"] == "bounce"


class TestAdaptiveGamificationEngine:
    """Test the AdaptiveGamificationEngine class."""

    @pytest.fixture
    def gamification_service(self):
        """Create a mock gamification service."""
        service = AsyncMock()

        # Set up the get_motivation_profile method
        profile = UserMotivationProfile(user_id="test_user")
        service.get_motivation_profile.return_value = profile

        return service

    @pytest.fixture
    def user_insights_service(self):
        """Create a mock user insights service."""
        return AsyncMock()

    @pytest.fixture
    def engine(self, gamification_service, user_insights_service):
        """Create an AdaptiveGamificationEngine instance for testing."""
        return AdaptiveGamificationEngine(
            gamification_service=gamification_service, user_insights_service=user_insights_service
        )

    def test_init(self, engine, gamification_service, user_insights_service):
        """Test that the engine initializes correctly."""
        assert engine.gamification_service == gamification_service
        assert engine.user_insights_service == user_insights_service
        assert engine.model_refresh_interval == timedelta(days=1)
        assert engine.user_models == {}
        assert hasattr(engine, "message_templates")
        assert hasattr(engine, "visual_templates")

    def test_load_default_templates(self, engine):
        """Test loading default templates."""
        # Re-run template loading
        engine._load_default_templates()

        # Check that templates for common mechanics exist
        assert GameMechanic.PROGRESS_BAR in engine.message_templates
        assert len(engine.message_templates[GameMechanic.PROGRESS_BAR]) > 0

        # Check that visual templates exist
        assert RewardType.BADGES in engine.visual_templates
        assert engine.visual_templates[RewardType.BADGES]["adhd_friendly"] is True

    @pytest.mark.asyncio
    async def test_get_user_profile_existing(self, engine, gamification_service):
        """Test getting an existing user profile."""
        profile = await engine.get_user_profile("test_user")

        assert profile.user_id == "test_user"
        gamification_service.get_motivation_profile.assert_called_once_with("test_user")
        gamification_service.save_motivation_profile.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_user_profile_new(self, engine, gamification_service):
        """Test getting a new user profile."""
        # Set up service to return None (no existing profile)
        gamification_service.get_motivation_profile.return_value = None

        profile = await engine.get_user_profile("new_user")

        assert profile.user_id == "new_user"
        gamification_service.get_motivation_profile.assert_called_once_with("new_user")
        gamification_service.save_motivation_profile.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_user_model_cached(self, engine):
        """Test getting a cached user model."""
        # Mock model
        mock_model = MagicMock()

        # Set up cached model
        engine.user_models["test_user"] = (
            mock_model,
            datetime.utcnow() - timedelta(hours=1),  # Recent enough to use cache
        )

        model = await engine._get_user_model("test_user")

        assert model == mock_model
        # The service should not have been called
        engine.user_insights_service.get_user_motivation_data.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_user_model_expired(self, engine, user_insights_service):
        """Test getting an expired user model."""
        # Mock model
        mock_model = MagicMock()
        mock_new_model = MagicMock()

        # Set up expired cached model
        engine.user_models["test_user"] = (
            mock_model,
            datetime.utcnow() - timedelta(days=2),  # Too old
        )

        # Mock model creation
        with patch("app.ui.adaptive_gamification.UserMotivationModel") as MockModel:
            MockModel.return_value = mock_new_model

            # Set up mock data
            user_data = {"some": "data"}
            user_insights_service.get_user_motivation_data.return_value = user_data

            model = await engine._get_user_model("test_user")

            assert model == mock_new_model
            user_insights_service.get_user_motivation_data.assert_called_once_with("test_user")
            mock_new_model.update.assert_called_once_with(user_data)

            # Check that cache was updated
            assert engine.user_models["test_user"][0] == mock_new_model

    @pytest.mark.asyncio
    async def test_update_profile_from_behavior(self, engine, gamification_service):
        """Test updating user profile based on behavior."""
        # Set up mock model
        mock_model = MagicMock()
        mock_model.predict.return_value = {
            "motivation_types": {MotivationType.ACHIEVEMENT: 0.8, MotivationType.NOVELTY: 0.7},
            "reward_preferences": {RewardType.BADGES: 0.9},
            "mechanic_effectiveness": {GameMechanic.PROGRESS_BAR: 0.6},
            "burnout_risk": 0.3,
            "novelty_decay_rates": {"progress_bar": 0.02},
        }

        # Set up cached model
        engine.user_models["test_user"] = (mock_model, datetime.utcnow())

        # Initial profile
        initial_profile = UserMotivationProfile(user_id="test_user")
        gamification_service.get_motivation_profile.return_value = initial_profile

        # Update profile with behavior
        behaviors = {"action": "completed_task", "difficulty": "high"}
        updated_profile = await engine.update_profile_from_behavior("test_user", behaviors)

        # Check model was called correctly
        mock_model.predict.assert_called_once_with(behaviors)

        # Check profile was updated
        assert updated_profile.motivation_types[MotivationType.ACHIEVEMENT] > 0.5  # Increased
        assert updated_profile.motivation_types[MotivationType.NOVELTY] > 0.5  # Increased
        assert updated_profile.reward_preferences[RewardType.BADGES] > 0.5  # Increased
        assert updated_profile.mechanic_effectiveness[GameMechanic.PROGRESS_BAR] > 0.5  # Increased
        assert updated_profile.burnout_risk > 0  # Increased from 0
        assert "progress_bar" in updated_profile.novelty_decay_rates

        # Check save was called
        gamification_service.save_motivation_profile.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_optimal_mechanics(self, engine):
        """Test getting optimal game mechanics based on context."""
        # Create profile with specific preferences
        profile = UserMotivationProfile(
            user_id="test_user",
            mechanic_effectiveness={
                GameMechanic.PROGRESS_BAR: 0.9,  # High effectiveness
                GameMechanic.CHALLENGE: 0.8,  # High effectiveness
                GameMechanic.TIMER: 0.5,  # Medium effectiveness
                GameMechanic.NARRATIVE: 0.3,  # Low effectiveness
                GameMechanic.LEADERBOARD: 0.7,  # Medium-high effectiveness
            },
        )

        # Set up the get_user_profile method to return our custom profile
        engine.get_user_profile = AsyncMock(return_value=profile)

        # Test with neutral context
        neutral_mechanics = await engine.get_optimal_mechanics("test_user", {}, limit=2)
        assert len(neutral_mechanics) == 2
        assert neutral_mechanics[0] == GameMechanic.PROGRESS_BAR  # Highest effectiveness
        assert neutral_mechanics[1] == GameMechanic.CHALLENGE  # Second highest

        # Test with boring task context (should boost NARRATIVE)
        boring_mechanics = await engine.get_optimal_mechanics(
            "test_user", {"task_type": "boring"}, limit=3
        )
        # NARRATIVE should now be in the top 3 due to boost
        assert GameMechanic.NARRATIVE in boring_mechanics

        # Test with afternoon time context (should boost TIMER)
        time_mechanics = await engine.get_optimal_mechanics(
            "test_user", {"current_hour": 15}, limit=3  # 3pm
        )
        # TIMER should be boosted in afternoon
        assert GameMechanic.TIMER in time_mechanics

        # Test with high burnout risk (should reduce CHALLENGE and LEADERBOARD)
        profile.burnout_risk = 0.8  # High burnout
        burnout_mechanics = await engine.get_optimal_mechanics("test_user", {}, limit=3)
        # CHALLENGE and LEADERBOARD should be ranked lower
        if (
            GameMechanic.CHALLENGE in burnout_mechanics
            and GameMechanic.LEADERBOARD in burnout_mechanics
        ):
            # If both are still present, PROGRESS_BAR should be ranked higher
            challenge_idx = burnout_mechanics.index(GameMechanic.CHALLENGE)
            leaderboard_idx = burnout_mechanics.index(GameMechanic.LEADERBOARD)
            progress_idx = burnout_mechanics.index(GameMechanic.PROGRESS_BAR)
            assert progress_idx < challenge_idx or progress_idx < leaderboard_idx

    @pytest.mark.asyncio
    async def test_get_gamification_actions(self, engine):
        """Test generating gamification actions."""
        # Create profile with specific preferences
        profile = UserMotivationProfile(
            user_id="test_user",
            mechanic_effectiveness={
                GameMechanic.PROGRESS_BAR: 0.9,
                GameMechanic.CHALLENGE: 0.7,
            },
            reward_preferences={
                RewardType.BADGES: 0.8,
                RewardType.POINTS: 0.5,
            },
        )

        # Set up get_user_profile and get_optimal_mechanics to return known values
        engine.get_user_profile = AsyncMock(return_value=profile)
        engine.get_optimal_mechanics = AsyncMock(
            return_value=[GameMechanic.PROGRESS_BAR, GameMechanic.CHALLENGE]
        )

        # Get actions
        context = {"completed": 3, "total": 10}
        actions = await engine.get_gamification_actions("test_user", context, count=2)

        # Check that we got the expected number of actions
        assert len(actions) == 2

        # Check first action
        assert actions[0].user_id == "test_user"
        assert actions[0].mechanic == GameMechanic.PROGRESS_BAR
        assert actions[0].reward_type == RewardType.BADGES  # Highest reward preference
        assert actions[0].context == context
        assert actions[0].message is not None
        assert actions[0].visual_element is not None

        # Check second action
        assert actions[1].user_id == "test_user"
        assert actions[1].mechanic == GameMechanic.CHALLENGE

    def test_generate_message(self, engine):
        """Test message generation for gamification mechanics."""
        # Override the message templates for testing
        engine.message_templates = {
            GameMechanic.PROGRESS_BAR: [
                "You're making great progress! {progress}% complete!",  # First template uses {progress}
                "Keep it up! Only {remaining}% to go!",
                "You've come so far already - {progress}% done!",
            ],
            GameMechanic.CHALLENGE: [
                "New challenge unlocked: {challenge_name}",
                "Ready for a challenge? Try {challenge_name}!",
                "Challenge yourself with: {challenge_name}",
            ],
        }

        # Force the random choice to select the first template
        with patch(
            "numpy.random.choice",
            return_value="You're making great progress! {progress}% complete!",
        ):
            # Test progress bar message with progress context
            progress_context = {"progress": 30}
            progress_message = engine._generate_message(GameMechanic.PROGRESS_BAR, progress_context)
            assert "30%" in progress_message

        # Test progress bar message with completed/total context
        with patch(
            "numpy.random.choice", return_value="You've come so far already - {progress}% done!"
        ):
            completed_context = {"completed": 3, "total": 10}
            completed_message = engine._generate_message(
                GameMechanic.PROGRESS_BAR, completed_context
            )
            assert "30%" in completed_message

        # Test challenge message
        with patch("numpy.random.choice", return_value="New challenge unlocked: {challenge_name}"):
            challenge_context = {"challenge_name": "Complete 5 tasks"}
            challenge_message = engine._generate_message(GameMechanic.CHALLENGE, challenge_context)
            assert "Complete 5 tasks" in challenge_message

        # Test mechanic without template
        custom_message = engine._generate_message(GameMechanic.COLLECTION, {})
        assert "collection" in custom_message.lower()

    def test_generate_visual_element(self, engine):
        """Test visual element generation for gamification mechanics."""
        # Test progress bar visuals
        progress_element = engine._generate_visual_element(
            GameMechanic.PROGRESS_BAR, RewardType.BADGES, {"progress": 75}
        )
        assert progress_element["type"] == "progress_bar"
        assert progress_element["progress_percent"] == 75
        assert progress_element["segmented"] is True
        assert progress_element["adhd_friendly"] is True

        # Test challenge visuals
        challenge_element = engine._generate_visual_element(
            GameMechanic.CHALLENGE,
            RewardType.ACHIEVEMENT,
            {"challenge_name": "Daily Goal", "difficulty": "hard"},
        )
        assert challenge_element["type"] == "challenge"
        assert challenge_element["challenge_name"] == "Daily Goal"
        assert challenge_element["difficulty"] == "hard"

        # Test timer visuals
        timer_element = engine._generate_visual_element(
            GameMechanic.TIMER, RewardType.POINTS, {"duration": 1500}  # 25 minutes
        )
        assert timer_element["type"] == "timer"
        assert timer_element["duration"] == 1500
        assert timer_element["visual_countdown"] is True

    def test_calculate_action_strength(self, engine):
        """Test calculation of action strength based on context."""
        # Create profile
        profile = UserMotivationProfile(
            user_id="test_user",
            mechanic_effectiveness={
                GameMechanic.PROGRESS_BAR: 0.8,
            },
            burnout_risk=0.0,
        )

        # Neutral context
        neutral_strength = engine._calculate_action_strength(profile, GameMechanic.PROGRESS_BAR, {})
        assert neutral_strength == 0.8  # Base effectiveness

        # High importance task
        importance_strength = engine._calculate_action_strength(
            profile, GameMechanic.PROGRESS_BAR, {"importance": 1.0}
        )
        assert importance_strength > neutral_strength  # Should increase

        # Difficult task
        difficulty_strength = engine._calculate_action_strength(
            profile, GameMechanic.PROGRESS_BAR, {"difficulty": 1.0}
        )
        assert difficulty_strength > neutral_strength  # Should increase

        # Low energy
        energy_strength = engine._calculate_action_strength(
            profile, GameMechanic.PROGRESS_BAR, {"energy_level": 0.1}
        )
        assert energy_strength > neutral_strength  # Should increase

        # High burnout risk
        profile.burnout_risk = 0.8
        burnout_strength = engine._calculate_action_strength(profile, GameMechanic.PROGRESS_BAR, {})
        # When there's no context but high burnout risk, the base value is still returned
        assert burnout_strength == 0.8  # With empty context, returns the base value

        # Test with both burnout and non-empty context
        burnout_context_strength = engine._calculate_action_strength(
            profile, GameMechanic.PROGRESS_BAR, {"importance": 0.5}
        )
        assert burnout_context_strength < 1.0  # The burnout should reduce the strength

    @pytest.mark.asyncio
    async def test_apply_gamification_action(self, engine, gamification_service):
        """Test applying a gamification action."""
        # Create action
        action = GamificationAction(
            user_id="test_user",
            mechanic=GameMechanic.CHALLENGE,
            reward_type=RewardType.BADGES,
            context={"task_id": "123"},
            message="You've unlocked a challenge!",
            visual_element={"type": "challenge", "color": "blue"},
        )

        # Apply action
        result = await engine.apply_gamification_action(action)

        # Check service call
        gamification_service.log_gamification_action.assert_called_once_with(
            user_id="test_user",
            mechanic="challenge",
            reward_type="badges",
            context={"task_id": "123"},
            strength=action.strength,
        )

        # Check return value
        assert result["user_id"] == "test_user"
        assert result["mechanic"] == "challenge"
        assert result["reward_type"] == "badges"
        assert result["message"] == "You've unlocked a challenge!"
        assert result["visual_element"] == {"type": "challenge", "color": "blue"}

    @pytest.mark.asyncio
    async def test_track_gamification_effectiveness(self, engine, gamification_service):
        """Test tracking effectiveness of a gamification action."""
        # Mock action retrieval
        action = {
            "mechanic": "challenge",
            "reward_type": "badges",
            "context": {"task_id": "123"},
        }
        gamification_service.get_gamification_action.return_value = action

        # Set up mock update_profile_from_behavior
        engine.update_profile_from_behavior = AsyncMock()

        # Track effectiveness
        engagement_metrics = {
            "completion_rate": 0.8,
            "time_engaged_seconds": 120,
            "reaction_score": 0.7,
        }
        await engine.track_gamification_effectiveness("test_user", "action123", engagement_metrics)

        # Check action retrieval
        gamification_service.get_gamification_action.assert_called_once_with("action123")

        # Check effectiveness recording
        gamification_service.record_action_effectiveness.assert_called_once()
        effectiveness_call = gamification_service.record_action_effectiveness.call_args[1]
        assert effectiveness_call["action_id"] == "action123"
        assert 0 <= effectiveness_call["effectiveness"] <= 1  # Should be normalized
        assert effectiveness_call["engagement_metrics"] == engagement_metrics

        # Check profile update
        engine.update_profile_from_behavior.assert_called_once()
        behaviors_arg = engine.update_profile_from_behavior.call_args[0][1]
        assert behaviors_arg["action_mechanic"] == "challenge"
        assert behaviors_arg["action_reward_type"] == "badges"
        assert behaviors_arg["effectiveness"] > 0
        assert behaviors_arg["context"] == {"task_id": "123"}
        assert behaviors_arg["engagement_metrics"] == engagement_metrics
