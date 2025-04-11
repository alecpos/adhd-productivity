"""
Transparent Fallback Protocols for Preserving User Autonomy

This module implements a system of fallback protocols that preserve user autonomy
when ML model predictions have low confidence or might be inappropriate. The system
provides multiple fallback strategies with progressive levels of intervention based
on prediction confidence.
"""

import abc
import logging
import time
from enum import Enum
from typing import Dict, List, Optional, Tuple, Union, Any, Callable
from dataclasses import dataclass
import numpy as np

logger = logging.getLogger(__name__)


class FallbackReason(str, Enum):
    """Reasons for triggering a fallback protocol."""

    LOW_CONFIDENCE = "low_confidence"
    MODEL_ERROR = "model_error"
    OUT_OF_DISTRIBUTION = "out_of_distribution"
    MISSING_DATA = "missing_data"
    CONFLICTING_PREDICTIONS = "conflicting_predictions"
    UNEXPECTED_INPUT = "unexpected_input"
    TIMEOUT = "timeout"
    USER_PREFERENCE = "user_preference"


class FallbackAction(str, Enum):
    """Possible fallback actions when a model's prediction cannot be used."""

    ASK_USER = "ask_user"
    USE_DEFAULT = "use_default"
    USE_HEURISTIC = "use_heuristic"
    DEFER_DECISION = "defer_decision"
    SUGGEST_ALTERNATIVES = "suggest_alternatives"
    LOG_ONLY = "log_only"
    USE_PREVIOUS = "use_previous"


@dataclass
class FallbackEvent:
    """Record of a fallback protocol being triggered."""

    timestamp: float
    model_id: str
    reason: FallbackReason
    action_taken: FallbackAction
    input_summary: Dict[str, Any]
    confidence: Optional[float] = None
    error_message: Optional[str] = None
    user_response: Optional[Any] = None
    resolution: Optional[str] = None


