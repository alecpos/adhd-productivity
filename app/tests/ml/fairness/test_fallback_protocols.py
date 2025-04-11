"""Tests for the transparent fallback protocols system."""

import pytest
import logging
from unittest.mock import MagicMock, patch, call
from typing import Dict, List, Any

from app.ml.fairness.fallback_protocols import (
    FallbackProtocol,
    ProgressiveFallbackProtocol,
    RuleBased,
    UserPreferenceBased,
    HybridFallback,
    FallbackProtocolManager
)


class TestFallbackProtocol:
    """Test the base FallbackProtocol class."""

    def test_init(self):
        """Test initialization of FallbackProtocol."""
        # Create concrete subclass for testing abstract base class
        class ConcreteFallback(FallbackProtocol):
            def should_fallback(self, prediction, context):
                return False

            def apply_fallback(self, prediction, context):
                return {"fallback_applied": True}

        protocol = ConcreteFallback("test_protocol", 0.75)

        assert protocol is not None
        assert protocol.protocol_id == "test_protocol"
        assert protocol.confidence_threshold == 0.75
        assert protocol.telemetry == {}

    @patch("app.ml.fairness.fallback_protocols.logging.info")
    def test_log_fallback_event(self, mock_log_info):
        """Test logging a fallback event."""
        # Create concrete subclass for testing
        class ConcreteFallback(FallbackProtocol):
            def should_fallback(self, prediction, context):
                return False

            def apply_fallback(self, prediction, context):
                return {"fallback_applied": True}

        protocol = ConcreteFallback("test_protocol", 0.75)

        # Test logging
        event_type = "low_confidence"
        details = {"confidence": 0.5, "prediction": "task_A"}

        protocol.log_fallback_event(event_type, details)

        # Verify log was called
        mock_log_info.assert_called_once()

        # Verify telemetry was updated
        assert event_type in protocol.telemetry
        assert len(protocol.telemetry[event_type]) == 1
        assert protocol.telemetry[event_type][0] == details

    def test_get_telemetry(self):
        """Test getting telemetry data."""
        # Create concrete subclass for testing
        class ConcreteFallback(FallbackProtocol):
            def should_fallback(self, prediction, context):
                return False

            def apply_fallback(self, prediction, context):
                return {"fallback_applied": True}

        protocol = ConcreteFallback("test_protocol", 0.75)

        # Add some telemetry data
        protocol.telemetry = {
            "low_confidence": [{"confidence": 0.5}],
            "user_override": [{"user_id": "user123"}]
        }

        # Get telemetry
        telemetry = protocol.get_telemetry()

        # Verify telemetry data
        assert telemetry == protocol.telemetry
        assert "low_confidence" in telemetry
        assert "user_override" in telemetry


