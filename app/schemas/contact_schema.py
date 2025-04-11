from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr
from enum import Enum


class ContactType(Enum):
    """Contact type enum."""

    FAMILY = "FAMILY"
    FRIEND = "FRIEND"
    WORK = "WORK"
    OTHER = "OTHER"


class ContactBaseSchema(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    contact_type: ContactType = ContactType.OTHER
    notes: Optional[str] = None
    relationship_strength: int
    tags: List[str] = []


class ContactCreateSchema(ContactBaseSchema):
    pass


class ContactUpdateSchema(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    contact_type: Optional[ContactType] = None
    notes: Optional[str] = None
    relationship_strength: Optional[int] = None
    tags: Optional[List[str]] = None


class ContactResponseSchema(ContactBaseSchema):
    id: int
    user_id: int
    last_contact: Optional[datetime] = None
    next_reminder: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
