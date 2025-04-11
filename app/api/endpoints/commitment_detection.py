"""
Commitment Detection API Endpoints for ADHD Calendar.

This module defines FastAPI endpoints for the commitment detection and
proactive forgetfulness mitigation system.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user_model import UserModel
from app.models.commitment_model import CommitmentStatus, CommitmentSource, CommitmentPriority
from app.schemas.commitment_schema import (
    CommitmentCreate,
    CommitmentUpdate,
    CommitmentResponse,
    CommitmentsList,
    CommitmentDetectionRequest,
    CommitmentDetectionResponse,
    DialogueRequest,
    DialogueResponse,
)
from app.services.commitment_detection_service import CommitmentDetectionService
from app.services.dialogue_system_service import DialogueSystemService
from app.services.smart_reminder_service import SmartReminderService


router = APIRouter()


@router.post("/detect", response_model=CommitmentDetectionResponse)
def detect_commitments(
    request: CommitmentDetectionRequest,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """
    Detect commitments in text.

    This endpoint analyzes text for explicit and implicit commitments
    and returns the detected commitments.
    """
    service = CommitmentDetectionService(db)

    # Make sure the user ID in the request matches the current user
    if str(request.user_id) != str(current_user.id):
        raise HTTPException(
            status_code=403, detail="User ID in request does not match authenticated user"
        )

    detection_response = service.detect_commitments(request)
    return detection_response


@router.post("/commitments", response_model=CommitmentResponse)
def create_commitment(
    commitment: CommitmentCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """
    Create a new commitment.

    This endpoint creates a new commitment from the provided data.
    """
    service = CommitmentDetectionService(db)

    # Make sure the user ID in the request matches the current user
    if str(commitment.user_id) != str(current_user.id):
        raise HTTPException(
            status_code=403, detail="User ID in request does not match authenticated user"
        )

    db_commitment = service.create_commitment(commitment)
    return CommitmentResponse.from_orm(db_commitment)


@router.get("/commitments", response_model=CommitmentsList)
def get_commitments(
    status: Optional[str] = None,
    source: Optional[str] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    priority: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """
    Get commitments for the current user.

    This endpoint retrieves commitments with optional filtering.
    """
    service = CommitmentDetectionService(db)

    # Convert string parameters to enums if provided
    status_enum = None
    if status:
        try:
            status_enum = CommitmentStatus(status)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status}")

    source_enum = None
    if source:
        try:
            source_enum = CommitmentSource(source)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid source: {source}")

    priority_enum = None
    if priority:
        try:
            priority_enum = CommitmentPriority(priority)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid priority: {priority}")

    commitments, total = service.get_user_commitments(
        user_id=current_user.id,
        status=status_enum,
        from_date=from_date,
        to_date=to_date,
        source=source_enum,
        priority=priority_enum,
        skip=skip,
        limit=limit,
    )

    return CommitmentsList(
        items=[CommitmentResponse.from_orm(c) for c in commitments],
        total=total,
        page=skip // limit + 1,
        size=limit,
    )


@router.get("/commitments/{commitment_id}", response_model=CommitmentResponse)
def get_commitment(
    commitment_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """
    Get a specific commitment.

    This endpoint retrieves a commitment by ID.
    """
    service = CommitmentDetectionService(db)

    try:
        commitment = service.get_commitment(commitment_id)

        # Make sure the commitment belongs to the current user
        if str(commitment.user_id) != str(current_user.id):
            raise HTTPException(
                status_code=403, detail="This commitment does not belong to the current user"
            )

        return CommitmentResponse.from_orm(commitment)

    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Commitment not found: {str(e)}")


@router.put("/commitments/{commitment_id}", response_model=CommitmentResponse)
def update_commitment(
    commitment_id: int = Path(..., gt=0),
    update_data: CommitmentUpdate = None,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """
    Update a commitment.

    This endpoint updates a commitment with the provided data.
    """
    service = CommitmentDetectionService(db)

    try:
        # First get the commitment to check ownership
        commitment = service.get_commitment(commitment_id)

        # Make sure the commitment belongs to the current user
        if str(commitment.user_id) != str(current_user.id):
            raise HTTPException(
                status_code=403, detail="This commitment does not belong to the current user"
            )

        # Update the commitment
        updated_commitment = service.update_commitment(commitment_id, update_data)
        return CommitmentResponse.from_orm(updated_commitment)

    except Exception as e:
        raise HTTPException(
            status_code=404, detail=f"Commitment not found or could not be updated: {str(e)}"
        )


@router.delete("/commitments/{commitment_id}", status_code=204)
def delete_commitment(
    commitment_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """
    Delete a commitment.

    This endpoint deletes a commitment by ID.
    """
    service = CommitmentDetectionService(db)

    try:
        # First get the commitment to check ownership
        commitment = service.get_commitment(commitment_id)

        # Make sure the commitment belongs to the current user
        if str(commitment.user_id) != str(current_user.id):
            raise HTTPException(
                status_code=403, detail="This commitment does not belong to the current user"
            )

        # Delete the commitment
        service.delete_commitment(commitment_id)

    except Exception as e:
        raise HTTPException(
            status_code=404, detail=f"Commitment not found or could not be deleted: {str(e)}"
        )


@router.post("/commitments/{commitment_id}/confirm", response_model=CommitmentResponse)
def confirm_commitment(
    commitment_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """
    Confirm a commitment.

    This endpoint marks a commitment as confirmed.
    """
    service = CommitmentDetectionService(db)

    try:
        # First get the commitment to check ownership
        commitment = service.get_commitment(commitment_id)

        # Make sure the commitment belongs to the current user
        if str(commitment.user_id) != str(current_user.id):
            raise HTTPException(
                status_code=403, detail="This commitment does not belong to the current user"
            )

        # Confirm the commitment
        confirmed_commitment = service.confirm_commitment(commitment_id)
        return CommitmentResponse.from_orm(confirmed_commitment)

    except Exception as e:
        raise HTTPException(
            status_code=404, detail=f"Commitment not found or could not be confirmed: {str(e)}"
        )


@router.post("/commitments/{commitment_id}/reject", response_model=CommitmentResponse)
def reject_commitment(
    commitment_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """
    Reject a commitment.

    This endpoint marks a commitment as rejected.
    """
    service = CommitmentDetectionService(db)

    try:
        # First get the commitment to check ownership
        commitment = service.get_commitment(commitment_id)

        # Make sure the commitment belongs to the current user
        if str(commitment.user_id) != str(current_user.id):
            raise HTTPException(
                status_code=403, detail="This commitment does not belong to the current user"
            )

        # Reject the commitment
        rejected_commitment = service.reject_commitment(commitment_id)
        return CommitmentResponse.from_orm(rejected_commitment)

    except Exception as e:
        raise HTTPException(
            status_code=404, detail=f"Commitment not found or could not be rejected: {str(e)}"
        )


@router.post("/dialogue", response_model=DialogueResponse)
def process_dialogue(
    request: DialogueRequest,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """
    Process a dialogue message.

    This endpoint processes a message from the user in the 'forgot anything?'
    dialogue system and returns an appropriate response.
    """
    service = DialogueSystemService(db)

    response = service.process_message(request, str(current_user.id))
    return response


@router.post("/analyze/journal", response_model=List[CommitmentResponse])
def analyze_journal_entry(
    text: str, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)
):
    """
    Analyze a journal entry for commitments.

    This endpoint analyzes a journal entry for commitments and saves any
    detected commitments.
    """
    service = CommitmentDetectionService(db)

    commitments = service.analyze_journal_entry(text, current_user.id)
    return [CommitmentResponse.from_orm(c) for c in commitments]


@router.post("/reminders/process", response_model=Dict[str, Any])
def process_smart_reminders(
    db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)
):
    """
    Process smart reminders.

    This endpoint processes smart reminders for the current user,
    sending any that are due.
    """
    service = SmartReminderService(db)

    result = service.process_smart_reminders(current_user.id)
    return result
