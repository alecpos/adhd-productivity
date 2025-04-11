"""Subscription schemas."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import Field, validator
from app.schemas.schema_validation_schema import ValidationRule, RequiredFieldRule
from app.core.responses import APIResponse
from app.schemas.base_schema import BaseSchema, TimestampedSchema


class SubscriptionSchema(BaseSchema):
    """Base schema for subscription management with comprehensive validation."""

    name: str = Field(..., description="Name of the subscription", min_length=1, max_length=100)
    amount: float = Field(..., description="SubscriptionSchema amount", ge=0)
    due_date: datetime = Field(..., description="SubscriptionSchema due date")
    billing_cycle: str = Field("monthly", description="Billing cycle frequency")
    auto_renew: bool = Field(True, description="Whether the subscription auto-renews")
    category: Optional[str] = Field(
        None, description="SubscriptionModelSchema category for organization"
    )
    description: Optional[str] = Field(
        None, description="Detailed description of the subscription", max_length=500
    )
    payment_method: Optional[str] = Field(None, description="Payment method for the subscription")
    status: str = Field("active", description="Current subscription status")
    notifications_enabled: bool = Field(
        True, description="Whether to send subscription notifications"
    )

    @validator("billing_cycle")
    def validate_billing_cycle(cls, v):
        valid_cycles = ["monthly", "quarterly", "semi-annual", "annual", "custom"]
        if v.lower() not in valid_cycles:
            raise ValueError(f"Billing cycle must be one of: {', '.join(valid_cycles)}")
        return v.lower()

    @validator("status")
    def validate_status(cls, v):
        valid_statuses = ["active", "pending", "cancelled", "expired", "suspended"]
        if v.lower() not in valid_statuses:
            raise ValueError(f"Status must be one of: {', '.join(valid_statuses)}")
        return v.lower()

    @validator("amount")
    def validate_amount(cls, v):
        if v < 0:
            raise ValueError("Amount cannot be negative")
        return round(v, 2)


class SubscriptionCreateSchema(SubscriptionSchema):
    """Schema for creating a new subscription."""

    user_id: UUID = Field(..., description="ID of the user owning the subscription")


class SubscriptionUpdateSchema(BaseSchema):
    """Schema for updating a subscription."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    amount: Optional[float] = Field(None, ge=0)
    due_date: Optional[datetime] = None
    billing_cycle: Optional[str] = None
    auto_renew: Optional[bool] = None
    category: Optional[str] = None
    description: Optional[str] = Field(None, max_length=500)
    payment_method: Optional[str] = None
    status: Optional[str] = None
    notifications_enabled: Optional[bool] = None

    @validator("billing_cycle")
    def validate_billing_cycle(cls, v):
        if v is not None:
            valid_cycles = ["monthly", "quarterly", "semi-annual", "annual", "custom"]
            if v.lower() not in valid_cycles:
                raise ValueError(f"Billing cycle must be one of: {', '.join(valid_cycles)}")
            return v.lower()

    @validator("status")
    def validate_status(cls, v):
        if v is not None:
            valid_statuses = ["active", "pending", "cancelled", "expired", "suspended"]
            if v.lower() not in valid_statuses:
                raise ValueError(f"Status must be one of: {', '.join(valid_statuses)}")
            return v.lower()


class SubscriptionResponseSchema(SubscriptionSchema, TimestampedSchema):
    """Schema for subscription response with comprehensive details."""

    id: UUID = Field(..., description="Unique subscription identifier")
    user_id: UUID = Field(..., description="ID of the subscription owner")
    next_payment_date: Optional[datetime] = Field(None, description="Next scheduled payment date")
    last_payment_date: Optional[datetime] = Field(None, description="Last successful payment date")
    payment_history: Optional[List[Dict[str, Any]]] = Field(
        None, description="History of subscription payments"
    )
    renewal_date: Optional[datetime] = Field(None, description="Next renewal date")
    total_paid: float = Field(0.0, description="Total amount paid for this subscription")
    active_period: Dict[str, datetime] = Field(
        ..., description="Current active period of the subscription"
    )
    features: Optional[List[str]] = Field(
        None, description="List of features included in the subscription"
    )

    @validator("next_payment_date", "renewal_date")
    def validate_future_dates(cls, v):
        if v and v < datetime.now():
            raise ValueError("Date must be in the future")

    @validator("total_paid")
    def validate_total_paid(cls, v):
        if v < 0:
            raise ValueError("Total paid cannot be negative")
        return round(v, 2)


class SubscriptionListResponseSchema(APIResponse):
    """Schema for paginated list of subscriptions."""

    data: List[SubscriptionResponseSchema]
    total_count: int = Field(..., description="Total number of subscriptions")
    active_count: int = Field(..., description="Number of active subscriptions")
    total_monthly_cost: float = Field(..., description="Total monthly subscription cost")


validation_rules = [
    RequiredFieldRule(field_name="name", error_message="SubscriptionSchema name is required"),
    RequiredFieldRule(field_name="amount", error_message="SubscriptionSchema amount is required"),
    RequiredFieldRule(field_name="due_date", error_message="Due date is required"),
    ValidationRule(
        field_name="amount", validator=lambda v: v >= 0, error_message="Amount must be non-negative"
    ),
    ValidationRule(
        field_name="billing_cycle",
        validator=lambda v: v.lower()
        in ["monthly", "quarterly", "semi-annual", "annual", "custom"],
        error_message="Invalid billing cycle",
    ),
    ValidationRule(
        field_name="status",
        validator=lambda v: v.lower() in ["active", "pending", "cancelled", "expired", "suspended"],
        error_message="Invalid subscription status",
    ),
    ValidationRule(
        field_name="name",
        validator=lambda v: 1 <= len(v) <= 100,
        error_message="Name must be between 1 and 100 characters",
    ),
    ValidationRule(
        field_name="description",
        validator=lambda v: not v or len(v) <= 500,
        error_message="Description cannot exceed 500 characters",
    ),
]
__all__ = [
    "SubscriptionSchema",
    "SubscriptionCreateSchema",
    "SubscriptionUpdateSchema",
    "SubscriptionResponseSchema",
    "SubscriptionListResponseSchema",
    "validation_rules",
]