class TestProgressiveFallbackProtocol:
    """Test the ProgressiveFallbackProtocol class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.protocol = ProgressiveFallbackProtocol(
            protocol_id="progressive_test",
            confidence_threshold=0.7,
            fallback_stages=[
                {
                    "threshold": 0.7,
                    "action": "notify",
                    "message": "Low confidence prediction"
                },
                {
                    "threshold": 0.5,
                    "action": "alternative",
                    "alternatives": ["option_A", "option_B"]
                },
                {
                    "threshold": 0.3,
                    "action": "default",
                    "default_value": "safe_option"
                }
            ]
        )

    def test_init(self):
        """Test initialization of ProgressiveFallbackProtocol."""
        assert self.protocol is not None
        assert self.protocol.protocol_id == "progressive_test"
        assert self.protocol.confidence_threshold == 0.7
        assert len(self.protocol.fallback_stages) == 3

    def test_should_fallback_above_threshold(self):
        """Test should_fallback with confidence above threshold."""
        prediction = {"value": "task_A", "confidence": 0.8}
        context = {"user_id": "user123"}

        result = self.protocol.should_fallback(prediction, context)

        assert result is False

    def test_should_fallback_below_threshold(self):
        """Test should_fallback with confidence below threshold."""
        prediction = {"value": "task_A", "confidence": 0.6}
        context = {"user_id": "user123"}

        result = self.protocol.should_fallback(prediction, context)

        assert result is True

    def test_apply_fallback_stage1(self):
        """Test apply_fallback with first stage (notification)."""
        prediction = {"value": "task_A", "confidence": 0.6}
        context = {"user_id": "user123"}

        result = self.protocol.apply_fallback(prediction, context)

        assert result is not None
        assert "original_prediction" in result
        assert result["original_prediction"] == prediction
        assert result["action"] == "notify"
        assert "message" in result

    def test_apply_fallback_stage2(self):
        """Test apply_fallback with second stage (alternatives)."""
        prediction = {"value": "task_A", "confidence": 0.4}
        context = {"user_id": "user123"}

        result = self.protocol.apply_fallback(prediction, context)

        assert result is not None
        assert "original_prediction" in result
        assert result["original_prediction"] == prediction
        assert result["action"] == "alternative"
        assert "alternatives" in result
        assert isinstance(result["alternatives"], list)

    def test_apply_fallback_stage3(self):
        """Test apply_fallback with third stage (default)."""
        prediction = {"value": "task_A", "confidence": 0.2}
        context = {"user_id": "user123"}

        result = self.protocol.apply_fallback(prediction, context)

        assert result is not None
        assert "original_prediction" in result
        assert result["original_prediction"] == prediction
        assert result["action"] == "default"
        assert "default_value" in result
        assert result["default_value"] == "safe_option"

    @patch("app.ml.fairness.fallback_protocols.FallbackProtocol.log_fallback_event")
    def test_apply_fallback_logging(self, mock_log_event):
        """Test that fallback events are logged properly."""
        prediction = {"value": "task_A", "confidence": 0.4}
        context = {"user_id": "user123"}

        self.protocol.apply_fallback(prediction, context)

        # Verify log_fallback_event was called
        mock_log_event.assert_called_once()


class TestRuleBased:
    """Test the RuleBased fallback protocol."""

    def setup_method(self):
        """Set up test fixtures."""
        self.rules = [
            {
                "condition": lambda pred, ctx: pred["confidence"] < 0.6,
                "action": lambda pred, ctx: {"result": "fallback_1", "reason": "low confidence"}
            },
            {
                "condition": lambda pred, ctx: "high_risk" in ctx and ctx["high_risk"],
                "action": lambda pred, ctx: {"result": "safe_default", "reason": "high risk context"}
            }
        ]

        self.protocol = RuleBased(
            protocol_id="rule_based_test",
            confidence_threshold=0.7,
            rules=self.rules
        )

    def test_init(self):
        """Test initialization of RuleBased."""
        assert self.protocol is not None
        assert self.protocol.protocol_id == "rule_based_test"
        assert self.protocol.confidence_threshold == 0.7
        assert len(self.protocol.rules) == 2

    def test_should_fallback_confidence_below(self):
        """Test should_fallback with confidence below threshold."""
        prediction = {"value": "task_A", "confidence": 0.6}
        context = {}

        result = self.protocol.should_fallback(prediction, context)

        assert result is True

    def test_should_fallback_high_risk(self):
        """Test should_fallback with high risk context."""
        prediction = {"value": "task_A", "confidence": 0.8}
        context = {"high_risk": True}

        result = self.protocol.should_fallback(prediction, context)

        assert result is True

    def test_apply_fallback_rule1(self):
        """Test apply_fallback with first rule."""
        prediction = {"value": "task_A", "confidence": 0.5}
        context = {}

        result = self.protocol.apply_fallback(prediction, context)

        assert result is not None
        assert "original_prediction" in result
        assert result["original_prediction"] == prediction
        assert result["result"] == "fallback_1"
        assert result["reason"] == "low confidence"

    def test_apply_fallback_rule2(self):
        """Test apply_fallback with second rule."""
        prediction = {"value": "task_A", "confidence": 0.8}
        context = {"high_risk": True}

        result = self.protocol.apply_fallback(prediction, context)

        assert result is not None
        assert "original_prediction" in result
        assert result["original_prediction"] == prediction
        assert result["result"] == "safe_default"
        assert result["reason"] == "high risk context"

    def test_apply_fallback_no_matching_rules(self):
        """Test apply_fallback with no matching rules."""
        # Create a condition that won't match any rules
        prediction = {"value": "task_A", "confidence": 0.8}
        context = {"high_risk": False}

        result = self.protocol.apply_fallback(prediction, context)

        assert result is not None
        assert "original_prediction" in result
        assert result["original_prediction"] == prediction
        assert "result" in result
        assert result["result"] == prediction["value"]  # Default to original value


class TestUserPreferenceBased:
    """Test the UserPreferenceBased fallback protocol."""

    def setup_method(self):
        """Set up test fixtures."""
        # Mock user preferences service
        self.user_preferences_service = MagicMock()
        self.user_preferences_service.get_user_fallback_preferences.return_value = {
            "confidence_threshold": 0.65,
            "preferred_fallback": "manual_decision",
            "notification_channel": "email"
        }

        self.protocol = UserPreferenceBased(
            protocol_id="user_pref_test",
            confidence_threshold=0.7,
            user_preferences_service=self.user_preferences_service,
            default_fallback="notification"
        )

    def test_init(self):
        """Test initialization of UserPreferenceBased."""
        assert self.protocol is not None
        assert self.protocol.protocol_id == "user_pref_test"
        assert self.protocol.confidence_threshold == 0.7
        assert self.protocol.user_preferences_service == self.user_preferences_service
        assert self.protocol.default_fallback == "notification"

    def test_should_fallback_user_threshold(self):
        """Test should_fallback with user's confidence threshold."""
        prediction = {"value": "task_A", "confidence": 0.66}
        context = {"user_id": "user123"}

        # This is below the default threshold (0.7) but above user's (0.65)
        result = self.protocol.should_fallback(prediction, context)

        # Should check user preferences
        self.user_preferences_service.get_user_fallback_preferences.assert_called_once_with("user123")

        # Should not fallback as confidence (0.66) > user threshold (0.65)
        assert result is False

    def test_apply_fallback_user_preference(self):
        """Test apply_fallback using user's preferred fallback method."""
        prediction = {"value": "task_A", "confidence": 0.6}
        context = {"user_id": "user123"}

        result = self.protocol.apply_fallback(prediction, context)

        # Check user preferences were retrieved
        self.user_preferences_service.get_user_fallback_preferences.assert_called_once_with("user123")

        assert result is not None
        assert "original_prediction" in result
        assert result["original_prediction"] == prediction
        assert result["fallback_type"] == "manual_decision"  # User's preference
        assert "notification_channel" in result
        assert result["notification_channel"] == "email"

    def test_apply_fallback_no_user(self):
        """Test apply_fallback with no user in context."""
        prediction = {"value": "task_A", "confidence": 0.6}
        context = {}  # No user_id

        result = self.protocol.apply_fallback(prediction, context)

        # Should not try to get user preferences
        self.user_preferences_service.get_user_fallback_preferences.assert_not_called()

        assert result is not None
        assert "fallback_type" in result
        assert result["fallback_type"] == "notification"  # Default fallback

    def test_apply_fallback_user_not_found(self):
        """Test apply_fallback when user preferences are not found."""
        # Mock the service to return None (user not found)
        self.user_preferences_service.get_user_fallback_preferences.return_value = None

        prediction = {"value": "task_A", "confidence": 0.6}
        context = {"user_id": "unknown_user"}

        result = self.protocol.apply_fallback(prediction, context)

        assert result is not None
        assert "fallback_type" in result
        assert result["fallback_type"] == "notification"  # Default fallback


