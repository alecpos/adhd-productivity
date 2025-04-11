"""
Adversarial Debiasing System for Reminder and Suggestion Equity

This module implements an adversarial approach to mitigate bias in the reminder and
suggestion systems, ensuring fair treatment across different user groups, neurotypes,
and demographic characteristics.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import logging
from typing import Dict, List, Optional, Tuple, Union, Any, Callable

from app.core.config import settings

logger = logging.getLogger(__name__)


class AdversarialDebiasingModel(nn.Module):
    """
    Neural network with adversarial debiasing for fair recommendations.

    This model uses adversarial training to remove correlations with protected
    attributes (like neurotype, gender, age) from the model's predictions.
    """

    def __init__(
        self,
        input_dim: int,
        hidden_dim: int,
        output_dim: int,
        protected_dim: int,
        adversary_hidden_dim: int = 64,
        lambda_param: float = 1.0,
        dropout: float = 0.2
    ):
        """
        Initialize the adversarial debiasing model.

        Args:
            input_dim: Dimension of input features
            hidden_dim: Dimension of hidden layers
            output_dim: Dimension of output predictions
            protected_dim: Dimension of protected attributes
            adversary_hidden_dim: Dimension of adversary hidden layer
            lambda_param: Weight of adversarial loss
            dropout: Dropout rate for regularization
        """
        super().__init__()

        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.output_dim = output_dim
        self.protected_dim = protected_dim
        self.lambda_param = lambda_param

        # Main predictor network
        self.predictor = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim // 2, output_dim)
        )

        # Adversarial network to predict protected attributes
        self.adversary = nn.Sequential(
            nn.Linear(output_dim, adversary_hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(adversary_hidden_dim, protected_dim)
        )

        # Separate optimizers for predictor and adversary
        self.predictor_optimizer = torch.optim.Adam(self.predictor.parameters())
        self.adversary_optimizer = torch.optim.Adam(self.adversary.parameters())

        # Loss functions
        self.predictor_criterion = nn.MSELoss() if output_dim == 1 else nn.CrossEntropyLoss()
        self.adversary_criterion = nn.BCEWithLogitsLoss() if protected_dim == 1 else nn.CrossEntropyLoss()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass through the predictor only (for inference).

        Args:
            x: Input features of shape [batch_size, input_dim]

        Returns:
            Model predictions of shape [batch_size, output_dim]
        """
        predictor_output = self.predictor(x)
        adversary_output = self.adversary(predictor_output)
        return (predictor_output, adversary_output)

    def predictor_loss(self, predictions: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        """
        Calculate loss for the predictor network.

        Args:
            predictions: Model predictions
            targets: Ground truth targets

        Returns:
            Loss tensor
        """
        return self.predictor_criterion(predictions, targets)

    def adversary_loss(self, protected_predictions: torch.Tensor, protected_targets: torch.Tensor) -> torch.Tensor:
        """
        Calculate loss for the adversary network.

        Args:
            protected_predictions: Predicted protected attributes
            protected_targets: Actual protected attributes

        Returns:
            Loss tensor
        """
        return self.adversary_criterion(protected_predictions, protected_targets)

    def training_step(self, batch: Dict[str, torch.Tensor],
                     predictor_optimizer: torch.optim.Optimizer,
                     adversary_optimizer: torch.optim.Optimizer) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Perform one training step with adversarial debiasing.

        Args:
            batch: Dictionary containing features, targets, and protected_attributes
            predictor_optimizer: Optimizer for the predictor network
            adversary_optimizer: Optimizer for the adversary network

        Returns:
            Tuple of (predictor_loss, adversary_loss)
        """
        # Enable anomaly detection for debugging
        torch.autograd.set_detect_anomaly(True)

        features = batch["features"].clone()  # Use clone to avoid in-place modifications
        targets = batch["targets"].clone()
        protected_attributes = batch["protected_attributes"].clone()

        # Forward pass
        predictor_output = self.predictor(features)
        adversary_output = self.adversary(predictor_output)

        # Calculate predictor loss
        pred_loss = self.predictor_criterion(predictor_output, targets)

        # Step 1: Train adversary to predict protected attributes
        adversary_optimizer.zero_grad()
        adv_loss = self.adversary_criterion(adversary_output, protected_attributes)
        adv_loss.backward(retain_graph=True)
        adversary_optimizer.step()

        # Step 2: Train predictor to predict targets while fooling adversary
        predictor_optimizer.zero_grad()
        # Get new adversary output after adversary updates
        new_predictor_output = self.predictor(features)
        new_adversary_output = self.adversary(new_predictor_output)

        # Negative adversary loss encourages predictor to make it harder for adversary
        pred_loss_2 = self.predictor_criterion(new_predictor_output, targets)
        fool_loss = -self.lambda_param * self.adversary_criterion(new_adversary_output, protected_attributes)
        combined_loss = pred_loss_2 + fool_loss
        combined_loss.backward()
        predictor_optimizer.step()

        return pred_loss, adv_loss

    def evaluate(self, test_data: Dict[str, torch.Tensor]) -> Dict[str, float]:
        """
        Evaluate model performance on test data.

        Args:
            test_data: Dictionary with test features and targets

        Returns:
            Dictionary with evaluation metrics
        """
        features = test_data["features"]
        targets = test_data["targets"]
        protected_attributes = test_data["protected_attributes"]

        self.eval()
        with torch.no_grad():
            predictor_output, adversary_output = self.forward(features)

            # Calculate losses
            pred_loss = self.predictor_criterion(predictor_output, targets)
            adv_loss = self.adversary_criterion(adversary_output, protected_attributes)

            # Calculate metrics
            metrics = {
                "predictor_loss": pred_loss.item(),
                "adversary_loss": adv_loss.item(),
            }

            # Calculate fairness metrics
            demographics = torch.argmax(protected_attributes, dim=1) if protected_attributes.dim() > 1 else protected_attributes
            metrics.update(self._calculate_fairness_metrics(predictor_output, targets, demographics))

        return metrics

    def _calculate_fairness_metrics(self, predictions: torch.Tensor,
                                   targets: torch.Tensor,
                                   demographics: torch.Tensor) -> Dict[str, float]:
        """
        Calculate fairness metrics across demographic groups.

        Args:
            predictions: Model predictions
            targets: Ground truth values
            demographics: Group membership indicators

        Returns:
            Dictionary with fairness metrics
        """
        # Convert to binary predictions if needed
        binary_preds = (predictions > 0.5).float() if predictions.dim() == targets.dim() else torch.argmax(predictions, dim=1)
        binary_targets = (targets > 0.5).float() if targets.dim() > 1 else targets

        # Get unique demographic groups
        unique_groups = torch.unique(demographics)

        # Calculate group-wise metrics
        group_metrics = {}
        overall_accuracy = (binary_preds == binary_targets).float().mean().item()

        # Per-group metrics
        accuracies = []
        for group in unique_groups:
            group_mask = (demographics == group)
            if group_mask.sum() > 0:
                group_acc = (binary_preds[group_mask] == binary_targets[group_mask]).float().mean().item()
                accuracies.append(group_acc)
                group_metrics[f"group_{int(group)}_accuracy"] = group_acc

        # Fairness metrics
        if len(accuracies) > 1:
            min_acc = min(accuracies)
            max_acc = max(accuracies)
            accuracy_disparity = max_acc - min_acc
            group_metrics["accuracy_disparity"] = accuracy_disparity
            group_metrics["min_accuracy"] = min_acc
            group_metrics["max_accuracy"] = max_acc

        group_metrics["overall_accuracy"] = overall_accuracy

        return group_metrics

    def save(self, path: str) -> None:
        """
        Save the model to the specified path.

        Args:
            path: Path to save the model
        """
        torch.save({
            "predictor_state": self.predictor.state_dict(),
            "adversary_state": self.adversary.state_dict(),
            "config": {
                "input_dim": self.input_dim,
                "hidden_dim": self.hidden_dim,
                "output_dim": self.output_dim,
                "protected_dim": self.protected_dim,
                "dropout": self.dropout if hasattr(self, 'dropout') else 0.2,
                "lambda_param": self.lambda_param
            }
        }, path)

    @classmethod
    def load(cls, path: str, device: str = "cpu") -> "AdversarialDebiasingModel":
        """Load the model from the specified path."""
        checkpoint = torch.load(path, map_location=device)
        config = checkpoint["config"]

        # Create model with saved config
        model = cls(
            input_dim=config["input_dim"],
            hidden_dim=config["hidden_dim"],
            output_dim=config["output_dim"],
            protected_dim=config["protected_dim"],
            dropout=config["dropout"],
            lambda_param=config["lambda_param"]
        )

        # Load state dictionaries
        model.predictor.load_state_dict(checkpoint["predictor_state"])
        model.adversary.load_state_dict(checkpoint["adversary_state"])
        model.eval()

        return model


class ReminderDebiasingModel(AdversarialDebiasingModel):
    """
    Specialized adversarial debiasing model for reminders.

    This model ensures reminders are equitable across different user groups
    and prevents reinforcement of stereotypes or bias.
    """

    def __init__(
        self,
        feature_extractor: nn.Module,
        protected_attributes: List[str],
        hidden_dim: int = 128,
        lambda_param: float = 1.0
    ):
        """
        Initialize the reminder debiasing model.

        Args:
            feature_extractor: Pre-trained feature extractor for reminders
            protected_attributes: List of protected attribute names
            hidden_dim: Dimension of hidden layers
            lambda_param: Weight of adversarial loss
        """
        # Get dimensions from feature extractor
        input_dim = feature_extractor.output_dim

        # Output is reminder relevance score (0-1)
        output_dim = 1

        # Number of protected attributes
        protected_dim = len(protected_attributes)

        super().__init__(
            input_dim=input_dim,
            hidden_dim=hidden_dim,
            output_dim=output_dim,
            protected_dim=protected_dim,
            lambda_param=lambda_param
        )

        # Store the feature extractor
        self.feature_extractor = feature_extractor
        self.protected_attributes = protected_attributes

    def forward_with_features(self, inputs: Dict[str, Any]) -> torch.Tensor:
        """
        Forward pass with feature extraction.

        Args:
            inputs: Dictionary of input data

        Returns:
            Reminder relevance scores (0-1)
        """
        # Extract features
        features = self.feature_extractor(inputs)

        # Get predictions
        predictions = self.predictor(features)

        # Apply sigmoid to get scores in range 0-1
        relevance_scores = torch.sigmoid(predictions)

        return relevance_scores

    def evaluate_equity(
        self,
        test_data: List[Dict[str, Any]],
        protected_groups: Dict[str, List[int]],
        fairness_metrics: List[str] = ["demographic_parity", "equal_opportunity"]
    ) -> Dict[str, float]:
        """
        Evaluate fairness metrics across protected groups.

        Args:
            test_data: List of test data points
            protected_groups: Dictionary mapping attribute names to group indices
            fairness_metrics: List of fairness metrics to compute

        Returns:
            Dictionary with fairness metrics
        """
        self.eval()
        results = {}

        # Convert test data to tensors
        x_list, y_list, protected_list = [], [], []

        for item in test_data:
            # Extract features
            features = self.feature_extractor(item)
            x_list.append(features)

            # Extract target
            y_list.append(torch.tensor([item["relevant"]]).float())

            # Extract protected attributes
            protected_values = []
            for attr in self.protected_attributes:
                protected_values.append(item.get(attr, 0))
            protected_list.append(torch.tensor(protected_values).float())

        x = torch.stack(x_list)
        y = torch.stack(y_list)
        protected = torch.stack(protected_list)

        # Get model predictions
        with torch.no_grad():
            predictions = self.predictor(x)
            protected_predictions = self.adversary(predictions)
            relevance_scores = torch.sigmoid(protected_predictions)
            predicted_relevant = (relevance_scores >= 0.5).float()

        # Calculate fairness metrics
        for metric in fairness_metrics:
            if metric == "demographic_parity":
                # Calculate acceptance rate for each group
                for i, attr in enumerate(self.protected_attributes):
                    group_0_mask = protected[:, i] == 0
                    group_1_mask = protected[:, i] == 1

                    if torch.sum(group_0_mask) > 0 and torch.sum(group_1_mask) > 0:
                        group_0_rate = torch.mean(predicted_relevant[group_0_mask])
                        group_1_rate = torch.mean(predicted_relevant[group_1_mask])

                        # Difference in acceptance rates
                        results[f"demographic_parity_diff_{attr}"] = abs(
                            group_0_rate.item() - group_1_rate.item()
                        )

            elif metric == "equal_opportunity":
                # Calculate true positive rate for each group
                for i, attr in enumerate(self.protected_attributes):
                    group_0_mask = (protected[:, i] == 0) & (y.squeeze() == 1)
                    group_1_mask = (protected[:, i] == 1) & (y.squeeze() == 1)

                    if torch.sum(group_0_mask) > 0 and torch.sum(group_1_mask) > 0:
                        group_0_tpr = torch.mean(predicted_relevant[group_0_mask])
                        group_1_tpr = torch.mean(predicted_relevant[group_1_mask])

                        # Difference in true positive rates
                        results[f"equal_opportunity_diff_{attr}"] = abs(
                            group_0_tpr.item() - group_1_tpr.item()
                        )

        # Overall equity score (lower is better)
        equity_scores = [
            value for key, value in results.items()
            if key.startswith("demographic_parity") or key.startswith("equal_opportunity")
        ]
        if equity_scores:
            results["overall_equity_score"] = np.mean(equity_scores)

        self.train()
        return results


class SuggestionDebiasingModel(AdversarialDebiasingModel):
    """
    Specialized adversarial debiasing model for scheduling suggestions.

    This model ensures that schedule suggestions don't reinforce stereotypes
    or show bias toward certain user groups or neurotypes.
    """

    def __init__(
        self,
        input_dim: int,
        num_task_types: int,
        protected_attributes: List[str],
        hidden_dim: int = 128,
        lambda_param: float = 1.0
    ):
        """
        Initialize the suggestion debiasing model.

        Args:
            input_dim: Dimension of input features
            num_task_types: Number of different task types
            protected_attributes: List of protected attribute names
            hidden_dim: Dimension of hidden layers
            lambda_param: Weight of adversarial loss
        """
        # Output is task type preference scores
        output_dim = num_task_types

        # Number of protected attributes
        protected_dim = len(protected_attributes)

        super().__init__(
            input_dim=input_dim,
            hidden_dim=hidden_dim,
            output_dim=output_dim,
            protected_dim=protected_dim,
            lambda_param=lambda_param
        )

        self.protected_attributes = protected_attributes
        self.num_task_types = num_task_types

    def get_debiased_suggestions(
        self,
        user_features: Dict[str, Any],
        tasks: List[Dict[str, Any]],
        time_slots: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Generate debiased scheduling suggestions.

        Args:
            user_features: Dictionary of user features
            tasks: List of tasks to schedule
            time_slots: List of available time slots

        Returns:
            List of suggested task-to-slot assignments
        """
        self.eval()
        suggestions = []

        # Convert inputs to tensors
        user_tensor = self._extract_user_features(user_features)

        with torch.no_grad():
            for slot in time_slots:
                slot_tensor = self._extract_slot_features(slot)

                # Calculate scores for each task
                task_scores = []
                for task in tasks:
                    if task.get("scheduled", False):
                        # Skip already scheduled tasks
                        continue

                    task_tensor = self._extract_task_features(task)

                    # Combine features
                    combined_features = torch.cat([user_tensor, slot_tensor, task_tensor])

                    # Ensure the shape is correct for model input (batch dimension)
                    if combined_features.dim() == 1:
                        combined_features = combined_features.unsqueeze(0)  # Add batch dimension

                    # Get task suitability score from debiased model
                    predictor_output, _ = self.forward(combined_features)

                    # Extract the score (first element if it's a batch)
                    score = predictor_output[0][0].item() if predictor_output.dim() > 1 else predictor_output.item()
                    task_scores.append((task, score))

                if task_scores:
                    # Select best task for this slot
                    best_task, best_score = max(task_scores, key=lambda x: x[1])

                    suggestions.append({
                        "task_id": best_task.get("id", "unknown"),
                        "slot_id": slot.get("id", "unknown"),
                        "start_time": slot.get("start_time"),
                        "end_time": slot.get("end_time"),
                        "confidence": best_score,
                        "debiased": True
                    })

        self.train()
        return suggestions

    def _extract_user_features(self, user_features: Dict[str, Any]) -> torch.Tensor:
        """Extract and normalize user features."""
        # Simplified implementation - in a real system, you would have proper feature extraction
        feature_list = []
        for key, value in user_features.items():
            if key not in self.protected_attributes:
                if isinstance(value, (int, float)):
                    feature_list.append(float(value))

        # Pad or truncate to expected size
        while len(feature_list) < 10:  # Assuming 10 features
            feature_list.append(0.0)

        return torch.tensor(feature_list[:10]).float()

    def _extract_slot_features(self, slot: Dict[str, Any]) -> torch.Tensor:
        """Extract features from a time slot."""
        # Simplified implementation
        features = [
            slot.get("hour", 0) / 24.0,  # Normalize hour to 0-1
            slot.get("day_of_week", 0) / 7.0,  # Normalize day to 0-1
            1.0 if slot.get("is_morning", False) else 0.0,
            1.0 if slot.get("is_afternoon", False) else 0.0,
            1.0 if slot.get("is_evening", False) else 0.0
        ]
        return torch.tensor(features).float()

    def _extract_task_features(self, task: Dict[str, Any]) -> torch.Tensor:
        """Extract features from a task."""
        # Simplified implementation
        features = [
            task.get("estimated_duration", 60) / 480.0,  # Normalize duration to 0-1 (assumes max 8 hours)
            task.get("priority", 0) / 5.0,  # Normalize priority to 0-1
            1.0 if task.get("requires_focus", False) else 0.0,
            1.0 if task.get("is_creative", False) else 0.0,
            1.0 if task.get("is_routine", False) else 0.0
        ]
        return torch.tensor(features).float()


class DebiasingService:
    """
    Service for handling debiasing across the ADHD Calendar system.

    This service manages different debiasing models and provides interfaces
    for utilizing them within the application.
    """

    def __init__(self):
        """Initialize the debiasing service."""
        self.reminder_debiasing_model = None
        self.suggestion_debiasing_model = None
        self.protected_attributes = settings.PROTECTED_ATTRIBUTES if hasattr(settings, 'PROTECTED_ATTRIBUTES') else [
            "neurotype",
            "gender",
            "age_group",
            "socioeconomic_status"
        ]

    def initialize_models(
        self,
        reminder_feature_extractor: nn.Module = None,
        suggestion_input_dim: int = None,
        num_task_types: int = None
    ) -> None:
        """
        Initialize debiasing models.

        Args:
            reminder_feature_extractor: Feature extractor for reminder model
            suggestion_input_dim: Input dimension for suggestion model
            num_task_types: Number of task types for suggestion model
        """
        # Initialize reminder debiasing model if feature extractor provided
        if reminder_feature_extractor is not None:
            self.reminder_debiasing_model = ReminderDebiasingModel(
                feature_extractor=reminder_feature_extractor,
                protected_attributes=self.protected_attributes
            )
            logger.info("Initialized reminder debiasing model")

        # Initialize suggestion debiasing model if dimensions provided
        if suggestion_input_dim is not None and num_task_types is not None:
            self.suggestion_debiasing_model = SuggestionDebiasingModel(
                input_dim=suggestion_input_dim,
                num_task_types=num_task_types,
                protected_attributes=self.protected_attributes
            )
            logger.info("Initialized suggestion debiasing model")

    def load_models(self, reminder_path: str = None, suggestion_path: str = None) -> None:
        """
        Load trained debiasing models from files.

        Args:
            reminder_path: Path to saved reminder debiasing model
            suggestion_path: Path to saved suggestion debiasing model
        """
        if reminder_path:
            try:
                self.reminder_debiasing_model = ReminderDebiasingModel.load(reminder_path)
                logger.info(f"Loaded reminder debiasing model from {reminder_path}")
            except Exception as e:
                logger.error(f"Failed to load reminder debiasing model: {e}")

        if suggestion_path:
            try:
                self.suggestion_debiasing_model = SuggestionDebiasingModel.load(suggestion_path)
                logger.info(f"Loaded suggestion debiasing model from {suggestion_path}")
            except Exception as e:
                logger.error(f"Failed to load suggestion debiasing model: {e}")

    def get_debiased_reminders(self, reminders: List[Dict[str, Any]], user_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Apply debiasing to a list of reminders.

        Args:
            reminders: List of reminder objects
            user_profile: User profile information

        Returns:
            List of reminders with debiased priority scores
        """
        # Handle invalid input types
        if reminders is None:
            return reminders

        # Check if it's a list-like structure containing dictionaries
        if not isinstance(reminders, list) or not all(isinstance(item, dict) for item in reminders if item is not None):
            return reminders

        if self.reminder_debiasing_model is None:
            logger.warning("Reminder debiasing model not initialized")
            return reminders

        debiased_reminders = []
        for reminder in reminders:
            # Create a copy of the reminder
            debiased_reminder = reminder.copy()

            # Create input for the model containing task and user info
            model_input = {
                "task": reminder["task"],
                "user": user_profile
            }

            # Get debiased score from model
            try:
                debiased_score = self.reminder_debiasing_model.forward_with_features(model_input)
                # Convert tensor to float
                if isinstance(debiased_score, torch.Tensor):
                    debiased_score = debiased_score.item()
                debiased_reminder["priority"] = float(debiased_score)
            except Exception as e:
                logger.error(f"Error debiasing reminder: {str(e)}")

            debiased_reminders.append(debiased_reminder)

        return debiased_reminders

    def get_debiased_suggestions(
        self,
        user_features: Dict[str, Any],
        tasks: List[Dict[str, Any]],
        time_slots: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Get debiased scheduling suggestions.

        Args:
            user_features: Dictionary of user features
            tasks: List of tasks to schedule
            time_slots: List of available time slots

        Returns:
            List of suggested task-to-slot assignments
        """
        if self.suggestion_debiasing_model is None:
            logger.warning("Suggestion debiasing model not initialized")
            return []

        return self.suggestion_debiasing_model.get_debiased_suggestions(
            user_features=user_features,
            tasks=tasks,
            time_slots=time_slots
        )

    def audit_fairness(
        self,
        model_type: str,
        test_data: List[Dict[str, Any]],
        protected_groups: Dict[str, List[int]] = None
    ) -> Dict[str, float]:
        """
        Audit a model for fairness across protected groups.

        Args:
            model_type: Type of model to audit ('reminder' or 'suggestion')
            test_data: Test data for auditing
            protected_groups: Dictionary mapping attribute names to group indices

        Returns:
            Dictionary with fairness metrics
        """
        if model_type == "reminder" and self.reminder_debiasing_model is not None:
            return self.reminder_debiasing_model.evaluate_equity(
                test_data=test_data,
                protected_groups=protected_groups or {}
            )
        elif model_type == "suggestion" and self.suggestion_debiasing_model is not None:
            # Implement suggestion fairness audit if needed
            pass

        logger.warning(f"{model_type.capitalize()} debiasing model not initialized for audit")
        return {}


# Singleton instance
debiasing_service = DebiasingService()

def get_debiasing_service() -> DebiasingService:
    """Get the debiasing service singleton instance."""
    return debiasing_service
