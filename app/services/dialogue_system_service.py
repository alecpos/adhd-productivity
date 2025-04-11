"""
Dialogue System Service for ADHD Calendar.

This service implements the 'forgot anything?' NLP dialogue system
for proactive forgetfulness and distraction mitigation.
"""
import logging
import re
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any

from sqlalchemy.orm import Session

from app.models.commitment_model import CommitmentModel, CommitmentSource, CommitmentStatus
from app.schemas.commitment_schema import (
    DialogueRequest,
    DialogueResponse,
    DialogueSession,
    DialogueMessage,
    CommitmentResponse
)
from app.services.base_service import BaseService
from app.services.llm_service import LLMService
from app.services.commitment_detection_service import CommitmentDetectionService
from app.core.exceptions import ServiceException

logger = logging.getLogger(__name__)


class DialogueSystemService(BaseService):
    """
    Service for the 'forgot anything?' NLP dialogue system.

    This service provides an interactive dialogue system that helps users
    remember commitments, identify potential forgotten promises, and
    proactively manage tasks.
    """

    def __init__(
        self,
        db: Session,
        llm_service: Optional[LLMService] = None,
        commitment_service: Optional[CommitmentDetectionService] = None
    ):
        """Initialize the dialogue system service."""
        super().__init__(db)
        self.llm_service = llm_service or LLMService()
        self.commitment_service = commitment_service or CommitmentDetectionService(db)

        # Store active dialogue sessions in memory
        self.active_sessions: Dict[str, DialogueSession] = {}

    def process_message(self, request: DialogueRequest, user_id: str) -> DialogueResponse:
        """
        Process a message from the user.

        Args:
            request: The dialogue request containing the message
            user_id: The user ID

        Returns:
            A dialogue response containing the system message and any detected commitments
        """
        # Get or create session
        session = self._get_or_create_session(request.session_id, user_id)

        # Add user message to session
        user_message = DialogueMessage(content=request.message, is_user=True)
        session.messages.append(user_message)

        # Process message
        detected_commitments = []

        # Check for commitments in the message
        if len(request.message.strip()) > 5:  # Only analyze non-trivial messages
            detection_result = self._detect_commitments_in_message(request.message, user_id, session)

            # If commitments were detected, add them to the session
            if detection_result:
                new_commitments, commitment_models = detection_result
                session.detected_commitments.extend([c.id for c in commitment_models])
                detected_commitments = [
                    CommitmentResponse.from_orm(model) for model in commitment_models
                ]

        # Generate response based on dialogue context
        system_message, suggestions = self._generate_system_response(
            session,
            detected_commitments,
            request.context
        )

        # Add system message to session
        system_dialogue_message = DialogueMessage(
            content=system_message,
            is_user=False
        )
        session.messages.append(system_dialogue_message)

        # Update session timestamp
        session.updated_at = datetime.utcnow()

        # Store updated session
        self.active_sessions[session.session_id] = session

        # Return response
        return DialogueResponse(
            message=system_message,
            session_id=session.session_id,
            detected_commitments=detected_commitments,
            suggestions=suggestions,
            context=session.context
        )

    def _get_or_create_session(
        self, session_id: Optional[str], user_id: str
    ) -> DialogueSession:
        """
        Get an existing session or create a new one.

        Args:
            session_id: Optional session ID
            user_id: The user ID

        Returns:
            The dialogue session
        """
        # If session ID is provided and valid, return that session
        if session_id and session_id in self.active_sessions:
            return self.active_sessions[session_id]

        # Otherwise create a new session
        new_session_id = str(uuid.uuid4())
        session = DialogueSession(
            session_id=new_session_id,
            user_id=user_id,
            messages=[],
            detected_commitments=[],
            context={}
        )

        self.active_sessions[new_session_id] = session
        return session

    def _detect_commitments_in_message(
        self, message: str, user_id: str, session: DialogueSession
    ) -> Optional[Tuple[List[CommitmentResponse], List[CommitmentModel]]]:
        """
        Detect commitments in a user message.

        Args:
            message: The user message
            user_id: The user ID
            session: The current dialogue session

        Returns:
            Tuple of (commitment responses, commitment models) or None
        """
        try:
            detection_request = {
                "text": message,
                "source": CommitmentSource.CHAT,
                "user_id": user_id,
                "context": session.context
            }

            detection_response = self.commitment_service.detect_commitments(detection_request)

            if detection_response.detected_commitments:
                commitment_models = self.commitment_service.create_multiple_commitments(
                    detection_response.detected_commitments
                )

                commitment_responses = [
                    CommitmentResponse.from_orm(model) for model in commitment_models
                ]

                return commitment_responses, commitment_models

            return None
        except Exception as e:
            logger.error(f"Error detecting commitments: {str(e)}")
            return None

    def _generate_system_response(
        self,
        session: DialogueSession,
        detected_commitments: List[CommitmentResponse],
        context: Optional[Dict[str, Any]]
    ) -> Tuple[str, List[str]]:
        """
        Generate a response from the system.

        Args:
            session: The dialogue session
            detected_commitments: Any newly detected commitments
            context: Additional context for response generation

        Returns:
            Tuple of (system message, suggested follow-up messages)
        """
        # Combine session messages for context
        messages_context = "\n".join([
            f"{'User' if msg.is_user else 'System'}: {msg.content}"
            for msg in session.messages[-5:]  # Use last 5 messages for context
        ])

        # Get pending commitments for this user
        pending_commitments = self._get_pending_commitments_summary(session.user_id)

        # Check for upcoming deadlines
        upcoming_tasks = self._get_upcoming_tasks_summary(session.user_id)

        # Create prompt for the LLM
        prompt = self._create_response_generation_prompt(
            messages_context=messages_context,
            detected_commitments=detected_commitments,
            pending_commitments=pending_commitments,
            upcoming_tasks=upcoming_tasks,
            context=context
        )

        try:
            llm_response = self.llm_service.generate_structured_output(
                prompt=prompt,
                output_format={
                    "response": "string",
                    "suggestions": ["string"]
                }
            )

            return llm_response.get("response", "I'm sorry, I couldn't process that."), llm_response.get("suggestions", [])

        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return "I'm sorry, I encountered an issue processing your message.", ["Can I help you with something else?"]

    def _create_response_generation_prompt(
        self,
        messages_context: str,
        detected_commitments: List[CommitmentResponse],
        pending_commitments: str,
        upcoming_tasks: str,
        context: Optional[Dict[str, Any]]
    ) -> str:
        """
        Create a prompt for response generation.

        Args:
            messages_context: Recent message history
            detected_commitments: Newly detected commitments
            pending_commitments: Summary of pending commitments
            upcoming_tasks: Summary of upcoming tasks
            context: Additional context

        Returns:
            Formatted prompt for the LLM
        """
        prompt = """
        You are a helpful reminder and assistant for a person with ADHD. Your goal is to help them remember commitments,
        manage tasks, and avoid forgetting important things.

        RECENT CONVERSATION:
        {messages_context}

        NEW COMMITMENTS DETECTED IN LAST MESSAGE:
        {detected_commitments}

        PENDING COMMITMENTS:
        {pending_commitments}

        UPCOMING TASKS:
        {upcoming_tasks}

        GUIDELINES:
        1. Be conversational and supportive, but concise.
        2. If new commitments were detected, acknowledge them and ask if the user wants to track them.
        3. If the user seems to be planning something, ask clarifying questions.
        4. If appropriate, remind them of pending commitments or upcoming tasks.
        5. Don't overwhelm with too many reminders at once.
        6. If the user asks about what they might have forgotten, provide helpful reminders.
        7. If the user is struggling with time management, offer ADHD-friendly strategies.

        Based on all this information, generate:
        1. A helpful, supportive response (1-3 sentences)
        2. 2-3 suggested follow-up questions or prompts
        """

        # Format detected commitments
        formatted_detected = "None"
        if detected_commitments:
            formatted_detected = "\n".join([
                f"- {c.text} (Priority: {c.priority.value})"
                for c in detected_commitments
            ])

        # Format the prompt with all the information
        formatted_prompt = prompt.format(
            messages_context=messages_context,
            detected_commitments=formatted_detected,
            pending_commitments=pending_commitments,
            upcoming_tasks=upcoming_tasks
        )

        # Add additional context if provided
        if context:
            formatted_prompt += "\n\nADDITIONAL CONTEXT:\n"
            for key, value in context.items():
                formatted_prompt += f"{key}: {value}\n"

        return formatted_prompt

    def _get_pending_commitments_summary(self, user_id: str) -> str:
        """
        Get a summary of pending commitments for a user.

        Args:
            user_id: The user ID

        Returns:
            Summary text of pending commitments
        """
        try:
            commitments, _ = self.commitment_service.get_user_commitments(
                user_id=user_id,
                status=CommitmentStatus.CONFIRMED,
                limit=5
            )

            if not commitments:
                return "No pending commitments."

            return "\n".join([
                f"- {c.text}" + (f" (Due: {c.due_date.strftime('%Y-%m-%d')})" if c.due_date else "")
                for c in commitments
            ])

        except Exception as e:
            logger.error(f"Error getting pending commitments: {str(e)}")
            return "Unable to retrieve pending commitments."

    def _get_upcoming_tasks_summary(self, user_id: str) -> str:
        """
        Get a summary of upcoming tasks for a user.

        Args:
            user_id: The user ID

        Returns:
            Summary text of upcoming tasks
        """
        # TODO: Implement integration with task service
        return "No upcoming tasks found."

    def get_active_sessions(self, user_id: str) -> List[DialogueSession]:
        """
        Get all active dialogue sessions for a user.

        Args:
            user_id: The user ID

        Returns:
            List of active dialogue sessions
        """
        # Find sessions for this user
        user_sessions = [
            session for session in self.active_sessions.values()
            if str(session.user_id) == str(user_id)
        ]

        # Sort by updated time (most recent first)
        return sorted(
            user_sessions,
            key=lambda s: s.updated_at,
            reverse=True
        )

    def clear_old_sessions(self, max_age_hours: int = 24) -> int:
        """
        Clear sessions older than the specified age.

        Args:
            max_age_hours: Maximum age in hours (default 24)

        Returns:
            Number of sessions cleared
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
        session_ids_to_remove = [
            session_id for session_id, session in self.active_sessions.items()
            if session.updated_at < cutoff_time
        ]

        for session_id in session_ids_to_remove:
            del self.active_sessions[session_id]

        return len(session_ids_to_remove)

    def end_session(self, session_id: str) -> bool:
        """
        End a dialogue session.

        Args:
            session_id: The session ID

        Returns:
            True if session was found and ended, False otherwise
        """
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
            return True
        return False