class FallbackProtocol(abc.ABC):
    """
    Abstract base class for fallback protocols.

    Each protocol determines when to fall back from ML predictions to alternative
    approaches, and how to handle those fallback situations while preserving user
    autonomy.
    """

    def __init__(self, protocol_id: str, confidence_threshold: float):
        """
        Initialize a fallback protocol.

        Args:
            protocol_id: Unique identifier for this protocol
            confidence_threshold: The confidence threshold below which fallback is triggered
        """
        self.protocol_id = protocol_id
        self.confidence_threshold = confidence_threshold
        self.telemetry = {}  # Store telemetry data for monitoring protocol effectiveness

    @abc.abstractmethod
    def should_fallback(self, prediction: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """
        Determine if fallback should be triggered for this prediction.

        Args:
            prediction: The prediction made by the ML model
            context: Additional context information

        Returns:
            True if fallback should be triggered, False otherwise
        """
        pass

    @abc.abstractmethod
    def apply_fallback(self, prediction: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply the appropriate fallback strategy.

        Args:
            prediction: The prediction made by the ML model
            context: Additional context information

        Returns:
            The modified prediction or alternative result
        """
        pass

    def log_fallback_event(self, event_type: str, details: Dict[str, Any]) -> None:
        """
        Log a fallback event for monitoring and improvement.

        Args:
            event_type: Type of fallback event
            details: Details about the event
        """
        if event_type not in self.telemetry:
            self.telemetry[event_type] = []

        self.telemetry[event_type].append(details)
        logging.info(
            f"Fallback event: {event_type} - Protocol: {self.protocol_id} - Details: {details}"
        )

    def get_telemetry(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get telemetry data collected by this protocol.

        Returns:
            Dictionary of telemetry data by event type
        """
        return self.telemetry


class ProgressiveFallbackProtocol(FallbackProtocol):
    """
    A fallback protocol that applies progressively stronger interventions
    as confidence decreases.
    """

    def __init__(
        self, protocol_id: str, confidence_threshold: float, fallback_stages: List[Dict[str, Any]]
    ):
        """
        Initialize a progressive fallback protocol.

        Args:
            protocol_id: Unique identifier for this protocol
            confidence_threshold: The confidence threshold below which fallback is triggered
            fallback_stages: List of fallback stages, ordered by decreasing confidence threshold
        """
        super().__init__(protocol_id, confidence_threshold)
        self.fallback_stages = sorted(fallback_stages, key=lambda s: s["threshold"], reverse=True)

    def should_fallback(self, prediction: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """
        Determine if fallback should be triggered based on prediction confidence.

        Args:
            prediction: The prediction made by the ML model
            context: Additional context information

        Returns:
            True if confidence is below threshold, False otherwise
        """
        return prediction.get("confidence", 0) < self.confidence_threshold

    def apply_fallback(self, prediction: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply the appropriate fallback strategy based on confidence level.

        Args:
            prediction: The prediction made by the ML model
            context: Additional context information

        Returns:
            The modified prediction or alternative result
        """
        confidence = prediction.get("confidence", 0)

        # Find the appropriate stage - we need to find the stage with the lowest threshold
        # that's still above our confidence level
        # First, sort stages by threshold in ascending order
        sorted_stages = sorted(self.fallback_stages, key=lambda s: s["threshold"])

        # Find the first stage where confidence is above threshold
        appropriate_stage = None
        for stage in sorted_stages:
            if confidence < stage["threshold"]:
                appropriate_stage = stage
                break

        # If no stage was found, use the stage with the lowest threshold
        if appropriate_stage is None and sorted_stages:
            appropriate_stage = sorted_stages[-1]

        if appropriate_stage is None:
            # No stages available, return original prediction
            return prediction

        # Apply the appropriate stage
        result = {"original_prediction": prediction, "action": appropriate_stage["action"]}

        # Add stage-specific information
        if appropriate_stage["action"] == "notify":
            result["message"] = appropriate_stage.get("message", "Low confidence prediction")

        elif appropriate_stage["action"] == "alternative":
            result["alternatives"] = appropriate_stage.get("alternatives", [])

        elif appropriate_stage["action"] == "default":
            result["default_value"] = appropriate_stage.get("default_value", "default")

        # Log the fallback
        self.log_fallback_event(
            "progressive_fallback",
            {
                "confidence": confidence,
                "stage": appropriate_stage["action"],
                "threshold": appropriate_stage["threshold"],
            },
        )

        return result


class RuleBased(FallbackProtocol):
    """
    A fallback protocol that applies rules to determine when and how to fall back.
    """

    def __init__(
        self, protocol_id: str, confidence_threshold: float, rules: List[Dict[str, Callable]]
    ):
        """
        Initialize a rule-based fallback protocol.

        Args:
            protocol_id: Unique identifier for this protocol
            confidence_threshold: The confidence threshold below which fallback is triggered
            rules: List of rules, each with a condition and action function
        """
        super().__init__(protocol_id, confidence_threshold)
        self.rules = rules

    def should_fallback(self, prediction: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """
        Determine if fallback should be triggered based on rules.

        Args:
            prediction: The prediction made by the ML model
            context: Additional context information

        Returns:
            True if any rule condition is met, False otherwise
        """
        # Check confidence threshold first
        if prediction.get("confidence", 0) < self.confidence_threshold:
            return True

        # Check each rule's condition
        for rule in self.rules:
            if rule["condition"](prediction, context):
                return True

        return False

    def apply_fallback(self, prediction: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply the appropriate rule-based fallback.

        Args:
            prediction: The prediction made by the ML model
            context: Additional context information

        Returns:
            The modified prediction or alternative result
        """
        # Start with basic result structure
        result = {"original_prediction": prediction}

        # Find and apply the first matching rule
        for rule in self.rules:
            if rule["condition"](prediction, context):
                rule_result = rule["action"](prediction, context)
                result.update(rule_result)

                # Log the fallback event
                self.log_fallback_event(
                    "rule_based_fallback",
                    {"rule_result": rule_result, "prediction_value": prediction.get("value")},
                )

                return result

        # If no rule matches, return original prediction with minimal change
        result["result"] = prediction.get("value")
        return result


class UserPreferenceBased(FallbackProtocol):
    """
    A fallback protocol that respects user preferences for handling low-confidence predictions.
    """

    def __init__(
        self,
        protocol_id: str,
        confidence_threshold: float,
        user_preferences_service: Any,
        default_fallback: str = "notification",
    ):
        """
        Initialize a user preference-based fallback protocol.

        Args:
            protocol_id: Unique identifier for this protocol
            confidence_threshold: The confidence threshold below which fallback is triggered
            user_preferences_service: Service for retrieving user preferences
            default_fallback: Default fallback type if user preferences not available
        """
        super().__init__(protocol_id, confidence_threshold)
        self.user_preferences_service = user_preferences_service
        self.default_fallback = default_fallback

    def should_fallback(self, prediction: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """
        Determine if fallback should be triggered based on user-specific threshold.

        Args:
            prediction: The prediction made by the ML model
            context: Additional context information

        Returns:
            True if confidence is below user's threshold, False otherwise
        """
        user_id = context.get("user_id")
        confidence = prediction.get("confidence", 0)

        # Use default threshold if no user_id
        if not user_id:
            return confidence < self.confidence_threshold

        # Get user preferences
        preferences = self.user_preferences_service.get_user_fallback_preferences(user_id)

        # Use user's threshold if available, otherwise use default
        user_threshold = (
            preferences.get("confidence_threshold", self.confidence_threshold)
            if preferences
            else self.confidence_threshold
        )

        return confidence < user_threshold

    def apply_fallback(self, prediction: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply fallback based on user preferences.

        Args:
            prediction: The prediction made by the ML model
            context: Additional context information

        Returns:
            The modified prediction or alternative result
        """
        user_id = context.get("user_id")

        # Start with basic result structure
        result = {"original_prediction": prediction, "fallback_type": self.default_fallback}

        # Get user preferences if user_id is available
        if user_id:
            preferences = self.user_preferences_service.get_user_fallback_preferences(user_id)

            if preferences:
                # Use user's preferred fallback approach
                result["fallback_type"] = preferences.get(
                    "preferred_fallback", self.default_fallback
                )

                # Include notification channel if available
                if "notification_channel" in preferences:
                    result["notification_channel"] = preferences["notification_channel"]

        # Log the fallback event
        self.log_fallback_event(
            "user_preference_fallback",
            {
                "user_id": user_id,
                "fallback_type": result["fallback_type"],
                "prediction_value": prediction.get("value"),
            },
        )

        return result


class HybridFallback(FallbackProtocol):
    """
    A fallback protocol that combines multiple protocols using a selection strategy.
    """

    def __init__(
        self,
        protocol_id: str,
        confidence_threshold: float,
        protocols: List[FallbackProtocol],
        selection_strategy: str = "first_applicable",
    ):
        """
        Initialize a hybrid fallback protocol.

        Args:
            protocol_id: Unique identifier for this protocol
            confidence_threshold: The confidence threshold below which fallback is triggered
            protocols: List of fallback protocols to combine
            selection_strategy: Strategy for selecting which protocol to use:
                               "first_applicable" or "voting"
        """
        super().__init__(protocol_id, confidence_threshold)
        self.protocols = protocols
        self.selection_strategy = selection_strategy

    def should_fallback(self, prediction: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """
        Determine if fallback should be triggered using multiple protocols.

        Args:
            prediction: The prediction made by the ML model
            context: Additional context information

        Returns:
            True if fallback should be triggered, False otherwise
        """
        if self.selection_strategy == "first_applicable":
            # If any protocol says to fall back, we fall back
            for protocol in self.protocols:
                if protocol.should_fallback(prediction, context):
                    return True
            return False

        elif self.selection_strategy == "voting":
            # Majority vote
            votes = sum(1 for p in self.protocols if p.should_fallback(prediction, context))
            return votes > len(self.protocols) / 2

        else:
            # Default to first applicable
            return any(p.should_fallback(prediction, context) for p in self.protocols)

    def apply_fallback(self, prediction: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply fallback using the selected protocol.

        Args:
            prediction: The prediction made by the ML model
            context: Additional context information

        Returns:
            The modified prediction or alternative result from the selected protocol
        """
        # Find the first protocol that says to fall back
        for protocol in self.protocols:
            if protocol.should_fallback(prediction, context):
                result = protocol.apply_fallback(prediction, context)
                result["protocol_id"] = protocol.protocol_id
                return result

        # If no protocol says to fall back, return original with a note
        return {
            "original_prediction": prediction,
            "protocol_id": self.protocol_id,
            "message": "No fallback needed",
        }


class FallbackProtocolManager:
    """
    Manages multiple fallback protocols for different prediction types.
    """

    def __init__(self):
        """Initialize the fallback protocol manager."""
        self.protocols = {}
        self.default_protocol = None

    def register_protocol(self, prediction_type: str, protocol: FallbackProtocol) -> None:
        """
        Register a fallback protocol for a specific prediction type.

        Args:
            prediction_type: Type of prediction this protocol handles
            protocol: The fallback protocol to register
        """
        self.protocols[prediction_type] = protocol

    def set_default_protocol(self, protocol: FallbackProtocol) -> None:
        """
        Set the default fallback protocol.

        Args:
            protocol: The fallback protocol to use as default
        """
        self.default_protocol = protocol

    def get_protocol(self, prediction_type: str) -> FallbackProtocol:
        """
        Get the fallback protocol for a specific prediction type.

        Args:
            prediction_type: Type of prediction

        Returns:
            The appropriate fallback protocol

        Raises:
            ValueError: If no protocol is registered for this prediction type
        """
        if prediction_type in self.protocols:
            return self.protocols[prediction_type]
        elif self.default_protocol:
            return self.default_protocol
        else:
            raise ValueError(
                f"No fallback protocol registered for prediction type: {prediction_type}"
            )

    def apply_protocol(
        self, prediction_type: str, prediction: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Apply the appropriate fallback protocol for a prediction.

        Args:
            prediction_type: Type of prediction
            prediction: The prediction made by the ML model
            context: Additional context information

        Returns:
            The modified prediction or alternative result

        Raises:
            ValueError: If no protocol is registered for this prediction type
        """
        try:
            protocol = self.get_protocol(prediction_type)
        except ValueError as e:
            raise e

        # Check if fallback should be triggered
        if protocol.should_fallback(prediction, context):
            return protocol.apply_fallback(prediction, context)
        else:
            return prediction

    def get_telemetry(self) -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
        """
        Get telemetry data from all registered protocols.

        Returns:
            Dictionary of telemetry data by prediction type and event type
        """
        telemetry = {}
        for pred_type, protocol in self.protocols.items():
            telemetry[pred_type] = protocol.get_telemetry()

        return telemetry


class ReminderFallbackProtocol(FallbackProtocol):
    """
    Fallback protocol for reminder systems.

    This protocol handles cases where the reminder relevance or
    timing predictions may not be reliable.
    """

    def __init__(
        self,
        confidence_threshold: float = 0.65,
        enable_gradual_fallback: bool = True,
        user_preference_key: str = "reminder_fallback_preference",
    ):
        """
        Initialize the reminder fallback protocol.

        Args:
            confidence_threshold: Minimum confidence for automatic reminders
            enable_gradual_fallback: Whether to use gradual fallback for low confidence
            user_preference_key: Key for storing user preferences
        """
        super().__init__(
            name="reminder_fallback", confidence_threshold=confidence_threshold, timeout_seconds=3.0
        )
        self.enable_gradual_fallback = enable_gradual_fallback
        self.user_preference_key = user_preference_key

        # Previous successful reminders cache (for fallback)
        self.previous_reminders: Dict[str, Any] = {}

    def check_prediction(
        self,
        prediction: Dict[str, Any],
        confidence: float,
        model_id: str,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> Tuple[Dict[str, Any], bool, Optional[FallbackEvent]]:
        """
        Check a reminder prediction for fallback conditions.

        Args:
            prediction: Reminder prediction
            confidence: Confidence score
            model_id: Model identifier
            input_data: Input data
            context: Additional context

        Returns:
            Tuple of (potentially modified prediction, was_fallback_triggered, fallback_event)
        """
        # Get user preferences if available
        user_id = input_data.get("user_id")
        user_preferences = context.get("user_preferences", {}) if context else {}

        # Check for user override of fallback threshold
        user_threshold = None
        if user_id and user_preferences:
            user_threshold = user_preferences.get(f"{user_id}_{self.user_preference_key}_threshold")

        # Use user threshold if available
        threshold = user_threshold if user_threshold is not None else self.confidence_threshold

        # Check if confidence is below threshold
        if confidence < threshold:
            return self._handle_fallback(
                prediction=prediction,
                reason=FallbackReason.LOW_CONFIDENCE,
                model_id=model_id,
                input_data=input_data,
                context=context,
                confidence=confidence,
            )

        # Check for out-of-distribution inputs
        if context and context.get("is_out_of_distribution", False):
            return self._handle_fallback(
                prediction=prediction,
                reason=FallbackReason.OUT_OF_DISTRIBUTION,
                model_id=model_id,
                input_data=input_data,
                context=context,
                confidence=confidence,
            )

        # Store successful prediction for potential future fallbacks
        if user_id and "reminder_id" in prediction:
            key = f"{user_id}_{prediction['reminder_id']}"
            self.previous_reminders[key] = prediction

        return prediction, False, None

    def _get_fallback_action(
        self, reason: FallbackReason, prediction: Dict[str, Any], context: Optional[Dict[str, Any]]
    ) -> Tuple[FallbackAction, Dict[str, Any]]:
        """
        Determine the appropriate fallback action for reminders.

        Args:
            reason: Reason for the fallback
            prediction: The original prediction
            context: Additional context

        Returns:
            Tuple of (fallback_action, modified_prediction)
        """
        # Default to asking the user
        action = FallbackAction.ASK_USER
        modified_prediction = prediction.copy() if prediction else {}

        # Set fallback flag
        if modified_prediction:
            modified_prediction["is_fallback"] = True
            modified_prediction["fallback_reason"] = reason

        # Different handling based on reason
        if reason == FallbackReason.LOW_CONFIDENCE:
            if self.enable_gradual_fallback and prediction and "confidence" in prediction:
                # For low but not terrible confidence, use the prediction but mark it
                confidence = prediction["confidence"]
                if confidence > self.confidence_threshold * 0.8:  # Close to threshold
                    action = FallbackAction.SUGGEST_ALTERNATIVES
                    modified_prediction["needs_confirmation"] = True
                    modified_prediction["fallback_mode"] = "low_confidence_confirmation"
                else:
                    # Very low confidence
                    user_id = context.get("user_id") if context else None
                    reminder_id = prediction.get("reminder_id") if prediction else None

                    # Try to use previous successful reminder if available
                    if user_id and reminder_id:
                        key = f"{user_id}_{reminder_id}"
                        if key in self.previous_reminders:
                            action = FallbackAction.USE_PREVIOUS
                            modified_prediction = self.previous_reminders[key].copy()
                            modified_prediction["is_fallback"] = True
                            modified_prediction["fallback_mode"] = "previous_success"

        elif reason == FallbackReason.OUT_OF_DISTRIBUTION:
            # For OOD, use a simple heuristic
            action = FallbackAction.USE_HEURISTIC

            # Apply a safe heuristic (e.g., remind at standard times)
            if not modified_prediction:
                modified_prediction = {
                    "is_fallback": True,
                    "fallback_reason": reason,
                    "fallback_mode": "standard_schedule",
                    "reminder_time": "09:00",  # Default morning reminder
                    "needs_confirmation": True,
                }

        elif reason == FallbackReason.MODEL_ERROR:
            # For errors, defer to user but log the issue
            action = FallbackAction.ASK_USER

            # Prepare a user-friendly message
            if not modified_prediction:
                modified_prediction = {
                    "is_fallback": True,
                    "fallback_reason": reason,
                    "fallback_mode": "error_recovery",
                    "user_message": "I encountered an issue with your reminders. Would you like to set them manually?",
                    "needs_input": True,
                }

        return action, modified_prediction


class ScheduleFallbackProtocol(FallbackProtocol):
    """
    Fallback protocol for schedule recommendations.

    This protocol handles cases where schedule optimization or
    task assignment predictions may not be reliable.
    """

    def __init__(
        self,
        confidence_threshold: float = 0.7,
        max_suggestions: int = 3,
        allow_partial_results: bool = True,
    ):
        """
        Initialize the schedule fallback protocol.

        Args:
            confidence_threshold: Minimum confidence for automatic scheduling
            max_suggestions: Maximum number of alternative suggestions
            allow_partial_results: Whether to allow partial scheduling results
        """
        super().__init__(
            name="schedule_fallback",
            confidence_threshold=confidence_threshold,
            timeout_seconds=10.0,
        )
        self.max_suggestions = max_suggestions
        self.allow_partial_results = allow_partial_results

        # Store alternative schedules for fallback
        self.alternative_schedules: Dict[str, List[Dict[str, Any]]] = {}

    def check_prediction(
        self,
        prediction: Dict[str, Any],
        confidence: float,
        model_id: str,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> Tuple[Dict[str, Any], bool, Optional[FallbackEvent]]:
        """
        Check a schedule prediction for fallback conditions.

        Args:
            prediction: Schedule prediction
            confidence: Confidence score
            model_id: Model identifier
            input_data: Input data
            context: Additional context

        Returns:
            Tuple of (potentially modified prediction, was_fallback_triggered, fallback_event)
        """
        # Basic confidence check
        if confidence < self.confidence_threshold:
            return self._handle_fallback(
                prediction=prediction,
                reason=FallbackReason.LOW_CONFIDENCE,
                model_id=model_id,
                input_data=input_data,
                context=context,
                confidence=confidence,
            )

        # Check for conflicting predictions
        if prediction and "conflicts" in prediction and prediction["conflicts"]:
            if len(prediction["conflicts"]) > 2:  # Multiple conflicts
                return self._handle_fallback(
                    prediction=prediction,
                    reason=FallbackReason.CONFLICTING_PREDICTIONS,
                    model_id=model_id,
                    input_data=input_data,
                    context=context,
                    confidence=confidence,
                )

        # Check for missing essential data
        if "schedule" not in prediction or not prediction["schedule"]:
            return self._handle_fallback(
                prediction=prediction,
                reason=FallbackReason.MISSING_DATA,
                model_id=model_id,
                input_data=input_data,
                context=context,
                confidence=confidence,
            )

        # Store alternative schedules if available
        user_id = input_data.get("user_id")
        if user_id and "alternatives" in prediction and prediction["alternatives"]:
            self.alternative_schedules[user_id] = prediction["alternatives"]

        return prediction, False, None

    def _get_fallback_action(
        self, reason: FallbackReason, prediction: Dict[str, Any], context: Optional[Dict[str, Any]]
    ) -> Tuple[FallbackAction, Dict[str, Any]]:
        """
        Determine the appropriate fallback action for schedules.

        Args:
            reason: Reason for the fallback
            prediction: The original prediction
            context: Additional context

        Returns:
            Tuple of (fallback_action, modified_prediction)
        """
        modified_prediction = prediction.copy() if prediction else {}

        # Set fallback flag
        if modified_prediction:
            modified_prediction["is_fallback"] = True
            modified_prediction["fallback_reason"] = reason

        user_id = context.get("user_id") if context else None

        # Different handling based on reason
        if reason == FallbackReason.LOW_CONFIDENCE:
            # For low confidence, suggest alternatives
            if user_id and user_id in self.alternative_schedules:
                alternatives = self.alternative_schedules[user_id]
                if alternatives:
                    action = FallbackAction.SUGGEST_ALTERNATIVES
                    modified_prediction["fallback_mode"] = "alternative_suggestions"
                    modified_prediction["alternatives"] = alternatives[: self.max_suggestions]
                    return action, modified_prediction

            # If no alternatives, use a heuristic
            action = FallbackAction.USE_HEURISTIC
            if not modified_prediction.get("schedule"):
                modified_prediction["schedule"] = self._generate_heuristic_schedule(context)
            modified_prediction["fallback_mode"] = "heuristic_schedule"
            modified_prediction["needs_review"] = True

        elif reason == FallbackReason.CONFLICTING_PREDICTIONS:
            # For conflicts, ask the user to resolve them
            action = FallbackAction.ASK_USER
            modified_prediction["fallback_mode"] = "conflict_resolution"
            modified_prediction["needs_resolution"] = True

            # Highlight the conflicts for user resolution
            if "conflicts" in modified_prediction:
                modified_prediction["highlighted_conflicts"] = self._highlight_conflicts(
                    modified_prediction["conflicts"]
                )

        elif reason == FallbackReason.MISSING_DATA:
            # For missing data, use partial results if available and allowed
            if self.allow_partial_results and "partial_schedule" in modified_prediction:
                action = FallbackAction.USE_HEURISTIC
                modified_prediction["schedule"] = modified_prediction["partial_schedule"]
                modified_prediction["fallback_mode"] = "partial_results"
                modified_prediction["needs_completion"] = True
            else:
                # Otherwise, ask the user
                action = FallbackAction.ASK_USER
                modified_prediction["fallback_mode"] = "manual_scheduling"
                modified_prediction["needs_input"] = True

        else:  # MODEL_ERROR, TIMEOUT, etc.
            # For other issues, ask the user
            action = FallbackAction.ASK_USER
            modified_prediction["fallback_mode"] = "error_recovery"
            modified_prediction["user_message"] = (
                "I encountered an issue while optimizing your schedule. "
                "Would you like to create it manually?"
            )
            modified_prediction["needs_input"] = True

        return action, modified_prediction

    def _generate_heuristic_schedule(
        self, context: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Generate a simple heuristic schedule when ML model fails.

        Args:
            context: Context information

        Returns:
            A simple heuristic schedule
        """
        # Simple heuristic: distribute tasks evenly across standard work hours
        # In a real implementation, this would be more sophisticated
        schedule = []

        if not context or "tasks" not in context:
            return schedule

        tasks = context.get("tasks", [])

        # Define standard work hours (9 AM to 5 PM)
        start_hour = 9
        end_hour = 17
        total_hours = end_hour - start_hour

        # Evenly distribute tasks
        for i, task in enumerate(tasks[:total_hours]):  # Limit to available hours
            hour = start_hour + i
            schedule.append(
                {
                    "task_id": task.get("id", f"task_{i}"),
                    "start_time": f"{hour:02d}:00",
                    "end_time": f"{hour+1:02d}:00",
                    "is_heuristic": True,
                }
            )

        return schedule

    def _highlight_conflicts(self, conflicts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Highlight conflicts for user resolution.

        Args:
            conflicts: List of conflicts

        Returns:
            Highlighted conflicts with resolution suggestions
        """
        highlighted = []

        for i, conflict in enumerate(conflicts):
            highlighted_conflict = conflict.copy()

            # Add a simple resolution suggestion
            if "type" in conflict:
                if conflict["type"] == "overlap":
                    highlighted_conflict["suggestion"] = (
                        "These tasks overlap. Consider rescheduling one of them."
                    )
                elif conflict["type"] == "adjacency":
                    highlighted_conflict["suggestion"] = (
                        "These tasks are back-to-back with no transition time."
                    )
                elif conflict["type"] == "energy":
                    highlighted_conflict["suggestion"] = (
                        "This task may require more energy than you typically have at this time."
                    )

            highlighted.append(highlighted_conflict)

        return highlighted


# Factory function to get appropriate fallback protocol
def get_fallback_protocol(system_type: str) -> FallbackProtocol:
    """
    Get the appropriate fallback protocol for a system.

    Args:
        system_type: Type of system ('reminder', 'schedule', etc.)

    Returns:
        Appropriate fallback protocol
    """
    if system_type == "reminder":
        return ReminderFallbackProtocol()
    elif system_type == "schedule":
        return ScheduleFallbackProtocol()
    else:
        return FallbackProtocol(name=f"{system_type}_fallback")
