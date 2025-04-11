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

from app.models.commitment_model import (
    CommitmentModel,
    CommitmentSource,
    CommitmentStatus,
    CommitmentPriority,
)
from app.schemas.commitment_schema import (
    CommitmentCreate,
    CommitmentDetectionRequest,
    CommitmentDetectionResponse,
    CommitmentUpdate,
    CommitmentInDB,
)
from app.services.base_service import BaseService, OPEN, CLOSED, HALF_OPEN
from app.services.llm_service import LLMService
from app.core.exceptions import ServiceException

logger = logging.getLogger(__name__)


class CommitmentDetectionService(BaseService[CommitmentModel, CommitmentInDB, CommitmentCreate]):
    """
    Service for detecting and managing commitments.

    This service uses transformer-based models to detect commitments
    in text and manages the commitment lifecycle.
    """

    def __init__(self, db: Session, llm_service: Optional[LLMService] = None):
        """Initialize the commitment detection service."""
        super().__init__(db=db, model=CommitmentModel, schema_class=CommitmentInDB)
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
        self.compiled_patterns = [
            re.compile(pattern, re.IGNORECASE) for pattern in self.commitment_patterns
        ]

        # Initialize bulkhead for LLM processing
        self._llm_processing_bulkhead = self.with_bulkhead(
            name="llm_processing", max_concurrent_calls=3, max_queue_size=10
        )

    @BaseService.with_retry(
        max_retries=3,
        initial_delay=0.2,
        max_delay=2.0,
        backoff_factor=2.0,
        error_message="Failed to detect commitments",
    )
    @BaseService.with_circuit_breaker(
        name="detect_commitments", failure_threshold=5, recovery_timeout=30
    )
    def detect_commitments(
        self, request: CommitmentDetectionRequest
    ) -> CommitmentDetectionResponse:
        """
        Detect commitments in text with resilience patterns.

        Args:
            request: The commitment detection request

        Returns:
            A response containing detected commitments
        """
        logger.info(
            f"Detecting commitments for user {request.user_id} in text of length {len(request.text)}"
        )
        start_time = time.time()

        try:
            # Extract commitments using both approaches
            regex_commitments = self._detect_with_regex(request.text)
            llm_commitments = self._detect_with_llm(request.text, request.context)

            # Merge and deduplicate
            all_commitments = self._merge_commitment_detections(regex_commitments, llm_commitments)

            # Create CommitmentCreate objects
            commitment_creates = []
            for text, details in all_commitments.items():
                commitment = CommitmentCreate(
                    user_id=request.user_id,
                    text=text,
                    source=CommitmentSource.DETECTION,
                    source_details=f"Detected from: {details.get('source', 'text')}",
                    detection_confidence=details.get("confidence", 0.7),
                    priority=details.get("priority", CommitmentPriority.MEDIUM),
                    due_date=details.get("due_date"),
                    status=CommitmentStatus.PENDING,
                )
                commitment_creates.append(commitment)

            # Save commitments to database if auto-save is enabled
            saved_commitments = []
            if request.auto_save:
                for commitment in commitment_creates:
                    try:
                        saved = self.create_commitment(commitment)
                        saved_commitments.append(saved)
                    except Exception as e:
                        logger.error(f"Error saving commitment: {str(e)}")

            elapsed_time = time.time() - start_time
            logger.info(
                f"Commitment detection completed in {elapsed_time:.2f}s, found {len(commitment_creates)} commitments"
            )

            return CommitmentDetectionResponse(
                commitments=commitment_creates,
                saved_commitments=saved_commitments,
                request_id=request.request_id,
                processing_time=elapsed_time,
            )
        except Exception as e:
            logger.error(f"Error in detect_commitments: {str(e)}", exc_info=True)
            raise

    def _detect_with_regex(self, text: str) -> Dict[str, Dict[str, Any]]:
        """Apply regex patterns to detect potential commitments."""
        logger.debug("Detecting commitments with regex patterns")
        commitments = {}

        try:
            for pattern in self.compiled_patterns:
                matches = pattern.finditer(text)
                for match in matches:
                    commitment_text = match.group(1).strip()
                    if (
                        commitment_text and len(commitment_text) > 3
                    ):  # Filter out very short matches
                        commitments[commitment_text] = {
                            "source": "regex",
                            "confidence": 0.7,
                            "pattern": pattern.pattern,
                        }

            logger.debug(f"Detected {len(commitments)} commitments with regex")
            return commitments
        except Exception as e:
            logger.error(f"Error in regex detection: {str(e)}", exc_info=True)
            return {}

    @BaseService.with_retry(
        max_retries=2,
        initial_delay=0.5,
        max_delay=3.0,
        backoff_factor=2.0,
        error_message="Failed to detect commitments with LLM",
    )
    @BaseService.with_circuit_breaker(
        name="llm_detection", failure_threshold=3, recovery_timeout=60
    )
    def _detect_with_llm(
        self, text: str, context: Optional[str] = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        Use LLM to detect commitments with advanced semantic understanding.

        This method uses the LLM service with circuit breaker protection.
        """
        logger.debug("Detecting commitments with LLM")

        # Define the operation to perform inside the bulkhead
        async def llm_detect_operation():
            try:
                if not self.llm_service:
                    logger.warning("No LLM service available, skipping LLM detection")
                    return {}

                llm_result = self.llm_service.analyze_text_for_commitments(text, context)

                # Convert result to expected format
                commitments = {}
                for item in llm_result.get("commitments", []):
                    commitment_text = item.get("text", "").strip()
                    if commitment_text and len(commitment_text) > 3:
                        commitments[commitment_text] = {
                            "source": "llm",
                            "confidence": item.get("confidence", 0.8),
                            "due_date": item.get("due_date"),
                            "priority": item.get("priority", CommitmentPriority.MEDIUM),
                        }

                logger.debug(f"Detected {len(commitments)} commitments with LLM")
                return commitments
            except Exception as e:
                logger.error(f"Error in LLM detection: {str(e)}", exc_info=True)
                return {}

        # Use bulkhead pattern to isolate LLM processing
        try:
            return self.bulkhead_llm_processing(text, context)
        except Exception as e:
            logger.error(f"Bulkhead error in LLM detection: {str(e)}", exc_info=True)
            # Fallback to regex only
            return {}

    async def bulkhead_llm_processing(
        self, text: str, context: Optional[str] = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        Process text with LLM using bulkhead pattern.

        This provides isolation for the resource-intensive LLM processing.
        """

        # Define the operation to perform inside the bulkhead
        async def process_with_llm():
            if not self.llm_service:
                logger.warning("No LLM service available, skipping LLM detection")
                return {}

            llm_result = self.llm_service.analyze_text_for_commitments(text, context)

            # Convert result to expected format
            commitments = {}
            for item in llm_result.get("commitments", []):
                commitment_text = item.get("text", "").strip()
                if commitment_text and len(commitment_text) > 3:
                    commitments[commitment_text] = {
                        "source": "llm",
                        "confidence": item.get("confidence", 0.8),
                        "due_date": item.get("due_date"),
                        "priority": item.get("priority", CommitmentPriority.MEDIUM),
                    }

            return commitments

        # Execute with bulkhead isolation
        try:
            logger.info(f"Processing text of length {len(text)} with LLM using bulkhead")
            result = await self._llm_processing_bulkhead(process_with_llm)()
            logger.info(f"LLM processing completed, found {len(result)} commitments")
            return result
        except Exception as e:
            logger.error(f"Error in bulkhead_llm_processing: {str(e)}", exc_info=True)
            return {}

    def _merge_commitment_detections(
        self,
        regex_commitments: Dict[str, Dict[str, Any]],
        llm_commitments: Dict[str, Dict[str, Any]],
    ) -> Dict[str, Dict[str, Any]]:
        """Merge and deduplicate commitments from different detection methods."""
        # Start with LLM commitments as they're likely higher quality
        merged = {**llm_commitments}

        # Add regex commitments if not already detected by LLM
        for text, details in regex_commitments.items():
            if text not in merged:
                merged[text] = details
            else:
                # If already detected by LLM, increase confidence
                merged[text]["confidence"] = min(0.95, merged[text].get("confidence", 0.7) + 0.1)
                merged[text]["source"] = "multiple"

        return merged

    @BaseService.with_retry(
        max_retries=3,
        initial_delay=0.1,
        max_delay=1.0,
        backoff_factor=2.0,
        error_message="Failed to create commitment",
    )
    @BaseService.with_circuit_breaker(
        name="create_commitment", failure_threshold=5, recovery_timeout=30
    )
    def create_commitment(self, commitment_data: CommitmentCreate) -> CommitmentModel:
        """Create a new commitment with resilience patterns."""
        logger.info(f"Creating commitment for user {commitment_data.user_id}")

        try:
            commitment = CommitmentModel(
                user_id=commitment_data.user_id,
                text=commitment_data.text,
                source=commitment_data.source,
                source_details=commitment_data.source_details,
                detection_confidence=commitment_data.detection_confidence,
                priority=commitment_data.priority,
                due_date=commitment_data.due_date,
                status=commitment_data.status,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )

            self.db.add(commitment)
            self.db.commit()
            self.db.refresh(commitment)

            logger.info(f"Successfully created commitment with ID: {commitment.id}")
            return commitment
        except Exception as e:
            logger.error(f"Error creating commitment: {str(e)}", exc_info=True)
            self.db.rollback()
            raise

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
                cross_references=commitment.cross_references,
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
        commitment = (
            self.db.query(CommitmentModel).filter(CommitmentModel.id == commitment_id).first()
        )

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
        limit: int = 100,
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
            commitment_id, CommitmentUpdate(status=CommitmentStatus.CONFIRMED)
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
            commitment_id, CommitmentUpdate(status=CommitmentStatus.REJECTED)
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
            commitment_id, CommitmentUpdate(status=CommitmentStatus.COMPLETED)
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
            text=text, source=CommitmentSource.JOURNAL, user_id=user_id
        )

        detection_response = self.detect_commitments(detection_request)

        # Save detected commitments
        return self.create_multiple_commitments(detection_response.detected_commitments)

    def get_commitments_due_soon(
        self, user_id: UUID, hours_threshold: int = 24
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
            CommitmentModel.due_date >= now,
        )

        return query.all()

    async def health_check(self) -> Dict[str, Any]:
        """
        Get the health status of the commitment detection service.

        This implementation tracks the status of the LLM service dependency.
        """
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        llm_health = await self._get_llm_health()

        # Get circuit states for key operations
        circuit_states = {
            "detect_commitments": self._get_circuit_state("detect_commitments"),
            "llm_detection": self._get_circuit_state("llm_detection"),
            "create_commitment": self._get_circuit_state("create_commitment"),
        }

        # Get bulkhead state
        bulkhead_state = {
            "llm_processing": {
                "max_concurrent": 3,  # From initialization
                "max_queue": 10,  # From initialization
            }
        }

        # Determine overall health based on circuits
        is_healthy = all(state == CLOSED for state in circuit_states.values())
        llm_is_healthy = llm_health.get("status") == "healthy"

        return {
            "service": "CommitmentDetectionService",
            "status": "healthy" if (is_healthy and llm_is_healthy) else "degraded",
            "timestamp": now,
            "details": {
                "circuits": circuit_states,
                "bulkheads": bulkhead_state,
                "llm_service": llm_health,
            },
        }

    async def _get_llm_health(self) -> Dict[str, Any]:
        """Get health status of LLM service."""
        if not self.llm_service:
            return {"status": "unavailable", "message": "LLM service not configured"}

        # Check if circuit is open for LLM
        if self._get_circuit_state("llm_detection") == OPEN:
            return {"status": "unhealthy", "message": "Circuit breaker open for LLM service"}

        try:
            # Try a quick health probe to the LLM service
            is_healthy = self.llm_service.check_availability()
            return {
                "status": "healthy" if is_healthy else "degraded",
                "message": (
                    "LLM service responding normally"
                    if is_healthy
                    else "LLM service responding but degraded"
                ),
            }
        except Exception as e:
            logger.error(f"Error checking LLM service health: {str(e)}")
            return {"status": "unhealthy", "message": f"Error connecting to LLM service: {str(e)}"}
