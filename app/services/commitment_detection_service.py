"""
Commitment Detection Service for ADHD Calendar.

This service provides functionality to detect commitments in text,
supporting proactive forgetfulness and distraction mitigation.
"""
import re
import time
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.commitment_model import CommitmentModel, CommitmentSource, CommitmentStatus, CommitmentPriority
from app.schemas.commitment_schema import (
    CommitmentCreate, 
    CommitmentDetectionRequest, 
    CommitmentDetectionResponse,
    CommitmentUpdate,
    CommitmentInDB
)
from app.services.base_service import BaseService
from app.services.llm_service import LLMService
from app.core.exceptions import ServiceException

logger = logging.getLogger(__name__)


class CommitmentDetectionService(BaseService):
    """
    Service for detecting and managing commitments.
    
    This service uses transformer-based models to detect commitments
    in text and manages the commitment lifecycle.
    """

    def __init__(self, db: Session, llm_service: Optional[LLMService] = None):
        """Initialize the commitment detection service."""
        super().__init__(db)
        self.llm_service = llm_service or LLMService()
        
        # Common commitment patterns for regex-based detection
        self.commitment_patterns = [
            r"I\s+(?:will|shall|am\s+going\s+to|plan\s+to)\s+([^.,;!?]+)",
            r"I\s+(?:promise|commit|pledge|guarantee|assure)\s+(?:to|that)\s+([^.,;!?]+)",
            r"I'll\s+([^.,;!?]+)",
            r"I\s+need\s+to\s+([^.,;!?]+)",
            r"let\s+me\s+([^.,;!?]+)",
            r"I\s+should\s+([^.,;!?]+)",
            r"I\s+must\s+([^.,;!?]+)",
            r"I\s+have\s+to\s+([^.,;!?]+)",
            r"(?:don't\s+let\s+me\s+forget|remind\s+me)\s+to\s+([^.,;!?]+)",
        ]
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.commitment_patterns]
        
    def detect_commitments(
        self, request: CommitmentDetectionRequest
    ) -> CommitmentDetectionResponse:
        """
        Detect commitments in text.
        
        Args:
            request: The commitment detection request
            
        Returns:
            A response containing detected commitments
        """
        start_time = time.time()
        
        # Extract commitments using both approaches
        regex_commitments = self._detect_with_regex(request.text)
        llm_commitments = self._detect_with_llm(request.text, request.context)
        
        # Merge and deduplicate
        all_commitments = self._merge_commitment_detections(regex_commitments, llm_commitments)
        
        # Create CommitmentCreate objects
        commitment_creates = []
        for text, details in all_commitments.items():
            commitment_creates.append(
                CommitmentCreate(
                    text=text,
                    source=request.source,
                    source_reference=request.source_reference,
                    extracted_from=request.text,
                    confidence_score=details["confidence"],
                    user_id=request.user_id,
                    priority=details.get("priority", CommitmentPriority.MEDIUM),
                    due_date=details.get("due_date"),
                    time_frame=details.get("time_frame"),
                    action_required=details.get("action"),
                    related_person=details.get("related_person"),
                    tags=details.get("tags"),
                )
            )
        
        # Prepare summary
        processing_time = (time.time() - start_time) * 1000  # convert to ms
        analysis_summary = {
            "regex_detections": len(regex_commitments),
            "llm_detections": len(llm_commitments),
            "final_commitment_count": len(commitment_creates),
            "text_length": len(request.text),
        }
        
        return CommitmentDetectionResponse(
            detected_commitments=commitment_creates,
            analysis_summary=analysis_summary,
            processing_time_ms=processing_time
        )
        
    def _detect_with_regex(self, text: str) -> Dict[str, Dict[str, Any]]:
        """
        Detect commitments using regex patterns.
        
        Args:
            text: The text to analyze
            
        Returns:
            Dictionary mapping commitment text to details
        """
        commitments = {}
        
        # Split text into sentences
        sentences = re.split(r'[.!?]\s+', text)
        
        for sentence in sentences:
            for pattern in self.compiled_patterns:
                matches = pattern.findall(sentence)
                for match in matches:
                    if len(match.strip()) > 3:  # Avoid very short matches
                        cleaned_text = match.strip()
                        if cleaned_text not in commitments:
                            commitments[cleaned_text] = {
                                "confidence": 0.7,  # Base confidence for regex
                                "source": "regex"
                            }
        
        return commitments
    
    def _detect_with_llm(self, text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Dict[str, Any]]:
        """
        Detect commitments using LLM.
        
        Args:
            text: The text to analyze
            context: Additional context for detection
            
        Returns:
            Dictionary mapping commitment text to details
        """
        prompt = self._create_commitment_detection_prompt(text, context)
        
        try:
            llm_response = self.llm_service.generate_structured_output(
                prompt=prompt,
                output_format={
                    "commitments": [
                        {
                            "text": "string",
                            "confidence": "float",
                            "priority": "string (LOW, MEDIUM, HIGH, CRITICAL)",
                            "time_frame": "string?",
                            "due_date": "string? (ISO format)",
                            "action": "string?",
                            "related_person": "string?",
                            "tags": ["string"]
                        }
                    ]
                }
            )
            
            commitments = {}
            for commitment in llm_response.get("commitments", []):
                # Convert string priority to enum
                priority_map = {
                    "LOW": CommitmentPriority.LOW,
                    "MEDIUM": CommitmentPriority.MEDIUM,
                    "HIGH": CommitmentPriority.HIGH,
                    "CRITICAL": CommitmentPriority.CRITICAL
                }
                
                # Parse due date if provided
                due_date = None
                if commitment.get("due_date"):
                    try:
                        due_date = datetime.fromisoformat(commitment["due_date"])
                    except (ValueError, TypeError):
                        logger.warning(f"Invalid due date format: {commitment.get('due_date')}")
                
                commitments[commitment["text"]] = {
                    "confidence": float(commitment["confidence"]),
                    "priority": priority_map.get(commitment.get("priority", "MEDIUM"), CommitmentPriority.MEDIUM),
                    "time_frame": commitment.get("time_frame"),
                    "due_date": due_date,
                    "action": commitment.get("action"),
                    "related_person": commitment.get("related_person"),
                    "tags": commitment.get("tags", []),
                    "source": "llm"
                }
            
            return commitments
            
        except Exception as e:
            logger.error(f"Error in LLM commitment detection: {str(e)}")
            return {}
    
    def _create_commitment_detection_prompt(self, text: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a prompt for the LLM to detect commitments.
        
        Args:
            text: The text to analyze
            context: Additional context
            
        Returns:
            Formatted prompt for the LLM
        """
        prompt = """
        Analyze the following text and identify any commitments, promises, or obligations.
        Look for explicit statements like "I will", "I promise", "I need to", etc.
        Also look for implicit commitments and tasks the person needs to remember.
        
        For each commitment, provide:
        1. The exact commitment text
        2. A confidence score (0.0-1.0)
        3. Priority (LOW, MEDIUM, HIGH, CRITICAL)
        4. Any time frame mentioned (e.g., "next week", "tomorrow")
        5. Due date in ISO format if specified
        6. The action required
        7. Any person the commitment was made to
        8. Relevant tags
        
        TEXT TO ANALYZE:
        
        {text}
        """
        
        if context:
            prompt += "\n\nADDITIONAL CONTEXT:\n\n"
            for key, value in context.items():
                prompt += f"{key}: {value}\n"
        
        return prompt.format(text=text)
    
    def _merge_commitment_detections(
        self, 
        regex_commitments: Dict[str, Dict[str, Any]], 
        llm_commitments: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Merge and deduplicate commitments from different detection methods.
        
        Args:
            regex_commitments: Commitments detected by regex
            llm_commitments: Commitments detected by LLM
            
        Returns:
            Merged dictionary of unique commitments
        """
        merged = {}
        
        # First add all LLM commitments
        merged.update(llm_commitments)
        
        # Then add regex commitments if not already detected by LLM
        for text, details in regex_commitments.items():
            if text not in merged:
                merged[text] = details
            else:
                # If detected by both, increase confidence
                merged[text]["confidence"] = min(0.95, merged[text]["confidence"] + 0.1)
                merged[text]["source"] = "both"
        
        return merged
    
    def create_commitment(self, commitment: CommitmentCreate) -> CommitmentModel:
        """
        Create a new commitment in the database.
        
        Args:
            commitment: The commitment to create
            
        Returns:
            The created commitment model
        """
        db_commitment = CommitmentModel(
            user_id=commitment.user_id,
            text=commitment.text,
            source=commitment.source,
            source_reference=commitment.source_reference,
            extracted_from=commitment.extracted_from,
            confidence_score=commitment.confidence_score,
            status=CommitmentStatus.DETECTED,
            priority=commitment.priority,
            related_person=commitment.related_person,
            related_task_id=commitment.related_task_id,
            due_date=commitment.due_date,
            time_frame=commitment.time_frame,
            action_required=commitment.action_required,
            tags=commitment.tags,
            notes=commitment.notes,
            should_remind=commitment.should_remind,
            reminder_frequency=commitment.reminder_frequency,
            cross_references=commitment.cross_references
        )
        
        self.db.add(db_commitment)
        self.db.commit()
        self.db.refresh(db_commitment)
        
        return db_commitment
    
    def create_multiple_commitments(
        self, commitments: List[CommitmentCreate]
    ) -> List[CommitmentModel]:
        """
        Create multiple commitments in the database.
        
        Args:
            commitments: List of commitments to create
            
        Returns:
            List of created commitment models
        """
        db_commitments = []
        
        for commitment in commitments:
            db_commitment = CommitmentModel(
                user_id=commitment.user_id,
                text=commitment.text,
                source=commitment.source,
                source_reference=commitment.source_reference,
                extracted_from=commitment.extracted_from,
                confidence_score=commitment.confidence_score,
                status=CommitmentStatus.DETECTED,
                priority=commitment.priority,
                related_person=commitment.related_person,
                related_task_id=commitment.related_task_id,
                due_date=commitment.due_date,
                time_frame=commitment.time_frame,
                action_required=commitment.action_required,
                tags=commitment.tags,
                notes=commitment.notes,
                should_remind=commitment.should_remind,
                reminder_frequency=commitment.reminder_frequency,
                cross_references=commitment.cross_references
            )
            
            self.db.add(db_commitment)
            db_commitments.append(db_commitment)
        
        self.db.commit()
        for commitment in db_commitments:
            self.db.refresh(commitment)
        
        return db_commitments
    
    def get_commitment(self, commitment_id: int) -> CommitmentModel:
        """
        Get a commitment by ID.
        
        Args:
            commitment_id: The commitment ID
            
        Returns:
            The commitment model
            
        Raises:
            ServiceException: If commitment not found
        """
        commitment = self.db.query(CommitmentModel).filter(CommitmentModel.id == commitment_id).first()
        
        if not commitment:
            raise ServiceException(f"Commitment with ID {commitment_id} not found")
            
        return commitment
    
    def update_commitment(
        self, commitment_id: int, update_data: CommitmentUpdate
    ) -> CommitmentModel:
        """
        Update a commitment.
        
        Args:
            commitment_id: The commitment ID
            update_data: The data to update
            
        Returns:
            The updated commitment model
            
        Raises:
            ServiceException: If commitment not found
        """
        commitment = self.get_commitment(commitment_id)
        
        # Update fields
        update_dict = update_data.dict(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(commitment, key, value)
        
        self.db.commit()
        self.db.refresh(commitment)
        
        return commitment
    
    def delete_commitment(self, commitment_id: int) -> None:
        """
        Delete a commitment.
        
        Args:
            commitment_id: The commitment ID
            
        Raises:
            ServiceException: If commitment not found
        """
        commitment = self.get_commitment(commitment_id)
        
        self.db.delete(commitment)
        self.db.commit()
    
    def get_user_commitments(
        self, 
        user_id: UUID, 
        status: Optional[CommitmentStatus] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        source: Optional[CommitmentSource] = None,
        priority: Optional[CommitmentPriority] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[CommitmentModel], int]:
        """
        Get commitments for a user with optional filters.
        
        Args:
            user_id: The user ID
            status: Filter by status
            from_date: Filter by detection date (from)
            to_date: Filter by detection date (to)
            source: Filter by source
            priority: Filter by priority
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            Tuple of (list of commitments, total count)
        """
        query = self.db.query(CommitmentModel).filter(CommitmentModel.user_id == user_id)
        
        # Apply filters
        if status:
            query = query.filter(CommitmentModel.status == status)
        
        if from_date:
            query = query.filter(CommitmentModel.detected_at >= from_date)
            
        if to_date:
            query = query.filter(CommitmentModel.detected_at <= to_date)
            
        if source:
            query = query.filter(CommitmentModel.source == source)
            
        if priority:
            query = query.filter(CommitmentModel.priority == priority)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        query = query.order_by(CommitmentModel.detected_at.desc())
        query = query.offset(skip).limit(limit)
        
        return query.all(), total
    
    def confirm_commitment(self, commitment_id: int) -> CommitmentModel:
        """
        Mark a commitment as confirmed.
        
        Args:
            commitment_id: The commitment ID
            
        Returns:
            The updated commitment model
        """
        return self.update_commitment(
            commitment_id, 
            CommitmentUpdate(status=CommitmentStatus.CONFIRMED)
        )
    
    def reject_commitment(self, commitment_id: int) -> CommitmentModel:
        """
        Mark a commitment as rejected.
        
        Args:
            commitment_id: The commitment ID
            
        Returns:
            The updated commitment model
        """
        return self.update_commitment(
            commitment_id, 
            CommitmentUpdate(status=CommitmentStatus.REJECTED)
        )
    
    def complete_commitment(self, commitment_id: int) -> CommitmentModel:
        """
        Mark a commitment as completed.
        
        Args:
            commitment_id: The commitment ID
            
        Returns:
            The updated commitment model
        """
        return self.update_commitment(
            commitment_id, 
            CommitmentUpdate(status=CommitmentStatus.COMPLETED)
        )
    
    def analyze_journal_entry(self, text: str, user_id: UUID) -> List[CommitmentModel]:
        """
        Analyze a journal entry for commitments and save them.
        
        Args:
            text: The journal entry text
            user_id: The user ID
            
        Returns:
            List of detected and saved commitments
        """
        # Detect commitments
        detection_request = CommitmentDetectionRequest(
            text=text,
            source=CommitmentSource.JOURNAL,
            user_id=user_id
        )
        
        detection_response = self.detect_commitments(detection_request)
        
        # Save detected commitments
        return self.create_multiple_commitments(detection_response.detected_commitments)
    
    def get_commitments_due_soon(
        self, 
        user_id: UUID, 
        hours_threshold: int = 24
    ) -> List[CommitmentModel]:
        """
        Get commitments due within the specified hours threshold.
        
        Args:
            user_id: The user ID
            hours_threshold: Hours threshold (default 24)
            
        Returns:
            List of commitments due soon
        """
        # TODO: Implement time frame parsing logic and due date calculation
        # For now, return commitments with explicit due dates
        from datetime import timedelta
        
        now = datetime.utcnow()
        threshold = now + timedelta(hours=hours_threshold)
        
        query = self.db.query(CommitmentModel).filter(
            CommitmentModel.user_id == user_id,
            CommitmentModel.status.in_([CommitmentStatus.DETECTED, CommitmentStatus.CONFIRMED]),
            CommitmentModel.due_date.isnot(None),
            CommitmentModel.due_date <= threshold,
            CommitmentModel.due_date >= now
        )
        
        return query.all()