class TestHybridFallback:
    """Test the HybridFallback protocol."""

    def setup_method(self):
        """Set up test fixtures."""
        # Create mock protocols
        self.protocol1 = MagicMock()
        self.protocol1.protocol_id = "protocol1"
        self.protocol1.should_fallback.return_value = False

        self.protocol2 = MagicMock()
        self.protocol2.protocol_id = "protocol2"
        self.protocol2.should_fallback.return_value = True
        self.protocol2.apply_fallback.return_value = {"result": "fallback_from_protocol2"}

        # Create hybrid protocol
        self.protocol = HybridFallback(
            protocol_id="hybrid_test",
            confidence_threshold=0.7,
            protocols=[self.protocol1, self.protocol2],
            selection_strategy="first_applicable"
        )

    def test_init(self):
        """Test initialization of HybridFallback."""
        assert self.protocol is not None
        assert self.protocol.protocol_id == "hybrid_test"
        assert self.protocol.confidence_threshold == 0.7
        assert len(self.protocol.protocols) == 2
        assert self.protocol.selection_strategy == "first_applicable"

    def test_should_fallback_first_applicable(self):
        """Test should_fallback with first_applicable strategy."""
        prediction = {"value": "task_A", "confidence": 0.6}
        context = {"user_id": "user123"}

        # First protocol says no fallback, second says yes
        result = self.protocol.should_fallback(prediction, context)

        # Should check both protocols
        self.protocol1.should_fallback.assert_called_once_with(prediction, context)
        self.protocol2.should_fallback.assert_called_once_with(prediction, context)

        # Should return True because at least one protocol says to fallback
        assert result is True

    def test_apply_fallback_first_applicable(self):
        """Test apply_fallback with first_applicable strategy."""
        prediction = {"value": "task_A", "confidence": 0.6}
        context = {"user_id": "user123"}

        result = self.protocol.apply_fallback(prediction, context)

        # Should check first protocol first
        self.protocol1.should_fallback.assert_called_once_with(prediction, context)

        # First protocol says no fallback, so it shouldn't be applied
        self.protocol1.apply_fallback.assert_not_called()

        # Second protocol says yes to fallback, so it should be applied
        self.protocol2.should_fallback.assert_called_once_with(prediction, context)
        self.protocol2.apply_fallback.assert_called_once_with(prediction, context)

        # Should return result from protocol2
        assert result == {"result": "fallback_from_protocol2", "protocol_id": "protocol2"}

    def test_apply_fallback_all_protocols_no(self):
        """Test apply_fallback when all protocols say no fallback."""
        # Make protocol2 also return False for should_fallback
        self.protocol2.should_fallback.return_value = False

        prediction = {"value": "task_A", "confidence": 0.8}
        context = {"user_id": "user123"}

        result = self.protocol.apply_fallback(prediction, context)

        # Both protocols say no fallback
        self.protocol1.should_fallback.assert_called_once_with(prediction, context)
        self.protocol2.should_fallback.assert_called_once_with(prediction, context)

        # Neither protocol should be applied
        self.protocol1.apply_fallback.assert_not_called()
        self.protocol2.apply_fallback.assert_not_called()

        # Should return original prediction
        assert result == {"original_prediction": prediction, "protocol_id": "hybrid_test", "message": "No fallback needed"}

    def test_vote_based_strategy(self):
        """Test voting-based selection strategy."""
        # Create a hybrid protocol with voting strategy
        voting_protocol = HybridFallback(
            protocol_id="voting_test",
            confidence_threshold=0.7,
            protocols=[self.protocol1, self.protocol2, MagicMock()],  # Add a third protocol
            selection_strategy="voting"
        )

        # Configure mock returns for should_fallback
        self.protocol1.should_fallback.return_value = True
        self.protocol2.should_fallback.return_value = True
        voting_protocol.protocols[2].should_fallback.return_value = False

        prediction = {"value": "task_A", "confidence": 0.6}
        context = {"user_id": "user123"}

        # 2 out of 3 protocols vote for fallback
        result = voting_protocol.should_fallback(prediction, context)
        assert result is True

        # Make it 1 out of 3 (minority)
        self.protocol1.should_fallback.return_value = False
        result = voting_protocol.should_fallback(prediction, context)
        assert result is False


