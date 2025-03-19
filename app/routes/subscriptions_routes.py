from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.subscription_schema import (
    SubscriptionCreateSchema,
    SubscriptionListResponseSchema,
    SubscriptionResponseSchema,
    SubscriptionUpdateSchema,
)
from app.services.subscription_service import SubscriptionService
from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])


async def get_subscription_service(db: AsyncSession = Depends(get_db)):
    return SubscriptionService(db=db)


@router.post("/", response_model=SubscriptionResponseSchema, summary="Create a new subscription")
async def create_subscription(
    subscription_data: SubscriptionCreateSchema,
    service: SubscriptionService = Depends(get_subscription_service),
):
    """Create a new subscription for a user."""
    try:
        subscription = await service.create_subscription(
            name=subscription_data.name,
            amount=subscription_data.amount,
            due_date=subscription_data.due_date,
            user_id=subscription_data.user_id,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating subscription: {str(e)}")


@router.get(
    "/",
    response_model=SubscriptionListResponseSchema,
    summary="List all subscriptions for a user",
)
async def list_subscriptions(
    user_id: UUID, service: SubscriptionService = Depends(get_subscription_service)
):
    """List all subscriptions associated with a specific user."""
    try:
        subscriptions = await service.get_subscriptions(user_id)
        return {"subscriptions": subscriptions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing subscriptions: {str(e)}")


@router.put(
    "/{subscription_id}",
    response_model=SubscriptionResponseSchema,
    summary="Update a subscription",
)
async def update_subscription(
    subscription_id: UUID,
    updates: SubscriptionUpdateSchema,
    service: SubscriptionService = Depends(get_subscription_service),
):
    """Update details of a specific subscription."""
    try:
        subscription = await service.update_subscription(
            subscription_id, updates.dict(exclude_unset=True)
        )
        if not subscription:
            raise HTTPException(status_code=404, detail="SubscriptionModel not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating subscription: {str(e)}")


@router.delete("/{subscription_id}", summary="Delete a subscription")
async def delete_subscription(
    subscription_id: UUID,
    service: SubscriptionService = Depends(get_subscription_service),
):
    """Delete a specific subscription."""
    try:
        success = await service.delete_subscription(subscription_id)
        if not success:
            raise HTTPException(status_code=404, detail="SubscriptionModel not found.")
        return {"message": "SubscriptionModel deleted successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting subscription: {str(e)}")
