"""
Smart Reminder Service for ADHD Calendar.

This service provides contextually-aware reminders for commitments and tasks,
supporting proactive forgetfulness and distraction mitigation.
"""
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Tuple
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.commitment_model import CommitmentModel, CommitmentStatus, CommitmentPriority
from app.models.reminder_model import ReminderModel
from app.schemas.commitment_schema import CommitmentReminder
from app.services.base_service import BaseService
from app.services.commitment_detection_service import CommitmentDetectionService
from app.services.notifications_service import NotificationsService
from app.core.exceptions import ServiceException

logger = logging.getLogger(__name__)


class SmartReminderService(BaseService):
    """
    Service for generating contextually-aware reminders.
    
    This service provides smart reminders with sensitivity to context,
    importance, and timing needs for ADHD users.
    """

    def __init__(
        self, 
        db: Session, 
        commitment_service: Optional[CommitmentDetectionService] = None,
        notifications_service: Optional[NotificationsService] = None
    ):
        """Initialize the smart reminder service."""
        super().__init__(db)
        self.commitment_service = commitment_service or CommitmentDetectionService(db)
        self.notifications_service = notifications_service or NotificationsService()
        
    def get_due_reminders(self, user_id: UUID) -> List[CommitmentReminder]:
        """
        Get reminders that are due for a user.
        
        Args:
            user_id: The user ID
            
        Returns:
            List of due commitment reminders
        """
        # Get commitments due in the next 24 hours
        due_commitments = self.commitment_service.get_commitments_due_soon(
            user_id=user_id,
            hours_threshold=24
        )
        
        # Convert to reminders
        reminders = []
        for commitment in due_commitments:
            reminders.append(
                CommitmentReminder(
                    commitment_id=commitment.id,
                    text=commitment.text,
                    due_date=commitment.due_date,
                    time_frame=commitment.time_frame,
                    priority=commitment.priority,
                    related_person=commitment.related_person,
                    action_required=commitment.action_required
                )
            )
        
        return reminders
    
    def send_commitment_reminder(self, reminder: CommitmentReminder, user_id: UUID) -> bool:
        """
        Send a commitment reminder to a user.
        
        Args:
            reminder: The commitment reminder
            user_id: The user ID
            
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            # Create a reminder message based on the commitment
            message = self._create_reminder_message(reminder)
            
            # Track the reminder in the database
            db_reminder = ReminderModel(
                user_id=user_id,
                title=f"Commitment: {reminder.text[:30]}...",
                description=message,
                reminder_type="commitment",
                priority=reminder.priority.value,
                status="sent",
                scheduled_time=datetime.utcnow(),
                related_commitment_id=reminder.commitment_id
            )
            
            self.db.add(db_reminder)
            self.db.commit()
            
            # Send the reminder via notifications service
            self.notifications_service.send_notification(
                user_id=user_id,
                title=f"Commitment Reminder",
                message=message,
                notification_type="commitment_reminder",
                data={"commitment_id": reminder.commitment_id}
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending commitment reminder: {str(e)}")
            return False
    
    def _create_reminder_message(self, reminder: CommitmentReminder) -> str:
        """
        Create a reminder message based on the commitment details.
        
        Args:
            reminder: The commitment reminder
            
        Returns:
            Formatted reminder message
        """
        # Base message with the commitment text
        message = f"Remember: {reminder.text}"
        
        # Add due date information if available
        if reminder.due_date:
            due_date_str = reminder.due_date.strftime("%A, %B %d at %I:%M %p")
            message += f" (Due: {due_date_str})"
        elif reminder.time_frame:
            message += f" (Due: {reminder.time_frame})"
        
        # Add action information if available
        if reminder.action_required:
            message += f"\nAction needed: {reminder.action_required}"
        
        # Add person information if available
        if reminder.related_person:
            message += f"\nInvolves: {reminder.related_person}"
        
        return message
    
    def process_smart_reminders(self, user_id: UUID) -> Dict[str, Any]:
        """
        Process smart reminders for a user.
        
        This method retrieves due commitments, determines which ones need reminders,
        sends the reminders, and returns a summary of the actions taken.
        
        Args:
            user_id: The user ID
            
        Returns:
            Summary of reminder processing
        """
        try:
            # Get due reminders
            due_reminders = self.get_due_reminders(user_id)
            
            # Prioritize reminders based on context, importance, etc.
            prioritized_reminders = self._prioritize_reminders(due_reminders, user_id)
            
            # Send the reminders
            sent_count = 0
            for reminder in prioritized_reminders:
                if self.send_commitment_reminder(reminder, user_id):
                    sent_count += 1
            
            return {
                "total_due": len(due_reminders),
                "sent": sent_count,
                "processed_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing smart reminders: {str(e)}")
            return {
                "error": str(e),
                "processed_at": datetime.utcnow().isoformat()
            }
    
    def _prioritize_reminders(
        self, reminders: List[CommitmentReminder], user_id: UUID
    ) -> List[CommitmentReminder]:
        """
        Prioritize reminders based on context and importance.
        
        Args:
            reminders: List of commitment reminders
            user_id: The user ID
            
        Returns:
            Prioritized list of reminders
        """
        if not reminders:
            return []
        
        # For now, just sort by priority and due date
        # TODO: Implement more sophisticated prioritization based on context
        def sort_key(reminder):
            # Create a tuple for sorting (priority value, due date)
            priority_values = {
                CommitmentPriority.CRITICAL: 0,
                CommitmentPriority.HIGH: 1,
                CommitmentPriority.MEDIUM: 2,
                CommitmentPriority.LOW: 3
            }
            priority_value = priority_values.get(reminder.priority, 4)
            due_date = reminder.due_date or datetime.max
            
            return (priority_value, due_date)
        
        # Sort reminders
        sorted_reminders = sorted(reminders, key=sort_key)
        
        # Only return top 5 to avoid overwhelming the user
        return sorted_reminders[:5]
    
    def schedule_reminder_for_commitment(
        self, 
        commitment_id: int, 
        reminder_time: datetime,
        user_id: UUID
    ) -> ReminderModel:
        """
        Schedule a reminder for a specific commitment.
        
        Args:
            commitment_id: The commitment ID
            reminder_time: When to send the reminder
            user_id: The user ID
            
        Returns:
            The created reminder model
            
        Raises:
            ServiceException: If commitment not found
        """
        # Get the commitment
        commitment = self.commitment_service.get_commitment(commitment_id)
        
        if commitment.user_id != user_id:
            raise ServiceException("Commitment does not belong to user")
        
        # Create a reminder
        reminder = ReminderModel(
            user_id=user_id,
            title=f"Commitment: {commitment.text[:30]}...",
            description=commitment.text,
            reminder_type="commitment",
            priority=commitment.priority.value,
            status="scheduled",
            scheduled_time=reminder_time,
            related_commitment_id=commitment_id
        )
        
        self.db.add(reminder)
        self.db.commit()
        self.db.refresh(reminder)
        
        return reminder
    
    def mark_commitment_reminded(self, commitment_id: int) -> CommitmentModel:
        """
        Mark a commitment as having been reminded.
        
        Args:
            commitment_id: The commitment ID
            
        Returns:
            The updated commitment model
        """
        # This method would update metadata on the commitment
        # For now, we just return the commitment
        return self.commitment_service.get_commitment(commitment_id)
    
    def get_reminders_history(
        self, 
        user_id: UUID,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        limit: int = 50
    ) -> List[ReminderModel]:
        """
        Get reminder history for a user.
        
        Args:
            user_id: The user ID
            from_date: Start date filter
            to_date: End date filter
            limit: Maximum number of records to return
            
        Returns:
            List of reminder models
        """
        query = self.db.query(ReminderModel).filter(ReminderModel.user_id == user_id)
        
        if from_date:
            query = query.filter(ReminderModel.scheduled_time >= from_date)
            
        if to_date:
            query = query.filter(ReminderModel.scheduled_time <= to_date)
        
        query = query.order_by(ReminderModel.scheduled_time.desc())
        query = query.limit(limit)
        
        return query.all()
    
    def get_contextual_reminders(self, user_id: UUID, context: Dict[str, Any]) -> List[CommitmentReminder]:
        """
        Get reminders that are relevant to the current context.
        
        Args:
            user_id: The user ID
            context: Context information (location, activity, etc.)
            
        Returns:
            List of contextually relevant reminders
        """
        # This would implement sophisticated context matching
        # For now, we just return due reminders
        return self.get_due_reminders(user_id)