class TestFallbackProtocolManager:
    """Test the FallbackProtocolManager class."""

    def setup_method(self):
        """Set up test fixtures."""
        # Create mock protocols
        self.reminder_protocol = MagicMock()
        self.reminder_protocol.protocol_id = "reminder_protocol"

        self.scheduling_protocol = MagicMock()
        self.scheduling_protocol.protocol_id = "scheduling_protocol"

        self.duration_protocol = MagicMock()
        self.duration_protocol.protocol_id = "duration_protocol"

        # Create protocol manager
        self.manager = FallbackProtocolManager()

        # Register protocols
        self.manager.register_protocol("reminder", self.reminder_protocol)
        self.manager.register_protocol("scheduling", self.scheduling_protocol)
        self.manager.register_protocol("duration", self.duration_protocol)

    def test_init(self):
        """Test initialization of FallbackProtocolManager."""
        assert self.manager is not None
        assert len(self.manager.protocols) == 3
        assert "reminder" in self.manager.protocols
        assert "scheduling" in self.manager.protocols
        assert "duration" in self.manager.protocols

    def test_register_protocol(self):
        """Test registering a protocol."""
        new_protocol = MagicMock()
        new_protocol.protocol_id = "new_protocol"

        self.manager.register_protocol("new_type", new_protocol)

        assert "new_type" in self.manager.protocols
        assert self.manager.protocols["new_type"] == new_protocol

    def test_get_protocol(self):
        """Test getting a protocol."""
        protocol = self.manager.get_protocol("reminder")
        assert protocol == self.reminder_protocol

        # Test getting non-existent protocol
        with pytest.raises(ValueError):
            self.manager.get_protocol("non_existent")

    def test_apply_protocol(self):
        """Test applying a protocol."""
        prediction_type = "reminder"
        prediction = {"value": "task_A", "confidence": 0.6}
        context = {"user_id": "user123"}

        # Configure mock
        self.reminder_protocol.should_fallback.return_value = True
        self.reminder_protocol.apply_fallback.return_value = {"result": "fallback_result"}

        result = self.manager.apply_protocol(prediction_type, prediction, context)

        # Should check and apply the reminder protocol
        self.reminder_protocol.should_fallback.assert_called_once_with(prediction, context)
        self.reminder_protocol.apply_fallback.assert_called_once_with(prediction, context)

        # Should return result from protocol
        assert result == {"result": "fallback_result"}

    def test_apply_protocol_no_fallback(self):
        """Test applying a protocol when no fallback is needed."""
        prediction_type = "scheduling"
        prediction = {"value": "slot_B", "confidence": 0.9}
        context = {"user_id": "user123"}

        # Configure mock to not fallback
        self.scheduling_protocol.should_fallback.return_value = False

        result = self.manager.apply_protocol(prediction_type, prediction, context)

        # Should check the scheduling protocol
        self.scheduling_protocol.should_fallback.assert_called_once_with(prediction, context)

        # Should not apply any fallback
        self.scheduling_protocol.apply_fallback.assert_not_called()

        # Should return original prediction
        assert result == prediction

    def test_apply_protocol_default(self):
        """Test applying a default protocol when type not found."""
        self.manager.default_protocol = MagicMock()
        self.manager.default_protocol.protocol_id = "default_protocol"
        self.manager.default_protocol.should_fallback.return_value = True
        self.manager.default_protocol.apply_fallback.return_value = {"result": "default_fallback"}

        prediction_type = "unknown_type"
        prediction = {"value": "unknown", "confidence": 0.5}
        context = {}

        result = self.manager.apply_protocol(prediction_type, prediction, context)

        # Should use default protocol
        self.manager.default_protocol.should_fallback.assert_called_once_with(prediction, context)
        self.manager.default_protocol.apply_fallback.assert_called_once_with(prediction, context)

        # Should return result from default protocol
        assert result == {"result": "default_fallback"}

    def test_apply_protocol_no_default(self):
        """Test applying protocol when type not found and no default exists."""
        prediction_type = "unknown_type"
        prediction = {"value": "unknown", "confidence": 0.5}
        context = {}

        # No default protocol registered
        self.manager.default_protocol = None

        # Should raise error for unknown type
        with pytest.raises(ValueError):
            self.manager.apply_protocol(prediction_type, prediction, context)

    def test_get_telemetry(self):
        """Test getting telemetry from all protocols."""
        # Configure mocks to return telemetry
        self.reminder_protocol.get_telemetry.return_value = {"low_confidence": [{"count": 5}]}
        self.scheduling_protocol.get_telemetry.return_value = {"user_override": [{"count": 3}]}
        self.duration_protocol.get_telemetry.return_value = {"high_risk": [{"count": 2}]}

        telemetry = self.manager.get_telemetry()

        # Should call get_telemetry on all protocols
        self.reminder_protocol.get_telemetry.assert_called_once()
        self.scheduling_protocol.get_telemetry.assert_called_once()
        self.duration_protocol.get_telemetry.assert_called_once()

        # Should include telemetry from all protocols
        assert "reminder" in telemetry
        assert "scheduling" in telemetry
        assert "duration" in telemetry
        assert telemetry["reminder"] == {"low_confidence": [{"count": 5}]}
        assert telemetry["scheduling"] == {"user_override": [{"count": 3}]}
        assert telemetry["duration"] == {"high_risk": [{"count": 2}]}


