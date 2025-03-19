"""
Commitment Schema Module for ADHD Calendar.

This module defines Pydantic schemas for commitment detection and management
to support proactive forgetfulness and distraction mitigation.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from uuid import UUID
from pydantic import BaseModel, Field, validator

from app.models.commitment_model import CommitmentSource, CommitmentStatus, CommitmentPriority


class CommitmentBase(BaseModel):
    """Base schema for commitments."""
    text: str = Field(..., description="Text content of the commitment")
    source: CommitmentSource = Field(..., description="Source of the commitment")
    source_reference: Optional[str] = Field(None, description="Reference ID in the source system")
    related_person: Optional[str] = Field(None, description="Person the commitment was made to")
    priority: CommitmentPriority = Field(CommitmentPriority.MEDIUM, description="Priority of the commitment")
    due_date: Optional[datetime] = Field(None, description="Due date if specified")
    time_frame: Optional[str] = Field(None, description="Natural language time frame")
    action_required: Optional[str] = Field(None, description="Action that needs to be taken")
    tags: Optional[List[str]] = Field(None, description="Tags for categorization")
    notes: Optional[str] = Field(None, description="Additional notes")
    should_remind: bool = Field(True, description="Whether to send reminders")
    reminder_frequency: Optional[str] = Field(None, description="How often to remind")


class CommitmentCreate(CommitmentBase):
    """Schema for creating a new commitment."""
    extracted_from: Optional[str] = Field(None, description="Original text it was extracted from")
    confidence_score: float = Field(0.0, description="Confidence score of the detection")
    user_id: UUID = Field(..., description="User who made the commitment")
    related_task_id: Optional[int] = Field(None, description="Related task ID if any")
    cross_references: Optional[List[int]] = Field(None, description="References to related commitments")
    

class CommitmentUpdate(BaseModel):
    """Schema for updating an existing commitment."""
    text: Optional[str] = None
    status: Optional[CommitmentStatus] = None
    priority: Optional[CommitmentPriority] = None
    related_person: Optional[str] = None
    related_task_id: Optional[int] = None
    due_date: Optional[datetime] = None
    time_frame: Optional[str] = None
    action_required: Optional[str] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None
    should_remind: Optional[bool] = None
    reminder_frequency: Optional[str] = None
    cross_references: Optional[List[int]] = None


class CommitmentInDB(CommitmentBase):
    """Schema for commitment from database."""
    id: int
    user_id: UUID
    status: CommitmentStatus
    extracted_from: Optional[str] = None
    confidence_score: float
    detected_at: datetime
    related_task_id: Optional[int] = None
    cross_references: Optional[List[int]] = None
    
    class Config:
        orm_mode = True


class CommitmentResponse(CommitmentInDB):
    """Schema for commitment API response."""
    pass


class CommitmentDetectionRequest(BaseModel):
    """Schema for commitment detection request."""
    text: str = Field(..., description="Text to analyze for commitments")
    source: CommitmentSource = Field(..., description="Source of the text")
    source_reference: Optional[str] = Field(None, description="Reference ID in the source system")
    user_id: UUID = Field(..., description="User ID for personalization")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context for detection")


class CommitmentDetectionResponse(BaseModel):
    """Schema for commitment detection response."""
    detected_commitments: List[CommitmentCreate] = Field([], description="Detected commitments")
    analysis_summary: Dict[str, Any] = Field({}, description="Summary of the analysis")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")


class CommitmentsList(BaseModel):
    """Schema for list of commitments."""
    items: List[CommitmentResponse]
    total: int
    page: int
    size: int


class CommitmentReminder(BaseModel):
    """Schema for commitment reminder."""
    commitment_id: int
    text: str
    due_date: Optional[datetime] = None
    time_frame: Optional[str] = None
    priority: CommitmentPriority
    related_person: Optional[str] = None
    action_required: Optional[str] = None


class DialogueMessage(BaseModel):
    """Schema for dialogue system messages."""
    content: str
    is_user: bool = True
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class DialogueSession(BaseModel):
    """Schema for dialogue session."""
    session_id: str
    user_id: UUID
    messages: List[DialogueMessage] = []
    detected_commitments: List[int] = []  # IDs of detected commitments
    context: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class DialogueRequest(BaseModel):
    """Schema for dialogue request."""
    message: str
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class DialogueResponse(BaseModel):
    """Schema for dialogue response."""
    message: str
    session_id: str
    detected_commitments: List[CommitmentResponse] = []
    suggestions: List[str] = []
    context: Dict[str, Any] = {}