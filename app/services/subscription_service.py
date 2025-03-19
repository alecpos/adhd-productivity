from sqlalchemy.ext.asyncio import AsyncSession

from app.services.base_service import BaseService
from app.schemas.subscription_schema import (
    SubscriptionCreateSchema,
    SubscriptionListResponseSchema,
    SubscriptionResponseSchema,
    SubscriptionUpdateSchema,
)
from app.schemas.schema_manager_schema import SchemaManagerSchema as SchemaManager
from app.schemas.schema_validation_schema import validate_schema, ValidationRule, RequiredFieldRule
from app.utils.error_handler import handle_service_error
from app.models.subscription_model import SubscriptionModel
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from datetime import datetime
from dateutil.relativedelta import relativedelta
from typing import Optional, Dict, Any
from uuid import UUID


class SubscriptionService(BaseService[SubscriptionModel, SubscriptionResponseSchema, SubscriptionCreateSchema]):
    """Service for managing subscriptions."""

    def __init__(self, db: AsyncSession):
        """Initialize the service with database session."""
        super().__init__(db=db, model=SubscriptionModel, schema=SubscriptionResponseSchema)
        self.schema_manager = SchemaManager()

    @handle_service_error
    async def create_subscription(
        self, subscription_data: SubscriptionCreateSchema
    ) -> SubscriptionResponseSchema:
        """Create a new subscription with validation."""
        validate_schema(subscription_data)
        new_subscription = self.model(**subscription_data.dict(exclude_unset=True))
        self.db.add(new_subscription)
        await self.db.commit()
        await self.db.refresh(new_subscription)
        return self.schema.from_orm(new_subscription)

    @handle_service_error
    async def get_subscriptions(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100,
        include_inactive: bool = False,
    ) -> SubscriptionListResponseSchema:
        """Get paginated list of subscriptions with optional filtering."""
        query = select(self.model).where(self.model.user_id == user_id)
        if not include_inactive:
            query = query.where(self.model.status == "active")
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        subscriptions = result.scalars().all()
        total_query = select(self.model).where(
            self.model.user_id == user_id
        )
        active_query = total_query.where(self.model.status == "active")
        total_count = len((await self.db.execute(total_query)).scalars().all())
        active_count = len((await self.db.execute(active_query)).scalars().all())
        total_monthly_cost = sum(
            (
                sub.amount
                for sub in subscriptions
                if sub.status == "active" and sub.billing_cycle == "monthly"
            )
        )
        return SubscriptionListResponseSchema(
            data=[self.schema.from_orm(sub) for sub in subscriptions],
            total_count=total_count,
            active_count=active_count,
            total_monthly_cost=total_monthly_cost,
        )

    @handle_service_error
    async def get_subscription(self, subscription_id: UUID) -> Optional[SubscriptionResponseSchema]:
        """Get a single subscription by ID."""
        result = await self.db.execute(
            select(self.model)
            .where(self.model.id == subscription_id)
            .options(selectinload(self.model.payment_history))
        )
        subscription = result.scalar_one_or_none()
        if subscription:
            return self.schema.from_orm(subscription)

    @handle_service_error
    async def update_subscription(
        self, subscription_id: UUID, updates: SubscriptionUpdateSchema
    ) -> Optional[SubscriptionResponseSchema]:
        """Update a subscription with validation."""
        validate_schema(updates)
        result = await self.db.execute(
            select(self.model).where(self.model.id == subscription_id)
        )
        subscription = result.scalar_one_or_none()
        if subscription:
            update_data = updates.dict(exclude_unset=True)
            for key, value in update_data.items():
                setattr(subscription, key, value)
            subscription.updated_at = datetime.utcnow()
            await self.db.commit()
            await self.db.refresh(subscription)
            return self.schema.from_orm(subscription)

    @handle_service_error
    async def delete_subscription(self, subscription_id: UUID) -> bool:
        """Delete a subscription."""
        result = await self.db.execute(
            select(self.model).where(self.model.id == subscription_id)
        )
        subscription = result.scalar_one_or_none()
        if subscription:
            await self.db.delete(subscription)
            await self.db.commit()

    @handle_service_error
    async def process_subscription_payment(
        self, subscription_id: UUID, payment_data: Dict[str, Any]
    ) -> Optional[SubscriptionResponseSchema]:
        """Process a subscription payment and update payment history."""
        result = await self.db.execute(
            select(self.model).where(self.model.id == subscription_id)
        )
        subscription = result.scalar_one_or_none()
        if subscription:
            payment_data["processed_at"] = datetime.utcnow()
            if not subscription.payment_history:
                subscription.payment_history = []
            subscription.payment_history.append(payment_data)
            subscription.last_payment_date = datetime.utcnow()
            subscription.next_payment_date = self._calculate_next_payment_date(
                subscription.billing_cycle, subscription.last_payment_date
            )
            await self.db.commit()
            await self.db.refresh(subscription)
            return self.schema.from_orm(subscription)

    def _calculate_next_payment_date(
        self, billing_cycle: str, last_payment_date: datetime
    ) -> datetime:
        """Calculate the next payment date based on billing cycle."""
        cycle_map = {
            "monthly": relativedelta(months=1),
            "quarterly": relativedelta(months=3),
            "semi-annual": relativedelta(months=6),
            "annual": relativedelta(years=1),
        }
        return last_payment_date + cycle_map.get(billing_cycle, relativedelta(months=1))