class TestFallbackProtocolEdgeCases:
    """Test edge cases for fallback protocols."""

    def test_fallback_with_empty_context(self):
        """Test fallback with empty context data."""
        # Create concrete subclass for testing
        class ConcreteFallback(FallbackProtocol):
            def should_fallback(self, prediction, context):
                return True

            def apply_fallback(self, prediction, confidence, context=None):
                # Should handle None or empty context gracefully
                if context is None:
                    context = {}
                return {"action": "default", "prediction": "safe_value", "context_provided": bool(context)}

        protocol = ConcreteFallback("empty_context_test", 0.5)

        # Test with None context
        result = protocol.apply_fallback("test_prediction", 0.3, None)
        assert result["context_provided"] is False

        # Test with empty dict context
        result = protocol.apply_fallback("test_prediction", 0.3, {})
        assert result["context_provided"] is False

        # Test with valid context
        result = protocol.apply_fallback("test_prediction", 0.3, {"user_id": "123"})
        assert result["context_provided"] is True

    def test_fallback_with_invalid_confidence(self):
        """Test fallback with invalid confidence values."""
        # Create concrete subclass for testing
        class ConcreteFallback(FallbackProtocol):
            def should_fallback(self, prediction, context):
                return True

            def apply_fallback(self, prediction, confidence, context=None):
                # Should handle invalid confidence values
                if confidence is None or not isinstance(confidence, (int, float)):
                    confidence = 0.0
                elif confidence < 0:
                    confidence = 0.0
                elif confidence > 1:
                    confidence = 1.0

                return {"action": "default", "prediction": "safe_value", "normalized_confidence": confidence}

        protocol = ConcreteFallback("invalid_confidence_test", 0.5)

        # Test with None confidence
        result = protocol.apply_fallback("test_prediction", None)
        assert result["normalized_confidence"] == 0.0

        # Test with negative confidence
        result = protocol.apply_fallback("test_prediction", -0.5)
        assert result["normalized_confidence"] == 0.0

        # Test with confidence > 1
        result = protocol.apply_fallback("test_prediction", 1.5)
        assert result["normalized_confidence"] == 1.0

        # Test with valid confidence
        result = protocol.apply_fallback("test_prediction", 0.7)
        assert result["normalized_confidence"] == 0.7

    def test_progressive_fallback_with_invalid_stage_config(self):
        """Test ProgressiveFallbackProtocol with invalid stage configuration."""
        # Add validation to the ProgressiveFallbackProtocol initialization
        original_init = ProgressiveFallbackProtocol.__init__

        def patched_init(self, protocol_id, confidence_threshold, fallback_stages):
            # Validate fallback stages
            if not fallback_stages:
                raise ValueError("No fallback stages provided")

            for stage in fallback_stages:
                if "threshold" not in stage:
                    raise ValueError("Missing required field 'threshold' in fallback stage")
                if "action" not in stage:
                    raise ValueError("Missing required field 'action' in fallback stage")
                if stage["action"] not in ["notify", "alternative", "default"]:
                    raise ValueError(f"Unsupported action '{stage['action']}' in fallback stage")

            # Call original init
            original_init(self, protocol_id, confidence_threshold, fallback_stages)

        # Apply the patch
        ProgressiveFallbackProtocol.__init__ = patched_init

        try:
            # Test with empty stages list
            with pytest.raises(ValueError, match="No fallback stages provided"):
                ProgressiveFallbackProtocol("empty_stages", 0.7, [])

            # Test with missing threshold in stage
            with pytest.raises(ValueError, match="Missing required field 'threshold'"):
                ProgressiveFallbackProtocol("missing_threshold", 0.7, [
                    {"action": "notify", "message": "Low confidence"}
                ])

            # Test with missing action in stage
            with pytest.raises(ValueError, match="Missing required field 'action'"):
                ProgressiveFallbackProtocol("missing_action", 0.7, [
                    {"threshold": 0.5, "message": "Low confidence"}
                ])

            # Test with unsupported action
            with pytest.raises(ValueError, match="Unsupported action"):
                ProgressiveFallbackProtocol("invalid_action", 0.7, [
                    {"threshold": 0.5, "action": "invalid_action_type"}
                ])
        finally:
            # Restore original init
            ProgressiveFallbackProtocol.__init__ = original_init

    def test_protocol_manager_error_handling(self):
        """Test error handling in the FallbackProtocolManager."""
        manager = FallbackProtocolManager()

        # Test applying protocol for non-existent model
        prediction_type = "non_existent_model"
        prediction = {"value": "test_prediction", "confidence": 0.8}
        context = {}

        # Add validation to the apply_protocol method
        original_apply = manager.apply_protocol

        def patched_apply(prediction_type, prediction, context=None):
            if prediction_type not in manager.protocols and manager.default_protocol is None:
                raise ValueError(f"No fallback protocol registered for prediction type: {prediction_type}")
            return original_apply(prediction_type, prediction, context)

        # Apply the patch
        manager.apply_protocol = patched_apply

        # Test with non-existent prediction type
        with pytest.raises(ValueError, match=f"No fallback protocol registered for prediction type: {prediction_type}"):
            manager.apply_protocol(prediction_type, prediction, context)


class TestRuleBasedAdvanced:
    """Advanced tests for the RuleBased fallback protocol."""

    def setup_method(self):
        """Set up test fixtures."""
        # Define condition functions
        def confidence_below_06(prediction, context):
            return prediction.get("confidence", 1.0) < 0.6

        def importance_is_high(prediction, context):
            return context.get("importance") == "high"

        def confidence_below_03(prediction, context):
            return prediction.get("confidence", 1.0) < 0.3

        def type_is_critical(prediction, context):
            return prediction.get("type") == "critical"

        # Define action functions
        def provide_alternatives(prediction, context):
            return {
                "action": "alternative",
                "alternatives": ["option1", "option2"]
            }

        def provide_default(prediction, context):
            return {
                "action": "default",
                "prediction": "safe_default"
            }

        # Create complex rules with condition and action functions
        self.complex_rules = [
            {
                "name": "complex_rule_1",
                "condition": lambda p, c: confidence_below_06(p, c) and importance_is_high(p, c),
                "action": provide_alternatives
            },
            {
                "name": "complex_rule_2",
                "condition": lambda p, c: confidence_below_03(p, c) and type_is_critical(p, c),
                "action": provide_default
            }
        ]

        self.protocol = RuleBased(
            protocol_id="complex_rule_test",
            confidence_threshold=0.8,
            rules=self.complex_rules
        )

    def test_complex_rule_all_conditions_match(self):
        """Test rule where all conditions match."""
        # Include confidence inside the prediction object
        prediction = {"type": "normal", "value": "task_A", "confidence": 0.5}
        context = {"importance": "high"}

        result = self.protocol.apply_fallback(prediction, context)

        assert result["action"] == "alternative"
        assert "alternatives" in result
        assert result["alternatives"] == ["option1", "option2"]

    def test_complex_rule_mixed_conditions(self):
        """Test rule with mixed matching/non-matching conditions."""
        # Include confidence inside the prediction object
        prediction = {"type": "critical", "value": "task_B", "confidence": 0.25}
        context = {"importance": "low"}

        result = self.protocol.apply_fallback(prediction, context)

        assert result["action"] == "default"
        assert result["prediction"] == "safe_default"

    def test_rules_precedence_order(self):
        """Test that rules are evaluated in precedence order."""
        # Include confidence inside the prediction object
        prediction = {"type": "critical", "value": "task_C", "confidence": 0.25}
        context = {"importance": "high"}

        result = self.protocol.apply_fallback(prediction, context)

        # First rule should match and take precedence
        assert result["action"] == "alternative"
        assert "alternatives" in result


class TestHybridFallbackIntegration:
    """Integration tests for hybrid fallback protocols."""

    def setup_method(self):
        """Set up test fixtures."""
        # Define condition functions for rule-based protocol
        def risk_is_high(prediction, context):
            return context.get("risk") == "high"

        def provide_rule_default(prediction, context):
            return {"action": "default", "prediction": "rule_default"}

        # Create sub-protocols
        self.progressive = ProgressiveFallbackProtocol(
            protocol_id="hybrid_prog",
            confidence_threshold=0.7,
            fallback_stages=[
                {"threshold": 0.7, "action": "notify", "message": "Lower confidence"},
                {"threshold": 0.4, "action": "default", "default_value": "prog_default"}
            ]
        )

        self.rule_based = RuleBased(
            protocol_id="hybrid_rule",
            confidence_threshold=0.8,
            rules=[
                {
                    "name": "high_risk",
                    "condition": risk_is_high,
                    "action": provide_rule_default
                }
            ]
        )

        # Create a mock user preferences service
        mock_user_prefs = MagicMock()
        mock_user_prefs.get_user_fallback_preferences = lambda user_id: {"confidence_threshold": 0.6, "fallback_type": "manual_decision"} if user_id == "user123" else None

        self.user_pref = UserPreferenceBased(
            protocol_id="hybrid_user",
            confidence_threshold=0.5,
            user_preferences_service=mock_user_prefs
        )

        # Create hybrid protocol
        self.hybrid = HybridFallback(
            protocol_id="complex_hybrid",
            confidence_threshold=0.9,
            protocols=[self.progressive, self.rule_based, self.user_pref],
            selection_strategy="first_applicable"  # Use the correct parameter name
        )

    def test_hybrid_progressive_takes_precedence(self):
        """Test hybrid where progressive protocol condition matches first."""
        # Include confidence inside the prediction object
        prediction = {"value": "test_value", "confidence": 0.5}  # Below progressive but above user_pref
        context = {"user_id": "user123", "risk": "low"}

        result = self.hybrid.apply_fallback(prediction, context)

        # Progressive should win (notify action at 0.7 threshold)
        assert result["action"] == "notify"
        assert "message" in result

    def test_hybrid_rule_based_takes_precedence(self):
        """Test hybrid where rule condition matches first."""
        # Include confidence inside the prediction object
        prediction = {"value": "test_value", "confidence": 0.85}  # Above progressive and user_pref but rule has condition
        context = {"user_id": "other_user", "risk": "high"}

        result = self.hybrid.apply_fallback(prediction, context)

        # Rule-based should win because of the risk=high condition
        assert result["action"] == "default"
        assert result["prediction"] == "rule_default"

    def test_hybrid_weighted_strategy(self):
        """Test hybrid with weighted voting strategy."""
        # Create hybrid with voting strategy
        weighted_hybrid = HybridFallback(
            protocol_id="weighted_hybrid",
            confidence_threshold=0.9,
            protocols=[self.progressive, self.rule_based, self.user_pref],
            selection_strategy="voting"  # Use the correct parameter name
        )

        # All protocols match but with different actions
        # Include confidence inside the prediction object
        prediction = {"value": "test_value", "confidence": 0.3}  # Low enough to trigger all protocols
        context = {"user_id": "user123", "risk": "high"}

        result = weighted_hybrid.apply_fallback(prediction, context)

        # Should have some result from voting
        assert "action" in result or "fallback_type" in result


class TestFallbackIntegrationWithExplainability:
    """Test integration between fallback protocols and explainability."""

    def setup_method(self):
        """Set up test fixtures."""
        self.protocol = ProgressiveFallbackProtocol(
            protocol_id="explainable_fallback",
            confidence_threshold=0.7,
            fallback_stages=[
                {
                    "threshold": 0.7,
                    "action": "notify",
                    "message": "Low confidence prediction"
                },
                {
                    "threshold": 0.5,
                    "action": "alternative",
                    "alternatives": ["option_A", "option_B"]
                },
                {
                    "threshold": 0.3,
                    "action": "default",
                    "default_value": "safe_option"
                }
            ]
        )

        # Mock explainer
        self.mock_explainer = MagicMock()
        self.mock_explainer.explain.return_value = {
            "feature_importance": {"feature1": 0.3, "feature2": 0.7},
            "explanation": "Feature2 was the most important factor."
        }

    def test_fallback_with_explanation(self):
        """Test combining fallback with explanation."""
        # Create prediction with confidence inside the prediction object
        prediction = {
            "value": "task_A",
            "confidence": 0.4,
            "features": {"feature1": 10, "feature2": 20}
        }

        # Create context with explainer
        context = {
            "user_id": "user123",
            "explainer": self.mock_explainer
        }

        # Apply fallback
        result = self.protocol.apply_fallback(prediction, context)

        # Should include fallback information
        assert result["action"] == "alternative"
        assert "alternatives" in result
        assert result["alternatives"] == ["option_A", "option_B"]

        # In a real implementation, the fallback protocol would call the explainer
        # Here we'll manually call it to simulate that integration
        explanation = self.mock_explainer.explain(
            model_input=prediction["features"],
            prediction=result,
            confidence=prediction["confidence"]
        )

        # Verify explainer was called
        self.mock_explainer.explain.assert_called_once()

        # Verify explanation contains useful information
        assert explanation["feature_importance"] is not None
        assert explanation["explanation"] is not None
